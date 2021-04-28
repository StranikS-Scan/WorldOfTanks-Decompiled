# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/weekend_brawl_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder
from gui.shared.tooltips.weekend_brawl_tooltips import WeekendBrawlSelectorTooltip, WeekendBrawlServerPrimeTime
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.WEEKEND_BRAWL_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, WeekendBrawlSelectorTooltip(contexts.ToolTipContext(None))), DefaultFormatBuilder(TOOLTIPS_CONSTANTS.WEEKEND_BRAWL_SERVER_PRIMETIME, TOOLTIPS_CONSTANTS.COMPLEX_UI, WeekendBrawlServerPrimeTime(contexts.ToolTipContext(None))))
