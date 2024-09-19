# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_battles_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder, TooltipWindowBuilder
from gui.shared.tooltips.event_battles_tooltips import EventBattlesSelectorTooltip, EventBattlesServerPrimeTime, EventBattlesCalendar, EventQuestsTooltipData, EventTicketTooltipWindowData, EventLootBoxTooltipWindowData, EventCarouselVehicleTooltipData, EventBuyLootBoxTooltipWindowData, EventStampTooltipWindowData, EventGiftTokenTooltipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventBattlesSelectorTooltip(contexts.ToolTipContext(None))),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_SERVER_PRIMETIME, TOOLTIPS_CONSTANTS.COMPLEX_UI, EventBattlesServerPrimeTime(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_CALENDAR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventBattlesCalendar(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventQuestsTooltipData(contexts.QuestsBoosterContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_BATTLES_TICKET, None, EventTicketTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_STAMP, None, EventStampTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_LOOTBOX, None, EventLootBoxTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_BUY_LOOTBOX, None, EventBuyLootBoxTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, EventCarouselVehicleTooltipData(contexts.CarouselContext(), TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE)),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_GIFT_TOKEN, TOOLTIPS_CONSTANTS.EVENT_GIFT_TOKEN_UI, EventGiftTokenTooltipData(contexts.ToolTipContext(None))))
