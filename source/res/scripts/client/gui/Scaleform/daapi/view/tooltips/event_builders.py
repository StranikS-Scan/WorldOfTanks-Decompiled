# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/event_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder, TooltipWindowBuilder
from gui.shared.tooltips.game_event.lobby_header import EventSelectorTooltip, EventUnavailableTooltip, EventQuestsTooltipData
from gui.shared.tooltips.game_event.wt_boss_ticket_tooltip import WtEventBossTicketTooltipWindowData
from gui.shared.tooltips.game_event.wt_loot_box_tooltip import WtEventLootBoxTooltipWindowData
from gui.shared.tooltips.game_event.wt_loot_box_vehicles_tooltip import WtEventLootBoxVehiclesWindowData
__all__ = 'getTooltipBuilders'

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.EVENT_SELECTOR_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventSelectorTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.EVENT_UNAVAILABLE_UNFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventUnavailableTooltip(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.WT_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EventQuestsTooltipData(contexts.QuestsBoosterContext())),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.WT_EVENT_BOSS_TICKET, None, WtEventBossTicketTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX, None, WtEventLootBoxTooltipWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX_VEHICLES, None, WtEventLootBoxVehiclesWindowData(contexts.ToolTipContext(None))))
