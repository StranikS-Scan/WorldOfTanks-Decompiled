# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/comparator.py
import collections
import sys
import typing
from constants import BonusTypes
from items.vehicles import getBonusID
from gui.shared.items_parameters import params_cache
from gui.shared.gui_items import KPI
from gui.shared.utils import WHEELED_SWITCH_ON_TIME, WHEELED_SWITCH_OFF_TIME, DUAL_GUN_CHARGE_TIME, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR
BACKWARD_QUALITY_PARAMS = frozenset(['aimingTime',
 'shotDispersionAngle',
 'weight',
 'dispertionRadius',
 'fireStartingChance',
 'reloadTimeSecs',
 'autoReloadTime',
 'shellReloadingTime',
 'clipFireRate',
 'reloadMagazineTime',
 'weight',
 'switchOnTime',
 'switchOffTime',
 WHEELED_SWITCH_ON_TIME,
 WHEELED_SWITCH_OFF_TIME,
 DUAL_GUN_CHARGE_TIME,
 'vehicleOwnSpottingTime',
 'crewStunDuration',
 'crewRepeatedStunDuration',
 'vehicleChassisFallDamage',
 'vehPenaltyForDamageEngineAndCombat',
 'demaskFoliageFactor',
 'demaskMovingFactor',
 'vehicleRamDamageResistance',
 'vehicleExplosionDamageResistance',
 'vehicleFireChance',
 'equipmentPreparationTime',
 'upDamageDispersion',
 'upPenetrationDispersion',
 'turretAimingDispersion',
 'movingAimingDispersion',
 'deathPenaltyFactor',
 'moduleCritMod',
 'firstAidKitPreparationTime',
 'repairKitPreparationTime',
 'trackRamDamageResist',
 'aimingDispersionWhileGunDamaged',
 'stunResistanceEffect',
 'firstAidKitPreparationTime',
 'repairKitPreparationTime',
 'damageMonitoringDelay'])
NEGATIVE_PARAMS = ['switchOnTime', 'switchOffTime']
_CUSTOM_QUALITY_PARAMS = {'vehicleWeight': (True, False),
 'clipFireRate': (True, True, False),
 'pitchLimits': (True, False)}

class PARAM_STATE(object):
    WORSE = 'worse'
    NORMAL = 'normal'
    BETTER = 'better'
    NOT_APPLICABLE = 'N/A'


DEFAULT_AVG_VALUE = (sys.maxint, -1)

def getParamExtendedData(paramName, value, otherValue, penalties=None, customQualityParams=None):
    possibleBonuses, bonuses, inactive, penalties = penalties if penalties is not None else ([],
     [],
     [],
     [])
    if paramName not in NEGATIVE_PARAMS:
        if otherValue is None or otherValue == DEFAULT_AVG_VALUE:
            otherValue = value
    return _ParameterInfo(paramName, value, rateParameterState(paramName, value, otherValue, customQualityParams=customQualityParams), possibleBonuses, inactive, bonuses, penalties)


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

    def getExtendedData(self, paramName, compareWithEmpty=False):
        return getParamExtendedData(paramName, self._currentParams.get(paramName), self._otherParams.get(paramName) if not compareWithEmpty else 0, self._getPenaltiesAndBonuses(paramName))

    def _getPenaltiesAndBonuses(self, _):
        return ([],
         [],
         {},
         [])


