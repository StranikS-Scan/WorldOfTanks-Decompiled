# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/dyn_squad_hint_plugin.py
import logging
from typing import TYPE_CHECKING
import CommandMapping
from constants import ARENA_PERIOD, ARENA_GUI_TYPE
from account_helpers import AccountSettings
from account_helpers.AccountSettings import DYN_SQUAD_HINT_SECTION
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getReadableKey
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from hint_panel_plugin import HintPanelPlugin, HintData, HintPriority
import VOIP
if TYPE_CHECKING:
    from component import BattleHintPanel
    from typing import Type as TType, Any as TAny
_logger = logging.getLogger(__name__)

class DynSquadHintPlugin(HintPanelPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HINT_DAY_COOLDOWN = 30
    _HINT_BATTLES_COOLDOWN = 10
    _HINT_TIMEOUT = 6

    def __init__(self, parentObj):
        super(DynSquadHintPlugin, self).__init__(parentObj)
        self.__shouldShowHint = False
        self.__isHintShown = False
        self.__isDestroyTimerDisplaying = False
        self.__isObserver = False
        self.__settings = {}
        self.__wasDisplayed = False
        self.__callbackDelayer = None
        self._isInRecovery = False
        self._isUnderFire = False
        self._isInProgressCircle = False
        return

    @classmethod
    def isSuitable(cls):
        return cls.sessionProvider.arenaVisitor.getArenaGuiType() in (ARENA_GUI_TYPE.RANDOM, ARENA_GUI_TYPE.EPIC_BATTLE, ARENA_GUI_TYPE.EPIC_RANDOM)

    def start(self):
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is not None:
            vInfo = arenaDP.getVehicleInfo()
            self.__isObserver = vInfo.isObserver()
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        dynSquads = self.sessionProvider.dynamic.dynSquads
        if dynSquads is not None:
            dynSquads.onDynSquadCreatedOrJoined += self.__onDynSquadCreatedOrJoined
        self.__settings = AccountSettings.getSettings(DYN_SQUAD_HINT_SECTION)
        self._updateCounterOnStart(self.__settings, self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)
        g_eventBus.addListener(GameEvent.TOGGLE_VOIP_CHANNEL_ENABLED, self.__onToggleVoipChannel, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        dynSquads = self.sessionProvider.dynamic.dynSquads
        if dynSquads is not None:
            dynSquads.onDynSquadCreatedOrJoined -= self.__onDynSquadCreatedOrJoined
        if self.__callbackDelayer is not None:
            self.__callbackDelayer.destroy()
        if not self.sessionProvider.isReplayPlaying:
            AccountSettings.setSettings(DYN_SQUAD_HINT_SECTION, self.__settings)
        g_eventBus.removeListener(GameEvent.TOGGLE_VOIP_CHANNEL_ENABLED, self.__onToggleVoipChannel, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def show(self):
        self.__shouldShowHint = True
        self.__updateHint()

    def hide(self):
        self.__shouldShowHint = False
        self.__updateHint()

    def setPeriod(self, period):
        if period is ARENA_PERIOD.BATTLE:
            self._updateCounterOnBattle(self.__settings)

    def updateMapping(self):
        if self.__isHintShown:
            self.__wasDisplayed = False
            self.__addHint()

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_VOICECHAT_ENABLE)
        hintTextLeft = backport.text(R.strings.ingame_gui.dynamicSquad.hint.voipToggleKeyLeft())
        hintTextRight = backport.text(R.strings.ingame_gui.dynamicSquad.hint.voipToggleKeyRight())
        return HintData(keyName, hintTextLeft, hintTextRight, 0, 0, HintPriority.DYN_SQUAD)

    def __onToggleVoipChannel(self, *args, **kwargs):
        self._updateCounterOnUsed(self.__settings)
        self.hide()

    def __canShowHint(self):
        if self.__isObserver or self.sessionProvider.isReplayPlaying or self.__wasDisplayed or self.__areOtherIndicatorsShown():
            return False
        voipMgr = VOIP.getVOIPManager()
        if voipMgr:
            if not voipMgr.isVoiceSupported():
                return False
        keyName = getReadableKey(CommandMapping.CMD_VOICECHAT_ENABLE)
        return False if not keyName else self._haveHintsLeft(self.__settings)

    def __addHint(self):
        if not self.__canShowHint():
            return
        else:
            self._parentObj.setBtnHint(CommandMapping.CMD_VOICECHAT_ENABLE, self._getHint())
            self.__isHintShown = True
            self.__wasDisplayed = True
            if self.__callbackDelayer is None:
                self.__callbackDelayer = CallbackDelayer()
            self.__callbackDelayer.delayCallback(self._HINT_TIMEOUT, self.__onHintTimeOut)
            return

    def __removeHint(self):
        if not self.__isHintShown:
            return
        else:
            self._parentObj.removeBtnHint(CommandMapping.CMD_VOICECHAT_ENABLE)
            self.__isHintShown = False
            if self.__callbackDelayer is not None:
                self.__callbackDelayer.stopCallback(self.__onHintTimeOut)
            return

    def __onHintTimeOut(self):
        self.__shouldShowHint = False
        self.__updateHint()

    def __updateHint(self):
        _logger.debug('Updating dyn squad: hint')
        if self.__isObserver or self.sessionProvider.isReplayPlaying:
            return
        showHint = self.__shouldShowHint and not self.__areOtherIndicatorsShown()
        if not self.__isHintShown and showHint:
            self.__addHint()
        elif self.__isHintShown and not showHint:
            self.__removeHint()

    def __onDynSquadCreatedOrJoined(self, isCreator, squadID):
        self.show()

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.RECOVERY:
            self._isInRecovery = value[0]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.PROGRESS_CIRCLE:
            self._isInProgressCircle = value[1]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            self._isUnderFire = value
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isInDisplayPeriod = False
            self.__updateHint()

    def __areOtherIndicatorsShown(self):
        return self._isUnderFire or self._isInRecovery or self._isInProgressCircle
