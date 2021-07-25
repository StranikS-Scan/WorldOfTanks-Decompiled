# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/bonus_helper.py
import typing
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.perk import PerkGUI
from gui.shared.items_parameters.comparator import CONDITIONAL_BONUSES, getParamExtendedData
from gui.shared.items_parameters.params import VehicleParams, EXTRAS_CAMOUFLAGE
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from helpers import dependency
from constants import BonusTypes, TANK_CONTROL_LEVEL, AbilitySystemScopeNames
from items.components.c11n_components import SeasonType
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.items_parameters.comparator import _ParameterInfo

def isBonusAutoPerk(bnsID, bnsType):
    if bnsType != BonusTypes.DETACHMENT:
        return False
    perk = PerkGUI(int(bnsID))
    return perk.isAutoperk


def _removeCamouflageModifier(vehicle, bonusID):
    if bonusID == EXTRAS_CAMOUFLAGE:
        for season in SeasonType.SEASONS:
            outfit = vehicle.getOutfit(season)
            if outfit:
                outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()

    return vehicle


def _removeDetachmentPerkModifier(vehicle, perkName):
    perksController = vehicle.getPerksController()
    detachmentCache = dependency.instance(IDetachmentCache)
    detachment = detachmentCache.getDetachment(vehicle.getLinkedDetachmentID())
    if not perksController:
        return vehicle
    bonusPerks = g_detachmentTankSetupVehicle.getBackupedBonusPerks()
    perkID = int(perkName)
    perksDict = perksController.mergedPerks
    perkLevel = perksDict.get(perkID, 0)
    comparableInstructors = g_detachmentTankSetupVehicle.comparableInstructors
    boosterPerkBonus = detachment.getPerkBoosterInfluence(perkID=perkID, vehicle=vehicle, bonusPerks=bonusPerks, comparableInstructors=comparableInstructors) if detachment else []
    boosterPerkLevel = sum((points for _, points, _ in boosterPerkBonus))
    perksController.customizedRecalc(AbilitySystemScopeNames.DETACHMENT, {perkID: perkLevel - boosterPerkLevel})
    return vehicle


def _removeSkillModifier(vehicle, skillName):
    if skillName == TANK_CONTROL_LEVEL:
        perksController = vehicle.getPerksController()
        if not perksController:
            return vehicle
        perksController.ignoreCrewMastery()
    else:
        vehicle.crew = vehicle.getCrewWithoutSkill(skillName)
    return vehicle


def _removeBattleBoosterModifier(vehicle, boosterName):
    battleBooster = vehicle.battleBoosters.installed[0]
    if battleBooster is not None:
        if not battleBooster.isCrewBooster():
            vehicle.battleBoosters.installed[0] = None
        else:
            perksController = vehicle.getPerksController()
            detachmentCache = dependency.instance(IDetachmentCache)
            detachment = detachmentCache.getDetachment(vehicle.getLinkedDetachmentID())
            if not perksController:
                return vehicle
            bonusPerks = g_detachmentTankSetupVehicle.getBackupedBonusPerks()
            comparableInstructors = g_detachmentTankSetupVehicle.comparableInstructors
            boosterPerksBonus = detachment.getPerksBoosterInfluence(vehicle=vehicle, bonusPerks=bonusPerks, comparableInstructors=comparableInstructors) if detachment else []
            perksController.customizedRecalc(AbilitySystemScopeNames.DETACHMENT, {perkID:level for _, perkID, level, _ in boosterPerksBonus})
    return vehicle


def _removeOptionalDeviceModifier(vehicle, optDevName):
    for slotIdx, optDev in enumerate(vehicle.optDevices.installed):
        if optDev and optDev.name == optDevName:
            vehicle.descriptor.removeOptionalDevice(slotIdx)
            vehicle.optDevices.installed[slotIdx] = None

    return vehicle


def _removeEquipmentModifier(vehicle, eqName):
    for slotIdx, equipment in enumerate(vehicle.consumables.installed):
        if equipment and equipment.name == eqName:
            vehicle.consumables.installed[slotIdx] = None

    return vehicle


