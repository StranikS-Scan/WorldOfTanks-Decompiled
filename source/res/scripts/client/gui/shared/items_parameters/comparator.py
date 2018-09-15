# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/comparator.py
import collections
import sys
from gui.shared.items_parameters import params_cache
BACKWARD_QUALITY_PARAMS = ['aimingTime',
 'shotDispersionAngle',
 'weight',
 'dispertionRadius',
 'fireStartingChance',
 'reloadTimeSecs',
 'shellReloadingTime',
 'clipFireRate',
 'reloadMagazineTime',
 'weight',
 'switchOnTime',
 'switchOffTime']
NEGATIVE_PARAMS = ['switchOnTime', 'switchOffTime']
CUSTOM_QUALITY_PARAMS = {'vehicleWeight': (True, False),
 'clipFireRate': (True, True, False),
 'pitchLimits': (True, False)}

class PARAM_STATE(object):
    WORSE = 'worse'
    NORMAL = 'normal'
    BETTER = 'better'


PARAMS_STATES = (PARAM_STATE.WORSE, PARAM_STATE.NORMAL, PARAM_STATE.BETTER)
DEFAULT_AVG_VALUE = (sys.maxint, -1)

def getParamExtendedData(paramName, value, otherValue, penalties=None):
    possibleBonuses, bonuses, inactive, penalties = penalties if penalties is not None else ([],
     [],
     [],
     [])
    if paramName not in NEGATIVE_PARAMS:
        if otherValue is None or otherValue == DEFAULT_AVG_VALUE:
            otherValue = value
    return _ParameterInfo(paramName, value, rateParameterState(paramName, value, otherValue), possibleBonuses, inactive, bonuses, penalties)


class ItemsComparator(object):

    def __init__(self, currentParams, otherParams):
        """params
            currentParams -- item which we compare,
                            e.g. if this item has worse parameter then second, it will be highlighted as worse
            otherParams -- item to which we compare
        """
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

    def getExtendedData(self, paramName):
        return getParamExtendedData(paramName, self._currentParams.get(paramName), self._otherParams.get(paramName), self._getPenaltiesAndBonuses(paramName))

    def _getPenaltiesAndBonuses(self, _):
        return ([],
         [],
         {},
         [])


class VehiclesComparator(ItemsComparator):

    def __init__(self, currentVehicleParams, otherVehicleParams, suitableArtefacts=None, bonuses=None, penalties=None):
        super(VehiclesComparator, self).__init__(currentVehicleParams, otherVehicleParams)
        self.__suitableArtefacts = suitableArtefacts or set()
        self.__bonuses = bonuses or set()
        self.__penalties = penalties or dict()

    def _getPenaltiesAndBonuses(self, paramName):
        """
        Gets: set of possible bonuses which may affect on selected param but do not work now,
        set of actual bonuses which affect now on selected param,
        set of actual penalties which affect now on param,
        """
        penalties = self.__penalties.get(paramName, [])
        allPossibleParamBonuses = self.__getPossibleParamBonuses(paramName)
        currentParamBonuses, inactive = self.__getCurrentParamBonuses(paramName, allPossibleParamBonuses)
        possibleBonuses = allPossibleParamBonuses - currentParamBonuses
        return (possibleBonuses,
         currentParamBonuses,
         inactive,
         penalties)

    def __getPossibleParamBonuses(self, paramName):
        """
        Gets set of all possible bonuses (<set((bonusName:str, bonusGroup:str),..)>),
        which suit for selected paramName
        """
        paramBonuses = set(params_cache.g_paramsCache.getBonuses().get(paramName, []))
        allPossibleParamBonuses = set()
        for bonusName, bonusGroup in paramBonuses:
            if (bonusName, bonusGroup) in self.__suitableArtefacts or bonusGroup in ('skill', 'role', 'extra', 'battleBooster'):
                allPossibleParamBonuses.add((bonusName, bonusGroup))

        return allPossibleParamBonuses

    def __getCurrentParamBonuses(self, paramName, possibleBonuses):
        """
        Gets set of actual bonuses which suit for selected paramName
        if paramName is a conditional bonus then return set of bonuses which work only together with that bonus
        """
        if paramName in CONDITIONAL_BONUSES:
            return self.__getConditionalBonuses(paramName, possibleBonuses)
        else:
            return (possibleBonuses.intersection(self.__bonuses), {})

    def __getConditionalBonuses(self, paramName, possibleBonuses):
        """
        Gets set of bonuses which work only together with selected paramName
        example: on invisibilityMovingFactor affect camouflage skill,
        but on camouflage skill may affect brotherhood skill,
        that is why brotherhood skill do not increase invisibilityMovingFactor without camouflage skill
        """
        currentBonuses, affectedBonuses = set(), {}
        condition, affected = CONDITIONAL_BONUSES[paramName]
        bonuses = possibleBonuses.intersection(self.__bonuses)
        for bonus in bonuses:
            isAffected = bonus in affected
            if not isAffected or isAffected and condition in bonuses:
                currentBonuses.add(bonus)
            if isAffected:
                affectedBonuses[bonus] = condition

        return (currentBonuses, affectedBonuses)


