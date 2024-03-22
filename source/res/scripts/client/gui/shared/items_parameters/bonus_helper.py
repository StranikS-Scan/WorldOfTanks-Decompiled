# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/bonus_helper.py
from constants import BonusTypes
from gui.shared.gui_items import GUI_ITEM_TYPE, KPI, VEHICLE_ATTR_TO_KPI_NAME_MAP
from gui.shared.items_parameters.comparator import CONDITIONAL_BONUSES, getParamExtendedData
from gui.shared.items_parameters.params import VehicleParams
from gui.shared.items_parameters.params import EXTRAS_CAMOUFLAGE
from helpers import dependency
from items import vehicles
from items.components.c11n_components import SeasonType
from post_progression_common import ACTION_TYPES
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache

def isSituationalBonus(bonusName, bonusType='', paramName=''):
    from items import tankmen
    skill = tankmen.getSkillsConfig().getSkill(bonusName)
    if not paramName:
        return skill.situational
    if paramName and KPI.Name.getKeyByValue(paramName):
        for kpi in skill.kpi:
            if kpi.name in (paramName, VEHICLE_ATTR_TO_KPI_NAME_MAP.get(paramName)):
                return kpi.situational

    param = skill.params.get(paramName)
    if param:
        return param.situational
    return paramName in _PARTIALLY_SITUATIONAL_BONUSES[bonusName] if bonusName in _PARTIALLY_SITUATIONAL_BONUSES else bonusName in _SITUATIONAL_BONUSES


_SITUATIONAL_BONUSES = ('camouflageNet', 'stereoscope', 'removedRpmLimiter', 'radioman_inventor', 'radioman_retransmitter')
CREW_MASTERY_BONUSES = ('radioman_inventor', 'radioman_retransmitter')
_PARTIALLY_SITUATIONAL_BONUSES = {'lastEffortBattleBooster': KPI.Name.RADIOMAN_ACTIVITY_TIME_AFTER_VEHICLE_DESTROY}

def _removeCamouflageModifier(vehicle, bonusID):
    if bonusID == EXTRAS_CAMOUFLAGE:
        for season in SeasonType.SEASONS:
            outfit = vehicle.getOutfit(season)
            if outfit:
                outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()
                vehicle.removeOutfitForSeason(season)

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
 BonusTypes.PAIR_MODIFICATION: _removePostProgressionModification,
 BonusTypes.BASE_MODIFICATION: _removePostProgressionBaseModifications}
_NOT_STACK_BONUSES = {'circularVisionRadius': (('stereoscope_tier1', BonusTypes.OPTIONAL_DEVICE), ('stereoscope_tier2', BonusTypes.OPTIONAL_DEVICE), ('stereoscope_tier3', BonusTypes.OPTIONAL_DEVICE)),
 'invisibilityStillFactor': (('camouflageNet_tier2', BonusTypes.OPTIONAL_DEVICE), ('camouflageNet_tier3', BonusTypes.OPTIONAL_DEVICE), ('camouflageBattleBooster', BonusTypes.BATTLE_BOOSTER)),
 'chassisRotationSpeed': (('virtuosoBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'invisibilityMovingFactor': (('camouflageBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'turboshaftInvisibilityMovingFactor': (('camouflageBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'turboshaftInvisibilityStillFactor': (('camouflageBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'vehicleGunShotDispersionTurretRotation': (('smoothTurretBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'vehicleGunShotDispersionChassisMovement': (('smoothDrivingBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'vehicleEnemySpottingTime': (('rancorousBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'vehicleAmmoBayStrength': (('pedantBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'radiomanHitChance': (('lastEffortBattleBooster', BonusTypes.BATTLE_BOOSTER),),
 'radiomanActivityTimeAfterVehicleDestroy': (('lastEffortBattleBooster', BonusTypes.BATTLE_BOOSTER),)}

class _BonusSorter(object):

    def __init__(self, paramName):
        self.__paramName = paramName

    def sort(self, bonuses):
        sortedBonuses = self.__conditionsSorter(list(bonuses))
        sortedBonuses = self.__notStackSorter(sortedBonuses)
        return sortedBonuses

    def __conditionsSorter(self, bonuses):
        if self.__paramName in CONDITIONAL_BONUSES:
            prioritizedBonuses = {}
            for bonus in bonuses:
                numDependencies = self.__getNumDependencies(bonus)
                if numDependencies not in prioritizedBonuses:
                    prioritizedBonuses[numDependencies] = []
                prioritizedBonuses[numDependencies].append(bonus)

            bonuses = [ bonus for key in sorted(prioritizedBonuses.keys())[::-1] for bonus in prioritizedBonuses[key] ]
        return bonuses

    def __getNumDependencies(self, bonus, dependenciesNum=0):
        return self.__getNumDependencies(CONDITIONAL_BONUSES[self.__paramName][bonus], dependenciesNum + 1) if bonus in CONDITIONAL_BONUSES[self.__paramName] else dependenciesNum

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
        self.__vehicle.setOutfits(vehicle)
        self.__paramName = paramName
        self.__bonuses = _BonusSorter(self.__paramName).sort(bonuses)
        self.__removeCamouflage = False

    def getBonusInfo(self):
        self.__reorderDevices(self.__bonuses)
        for bnsId, bnsGroup in self.__bonuses:
            yield (bnsGroup, bnsId, self.extractBonus(bnsGroup, bnsId))

    def extractBonus(self, bonusGroup, bonusID):
        paramName = self.__paramName
        if isSituationalBonus(bonusID, bonusGroup, paramName):
            paramName += 'Situational'
        valueWithBonus = self.__extractParamValue(paramName)
        self.__vehicle = _VEHICLE_MODIFIERS[bonusGroup](self.__vehicle, bonusID)
        if bonusGroup == BonusTypes.EXTRA and bonusID == EXTRAS_CAMOUFLAGE:
            self.__removeCamouflage = True
        valueWithoutBonus = self.__extractParamValue(paramName)
        return getParamExtendedData(self.__paramName, valueWithBonus, valueWithoutBonus)

    def _getCopyVehicle(self, vehicle):
        return self.itemsCache.items.getVehicleCopy(vehicle)

    def __extractParamValue(self, paramName):
        return getattr(_CustomizedVehicleParams(self.__vehicle, self.__removeCamouflage), paramName)

    @staticmethod
    def __reorderDevices(devices):
        invisDevice = [ item[0].find('additionalInvisibilityDevice') != -1 for item in devices ]
        camoNet = [ item[0].find('camouflageNet') != -1 for item in devices ]
        if any(invisDevice) and any(camoNet):
            invisDeviceIndex = invisDevice.index(True)
            camoNetIndex = camoNet.index(True)
            if invisDeviceIndex < camoNetIndex:
                devices[invisDeviceIndex], devices[camoNetIndex] = devices[camoNetIndex], devices[invisDeviceIndex]


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
