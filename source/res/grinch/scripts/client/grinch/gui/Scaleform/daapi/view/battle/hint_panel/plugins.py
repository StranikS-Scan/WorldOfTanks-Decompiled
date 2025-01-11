# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/hint_panel/plugins.py
import CommandMapping
from gui.impl import backport
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HintPriority, HintData
from gui.Scaleform.daapi.view.battle.shared.hint_panel.plugins import SiegeIndicatorHintPlugin
from gui.impl.gen import R
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from grinch_common.grinch_constants import ARENA_GUI_TYPE

def createPlugin():
    plugins = {}
    if GrinchHelpPlugin.isSuitable():
        plugins['grinchHelpHint'] = GrinchHelpPlugin
    return plugins


class GrinchHelpPlugin(SiegeIndicatorHintPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @classmethod
    def isSuitable(cls):
        return cls.__sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.GRINCH

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        key = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        pressText = backport.text(R.strings.ingame_gui.siegeMode.hint.press())
        hintText = backport.text(R.strings.ingame_gui.siegeMode.hint.rocketAcceleration())
        return HintData(key, keyName, pressText, hintText, 0, 0, HintPriority.HELP, False, None, False)

    def _canDisplayCustomHelpHint(self):
        return True