class VehiclesComparator(ItemsComparator):

    def __init__(self, currentVehicleParams, otherVehicleParams, suitableArtefacts=None, bonuses=None, penalties=None, extraBonuses=None, otherBonuses=None, otherExtraBonuses=None):
        super(VehiclesComparator, self).__init__(currentVehicleParams, otherVehicleParams)
        self.__suitableArtefacts = suitableArtefacts or set()
        self.__bonuses = bonuses or set()
        self.__extraBonuses = extraBonuses or ({}, {}, {})
        self.__otherBonuses = otherBonuses or set()
        self.__otherExtraBonuses = otherExtraBonuses or ({}, {}, {})
        self.__penalties = penalties or dict()
        self.__normalizedBonuses = {(bonusID if bonusType != BonusTypes.DETACHMENT else getBonusID(bonusType, bonusID), bonusType) for bonusID, bonusType in self.__bonuses}

    def getExtendedData(self, paramName, compareWithEmpty=False):
        return getParamExtendedData(paramName, self._currentParams.get(paramName), self._otherParams.get(paramName) if not compareWithEmpty else 0, self._getPenaltiesAndBonuses(paramName))

    def getBonuses(self):
        return self.__bonuses

    def getExtraBonuses(self):
        return self.__extraBonuses

    def getOtherBonuses(self):
        return self.__otherBonuses

    def getOtherExtraBonuses(self):
        return self.__otherExtraBonuses

    def getBonusesWithBoosters(self):
        return self.__mergeBonuses(self.__bonuses, self.__extraBonuses)

    def getOtherBonusesWithBoosters(self):
        return self.__mergeBonuses(self.__otherBonuses, self.__otherExtraBonuses)

    def hasBonusOfType(self, bnsType):
        return any((i == bnsType for _, i in self.__bonuses))

    def getKpiPassiveParam(self, paramName):
        return self._currentParams.getKpiPassiveParam(paramName)

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
        paramBonuses = set(params_cache.g_paramsCache.getBonuses().get(paramName, []))
        allPossibleParamBonuses = set()
        for bonusName, bonusGroup in paramBonuses:
            if (bonusName, bonusGroup) in self.__suitableArtefacts or bonusGroup in BonusTypes.POSSIBLE:
                allPossibleParamBonuses.add((bonusName, bonusGroup))

        return allPossibleParamBonuses

    def __getCurrentParamBonuses(self, paramName, possibleBonuses):
        bonuses = possibleBonuses.intersection(self.__normalizedBonuses)
        inactive = {}
        if paramName in CONDITIONAL_BONUSES:
            bonuses, inactive = self.__getConditionalBonuses(paramName, bonuses)
        for possibleBonus in possibleBonuses:
            if possibleBonus in PROGRESSION_CONDITIONAL_BONUSES and possibleBonus not in bonuses:
                inactive[possibleBonus] = [possibleBonus]

        return (bonuses, inactive)

    @staticmethod
    def __getConditionalBonuses(paramName, bonuses):
        currentBonuses, affectedBonuses = set(), {}
        conditions, affected = CONDITIONAL_BONUSES[paramName]
        for bonus in bonuses:
            isAffected = bonus in affected
            if not isAffected or isAffected and any((condition in bonuses for condition in conditions)):
                currentBonuses.add(bonus)
            if isAffected:
                affectedBonuses[bonus] = conditions

        return (currentBonuses, affectedBonuses)

    def __mergeBonuses(self, bonuses, extraBonuses):
        result = set()
        mergedBonuses = {}
        for bonus, bonusType in bonuses:
            if bonusType == BonusTypes.DETACHMENT:
                perkID, perkLevel = bonus.split('_')
                mergedBonuses[int(perkID)] = int(perkLevel)
            result.add((bonus, bonusType))

        crewBoosterBonuses = extraBonuses[1]
        for perkID, perkLevel in crewBoosterBonuses.iteritems():
            mergedBonuses[perkID] = mergedBonuses.get(perkID, 0) + perkLevel

        result.update(set((('{}_{}'.format(perkID, perkLevel), BonusTypes.DETACHMENT) for perkID, perkLevel in mergedBonuses.iteritems())))
        return result


class _ParameterInfo(collections.namedtuple('_ParameterInfo', ('name', 'value', 'state', 'possibleBonuses', 'inactiveBonuses', 'bonuses', 'penalties'))):

    def getParamDiff(self):
        if isinstance(self.value, (tuple, list)):
            diff = [ d for _, d in self.state ]
            if any(diff):
                return diff
        else:
            _, diff = self.state
            if diff is not None:
                return diff
        return


_CONDITIONAL_BONUSES = {('invisibilityMovingFactor',
 'invisibilityStillFactor',
 TURBOSHAFT_INVISIBILITY_MOVING_FACTOR,
 TURBOSHAFT_INVISIBILITY_STILL_FACTOR): ([('302', BonusTypes.DETACHMENT), ('camouflagePerkBattleBooster', BonusTypes.BATTLE_BOOSTER)], [('tankControlLevel', BonusTypes.SKILL)]),
 (KPI.Name.VEHICLE_REPAIR_SPEED,): ([('301', BonusTypes.DETACHMENT)], [('tankControlLevel', BonusTypes.SKILL)]),
 (KPI.Name.DETACHMENT_PERK_FIRE_EXTINGUISHING_RATE,): ([('305', BonusTypes.DETACHMENT)], [('tankControlLevel', BonusTypes.SKILL)])}
CONDITIONAL_BONUSES = {k:v for keys, v in _CONDITIONAL_BONUSES.items() for k in keys}
PROGRESSION_CONDITIONAL_BONUSES = [('1', BonusTypes.DETACHMENT)]

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
            diff = round(diff, 2)
        else:
            if isinstance(val1, float):
                val1 = round(val1, 2)
            if isinstance(val2, float):
                val2 = round(val2, 2)
            diff = val1 - val2
    if paramName in NEGATIVE_PARAMS and hasNoParam:
        if val1 is None:
            return (PARAM_STATE.BETTER, diff)
        return (PARAM_STATE.WORSE, diff)
    elif diff == 0:
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
        val2Len = len(val2)
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
