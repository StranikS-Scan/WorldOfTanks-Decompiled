# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/filter/__init__.py
import typing
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui import GUI_NATIONS, TANKMEN_ROLES_ORDER_DICT
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType, FilterToggleGroupModel, FilterToggleButtonModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.personal_data_card_model import DataCardFilter
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanLocation, TankmanKind
from gui.impl.lobby.crew.filter.state import FilterState
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
if typing.TYPE_CHECKING:
    from typing import Iterable, Optional
    from gui.impl.gen_utils import DynAccessor
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


def getNationSettings(customTooltipBody=None):
    tooltipBody = customTooltipBody or R.strings.crew.filter.tooltip.nation.vehicles.body()
    return FilterGroupSettings(toggleID=ToggleGroupType.NATION.value, labelResId=R.strings.crew.filter.group.nation.title(), toggleType=ToggleGroupType.NATION, toggles=[ ToggleButtonSettings(toggleID=nation, icon=R.images.gui.maps.icons.filters.nations.dyn(nation)(), tooltipHeader=R.strings.nations.dyn(nation)(), tooltipBody=tooltipBody) for nation in GUI_NATIONS ])


def getTankmanKindSettings(labelResId=R.invalid(), options=None, dismissedTooltipTargetId=R.invalid()):
    kindList = options or (TankmanKind.RECRUIT, TankmanKind.TANKMAN, TankmanKind.DISMISSED)
    toggles = []
    for kind in kindList:
        if kind == TankmanKind.DISMISSED:
            toggles.append(ToggleButtonSettings(toggleID=kind.value, icon=R.images.gui.maps.icons.tankmen.card.location.dismissed(), tooltipContentId=R.views.lobby.crew.tooltips.DismissedToggleTooltip(), tooltipTargetId=dismissedTooltipTargetId))
        toggles.append(_createTankmanKindToggle(kind.value))

    return FilterGroupSettings(toggleID=ToggleGroupType.TANKMANKIND.value, toggleType=ToggleGroupType.TANKMANKIND, labelResId=labelResId, toggles=toggles)


def getTankmanLocationSettings():
    toggles = _getTankmanLocationToggles() + [ _createTankmanKindToggle(kind.value) for kind in (TankmanKind.RECRUIT, TankmanKind.TANKMAN) ]
    return FilterGroupSettings(toggleID=ToggleGroupType.LOCATION.value, labelResId=R.invalid(), toggleType=ToggleGroupType.LOCATION, toggles=toggles)


def getVehicleLocationSettings():
    return FilterGroupSettings(toggleID=ToggleGroupType.LOCATION.value, labelResId=R.strings.crew.common.filter.location(), toggleType=ToggleGroupType.LOCATION, toggles=[ToggleButtonSettings(toggleID=VEHICLE_LOCATION_IN_HANGAR, icon=R.images.gui.maps.icons.tankmen.card.location.in_barracks(), tooltipHeader=R.strings.crew.tankChange.tooltip.location.header(), tooltipBody=R.strings.crew.tankChange.tooltip.location.body())])


def getTankmanRoleSettings(hasDiscount=False):
    return FilterGroupSettings(toggleID=ToggleGroupType.TANKMANROLE.value, labelResId=R.strings.crew.filter.group.tankmanRole.title(), toggleType=ToggleGroupType.TANKMANROLE, hasDiscount=hasDiscount, toggles=[ ToggleButtonSettings(toggleID=role, icon=R.images.gui.maps.icons.tankmen.roles.c_14x14.dyn(role)(), tooltipHeader=R.strings.item_types.tankman.roles.dyn(role)(), tooltipBody=R.strings.crew.filter.tooltip.tankmanRole.body()) for role in TANKMEN_ROLES_ORDER_DICT['plain'] ])


