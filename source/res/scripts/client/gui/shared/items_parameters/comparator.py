# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/comparator.py
import collections
import sys
import typing
from constants import BonusTypes
from gui.shared.gui_items import KPI
from gui.shared.items_parameters import params_cache
from shared_utils import first
from gui.shared.utils import WHEELED_SWITCH_ON_TIME, WHEELED_SWITCH_OFF_TIME, DUAL_GUN_CHARGE_TIME, SHOT_DISPERSION_ANGLE, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, DISPERSION_RADIUS, CHASSIS_REPAIR_TIME, TURBOSHAFT_SWITCH_TIME, DUAL_GUN_RATE_TIME, DUAL_ACCURACY_COOLING_DELAY, BURST_FIRE_RATE, BURST_TIME_INTERVAL
if typing.TYPE_CHECKING:
    from gui.shared.items_parameters.params import _PenaltyInfo
BACKWARD_QUALITY_PARAMS = frozenset(['aimingTime',
 'autoReloadTime',
 DISPERSION_RADIUS,
 'fireStartingChance',
 'reloadMagazineTime',
 'reloadTimeSecs',
 'shellReloadingTime',
 SHOT_DISPERSION_ANGLE,
 'weight',
 'turboshaftBurstFireRate',
 BURST_FIRE_RATE,
 BURST_TIME_INTERVAL,
 'switchOnTime',
 'switchOffTime',
 CHASSIS_REPAIR_TIME,
 DUAL_GUN_CHARGE_TIME,
 KPI.Name.CREW_STUN_DURATION,
 KPI.Name.CREW_STUN_RESISTANCE,
 KPI.Name.DAMAGE_AND_PIERCING_DISTRIBUTION_UPPER_BOUND,
 KPI.Name.DEMASK_FOLIAGE_FACTOR,
 KPI.Name.DEMASK_MOVING_FACTOR,
 KPI.Name.EQUIPMENT_PREPARATION_TIME,
 KPI.Name.STUN_RESISTANCE_EFFECT_FACTOR,
 KPI.Name.VEHICLE_CHASSIS_FALL_DAMAGE,
 KPI.Name.VEHICLE_FIRE_CHANCE,
 KPI.Name.VEHICLE_GUN_RELOAD_TIME,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_AFTER_SHOT,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_MOVEMENT,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_CHASSIS_ROTATION,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_TURRET_ROTATION,
 KPI.Name.VEHICLE_GUN_SHOT_DISPERSION_WHILE_GUN_DAMAGED,
 KPI.Name.VEHICLE_GUN_SHOT_FULL_DISPERSION,
 KPI.Name.VEHICLE_OWN_SPOTTING_TIME,
 KPI.Name.VEHICLE_PENALTY_FOR_DAMAGED_ENGINE_AND_COMBAT,
 KPI.Name.VEHICLE_RAM_DAMAGE_RESISTANCE,
 KPI.Name.VEHICLE_RAM_OR_EXPLOSION_DAMAGE_RESISTANCE,
 KPI.Name.VEHICLE_FUEL_TANK_LESION_CHANCE,
 WHEELED_SWITCH_OFF_TIME,
 WHEELED_SWITCH_ON_TIME,
 TURBOSHAFT_SWITCH_TIME,
 KPI.Name.VEHICLE_RAM_CHASSIS_DAMAGE_RESISTANCE,
 KPI.Name.WOUNDED_CREW_EFFICIENCY,
 DUAL_GUN_RATE_TIME,
 DUAL_ACCURACY_COOLING_DELAY,
 KPI.Name.ART_NOTIFICATION_DELAY_FACTOR,
 KPI.Name.DAMAGED_MODULES_DETECTION_TIME])
PARAMS_WITH_BATTLE_MODIFIERS = {'maxHealth': {'vehicleHealth'}}
NEGATIVE_PARAMS = ['switchOnTime', 'switchOffTime']
PARAMS_WITH_IGNORED_EMPTY_VALUES = {SHOT_DISPERSION_ANGLE, DISPERSION_RADIUS}

def normalizeShotDispersionValue(value):
    return [None] + value if len(value) == 1 else value


