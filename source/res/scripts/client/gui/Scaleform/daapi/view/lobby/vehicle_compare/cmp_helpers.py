# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_helpers.py
import operator
from helpers import dependency
from items import tankmen
from shared_utils import first
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_top_modules import TopModulesChecker
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import g_appLoader
from gui.game_control.veh_comparison_basket import PARAMS_AFFECTED_TANKMEN_SKILLS
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman
from items.components.c11n_components import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
MODULES_INSTALLING_ORDER = (GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.RADIO)
NOT_AFFECTED_DEVICES = {}
NOT_AFFECTED_EQUIPMENTS = {'handExtinguishers',
 'autoExtinguishers',
 'smallMedkit',
 'largeMedkit',
 'smallRepairkit',
 'largeRepairkit'}
OPTIONAL_DEVICE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.OPTIONALDEVICE]
EQUIPMENT_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.EQUIPMENT]
BATTLE_BOOSTER_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_BOOSTER]

def createTankman(nationID, vehicleTypeID, role, roleLevel, skills):
    descr = tankmen.generateCompactDescr(tankmen.generatePassport(nationID), vehicleTypeID, role, roleLevel, skills)
    return Tankman(descr)


def sortSkills(skillsSet):
    return sorted(skillsSet, key=PARAMS_AFFECTED_TANKMEN_SKILLS.index)


def _getAvailableSkillsByRoles(availableSkills):
    outcome = {}
    for role, skills in tankmen.SKILLS_BY_ROLES.iteritems():
        intersection = skills.intersection(set(availableSkills))
        if intersection:
            outcome[role] = intersection

    return outcome


_PARAMS_AFFECTED_SKILLS_BY_ROLES = _getAvailableSkillsByRoles(PARAMS_AFFECTED_TANKMEN_SKILLS)

def getVehicleCrewSkills(vehicle):
    descCrewRoles = vehicle.descriptor.type.crewRoles
    mainRoles = map(operator.itemgetter(0), descCrewRoles)
    outcome = [ [role, _PARAMS_AFFECTED_SKILLS_BY_ROLES[role]] for role in mainRoles ]
    leftRoles = set(tankmen.ROLES.difference(set(mainRoles)))
    if leftRoles:
        for idx, rolesRange in reversed(list(enumerate(descCrewRoles))):
            for role in rolesRange:
                if role in leftRoles:
                    leftRoles.remove(role)
                    outcome[idx][1] |= _PARAMS_AFFECTED_SKILLS_BY_ROLES[role]
                    if not leftRoles:
                        return outcome

    else:
        return outcome


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVehCrewInfo(vehIntCD, itemsCache=None):
    levelsByIndexes = {}
    nativeVehiclesByIndexes = {}
    if itemsCache is not None:
        hangarVehicle = itemsCache.items.getItemByCD(vehIntCD)
        for roleIdx, tman in hangarVehicle.crew:
            if tman:
                levelsByIndexes[roleIdx] = int(tman.roleLevel)
                nativeVehiclesByIndexes[roleIdx] = itemsCache.items.getItemByCD(tman.vehicleNativeDescr.type.compactDescr)

    return (levelsByIndexes, nativeVehiclesByIndexes)


def createTankmans(crewData):
    return [ (strCD[0], Tankman(strCD[1]) if strCD[1] else None) for strCD in crewData ]


def isEquipmentSame(equipment1, equipment2):
    if equipment1 is None or equipment2 is None:
        return False
    elif len(equipment1) != len(equipment2):
        return False
    else:
        for i in xrange(len(equipment1)):
            if equipment1[i] != equipment2[i]:
                return False

        return True


def getCmpConfiguratorMainView():
    cmpConfiguratorMain = g_appLoader.getApp().containerManager.getView(ViewTypes.LOBBY_SUB, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR})
    return cmpConfiguratorMain


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getSuitableCamouflage(vehicle, c11nService=None):
    return first(c11nService.getCamouflages(vehicle=vehicle).itervalues())


def isCamouflageSet(vehicle):
    return bool(vehicle.getBonusCamo())


@dependency.replace_none_kwargs(factory=IGuiItemsFactory)
def applyCamouflage(vehicle, select, factory=None):
    if select:
        camo = getSuitableCamouflage(vehicle)
        if camo:
            season = first(camo.seasons)
            outfit = vehicle.getCustomOutfit(season)
            outfit = outfit or factory.createOutfit(isEnabled=True, isInstalled=True)
            outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).set(camo)
            vehicle.setCustomOutfit(season, outfit)
    else:
        removeVehicleCamouflages(vehicle)


def removeVehicleCamouflages(vehicle):
    for season in SeasonType.SEASONS:
        outfit = vehicle.getOutfit(season)
        if outfit:
            outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()


def getVehicleModules(vehicle):
    return (vehicle.chassis,
     vehicle.turret,
     vehicle.gun,
     vehicle.engine,
     vehicle.radio)


def getVehicleTopModules(vehicle):
    checker = TopModulesChecker(vehicle)
    topModules = checker.process()
    checker.clear()
    return sorted(topModules, key=lambda module: MODULES_INSTALLING_ORDER.index(module.itemTypeID))


def isVehicleTopConfiguration(vehicle):
    selectedModules = getVehicleModules(vehicle)
    topModules = getVehicleTopModules(vehicle)
    topModulesFromStock = not topModules
    return True if topModulesFromStock else all((bool(item in selectedModules) for item in topModules))
