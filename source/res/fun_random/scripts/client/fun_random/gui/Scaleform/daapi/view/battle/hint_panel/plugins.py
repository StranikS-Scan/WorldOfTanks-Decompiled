# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/hint_panel/plugins.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FUN_RANDOM_HINT_SECTION, HINTS_LEFT
from fun_random.gui.Scaleform.daapi.view.battle.hint_panel.hint_panel_plugin import HelpHintContext
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasBattleSubMode
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HintPriority
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import PreBattleHintPlugin, HelpPlugin

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


class FunRandomHelpPlugin(HelpPlugin, FunSubModesWatcher):

    def __init__(self, parentObj):
        battleSubMode = self.getBattleSubMode()
        super(FunRandomHelpPlugin, self).__init__(FUN_RANDOM_HINT_SECTION, battleSubMode.getSettings().client.settingsKey, battleSubMode.getLocalsResRoot().detailsHelpHint, HintPriority.HELP, HelpHintContext.FUN_RANDOM, parentObj)

    @classmethod
    @hasBattleSubMode(defReturn=False)
    def isSuitable(cls):
        settingsKey = cls.getBattleSubMode().getSettings().client.settingsKey
        funRandomSettings = AccountSettings.getSettings(FUN_RANDOM_HINT_SECTION)
        return settingsKey not in funRandomSettings or funRandomSettings[settingsKey][HINTS_LEFT] > 0