class _ParameterInfo(collections.namedtuple('_ParamInfo', ('name', 'value', 'state', 'possibleBonuses', 'inactiveBonuses', 'bonuses', 'penalties'))):

    def getParamDiff(self):
        if isinstance(self.value, (tuple, list)):
            diff = map(lambda (_, d): d, self.state)
            if any(diff):
                return diff
        else:
            _, diff = self.state
            if bool(diff):
                return diff
        return None


CONDITIONAL_BONUSES = {'invisibilityMovingFactor': (('camouflage', 'skill'), [('brotherhood', 'skill'),
                               ('chocolate', 'equipment'),
                               ('cocacola', 'equipment'),
                               ('ration', 'equipment'),
                               ('hotCoffee', 'equipment'),
                               ('ration_china', 'equipment'),
                               ('ration_uk', 'equipment'),
                               ('ration_japan', 'equipment'),
                               ('ration_czech', 'equipment'),
                               ('improvedVentilation_class1', 'optionalDevice'),
                               ('improvedVentilation_class2', 'optionalDevice'),
                               ('improvedVentilation_class3', 'optionalDevice'),
                               ('deluxImprovedVentilation', 'optionalDevice')]),
 'invisibilityStillFactor': (('camouflage', 'skill'), [('brotherhood', 'skill'),
                              ('chocolate', 'equipment'),
                              ('cocacola', 'equipment'),
                              ('ration', 'equipment'),
                              ('hotCoffee', 'equipment'),
                              ('ration_china', 'equipment'),
                              ('ration_uk', 'equipment'),
                              ('ration_japan', 'equipment'),
                              ('ration_czech', 'equipment'),
                              ('improvedVentilation_class1', 'optionalDevice'),
                              ('improvedVentilation_class2', 'optionalDevice'),
                              ('improvedVentilation_class3', 'optionalDevice'),
                              ('deluxImprovedVentilation', 'optionalDevice')])}

def _getComparableValue(currentValue, comparableList, idx):
    return comparableList[idx] if len(comparableList) > idx else currentValue


def _getParamStateInfo(paramName, val1, val2, customReverted=False):
    if val1 is None or val2 is None:
        hasNoParam = True
        diff = 0
    else:
        hasNoParam = False
        if isinstance(val1, float):
            val1 = round(val1, 2)
        if isinstance(val2, float):
            val2 = round(val2, 2)
        diff = val1 - val2
    if paramName in NEGATIVE_PARAMS and hasNoParam:
        if val1 is None:
            return (PARAM_STATE.BETTER, diff)
        else:
            return (PARAM_STATE.WORSE, diff)
    if diff == 0:
        return (PARAM_STATE.NORMAL, diff)
    else:
        isInverted = paramName in BACKWARD_QUALITY_PARAMS or customReverted
        if isInverted and diff > 0 or not isInverted and diff < 0:
            return (PARAM_STATE.WORSE, diff)
        return (PARAM_STATE.BETTER, diff)
        return


def rateParameterState(paramName, val1, val2, customQualityParams=None):
    if customQualityParams is None:
        customQualityParams = CUSTOM_QUALITY_PARAMS.get(paramName)
    if isinstance(val1, collections.Iterable):
        result = []
        for i, val in enumerate(val1):
            val2ToCompare = _getComparableValue(val, val2, i)
            if customQualityParams is not None:
                customQuality = _getComparableValue(customQualityParams[-1], customQualityParams, i)
            else:
                customQuality = None
            result.append(rateParameterState(paramName, val, val2ToCompare, customQuality))

        return tuple(result)
    else:
        return _getParamStateInfo(paramName, val1, val2, customQualityParams)
