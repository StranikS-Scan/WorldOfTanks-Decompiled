# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import event
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventBonusesInfoTooltipData(contexts.TankmanHangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_TANK_RENT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventTankRentInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_TANK_REPAIR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventTankRepairInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_CREW_BOOSTER_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventCrewBoosterInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_COMMANDER_IN_BATTLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventCommanderInBattle(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BANNER_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventBannerInfoTooltipData(contexts.HangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventVehicleInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_COMMANDERS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventCommandersInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_MISSION_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventMissionInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventSelectorWarningTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_CRDITS_ERROR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventCreditsErrorTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_TOKEN_ERROR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventTokenErrorTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_GOLD_ERROR, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventGoldErrorTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BAN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventBanInfoToolTipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.HalloweenQuestsPreviewTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_TOKEN_BONUS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.HalloweenTokenBonusesInfoTooltipData(contexts.TankmanHangarContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_TOKEN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventTokenInfoTooltipData(contexts.ToolTipContext(None))),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_NO_SUITABLE_VEHICLE_FOR_QUEST, TOOLTIPS_CONSTANTS.COMPLEX_UI, event.EventNoSuitableVehicleForQuest(contexts.ToolTipContext(None))))
