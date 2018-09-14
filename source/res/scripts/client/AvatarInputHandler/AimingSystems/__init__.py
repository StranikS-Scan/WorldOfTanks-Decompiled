# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/__init__.py
import math
from functools import wraps
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

    @property
    def aimMatrix(self):
        """Returns reference of matrix that containing transformation of player aiming.
        But it may not consider collision with game objects and camera transformation equals
        aim transformation by default."""
        return self._matrix

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

    def getShotPoint(self):
        return None

    def getZoom(self):
        return None


def getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw=0.0, overrideTurretLocalZ=None):
    turretOffset = getTurretJointOffset(vehicleTypeDescriptor)
    if overrideTurretLocalZ is not None:
        turretOffset.z = overrideTurretLocalZ
    turretJointMat = mathUtils.createRTMatrix(Vector3(turretYaw, 0, 0), turretOffset)
    turretJointMat.postMultiply(vehicleMatrix)
    return turretJointMat


def getTurretJointOffset(vehicleTypeDescriptor):
    return vehicleTypeDescriptor.chassis['hullPosition'] + vehicleTypeDescriptor.hull['turretPositions'][0]


def getGunJointMat(vehicleTypeDescriptor, turretMatrix, gunPitch, overrideTurretLocalZ=None):
    gunOffset = Vector3(vehicleTypeDescriptor.turret['gunPosition'])
    if overrideTurretLocalZ is not None:
        offset = getTurretJointOffset(vehicleTypeDescriptor)
        yOffset = math.tan(gunPitch) * offset.z
        gunOffset.y += yOffset
    gunMat = mathUtils.createRTMatrix(Vector3(0, gunPitch, 0), gunOffset)
    gunMat.postMultiply(turretMatrix)
    return gunMat


def getPlayerTurretMats(turretYaw=0.0, gunPitch=0.0, overrideTurretLocalZ=None):
    player = BigWorld.player()
    if player.isObserver() and player.getVehicleAttached() is not None:
        vehicleTypeDescriptor = player.getVehicleAttached().typeDescriptor
    else:
        vehicleTypeDescriptor = player.vehicleTypeDescriptor
    isPitchHullAimingAvailable = vehicleTypeDescriptor.isPitchHullAimingAvailable
    vehicleMatrix = player.inputHandler.steadyVehicleMatrixCalculator.outputMProv
    correctGunPitch = gunPitch
    if isPitchHullAimingAvailable:
        vehicleMatrix = player.inputHandler.steadyVehicleMatrixCalculator.stabilisedMProv
        correctGunPitch = 0.0
    turretMat = getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw, overrideTurretLocalZ)
    gunMat = getGunJointMat(vehicleTypeDescriptor, turretMat, correctGunPitch, overrideTurretLocalZ)
    if not isPitchHullAimingAvailable:
        return (turretMat, gunMat)
    else:
        turretMatTranslation = turretMat.translation
        gunMatTranslation = gunMat.translation
        vehicleMatrix = player.inputHandler.steadyVehicleMatrixCalculator.outputMProv
        turretMat = getTurretJointMat(vehicleTypeDescriptor, vehicleMatrix, turretYaw)
        gunMat = getGunJointMat(vehicleTypeDescriptor, turretMat, gunPitch)
        if overrideTurretLocalZ is not None:
            gunMatTranslation += _calculateGunPointOffsetFromHullCenter(vehicleTypeDescriptor, vehicleMatrix, player.inputHandler.steadyVehicleMatrixCalculator.stabilisedMProv, gunPitch, overrideTurretLocalZ)
        turretMat.translation = turretMatTranslation
        gunMat.translation = gunMatTranslation
        return (turretMat, gunMat)


def getPlayerGunMat(turretYaw=0.0, gunPitch=0.0, overrideTurretLocalZ=None):
    return getPlayerTurretMats(turretYaw, gunPitch, overrideTurretLocalZ)[1]


def getCenteredPlayerGunMat(turretYaw=0.0, gunPitch=0.0):
    return getPlayerTurretMats(turretYaw, gunPitch, 0.0)[1]


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


def _calculateGunPointOffsetFromHullCenter(vehicleTypeDescriptor, steadyMatrix, stabilisedMatrix, gunPitch, overrideTurretLocalZ):
    turretOffset = getTurretJointOffset(vehicleTypeDescriptor)
    hullLocal = Math.Matrix(steadyMatrix)
    hullLocal.invert()
    hullLocal.preMultiply(stabilisedMatrix)
    projectedOffset = math.cos(hullLocal.pitch) * abs(turretOffset.z - overrideTurretLocalZ)
    upVector = Math.Matrix(steadyMatrix).applyToAxis(1)
    upOffsetGunPitch = math.tan(-gunPitch) * projectedOffset
    upOffsetHullPitch = math.tan(hullLocal.pitch) * projectedOffset
    return upVector * (upOffsetGunPitch + upOffsetHullPitch)


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


def _trackcalls(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.has_been_called = True
        return func(*args, **kwargs)

    wrapper.has_been_called = False
    return wrapper


@_trackcalls
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
