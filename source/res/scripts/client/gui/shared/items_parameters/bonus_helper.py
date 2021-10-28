# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/bonus_helper.py
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters.comparator import CONDITIONAL_BONUSES, getParamExtendedData
from gui.shared.items_parameters.params import VehicleParams
from gui.shared.items_parameters.params import EXTRAS_CAMOUFLAGE
from helpers import dependency
from items import perks, vehicles
from constants import BonusTypes
from items.components.c11n_components import SeasonType
from post_progression_common import ACTION_TYPES
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache

def isSituationalBonus(bonusName, bonusType=''):
    if bonusType == BonusTypes.PERK:
        cache = perks.g_cache.perks()
        perkItem = cache.perks[int(bonusName)]
        return perkItem.situational
    return bonusName in _SITUATIONAL_BONUSES


_SITUATIONAL_BONUSES = ('camouflageNet', 'stereoscope', 'removedRpmLimiter', 'gunner_rancorous')

def _removeCamouflageModifier(vehicle, bonusID):
    if bonusID == EXTRAS_CAMOUFLAGE:
        for season in SeasonType.SEASONS:
            outfit = vehicle.getOutfit(season)
            if outfit:
                outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()
                vehicle.removeOutfitForSeason(season)

    return vehicle


def _removePlatoonPerkModifier(vehicle, perkName):
    perksController = vehicle.getPerksController()
    if not perksController:
        return vehicle
    perksController.customizedRecalc(int(perkName))
    return vehicle


def _removeSkillModifier(vehicle, skillName):
    vehicle.crew = vehicle.getCrewWithoutSkill(skillName)
    return vehicle


def _removeBattleBoosterModifier(vehicle, boosterName):
    if vehicle.battleBoosters.installed[0] is not None:
        vehicle.battleBoosters.installed[0] = None
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


def _removePostProgressionModification(vehicle, modificationName):
    modID = vehicles.g_cache.postProgression().modificationIDs.get(modificationName, None)
    state = vehicle.postProgression.getState()
    if modID is not None:
        for step in vehicle.postProgression.iterUnorderedSteps():
            if step.isReceived() and step.action.getActiveID() == modID:
                if step.action.actionType == ACTION_TYPES.PAIR_MODIFICATION:
                    state.removePair(step.stepID)
                state.removeUnlock(step.stepID)

    vehicle.installPostProgression(state, True)
    return vehicle


def _removePostProgressionBaseModifications(vehicle, modificationsName):
    state = vehicle.postProgression.getState()
    removedStep = findFirst(lambda s: s.action.getTechName() == modificationsName, vehicle.postProgression.iterUnorderedSteps())
    if removedStep is not None:
        for step in vehicle.postProgression.iterUnorderedSteps():
            if step.isReceived() and step.action.getLocName() == removedStep.action.getLocName():
                state.removeUnlock(step.stepID)

    vehicle.installPostProgression(state, True)
    return vehicle


_VEHICLE_MODIFIERS = {BonusTypes.SKILL: _removeSkillModifier,
 BonusTypes.EXTRA: _removeCamouflageModifier,
 BonusTypes.EQUIPMENT: _removeEquipmentModifier,
 BonusTypes.OPTIONAL_DEVICE: _removeOptionalDeviceModifier,
 BonusTypes.BATTLE_BOOSTER: _removeBattleBoosterModifier,
 BonusTypes.PERK: _removePlatoonPerkModifier,
 BonusTypes.PAIR_MODIFICATION: _removePostProgressionModification,
 BonusTypes.BASE_MODIFICATION: _removePostProgressionBaseModifications}
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
            yield (bnsGroup, bnsId, self.extractBonus(bnsGroup, bnsId))

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

    def getVehicle(self):
        return self.__vehicle

    def reUpdateCurrValue(self):
        self.__updateCurrValue()


class TankSetupBonusExtractor(BonusExtractor):

    def _getCopyVehicle(self, vehicle):
        return self.itemsCache.items.getLayoutsVehicleCopy(vehicle)


class PostProgressionBonusExtractor(BonusExtractor):

    def _getCopyVehicle(self, vehicle):
        return self.itemsCache.items.getLayoutsVehicleCopy(vehicle, ignoreDisabledProgression=True)


class _CustomizedVehicleParams(VehicleParams):

    def __init__(self, vehicle, removeCamouflage):
        self.__removeCamouflage = removeCamouflage
        super(_CustomizedVehicleParams, self).__init__(vehicle)

    def _getVehicleDescriptor(self, vehicle):
        return vehicle.descriptor if self.__removeCamouflage else super(_CustomizedVehicleParams, self)._getVehicleDescriptor(vehicle)
