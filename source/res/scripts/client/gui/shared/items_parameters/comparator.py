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
 'weight']
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
    possibleBonuses, bonuses, penalties = penalties if penalties is not None else ([], [], [])
    if otherValue is None or otherValue == DEFAULT_AVG_VALUE:
        otherValue = value
    return _ParameterInfo(paramName, value, rateParameterState(paramName, value, otherValue), possibleBonuses, bonuses, penalties)


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
        return ([], [], [])


class VehiclesComparator(ItemsComparator):

    def __init__(self, currentVehicleParams, otherVehicleParams, possibleBonuses=None, bonuses=None, penalties=None):
        super(VehiclesComparator, self).__init__(currentVehicleParams, otherVehicleParams)
        self.__possibleBonuses = possibleBonuses or set()
        self.__bonuses = bonuses or set()
        self.__penalties = penalties or dict()

    def _getPenaltiesAndBonuses(self, paramName):
        penalties = self.__penalties.get(paramName, [])
        compatibleBonuses = params_cache.g_paramsCache.getBonuses().get(paramName, [])
        allBonuses = []
        for bonus in compatibleBonuses:
            bonusName, bonusGroup = bonus
            if bonus in self.__possibleBonuses or bonusGroup == 'skill' or bonusGroup == 'role' or bonusGroup == 'extra':
                allBonuses.append(bonus)

        bonusCondition = _getConditionsForParamBonuses(paramName, self.__bonuses)
        currBonuses = set([ bonus for bonus in self.__bonuses if bonus in allBonuses and bonusCondition(bonus) ])
        return (set(allBonuses) - currBonuses, currBonuses, penalties)


_ParameterInfo = collections.namedtuple('ParameterInfo', 'name, value, state, possibleBonuses, bonuses, penalties')
_CONDITIONAL_BONUSES = {'invisibilityMovingFactor': {('camouflage', 'skill'): [('chocolate', 'equipment'),
                                                        ('cocacola', 'equipment'),
                                                        ('ration', 'equipment'),
                                                        ('hotCoffee', 'equipment'),
                                                        ('ration_china', 'equipment'),
                                                        ('ration_uk', 'equipment'),
                                                        ('ration_japan', 'equipment'),
                                                        ('ration_czech', 'equipment'),
                                                        ('improvedVentilation_class1', 'optionalDevice'),
                                                        ('improvedVentilation_class2', 'optionalDevice'),
                                                        ('improvedVentilation_class3', 'optionalDevice')]},
 'invisibilityStillFactor': {('camouflage', 'skill'): [('chocolate', 'equipment'),
                                                       ('cocacola', 'equipment'),
                                                       ('ration', 'equipment'),
                                                       ('hotCoffee', 'equipment'),
                                                       ('ration_china', 'equipment'),
                                                       ('ration_uk', 'equipment'),
                                                       ('ration_japan', 'equipment'),
                                                       ('ration_czech', 'equipment'),
                                                       ('improvedVentilation_class1', 'optionalDevice'),
                                                       ('improvedVentilation_class2', 'optionalDevice'),
                                                       ('improvedVentilation_class3', 'optionalDevice')]}}

def _getConditionsForParamBonuses(paramName, allBonuses):
    if paramName in _CONDITIONAL_BONUSES:
        conditions = {}
        for condition, affected in _CONDITIONAL_BONUSES[paramName].iteritems():
            for affectedParam in affected:
                conditions.setdefault(affectedParam, []).append(condition)

        return lambda bonus: bonus not in conditions or all((c in allBonuses for c in conditions[bonus]))
    else:
        return lambda _: True


def _getComparableValue(currentValue, comparableList, idx):
    return comparableList[idx] if len(comparableList) > idx else currentValue


def _getParamStateInfo(paramName, val1, val2, valueIdx=None):
    if val1 is None or val2 is None:
        diff = 0
    else:
        diff = val1 - val2
    if diff == 0:
        return (PARAM_STATE.NORMAL, diff)
    else:
        if valueIdx is not None and paramName in CUSTOM_QUALITY_PARAMS:
            isInverted = CUSTOM_QUALITY_PARAMS[paramName][valueIdx]
        else:
            isInverted = paramName in BACKWARD_QUALITY_PARAMS
        if isInverted and diff > 0 or not isInverted and diff < 0:
            return (PARAM_STATE.WORSE, diff)
        return (PARAM_STATE.BETTER, diff)
        return


def rateParameterState(paramName, val1, val2):
    if isinstance(val1, collections.Iterable):
        return tuple([ _getParamStateInfo(paramName, val, _getComparableValue(val, val2, i), i) for i, val in enumerate(val1) ])
    return _getParamStateInfo(paramName, val1, val2)
