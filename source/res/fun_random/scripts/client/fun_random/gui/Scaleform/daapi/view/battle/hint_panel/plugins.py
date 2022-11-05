# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/hint_panel/plugins.py
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FUN_RANDOM_HINT_SECTION, HINTS_LEFT
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode
from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.hint_panel_plugin import HelpHintContext
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HintPanelPlugin, HintData, HintPriority
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import PreBattleHintPlugin, BEFORE_START_BATTLE_PERIODS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ViewEventType, GameEvent
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider

def updatePlugins(plugins):
    if FunRandomPreBattleHintPlugin.isSuitable():
        plugins['prebattleHints'] = FunRandomPreBattleHintPlugin
    else:
        plugins.pop('prebattleHints', None)
    if FunRandomHelpPlugin.isSuitable():
        plugins['funRandomHelpHint'] = FunRandomHelpPlugin
    return plugins


class FunRandomPreBattleHintPlugin(PreBattleHintPlugin, FunSubModesWatcher):

    @classmethod
    @hasBattleSubMode(defReturn=False)
    def isSuitable(cls):
        settingsKey = cls.getBattleSubMode().getSettings().client.settingsKey
        funRandomSettings = AccountSettings.getSettings(FUN_RANDOM_HINT_SECTION)
        return settingsKey in funRandomSettings and funRandomSettings[settingsKey][HINTS_LEFT] <= 0


class FunRandomHelpPlugin(HintPanelPlugin, FunSubModesWatcher):
    __slots__ = ('__isActive', '__settings', '__isShown', '__isInDisplayPeriod', '__callbackDelayer', '__isVisible', '__settingKey')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HINT_TIMEOUT = 6

    def __init__(self, parentObj):
        super(FunRandomHelpPlugin, self).__init__(parentObj)
        self.__isActive = False
        self.__settings = None
        self.__isShown = False
        self.__isVisible = False
        self.__isInDisplayPeriod = False
        self.__callbackDelayer = None
        self.__settingKey = ''
        return

    @classmethod
    @hasBattleSubMode(defReturn=False)
    def isSuitable(cls):
        settingsKey = cls.getBattleSubMode().getSettings().client.settingsKey
        funRandomSettings = AccountSettings.getSettings(FUN_RANDOM_HINT_SECTION)
        return settingsKey not in funRandomSettings or funRandomSettings[settingsKey][HINTS_LEFT] > 0

    def start(self):
        self.__isActive = True
        self.__callbackDelayer = CallbackDelayer()
        self.__settingKey = self.getBattleSubMode().getSettings().client.settingsKey
        self.__settings = AccountSettings.getSettings(FUN_RANDOM_HINT_SECTION)
        self.__settings[self.__settingKey] = self.__settings.get(self.__settingKey, {HINTS_LEFT: 3})
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.BATTLE_LOADING, self.__onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        if self.__isActive:
            self.__hide()
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.BATTLE_LOADING, self.__onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
            if self.__isShown:
                AccountSettings.setSettings(FUN_RANDOM_HINT_SECTION, self.__settings)
        self.__settingKey = ''
        self.__isActive = False
        return

    def setPeriod(self, period):
        if not self.__isActive:
            return
        self.__isInDisplayPeriod = period in BEFORE_START_BATTLE_PERIODS
        if self.__isVisible and not self.__isInDisplayPeriod:
            self.__hide()

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_SHOW_HELP)
        key = getVirtualKey(CommandMapping.CMD_SHOW_HELP)
        pressText = backport.text(R.strings.ingame_gui.helpScreen.hint.funSubModePress())
        hintText = backport.text(R.strings.ingame_gui.helpScreen.hint.funSubModeDescription())
        return HintData(key, keyName, pressText, hintText, 0, 0, HintPriority.HELP, False, HelpHintContext.FUN_RANDOM)

    def __showHint(self):
        self._parentObj.setBtnHint(CommandMapping.CMD_SHOW_HELP, self._getHint())
        self._updateBattleCounterOnUsed(self.__settings[self.__settingKey])
        self.__callbackDelayer.delayCallback(self._HINT_TIMEOUT, self.__hide)
        self.__isVisible = True
        self.__isShown = True

    def __handleLoadView(self, event):
        if event.alias == VIEW_ALIAS.INGAME_DETAILS_HELP:
            self.__hide()

    def __onBattleLoading(self, event):
        battleLoadingShown = event.ctx.get('isShown')
        if not battleLoadingShown and self.__isInDisplayPeriod and self.__settings[self.__settingKey][HINTS_LEFT] > 0:
            self.__showHint()

    def __hide(self):
        if self.__isVisible:
            self.__callbackDelayer.stopCallback(self.__hide)
            self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
            self.__isVisible = False
