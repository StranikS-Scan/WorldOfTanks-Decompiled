# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/Scaleform/daapi/view/battle/prebattle_timer.py
import BattleReplay
import BigWorld
from comp7_core_constants import ArenaPrebattlePhase
from comp7_core.gui.Scaleform.daapi.view.meta.Comp7PrebattleTimerMeta import Comp7PrebattleTimerMeta
from comp7_core.gui.comp7_core_constants import BATTLE_CTRL_ID
from constants import ARENA_PERIOD, VEHICLE_SELECTION_BLOCK_DELAY
from gui.Scaleform.genConsts.PREBATTLE_TIMER import PREBATTLE_TIMER
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, i18n
from skeletons.gui.battle_session import IBattleSessionProvider

class Comp7PrebattleTimer(Comp7PrebattleTimerMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __RES_ROOT = R.strings.comp7_core.prebattleTimer

    def __init__(self):
        super(Comp7PrebattleTimer, self).__init__()
        self.__isSelectionConfirmed = False
        self.__winConditionStr = ''
        self.__isPrebattleInputStateLocked = False
        self.__isUIUpdateNeeded = True
        self.__lastProcessedState = self._state

    def updateBattleCtx(self, battleCtx):
        self.__winConditionStr = battleCtx.getArenaWinString()
        self.__updateMessageAndWinDescription()
        super(Comp7PrebattleTimer, self).updateBattleCtx(battleCtx)

    def setCountdown(self, state, timeLeft):
        if state == ARENA_PERIOD.PREBATTLE:
            _, _, banPhaseTimeLeft = self.__getBanPhaseData(countdownTimeLeft=timeLeft)
            if banPhaseTimeLeft is not None:
                timeLeft = banPhaseTimeLeft
                if not timeLeft:
                    self.as_setTimerS(0)
            elif timeLeft is not None:
                timeLeft -= VEHICLE_SELECTION_BLOCK_DELAY
        super(Comp7PrebattleTimer, self).setCountdown(state, timeLeft)
        self.__updateUIIfNeeded()
        return

    def onReadyBtnClick(self):
        self.__sessionProvider.dynamic.prebattleSetup.confirmVehicleSelection()
        self.__setIsSelectionConfirmed(True)
        self.as_hideInfoS()
        self.__updateMessageAndWinDescription()

    def hideCountdown(self, state, speed):
        if not self.__isSelectionConfirmed:
            self.as_setWinConditionTextS(self.__winConditionStr)
        super(Comp7PrebattleTimer, self).hideCountdown(state, speed)

    def _populate(self):
        super(Comp7PrebattleTimer, self)._populate()
        self.__isSelectionConfirmed = self.__sessionProvider.dynamic.prebattleSetup.isSelectionConfirmed()
        g_eventBus.addListener(GameEvent.PREBATTLE_INPUT_STATE_LOCKED, self.__onPrebattleInputStateLocked, scope=EVENT_BUS_SCOPE.BATTLE)
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.onBanPhaseUpdated += self.__updateBanPhaseUI
        self.__updateUIIfNeeded()
        return

    def _dispose(self):
        g_eventBus.removeListener(GameEvent.PREBATTLE_INPUT_STATE_LOCKED, self.__onPrebattleInputStateLocked, scope=EVENT_BUS_SCOPE.BATTLE)
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        if vehicleBanCtrl is not None:
            vehicleBanCtrl.onBanPhaseUpdated -= self.__updateBanPhaseUI
        super(Comp7PrebattleTimer, self)._dispose()
        return

    def _isDisplayWinCondition(self):
        return False

    def _getMessage(self):
        if self._state == COUNTDOWN_STATE.WAIT:
            return backport.text(self.__RES_ROOT.wait.header())
        if self.__isSelectionPossible():
            if self.__isPrebattleInputStateLocked:
                return ''
            if self._state == COUNTDOWN_STATE.START:
                banText, _, _ = self.__getBanPhaseData()
                return banText or backport.text(self.__RES_ROOT.wait.selectVehicle())
        return i18n.makeString(self._battleTypeStr)

    def __updateUIIfNeeded(self):
        self.__invalidateLastProcessedState()
        if self.__isUIUpdateNeeded:
            self.__updateHint()
            self.__updateButton()
            self.__updateMessageAndWinDescription()
            self.__isUIUpdateNeeded = False

    def __invalidateLastProcessedState(self):
        if self.__lastProcessedState != self._state:
            self.__lastProcessedState = self._state
            self.__isUIUpdateNeeded = True

    def __updateHint(self):
        if self.__isSelectionConfirmed:
            self.as_hideInfoS()
        elif not self.__isPrebattleInputStateLocked:
            self.as_setInfoHintS('')

    def __updateButton(self):
        hideButtonForBan = False
        if self.__isVehicleBanEnabled():
            hideButtonForBan = self.__getVehicleBanCtrl().getArenaPrebattlePhase() != ArenaPrebattlePhase.PICK
        if not self.__isSelectionPossible() or hideButtonForBan:
            self.as_hideInfoS()
        elif self._state == COUNTDOWN_STATE.START and not self.__isPrebattleInputStateLocked and not BattleReplay.g_replayCtrl.isPlaying:
            self.as_addInfoS(PREBATTLE_TIMER.COMP7_PREBATTLE_INFO_VIEW_LINKAGE, self.__getInfoVO())
            self.as_showInfoS()

    def __getInfoVO(self):
        return {'readyBtnLabel': backport.text(self.__RES_ROOT.info.readyBtn.label()),
         'readyBtnTooltip': makeTooltip(body=backport.text(self.__RES_ROOT.info.readyBtn.tooltip.body()))}

    def __onPrebattleInputStateLocked(self, _):
        self.__setIsPrebattleInputStateLocked(True)
        if not self.__isSelectionConfirmed:
            self.as_setMessageS(self._getMessage())
            self.as_hideInfoS()

    def __updateMessageAndWinDescription(self):
        if not self.__isSelectionPossible():
            self.as_setMessageS(self._getMessage())
            self.as_setWinConditionTextS(self.__winConditionStr)
        elif self._state == COUNTDOWN_STATE.WAIT:
            self.as_setWinConditionTextS(backport.text(self.__RES_ROOT.wait.additionalInfo()))
        elif self._state == COUNTDOWN_STATE.START and self.__isVehicleBanEnabled():
            _, banText, _ = self.__getBanPhaseData()
            self.as_setMessageS(self._getMessage())
            self.as_setWinConditionTextS(banText or '')
        else:
            self.as_setWinConditionTextS('')

    def __isSelectionPossible(self):
        return not self.__isSelectionConfirmed and not avatar_getter.isObserver()

    def __setIsSelectionConfirmed(self, value):
        self.__isUIUpdateNeeded = self.__isSelectionConfirmed != value
        self.__isSelectionConfirmed = value

    def __setIsPrebattleInputStateLocked(self, value):
        self.__isUIUpdateNeeded = self.__isPrebattleInputStateLocked != value
        self.__isPrebattleInputStateLocked = value

    def __getVehicleBanCtrl(self):
        return self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL)

    def __isVehicleBanEnabled(self):
        vehicleBanCtrl = self.__getVehicleBanCtrl()
        return vehicleBanCtrl is not None and vehicleBanCtrl.isVehicleBanEnabled

    def __getBanPhaseData(self, countdownTimeLeft=None):
        header, info, timeLeft = (None, None, None)
        if not self.__isVehicleBanEnabled():
            return (header, info, timeLeft)
        else:
            vehicleBanCtrl = self.__getVehicleBanCtrl()
            banPhase = vehicleBanCtrl.getArenaPrebattlePhase()
            if banPhase == ArenaPrebattlePhase.NONE:
                timeLeft = 0
            elif banPhase == ArenaPrebattlePhase.PREPICK:
                header = backport.text(self.__RES_ROOT.prepick.header())
                info = backport.text(self.__RES_ROOT.prepick.additionalInfo())
                timeLeft = round(vehicleBanCtrl.vehiclePrepickEndTime - BigWorld.serverTime())
            elif banPhase == ArenaPrebattlePhase.VOTING:
                header = backport.text(self.__RES_ROOT.ban.header())
                info = backport.text(self.__RES_ROOT.ban.additionalInfo())
                timeLeft = int(vehicleBanCtrl.vehicleBanEndTime - BigWorld.serverTime())
            else:
                header = backport.text(self.__RES_ROOT.pick.header())
                info = ''
                if countdownTimeLeft is not None:
                    timeLeft = countdownTimeLeft - VEHICLE_SELECTION_BLOCK_DELAY
            return (header, info, timeLeft)

    def __updateBanPhaseUI(self):
        self.__updateButton()
        self.__updateMessageAndWinDescription()
