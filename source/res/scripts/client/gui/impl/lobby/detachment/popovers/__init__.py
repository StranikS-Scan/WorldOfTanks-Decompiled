# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/__init__.py
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from crew2 import settings_globals
from gui import GUI_NATIONS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.recruit_type_constants import RecruitTypeConstants
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_type_constants import VehicleTypeConstants
from gui.impl.gen.view_models.views.lobby.detachment.popovers.toggle_group_model import ToggleGroupModel

class ToggleButtonSettings(object):

    def __init__(self, toggleID, icon=R.invalid(), tooltipHeader=None, tooltipBody=None):
        self.id = toggleID
        self.icon = icon
        self.tooltipHeader = tooltipHeader
        self.tooltipBody = tooltipBody


class PopoverFilterGroups(object):
    NATION = 'nation'
    VEHICLE_TYPE = 'vehicle_type'
    RECRUIT_ROLES = 'recruit_roles'
    COMMANDER_TYPE = 'commander_type'
    INSTRUCTOR_CLASS = 'instructor_class'
    VEHICLE_LEVEL = 'vehicle_level'


def getNationSettings(customTooltipBody=None):
    tooltipBody = customTooltipBody or R.strings.tooltips.filterToggle.nation.detachment.body()
    return {'id': PopoverFilterGroups.NATION,
     'label': R.strings.detachment.toggleFilterPopover.group.nation.label(),
     'toggleType': ToggleGroupModel.NATION,
     'toggles': [ ToggleButtonSettings(toggleID=nation, tooltipHeader=R.strings.nations.dyn(nation)(), tooltipBody=tooltipBody) for nation in GUI_NATIONS ]}


def getVehicleTypeSettings(customTooltipBody=None, customLabel=None):
    tooltipBody = customTooltipBody or R.strings.tooltips.filterToggle.specialization.detachment.body()
    label = customLabel or R.strings.detachment.toggleFilterPopover.group.specialization.label()
    return {'id': PopoverFilterGroups.VEHICLE_TYPE,
     'label': label,
     'toggleType': ToggleGroupModel.SPECIALIZATION,
     'toggles': [ToggleButtonSettings(toggleID=VehicleTypeConstants.LIGHT_TANK, tooltipHeader=R.strings.item_types.vehicle.tags.light_tank.name(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=VehicleTypeConstants.MEDIUM_TANK, tooltipHeader=R.strings.item_types.vehicle.tags.medium_tank.name(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=VehicleTypeConstants.HEAVY_TANK, tooltipHeader=R.strings.item_types.vehicle.tags.heavy_tank.name(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=VehicleTypeConstants.AT_SPG, tooltipHeader=R.strings.item_types.vehicle.tags.at_spg.name(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=VehicleTypeConstants.SPG, tooltipHeader=R.strings.item_types.vehicle.tags.spg.name(), tooltipBody=tooltipBody)]}


def getRecruitRoleSettings():
    tooltipBody = R.strings.tooltips.filterToggle.speciality.recruit.body()
    return {'id': PopoverFilterGroups.RECRUIT_ROLES,
     'label': R.strings.detachment.toggleFilterPopover.group.speciality.label(),
     'toggleType': ToggleGroupModel.SPECIALITY,
     'toggles': [ToggleButtonSettings(toggleID=RecruitTypeConstants.COMMANDER, tooltipHeader=R.strings.item_types.tankman.roles.commander(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=RecruitTypeConstants.GUNNER, tooltipHeader=R.strings.item_types.tankman.roles.gunner(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=RecruitTypeConstants.DRIVER, tooltipHeader=R.strings.item_types.tankman.roles.driver(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=RecruitTypeConstants.RADIOMAN, tooltipHeader=R.strings.item_types.tankman.roles.radioman(), tooltipBody=tooltipBody),
                 ToggleButtonSettings(toggleID=RecruitTypeConstants.LOADER, tooltipHeader=R.strings.item_types.tankman.roles.loader(), tooltipBody=tooltipBody)]}


class CommanderToggleTypes(object):
    HISTORICAL = 'historical'
    NON_HISTORICAL = 'nonHistorical'
    USED = 'used'


def getCommanderTypeSettings():
    return {'id': PopoverFilterGroups.COMMANDER_TYPE,
     'label': R.strings.detachment.toggleFilterPopover.group.commanderType.label(),
     'toggleType': ToggleGroupModel.DEFAULT,
     'toggles': [ToggleButtonSettings(toggleID=CommanderToggleTypes.HISTORICAL, icon=R.images.gui.maps.icons.filters.historical(), tooltipHeader=R.strings.tooltips.filterToggle.historical.profile.header(), tooltipBody=R.strings.tooltips.filterToggle.historical.profile.body()), ToggleButtonSettings(toggleID=CommanderToggleTypes.NON_HISTORICAL, icon=R.images.gui.maps.icons.filters.non_historical(), tooltipHeader=R.strings.tooltips.filterToggle.nonHistorical.profile.header(), tooltipBody=R.strings.tooltips.filterToggle.nonHistorical.profile.body()), ToggleButtonSettings(toggleID=CommanderToggleTypes.USED, icon=R.images.gui.maps.icons.filters.crew_check(), tooltipHeader=R.strings.tooltips.filterToggle.used.profile.header(), tooltipBody=R.strings.tooltips.filterToggle.used.profile.body())]}


def getInstructorGradeSettings():
    return {'id': PopoverFilterGroups.INSTRUCTOR_CLASS,
     'label': R.strings.detachment.toggleFilterPopover.group.instructorGrade.label(),
     'toggleType': ToggleGroupModel.GRADE,
     'toggles': [ ToggleButtonSettings(toggleID=str(classID), icon=R.images.gui.maps.icons.filters.dyn('filter_grade_{}'.format(classID))(), tooltipHeader=R.strings.tooltips.filterToggle.grade.instructors.dyn('grade' + str(classID)).header(), tooltipBody=R.strings.tooltips.filterToggle.grade.instructors.body()) for classID in settings_globals.g_instructorSettingsProvider.classes.getClassIDs() ]}


def getVehicleLevelSettings():
    return {'id': PopoverFilterGroups.VEHICLE_LEVEL,
     'label': R.strings.detachment.toggleFilterPopover.group.vehicleLevel.label(),
     'toggleType': ToggleGroupModel.LEVEL,
     'toggles': [ ToggleButtonSettings(toggleID=str(level), tooltipHeader=R.strings.tooltips.filterToggle.level.vehicle.header(), tooltipBody=R.strings.tooltips.filterToggle.level.vehicle.body()) for level in xrange(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1) ]}
