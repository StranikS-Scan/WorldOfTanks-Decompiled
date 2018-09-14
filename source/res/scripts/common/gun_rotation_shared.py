# Embedded file name: scripts/common/gun_rotation_shared.py
import BigWorld
import Math
from math import pi
from constants import IS_CLIENT, IS_CELLAPP
from debug_utils import *
if IS_CELLAPP:
    from server_constants import MAX_VEHICLE_RADIUS

def calcPitchLimitsFromDesc(turretYaw, pitchLimitsDesc):
    minPitch = pitchLimitsDesc['minPitch']
    maxPitch = pitchLimitsDesc['maxPitch']
    return BigWorld.wg_calcGunPitchLimits(turretYaw, minPitch, maxPitch)


def encodeAngleToUint(angle, bits):
    mask = (1 << bits) - 1
    return int(round((mask + 1) * (angle + pi) / (pi * 2.0))) & mask


def decodeAngleFromUint(code, bits):
    return pi * 2.0 * code / (1 << bits) - pi


def encodeRestrictedValueToUint(angle, bits, minBound, maxBound):
    t = (angle - minBound) / (maxBound - minBound)
    t = _clamp(0.0, t, 1.0)
    mask = (1 << bits) - 1
    return int(round(mask * t)) & mask


def decodeRestrictedValueFromUint(code, bits, minBound, maxBound):
    t = float(code) / ((1 << bits) - 1)
    return minBound + t * (maxBound - minBound)


def encodeGunAngles(yaw, pitch, pitchLimits):
    return encodeAngleToUint(yaw, 10) << 6 | encodeRestrictedValueToUint(pitch, 6, *pitchLimits)


def decodeGunAngles(code, pitchLimits):
    return (decodeAngleFromUint(code >> 6 & 1023, 10), decodeRestrictedValueFromUint((code & 63), 6, *pitchLimits))


def _clamp(minBound, value, maxBound):
    if value < minBound:
        return minBound
    if value > maxBound:
        return maxBound
    return value


def isShootPositionInsideOtherVehicle(vehicle, turretPosition, shootPosition):
    if IS_CLIENT:

        def getNearVehicles(vehicle, shootPosition):
            nearVehicles = []
            arenaVehicles = BigWorld.player().arena.vehicles
            for id in arenaVehicles.iterkeys():
                v = BigWorld.entities.get(id)
                if v and not v.isPlayer:
                    nearVehicles.append(v)

            return nearVehicles

    elif IS_CELLAPP:

        def getNearVehicles(vehicle, shootPosition):
            return vehicle.entitiesInRange(MAX_VEHICLE_RADIUS, 'Vehicle', shootPosition)

    nearVehicles = getNearVehicles(vehicle, shootPosition)
    for v in nearVehicles:
        if shootPosition.distTo(v.position) < v.typeDescriptor.boundingRadius and isSegmentCollideWithVehicle(v, turretPosition, shootPosition):
            return True

    return False


def isSegmentCollideWithVehicle(vehicle, startPoint, endPoint):
    if IS_CLIENT:

        def getVehicleSpaceMatrix(vehicle):
            toVehSpace = Math.Matrix(vehicle.model.matrix)
            toVehSpace.invert()
            return toVehSpace

        def getVehicleComponents(vehicle):
            return vehicle.getComponents()

    elif IS_CELLAPP:

        def getVehicleSpaceMatrix(vehicle):
            toVehSpace = Math.Matrix(vehicle.mover.matrix)
            toVehSpace.invert()
            return toVehSpace

        def getVehicleComponents(vehicle):
            return vehicle.getComponents(vehicle.gunAngles)

    toVehSpace = getVehicleSpaceMatrix(vehicle)
    vehStartPoint = toVehSpace.applyPoint(startPoint)
    vehEndPoint = toVehSpace.applyPoint(endPoint)
    for compDescr, toCompSpace, isAttached in getVehicleComponents(vehicle):
        if not isAttached or compDescr.get('itemTypeName') == 'vehicleGun':
            continue
        compStartPoint = toCompSpace.applyPoint(vehStartPoint)
        compEndPoint = toCompSpace.applyPoint(vehEndPoint)
        collisions = compDescr['hitTester'].localAnyHitTest(compStartPoint, compEndPoint)
        if collisions is not None:
            return True

    return False