PARAMS_NORMALIZATION_MAP = {SHOT_DISPERSION_ANGLE: normalizeShotDispersionValue}
_CUSTOM_QUALITY_PARAMS = {'vehicleWeight': (True, False),
 'clipFireRate': (True, True, False),
 BURST_FIRE_RATE: (True, False, False),
 'turboshaftBurstFireRate': (True, False, False),
 'pitchLimits': (True, False)}

class PARAM_STATE(object):
    WORSE = 'worse'
    NORMAL = 'normal'
    BETTER = 'better'
    NOT_APPLICABLE = 'N/A'


DEFAULT_AVG_VALUE = (sys.maxint, -1)

def getParamExtendedData(paramName, value, otherValue, penalties=None, customQualityParams=None, isSituational=False, hasNormalization=False):
    possibleBonuses, bonuses, inactive, penalties = penalties if penalties is not None else ([],
     [],
     [],
     [])
    if paramName not in NEGATIVE_PARAMS:
        if otherValue is None or otherValue == DEFAULT_AVG_VALUE:
            otherValue = value
    if hasNormalization and paramName in PARAMS_NORMALIZATION_MAP:
        func = PARAMS_NORMALIZATION_MAP[paramName]
        value = func(value)
        otherValue = func(otherValue)
    return _ParameterInfo(paramName, value, rateParameterState(paramName, value, otherValue, customQualityParams=customQualityParams), possibleBonuses, inactive, bonuses, penalties, isSituational)


class ItemsComparator(object):

    def __init__(self, currentParams, otherParams):
        super(ItemsComparator, self).__init__()
        self._currentParams = currentParams
        self._otherParams = otherParams

    def getAllDifferentParams(self):
        result = []
        for paramName in self._currentParams.keys():
            data = self.getExtendedData(paramName)
            if data.state[0] != PARAM_STATE.NORMAL:
                result.append(data)

        return result

    def getExtendedData(self, paramName, hasNormalization=False):
        return getParamExtendedData(paramName, self._currentParams.get(paramName), self._otherParams.get(paramName), self._getPenaltiesAndBonuses(paramName), hasNormalization=hasNormalization)

    def getPenalties(self, _):
        return []

    def _getPenaltiesAndBonuses(self, _):
        return ([],
         [],
         {},
         [])


class VehiclesComparator(ItemsComparator):

    def __init__(self, currentVehicleParams, otherVehicleParams, suitableArtefacts=None, bonuses=None, penalties=None):
        super(VehiclesComparator, self).__init__(currentVehicleParams, otherVehicleParams)
        self.__suitableArtefacts = set(suitableArtefacts or set())
        self.__bonuses = bonuses or set()
        self.__penalties = penalties or dict()

    def hasBonusOfType(self, bnsType):
        return any((i == bnsType for _, i in self.__bonuses))

    def getPenalties(self, paramName):
        return self.__penalties.get(paramName, [])

    def _getPenaltiesAndBonuses(self, paramName):
        penalties = self.__penalties.get(paramName, [])
        allPossibleParamBonuses = self.__getPossibleParamBonuses(paramName)
        currentParamBonuses, inactive = self.__getCurrentParamBonuses(paramName, allPossibleParamBonuses)
        possibleBonuses = allPossibleParamBonuses - currentParamBonuses
        return (possibleBonuses,
         currentParamBonuses,
         inactive,
         penalties)

    def __getPossibleParamBonuses(self, paramName):
        paramBonuses = params_cache.g_paramsCache.getBonuses().get(paramName, [])
        allPossibleParamBonuses = set()
        for bonusName, bonusGroup in paramBonuses:
            if (bonusName, bonusGroup) in self.__suitableArtefacts or bonusGroup in BonusTypes.POSSIBLE:
                allPossibleParamBonuses.add((bonusName, bonusGroup))

        return allPossibleParamBonuses

    def __getCurrentParamBonuses(self, paramName, possibleBonuses):
        if paramName in CONDITIONAL_BONUSES:
            return self.__getConditionalBonuses(paramName, possibleBonuses)
        result = possibleBonuses.intersection(self.__bonuses)
        suitableBattleModifiers = PARAMS_WITH_BATTLE_MODIFIERS.get(paramName, set())
        for bonusName, bonusGroup in self.__bonuses:
            if bonusGroup == BonusTypes.BATTLE_MODIFIERS and bonusName in suitableBattleModifiers:
                result.add((bonusName, bonusGroup))

        return (result, {})

    def __getConditionalBonuses(self, paramName, possibleBonuses):
        currentBonuses, affectedBonuses = set(), {}
        bonuses = possibleBonuses.intersection(self.__bonuses)
        for bonus in bonuses:
            unmatchedDependency = self.__getUnmatchedDependency(paramName, bonuses, bonus)
            if unmatchedDependency is None:
                currentBonuses.add(bonus)
            affectedBonuses[bonus] = unmatchedDependency

        return (currentBonuses, affectedBonuses)

    def __getUnmatchedDependency(self, paramName, activeBonuses, bonus):
        dependencies = CONDITIONAL_BONUSES[paramName].get(bonus, ())
        unmatchedDependencies = []
        for dependency in dependencies:
            unmatchedDependency = self.__getUnmatchedDependency(paramName, activeBonuses, dependency)
            if unmatchedDependency is not None and unmatchedDependency not in activeBonuses and bonus not in NOT_HARD_DEPENDENCY:
                unmatchedDependencies.append(unmatchedDependency)

        unmatchedDependency = first(unmatchedDependencies) if len(unmatchedDependencies) == len(dependencies) else None
        if bonus not in activeBonuses:
            unmatchedDependency = unmatchedDependency or bonus
        return unmatchedDependency


