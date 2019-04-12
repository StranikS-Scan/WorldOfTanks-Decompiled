# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/ranked_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import advanced
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
from gui.shared.tooltips.ranked.rank_tooltip import RankedTooltipData
from gui.shared.tooltips.ranked.ranked_calendar_day_tooltip import RankedCalendarDayTooltip
from gui.shared.tooltips.ranked.ranked_calendar_steps_tooltip import RankedCalendarStepsTooltip
from gui.shared.tooltips.ranked.ranked_selector_tooltip import RankedSelectorTooltip, RankedUnavailableTooltip
from gui.shared.tooltips.ranked.ranked_step_tooltip import RankedStepTooltip
from gui.shared.tooltips.ranked.ranked_battles_division_tooltip import RankedDivisionTooltip
from gui.shared.tooltips.ranked.league_tooltip import BonusTooltipData
from gui.shared.tooltips.ranked.league_tooltip import LeagueTooltipData
from gui.shared.tooltips.ranked.league_tooltip import EfficiencyTooltipData
from gui.shared.tooltips.ranked.league_tooltip import PositionTooltipData
from gui.shared.tooltips.ranked.ranked_year_reward_tooltip import RankedYearReward
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_RANK, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedTooltipData(contexts.RankedRankContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_BONUS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BonusTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_LEAGUE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, LeagueTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_EFFICIENCY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EfficiencyTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_POSITION, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, PositionTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_STEP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedStepTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedCalendarDayTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_CALENDAR_STEPS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedCalendarStepsTooltip(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RANKED_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedSelectorTooltip(contexts.ToolTipContext(None)), advanced.RankedAdvanced(contexts.ToolTipContext(None))),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.RANKED_UNAVAILABLE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedUnavailableTooltip(contexts.ToolTipContext(None)), advanced.RankedAdvanced(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_DIVISION_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedDivisionTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.RANKED_BATTLES_YEAR_REWARD, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RankedYearReward(contexts.ToolTipContext(None))))
