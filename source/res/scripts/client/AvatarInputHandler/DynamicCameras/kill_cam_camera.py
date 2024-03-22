# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/kill_cam_camera.py
import logging
import math
from collections import namedtuple
from enum import Enum
from typing import Callable
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import MinMax
from constants import IS_DEVELOPMENT
import BattleReplay
import BigWorld
import Math
import math_utils
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera
from Math import MatrixAnimation, Vector2, Vector3
from gui.shared.events import DeathCamEvent
from helpers import dependency
from helpers.CallbackDelayer import CallbackPauseManager
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
PausedMomentInfo = namedtuple('PausedMomentInfo', ['cameraMatrix',
 'keyframes',
 'elapsedTime',
 'keyFramesTime',
 'yaw',
 'pitch',
 'distance',
 'heightAboveBase',
 'focusRadius'])
_MIN_TIME_TO_PLAYER = 2.0
_MAX_TIME_TO_PLAYER = 4.0
_MIN_DISTANCE_TO_PLAYER = 50
_MAX_DISTANCE_TO_PLAYER = 200
_FINISH_MOVE_DEGREE = 7
_LOOK_AT_KILLER_PITCH_OFFSET = 0.15
_SPOTTED_TRAJECTORY_DELAY = 0.5
_LOOK_AT_KILLER_YAW_OFFSET = 0.0
LOOK_AT_KILLER_DURATION = 5.0
_LOOK_AT_KILLER_TRANSITION = 1.0
_RESUME_TIME_SPEED = 0.2
_QUICK_SPIN_DURATION = 0.8
_TRAJECTORY_TIME_FOLLOW_SETBACK = 0.5
_FINAL_SPIN_DEGREE = 55
_KILLER_MARKER_DELAY = 1.0
_UNSPOTTED_MARKER_DELAY = 0.5
_PHASE_TRANSITION_DELAY = 0.5
_MARKER_FADEOUT_DELAY = 0.5
_HIDE_BUSHES_DURING_TRAJECTORY = False
_WATER_COLLISION_MAX_DISTANCE = 1000

def _floatFromString(value):
    return float(value)


def _boolFromString(value):
    return value.lower() in ('yes', 'true', '1')


def _registerLocalConstantWatcher(constants, name, convert):
    if not IS_DEVELOPMENT:
        return

    def setValue(value):
        constants[name] = convert(value)

    def getValue():
        return constants[name]

    watcherName = name
    if watcherName.startswith('_'):
        watcherName = watcherName[1:]
    BigWorld.addWatcher('KillCam/' + watcherName, getValue, setValue)


_registerLocalConstantWatcher(locals(), '_MIN_TIME_TO_PLAYER', _floatFromString)
_registerLocalConstantWatcher(locals(), '_MAX_TIME_TO_PLAYER', _floatFromString)
_registerLocalConstantWatcher(locals(), '_MIN_DISTANCE_TO_PLAYER', _floatFromString)
_registerLocalConstantWatcher(locals(), '_MAX_DISTANCE_TO_PLAYER', _floatFromString)
_registerLocalConstantWatcher(locals(), '_FINISH_MOVE_DEGREE', _floatFromString)
_registerLocalConstantWatcher(locals(), '_LOOK_AT_KILLER_PITCH_OFFSET', _floatFromString)
_registerLocalConstantWatcher(locals(), '_LOOK_AT_KILLER_YAW_OFFSET', _floatFromString)
_registerLocalConstantWatcher(locals(), 'LOOK_AT_KILLER_DURATION', _floatFromString)
_registerLocalConstantWatcher(locals(), '_LOOK_AT_KILLER_TRANSITION', _floatFromString)
_registerLocalConstantWatcher(locals(), '_RESUME_TIME_SPEED', _floatFromString)
_registerLocalConstantWatcher(locals(), '_SPOTTED_TRAJECTORY_DELAY', _floatFromString)
_registerLocalConstantWatcher(locals(), '_KILLER_MARKER_DELAY', _floatFromString)
_registerLocalConstantWatcher(locals(), '_HIDE_BUSHES_DURING_TRAJECTORY', _boolFromString)

class StartCamDirection(Enum):
    AWAY_FROM_TARGET = 'fromKiller'
    TOWARDS_TARGET = 'towardsKiller'


def getCameraAsSettingsHolder(settingsDataSec):
    return KillCamera(settingsDataSec)


