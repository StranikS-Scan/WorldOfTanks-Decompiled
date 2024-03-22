# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/helpers_common.py
import math
from typing import TYPE_CHECKING, Sequence, Optional, Tuple
from soft_exception import SoftException
from battle_modifiers_common import BattleModifiers
if TYPE_CHECKING:
    from battle_modifiers_common import BATTLE_MODIFIERS_TYPE
    from items.components.gun_components import GunShot
    from items.tankmen import TankmanDescr
TIME_UNITS = {'w': 604800,
 'd': 86400,
 'h': 3600,
 'm': 60,
 's': 1}
PI = math.pi
HALF_PI = PI * 0.5
HULL_AIMING_PITCH_BITS = 16

def bisectLE(a, v, lo=0, hi=None):
    if lo < 0:
        raise SoftException('lo must be non-negative')
    if hi is None:
        hi = len(a) - 1
    while lo < hi:
        mid = (lo + hi >> 1) + 1
        if a[mid] <= v:
            lo = mid
        hi = mid - 1

    return lo


def interpolateLinearly(arg, arg1, arg2, val1, val2, limitLower=False, limitUpper=False):
    if limitLower and arg <= arg1:
        return val1
    if limitUpper and arg >= arg2:
        return val2
    return val1 if arg1 == arg2 else val1 + (arg - arg1) * (val2 - val1) / (arg2 - arg1)


def computePiercingPowerAtDist(piercingPower, dist, modifiers=BattleModifiers()):
    constants = modifiers.getConstantsModification()
    piercingPowerValue = interpolateLinearly(dist, constants.PIERCING_POWER_INTERPOLATION_DIST_FIRST, constants.PIERCING_POWER_INTERPOLATION_DIST_LAST, piercingPower[0], piercingPower[1], limitLower=True, limitUpper=False)
    return max(0.0, piercingPowerValue)


def computeDamageAtDist(damages, dist, modifiers=BattleModifiers()):
    constants = modifiers.getConstantsModification()
    damageValue = interpolateLinearly(dist, constants.DAMAGE_INTERPOLATION_DIST_FIRST, constants.DAMAGE_INTERPOLATION_DIST_LAST, damages[0], damages[1], limitLower=True, limitUpper=False)
    return max(0.0, damageValue)


def computeMaxPiercingPowerDistance(piercingPower, modifiers=BattleModifiers()):
    if piercingPower[1] < piercingPower[0]:
        constants = modifiers.getConstantsModification()
        return interpolateLinearly(0.0, piercingPower[0], piercingPower[1], constants.PIERCING_POWER_INTERPOLATION_DIST_FIRST, constants.PIERCING_POWER_INTERPOLATION_DIST_LAST)
    else:
        return 1000000.0


def computeMaxDamageDistance(damages, modifiers=BattleModifiers()):
    if damages[1] < damages[0]:
        constants = modifiers.getConstantsModification()
        return interpolateLinearly(0.0, damages[0], damages[1], constants.DAMAGE_INTERPOLATION_DIST_FIRST, constants.DAMAGE_INTERPOLATION_DIST_LAST)
    else:
        return 1000000.0


def computeShotMaxDistance(shot, modifiers=BattleModifiers()):
    shell = shot.shell
    maxDistance = min(computeMaxDamageDistance(shell.armorDamage, modifiers), computeMaxDamageDistance(shell.deviceDamage, modifiers))
    if shell.isModernHE:
        for impact in shell.type.impacts:
            maxDistance = min(maxDistance, computeMaxDamageDistance(impact.armorDamage, modifiers), computeMaxDamageDistance(impact.deviceDamage, modifiers))

    return min(maxDistance, shot.nominalMaxDistance, computeMaxPiercingPowerDistance(shot.piercingPower, modifiers))


def getFinalRetrainCost(tmanDescr, cost):
    discountMult = 1.0
    if tmanDescr:
        discountMult = cost['discounts'].get('perk_{}'.format(tmanDescr.getFullSkillsCount()), 1.0)
    return (cost['credits'] * discountMult, cost['gold'] * discountMult)


def isAllRetrainOperationFree(tmanDescr, retrainCost):
    for _, cost in enumerate(retrainCost):
        credits, gold = getFinalRetrainCost(tmanDescr, cost)
        if credits or gold:
            return False

    return True


def getRetrainCost(tankmanCost, opts):
    retrainCosts = []
    for idx, (cost, option) in enumerate(zip(tankmanCost, opts)):
        cost = dict(cost.items() + option.items())
        retrainCosts.append(cost)

    return retrainCosts


def packFloat(value, minBound, maxBound, bits):
    t = (value - minBound) / (maxBound - minBound)
    t = max(0.0, min(t, 1.0))
    mask = (1 << bits) - 1
    return int(round(mask * t)) & mask


def unpacklFloat(packedValue, minBound, maxBound, bits):
    t = float(packedValue) / ((1 << bits) - 1)
    return minBound + t * (maxBound - minBound)


def packHullAimingPitch(angle):
    return packFloat(angle, -HALF_PI, HALF_PI, HULL_AIMING_PITCH_BITS)


def unpackHullAimingPitch(packedAngle):
    return unpacklFloat(packedAngle, -HALF_PI, HALF_PI, HULL_AIMING_PITCH_BITS)


def parseDuration(timeStr):
    timeStr = timeStr.strip()
    if timeStr == '0':
        return 0
    negative = timeStr[0] == '-'
    if negative:
        timeStr = timeStr[1:]
    parts = timeStr.split(' ')
    duration = 0
    for part in parts:
        value, unit = part[:-1], part[-1]
        duration += int(value) * TIME_UNITS[unit]

    if negative:
        duration = -duration
    return duration