class _ParameterInfo(collections.namedtuple('_ParameterInfo', ('name', 'value', 'state', 'possibleBonuses', 'inactiveBonuses', 'bonuses', 'penalties', 'isSituational'))):

    def getParamDiff(self):
        if isinstance(self.value, (tuple, list)):
            diff = [ d for _, d in self.state if d is not None ]
            if diff:
                return diff
        else:
            _, diff = self.state
            if diff is not None:
                return diff
        return


CONDITIONAL_BONUSES = {('invisibilityMovingFactor',
 'invisibilityStillFactor',
 TURBOSHAFT_INVISIBILITY_MOVING_FACTOR,
 TURBOSHAFT_INVISIBILITY_STILL_FACTOR): {(('brotherhood', BonusTypes.SKILL),
 ('chocolate', BonusTypes.EQUIPMENT),
 ('cocacola', BonusTypes.EQUIPMENT),
 ('ration', BonusTypes.EQUIPMENT),
 ('hotCoffee', BonusTypes.EQUIPMENT),
 ('ration_china', BonusTypes.EQUIPMENT),
 ('ration_uk', BonusTypes.EQUIPMENT),
 ('ration_japan', BonusTypes.EQUIPMENT),
 ('ration_czech', BonusTypes.EQUIPMENT),
 ('ration_sweden', BonusTypes.EQUIPMENT),
 ('ration_poland', BonusTypes.EQUIPMENT),
 ('ration_italy', BonusTypes.EQUIPMENT),
 ('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
 ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
 ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
 ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
 ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
 ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)): (('camouflage', BonusTypes.SKILL),),
                                                                                                                                           (('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                                                                                                                                           (('additInvisibilityDeviceBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('additionalInvisibilityDevice_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                    ('additionalInvisibilityDevice_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                    ('additionalInvisibilityDevice_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                    ('trophyBasicAdditionalInvisibilityDevice', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                                                                    ('trophyUpgradedAdditionalInvisibilityDevice', BonusTypes.OPTIONAL_DEVICE))},
 (CHASSIS_REPAIR_TIME,): {(('brotherhood', BonusTypes.SKILL),
 ('chocolate', BonusTypes.EQUIPMENT),
 ('cocacola', BonusTypes.EQUIPMENT),
 ('ration', BonusTypes.EQUIPMENT),
 ('hotCoffee', BonusTypes.EQUIPMENT),
 ('ration_china', BonusTypes.EQUIPMENT),
 ('ration_uk', BonusTypes.EQUIPMENT),
 ('ration_japan', BonusTypes.EQUIPMENT),
 ('ration_czech', BonusTypes.EQUIPMENT),
 ('ration_sweden', BonusTypes.EQUIPMENT),
 ('ration_poland', BonusTypes.EQUIPMENT),
 ('ration_italy', BonusTypes.EQUIPMENT),
 ('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
 ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
 ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
 ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
 ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
 ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)): (('repair', BonusTypes.SKILL),),
                          (('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                               ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                               ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                               ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                               ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                               ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                          (('improvedConfigurationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedConfiguration_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('improvedConfiguration_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('deluxImprovedConfiguration', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('trophyBasicImprovedConfiguration', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('trophyUpgradedImprovedConfiguration', BonusTypes.OPTIONAL_DEVICE))},
 ('reloadTime', 'reloadTimeSecs', 'avgDamagePerMinute'): {(('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                               ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                               ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                               ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                               ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                               ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                                                          (('rammerBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('tankRammer_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                  ('tankRammer_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                  ('tankRammer_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                  ('deluxRammer', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                  ('trophyBasicTankRammer', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                  ('trophyUpgradedTankRammer', BonusTypes.OPTIONAL_DEVICE))},
 ('clipFireRate', 'autoReloadTime', 'dualAccuracyCoolingDelay'): {(('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                       ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                       ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                       ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                       ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                       ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE))},
 ('circularVisionRadius',): {(('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                             (('coatedOpticsBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('coatedOptics_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                           ('coatedOptics_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                           ('coatedOptics_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                           ('deluxCoatedOptics', BonusTypes.OPTIONAL_DEVICE),
                                                                                           ('trophyBasicCoatedOptics', BonusTypes.OPTIONAL_DEVICE),
                                                                                           ('trophyUpgradedCoatedOptics', BonusTypes.OPTIONAL_DEVICE))},
 ('shotDispersionAngle',): {(('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                 ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                            (('improvedSightsBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedSights_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                            ('improvedSights_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                            ('improvedSights_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                            ('deluxeImprovedSights', BonusTypes.OPTIONAL_DEVICE),
                                                                                            ('trophyBasicImprovedSights', BonusTypes.OPTIONAL_DEVICE),
                                                                                            ('trophyUpgradedImprovedSights', BonusTypes.OPTIONAL_DEVICE))},
 ('aimingTime',): {(('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                        ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                        ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                        ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                        ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                        ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                   (('enhancedAimDrivesBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('enhancedAimDrives_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('enhancedAimDrives_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('enhancedAimDrives_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('deluxEnhancedAimDrives', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('trophyBasicAimDrives', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('trophyUpgradedAimDrives', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('modernizedAimDrivesAimingStabilizer1', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('modernizedAimDrivesAimingStabilizer2', BonusTypes.OPTIONAL_DEVICE),
                                                                                      ('modernizedAimDrivesAimingStabilizer3', BonusTypes.OPTIONAL_DEVICE))},
 ('turretRotationSpeed', 'chassisRotationSpeed', 'radioDistance'): {(('improvedVentilationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedVentilation_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                         ('improvedVentilation_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                         ('improvedVentilation_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                         ('deluxImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                         ('trophyBasicImprovedVentilation', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                         ('trophyUpgradedImprovedVentilation', BonusTypes.OPTIONAL_DEVICE)),
                                                                    (('driver_virtuoso', BonusTypes.SKILL),): (('brotherhood', BonusTypes.SKILL),)},
 ('enginePower', 'rocketAccelerationEnginePower', 'enginePowerPerTon', 'turboshaftEnginePower'): {(('turbochargerBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('turbocharger_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('turbocharger_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('turbocharger_tier3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('modernizedTurbochargerRotationMechanism1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('modernizedTurbochargerRotationMechanism2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('modernizedTurbochargerRotationMechanism3', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('deluxeTurbocharger', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('trophyBasicTurbocharger', BonusTypes.OPTIONAL_DEVICE),
                                                                                                                                                                ('trophyUpgradedTurbocharger', BonusTypes.OPTIONAL_DEVICE))},
 ('vehicleRepairSpeed',): {(('improvedConfigurationBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('improvedConfiguration_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('improvedConfiguration_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('deluxImprovedConfiguration', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('trophyBasicImprovedConfiguration', BonusTypes.OPTIONAL_DEVICE),
                                                                                                  ('trophyUpgradedImprovedConfiguration', BonusTypes.OPTIONAL_DEVICE))},
 ('vehicleGunShotDispersion',): {(('aimingStabilizerBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('aimingStabilizer_tier1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('aimingStabilizer_tier2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('deluxAimingStabilizer', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('trophyBasicAimingStabilizer', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('trophyUpgradedAimingStabilizer', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('modernizedAimDrivesAimingStabilizer1', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('modernizedAimDrivesAimingStabilizer2', BonusTypes.OPTIONAL_DEVICE),
                                                                                                   ('modernizedAimDrivesAimingStabilizer3', BonusTypes.OPTIONAL_DEVICE))},
 ('fireExtinguishingRate',): {(('fireFightingBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('fireFighting', BonusTypes.SKILL),)},
 ('wheelsRotationSpeed',): {(('virtuosoBattleBooster', BonusTypes.BATTLE_BOOSTER),): (('driver_virtuoso', BonusTypes.SKILL),)}}
CONDITIONAL_BONUSES = {k:{k1:v1 for keys1, v1 in values.iteritems() for k1 in keys1} for keys, values in CONDITIONAL_BONUSES.items() for k in keys}
NOT_HARD_DEPENDENCY = {('driver_virtuoso', BonusTypes.SKILL), ('fireFightingBattleBooster', BonusTypes.BATTLE_BOOSTER), ('virtuosoBattleBooster', BonusTypes.BATTLE_BOOSTER)}

def _getComparableValue(currentValue, comparableList, idx):
    return comparableList[idx] if len(comparableList) > idx else currentValue


def _getParamStateInfo(paramName, val1, val2, customReverted=False):
    if val1 is None or val2 is None:
        hasNoParam = True
        diff = 0
    else:
        hasNoParam = False
        if isinstance(val1, float) and isinstance(val2, float):
            diff = val1 - val2
            diff = round(diff, 4)
        else:
            if isinstance(val1, float):
                val1 = round(val1, 4)
            if isinstance(val2, float):
                val2 = round(val2, 4)
            diff = val1 - val2
    if paramName in NEGATIVE_PARAMS and hasNoParam:
        if val1 is None and val2 is None:
            return (PARAM_STATE.NORMAL, diff)
        if val1 is None:
            return (PARAM_STATE.BETTER, diff)
        return (PARAM_STATE.WORSE, diff)
    elif diff == 0:
        if hasNoParam and paramName in PARAMS_WITH_IGNORED_EMPTY_VALUES:
            return (PARAM_STATE.NOT_APPLICABLE, diff)
        return (PARAM_STATE.NORMAL, diff)
    else:
        isInverted = paramName in BACKWARD_QUALITY_PARAMS or customReverted
        return (PARAM_STATE.WORSE, diff) if isInverted and diff > 0 or not isInverted and diff < 0 else (PARAM_STATE.BETTER, diff)


def rateParameterState(paramName, val1, val2, customQualityParams=None):
    if isinstance(val1, (tuple, list)):
        if customQualityParams is None:
            customQualityParams = _CUSTOM_QUALITY_PARAMS.get(paramName)
        customQualityLen = len(customQualityParams) if customQualityParams else 0
        result = []
        val2Len = len(val2) if isinstance(val2, (tuple, list)) else 0
        for i, val in enumerate(val1):
            if val2Len == 0:
                result.append((PARAM_STATE.NORMAL, None))
                continue
            if val2Len > i:
                val2ToCompare = val2[i]
            else:
                result.append((PARAM_STATE.NOT_APPLICABLE, None))
                continue
            if customQualityParams is not None:
                customQuality = customQualityParams[min(i, customQualityLen - 1)]
            else:
                customQuality = None
            result.append(rateParameterState(paramName, val, val2ToCompare, customQuality))

        return tuple(result)
    else:
        return _getParamStateInfo(paramName, val1, val2, customQualityParams)
