# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/tooltips/tooltip_builders.py
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import TooltipWindowBuilder, DataBuilder
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from white_tiger.gui.shared.tooltips.white_tiger_tooltips import WhiteTigerTicketTooltipWindowData, WhiteTigerStampTooltipWindowData, WhiteTigerBattleCalendar
from white_tiger.gui.white_tiger_gui_constants import WHITE_TIGER_BATTLES_TICKET, WHITE_TIGER_STAMP
from white_tiger.gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (TooltipWindowBuilder(WHITE_TIGER_BATTLES_TICKET, None, WhiteTigerTicketTooltipWindowData(contexts.ToolTipContext(None))), TooltipWindowBuilder(WHITE_TIGER_STAMP, None, WhiteTigerStampTooltipWindowData(contexts.ToolTipContext(None))), DataBuilder(ModeSelectorTooltipsConstants.WHITE_TIGER_BATTLES_CALENDAR_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, WhiteTigerBattleCalendar(contexts.ToolTipContext(None))))
