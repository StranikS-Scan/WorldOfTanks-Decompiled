# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/tooltips/comp7_lobby_builders.py
from comp7.gui.Scaleform.daapi.view.lobby.tooltips.comp7_calendar_day_extended_tooltip import Comp7CalendarDayExtendedTooltip
from comp7.gui.Scaleform.daapi.view.lobby.tooltips.comp7_calendar_day_tooltip import Comp7CalendarDayTooltip
from comp7.gui.Scaleform.daapi.view.lobby.tooltips.comp7_selector_tooltip import Comp7SelectorTooltip, Comp7SelectorUnavailableTooltip
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.shared.tooltips.comp7_tooltips import RoleSkillLobbyTooltipData, BattleResultsRatingPointsTooltip, BattleResultsTournamentRatingPointsTooltip, BattleResultsTrainingRatingPointsTooltip, Comp7SelectableRewardTooltip
from comp7.gui.shared.tooltips.contexts import Comp7RoleSkillLobbyContext
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(COMP7_TOOLTIPS.COMP7_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7SelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.COMP7_SELECTOR_UNAVAILABLE_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7SelectorUnavailableTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7CalendarDayTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_EXTENDED_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7CalendarDayExtendedTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.COMP7_ROLE_SKILL_LOBBY_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, RoleSkillLobbyTooltipData(Comp7RoleSkillLobbyContext())),
     DataBuilder(COMP7_TOOLTIPS.COMP7_BATTLE_RESULTS_RATING_POINTS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleResultsRatingPointsTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.TOURNAMENT_COMP7_BATTLE_RESULTS_RATING_POINTS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleResultsTournamentRatingPointsTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.TRAINING_COMP7_BATTLE_RESULTS_RATING_POINTS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, BattleResultsTrainingRatingPointsTooltip(contexts.ToolTipContext(None))),
     DataBuilder(COMP7_TOOLTIPS.COMP7_SELECTABLE_REWARD, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, Comp7SelectableRewardTooltip(contexts.ToolTipContext(None))))
