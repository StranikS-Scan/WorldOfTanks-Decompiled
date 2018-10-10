# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleGunRotator.py
import weakref
import math
from math import pi, fmod
import BigWorld
import Math
from AvatarInputHandler import AimingSystems, mathUtils
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from constants import SERVER_TICK_LENGTH, SHELL_TRAJECTORY_EPSILON_CLIENT, AIMING_MODE, VEHICLE_SIEGE_STATE
import ProjectileMover
from ClientArena import CollisionResult
from projectile_trajectory import getShotAngles
from projectile_trajectory import computeProjectileTrajectory
import BattleReplay
from gun_rotation_shared import calcPitchLimitsFromDesc, getLocalAimPoint
import SoundGroups
import WWISE
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartNames
from helpers import gEffectsDisabled

class VehicleGunRotator(object):
    __INSUFFICIENT_TIME_DIFF = 0.02
    __MAX_TIME_DIFF = 0.2
    __ANGLE_EPS = 1e-06
    __ROTATION_TICK_LENGTH = SERVER_TICK_LENGTH
    __AIMING_PERFECTION_DELAY = 1.0
    __AIMING_PERFECTION_RANGE = math.radians(5.0)
    __TURRET_YAW_ALLOWED_ERROR_FACTOR = 0.4
    __TURRET_YAW_ALLOWED_ERROR_CONST = math.radians(8.0)
    USE_LOCK_PREDICTION = True
    soundEffect = property(lambda self: self.__turretRotationSoundEffect)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, avatar):
        self.__avatar = weakref.proxy(avatar)
        self.__isStarted = False
        self.__prevSentShotPoint = None
        self.__targetLastShotPoint = False
        self.__lastShotPoint = Math.Vector3(0, 0, 0)
        self.__shotPointSourceFunctor = self.__shotPointSourceFunctor_Default
        self.__maxTurretRotationSpeed = None
        self.__maxGunRotationSpeed = None
        self.__turretYaw = 0.0
        self.__gunPitch = 0.0
        self.__turretRotationSpeed = 0.0
        self.__dispersionAngles = [0.0, 0.0]
        self.__markerInfo = (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 1.0, 0.0), 1.0)
        self.__clientMode = True
        self.__showServerMarker = False
        self.__time = None
        self.__timerID = None
        self.__turretMatrixAnimator = _MatrixAnimator(self.__avatar)
        self.__gunMatrixAnimator = _MatrixAnimator(self.__avatar)
        self.__isLocked = False
        self.estimatedTurretRotationTime = 0
        if not gEffectsDisabled():
            self.__turretRotationSoundEffect = _PlayerTurretRotationSoundEffectWWISE()
        else:
            self.__turretRotationSoundEffect = None
        self.__aimingPerfectionStartTime = None
        return

    def destroy(self):
        self.stop()
        self.__turretMatrixAnimator.destroy(self.__avatar)
        self.__gunMatrixAnimator.destroy(self.__avatar)
        self.__avatar = None
        self.__shotPointSourceFunctor = None
        if self.__turretRotationSoundEffect is not None:
            self.__turretRotationSoundEffect.destroy()
            self.__turretRotationSoundEffect = None
        return

    def start(self):
        if self.__isStarted:
            return
        elif self.__maxTurretRotationSpeed is None:
            return
        elif not self.__avatar.isOnArena:
            return
        else:
            self.settingsCore.onSettingsChanged += self.applySettings
            self.showServerMarker = self.settingsCore.getSetting('useServerAim')
            self.__isStarted = True
            self.__updateGunMarker()
            self.__timerID = BigWorld.callback(self.__ROTATION_TICK_LENGTH, self.__onTick)
            if self.__clientMode:
                self.__time = BigWorld.time()
                if self.__showServerMarker:
                    self.__avatar.inputHandler.showGunMarker2(True)
            if self.__turretRotationSoundEffect is None and not gEffectsDisabled:
                self.__turretRotationSoundEffect = _PlayerTurretRotationSoundEffectWWISE()
            return

    def stop(self):
        if self.__timerID is not None:
            BigWorld.cancelCallback(self.__timerID)
            self.__timerID = None
        if self.__turretRotationSoundEffect is not None:
            self.__turretRotationSoundEffect.destroy()
            self.__turretRotationSoundEffect = None
        if not self.__isStarted:
            return
        else:
            self.__isStarted = False
            self.settingsCore.onSettingsChanged -= self.applySettings
            if self.__avatar.inputHandler is None:
                return
            if self.__clientMode and self.__showServerMarker:
                self.__showServerMarker = False
                self.__avatar.inputHandler.showGunMarker2(False)
            return

    def applySettings(self, diff):
        if 'useServerAim' in diff:
            self.showServerMarker = diff['useServerAim']

    def lock(self, isLocked):
        self.__isLocked = isLocked

    def reset(self):
        self.__turretYaw = self.__gunPitch = 0.0
        self.__updateTurretMatrix(0.0, 0.0)
        self.__updateGunMatrix(0.0, 0.0)
        self.__isLocked = False

    def update(self, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed):
        if self.__timerID is None or maxTurretRotationSpeed < self.__maxTurretRotationSpeed:
            self.__turretYaw, self.__gunPitch = turretYaw, gunPitch
            self.__updateTurretMatrix(turretYaw, 0.0)
            self.__updateGunMatrix(gunPitch, 0.0)
        self.__maxTurretRotationSpeed = maxTurretRotationSpeed
        self.__maxGunRotationSpeed = maxGunRotationSpeed
        self.__turretRotationSpeed = 0.0
        self.__dispersionAngles = self.__avatar.getOwnVehicleShotDispersionAngle(0.0)
        self.start()
        return

    def forceGunParams(self, turretYaw, gunPitch, dispAngle):
        self.__turretYaw = turretYaw
        self.__gunPitch = gunPitch
        self.__dispersionAngles = [dispAngle, dispAngle]
        self.__updateGunMarker(0.001)

    def setShotPosition(self, vehicleID, shotPos, shotVec, dispersionAngle, forceValueRefresh=False):
        if self.__clientMode and not self.__showServerMarker and not forceValueRefresh:
            return
        else:
            self.__dispersionAngles[0] = dispersionAngle
            if not self.__clientMode and VehicleGunRotator.USE_LOCK_PREDICTION:
                lockEnabled = BigWorld.player().inputHandler.getAimingMode(AIMING_MODE.TARGET_LOCK)
                if lockEnabled:
                    predictedTargetPos = self.predictLockedTargetShotPoint()
                    if predictedTargetPos is None:
                        return
                    dirToTarget = predictedTargetPos - shotPos
                    dirToTarget.normalise()
                    shotDir = Math.Vector3(shotVec)
                    shotDir.normalise()
                    if shotDir.dot(dirToTarget) > 0.0:
                        return
            markerPos, markerDir, markerSize, idealMarkerSize, collData = self.__getGunMarkerPosition(shotPos, shotVec, self.__dispersionAngles)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setGunMarkerParams(markerSize, markerPos, markerDir)
            if self.__clientMode and self.__showServerMarker:
                self.__avatar.inputHandler.updateGunMarker2(markerPos, markerDir, (markerSize, idealMarkerSize), SERVER_TICK_LENGTH, collData)
            if not self.__clientMode or forceValueRefresh:
                self.__lastShotPoint = markerPos
                self.__avatar.inputHandler.updateGunMarker(markerPos, markerDir, (markerSize, idealMarkerSize), SERVER_TICK_LENGTH, collData)
                self.__turretYaw, self.__gunPitch = getShotAngles(self.__avatar.getVehicleDescriptor(), self.__avatar.getOwnVehicleStabilisedMatrix(), (self.__turretYaw, self.__gunPitch), markerPos, True)
                turretYawLimits = self.__getTurretYawLimits()
                closestLimit = self.__isOutOfLimits(self.__turretYaw, turretYawLimits)
                if closestLimit is not None:
                    self.__turretYaw = closestLimit
                self.__updateTurretMatrix(self.__turretYaw, SERVER_TICK_LENGTH)
                self.__updateGunMatrix(self.__gunPitch, SERVER_TICK_LENGTH)
                self.__markerInfo = (markerPos, markerDir, markerSize)
            return

    def predictLockedTargetShotPoint(self):
        autoAimVehicle = BigWorld.player().autoAimVehicle
        if autoAimVehicle is not None:
            autoAimPosition = Math.Vector3(autoAimVehicle.position)
            offset = getLocalAimPoint(autoAimVehicle.typeDescriptor)
            autoAimPosition += Math.Matrix(autoAimVehicle.matrix).applyVector(offset)
            return autoAimPosition
        else:
            return

    def getShotParams(self, targetPoint, ignoreYawLimits=False):
        descr = self.__avatar.getVehicleAttached().typeDescriptor
        shotTurretYaw, shotGunPitch = getShotAngles(descr, self.__avatar.getOwnVehicleStabilisedMatrix(), (self.__turretYaw, self.__gunPitch), targetPoint)
        gunPitchLimits = calcPitchLimitsFromDesc(shotTurretYaw, self.__getGunPitchLimits())
        closestLimit = self.__isOutOfLimits(shotGunPitch, gunPitchLimits)
        if closestLimit is not None:
            shotGunPitch = closestLimit
        turretYawLimits = self.__getTurretYawLimits()
        if not ignoreYawLimits:
            closestLimit = self.__isOutOfLimits(shotTurretYaw, turretYawLimits)
            if closestLimit is not None:
                shotTurretYaw = closestLimit
        pos, vel = self.__getShotPosition(shotTurretYaw, shotGunPitch)
        grav = Math.Vector3(0.0, -descr.shot.gravity, 0.0)
        return (pos, vel, grav)

    def getCurShotPosition(self):
        return self.__getShotPosition(self.__turretYaw, self.__gunPitch)

    def __set_clientMode(self, value):
        if self.__clientMode == value:
            return
        self.__clientMode = value
        if not self.__isStarted:
            return
        if self.__clientMode:
            self.__time = BigWorld.time()
            self.stopTrackingOnServer()
        if self.__showServerMarker:
            self.__avatar.inputHandler.showGunMarker2(self.__clientMode)

    clientMode = property(lambda self: self.__clientMode, __set_clientMode)

    def __set_showServerMarker(self, value):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            return
        if self.__showServerMarker == value:
            return
        self.__showServerMarker = value
        BigWorld.player().enableServerAim(self.showServerMarker)
        if not self.__isStarted:
            return
        if self.__clientMode:
            self.__avatar.inputHandler.showGunMarker2(self.__showServerMarker)

    showServerMarker = property(lambda self: self.__showServerMarker, __set_showServerMarker)

    def __set_targetLastShotPoint(self, value):
        self.__targetLastShotPoint = value

    targetLastShotPoint = property(lambda self: self.__targetLastShotPoint, __set_targetLastShotPoint)

    def __set_shotPointSourceFunctor(self, value):
        if value is not None:
            self.__shotPointSourceFunctor = value
        else:
            self.__shotPointSourceFunctor = self.__shotPointSourceFunctor_Default
        return

    shotPointSourceFunctor = property(lambda self: self.__shotPointSourceFunctor, __set_shotPointSourceFunctor)

    def __shotPointSourceFunctor_Default(self):
        return self.__avatar.inputHandler.getDesiredShotPoint()

    turretMatrix = property(lambda self: self.__turretMatrixAnimator.matrix)
    gunMatrix = property(lambda self: self.__gunMatrixAnimator.matrix)
    turretRotationSpeed = property(lambda self: self.__turretRotationSpeed)
    maxturretRotationSpeed = property(lambda self: self.__maxTurretRotationSpeed)
    dispersionAngle = property(lambda self: self.__dispersionAngles[0])
    markerInfo = property(lambda self: self.__markerInfo)
    turretYaw = property(lambda self: self.__turretYaw)
    gunPitch = property(lambda self: self.__gunPitch)

    def updateRotationAndGunMarker(self, shotPoint, timeDiff):
        self.__rotate(shotPoint, timeDiff)
        self.__updateGunMarker()

    def __onTick(self):
        self.__timerID = BigWorld.callback(self.__ROTATION_TICK_LENGTH, self.__onTick)
        lockEnabled = BigWorld.player().inputHandler.getAimingMode(AIMING_MODE.TARGET_LOCK)
        usePredictedLockShotPoint = lockEnabled and VehicleGunRotator.USE_LOCK_PREDICTION
        replayCtrl = BattleReplay.g_replayCtrl
        if not self.__clientMode and not replayCtrl.isPlaying and not usePredictedLockShotPoint:
            return
        else:
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying:
                shotPoint = replayCtrl.getGunRotatorTargetPoint()
            else:
                predictedLockShotPoint = self.predictLockedTargetShotPoint() if usePredictedLockShotPoint else None
                shotPoint = self.__shotPointSourceFunctor() if predictedLockShotPoint is None else predictedLockShotPoint
            if shotPoint is None and self.__targetLastShotPoint:
                shotPoint = self.__lastShotPoint
            if replayCtrl.isRecording:
                if shotPoint is not None:
                    replayCtrl.setGunRotatorTargetPoint(shotPoint)
            self.__updateShotPointOnServer(shotPoint)
            timeDiff = self.__getTimeDiff()
            if timeDiff is None:
                return
            self.__time = BigWorld.time()
            self.updateRotationAndGunMarker(shotPoint, timeDiff)
            if replayCtrl.isPlaying:
                replayCtrl.resetUpdateGunOnTimeWarp()
            return

    def __getTimeDiff(self):
        timeDiff = BigWorld.time() - self.__time
        if timeDiff < self.__INSUFFICIENT_TIME_DIFF:
            return None
        else:
            if timeDiff > self.__MAX_TIME_DIFF:
                timeDiff = self.__MAX_TIME_DIFF
            return timeDiff

    def __calcAngleBetweenShotPointAndMarker(self):
        if self.__prevSentShotPoint is None:
            return
        else:
            shotStartPos, _ = self.getCurShotPosition()
            markerDelta = self.__markerInfo[0] - shotStartPos
            shotPointDelta = self.__prevSentShotPoint - shotStartPos
            sine = (markerDelta * shotPointDelta).length
            cosine = markerDelta.dot(shotPointDelta)
            return abs(math.atan2(sine, cosine))

    def __trackPointOnServer(self, shotPoint):
        avatar = self.__avatar
        vehicle = BigWorld.entity(avatar.playerVehicleID)
        if vehicle is not None and vehicle is avatar.vehicle:
            stabilisedVehPos = Math.Matrix(avatar.getOwnVehicleStabilisedMatrix()).translation
            vehicle.cell.trackRelativePointWithGun(shotPoint - stabilisedVehPos)
        else:
            avatar.base.vehicle_trackWorldPointWithGun(shotPoint)
        self.__prevSentShotPoint = shotPoint
        return

    def stopTrackingOnServer(self):
        self.__avatar.base.vehicle_stopTrackingWithGun(self.__turretYaw, self.__gunPitch)
        self.__prevSentShotPoint = None
        return

    def __stopTrackingWithPerfection(self):
        if self.__aimingPerfectionStartTime is None:
            angle = self.__calcAngleBetweenShotPointAndMarker()
            if angle is not None and angle < self.__AIMING_PERFECTION_RANGE:
                self.__aimingPerfectionStartTime = BigWorld.time()
            else:
                self.stopTrackingOnServer()
        elif BigWorld.time() - self.__aimingPerfectionStartTime > self.__AIMING_PERFECTION_DELAY:
            self.__aimingPerfectionStartTime = None
            self.stopTrackingOnServer()
        return

    def __updateShotPointOnServer(self, shotPoint):
        if shotPoint == self.__prevSentShotPoint:
            return
        else:
            if self.__avatar.vehicleTypeDescriptor.isHullAimingAvailable:
                if shotPoint is None:
                    self.__stopTrackingWithPerfection()
                else:
                    self.__aimingPerfectionStartTime = None
                    self.__trackPointOnServer(shotPoint)
            elif shotPoint is None:
                self.stopTrackingOnServer()
            else:
                self.__trackPointOnServer(shotPoint)
            return

    def __rotate(self, shotPoint, timeDiff):
        self.__turretRotationSpeed = 0.0
        targetPoint = shotPoint if shotPoint is not None else self.__prevSentShotPoint
        if targetPoint is None or self.__isLocked:
            self.__dispersionAngles = self.__avatar.getOwnVehicleShotDispersionAngle(0.0)
            return
        else:
            avatar = self.__avatar
            descr = avatar.getVehicleDescriptor()
            turretYawLimits = self.__getTurretYawLimits()
            maxTurretRotationSpeed = self.__maxTurretRotationSpeed
            prevTurretYaw = self.__turretYaw
            vehicleMatrix = self.getAvatarOwnVehicleStabilisedMatrix()
            shotTurretYaw, shotGunPitch = getShotAngles(descr, vehicleMatrix, (prevTurretYaw, self.__gunPitch), targetPoint)
            estimatedTurretYaw = self.getNextTurretYaw(prevTurretYaw, shotTurretYaw, maxTurretRotationSpeed * timeDiff, turretYawLimits)
            self.__turretYaw = turretYaw = self.__syncWithServerTurretYaw(estimatedTurretYaw)
            if maxTurretRotationSpeed != 0:
                self.estimatedTurretRotationTime = abs(turretYaw - shotTurretYaw) / maxTurretRotationSpeed
            else:
                self.estimatedTurretRotationTime = 0
            gunPitchLimits = calcPitchLimitsFromDesc(turretYaw, self.__getGunPitchLimits())
            self.__gunPitch = self.getNextGunPitch(self.__gunPitch, shotGunPitch, timeDiff, gunPitchLimits)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isUpdateGunOnTimeWarp:
                self.__updateTurretMatrix(turretYaw, 0.001)
                self.__updateGunMatrix(self.__gunPitch, 0.001)
            else:
                self.__updateTurretMatrix(turretYaw, self.__ROTATION_TICK_LENGTH)
                self.__updateGunMatrix(self.__gunPitch, self.__ROTATION_TICK_LENGTH)
            diff = abs(estimatedTurretYaw - prevTurretYaw)
            if diff > pi:
                diff = 2 * pi - diff
            self.__turretRotationSpeed = diff / timeDiff
            self.__dispersionAngles = avatar.getOwnVehicleShotDispersionAngle(self.__turretRotationSpeed)
            return

    def __updateGunMarker(self, forceRelaxTime=None):
        if self.__avatar.getVehicleAttached() is None:
            return
        else:
            shotPos, shotVec = self.getCurShotPosition()
            markerPos, markerDir, markerSize, idealMarkerSize, collData = self.__getGunMarkerPosition(shotPos, shotVec, self.__dispersionAngles)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording and not replayCtrl.isServerAim:
                replayCtrl.setGunMarkerParams(markerSize, markerPos, markerDir)
            if not self.__targetLastShotPoint:
                self.__lastShotPoint = markerPos
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isUpdateGunOnTimeWarp:
                self.__avatar.inputHandler.updateGunMarker(markerPos, markerDir, (markerSize, idealMarkerSize), 0.001, collData)
            else:
                relaxTime = self.__ROTATION_TICK_LENGTH if forceRelaxTime is None else forceRelaxTime
                self.__avatar.inputHandler.updateGunMarker(markerPos, markerDir, (markerSize, idealMarkerSize), relaxTime, collData)
            self.__markerInfo = (markerPos, markerDir, markerSize)
            return

    def getNextTurretYaw(self, curAngle, shotAngle, speedLimit, angleLimits):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            turretYaw = replayCtrl.getTurretYaw()
            if turretYaw > -100000:
                return turretYaw
        if math.fabs(curAngle - shotAngle) < VehicleGunRotator.__ANGLE_EPS:
            return curAngle
        else:
            shortWayDiff, longWayDiff = self.__getRotationWays(curAngle, shotAngle)
            if speedLimit < 1e-05:
                return curAngle
            closestLimit = self.__isOutOfLimits(curAngle, angleLimits)
            if closestLimit is not None:
                return closestLimit
            shortWayDiffLimited = self.__applyTurretYawLimits(shortWayDiff, curAngle, angleLimits)
            if shortWayDiffLimited == shortWayDiff:
                return self.__getTurretYawWithSpeedLimit(curAngle, shortWayDiff, speedLimit)
            longWayDiffLimited = self.__applyTurretYawLimits(longWayDiff, curAngle, angleLimits)
            return self.__getTurretYawWithSpeedLimit(curAngle, longWayDiff, speedLimit) if longWayDiffLimited == longWayDiff else self.__getTurretYawWithSpeedLimit(curAngle, shortWayDiffLimited, speedLimit)

    def __syncWithServerTurretYaw(self, turretYaw):
        vehicle = self.__avatar.vehicle
        if vehicle is not None:
            serverTurretYaw, _ = vehicle.getServerGunAngles()
            diff = serverTurretYaw - turretYaw
            absDeviation = min(diff % (2.0 * pi), -diff % (2.0 * pi))
            allowedDeviation = self.__TURRET_YAW_ALLOWED_ERROR_CONST
            allowedDeviation += self.__TURRET_YAW_ALLOWED_ERROR_FACTOR * self.__maxTurretRotationSpeed
            if absDeviation > allowedDeviation:
                latency = BigWorld.LatencyInfo().value[3]
                errorDueLatency = latency * self.__maxTurretRotationSpeed
                if absDeviation > allowedDeviation + errorDueLatency:
                    return serverTurretYaw
        return turretYaw

    def __getRotationWays(self, curAngle, shotAngle):
        shotDiff1 = shotAngle - curAngle
        if shotDiff1 < 0.0:
            shotDiff2 = 2.0 * pi + shotDiff1
        else:
            shotDiff2 = -2.0 * pi + shotDiff1
        return (shotDiff1, shotDiff2) if abs(shotDiff1) <= pi else (shotDiff2, shotDiff1)

    def __isOutOfLimits(self, angle, limits):
        if limits is None:
            return
        elif abs(limits[1] - angle) < 1e-05 or abs(limits[0] - angle) < 1e-05:
            return
        dpi = 2 * pi
        minDiff = fmod(limits[0] - angle + dpi, dpi)
        maxDiff = fmod(limits[1] - angle + dpi, dpi)
        if minDiff > maxDiff:
            return
        else:
            return limits[0] if minDiff < dpi - maxDiff else limits[1]

    def __applyTurretYawLimits(self, diff, angle, limits):
        if limits is None:
            return diff
        else:
            dpi = 2 * pi
            if diff > 0:
                if abs(limits[1] - angle) < 1e-05:
                    return 0
                maxDiff = fmod(limits[1] - angle + dpi, dpi)
                return min(maxDiff, diff)
            if abs(limits[0] - angle) < 1e-05:
                return 0
            maxDiff = fmod(limits[0] - angle - dpi, dpi)
            return max(maxDiff, diff)
            return

    def __getTurretYawWithSpeedLimit(self, angle, diff, limit):
        dpi = 2 * pi
        return fmod(pi + angle + min(diff, limit), dpi) - pi if diff > 0 else fmod(-pi + angle + max(diff, -limit), dpi) + pi

    def getNextGunPitch(self, curAngle, shotAngle, timeDiff, angleLimits):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            gunPitch = replayCtrl.getGunPitch()
            if gunPitch > -100000:
                return gunPitch
        if self.__maxGunRotationSpeed == 0.0:
            shotAngle = curAngle
            shotDiff = 0.0
            descr = self.__avatar.getVehicleDescriptor()
            speedLimit = descr.gun.rotationSpeed * timeDiff
        else:
            if math.fabs(curAngle - shotAngle) < VehicleGunRotator.__ANGLE_EPS:
                if angleLimits is not None:
                    return mathUtils.clamp(angleLimits[0], angleLimits[1], shotAngle)
                return shotAngle
            shotDiff = shotAngle - curAngle
            speedLimit = self.__maxGunRotationSpeed * timeDiff
        if angleLimits is not None:
            if shotAngle < angleLimits[0]:
                shotDiff = angleLimits[0] - curAngle
            elif shotAngle > angleLimits[1]:
                shotDiff = angleLimits[1] - curAngle
        staticPitch = self.__getGunStaticPitch()
        if staticPitch is not None and shotDiff * (curAngle - staticPitch) < 0.0:
            speedLimit *= 2.0
        if staticPitch is not None and self.estimatedTurretRotationTime > 0.0:
            idealYawSpeed = abs(shotDiff) / self.estimatedTurretRotationTime
            speedLimit = min(speedLimit, idealYawSpeed * timeDiff)
        return curAngle + min(shotDiff, speedLimit) if shotDiff > 0.0 else curAngle + max(shotDiff, -speedLimit)

    def __getShotPosition(self, turretYaw, gunPitch):
        descr = self.__avatar.getVehicleDescriptor()
        turretOffs = descr.hull.turretPositions[0] + descr.chassis.hullPosition
        gunOffs = descr.turret.gunPosition
        shotSpeed = descr.shot.speed
        turretWorldMatrix = Math.Matrix()
        turretWorldMatrix.setRotateY(turretYaw)
        turretWorldMatrix.translation = turretOffs
        turretWorldMatrix.postMultiply(Math.Matrix(self.getAvatarOwnVehicleStabilisedMatrix()))
        position = turretWorldMatrix.applyPoint(gunOffs)
        gunWorldMatrix = Math.Matrix()
        gunWorldMatrix.setRotateX(gunPitch)
        gunWorldMatrix.postMultiply(turretWorldMatrix)
        vector = gunWorldMatrix.applyVector(Math.Vector3(0, 0, shotSpeed))
        return (position, vector)

    def getAttachedVehicleID(self):
        return self.__avatar.playerVehicleID

    def __getGunMarkerPosition(self, shotPos, shotVec, dispersionAngles):
        shotDescr = self.__avatar.getVehicleDescriptor().shot
        gravity = Math.Vector3(0.0, -shotDescr.gravity, 0.0)
        maxDist = shotDescr.maxDistance
        testVehicleID = self.getAttachedVehicleID()
        collideVehiclesAndStaticScene = ProjectileMover.collideDynamicAndStatic
        collideWithSpaceBB = self.__avatar.arena.collideWithSpaceBB
        prevPos = shotPos
        prevVelocity = shotVec
        dt = 0.0
        maxDistCheckFlag = False
        while True:
            dt += SERVER_TICK_LENGTH
            checkPoints = computeProjectileTrajectory(prevPos, prevVelocity, gravity, SERVER_TICK_LENGTH, SHELL_TRAJECTORY_EPSILON_CLIENT)
            prevCheckPoint = prevPos
            bBreak = False
            for curCheckPoint in checkPoints:
                testRes = collideVehiclesAndStaticScene(prevCheckPoint, curCheckPoint, (testVehicleID,))
                if testRes is not None:
                    collData = testRes[1]
                    if collData is not None and not collData.isVehicle():
                        collData = None
                    direction = testRes[0] - prevCheckPoint
                    endPos = testRes[0]
                    bBreak = True
                    break
                collisionResult, intersection = collideWithSpaceBB(prevCheckPoint, curCheckPoint)
                if collisionResult is CollisionResult.INTERSECTION:
                    collData = None
                    maxDistCheckFlag = True
                    direction = intersection - prevCheckPoint
                    endPos = intersection
                    bBreak = True
                    break
                elif collisionResult is CollisionResult.OUTSIDE:
                    collData = None
                    maxDistCheckFlag = True
                    direction = prevVelocity
                    endPos = prevPos + prevVelocity
                    bBreak = True
                prevCheckPoint = curCheckPoint

            if bBreak:
                break
            prevPos = shotPos + shotVec.scale(dt) + gravity.scale(dt * dt * 0.5)
            prevVelocity = shotVec + gravity.scale(dt)

        direction.normalise()
        distance = (endPos - shotPos).length
        markerDiameter = 2.0 * distance * dispersionAngles[0]
        idealMarkerDiameter = 2.0 * distance * dispersionAngles[1]
        if maxDistCheckFlag:
            if endPos.distTo(shotPos) >= maxDist:
                direction = endPos - shotPos
                direction.normalise()
                endPos = shotPos + direction.scale(maxDist)
                distance = maxDist
                markerDiameter = 2.0 * distance * dispersionAngles[0]
                idealMarkerDiameter = 2.0 * distance * dispersionAngles[1]
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            markerDiameter, endPos, direction = replayCtrl.getGunMarkerParams(endPos, direction)
        return (endPos,
         direction,
         markerDiameter,
         idealMarkerDiameter,
         collData)

    def __updateTurretMatrix(self, yaw, time):
        replayYaw = yaw
        staticTurretYaw = self.__getTurretStaticYaw()
        if staticTurretYaw is not None:
            yaw = staticTurretYaw
        m = Math.Matrix()
        m.setRotateY(yaw)
        self.__turretMatrixAnimator.update(m, time)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setTurretYaw(replayYaw)
        return

    def __updateGunMatrix(self, pitch, time):
        replayPitch = pitch
        staticPitch = self.__getGunStaticPitch()
        if staticPitch is not None:
            pitch = staticPitch
        m = Math.Matrix()
        m.setRotateX(pitch)
        self.__gunMatrixAnimator.update(m, time)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setGunPitch(replayPitch)
        return

    def getAvatarOwnVehicleStabilisedMatrix(self):
        avatar = self.__avatar
        playerVehicle = avatar.getVehicleAttached()
        vehicleMatrix = Math.Matrix(avatar.getOwnVehicleStabilisedMatrix())
        if self.__getTurretStaticYaw() is not None and playerVehicle is not None:
            vehicleMatrix = Math.Matrix(playerVehicle.filter.interpolateStabilisedMatrix(BigWorld.time()))
        return vehicleMatrix

    def __getGunPitchLimits(self):
        gunPitchLimits = self.__avatar.vehicleTypeDescriptor.gun.pitchLimits
        staticPitch = self.__getGunStaticPitch()
        if staticPitch is None:
            return gunPitchLimits
        else:
            playerVehicle = self.__avatar.getVehicleAttached()
            deviceStates = self.__avatar.deviceStates
            useGunStaticPitch = False
            useGunStaticPitch |= deviceStates.get('engine') == 'destroyed'
            useGunStaticPitch |= self.__avatar.isVehicleOverturned
            if playerVehicle is not None:
                useGunStaticPitch |= playerVehicle.siegeState in VEHICLE_SIEGE_STATE.SWITCHING
            if useGunStaticPitch:
                gunPitchLimits = {'minPitch': ((0.0, staticPitch), (math.pi * 2.0, staticPitch)),
                 'maxPitch': ((0.0, staticPitch), (math.pi * 2.0, staticPitch)),
                 'absolute': (staticPitch, staticPitch)}
            return gunPitchLimits

    def __getGunStaticPitch(self):
        return self.__avatar.vehicleTypeDescriptor.gun.staticPitch

    def __getTurretYawLimits(self):
        turretYawLimits = self.__avatar.vehicleTypeDescriptor.gun.turretYawLimits
        staticYaw = self.__getTurretStaticYaw()
        if staticYaw is None:
            return turretYawLimits
        else:
            playerVehicle = self.__avatar.getVehicleAttached()
            deviceStates = self.__avatar.deviceStates
            useStaticTurretYaw = False
            useStaticTurretYaw |= deviceStates.get('engine') == 'destroyed'
            useStaticTurretYaw |= deviceStates.get('leftTrack') == 'destroyed'
            useStaticTurretYaw |= deviceStates.get('rightTrack') == 'destroyed'
            useStaticTurretYaw |= self.__avatar.isVehicleOverturned
            if playerVehicle is not None:
                useStaticTurretYaw |= playerVehicle.hasMovingFlags
                useStaticTurretYaw |= playerVehicle.siegeState in VEHICLE_SIEGE_STATE.SWITCHING
            if useStaticTurretYaw:
                turretYawLimits = (staticYaw, staticYaw)
            return turretYawLimits

    def __getTurretStaticYaw(self):
        return self.__avatar.vehicleTypeDescriptor.gun.staticTurretYaw


