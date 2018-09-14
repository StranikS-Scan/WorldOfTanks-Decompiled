# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/__init__.py
import math
import BigWorld
import Math
from Math import Vector3
from AvatarInputHandler import mathUtils
from AvatarInputHandler.mathUtils import MatrixProviders
from ProjectileMover import collideDynamicAndStatic
from vehicle_systems.tankStructure import TankPartNames
from debug_utils import LOG_CODEPOINT_WARNING

class IAimingSystem(object):
    matrix = property(lambda self: self._matrix)

    def __init__(self):
        self._matrix = mathUtils.createIdentityMatrix()

    def destroy(self):
        pass

    def enable(self, targetPos):
        pass

    def disable(self):
        pass

    def getDesiredShotPoint(self):
        pass

    def handleMovement(self, dx, dy):
        pass

    def update(self, deltaTime):
        pass


def getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw=0.0):
    turretOffset = vehicleTypeDescriptor.chassis['hullPosition'] + vehicleTypeDescriptor.hull['turretPositions'][0]
    turretJointMat = mathUtils.createRTMatrix(Vector3(turretYaw, 0, 0), turretOffset)
    turretJointMat.postMultiply(vehicleMatrix)
    return turretJointMat


def getGunJointMat(vehicleTypeDescriptor, turretMatrix, gunPitch):
    gunOffset = vehicleTypeDescriptor.turret['gunPosition']
    gunMat = mathUtils.createRTMatrix(Vector3(0, gunPitch, 0), gunOffset)
    gunMat.postMultiply(turretMatrix)
    return gunMat


def getPlayerTurretMats(turretYaw=0.0, gunPitch=0.0):
    player = BigWorld.player()
    vehicleTypeDescriptor = player.vehicleTypeDescriptor
    vehicleMatrix = player.getOwnVehicleStabilisedMatrix()
    turretMat = getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw)
    return (turretMat, getGunJointMat(vehicleTypeDescriptor, turretMat, gunPitch))


def getPlayerGunMat(turretYaw=0.0, gunPitch=0.0):
    return getPlayerTurretMats(turretYaw, gunPitch)[1]


def getTurretMatrixProvider(vehicleTypeDescriptor, vehicleMatrixProvider, turretYawMatrixProvider):
    turretOffset = vehicleTypeDescriptor.chassis['hullPosition'] + vehicleTypeDescriptor.hull['turretPositions'][0]
    return MatrixProviders.product(turretYawMatrixProvider, MatrixProviders.product(mathUtils.createTranslationMatrix(turretOffset), vehicleMatrixProvider))


def getGunMatrixProvider(vehicleTypeDescriptor, turretMatrixProvider, gunPitchMatrixProvider):
    gunOffset = vehicleTypeDescriptor.turret['gunPosition']
    return MatrixProviders.product(gunPitchMatrixProvider, MatrixProviders.product(mathUtils.createTranslationMatrix(gunOffset), turretMatrixProvider))


def getTurretYawGunPitch(vehTypeDescr, vehicleMatrix, targetPos, compensateGravity=False):
    turretOffs = vehTypeDescr.hull['turretPositions'][0] + vehTypeDescr.chassis['hullPosition']
    gunOffs = vehTypeDescr.turret['gunPosition']
    speed = vehTypeDescr.shot['speed']
    gravity = vehTypeDescr.shot['gravity'] if not compensateGravity else 0.0
    return BigWorld.wg_getShotAngles(turretOffs, gunOffs, vehicleMatrix, speed, gravity, 0.0, 0.0, targetPos, False)


def _getDesiredShotPointUncached(start, dir, onlyOnGround, isStrategicMode, terrainOnlyCheck):
    end = start + dir.scale(10000.0)
    if isStrategicMode:
        if terrainOnlyCheck:
            return __collideTerrainOnly(start, end)
        point1 = __collideStaticOnly(start, end)
        point2 = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), skipGun=isStrategicMode)
        if point1 is None or point2 is None:
            point = None
        else:
            dir = Math.Vector3(point2[0]) - Math.Vector3(point1[0])
            point = (Math.Vector3(point1[0]) + dir.scale(0.5), None)
    else:
        point = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), skipGun=isStrategicMode)
    if point is not None:
        return point[0]
    else:
        return shootInSkyPoint(start, dir) if not onlyOnGround else None


g_desiredShotPoint = Vector3(0)
g_frameStamp = -1

def getDesiredShotPoint(start, dir, onlyOnGround=False, isStrategicMode=False, terrainOnlyCheck=False):
    global g_desiredShotPoint
    global g_frameStamp
    currentFrameStamp = BigWorld.wg_getFrameTimestamp()
    if g_frameStamp == currentFrameStamp:
        return g_desiredShotPoint
    g_frameStamp = currentFrameStamp
    g_desiredShotPoint = _getDesiredShotPointUncached(start, dir, onlyOnGround, isStrategicMode, terrainOnlyCheck)
    return g_desiredShotPoint


def shootInSkyPoint(startPos, dir):
    dirFromCam = dir
    start = startPos
    dirFromCam.normalise()
    vehicle = BigWorld.player().vehicle
    if vehicle is not None and vehicle.inWorld and vehicle.isStarted and not vehicle.isTurretDetached:
        compoundModel = vehicle.appearance.compoundModel
        shotPos = Math.Vector3(compoundModel.node(TankPartNames.GUN).position)
        shotDesc = vehicle.typeDescriptor.shot
    else:
        type = BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID]['vehicleType']
        shotPos = BigWorld.player().getOwnVehiclePosition()
        shotPos += type.hull['turretPositions'][0] + type.turret['gunPosition']
        shotDesc = type.shot
    dirAtCam = shotPos - start
    dirAtCam.normalise()
    cosAngle = dirAtCam.dot(dirFromCam)
    a = shotDesc['maxDistance']
    b = shotPos.distTo(start)
    try:
        dist = b * cosAngle + math.sqrt(b * b * (cosAngle * cosAngle - 1) + a * a)
    except:
        dist = shotDesc['maxDistance']
        LOG_CODEPOINT_WARNING()

    if dist < 0.0:
        dist = shotDesc['maxDistance']
    finalPoint = start + dirFromCam.scale(dist)
    intersecPoint = BigWorld.player().arena.collideWithSpaceBB(start, finalPoint)
    if intersecPoint is not None:
        finalPoint = intersecPoint
    return finalPoint


def __collideTerrainOnly(start, end):
    waterHeight = BigWorld.wg_collideWater(start, end, False)
    resultWater = None
    if waterHeight != -1:
        resultWater = start - Math.Vector3(0, waterHeight, 0)
    testResTerrain = BigWorld.wg_collideSegment(BigWorld.player().spaceID, start, end, 128, 8)
    result = testResTerrain[0] if testResTerrain is not None else None
    if resultWater is not None:
        distance = (result - start).length
        if distance - waterHeight < 0.2:
            return result
        return resultWater
    else:
        return result


def __collideStaticOnly(startPoint, endPoint):
    res = None
    testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, startPoint, endPoint, 128)
    if testRes is not None:
        res = (testRes[0], None)
    return res
