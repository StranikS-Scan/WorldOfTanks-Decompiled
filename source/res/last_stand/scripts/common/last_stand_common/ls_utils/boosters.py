# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/common/last_stand_common/ls_utils/boosters.py
from last_stand_common.last_stand_constants import BOOSTER_FACTOR_OPERATIONS

def getVehicleBoosterFactorsComponent(vehicle):
    return getattr(vehicle, 'lsBoosterFactors', None)


def applyBoosterFactors(value, factorName, factors):
    factorsByName = factors.get(factorName, {})
    return value + value * factorsByName.get(BOOSTER_FACTOR_OPERATIONS.ADD_PERCENT, 0.0) + factorsByName.get(BOOSTER_FACTOR_OPERATIONS.ADD, 0.0)


def getFactorsDiff(factors1, factors2):
    factors1 = factors1 or {}
    factors2 = factors2 or {}
    factorsName = set()
    for fName in set(factors1.keys()) | set(factors2.keys()):
        entry1 = factors1.get(fName, {})
        entry2 = factors2.get(fName, {})
        if any((entry1.get(op) != entry2.get(op) for op in set(entry1.keys()) | set(entry2.keys()))):
            factorsName.add(fName)

    return factorsName
