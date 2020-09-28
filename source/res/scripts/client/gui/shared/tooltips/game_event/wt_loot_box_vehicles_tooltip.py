# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/game_event/wt_loot_box_vehicles_tooltip.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_vehicle_tooltip_view import WtEventLootboxVehicleTooltipView
from gui.shared.tooltips import WulfTooltipData

class WtEventLootBoxVehiclesWindowData(WulfTooltipData):

    def __init__(self, context):
        super(WtEventLootBoxVehiclesWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX_VEHICLES)

    def getTooltipContent(self, vehiclesList, *args, **kwargs):
        return WtEventLootboxVehicleTooltipView(vehiclesList)
