# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/hint_panel/plugins.py
from __future__ import absolute_import
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import HINTS_LEFT
from constants import ARENA_PERIOD
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HintPriority, HintPanelPlugin, HintData
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from skeletons.gui.battle_session import IBattleSessionProvider
from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.plugins import FunRandomHelpPlugin
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode
from fall_tanks.gui.fall_tanks_account_settings import AccountSettingsKeys
from fall_tanks.gui.Scaleform.daapi.view.battle.hint_panel.hint_panel_plugin import VehicleEvacuationHintContext

def createPlugins():
    plugins = {}
    if FunRandomHelpPlugin.isSuitable():
        plugins['fallTanksHelpHint'] = FunRandomHelpPlugin
    if FallTanksEvacuationPlugin.isSuitable():
        plugins['fallTanksEvacuationHint'] = FallTanksEvacuationPlugin
    return plugins


class FallTanksEvacuationPlugin(HintPanelPlugin, FunSubModesWatcher):
    __slots__ = ('__isActive', '__settings', '__isShown', '__isInDisplayPeriod', '__callbackDelayer', '__isVisible', '__settingKey', '__hintContext')
    _PERIODS = (ARENA_PERIOD.BATTLE,)
    _HINTS_AMOUNT = 3
    _HINT_TIMEOUT = 6
    _CMD_KEY = CommandMapping.CMD_REQUEST_RECOVERY
    _SETTINGS_NAME = AccountSettingsKeys.FALL_TANKS_HINTS
    _HINT_PRIORITY = HintPriority.HELP
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(FallTanksEvacuationPlugin, self).__init__(parentObj)
        self.__isActive = False
        self.__settings = None
        self.__isShown = False
        self.__isVisible = False
        self.__isInDisplayPeriod = False
        self.__callbackDelayer = None
        self.__settingKey = self.getBattleSubMode().getSettings().client.settingsKey
        self.__hintContext = VehicleEvacuationHintContext.FALL_TANKS_EVACUATION
        return

    @classmethod
    @hasBattleSubMode(defReturn=False)
    def isSuitable(cls):
        settingsKey = cls.getBattleSubMode().getSettings().client.settingsKey
        fallTanksSettings = AccountSettings.getSettings(cls._SETTINGS_NAME)
        return settingsKey not in fallTanksSettings or fallTanksSettings[settingsKey][HINTS_LEFT] > 0

    def updateMapping(self):
        if self.__isActive:
            self.__hide()

    def setPeriod(self, period):
        if not self.__isActive:
            return
        self.__isInDisplayPeriod = period in self._PERIODS
        if self.__isVisible and not self.__isInDisplayPeriod:
            self.__hide()
        elif not self.__isVisible and self.__isInDisplayPeriod:
            self.__showHint()

    def start(self):
        self.__isActive = True
        self.__callbackDelayer = CallbackDelayer()
        self.__settings = AccountSettings.getSettings(self._SETTINGS_NAME)
        self.__settings[self.__settingKey] = self.__settings.get(self.__settingKey, {HINTS_LEFT: self._HINTS_AMOUNT})
        g_eventBus.addListener(GameEvent.BATTLE_LOADING, self.__onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__onHintShown, scope=EVENT_BUS_SCOPE.GLOBAL)

    def stop(self):
        if self.__isActive:
            self.__hide()
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
            g_eventBus.removeListener(GameEvent.BATTLE_LOADING, self.__onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__onHintShown, scope=EVENT_BUS_SCOPE.GLOBAL)
            if self.__isShown:
                AccountSettings.setSettings(self._SETTINGS_NAME, self.__settings)
        self.__isActive = False
        self.__settingKey = None
        self.__hintContext = None
        return

    def _getHint(self):
        keyName = getReadableKey(self._CMD_KEY)
        localRes = R.strings.fall_tanks.buttonHint.evacuation
        hintText = backport.text(localRes.description()) if keyName else backport.text(localRes.noBindingKey())
        return HintData(vKey=getVirtualKey(self._CMD_KEY), key=keyName, isKeyLong=False, messageLeft=backport.text(localRes.press()), messageRight=hintText, offsetX=0, offsetY=0, priority=self._HINT_PRIORITY, reducedPanning=False, hintCtx=self.__hintContext, centeredMessage=False)

    def __showHint(self):
        self._parentObj.setBtnHint(self._CMD_KEY, self._getHint())

    def __hide(self):
        if not self.__isVisible:
            return
        self.__callbackDelayer.stopCallback(self.__hide)
        self.__isVisible = False
        hint = self._parentObj.removeBtnHint(self._CMD_KEY)
        if hint and hint.hintCtx == self.__hintContext:
            self._updateBattleCounterOnUsed(self.__settings[self.__settingKey])

    def __onBattleLoading(self, event):
        battleLoadingShown = event.ctx.get('isShown')
        if not battleLoadingShown and self.__isInDisplayPeriod and self.__settings[self.__settingKey][HINTS_LEFT] > 0 and not self.__sessionProvider.isReplayPlaying:
            self.__showHint()

    def __onHintShown(self, event):
        if event.ctx.get('hintCtx') == self.__hintContext and not self.__isShown:
            self.__isVisible = True
            self.__isShown = True
            self.__callbackDelayer.delayCallback(self._HINT_TIMEOUT, self.__hide)