class KillCamera(ArcadeCamera):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    delayMgr = property(lambda self: self.__delayMgr)

    def __init__(self, dataSec, defaultOffset=None):
        self.__isPaused = False
        super(KillCamera, self).__init__(dataSec, defaultOffset)
        self.__bVisionActive = False
        self.__cbIDWait = None
        self.__spinManagerConfig = dataSec['cameraSpinParams']
        self.__delayMgr = CallbackPauseManager()
        self.__killerHuskID = None
        self.__playerHuskID = None
        self.__matrixAnimator = Math.MatrixAnimation()
        self.__currentState = DeathCamEvent.EventType.NONE
        self.__pausedInfo = PausedMomentInfo(Math.Matrix(), (), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.__trajectoryPoints = None
        self.__isCamAngleInverted = False
        self.__originalVehicleProvider = None
        self.__projectileTriNorm = None
        self.__hasProjectilePierced = None
        self.__isSPG = False
        self.__projectileData = None
        self.__isRicochet = False
        self.__onEndingCallback = lambda *args: None
        self.__configCamDistance = dataSec.readFloat('cameraDistance')
        self.__configPivotSettings = (dataSec.readFloat('heightAboveBase'), dataSec.readFloat('focusRadius'))
        self.__cameraCollisionScaleMult = dataSec['advancedCollider'].readFloat('cameraCollisionScaleMult')
        self.__configMovementDuration = dataSec.readFloat('killCamMovementDuration')
        self.__totalSpinDuration = self.__spinManagerConfig.readFloat('spinDuration')
        self.__spinVectorAttacker = self.__spinManagerConfig.readVector2('spinAnglesAttacker')
        self.__spinVectorPlayer = self.__spinManagerConfig.readVector2('spinAnglesPlayer')
        distRange = dataSec.readVector2('pauseDistRange')
        self.__pauseDistRange = MinMax(distRange.x, distRange.y)
        self.__pauseAngleRange = dataSec.readVector2('pauseAngleRange')
        self.__pauseAngleRange[0] = math.radians(self.__pauseAngleRange[0]) - math.pi * 0.5
        self.__pauseAngleRange[1] = math.radians(self.__pauseAngleRange[1]) - math.pi * 0.5
        self.__defaultAngleRange = self._cfg['angleRange']
        self.__defaultDistanceRange = self._cfg['distRange']
        self.__timeInMovement = 0.0
        self.__prevTime = 0.0
        spottedSec = dataSec['spotted']
        unspottedSec = dataSec['unspotted']
        self.__phase3EndAngleHE = dataSec.readFloat('phase3EndAngleHE')
        self.__spottedKillerRadius = spottedSec.readFloat('spottedKillerRadius')
        self.__spottedPlayerRadius = spottedSec.readFloat('spottedPlayerRadius')
        self.__spottedPlayerHERadiusOffset = spottedSec.readFloat('spottedPlayerHERadiusOffset')
        self.__spottedKillerExplosionPitchOffset = spottedSec.readFloat('spottedKillerExplosionPitchOffset')
        self.__spottedKillerExplosionYawOffset = spottedSec.readFloat('spottedKillerExplosionYawOffset')
        self.__spottedPhase1MarkerFadeOut = 1
        self.__spottedPhase2MarkerFadeOut = 1
        self.__trajectoryDelay = spottedSec.readFloat('trajectoryDelay')
        self.__finalSpinDelay = spottedSec.readFloat('finalSpinDelay')
        self.__unspottedRadius = unspottedSec.readFloat('unspottedRadius')
        self.__unspottedHERadiusOffset = unspottedSec.readFloat('unspottedHERadiusOffset')
        self.__unspottedInitAngle = unspottedSec.readFloat('unspottedInitAngle')
        self.__unspottedPhase1Angle = unspottedSec.readFloat('unspottedPhase1Angle')
        self.__unspottedToPhase1SpinDuration = unspottedSec.readFloat('unspottedToPhase1SpinDuration')
        self.__unspottedPhase1FreezeDuration = unspottedSec.readFloat('unspottedPhase1FreezeDuration')
        self.__unspottedPhase2Angle = unspottedSec.readFloat('unspottedPhase2Angle')
        self.__unspottedToPhase2SpinDuration = unspottedSec.readFloat('unspottedToPhase2SpinDuration')
        self.__unspottedPhase2FreezeDuration = unspottedSec.readFloat('unspottedPhase2FreezeDuration')
        self.__unspottedPhase3Angle = unspottedSec.readFloat('unspottedPhase3Angle')
        self.__unspottedToPhase3SpinDuration = unspottedSec.readFloat('unspottedToPhase3SpinDuration')
        self.__unspottedPhase3FreezeDuration = unspottedSec.readFloat('unspottedPhase3FreezeDuration')
        self.__unspottedPitchOffset = unspottedSec.readFloat('unspottedPitchOffset')
        return

    @staticmethod
    def _getConfigsKey():
        return KillCamera.__name__

    def _createCamera(self, enable):
        return BigWorld.DeathCamera(enable)

    @property
    def trajectoryPoints(self):
        return self.__trajectoryPoints

    @trajectoryPoints.setter
    def trajectoryPoints(self, value):
        self.__trajectoryPoints = value
        self.__configMovementDuration = KillCamera.calculateProperTravelTime(self.__trajectoryPoints)

    @property
    def playerHuskID(self):
        return self.__playerHuskID

    @playerHuskID.setter
    def playerHuskID(self, value):
        self.__playerHuskID = value

    @property
    def projectileTriNorm(self):
        return self.__projectileTriNorm

    @property
    def hasProjectilePierced(self):
        return self.__hasProjectilePierced

    @property
    def currentState(self):
        return self.__currentState

    @projectileTriNorm.setter
    def projectileTriNorm(self, value):
        self.__projectileTriNorm = value

    @hasProjectilePierced.setter
    def hasProjectilePierced(self, value):
        self.__hasProjectilePierced = value

    @property
    def isSPG(self):
        return self.__isSPG

    @isSPG.setter
    def isSPG(self, value):
        self.__isSPG = value

    @property
    def isNonPenetratingExplosion(self):
        return self.__projectileData['isExplosion'] and not self.hasProjectilePierced

    def setTestData(self, projectileData=None, isRicochet=None, isSPG=None, movementDuration=None):
        if projectileData is not None:
            self.__projectileData = projectileData
        if isRicochet is not None:
            self.__isRicochet = isRicochet
        if movementDuration is not None:
            self.__configMovementDuration = movementDuration
        if isSPG is not None:
            self.__isSPG = isSPG
        return

    def enable(self, vehicleMProv=None, preferredPos=None, closesDist=False, turretYaw=None, gunPitch=None, camTransitionParams=None, initialPivotSettings=None):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setAimClipPosition(self._aimOffset)
        vMProv = vehicleMProv
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            vehicle = BigWorld.entity(replayCtrl.playerVehicleID)
            if vehicle is not None:
                vMProv = vehicle.matrix
        self.__originalVehicleProvider = self.vehicleMProv = vMProv
        self.__setCameraSettings(pivotSettings=initialPivotSettings or self.__configPivotSettings, yawPitch=preferredPos)
        BigWorld.camera(self.camera)
        self._setDynamicCollisions(True)
        self.camera.aimingSystem = self.aimingSystem
        self.camera.playerSpace = BigWorld.player().spaceID
        self.camera.enable()
        self._cameraUpdate()
        self.delayCallback(0.0, self._cameraUpdate)
        self.__currentState = DeathCamEvent.EventType.ENABLED
        return

    def disable(self):
        self.stopActiveVision()
        self.resetCamera()
        super(KillCamera, self).disable()
        self.__currentState = DeathCamEvent.EventType.NONE

    def resetCamera(self):
        if self.__currentState == DeathCamEvent.EventType.NONE:
            return
        else:
            self.__isPaused = False
            self.__currentState = DeathCamEvent.EventType.ENABLED
            self.__enableTreeHiding(False)
            self.camera.speedTreeTarget = None
            self.camera.disable()
            self.__delayMgr.clearCallbacks()
            self.vehicleMProv = self.__originalVehicleProvider
            self.__matrixAnimator.keyframes = ((0.0, self.__originalVehicleProvider),)
            self.__matrixAnimator.time = 0.0
            self.setCollisionsOnlyAtPos(False)
            return

    def stopActiveVision(self):
        if not self.__bVisionActive:
            return
        else:
            if self.__cbIDWait:
                BigWorld.cancelCallback(self.__cbIDWait)
                self.__cbIDWait = None
            self.__onKillerVisionFinished()
            return

    def calculatePhaseDurations(self, isSpotted):
        if isSpotted:
            phase1Duration = self.__totalSpinDuration + self.__spottedPhase1MarkerFadeOut
            phase2Duration = self.__configMovementDuration + self.__spottedPhase2MarkerFadeOut + self.__trajectoryDelay
            phase3Duration = self.__totalSpinDuration + self.__finalSpinDelay
            marker1Duration = phase1Duration - _KILLER_MARKER_DELAY - self.__spottedPhase1MarkerFadeOut
            marker2Duration = phase2Duration - _PHASE_TRANSITION_DELAY
            marker3Duration = phase3Duration - _PHASE_TRANSITION_DELAY
        else:
            phase1Duration = _PHASE_TRANSITION_DELAY
            phase1Duration += self.__unspottedToPhase1SpinDuration + self.__unspottedPhase1FreezeDuration
            phase2Duration = self.__unspottedToPhase2SpinDuration + self.__unspottedPhase2FreezeDuration
            phase3Duration = self.__unspottedToPhase3SpinDuration + self.__unspottedPhase3FreezeDuration
            marker1Duration = phase1Duration - _PHASE_TRANSITION_DELAY * 2 - _UNSPOTTED_MARKER_DELAY
            marker2Duration = phase2Duration - _PHASE_TRANSITION_DELAY - _UNSPOTTED_MARKER_DELAY
            marker3Duration = phase3Duration - _UNSPOTTED_MARKER_DELAY
        marker1Duration -= _MARKER_FADEOUT_DELAY
        marker2Duration -= _MARKER_FADEOUT_DELAY
        marker3Duration -= _MARKER_FADEOUT_DELAY
        totalSceneDuration = phase1Duration + phase2Duration + phase3Duration
        return (marker1Duration,
         marker2Duration,
         marker3Duration,
         totalSceneDuration)

    def isCameraRotationInverted(self, forInitialSpin=False):
        if self.__isRicochet and forInitialSpin and len(self.__trajectoryPoints) > 2:
            firstLeg = self.__trajectoryPoints[1] - self.__trajectoryPoints[0]
            secondLeg = self.__trajectoryPoints[2] - self.__trajectoryPoints[1]
            firstLeg.normalise()
            secondLeg.normalise()
            return (firstLeg * secondLeg).y > 0
        lastPoint = self.__trajectoryPoints[-1]
        secondLastPoint = Vector3(self.__trajectoryPoints[-2])
        hitVectorInverted = secondLastPoint - lastPoint
        hitVector2D = Vector2(hitVectorInverted.x, hitVectorInverted.z)
        hitVector2D.normalise()
        if self.__isSPG and not self.__hasProjectilePierced:
            playerPosition = Math.Matrix(BigWorld.entity(self.__playerHuskID).matrix).translation
            playerPosFromCenterVector = Vector3(playerPosition - lastPoint)
            playerPos2DVector = Vector2(playerPosFromCenterVector.x, playerPosFromCenterVector.z)
            playerPos2DVector.normalise()
            cosAngle = hitVector2D.dot(playerPos2DVector)
            angle = math.acos(cosAngle)
            crossProduct = hitVector2D.cross2D(playerPos2DVector)
            return angle > math.pi / 2 and crossProduct > 0 or angle < math.pi / 2 and crossProduct < 0
        triNormNorm = Vector3(self.__projectileTriNorm)
        hitVector90DegreeRotated2D = Vector2(triNormNorm.z, -triNormNorm.x)
        hitVector90DegreeRotated2D.normalise()
        return hitVector2D.dot(hitVector90DegreeRotated2D) > 0

    def setCameraToLookTowards(self, sourceVehicleID, targetVehicleID=None, mode=None, firstPoint=None, lastPoint=None, isInstant=True, isInverted=False, originatesFromVehicle=True):
        if not targetVehicleID and not sourceVehicleID:
            return
        else:
            sourceVehicle = BigWorld.entity(sourceVehicleID)
            if sourceVehicle is None:
                return
            sourceVehicleTranslation = Math.Matrix(sourceVehicle.matrix).translation
            if targetVehicleID:
                targetVehicle = BigWorld.entity(targetVehicleID)
                if targetVehicle is None or mode is None:
                    return
                direction = Math.Matrix(targetVehicle.matrix).translation - sourceVehicleTranslation
                pitch = direction.pitch - _LOOK_AT_KILLER_PITCH_OFFSET
                pitch = math_utils.clamp(-math.pi * 0.5, math.pi * 0.5, pitch)
                yaw = direction.yaw
                if mode != StartCamDirection.AWAY_FROM_TARGET:
                    yaw += math.pi
                if isInverted:
                    yaw -= _LOOK_AT_KILLER_YAW_OFFSET
                else:
                    yaw += _LOOK_AT_KILLER_YAW_OFFSET
                if isInstant:
                    self.__setCameraSettings(pivotSettings=self.__configPivotSettings, cameraDistance=self.__configCamDistance, yawPitch=(yaw, pitch))
                    return
                offset = Vector2(_LOOK_AT_KILLER_YAW_OFFSET, _LOOK_AT_KILLER_PITCH_OFFSET)
                self.camera.startLockOnMatrix(LOOK_AT_KILLER_DURATION, sourceVehicle.matrix, targetVehicle.matrix, offset, _LOOK_AT_KILLER_TRANSITION, None)
                return
            if not firstPoint or not lastPoint:
                return
            direction = firstPoint - sourceVehicleTranslation
            if not originatesFromVehicle:
                direction = firstPoint - lastPoint
            yaw = direction.yaw + _LOOK_AT_KILLER_YAW_OFFSET
            pitch = (lastPoint - firstPoint).pitch - _LOOK_AT_KILLER_PITCH_OFFSET
            unwardsPitchLimit = 0 if targetVehicleID is None and not originatesFromVehicle else 0.5
            pitch = math_utils.clamp(-math.pi * 0.5, math.pi * unwardsPitchLimit, pitch)
            if isInstant:
                self.__setCameraSettings(pivotSettings=self.__configPivotSettings, cameraDistance=self.__configCamDistance, yawPitch=(yaw, pitch))
                return
            self.camera.startYawAndPitch(LOOK_AT_KILLER_DURATION + _LOOK_AT_KILLER_TRANSITION, yaw, pitch, None)
            return

    def startKillerVision(self, killerVehicleID, playerVehicleID, isRicochet, projData, onEndingCallback=lambda *args: None):
        self.__isRicochet = isRicochet
        self.__projectileData = projData
        self.__onEndingCallback = onEndingCallback
        self.__setCurrentState(DeathCamEvent.EventType.INIT_SPOTTED)
        self.setCollisionsOnlyAtPos(True, cameraCollisionScaleMult=self.__cameraCollisionScaleMult)
        self.camera.speedTreeTarget = self.__originalVehicleProvider
        self.__killerHuskID = killerVehicleID
        self.__isCamAngleInverted = self.isCameraRotationInverted(forInitialSpin=True)
        if killerVehicleID is None:
            self.__moveCameraTo(playerVehicleID)
        elif not self.__moveCameraTo(killerVehicleID, playerVehicleID):
            _logger.debug("Can't move camera to killer vehicle")
            return
        self.__bVisionActive = True
        self.__adjustCameraDistance(self.__spottedKillerRadius)
        self.__setupCameraYawPitchBeforeSpin(self.__spinVectorAttacker, self.__isCamAngleInverted)
        self.__startPhaseOneSpotted()
        return

    def startPlayerVision(self, projData, onEndingCallback=lambda *args: None):
        self.__isRicochet = False
        self.__projectileData = projData
        self.__onEndingCallback = onEndingCallback
        self.__setCurrentState(DeathCamEvent.EventType.INIT_UNSPOTTED)
        self.setCollisionsOnlyAtPos(True, cameraCollisionScaleMult=self.__cameraCollisionScaleMult)
        self.camera.speedTreeTarget = self.__originalVehicleProvider
        self.__bVisionActive = True
        self.__isCamAngleInverted = self.isCameraRotationInverted()
        if self.__isSPG:
            self.__isCamAngleInverted = not self.__isCamAngleInverted
        firstPoint = self.__trajectoryPoints[0]
        lastPoint = self.__trajectoryPoints[-1]
        projHitPoint = self.__projectileData['impactPoint']
        if projHitPoint:
            center = projHitPoint
        else:
            center = lastPoint
        cameraLength = self.__getCameraLength()
        if not self.hasProjectilePierced:
            center = self.__getPointBeforeCollision(center, cameraLength)
        center = self.__getPointAboveWater(center, cameraLength)
        dirVec = lastPoint - firstPoint
        if self.isNonPenetratingExplosion:
            dirVec = firstPoint - lastPoint
            dirVec.normalise()
            center = center + dirVec * 0.1
        self.vehicleMProv = math_utils.createTranslationMatrix(center)
        initCamOffset = convertDegreeToRad(self.__unspottedInitAngle)
        newYaw = dirVec.yaw - initCamOffset if self.__isCamAngleInverted else dirVec.yaw + initCamOffset
        self.__setKillCamDistance(self.__unspottedRadius, self.__unspottedHERadiusOffset)
        self.__setCameraSettings(pivotSettings=self.__configPivotSettings, yawPitch=(newYaw, dirVec.pitch - self.__unspottedPitchOffset))
        self.__delayMgr.delayCallback(_PHASE_TRANSITION_DELAY, self.__startPhaseOneUnspotted)

    @staticmethod
    def calculateProperTravelTime(points):
        distance = 0.0
        start = None
        for point in points:
            if start is not None:
                distance += (point - start).length
            start = point

        clampDistance = math_utils.clamp(_MIN_DISTANCE_TO_PLAYER, _MAX_DISTANCE_TO_PLAYER, distance)
        clampDistance -= _MIN_DISTANCE_TO_PLAYER
        q = math_utils.linearTween(clampDistance, 1.0, _MAX_DISTANCE_TO_PLAYER - _MIN_DISTANCE_TO_PLAYER)
        return math_utils.lerp(_MIN_TIME_TO_PLAYER, _MAX_TIME_TO_PLAYER, q)

    def _updateProperties(self, state=None):
        super(KillCamera, self)._updateProperties(state)
        if state is None and self.__isPaused:
            self._distRange = self.__pauseDistRange
        return

    def _updateCameraSettings(self, newDist):
        super(KillCamera, self)._updateCameraSettings(newDist)
        if self.__isPaused:
            self.aimingSystem.setAnglesRange(self.__pauseAngleRange)

    def __getCameraLength(self):
        fov = BigWorld.projection().fov
        nearPlane = BigWorld.projection().nearPlane
        fovRatio = self._getFovRatio()
        return fovRatio * nearPlane * math.tan(fov / 2.0) * 2.0

    def __getPointBeforeCollision(self, position, cameraLength):
        spaceID = BigWorld.player().spaceID
        if spaceID is None:
            return position
        else:
            skipFlags = 2 | 4 | 1
            previousTrajectoryPoint = Vector3(self.__trajectoryPoints[-2])
            collision = BigWorld.wg_collideSegment(spaceID, previousTrajectoryPoint, position, skipFlags)
            if collision is None:
                return position
            reverseVector = previousTrajectoryPoint - collision.closestPoint
            reverseVector.normalise()
            return collision.closestPoint + reverseVector * cameraLength

    def __getPointAboveWater(self, position, cameraLength):
        upPoint = Vector3(position)
        upPoint.y += _WATER_COLLISION_MAX_DISTANCE
        downPoint = Vector3(position)
        downPoint.y -= _WATER_COLLISION_MAX_DISTANCE
        waterDist = BigWorld.wg_collideWater(upPoint, downPoint, False)
        if waterDist >= 0:
            waterPos = Vector3(upPoint.x, upPoint.y - waterDist, upPoint.z)
            if waterPos.y > position.y:
                verticalOffset = Vector3(0, cameraLength, 0)
                return waterPos + verticalOffset
        return position

    def __shouldHideBushes(self, state):
        return _HIDE_BUSHES_DURING_TRAJECTORY if state == DeathCamEvent.EventType.MOVING_TO_PLAYER else True

    def __setCurrentState(self, state):
        self.__currentState = state
        self.__setCursorCollision()
        self.__enableTreeHiding(self.__shouldHideBushes(self.__currentState))
        ctx = {'configMovementDuration': self.__configMovementDuration}
        self.__guiSessionProvider.shared.killCamCtrl.changeCameraState(state, ctx)

    def __enableTreeHiding(self, isHidden):
        BigWorld.wg_enableTreeHiding(isHidden)

    def __setCursorCollision(self):
        collisionPhases = [DeathCamEvent.EventType.LAST_ROTATION]
        if self.hasProjectilePierced:
            collisionPhases += [DeathCamEvent.EventType.ROTATING_KILLER, DeathCamEvent.EventType.UNSPOTTED_PHASE_ONE, DeathCamEvent.EventType.UNSPOTTED_PHASE_TWO]
        isCollisionPhase = self.__currentState in collisionPhases
        if isCollisionPhase and not self.__isPaused:
            spaceID = BigWorld.player().spaceID
            if spaceID is None:
                return
            self.delayCallback(0, self.__collisionLoop, spaceID)
        elif self.__isPaused:
            self.stopCallback(self.__collisionLoop)
            if self.__currentState != DeathCamEvent.EventType.LAST_ROTATION:
                self.aimingSystem.cursorShouldCheckCollisions(True)
        else:
            self.stopCallback(self.__collisionLoop)
            self.aimingSystem.cursorShouldCheckCollisions(False)
        return

    def __collisionLoop(self, spaceID):
        skipFlags = 2 | 4 | 1
        pointToCheck = self.__trajectoryPoints[0] if self.__currentState == DeathCamEvent.EventType.ROTATING_KILLER else self.__trajectoryPoints[-1]
        collision = BigWorld.wg_collideSegment(spaceID, pointToCheck, BigWorld.camera().position, skipFlags)
        if collision is not None:
            if self.__currentState == DeathCamEvent.EventType.LAST_ROTATION:
                self.camera.stopAllMovements()
            else:
                self.aimingSystem.cursorShouldCheckCollisions(True)
        else:
            return 0.1
        return

    def __setupCameraYawPitchBeforeSpin(self, spinVector, isInverted):
        startDiffYaw = math.pi * spinVector[0] / 180
        finalYaw = self.aimingSystem.yaw - _LOOK_AT_KILLER_YAW_OFFSET
        if isInverted:
            finalYaw -= startDiffYaw
        else:
            finalYaw += startDiffYaw
        self.setYawPitch(finalYaw, 0 if self.aimingSystem.pitch > 0 else self.aimingSystem.pitch)

    def __onKillerVisionFinished(self):
        self.__bVisionActive = False
        self.__moveCameraTo(BigWorld.player().playerVehicleID)
        self.__cbIDWait = None
        return

    def __moveCameraTo(self, vehicleID, sourceVehicleID=None):
        if not BigWorld.player().inputHandler.isStarted:
            return False
        else:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is None:
                return False
            targetMatrix = vehicle.matrix
            self.__setCameraSettings(targetMP=targetMatrix, pivotSettings=self.getPivotSettings(), cameraDistance=self.getCameraDistance(), yawPitch=self.angles)
            if sourceVehicleID is not None:
                sourceVehicle = BigWorld.entity(sourceVehicleID)
                if sourceVehicle is not None:
                    self.setCameraToLookTowards(sourceVehicleID=sourceVehicleID, targetVehicleID=vehicleID, mode=StartCamDirection.AWAY_FROM_TARGET, isInverted=self.__isCamAngleInverted)
            return True

    def __setCameraSettings(self, targetMP=None, pivotSettings=None, cameraDistance=None, yawPitch=None):
        if targetMP is not None:
            self.vehicleMProv = targetMP
        if pivotSettings is not None:
            self.setPivotSettings(*pivotSettings)
        if cameraDistance is not None:
            if cameraDistance < 2:
                _logger.warning('Setting distance to low value: %s', cameraDistance)
            self.setCameraDistance(cameraDistance)
        if yawPitch is not None:
            self.setYawPitch(yawPitch[0], yawPitch[1])
        return

    def __startPhaseOneUnspotted(self):
        self.__delayMgr.delayCallback(_UNSPOTTED_MARKER_DELAY, self.__setCurrentState, DeathCamEvent.EventType.UNSPOTTED_PHASE_ONE)
        self.camera.startNewSpin(self.__unspottedToPhase1SpinDuration, self.__unspottedPhase1Angle, self.__spinVectorPlayer, self.__isCamAngleInverted, True, self.__transitionToUnspottedPhaseTwo)

    def __transitionToUnspottedPhaseTwo(self):
        self.__delayMgr.delayCallback(self.__unspottedPhase1FreezeDuration, self.__startPhaseTwoUnspotted)
        self.__delayMgr.delayCallback(self.__unspottedPhase1FreezeDuration - _PHASE_TRANSITION_DELAY, self.__startTransitionPhase)

    def __startPhaseTwoUnspotted(self):
        self.__delayMgr.delayCallback(_UNSPOTTED_MARKER_DELAY, self.__setCurrentState, DeathCamEvent.EventType.UNSPOTTED_PHASE_TWO)
        self.camera.startNewSpin(self.__unspottedToPhase2SpinDuration, self.__unspottedPhase2Angle, self.__spinVectorPlayer, self.__isCamAngleInverted, True, self.__transitionToUnspottedPhaseThree)

    def __transitionToUnspottedPhaseThree(self):
        self.__delayMgr.delayCallback(self.__unspottedPhase2FreezeDuration, self.__startPhaseThreeUnspotted)
        self.__delayMgr.delayCallback(self.__unspottedPhase2FreezeDuration - _PHASE_TRANSITION_DELAY, self.__startTransitionPhase)

    def __startPhaseThreeUnspotted(self):
        self.__delayMgr.delayCallback(_UNSPOTTED_MARKER_DELAY, self.__setCurrentState, DeathCamEvent.EventType.LAST_ROTATION)
        self.camera.startNewSpin(self.__unspottedToPhase3SpinDuration, self.__unspottedPhase3Angle, self.__spinVectorPlayer, self.__isCamAngleInverted, True, self.__transitionToUnspottedFinish)

    def __transitionToUnspottedFinish(self):
        self.__delayMgr.delayCallback(self.__unspottedPhase3FreezeDuration, self.__onEndingCallback)

    def __startPhaseOneSpotted(self):
        self.__delayMgr.delayCallback(_KILLER_MARKER_DELAY, self.__setCurrentState, DeathCamEvent.EventType.ROTATING_KILLER)
        self.camera.startNewSpin(self.__totalSpinDuration, None, self.__spinVectorAttacker, self.__isCamAngleInverted, False, self.__transitionToSpottedPhaseTwo)
        self.vehicleMProv = math_utils.createTranslationMatrix(self.__trajectoryPoints[0])
        return

    def __transitionToSpottedPhaseTwo(self):
        self.__delayMgr.delayCallback(self.__spottedPhase1MarkerFadeOut + self.__trajectoryDelay, self.__startPhaseTwoSpotted)
        self.__delayMgr.delayCallback(self.__spottedPhase1MarkerFadeOut, self.__setCurrentState, DeathCamEvent.EventType.MOVING_TO_PLAYER)
        self.__startTransitionPhase()

    def __startPhaseTwoSpotted(self):
        self.__isPaused = False
        if not self.__trajectoryPoints:
            self.__onEndingCallback()
            return
        else:
            beginningMatrix = math_utils.createTranslationMatrix(self.__trajectoryPoints[0])
            if beginningMatrix is None:
                self.__onEndingCallback()
                return
            heightAboveBase, focusRadius = self.aimingSystem.getPivotSettings()
            self.__pausedInfo = PausedMomentInfo(beginningMatrix, (), 0.0, 0.0, self.aimingSystem.yaw, self.aimingSystem.pitch, self.aimingSystem.distanceFromFocus, heightAboveBase, focusRadius)
            destVehicleMatrix = Math.Matrix(BigWorld.entity(self.__playerHuskID).matrix)
            if self.__isSPG:
                destVehicleMatrix.setRotateYPR((destVehicleMatrix.yaw + self.__spottedKillerExplosionYawOffset, destVehicleMatrix.pitch + self.__spottedKillerExplosionPitchOffset, destVehicleMatrix.roll))
            if self.__trajectoryPoints:
                self.__prepareMatrixWithTrajectoryPoints()
            else:
                self.__matrixAnimator.keyframes = ((0.0, beginningMatrix), (self.__configMovementDuration, destVehicleMatrix))
            self.__matrixAnimator.time = 0.0
            self.vehicleMProv = self.__matrixAnimator
            self.__setKillCamDistance(self.__spottedPlayerRadius, self.__spottedPlayerHERadiusOffset, self.__configMovementDuration)
            self.camera.startNewSpin(self.__configMovementDuration, _FINISH_MOVE_DEGREE, self.__spinVectorPlayer, not self.__isCamAngleInverted, False, self.__transitionToSpottedPhaseThree)
            self.__isCamAngleInverted = self.isCameraRotationInverted()
            return

    def __transitionToSpottedPhaseThree(self):
        self.__enableTreeHiding(self.__shouldHideBushes(self.__currentState))
        self.__delayMgr.delayCallback(self.__spottedPhase2MarkerFadeOut, self.__startPhaseThreeSpotted)
        self.__delayMgr.delayCallback(self.__spottedPhase2MarkerFadeOut - _PHASE_TRANSITION_DELAY, self.__startTransitionPhase)

    def __startPhaseThreeSpotted(self):
        self.__delayMgr.delayCallback(_PHASE_TRANSITION_DELAY, self.__setCurrentState, DeathCamEvent.EventType.LAST_ROTATION)
        self.__delayMgr.delayCallback(self.__finalSpinDelay, self.__transitionToSpottedFinish)

    def __transitionToSpottedFinish(self):
        self.camera.startNewSpin(self.__totalSpinDuration, _FINAL_SPIN_DEGREE, self.__spinVectorPlayer, self.__isCamAngleInverted, True, self.__onEndingCallback)

    def __prepareMatrixWithTrajectoryPoints(self):
        timePoint = 0.0
        newKeyframes = []
        eachPointTime = self.__configMovementDuration / (len(self.__trajectoryPoints) - 1)
        trajectory = self.__trajectoryPoints[:]
        if self.__projectileData['impactPoint']:
            trajectory[-1] = self.__projectileData['impactPoint']
        if self.isNonPenetratingExplosion:
            cameraLength = self.__getCameraLength()
            center = self.__getPointBeforeCollision(trajectory[-1], cameraLength)
            dirVec = self.__trajectoryPoints[0] - self.__trajectoryPoints[-1]
            dirVec.normalise()
            trajectory[-1] = center + dirVec * 0.1
        for point in trajectory:
            newKeyframes.append((timePoint, math_utils.createTranslationMatrix(point)))
            timePoint += eachPointTime

        self.__matrixAnimator.keyframes = tuple(newKeyframes)

    def userInterruption(self, isPaused):
        if self.__isPaused == isPaused:
            return
        self.__updateCameraSettingsOnPause(isPaused)
        if isPaused:
            self.__pauseMove()
            self.__delayMgr.pauseCallbacks()
        else:
            self.__resumeMove()
            self.__delayMgr.resumeCallbacks()

    def update(self, dx, dy, dz, rotateMode=True, zoomMode=True, updatedByKeyboard=False):
        if self.__isPaused:
            super(KillCamera, self).update(dx=dx, dy=dy, dz=dz, rotateMode=rotateMode, zoomMode=True, updatedByKeyboard=updatedByKeyboard)

    def __pauseMove(self):
        heightAboveBase, focusRadius = self.aimingSystem.getPivotSettings()
        self.__pausedInfo = PausedMomentInfo(Math.Matrix(self.__matrixAnimator), tuple(self.__matrixAnimator.keyframes), self.__matrixAnimator.time + self.__pausedInfo.elapsedTime, self.__matrixAnimator.time, self.aimingSystem.yaw, self.aimingSystem.pitch, self.aimingSystem.distanceFromFocus, heightAboveBase, focusRadius)
        self.__isPaused = True
        self.__setCursorCollision()
        self.camera.pause()
        self.__matrixAnimator.keyframes = ((0.0, self.__pausedInfo.cameraMatrix),)
        self.__enableTreeHiding(True)

    def __resumeMove(self):
        if self.__delayMgr.hasDelayedCallback(self.__startPhaseTwoSpotted):
            self.aimingSystem.distanceFromFocus = self.__pausedInfo.distance
        else:
            self.camera.startDistanceAnimation(_RESUME_TIME_SPEED, self.__pausedInfo.distance, None)
        self.camera.startYawAndPitch(_RESUME_TIME_SPEED, self.__pausedInfo.yaw, self.__pausedInfo.pitch, None)
        self.aimingSystem.setPivotSettings(self.__pausedInfo.heightAboveBase, self.__pausedInfo.focusRadius)
        self.__matrixAnimator.keyframes = tuple(self.__pausedInfo.keyframes)
        self.__matrixAnimator.time = self.__pausedInfo.keyFramesTime
        self.__enableTreeHiding(self.__shouldHideBushes(self.__currentState))
        self.__isPaused = False
        self.__setCursorCollision()
        self.camera.resume()
        return

    def __setKillCamDistance(self, distance, spgOffset, duration=0):
        isExplosion = self.__projectileData['isExplosion']
        if isExplosion:
            explosionRadius = self.__projectileData['explosionRadius']
            newDistance = explosionRadius + spgOffset
        else:
            newDistance = distance
        if duration > 0:
            self.camera.startDistanceAnimation(duration, newDistance, None)
        else:
            self.setCameraDistance(newDistance)
        return

    def __updateCameraSettingsOnPause(self, isPaused):
        if isPaused:
            self.aimingSystem.setAnglesRange(self.__pauseAngleRange)
        else:
            self.aimingSystem.setAnglesRange(self._cfg['angleRange'])

    def __startTransitionPhase(self):
        self.__setCurrentState(DeathCamEvent.EventType.TRANSITIONING)

    def __adjustCameraDistance(self, distance):
        distRange = self._distRange
        clampedDist = math_utils.clamp(distRange.min, distRange.max, distance)
        self.aimingSystem.adjustDistanceFromFocus(clampedDist)
        self.inputInertiaTeleport()


def convertDegreeToRad(angleDegree):
    return math.pi * angleDegree / 180
