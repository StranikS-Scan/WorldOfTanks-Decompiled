# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/hint_panel/plugins.py
import CommandMapping
from gui.impl import backport
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HintPriority, HintData
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import PreBattleHintPlugin
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from last_stand_common.last_stand_constants import ARENA_GUI_TYPE

def updatePlugins(plugins):
    plugins.pop('prebattleHints')
    if LSHelpPlugin.isSuitable():
        plugins['lsHelpHint'] = LSHelpPlugin
    return plugins


class LSHelpPlugin(PreBattleHintPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def isSuitable(cls):
        return cls.__sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.LAST_STAND

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_SHOW_HELP)
        key = getVirtualKey(CommandMapping.CMD_SHOW_HELP)
        pressText = backport.text(R.strings.last_stand_battle.helpScreen.hint.press())
        hintText = backport.text(R.strings.last_stand_battle.helpScreen.hint.description())
        return HintData(key, keyName, False, pressText, hintText, 0, 0, HintPriority.HELP, False)

    def _canDisplayCustomHelpHint(self):
        return True