def getVehicleTypeSettings(labelResId=R.strings.crew.filter.group.vehicleType.barracks.title(), customTooltipBody=R.strings.crew.filter.tooltip.vehicleType.body()):
    return FilterGroupSettings(toggleID=ToggleGroupType.VEHICLETYPE.value, labelResId=labelResId, toggleType=ToggleGroupType.VEHICLETYPE, toggles=[ ToggleButtonSettings(toggleID=vehicleType, icon=R.images.gui.maps.icons.vehicleTypes.extraSmall.dyn(vehicleType.replace('-', '_'))(), tooltipHeader=R.strings.menu.header.vehicleType.dyn(vehicleType.replace('-', '_'))(), tooltipBody=customTooltipBody) for vehicleType in VEHICLE_TYPES_ORDER ])


def getVehicleTierSettings(labelResId=R.strings.crew.filter.group.vehicleTier.longTitle()):
    return FilterGroupSettings(toggleID=ToggleGroupType.VEHICLETIER.value, labelResId=labelResId, toggleType=ToggleGroupType.VEHICLETIER, toggles=[ ToggleButtonSettings(toggleID=str(level)) for level in xrange(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1) ])


def getVehicleGradeSettings(options=None, withLocation=False, labelResId=R.strings.crew.filter.group.special.title(), tooltipDynAccessor=R.strings.crew.filter.tooltip.vehicleGrade):
    vehicleGradeIcons = {GRADE_PREMIUM: R.images.gui.maps.icons.library.prem_small_icon(),
     GRADE_ELITE: R.images.gui.maps.icons.library.elite_small_icon(),
     GRADE_PRIMARY: R.images.gui.maps.icons.library.favorite_medium()}
    grades = options or VEHICLE_GRADES
    locationToggles = _getTankmanLocationToggles() if withLocation else []
    return FilterGroupSettings(toggleID=ToggleGroupType.VEHICLEGRADE.value, toggleType=ToggleGroupType.VEHICLEGRADE, labelResId=labelResId, toggles=locationToggles + [ ToggleButtonSettings(toggleID=grade, icon=vehicleGradeIcons.get(grade), tooltipBody=tooltipDynAccessor.dyn(grade).body(), tooltipHeader=tooltipDynAccessor.dyn(grade).title()) for grade in grades ])


def getPersonalDataCardTypeSettings():
    return FilterGroupSettings(toggleID=ToggleGroupType.PERSONALDATATYPE.value, toggleType=ToggleGroupType.PERSONALDATATYPE, labelResId=R.strings.crew.personalData.filter.type.title(), toggles=[ ToggleButtonSettings(toggleID=filterType.value, icon=R.images.gui.maps.icons.crew.personalData.c_34x24.dyn(filterType.value)(), tooltipBody=R.strings.crew.personalData.filter.tooltip.type.dyn(filterType.value).body(), tooltipHeader=R.strings.crew.personalData.filter.tooltip.type.dyn(filterType.value).title()) for filterType in (DataCardFilter.SUITABLESKIN, DataCardFilter.DOCUMENT) ])


def _createTankmanKindToggle(tankmanKind):
    tankmanKindIcons = {TankmanKind.TANKMAN.value: R.images.gui.maps.icons.library.tankman(),
     TankmanKind.RECRUIT.value: R.images.gui.maps.icons.library.friendshipIcon_1(),
     TankmanKind.DISMISSED.value: R.images.gui.maps.icons.tankmen.card.location.dismissed()}
    return ToggleButtonSettings(toggleID=tankmanKind, icon=tankmanKindIcons.get(tankmanKind), tooltipBody=R.strings.crew.filter.tooltip.tankmanKind.dyn(tankmanKind).body(), tooltipHeader=R.strings.crew.filter.tooltip.tankmanKind.dyn(tankmanKind).title())


def _getTankmanLocationToggles():
    return [ ToggleButtonSettings(toggleID=location.value, icon=R.images.gui.maps.icons.tankmen.card.location.dyn(location.value)(), tooltipHeader=R.strings.crew.tankmanList.tooltip.location.dyn(location.value).title(), tooltipBody=R.strings.crew.tankmanList.tooltip.location.dyn(location.value).body()) for location in [TankmanLocation.INBARRACKS, TankmanLocation.INTANK] ]
