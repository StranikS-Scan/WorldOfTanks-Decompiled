# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/helpers_common.py
from __future__ import absolute_import, division
import math
import typing
from constants import VEHICLE_HIT_EFFECT
from soft_exception import SoftException
from battle_modifiers_common import BattleModifiers
from Math import Vector3
from math_common import decimal_round, round_py2_style_int
from debug_utils import LOG_WARNING
from items import vehicles
if typing.TYPE_CHECKING:
    from typing import Sequence, Optional, Tuple, List, Union, Dict
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


def computeMaxDamageDistance(damages, modifiers=BattleModifiers()):
    if damages[1] < damages[0]:
        constants = modifiers.getConstantsModification()
        return interpolateLinearly(0.0, damages[0], damages[1], constants.DAMAGE_INTERPOLATION_DIST_FIRST, constants.DAMAGE_INTERPOLATION_DIST_LAST)


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
    for cost, option in zip(tankmanCost, opts):
        cost = dict(cost.items() + option.items())
        retrainCosts.append(cost)

    return retrainCosts


def packFloat(value, minBound, maxBound, bits):
    t = (value - minBound) / (maxBound - minBound)
    t = max(0.0, min(t, 1.0))
    mask = (1 << bits) - 1
    return round_py2_style_int(mask * t) & mask


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


def packChunkObstacles(obstacles):
    return [ chunkID << 16 | itemIndex << 8 | matKind for chunkID, itemIndex, matKind in obstacles ]


def unpackChunkObstacles(obstacles):
    return [ (int(code >> 16), int(code >> 8 & 255), int(code & 255)) for code in obstacles ]


def castNumberToPrettyStr(value):
    if isinstance(value, float):
        return str(value).rstrip('0').rstrip('.')
    return str(value) if isinstance(value, int) else value


def getPercentFromFloat(value, accuracy=2):
    return decimal_round(value * 100, accuracy)


def _clipSegmentByAABB(start, stop, aabb):
    min = Vector3(aabb[0])
    max = Vector3(aabb[1])
    start = Vector3(start)
    stop = Vector3(stop)
    delta = stop - start
    tbeg = 0.0
    tend = 1.0
    for i in (0, 1, 2):
        d = delta[i]
        if d:
            t1 = (min[i] - start[i]) / d
            t2 = (max[i] - start[i]) / d
            if d > 0.0:
                if t1 > tend:
                    return None
                if t1 > tbeg:
                    tbeg = t1
                if t2 < tbeg:
                    return None
                if t2 < tend:
                    tend = t2
            else:
                if t2 > tend:
                    return None
                if t2 > tbeg:
                    tbeg = t2
                if t1 < tbeg:
                    return None
                if t1 < tend:
                    tend = t1
        if start[i] < min[i] or start[i] > max[i]:
            return None

    return (start + tbeg * delta, start + tend * delta)


def encodeSegment(bbox, componentIndex, startPoint, endPoint):
    test = _clipSegmentByAABB(startPoint, endPoint, bbox)
    if test is None:
        LOG_WARNING('Cannot encode segment', startPoint, endPoint, bbox)
        return componentIndex << 8
    else:
        min = Vector3(bbox[0])
        max = Vector3(bbox[1])
        a = (test[0] - min) * 255
        b = (test[1] - min) * 255
        d = max - min
        return round_py2_style_int(b[2] / d[2]) << 56 | round_py2_style_int(b[1] / d[1]) << 48 | round_py2_style_int(b[0] / d[0]) << 40 | round_py2_style_int(a[2] / d[2]) << 32 | round_py2_style_int(a[1] / d[1]) << 24 | round_py2_style_int(a[0] / d[0]) << 16 | componentIndex << 8


def getComponentIndexFromEncodedSegment(segment):
    return (segment & 65280) >> 8


def getEncodedSegmentContextData(segment):
    return segment & 255


def setEncodedSegmentContextData(segment, data):
    return segment & -256 | data & 255


def decodeSegment(segment, bbox):
    minimum = Vector3(bbox[0])
    delta = (bbox[1] - minimum).scale(0.00392156862745098)
    segStart = minimum + Vector3(delta[0] * (segment >> 16 & 255), delta[1] * (segment >> 24 & 255), delta[2] * (segment >> 32 & 255))
    segEnd = minimum + Vector3(delta[0] * (segment >> 40 & 255), delta[1] * (segment >> 48 & 255), delta[2] * (segment >> 56 & 255))
    offset = (segEnd - segStart) * 0.01
    return (int(segment >> 8 & 255),
     int(segment & 255),
     segStart - offset,
     segEnd + offset)


def reprSlots(self):
    return '%s(%s)' % (self.__class__.__name__, ', '.join(('%s=%s' % (name, getattr(self, name, 'NOT_FOUND')) for name in self.__slots__)))


class HitParamsEncoder(object):
    INVALID_HIT_PARAMS = 255

    @classmethod
    def encode(cls, hitType, shellType, caliber):
        return (int(caliber * 10) & 65535) << 8 | (shellType & 15) << 4 | hitType & 15

    @staticmethod
    def decode(params):
        return (params & 15, params >> 4 & 15, (params >> 8 & 65535) * 0.1)

    @staticmethod
    def setHitType(params, hitType):
        return params & -16 | hitType & 15

    @staticmethod
    def getHitType(params):
        return params & 15

    @staticmethod
    def setPrefabEffIndex(params, prefabEffIndex):
        return params & -4278190081L | (prefabEffIndex & 255) << 24

    @staticmethod
    def getPrefabEffIndex(params):
        return params >> 24 & 255


def setDamageSticker(sticker, effectsIndex, prefabEffIndex, isPierced):
    cache = vehicles.g_cache
    hitType = HitParamsEncoder.getHitType(sticker['params'])
    if not isPierced and hitType in VEHICLE_HIT_EFFECT.PIERCED_HITS:
        hitType = VEHICLE_HIT_EFFECT.ARMOR_NOT_PIERCED
        sticker['params'] = HitParamsEncoder.setHitType(sticker['params'], hitType)
    stickerTypeName = 'armorPierced' if isPierced else 'armorResisted'
    stickerID = cache.shotEffects[effectsIndex]['targetStickers'][stickerTypeName]
    if stickerID is None:
        return
    else:
        priority = cache.damageStickers['descrs'][stickerID]['priority']
        sticker['segment'] = setEncodedSegmentContextData(sticker['segment'], stickerID)
        sticker['params'] = HitParamsEncoder.setPrefabEffIndex(sticker['params'], prefabEffIndex)
        return priority
