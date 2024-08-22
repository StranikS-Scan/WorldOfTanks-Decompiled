# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_helpers.py
from frameworks.wulf import WindowLayer
from helpers import dependency
from items import tankmen
from items.tankmen import SKILLS_BY_ROLES, ROLES_BY_SKILLS
from shared_utils import first
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_top_modules import TopModulesChecker
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman, BROTHERHOOD_SKILL_NAME
from items.components.c11n_components import SeasonType
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from constants import NEW_PERK_SYSTEM as NPS
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

def createTankman(nationID, vehicleTypeID, role, roleLevel, skills, vehicle, vehicleSlotIDx, rolesBonusSkills=None, bonusSkillNamesMaxLvl=None):
    bonusSkillsLevels = [[tankmen.MAX_SKILL_LEVEL] * NPS.MAX_BONUS_SKILLS_PER_ROLE, bonusSkillNamesMaxLvl or []]
    descr = tankmen.generateCompactDescr(tankmen.generatePassport(nationID), vehicleTypeID, role, roleLevel, skills, rolesBonusSkills=rolesBonusSkills)
    newTankmen = Tankman(descr, vehicle=vehicle, vehicleSlotIdx=vehicleSlotIDx, bonusSkillsLevels=bonusSkillsLevels)
    if BROTHERHOOD_SKILL_NAME in skills:
        newTankmen.setBrotherhoodActivity(True)
        newTankmen.rebuildSkills()
    return newTankmen


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


def isSkillMajor(skillName, role):
    skills = SKILLS_BY_ROLES.get(role, set())
    return skillName in skills


def splitSkills(selectedSkills):
    skillsByIdx = {}
    bonusSkillsByIdx = {}
    bonusSkillNamesMaxLvl = []
    for idx, (mainRole, skills) in selectedSkills.items():
        for skillName in skills:
            if isSkillMajor(skillName, mainRole):
                skillsByIdx.setdefault(idx, []).append(skillName)
            role = list(ROLES_BY_SKILLS.get(skillName))[0]
            bonusSkillsByIdx.setdefault(idx, {}).setdefault(role, []).append(skillName)
            bonusSkillNamesMaxLvl.append(skillName)

    return (skillsByIdx, bonusSkillsByIdx, bonusSkillNamesMaxLvl)
