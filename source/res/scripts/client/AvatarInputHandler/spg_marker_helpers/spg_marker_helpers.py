# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/spg_marker_helpers/spg_marker_helpers.py
from enum import IntEnum
import BigWorld
import math_utils
from AvatarInputHandler import AimingSystems
from AvatarInputHandler.AimingSystems import CollisionStrategy
from Vehicle import Vehicle as VehicleEntity
_SPG_SHOT_RESULT_TOLERANCE = 0.25

class SPGShotResultEnum(IntEnum):
    NOT_HIT = 0
    HIT = 1


def getSPGShotResult(targetPosition, shotIdx, shotPos, shotVel, shotGravity, player=None, target=None):
    if player is None:
        player = BigWorld.player()
    shotResult = SPGShotResultEnum.NOT_HIT
    if targetPosition is None or player is None:
        return shotResult
    else:
        vehicleDescriptor = player.getVehicleDescriptor()
        shotDescr = vehicleDescriptor.getShot(shotIdx)
        minBounds, maxBounds = player.arena.getSpaceBB()
        endPos, _, collData, usedMaxDistance = AimingSystems.getCappedShotTargetInfos(shotPos, shotVel, shotGravity, shotDescr, player.playerVehicleID, minBounds, maxBounds, CollisionStrategy.COLLIDE_DYNAMIC_AND_STATIC)
        if not usedMaxDistance:
            if collData is None and (endPos - targetPosition).lengthSquared < _SPG_SHOT_RESULT_TOLERANCE:
                shotResult = SPGShotResultEnum.HIT
            elif collData is not None and collData.isVehicle():
                if target is None:
                    target = BigWorld.target()
                if isinstance(target, VehicleEntity):
                    targetVehicleID = target.id
                else:
                    targetVehicleID = None
                if targetVehicleID == collData.entity.id:
                    shotResult = SPGShotResultEnum.HIT
        return shotResult


def getSPGShotFlyTime(targetPosition, shotVelVector, shotPos, maxDistance, shotVel):
    distAxis = targetPosition - shotPos
    distAxis.y = 0
    distAxis.normalise()
    shotVelDA = shotVelVector.dot(distAxis)
    if math_utils.almostZero(shotVelDA):
        if shotVel != 0:
            return maxDistance / shotVel
        return -1.0
    return (targetPosition.dot(distAxis) - shotPos.dot(distAxis)) / shotVelDA
