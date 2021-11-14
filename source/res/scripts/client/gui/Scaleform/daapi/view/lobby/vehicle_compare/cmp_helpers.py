# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_helpers.py
import operator
from frameworks.wulf import WindowLayer
from helpers import dependency
from items import tankmen
from shared_utils import first
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_top_modules import TopModulesChecker
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.game_control.veh_comparison_basket import PARAMS_AFFECTED_TANKMEN_SKILLS
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman, BROTHERHOOD_SKILL_NAME
from items.components.c11n_components import SeasonType
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
MODULES_INSTALLING_ORDER = (GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.RADIO)
NOT_AFFECTED_DEVICES = {}
NOT_AFFECTED_EQUIPMENTS = {'smallRepairkit', 'smallMedkit', 'handExtinguishers'}
OPTIONAL_DEVICE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.OPTIONALDEVICE]
EQUIPMENT_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.EQUIPMENT]
BATTLE_BOOSTER_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_BOOSTER]

def createTankman(nationID, vehicleTypeID, role, roleLevel, skills, vehicle, vehicleSlotIDx):
    descr = tankmen.generateCompactDescr(tankmen.generatePassport(nationID), vehicleTypeID, role, roleLevel, skills)
    newTankmen = Tankman(descr, vehicle=vehicle, vehicleSlotIdx=vehicleSlotIDx)
    if BROTHERHOOD_SKILL_NAME in skills:
        newTankmen.setBrotherhoodActivity(True)
        newTankmen.rebuildSkills()
    return newTankmen


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


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def getCmpConfiguratorMainView(appLoader=None):
    cmpConfiguratorMain = appLoader.getApp().containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR})
    return cmpConfiguratorMain


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getSuitableCamouflage(vehicle, c11nService=None):
    return first(c11nService.getCamouflages(vehicle=vehicle).itervalues())


def isCamouflageSet(vehicle):
    return bool(vehicle.getBonusCamo())


@dependency.replace_none_kwargs(factory=IGuiItemsFactory, itemsCache=IItemsCache)
def applyCamouflage(vehicle, select, factory=None, itemsCache=None):
    if select:
        if not vehicle.outfits:
            vehicle.createAppliedOutfits(itemsCache.items)
        camo = getSuitableCamouflage(vehicle)
        if camo:
            season = first(camo.seasons)
            outfit = vehicle.getOutfit(season)
            outfit = outfit or factory.createOutfit(vehicleCD=vehicle.descriptor.makeCompactDescr())
            outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).set(camo.intCD)
            vehicle.setCustomOutfit(season, outfit)
    else:
        removeVehicleCamouflages(vehicle)


def removeVehicleCamouflages(vehicle):
    camo = getSuitableCamouflage(vehicle)
    if camo is None:
        return
    else:
        for season in SeasonType.SEASONS:
            outfit = vehicle.getOutfit(season)
            if outfit:
                outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()
                vehicle.removeOutfitForSeason(season)

        return


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
