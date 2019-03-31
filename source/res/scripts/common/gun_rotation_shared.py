# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/gun_rotation_shared.py
# Compiled at: 2011-10-06 14:54:10
import BigWorld
from math import pi
from constants import DEFAULT_GUN_PITCH_LIMITS_TRANSITION

def calcPitchLimits(turretYaw, basicLimits, frontLimits, backLimits, transition):
    if transition is None:
        transition = DEFAULT_GUN_PITCH_LIMITS_TRANSITION
    if frontLimits is not None:
        absYaw = abs(turretYaw)
        if absYaw < frontLimits[2]:
            return (frontLimits[0], frontLimits[1])
        if absYaw < frontLimits[2] + transition:
            t = (absYaw - frontLimits[2]) / transition
            minPitch = frontLimits[0] * (1.0 - t) + basicLimits[0] * t
            maxPitch = frontLimits[1] * (1.0 - t) + basicLimits[1] * t
            return (minPitch, maxPitch)
    if backLimits is not None:
        absYawDiff = abs(abs(turretYaw) - pi)
        if absYawDiff < backLimits[2]:
            return (backLimits[0], backLimits[1])
        if absYawDiff < backLimits[2] + transition:
            t = (absYawDiff - backLimits[2]) / transition
            minPitch = backLimits[0] * (1.0 - t) + basicLimits[0] * t
            maxPitch = backLimits[1] * (1.0 - t) + basicLimits[1] * t
            return (minPitch, maxPitch)
    return basicLimits


def calcPitchLimitsFromDesc(turretYaw, pitchLimitsDesc):
    return calcPitchLimits(turretYaw, pitchLimitsDesc['basic'], pitchLimitsDesc.get('front'), pitchLimitsDesc.get('back'), pitchLimitsDesc.get('transition'))
