# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/tooltips/wt_lobby_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder, TooltipWindowBuilder
from wt_tooltips import EventBattlesSelectorTooltip, EventBattlesServerPrimeTime, EventBattlesCalendar, EventQuestsTooltipData, EventTicketTooltipWindowData, EventLootBoxTooltipWindowData, EventCarouselVehicleTooltipData, EventBuyLootBoxTooltipWindowData, EventStampTooltipWindowData, EventMainPrizeDiscountTooltipWindowData, EventBattlesEndData, WtGuaranteedRewardTooltipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventBattlesSelectorTooltip(contexts.ToolTipContext(None))),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_SERVER_PRIMETIME, TOOLTIPS_CONSTANTS.COMPLEX_UI, EventBattlesServerPrimeTime(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_CALENDAR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventBattlesCalendar(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventQuestsTooltipData(contexts.QuestsBoosterContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_TICKET, None, EventTicketTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_STAMP, None, EventStampTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_MAIN_PRIZE_DISCOUNT, None, EventMainPrizeDiscountTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_LOOTBOX, None, EventLootBoxTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_BUY_LOOTBOX, None, EventBuyLootBoxTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, EventCarouselVehicleTooltipData(contexts.CarouselContext(), TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE)),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_END, None, EventBattlesEndData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.WT_GUARANTED_REWARD, None, WtGuaranteedRewardTooltipData(contexts.ToolTipContext(None))))
