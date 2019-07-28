# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, advanced
from gui.shared.tooltips import event
from gui.shared.tooltips.builders import DataBuilder, AdvancedDataBuilder
from gui.shared.tooltips.event import EventSelectorWarningTooltip
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_FACTION_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventFractionInfoTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_FRONT_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventFrontInfoTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_ENERGY_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventEnergyInfoTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_BANNER_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventBannerInfoTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_FACTION_INFO_WIN_SCREEN, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventFractionInfoWinScreenTooltipData(contexts.QuestsBoosterContext())),
     AdvancedDataBuilder(TOOLTIPS_CONSTANTS.EVENT_AWARD_MODULE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventModuleBlockTooltipData(contexts.AwardContext()), advanced.HangarModuleAdvanced(contexts.AwardContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventSelectorWarningTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_GENERAL_PROGRESSION, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, event.EventGeneralProgressionInfoTooltipData(contexts.QuestsBoosterContext())))
