# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/tooltips/lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, vehicle
from gui.shared.tooltips.builders import DataBuilder
from fun_random.gui.shared.tooltips.contexts import FunRandomCarouselContext
from fun_random.gui.Scaleform.daapi.view.lobby.feature.tooltips.calendar_day_tooltip import FunRandomCalendarDayTooltip
from fun_random.gui.Scaleform.daapi.view.lobby.feature.tooltips.quests_preview_tooltip import FunRandomQuestsPreviewTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_CALENDAR_DAY, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomCalendarDayTooltip(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FunRandomQuestsPreviewTooltip(contexts.QuestsBoosterContext())), DataBuilder(TOOLTIPS_CONSTANTS.FUN_RANDOM_CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, vehicle.VehicleInfoTooltipData(FunRandomCarouselContext())))
