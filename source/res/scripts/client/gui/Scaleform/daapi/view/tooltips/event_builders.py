# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import event
from gui.shared.tooltips.builders import DataBuilder, DefaultFormatBuilder, TooltipWindowBuilder
from gui.shared.tooltips.event import GfBannerTooltipData, EventDailyInfoTooltipData, EventSelectorPerfInfoTooltip
from vehicle_items_builders import AdvancedShellBuilder, _shellAdvancedBlockCondition
from gui.shared.tooltips.advanced import HangarShellAdvanced
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventVehicleInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_COST, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventCostTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_INTERROGATION, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventInterrogationTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_KEY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventKeyInfoTooltipData(contexts.CarouselContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_EFFICIENT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventEfficientInfoTooltipData(contexts.CarouselContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.EVENT_DAILY_INFO, None, EventDailyInfoTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SELECTOR_PERF_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventSelectorPerfInfoTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventSelectorWarningTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BAN_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventBanInfoToolTipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.HalloweenQuestsPreviewTooltipData(contexts.ToolTipContext(None))),
     DefaultFormatBuilder(TOOLTIPS_CONSTANTS.HALLOWEEN_NO_SUITABLE_VEHICLE_FOR_QUEST, TOOLTIPS_CONSTANTS.COMPLEX_UI, event.EventNoSuitableVehicleForQuest(contexts.ToolTipContext(None))),
     AdvancedShellBuilder(TOOLTIPS_CONSTANTS.TECH_MAIN_SHELL_EVENT, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventShellBlockToolTipData(contexts.TechMainContext()), HangarShellAdvanced(contexts.TechMainContext()), condition=_shellAdvancedBlockCondition(contexts.TechMainContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.GF_BANNER_TOOLTIP, None, GfBannerTooltipData(contexts.ToolTipContext(None))))