class _MatrixAnimator(object):

    def __init__(self, avatar):
        m = Math.Matrix()
        m.setIdentity()
        self.__animMat = Math.MatrixAnimation()
        self.__animMat.keyframes = ((0.0, m),)

    def destroy(self, avatar):
        self.__animMat = None
        return

    matrix = property(lambda self: self.__animMat)

    def update(self, matrix, time):
        self.__animMat.keyframes = ((0.0, Math.Matrix(self.__animMat)), (time, matrix))
        self.__animMat.time = 0.0


class _PlayerTurretRotationSoundEffectWWISE(CallbackDelayer):
    __slots__ = ('__rtpcTurretSpeed', '__rtpcTurretAngle', '__rtpcTurretPitch', '__rtpcTurretPitchSpeed', '__rtpcTurretDamaged', '__updatePeriod', '__soundObject', '__oldPitch', '__oldTime')

    def __init__(self, updatePeriod=0.1):
        CallbackDelayer.__init__(self)
        self.__rtpcTurretSpeed = WWISE.WW_getRTPCValue('RTPC_ext_turret_speed')
        self.__rtpcTurretAngle = WWISE.WW_getRTPCValue('RTPC_ext_turret_angle')
        self.__rtpcTurretPitch = WWISE.WW_getRTPCValue('RTPC_ext_turret_pitch')
        self.__rtpcTurretPitchSpeed = WWISE.WW_getRTPCValue('RTPC_ext_turret_pitch_speed')
        self.__rtpcTurretDamaged = WWISE.WW_getRTPCValue('RTPC_ext_turret_damaged')
        self.__updatePeriod = updatePeriod
        self.__soundObject = None
        self.__oldPitch = 0
        self.__oldTime = 0
        self.__init_sound()
        return

    def __init_sound(self):
        if BigWorld.player() is not None and BigWorld.player().getVehicleAttached() is not None:
            compoundModel = BigWorld.player().getVehicleAttached().appearance.compoundModel
            self.connectSoundToMatrix(compoundModel.node(TankPartNames.TURRET))
        else:
            self.connectSoundToMatrix(mathUtils.createIdentityMatrix())
        self.delayCallback(self.__updatePeriod, self.__update)
        return

    def connectSoundToMatrix(self, matrixProvider):
        if self.__soundObject is not None:
            self.__soundObject.stopAll()
            self.__soundObject = None
        soundEvent = BigWorld.player().vehicleTypeDescriptor.turret.turretRotatorSoundManual
        self.__soundObject = SoundGroups.g_instance.WWgetSoundObject('player_turret', matrixProvider)
        if self.__soundObject is None:
            return
        else:
            self.__rtpcTurretSpeed.set(self.__soundObject, 0.0)
            self.__soundObject.setRTPC('RTPC_ext_turret_weight', BigWorld.player().vehicleTypeDescriptor.turret.weight / 1000.0)
            self.__soundObject.play(soundEvent)
            return

    def lockSoundMatrix(self):
        if self.__soundObject is not None:
            provider = self.__soundObject.matrixProvider
            if provider is not None:
                self.__soundObject.matrixProvider = Math.Matrix(provider)
        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        if self.__soundObject is not None:
            self.__soundObject.stopAll()
            self.__soundObject = None
        self.__stateTable = None
        return

    def __update(self):
        if self.__soundObject is None:
            return
        elif not hasattr(BigWorld.player(), 'gunRotator'):
            return
        else:
            player = BigWorld.player()
            gunRotator = player.gunRotator
            speedValue = 0.0
            if gunRotator.maxturretRotationSpeed is not None and gunRotator.maxturretRotationSpeed > 0:
                speedValue = gunRotator.turretRotationSpeed / gunRotator.maxturretRotationSpeed
            self.__rtpcTurretSpeed.set(self.__soundObject, speedValue)
            vehicleTypeDescriptor = player.vehicleTypeDescriptor
            turretYaw = gunRotator.turretYaw
            desiredShotPoint = gunRotator.predictLockedTargetShotPoint()
            if desiredShotPoint is None:
                desiredShotPoint = player.inputHandler.getDesiredShotPoint()
            if desiredShotPoint is None:
                desiredShotPoint = gunRotator.markerInfo[0]
            cameraTurretYaw, _ = AimingSystems.getTurretYawGunPitch(vehicleTypeDescriptor, player.getOwnVehicleStabilisedMatrix(), desiredShotPoint, True)
            turretPitch = player.gunRotator.gunPitch
            angleDiff = abs(turretYaw - cameraTurretYaw)
            if angleDiff > math.pi:
                angleDiff = 2 * math.pi - angleDiff
            self.__rtpcTurretAngle.set(self.__soundObject, angleDiff)
            self.__rtpcTurretPitch.set(self.__soundObject, turretPitch)
            self.__rtpcTurretPitchSpeed.set(self.__soundObject, abs(self.__oldPitch - turretPitch) / (BigWorld.time() - self.__oldTime))
            self.__rtpcTurretDamaged.set(self.__soundObject, 0 if player.deviceStates.get('turretRotator', None) is None else 1)
            self.__oldPitch = turretPitch
            self.__oldTime = BigWorld.time()
            return self.__updatePeriod
