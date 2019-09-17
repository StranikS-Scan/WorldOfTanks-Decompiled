# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/festival_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import festival
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FESTIVAL_ITEM, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, festival.FestivalTooltipData(contexts.FestivalItemContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.RACE_VEHICLE, None, festival.RaceVehicleTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.RACE_WIDGET, None, festival.RaceWidgetTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.RACING_CUP, None, festival.RacingCupTooltipWindowData(contexts.ToolTipContext(None))))
