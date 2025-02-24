# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/filter/__init__.py
import typing
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui import GUI_NATIONS
from gui.impl.gen import R
from server_side_replay.gui.impl.gen.view_models.views.lobby.filter_toggle_group_model import ToggleGroupType, FilterToggleGroupModel, FilterToggleButtonModel
from server_side_replay.gui.impl.lobby.filter.state import FilterState
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
if typing.TYPE_CHECKING:
    from typing import Iterable, Optional
VEHICLE_FILTER = 'vehicle'
VEHICLE_LOCATION_IN_HANGAR = 'in_hangar'
GRADE_PREMIUM = 'premium'
GRADE_ELITE = 'elite'
GRADE_PRIMARY = 'primary'
VEHICLE_GRADES = (GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY)
SEARCH_MAX_LENGTH = 50

class ToggleButtonSettings(object):

    def __init__(self, toggleID, icon=R.invalid(), tooltipHeader=R.invalid(), tooltipBody=R.invalid(), tooltipContentId=R.invalid(), tooltipTargetId=R.invalid(), counter=0):
        self.id = toggleID
        self.icon = icon
        self.tooltipHeader = tooltipHeader
        self.tooltipBody = tooltipBody
        self.tooltipContentId = tooltipContentId
        self.tooltipTargetId = tooltipTargetId
        self.counter = counter

    def pack(self, model, state=None):
        model.setId(self.id)
        model.setIcon(self.icon)
        model.setIsSelected(True if state and self.id in state else False)
        model.setCounter(self.counter)
        model.tooltip.setBody(self.tooltipBody)
        model.tooltip.setHeader(self.tooltipHeader)
        model.tooltip.setContentId(self.tooltipContentId)
        model.tooltip.setTargetId(self.tooltipTargetId)


class FilterGroupSettings(object):

    def __init__(self, toggleID, labelResId, toggleType, toggles, hasDiscount=False):
        self.id = toggleID
        self.labelResId = labelResId
        self.toggleType = toggleType
        self.toggles = toggles
        self.hasDiscount = hasDiscount

    def pack(self, model, state=None):
        model.setId(self.id)
        model.setLabel(self.labelResId)
        model.setType(self.toggleType)
        model.setHasDiscount(self.hasDiscount)
        filters = model.getFilters()
        filters.clear()
        filters.invalidate()
        for toggle in self.toggles:
            vm = FilterToggleButtonModel()
            toggle.pack(vm, state[self.id] if state and self.id in state else None)
            filters.addViewModel(vm)

        return


def getNationSettings():
    tooltipBody = R.strings.replays.filter.tooltip.nation.vehicles.body()
    return FilterGroupSettings(toggleID=ToggleGroupType.NATION.value, labelResId=R.strings.replays.filter.group.nation.title(), toggleType=ToggleGroupType.NATION, toggles=[ ToggleButtonSettings(toggleID=nation, icon=R.images.gui.maps.icons.filters.nations.dyn(nation)(), tooltipHeader=R.strings.nations.dyn(nation)(), tooltipBody=tooltipBody) for nation in GUI_NATIONS ])


def getVehicleTypeSettings(labelResId=R.strings.replays.filter.group.vehicleType.barracks.title(), customTooltipBody=R.strings.replays.filter.tooltip.vehicleType.body()):
    return FilterGroupSettings(toggleID=ToggleGroupType.VEHICLETYPE.value, labelResId=labelResId, toggleType=ToggleGroupType.VEHICLETYPE, toggles=[ ToggleButtonSettings(toggleID=vehicleType, icon=R.images.gui.maps.icons.vehicleTypes.extraSmall.dyn(vehicleType.replace('-', '_'))(), tooltipHeader=R.strings.replays.filter.tooltip.vehicleType.header.dyn(vehicleType.replace('-', '_'))(), tooltipBody=customTooltipBody) for vehicleType in VEHICLE_TYPES_ORDER ])


def getVehicleTierSettings(labelResId=R.strings.replays.filter.group.vehicleTier.longTitle()):
    return FilterGroupSettings(toggleID=ToggleGroupType.VEHICLETIER.value, labelResId=labelResId, toggleType=ToggleGroupType.VEHICLETIER, toggles=[ ToggleButtonSettings(toggleID=str(level)) for level in xrange(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1) ])
