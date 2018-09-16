# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/shooting_utils.py
import WGAI
import math
from constants import SERVER_TICK_LENGTH, SHELL_TRAJECTORY_EPSILON_SERVER
__DIST_LIMIT_TAGS = ['lightTank',
 'mediumTank',
 'heavyTank',
 'AT-SPG']
__STEEP_AIMING_TAGS = []
__MIXED_AIMING_TAGS = []

class TrajectoryMode(object):
    FLAT_AIMING = 0
    STEEP_AIMING = 1
    MIXED_AIMING = 2


def getMaxShotDistance(height, vehicleDescr):
    shotDescr = vehicleDescr.shot
    speed = shotDescr.speed
    gravity = shotDescr.gravity
    radicand = 2.0 * (speed * speed + gravity * height)
    if radicand <= 0.0:
        return -1
    time = math.sqrt(radicand) / gravity
    sinP = (-height + gravity * time * time * 0.5) / (speed * time)
    sqrCosP = 1.0 - sinP * sinP
    return -1 if sqrCosP <= 0.0 else math.sqrt(sqrCosP) * speed * time


def getPyShootingTest(spaceID, vehicleDescr):
    global __STEEP_AIMING_TAGS
    global __MIXED_AIMING_TAGS
    global __DIST_LIMIT_TAGS
    shotDescr = vehicleDescr.shot
    gunDescr = vehicleDescr.gun
    vehicleTags = vehicleDescr.type.tags
    shootingTest = WGAI.PyShootingTest()
    shootingTest.speed = shotDescr.speed
    shootingTest.gravity = shotDescr.gravity
    turPos = vehicleDescr.hull.turretPositions[0] + vehicleDescr.chassis.hullPosition
    shootingTest.turretPositionLocal = turPos
    shootingTest.gunPositionLocal = vehicleDescr.turret.gunPosition
    staticPitch = gunDescr.staticPitch
    isPitchHullAimingEnabled = vehicleDescr.type.hullAimingParams['pitch']['isEnabled']
    pitchLimitsDesc = None
    if staticPitch is not None:
        if not isPitchHullAimingEnabled:
            zeroLimits = ((0.0, staticPitch), (2.0 * math.pi, staticPitch))
            pitchLimitsDesc = {'minPitch': zeroLimits,
             'maxPitch': zeroLimits,
             'absolute': (staticPitch, staticPitch)}
    if pitchLimitsDesc is None:
        pitchLimitsDesc = gunDescr.pitchLimits
    shootingTest.minGunPitchLimits = pitchLimitsDesc['minPitch']
    shootingTest.maxGunPitchLimits = pitchLimitsDesc['maxPitch']
    shootingTest.trajectoryMode = TrajectoryMode.FLAT_AIMING
    for tag in __STEEP_AIMING_TAGS:
        if tag in vehicleTags:
            shootingTest.trajectoryMode = TrajectoryMode.STEEP_AIMING
            break

    if shootingTest.trajectoryMode == TrajectoryMode.FLAT_AIMING:
        for tag in __MIXED_AIMING_TAGS:
            if tag in vehicleTags:
                shootingTest.trajectoryMode = TrajectoryMode.MIXED_AIMING
                break

    shootingTest.useDistanceLimit = False
    for tag in __DIST_LIMIT_TAGS:
        if tag in vehicleTags:
            shootingTest.useDistanceLimit = True
            break

    shootingTest.spaceID = spaceID
    shootingTest.timePeriod = SERVER_TICK_LENGTH
    shootingTest.epsilon = SHELL_TRAJECTORY_EPSILON_SERVER
    return shootingTest


def _getPyShootingTestYawLimits(spaceID, vehicleDescr):
    shootingTest = getPyShootingTest(spaceID, vehicleDescr)
    yawLimits = vehicleDescr.gun.turretYawLimits
    if yawLimits is not None:
        shootingTest.turretYawLimits = yawLimits
    return shootingTest


class ShootingTest(object):

    def __init__(self, spaceID, vehicleDescr):
        self.__impl = _getPyShootingTestYawLimits(spaceID, vehicleDescr)

    def updateVehicleMatrix(self, vehicleMatrix):
        self.__impl.vehicleMatrix = vehicleMatrix

    def setTargetEntity(self, targetEntity):
        self.__impl.targetEntity = targetEntity

    def setEntitiesToAvoid(self, entitiesToAvoid):
        self.__impl.entitiesToAvoid = entitiesToAvoid

    def setEntityCollisionCallback(self, entityCollisionCallback):
        self.__impl.entityCollisionCb = entityCollisionCallback

    def getCurTrajectoryMode(self):
        return self.__impl.curTrajectoryMode

    def setDestructibleHealthCallback(self, destructibleHealthCallback):
        self.__impl.destructibleHealthCb = destructibleHealthCallback

    def canShootAtPoint(self, targetPosition):
        return WGAI.canShootAtPoint(self.__impl, targetPosition)

    def canShootAtPointFixedAngles(self, targetPosition, turretYaw, gunPitch):
        return WGAI.canShootAtPointFixedAngles(self.__impl, targetPosition, turretYaw, gunPitch)
