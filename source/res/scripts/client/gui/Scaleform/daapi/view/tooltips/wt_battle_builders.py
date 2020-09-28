# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/wt_battle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DefaultFormatBuilder
from gui.shared.tooltips.game_event.wt_battle_shell_tooltip import WtBattleShellTooltipData
__all__ = 'getTooltipBuilders'

def getTooltipBuilders():
    return (DefaultFormatBuilder(TOOLTIPS_CONSTANTS.WT_EVENT_SHELL_BATTLE, TOOLTIPS_CONSTANTS.COMPLEX_UI, WtBattleShellTooltipData(contexts.ToolTipContext(None))),)
