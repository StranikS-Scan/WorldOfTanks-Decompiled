# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/tooltips/event_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import TooltipWindowBuilder, DataBuilder
from historical_battles.gui.impl.lobby.tooltips.entry_point_tooltip import EntryPointTooltipContentWindowData
from historical_battles.gui.impl.lobby.tooltips.interactive_object_tooltip import HangarInteractiveObjectTooltipContentWindowData
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltipWindowData
from historical_battles.gui.impl.lobby.tooltips.quest_flag_tooltip import QuestFlagTooltip
from historical_battles.gui.shared.tooltips.quests import HBUnavailableQuestTooltipData
from historical_battles.gui.shared.tooltips.vehicle import HBVehicleInfoTooltipData
from historical_battles.gui.shared.tooltips.special_vehicles import HBSpecialVehiclesTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_calendar_tooltip import HBCalendarTooltipData
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (TooltipWindowBuilder(TOOLTIPS_CONSTANTS.HANGAR_INTERACTIVE_OBJECT, None, HangarInteractiveObjectTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.ENTRY_POINT_TOOLTIP, None, EntryPointTooltipContentWindowData(contexts.ToolTipContext(None))),
     TooltipWindowBuilder(TOOLTIPS_CONSTANTS.HB_ORDER_TOOLTIP, None, OrderTooltipWindowData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.HB_UNAVAILABLE_QUEST, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, HBUnavailableQuestTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HB_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, QuestFlagTooltip(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HB_VEHICLE, TOOLTIPS_CONSTANTS.VEHICLE_INFO_UI, HBVehicleInfoTooltipData(contexts.DefaultContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.HB_CALENDAR_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, HBCalendarTooltipData(contexts.ToolTipContext(None))),
     DataBuilder(TOOLTIPS_CONSTANTS.HB_SPECIAL_VEHICLES_TOOLTIP, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, HBSpecialVehiclesTooltip(contexts.ToolTipContext(None))))