_VEHICLE_MODIFIERS = {BonusTypes.SKILL: _removeSkillModifier,
 BonusTypes.EXTRA: _removeCamouflageModifier,
 BonusTypes.EQUIPMENT: _removeEquipmentModifier,
 BonusTypes.OPTIONAL_DEVICE: _removeOptionalDeviceModifier,
 BonusTypes.BATTLE_BOOSTER: _removeBattleBoosterModifier,
 BonusTypes.DETACHMENT: _removeDetachmentPerkModifier}
_NOT_STACK_BONUSES = {'circularVisionRadius': (('stereoscope_tier1', BonusTypes.OPTIONAL_DEVICE), ('stereoscope_tier2', BonusTypes.OPTIONAL_DEVICE), ('stereoscope_tier3', BonusTypes.OPTIONAL_DEVICE)),
 'invisibilityStillFactor': (('camouflageNet_tier2', BonusTypes.OPTIONAL_DEVICE), ('camouflageNet_tier3', BonusTypes.OPTIONAL_DEVICE))}

class _BonusSorter(object):

    def __init__(self, paramName):
        self.__paramName = paramName

    def sort(self, bonuses):
        sortedBonuses = self.__conditionsSorter(list(bonuses))
        sortedBonuses = self.__notStackSorter(sortedBonuses)
        return sortedBonuses

    def __conditionsSorter(self, bonuses):
        if self.__paramName in CONDITIONAL_BONUSES:
            condition, _ = CONDITIONAL_BONUSES[self.__paramName]
            if condition in bonuses:
                bonuses.remove(condition)
                bonuses.append(condition)
        return bonuses

    def __notStackSorter(self, bonuses):
        if self.__paramName in _NOT_STACK_BONUSES:
            for notStackBonus in _NOT_STACK_BONUSES[self.__paramName]:
                if notStackBonus in bonuses:
                    bonuses.remove(notStackBonus)
                    bonuses.insert(0, notStackBonus)

        return bonuses


class BonusExtractor(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, bonuses, paramName):
        self.__vehicle = self._getCopyVehicle(vehicle)
        self.__paramName = paramName
        self.__bonuses = _BonusSorter(self.__paramName).sort(bonuses)
        self.__removeCamouflage = False
        perksController = vehicle.getPerksController()
        if perksController:
            self.__vehicle.setPerksController(perksController)
        self.__updateCurrValue()

    def getBonusInfo(self):
        for bnsId, bnsGroup in self.__bonuses:
            yield (bnsId, bnsGroup, self.extractBonus(bnsGroup, bnsId))

    def extractBonus(self, bonusGroup, bonusID):
        oldValue = self.__currValue
        self.__vehicle = _VEHICLE_MODIFIERS[bonusGroup](self.__vehicle, bonusID)
        if bonusGroup == BonusTypes.EXTRA and bonusID == EXTRAS_CAMOUFLAGE:
            self.__removeCamouflage = True
        self.__updateCurrValue()
        return getParamExtendedData(self.__paramName, oldValue, self.__currValue)

    def _getCopyVehicle(self, vehicle):
        return self.itemsCache.items.getVehicleCopy(vehicle)

    def __updateCurrValue(self):
        self.__currValue = getattr(_CustomizedVehicleParams(self.__vehicle, self.__removeCamouflage), self.__paramName)


class TankSetupBonusExtractor(BonusExtractor):

    def _getCopyVehicle(self, vehicle):
        return self.itemsCache.items.getLayoutsVehicleCopy(vehicle)


class _CustomizedVehicleParams(VehicleParams):

    def __init__(self, vehicle, removeCamouflage):
        self.__removeCamouflage = removeCamouflage
        super(_CustomizedVehicleParams, self).__init__(vehicle)

    def _getVehicleDescriptor(self, vehicle):
        return vehicle.descriptor if self.__removeCamouflage else super(_CustomizedVehicleParams, self)._getVehicleDescriptor(vehicle)

    @staticmethod
    def getIgnoreSituational():
        return False

    def __getattr__(self, item):
        return self.getKpiFactor(item, toCompare=True)
