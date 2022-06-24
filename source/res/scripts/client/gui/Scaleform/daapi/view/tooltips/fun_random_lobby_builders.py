# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/fun_random_lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
from gui.Scaleform.daapi.view.lobby.fun_random.tooltips.calendar_day_tooltip import FunRandomCalendarDayTooltip
from gui.Scaleform.daapi.view.lobby.fun_random.tooltips.quests_preview_tooltip import FunRandomQuestsPreviewTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_CALENDAR_DAY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomCalendarDayTooltip(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomQuestsPreviewTooltip(contexts.QuestsBoosterContext())))
