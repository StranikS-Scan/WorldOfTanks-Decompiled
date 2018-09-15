# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleGunRotator.py
import BigWorld
import Math
import weakref
import math
from AvatarInputHandler import AimingSystems, mathUtils
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from constants import SERVER_TICK_LENGTH, SHELL_TRAJECTORY_EPSILON_CLIENT, AIMING_MODE, VEHICLE_SIEGE_STATE
import ProjectileMover
from projectile_trajectory import getShotAngles
from math import pi, fmod
from projectile_trajectory import computeProjectileTrajectory
import BattleReplay
from gun_rotation_shared import calcPitchLimitsFromDesc, getLocalAimPoint
import SoundGroups
from skeletons.account_helpers.settings_core import ISettingsCore
from vehicle_systems.tankStructure import TankPartNames
from helpers import gEffectsDisabled
from debug_utils import LOG_DEBUG
_ENABLE_TURRET_ROTATOR_SOUND = True
_ENABLE_RELATIVE_SHOT_POINT = True

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
        self.__prevSentShotPoints = [None]
        self.__targetLastShotPoint = False
        self.__lastShotPoint = Math.Vector3(0, 0, 0)
        self.__shotPointSourceFunctor = self.__shotPointSourceFunctor_Default
        self.__maxTurretRotationSpeedList = [None]
        self.__maxGunRotationSpeedList = [None]
        self.__turretYawList = [0.0]
        self.__gunPitchList = [0.0]
        self.__turretRotationSpeedList = [0.0]
        self.__turretDispersionAnglesList = [[0.0, 0.0]]
        self.__turretMarkerInfoList = [(Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 1.0, 0.0), 1.0)]
        self.__clientMode = True
        self.__showServerMarker = False
        self.__time = None
        self.__timerID = None
        self.__turretAnimatorList = [_MatrixAnimator(self.__avatar)]
        self.__gunAnimatorList = [_MatrixAnimator(self.__avatar)]
        self.__turretLockedList = [False]
        self.__aimingPerfectionStartTimes = [None]
        self.__turretCount = len(avatar.getVehicleDescriptor().turrets)
        for i in range(1, self.__turretCount):
            self.__prevSentShotPoints.append(None)
            self.__maxTurretRotationSpeedList.append(None)
            self.__maxGunRotationSpeedList.append(None)
            self.__turretYawList.append(0.0)
            self.__gunPitchList.append(0.0)
            self.__turretRotationSpeedList.append(0.0)
            self.__turretDispersionAnglesList.append([0.0, 0.0])
            self.__turretMarkerInfoList.append((Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 1.0, 0.0), 1.0))
            self.__turretAnimatorList.append(_MatrixAnimator(self.__avatar))
            self.__gunAnimatorList.append(_MatrixAnimator(self.__avatar))
            self.__turretLockedList.append(False)
            self.__aimingPerfectionStartTimes.append(None)

        self.estimatedTurretRotationTime = 0
        if not gEffectsDisabled():
            self.__turretRotationSoundEffect = _PlayerTurretRotationSoundEffectWWISE()
        else:
            self.__turretRotationSoundEffect = None
        return

    def destroy(self):
        self.stop()
        for i in xrange(self.__turretCount):
            self.__turretAnimatorList[i].destroy(self.__avatar)
            self.__gunAnimatorList[i].destroy(self.__avatar)

        self.__avatar = None
        self.__shotPointSourceFunctor = None
        if self.__turretRotationSoundEffect is not None:
            self.__turretRotationSoundEffect.destroy()
            self.__turretRotationSoundEffect = None
        return

    def start(self):
        if self.__isStarted:
            return
        elif None in self.__maxTurretRotationSpeedList:
            return
        elif not self.__avatar.isOnArena:
            return
        else:
            self.settingsCore.onSettingsChanged += self.applySettings
            self.showServerMarker = self.settingsCore.getSetting('useServerAim')
            self.__isStarted = True
            for i in range(self.__turretCount):
                self.__updateGunMarker(i)

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
                self.__avatar.inputHandler.showGunMarker2(False)
            return

    def applySettings(self, diff):
        if 'useServerAim' in diff:
            self.showServerMarker = diff['useServerAim']

    def lock(self, isLocked, turretIndex):
        self.__turretLockedList[turretIndex] = isLocked

    def isLocked(self, turretIndex):
        return self.__turretLockedList[turretIndex]

    def reset(self):
        for i in range(self.__turretCount):
            self.__turretYawList[i] = self.__gunPitchList[i] = 0.0
            self.__updateTurretMatrix(0.0, i, 0.0)
            self.__updateGunMatrix(0.0, i, 0.0)
            self.__turretLockedList[i] = False

    def update(self, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed, turretIndex):
        if self.__timerID is None or maxTurretRotationSpeed < self.__maxTurretRotationSpeedList[turretIndex]:
            self.__turretYawList[turretIndex], self.__gunPitchList[turretIndex] = turretYaw, gunPitch
            self.__updateTurretMatrix(turretYaw, turretIndex, 0.0)
            self.__updateGunMatrix(gunPitch, turretIndex, 0.0)
        self.__maxTurretRotationSpeedList[turretIndex] = maxTurretRotationSpeed
        self.__maxGunRotationSpeedList[turretIndex] = maxGunRotationSpeed
        self.__turretRotationSpeedList[turretIndex] = 0.0
        self.__turretDispersionAnglesList[turretIndex] = self.__avatar.getOwnVehicleShotDispersionAngle(0.0, turretIndex)
        self.start()
        return

    def forceGunParams(self, turretYaw, gunPitch, dispAngle, turretIndex=0):
        self.__turretYawList[turretIndex] = turretYaw
        self.__gunPitchList[turretIndex] = gunPitch
        self.__turretDispersionAnglesList[turretIndex] = [dispAngle, dispAngle]
        self.__updateGunMarker(turretIndex, 0.001)

    def setShotPosition(self, vehicleID, shotPos, shotVec, dispersionAngle, turretIndex, forceValueRefresh=False):
        if self.__clientMode and not self.__showServerMarker and not forceValueRefresh:
            return
        elif turretIndex > 0:
            self.__turretDispersionAnglesList[turretIndex][0] = dispersionAngle
            return
        else:
            if BigWorld.player().isObserver():
                self.__avatar.observedVehicleData[vehicleID].dispAngle = dispersionAngle
            elif self.__clientMode and not self.__showServerMarker:
                return
            self.__turretDispersionAnglesList[turretIndex][0] = dispersionAngle
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
            markerPos, markerDir, markerSize, idealMarkerSize, collData = self.__getGunMarkerPosition(shotPos, shotVec, self.__turretDispersionAnglesList[turretIndex], turretIndex)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setGunMarkerParams(markerSize, markerPos, markerDir, turretIndex)
            if self.__clientMode and self.__showServerMarker:
                self.__avatar.inputHandler.updateGunMarker2(markerPos, markerDir, (markerSize, idealMarkerSize), SERVER_TICK_LENGTH, collData)
            if not self.__clientMode or forceValueRefresh:
                self.__lastShotPoint = markerPos
                self.__avatar.inputHandler.updateGunMarker(markerPos, markerDir, (markerSize, idealMarkerSize), SERVER_TICK_LENGTH, collData)
                descr = self.__avatar.getVehicleDescriptor()
                self.__turretYawList[turretIndex], self.__gunPitchList[turretIndex] = getShotAngles(self.__avatar.getVehicleDescriptor(), self.__avatar.getOwnVehicleStabilisedMatrix(), (self.__turretYawList[turretIndex], self.__gunPitchList[turretIndex]), markerPos, True, turretIndex)
                turretYawLimits = self.__getTurretYawLimits(turretIndex)
                closestLimit = self.__isOutOfLimits(self.__turretYawList[turretIndex], turretYawLimits)
                if closestLimit is not None:
                    self.__turretYawList[turretIndex] = closestLimit
                self.__updateTurretMatrix(self.__turretYawList[turretIndex], turretIndex, SERVER_TICK_LENGTH)
                self.__updateGunMatrix(self.__gunPitchList[turretIndex], turretIndex, SERVER_TICK_LENGTH)
                self.__turretMarkerInfoList[turretIndex] = (markerPos, markerDir, markerSize)
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

    def getShotParams(self, targetPoint, ignoreYawLimits=False, turretIndex=0):
        descr = self.__avatar.getVehicleAttached().typeDescriptor
        shotTurretYaw, shotGunPitch = getShotAngles(descr, self.__avatar.getOwnVehicleStabilisedMatrix(), (self.__turretYawList[turretIndex], self.__gunPitchList[turretIndex]), targetPoint, True, turretIndex)
        gunPitchLimits = calcPitchLimitsFromDesc(shotTurretYaw, self.__getGunPitchLimits(turretIndex))
        closestLimit = self.__isOutOfLimits(shotGunPitch, gunPitchLimits)
        if closestLimit is not None:
            shotGunPitch = closestLimit
        turretYawLimits = self.__getTurretYawLimits(turretIndex)
        if not ignoreYawLimits:
            closestLimit = self.__isOutOfLimits(shotTurretYaw, turretYawLimits)
            if closestLimit is not None:
                shotTurretYaw = closestLimit
        pos, vel = self.__getShotPosition(shotTurretYaw, shotGunPitch, turretIndex)
        grav = Math.Vector3(0.0, -descr.turrets[turretIndex].shot.gravity, 0.0)
        return (pos, vel, grav)

    def getCurShotPosition(self, turretIndex=0):
        return self.__getShotPosition(self.__turretYawList[turretIndex], self.__gunPitchList[turretIndex], turretIndex)

    def isTurretCloseToShotPoint(self, turretIndex, threshold):
        descr = self.__avatar.getVehicleAttached().typeDescriptor
        matrix = self.__avatar.getOwnVehicleStabilisedMatrix()
        shotYaw, _ = getShotAngles(descr, matrix, (0, 0), self.__prevSentShotPoints[turretIndex], False, turretIndex)
        return abs(self.__turretYawList[turretIndex] - shotYaw) <= threshold

    def __set_clientMode(self, value):
        if self.__clientMode == value:
            return
        self.__clientMode = value
        if not self.__isStarted:
            return
        if self.__clientMode:
            self.__time = BigWorld.time()
        if self.__showServerMarker:
            self.__avatar.inputHandler.showGunMarker2(self.__clientMode)

    clientMode = property(lambda self: self.__clientMode, __set_clientMode)

    def __set_showServerMarker(self, value):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            return
        if self.__avatar.vehicleTypeDescriptor.isMultiTurret:
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

    def getTurretMatrix(self, turretIndex):
        return self.__turretAnimatorList[turretIndex].matrix

    def getGunMatrix(self, turretIndex):
        return self.__gunAnimatorList[turretIndex].matrix

    def getTurretRotationSpeed(self, turretIndex):
        return self.__turretRotationSpeedList[turretIndex]

    def getMaxTurretRotationSpeed(self, turretIndex):
        return self.__maxTurretRotationSpeedList[turretIndex]

    def getDispersionAngle(self, turretIndex):
        return self.__turretDispersionAnglesList[turretIndex][0]

    def getMarkerInfo(self, turretIndex):
        return self.__turretMarkerInfoList[turretIndex]

    def getTurretYaw(self, turretIndex):
        return self.__turretYawList[turretIndex]

    def getGunPitch(self, turretIndex):
        return self.__gunPitchList[turretIndex]

    turretMatrix = property(lambda self: self.__turretAnimatorList[0].matrix)
    gunMatrix = property(lambda self: self.__gunAnimatorList[0].matrix)
    turretRotationSpeed = property(lambda self: self.__turretRotationSpeedList[0])
    dispersionAngle = property(lambda self: self.__turretDispersionAnglesList[0][0])
    markerInfo = property(lambda self: self.__turretMarkerInfoList[0])
    turretYaw = property(lambda self: self.__turretYawList[0])
    gunPitch = property(lambda self: self.__gunPitchList[0])

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
                shotPointFunctorResult = self.__shotPointSourceFunctor()
                shotPoint = shotPointFunctorResult if predictedLockShotPoint is None else predictedLockShotPoint
            if shotPoint is None and self.__targetLastShotPoint:
                shotPoint = self.__lastShotPoint
            if replayCtrl.isRecording:
                if shotPoint is not None:
                    replayCtrl.setGunRotatorTargetPoint(shotPoint)
            secondaryShotPoint = shotPoint
            if BigWorld.player().inputHandler.getAimingMode(AIMING_MODE.AIM_SECONDARY_ONLY) or self.__targetLastShotPoint:
                secondaryShotPoint = self.__avatar.inputHandler.getDesiredShotPoint(ignoreCurrentAimingMode=True)
            shotPoints = [shotPoint]
            for i in range(1, self.__turretCount):
                shotPoints.append(secondaryShotPoint)

            timeDiff = self.__getTimeDiff()
            if timeDiff is None:
                return
            self.__time = BigWorld.time()
            for i in range(self.__turretCount):
                self.__rotate(shotPoints[i], i, timeDiff)
                self.__updateGunMarker(i)
                self.__updateShotPointOnServer(shotPoints[i], i, timeDiff)

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

    def __calcAngleBetweenShotPointAndMarker(self, turretIndex):
        if self.__prevSentShotPoints[turretIndex] is None:
            return
        else:
            shotStartPos, _ = self.getCurShotPosition(turretIndex)
            markerDelta = self.__turretMarkerInfoList[turretIndex][0] - shotStartPos
            shotPointDelta = self.__prevSentShotPoints[turretIndex] - shotStartPos
            sine = (markerDelta * shotPointDelta).length
            cosine = markerDelta.dot(shotPointDelta)
            return abs(math.atan2(sine, cosine))

    def __trackPointOnServer(self, shotPoint, turretIndex):
        avatar = self.__avatar
        vehicle = BigWorld.entity(avatar.playerVehicleID)
        if vehicle is not None and vehicle is avatar.vehicle and _ENABLE_RELATIVE_SHOT_POINT:
            stabilisedVehPos = Math.Matrix(avatar.getOwnVehicleStabilisedMatrix()).translation
            vehicle.cell.trackRelativePointWithGun(shotPoint - stabilisedVehPos, turretIndex)
        else:
            vehicle.cell.trackWorldPointWithGun(shotPoint, turretIndex)
        self.__prevSentShotPoints[turretIndex] = shotPoint
        return

    def __stopTrackingOnServer(self, turretIndex):
        self.__avatar.base.vehicle_stopTrackingWithGun(self.__turretYawList[turretIndex], self.__gunPitchList[turretIndex], turretIndex)
        self.__prevSentShotPoints[turretIndex] = None
        return

    def __stopTrackingWithPerfection(self, turretIndex):
        if self.__aimingPerfectionStartTimes[turretIndex] is None:
            angle = self.__calcAngleBetweenShotPointAndMarker(turretIndex)
            if angle is not None and angle < self.__AIMING_PERFECTION_RANGE:
                self.__aimingPerfectionStartTimes[turretIndex] = BigWorld.time()
            else:
                self.__stopTrackingOnServer(turretIndex)
        elif BigWorld.time() - self.__aimingPerfectionStartTimes[turretIndex] > self.__AIMING_PERFECTION_DELAY:
            self.__aimingPerfectionStartTimes[turretIndex] = None
            self.__stopTrackingOnServer(turretIndex)
        return

    def __updateShotPointOnServer(self, shotPoint, turretIndex, timeDiff):
        if shotPoint is not None and shotPoint == self.__prevSentShotPoints[turretIndex]:
            return
        else:
            if self.__avatar.vehicleTypeDescriptor.isHullAimingAvailable:
                if shotPoint is None:
                    self.__stopTrackingWithPerfection(turretIndex)
                else:
                    self.__aimingPerfectionStartTimes[turretIndex] = None
                    self.__trackPointOnServer(shotPoint, turretIndex)
            elif shotPoint is None:
                self.__stopTrackingOnServer(turretIndex)
            else:
                self.__trackPointOnServer(shotPoint, turretIndex)
            return

    def __rotate(self, shotPoint, turretIndex, timeDiff):
        self.__turretRotationSpeedList[turretIndex] = 0.0
        targetPoint = shotPoint if shotPoint is not None else self.__prevSentShotPoints[turretIndex]
        if targetPoint is None or self.__turretLockedList[turretIndex]:
            self.__turretDispersionAnglesList[turretIndex] = self.__avatar.getOwnVehicleShotDispersionAngle(0.0, turretIndex)
            return
        else:
            avatar = self.__avatar
            descr = avatar.getVehicleDescriptor()
            turretYawLimits = self.__getTurretYawLimits(turretIndex)
            maxTurretRotationSpeed = self.__maxTurretRotationSpeedList[turretIndex]
            prevTurretYaw = self.__turretYawList[turretIndex]
            prevGunPitch = self.__gunPitchList[turretIndex]
            vehicleMatrix = self.getAvatarOwnVehicleStabilisedMatrix(turretIndex)
            shotTurretYaw, shotGunPitch = getShotAngles(descr, vehicleMatrix, (prevTurretYaw, prevGunPitch), targetPoint, True, turretIndex)
            estimatedTurretYaw = self.getNextTurretYaw(prevTurretYaw, shotTurretYaw, maxTurretRotationSpeed * timeDiff, turretYawLimits, turretIndex)
            self.__turretYawList[turretIndex] = turretYaw = self.__syncWithServerTurretYaw(estimatedTurretYaw, turretIndex)
            if maxTurretRotationSpeed != 0:
                self.estimatedTurretRotationTime = abs(turretYaw - shotTurretYaw) / maxTurretRotationSpeed
            else:
                self.estimatedTurretRotationTime = 0
            gunPitchLimits = calcPitchLimitsFromDesc(turretYaw, self.__getGunPitchLimits(turretIndex))
            self.__gunPitchList[turretIndex] = gunPitch = self.getNextGunPitch(prevGunPitch, shotGunPitch, timeDiff, gunPitchLimits, turretIndex)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isUpdateGunOnTimeWarp:
                self.__updateTurretMatrix(turretYaw, turretIndex, 0.001)
                self.__updateGunMatrix(gunPitch, turretIndex, 0.001)
            else:
                self.__updateTurretMatrix(turretYaw, turretIndex, self.__ROTATION_TICK_LENGTH)
                self.__updateGunMatrix(gunPitch, turretIndex, self.__ROTATION_TICK_LENGTH)
            diff = abs(estimatedTurretYaw - prevTurretYaw)
            if diff > pi:
                diff = 2 * pi - diff
            self.__turretRotationSpeedList[turretIndex] = diff / timeDiff
            self.__turretDispersionAnglesList[turretIndex] = avatar.getOwnVehicleShotDispersionAngle(self.__turretRotationSpeedList[turretIndex], turretIndex)
            return

    def __updateGunMarker(self, turretIndex, forceRelaxTime=None):
        if self.__avatar.getVehicleAttached() is None:
            return
        else:
            shotPos, shotVec = self.getCurShotPosition(turretIndex)
            markerPos, markerDir, markerSize, idealMarkerSize, collData = self.__getGunMarkerPosition(shotPos, shotVec, self.__turretDispersionAnglesList[turretIndex], turretIndex)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording and not replayCtrl.isServerAim:
                replayCtrl.setGunMarkerParams(markerSize, markerPos, markerDir, turretIndex)
            if turretIndex == 0 and not self.__targetLastShotPoint:
                self.__lastShotPoint = markerPos
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isUpdateGunOnTimeWarp:
                self.__avatar.inputHandler.updateGunMarker(markerPos, markerDir, (markerSize, idealMarkerSize), 0.001, collData, turretIndex)
            else:
                relaxTime = self.__ROTATION_TICK_LENGTH if forceRelaxTime is None else forceRelaxTime
                self.__avatar.inputHandler.updateGunMarker(markerPos, markerDir, (markerSize, idealMarkerSize), relaxTime, collData, turretIndex)
            self.__turretMarkerInfoList[turretIndex] = (markerPos, markerDir, markerSize)
            return

    def getNextTurretYaw(self, curAngle, shotAngle, speedLimit, angleLimits, turretIndex):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            turretYaw = replayCtrl.getTurretYaw(turretIndex)
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
            if longWayDiffLimited == longWayDiff:
                return self.__getTurretYawWithSpeedLimit(curAngle, longWayDiff, speedLimit)
            if turretIndex > 0:
                closestLimitToShot = self.__isOutOfLimits(shotAngle, angleLimits)
                if closestLimitToShot is not None:
                    shortAngle = curAngle + shortWayDiffLimited
                    dpi = 2 * pi
                    if shortWayDiffLimited > 0:
                        shortAngle = fmod(pi + shortAngle, dpi) - pi
                    else:
                        shortAngle = fmod(-pi + shortAngle, dpi) + pi
                    angleEqualsLimit = math.fabs(shortAngle - closestLimitToShot) < VehicleGunRotator.__ANGLE_EPS
                    wayToMove = shortWayDiffLimited if angleEqualsLimit else longWayDiffLimited
                    return self.__getTurretYawWithSpeedLimit(curAngle, wayToMove, speedLimit)
            return self.__getTurretYawWithSpeedLimit(curAngle, shortWayDiffLimited, speedLimit)

    def __syncWithServerTurretYaw(self, turretYaw, turretIndex):
        """Applies correction to given turretYaw, to keep it in sync with the server (WOTD-14553).
        :return: corrected turretYaw (unchanged in most cases)
        """
        vehicle = self.__avatar.vehicle
        if vehicle is not None:
            serverTurretYaw, _ = vehicle.getServerGunAngles(turretIndex)
            diff = serverTurretYaw - turretYaw
            absDeviation = min(diff % (2.0 * pi), -diff % (2.0 * pi))
            allowedDeviation = self.__TURRET_YAW_ALLOWED_ERROR_CONST
            allowedDeviation += self.__TURRET_YAW_ALLOWED_ERROR_FACTOR * self.__maxTurretRotationSpeedList[turretIndex]
            if absDeviation > allowedDeviation:
                latency = BigWorld.LatencyInfo().value[3]
                errorDueLatency = latency * self.__maxTurretRotationSpeedList[turretIndex]
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

    def getNextGunPitch(self, curAngle, shotAngle, timeDiff, angleLimits, turretIndex):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            gunPitch = replayCtrl.getGunPitch(turretIndex)
            if gunPitch > -100000:
                return gunPitch
        if self.__maxGunRotationSpeedList[turretIndex] == 0.0:
            shotAngle = curAngle
            shotDiff = 0.0
            descr = self.__avatar.getVehicleDescriptor()
            speedLimit = descr.turrets[turretIndex].gun.rotationSpeed * timeDiff
        else:
            if math.fabs(curAngle - shotAngle) < VehicleGunRotator.__ANGLE_EPS:
                if angleLimits is not None:
                    return mathUtils.clamp(angleLimits[0], angleLimits[1], shotAngle)
                return shotAngle
            shotDiff = shotAngle - curAngle
            speedLimit = self.__maxGunRotationSpeedList[turretIndex] * timeDiff
        if angleLimits is not None:
            if shotAngle < angleLimits[0]:
                shotDiff = angleLimits[0] - curAngle
            elif shotAngle > angleLimits[1]:
                shotDiff = angleLimits[1] - curAngle
        staticPitch = self.__getGunStaticPitch(turretIndex)
        if staticPitch is not None and shotDiff * (curAngle - staticPitch) < 0.0:
            speedLimit *= 2.0
        if staticPitch is not None and self.estimatedTurretRotationTime > 0.0:
            idealYawSpeed = abs(shotDiff) / self.estimatedTurretRotationTime
            speedLimit = min(speedLimit, idealYawSpeed * timeDiff)
        return curAngle + min(shotDiff, speedLimit) if shotDiff > 0.0 else curAngle + max(shotDiff, -speedLimit)

    def __getShotPosition(self, turretYaw, gunPitch, turretIndex):
        descr = self.__avatar.getVehicleDescriptor()
        turretOffs = descr.hull.turretPositions[turretIndex] + descr.chassis.hullPosition
        gunOffs = descr.turrets[turretIndex].turret.gunPosition
        shotSpeed = descr.turrets[turretIndex].shot.speed
        turretWorldMatrix = Math.Matrix()
        turretWorldMatrix.setRotateY(turretYaw)
        turretWorldMatrix.translation = turretOffs
        turretWorldMatrix.postMultiply(Math.Matrix(self.getAvatarOwnVehicleStabilisedMatrix(turretIndex)))
        position = turretWorldMatrix.applyPoint(gunOffs)
        gunWorldMatrix = Math.Matrix()
        gunWorldMatrix.setRotateX(gunPitch)
        gunWorldMatrix.postMultiply(turretWorldMatrix)
        vector = gunWorldMatrix.applyVector(Math.Vector3(0, 0, shotSpeed))
        return (position, vector)

    def getAttachedVehicleID(self):
        return self.__avatar.playerVehicleID

    def __getGunMarkerPosition(self, shotPos, shotVec, dispersionAngles, turretIndex):
        shotDescr = self.__avatar.getVehicleDescriptor().turrets[turretIndex].shot
        gravity = Math.Vector3(0.0, -shotDescr.gravity, 0.0)
        maxDist = shotDescr.maxDistance
        testStartPoint = shotPos
        testEndPoint = shotPos + shotVec * 10000.0
        testVehicleID = self.getAttachedVehicleID()
        testEntities = ProjectileMover.getCollidableEntities((testVehicleID,), testStartPoint, testEndPoint)
        collideVehiclesAndStaticScene = ProjectileMover.collideVehiclesAndStaticScene
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
                testRes = collideVehiclesAndStaticScene(prevCheckPoint, curCheckPoint, testEntities)
                if testRes is not None:
                    collData = testRes[1]
                    if collData is not None and not collData.isVehicle():
                        collData = None
                    dir = testRes[0] - prevCheckPoint
                    endPos = testRes[0]
                    bBreak = True
                    break
                pos = collideWithSpaceBB(prevCheckPoint, curCheckPoint)
                if pos is not None:
                    collData = None
                    maxDistCheckFlag = True
                    dir = pos - prevCheckPoint
                    endPos = pos
                    bBreak = True
                    break
                prevCheckPoint = curCheckPoint

            if bBreak:
                break
            prevPos = shotPos + shotVec.scale(dt) + gravity.scale(dt * dt * 0.5)
            prevVelocity = shotVec + gravity.scale(dt)

        dir.normalise()
        distance = (endPos - shotPos).length
        markerDiameter = 2.0 * distance * dispersionAngles[0]
        idealMarkerDiameter = 2.0 * distance * dispersionAngles[1]
        if maxDistCheckFlag:
            if endPos.distTo(shotPos) >= maxDist:
                dir = endPos - shotPos
                dir.normalise()
                endPos = shotPos + dir.scale(maxDist)
                distance = maxDist
                markerDiameter = 2.0 * distance * dispersionAngles[0]
                idealMarkerDiameter = 2.0 * distance * dispersionAngles[1]
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            markerDiameter, endPos, dir = replayCtrl.getGunMarkerParams(endPos, dir, turretIndex)
        return (endPos,
         dir,
         markerDiameter,
         idealMarkerDiameter,
         collData)

    def __updateTurretMatrix(self, yaw, turretIndex, time):
        replayYaw = yaw
        staticTurretYaw = self.__getTurretStaticYaw(turretIndex)
        if staticTurretYaw is not None:
            yaw = staticTurretYaw
        m = Math.Matrix()
        m.setRotateY(yaw)
        self.__turretAnimatorList[turretIndex].update(m, time)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setTurretYaw(replayYaw, turretIndex)
        return

    def __updateGunMatrix(self, pitch, turretIndex, time):
        replayPitch = pitch
        staticPitch = self.__getGunStaticPitch(turretIndex)
        if staticPitch is not None:
            pitch = staticPitch
        m = Math.Matrix()
        m.setRotateX(pitch)
        self.__gunAnimatorList[turretIndex].update(m, time)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setGunPitch(replayPitch, turretIndex)
        return

    def updateGunAngles(self, yaw, pitch, turretIndex):
        self.__updateTurretMatrix(yaw, turretIndex, 0.0)
        self.__updateGunMatrix(pitch, turretIndex, 0.0)

    def getAvatarOwnVehicleStabilisedMatrix(self, turretIndex):
        avatar = self.__avatar
        vehicleMatrix = Math.Matrix(avatar.getOwnVehicleStabilisedMatrix())
        if self.__getTurretStaticYaw(turretIndex) is not None and avatar.vehicle is not None:
            vehicleMatrix = Math.Matrix(avatar.vehicle.filter.interpolateStabilisedMatrix(BigWorld.time()))
        return vehicleMatrix

    def __getGunPitchLimits(self, turretIndex):
        gunPitchLimits = self.__avatar.vehicleTypeDescriptor.turrets[turretIndex].gun.pitchLimits
        staticPitch = self.__getGunStaticPitch(turretIndex)
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

    def __getGunStaticPitch(self, turretIndex):
        return self.__avatar.vehicleTypeDescriptor.turrets[turretIndex].gun.staticPitch

    def __getTurretYawLimits(self, turretIndex):
        turretYawLimits = self.__avatar.vehicleTypeDescriptor.turrets[turretIndex].gun.turretYawLimits
        staticYaw = self.__getTurretStaticYaw(turretIndex)
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

    def __getTurretStaticYaw(self, turretIndex):
        return self.__avatar.vehicleTypeDescriptor.turrets[turretIndex].gun.staticTurretYaw


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

    def __init__(self, updatePeriod=0.1):
        CallbackDelayer.__init__(self)
        self.__updatePeriod = updatePeriod
        self.__soundObjects = None
        self.__oldPitch = 0
        self.__oldTime = 0
        self.__turretCount = len(BigWorld.player().vehicleTypeDescriptor.turrets)
        self.__oldPitch = [ 0 for i in range(self.__turretCount) ]
        self.__init_sound()
        return

    def __init_sound(self):
        if BigWorld.player() is not None and BigWorld.player().getVehicleAttached() is not None:
            compoundModel = BigWorld.player().getVehicleAttached().appearance.compoundModel
            matrixProviders = [compoundModel.node(TankPartNames.TURRET)]
            for i in range(1, self.__turretCount):
                turretName = '%s%d' % (TankPartNames.ADDITIONAL_TURRET, i)
                matrixProviders.append(compoundModel.node(turretName))

            self.connectSoundToMatrix(matrixProviders)
        else:
            matrixProviders = []
            for i in range(self.__turretCount):
                matrixProviders.append(mathUtils.createIdentityMatrix())

            self.connectSoundToMatrix(matrixProviders)
        self.delayCallback(self.__updatePeriod, self.__update)
        return

    def connectSoundToMatrix(self, matrixProviders):
        if self.__soundObjects is not None:
            for i in xrange(len(self.__soundObjects)):
                if self.__soundObjects[i] is not None:
                    self.__soundObjects[i].stopAll()
                    self.__soundObjects[i] = None

        self.__soundObjects = []
        for i in range(self.__turretCount):
            soundEvent = BigWorld.player().vehicleTypeDescriptor.turrets[i].turret.turretRotatorSoundManual
            objectName = 'player_turret' if i == 0 else '%s%d' % ('secondary_turret', i)
            soundObject = SoundGroups.g_instance.WWgetSoundObject(objectName, matrixProviders[i])
            self.__soundObjects.append(soundObject)
            if soundObject is None:
                continue
            soundObject.setRTPC('RTPC_ext_turret_speed', 0)
            soundObject.setRTPC('RTPC_ext_turret_angle', 0)
            soundObject.setRTPC('RTPC_ext_turret_weight', BigWorld.player().vehicleTypeDescriptor.turrets[i].turret.weight / 1000.0)
            soundObject.play(soundEvent)

        return

    def lockSoundMatrix(self):
        if self.__soundObjects is not None:
            for i in xrange(len(self.__soundObjects)):
                provider = self.__soundObjects[i].matrixProvider
                if provider is not None:
                    self.__soundObjects[i].matrixProvider = Math.Matrix(provider)

        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        if self.__soundObjects is not None:
            for i in xrange(len(self.__soundObjects)):
                if self.__soundObjects[i] is not None:
                    self.__soundObjects[i].stopAll()
                    self.__soundObjects[i] = None

        self.__soundObjects = None
        self.__stateTable = None
        return

    def __update(self):
        if not self.__soundObjects:
            return
        elif not hasattr(BigWorld.player(), 'gunRotator'):
            return
        else:
            player = BigWorld.player()
            gunRotator = player.gunRotator
            vehicleTypeDescriptor = player.vehicleTypeDescriptor
            for i in xrange(self.__turretCount):
                soundObject = self.__soundObjects[i]
                if soundObject is None:
                    continue
                maxTurretRotationSpeed = gunRotator.getMaxTurretRotationSpeed(i)
                turretRotationSpeed = gunRotator.getTurretRotationSpeed(i)
                if maxTurretRotationSpeed is not None and maxTurretRotationSpeed > 0:
                    soundObject.setRTPC('RTPC_ext_turret_speed', turretRotationSpeed / maxTurretRotationSpeed)
                else:
                    soundObject.setRTPC('RTPC_ext_turret_speed', 0)
                turretYaw = gunRotator.getTurretYaw(i)
                desiredShotPoint = gunRotator.predictLockedTargetShotPoint()
                if desiredShotPoint is None:
                    isSecondary = False if i == 0 else True
                    desiredShotPoint = player.inputHandler.getDesiredShotPoint(ignoreCurrentAimingMode=isSecondary)
                if desiredShotPoint is None:
                    desiredShotPoint = gunRotator.getMarkerInfo(i)[0]
                cameraTurretYaw, _ = AimingSystems.getTurretYawGunPitch(vehicleTypeDescriptor, i, player.getOwnVehicleStabilisedMatrix(), desiredShotPoint, True)
                angleDiff = abs(turretYaw - cameraTurretYaw)
                if angleDiff > math.pi:
                    angleDiff = 2 * math.pi - angleDiff
                soundObject.setRTPC('RTPC_ext_turret_angle', angleDiff)
                gunPitch = gunRotator.getGunPitch(i)
                soundObject.setRTPC('RTPC_ext_turret_pitch', gunPitch)
                soundObject.setRTPC('RTPC_ext_turret_pitch_speed', abs(self.__oldPitch[i] - gunPitch) / (BigWorld.time() - self.__oldTime))
                self.__oldPitch[i] = gunPitch
                soundObject.setRTPC('RTPC_ext_turret_damaged', 0 if BigWorld.player().deviceStates.get('turretRotator', None) is None else 1)

            self.__oldTime = BigWorld.time()
            return self.__updatePeriod
