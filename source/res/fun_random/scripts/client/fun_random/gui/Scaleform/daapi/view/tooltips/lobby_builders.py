# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
from fun_random.gui.Scaleform.daapi.view.lobby.feature.tooltips.calendar_day_tooltip import FunRandomCalendarDayTooltip, FunRandomModeSelectorCalendarTooltip
from fun_random.gui.Scaleform.daapi.view.lobby.feature.tooltips.rewards_tooltip import FunRandomRewardsTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_CALENDAR_DAY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomCalendarDayTooltip(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_MODE_SELECTOR_CALENDAR_DAY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomModeSelectorCalendarTooltip(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_REWARDS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomRewardsTooltip(contexts.ToolTipContext(None))))
