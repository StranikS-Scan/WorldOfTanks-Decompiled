# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/ranked_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import ranked, advanced
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_calendar_day_tooltip import RankedCalendarDayTooltip
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_calendar_steps_tooltip import RankedCalendarStepsTooltip
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_selector_tooltip import RankedSelectorTooltip, RankedUnavailableTooltip
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_step_tooltip import RankedStepTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_RANK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, ranked.RankedTooltipData(contexts.RankedRankContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_STEP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedStepTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedCalendarDayTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_CALENDAR_STEPS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedCalendarStepsTooltip(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RANKED_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedSelectorTooltip(contexts.ToolTipContext(None)), advanced.RankedAdvanced(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RANKED_UNAVAILABLE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedUnavailableTooltip(contexts.ToolTipContext(None)), advanced.RankedAdvanced(contexts.ToolTipContext(None))))
