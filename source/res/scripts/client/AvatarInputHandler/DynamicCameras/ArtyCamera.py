# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/ArtyCamera.py
from math import pi, copysign, atan2, sqrt
import BattleReplay
import BigWorld
import Settings
from AvatarInputHandler import mathUtils, aih_global_binding, cameras
from AvatarInputHandler.AimingSystems.ArtyAimingSystem import ArtyAimingSystem
from AvatarInputHandler.AimingSystems.ArtyAimingSystemRemote import ArtyAimingSystemRemote
from AvatarInputHandler.DynamicCameras import createOscillatorFromSection, CameraDynamicConfig
from AvatarInputHandler.cameras import ICamera, readFloat, readVec2, ImpulseReason
from Math import slerp, Vector2, Vector3, Matrix, MatrixProduct
from ProjectileMover import collideDynamicAndStatic
from debug_utils import LOG_WARNING
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore

class Hysteresis(object):
    threshold = property(lambda self: self.__threshold)

    def __init__(self, state, threshold):
        self._state = state
        self.__threshold = threshold

    def _dist(self, _):
        return type(self.__threshold)()

    def update(self, state):
        self._state = state

    def check(self, state):
        return self._dist(state) > self.__threshold


class PositionHysteresis(Hysteresis):

    def __init__(self, threshold):
        Hysteresis.__init__(self, Vector3(0.0, 0.0, 0.0), threshold)

    def _dist(self, state):
        return (self._state - state).lengthSquared


class TimeHysteresis(Hysteresis):

    def __init__(self, threshold):
        Hysteresis.__init__(self, 0.0, threshold)

    def _dist(self, state):
        return state - self._state


def getCameraAsSettingsHolder(settingsDataSec):
    return ArtyCamera(settingsDataSec)


class ArtyCamera(ICamera, CallbackDelayer):
    _DYNAMIC_ENABLED = True

    @staticmethod
    def enableDynamicCamera(enable):
        ArtyCamera._DYNAMIC_ENABLED = enable

    @staticmethod
    def isCameraDynamic():
        return ArtyCamera._DYNAMIC_ENABLED

    camera = property(lambda self: self.__cam)
    aimingSystem = property(lambda self: self.__aimingSystem)
    settingsCore = dependency.descriptor(ISettingsCore)
    __aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def __init__(self, dataSec):
        CallbackDelayer.__init__(self)
        self.__positionOscillator = None
        self.__positionNoiseOscillator = None
        self.__dynamicCfg = CameraDynamicConfig()
        self.__readCfg(dataSec)
        self.__cam = BigWorld.CursorCamera()
        self.__curSense = self.__cfg['sensitivity']
        self.__onChangeControlMode = None
        self.__camDist = 0.0
        self.__desiredCamDist = 0.0
        self.__aimingSystem = None
        self.__prevTime = 0.0
        self.__dxdydz = Vector3(0.0, 0.0, 0.0)
        self.__autoUpdatePosition = False
        self.__needReset = 0
        self.__sourceMatrix = None
        self.__targetMatrix = None
        self.__rotation = 0.0
        self.__positionHysteresis = None
        self.__timeHysteresis = None
        return

    def create(self, onChangeControlMode=None):
        self.__onChangeControlMode = onChangeControlMode
        aimingSystemClass = ArtyAimingSystemRemote if BigWorld.player().isObserver() else ArtyAimingSystem
        self.__aimingSystem = aimingSystemClass()
        self.__camDist = self.__cfg['camDist']
        self.__desiredCamDist = self.__camDist
        self.__positionHysteresis = PositionHysteresis(self.__cfg['hPositionThresholdSq'])
        self.__timeHysteresis = TimeHysteresis(self.__cfg['hTimeThreshold'])
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = -1
        self.__cam.pivotPosition = Vector3(0.0, 0.0, 0.0)
        self.__sourceMatrix = Matrix()
        self.__targetMatrix = Matrix()
        self.__rotation = 0.0

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.disable()
        self.__onChangeControlMode = None
        self.__cam = None
        if self.__aimingSystem is not None:
            self.__aimingSystem.destroy()
            self.__aimingSystem = None
        return

    def enable(self, targetPos, saveDist):
        self.__prevTime = 0.0
        self.__aimingSystem.enable(targetPos)
        self.__positionHysteresis.update(Vector3(0.0, 0.0, 0.0))
        self.__timeHysteresis.update(BigWorld.timeExact())
        camTarget = MatrixProduct()
        self.__cam.target = camTarget
        self.__cam.source = self.__sourceMatrix
        self.__cam.wg_applyParams()
        BigWorld.camera(self.__cam)
        BigWorld.player().positionControl.moveTo(self.__aimingSystem.hitPoint)
        BigWorld.player().positionControl.followCamera(False)
        self.__rotation = 0.0
        self.__cameraUpdate()
        self.delayCallback(0.0, self.__cameraUpdate)
        self.__needReset = 1

    def disable(self):
        if self.__aimingSystem is not None:
            self.__aimingSystem.disable()
        self.stopCallback(self.__cameraUpdate)
        BigWorld.camera(None)
        self.__positionOscillator.reset()
        return

    def teleport(self, pos):
        self.__aimingSystem.updateTargetPos(pos)
        self.update(0.0, 0.0, 0.0)

    def getConfigValue(self, name):
        return self.__cfg.get(name)

    def getUserConfigValue(self, name):
        return self.__userCfg.get(name)

    def setUserConfigValue(self, name, value):
        if name not in self.__userCfg:
            return
        self.__userCfg[name] = value
        if name not in ('keySensitivity', 'sensitivity', 'scrollSensitivity'):
            self.__cfg[name] = self.__userCfg[name]
        else:
            self.__cfg[name] = self.__baseCfg[name] * self.__userCfg[name]

    def update(self, dx, dy, dz, updateByKeyboard=False):
        self.__curSense = self.__cfg['keySensitivity'] if updateByKeyboard else self.__cfg['sensitivity']
        self.__autoUpdatePosition = updateByKeyboard
        self.__dxdydz = Vector3(dx if not self.__cfg['horzInvert'] else -dx, dy if not self.__cfg['vertInvert'] else -dy, dz)

    def applyImpulse(self, position, impulse, reason=ImpulseReason.ME_HIT):
        adjustedImpulse, noiseMagnitude = self.__dynamicCfg.adjustImpulse(impulse, reason)
        impulseFlatDir = Vector3(adjustedImpulse.x, 0, adjustedImpulse.z)
        impulseFlatDir.normalise()
        impulseLocal = self.__sourceMatrix.applyVector(impulseFlatDir * (-1 * adjustedImpulse.length))
        self.__positionOscillator.applyImpulse(impulseLocal)
        self.__applyNoiseImpulse(noiseMagnitude)

    def applyDistantImpulse(self, position, impulseValue, reason=ImpulseReason.ME_HIT):
        if reason != ImpulseReason.SPLASH and reason != ImpulseReason.PROJECTILE_HIT:
            return
        impulse = BigWorld.player().getOwnVehiclePosition() - position
        distance = impulse.length
        if distance <= 1.0:
            distance = 1.0
        impulse.normalise()
        if reason == ImpulseReason.PROJECTILE_HIT:
            if not cameras.isPointOnScreen(position):
                return
            distance = 1.0
        impulse *= impulseValue / distance
        self.applyImpulse(position, impulse, reason)

    def writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self.__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('artyMode/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('artyMode/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('artyMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('artyMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('artyMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('artyMode/camera/camDist', self.__cfg['camDist'])

    def __applyNoiseImpulse(self, noiseMagnitude):
        noiseImpulse = mathUtils.RandomVectors.random3Flat(noiseMagnitude)
        self.__positionNoiseOscillator.applyImpulse(noiseImpulse)

    def __calculateAimOffset(self, aimWorldPos):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            aimOffset = replayCtrl.getAimClipPosition()
        else:
            aimOffset = cameras.projectPoint(aimWorldPos)
            aimOffset = Vector2(mathUtils.clamp(-0.95, 0.95, aimOffset.x), mathUtils.clamp(-0.95, 0.95, aimOffset.y))
            if replayCtrl.isRecording:
                replayCtrl.setAimClipPosition(aimOffset)
        return aimOffset

    def __handleMovement(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            if self.__needReset != 0:
                if self.__needReset > 1:
                    from helpers import isPlayerAvatar
                    player = BigWorld.player()
                    if isPlayerAvatar():
                        if player.inputHandler.ctrl is not None:
                            player.inputHandler.ctrl.resetGunMarkers()
                    self.__needReset = 0
                else:
                    self.__needReset += 1
            if replayCtrl.isControllingCamera:
                self.__aimingSystem.updateTargetPos(replayCtrl.getGunRotatorTargetPoint())
            else:
                self.__aimingSystem.handleMovement(self.__dxdydz.x * self.__curSense, -self.__dxdydz.y * self.__curSense)
                if self.__dxdydz.x != 0 or self.__dxdydz.y != 0 or self.__dxdydz.z != 0:
                    self.__needReset = 2
        else:
            self.__aimingSystem.handleMovement(self.__dxdydz.x * self.__curSense, -self.__dxdydz.y * self.__curSense)
        return

    def __getCameraDirection(self):
        direction = Vector3()
        direction.setPitchYaw(self.__rotation, self.__aimingSystem.direction.yaw)
        direction.normalise()
        return direction

    def __getDesiredCameraDistance(self):
        distRange = self.__cfg['distRange']
        self.__desiredCamDist -= self.__dxdydz.z * self.__curSense
        self.__desiredCamDist = mathUtils.clamp(distRange[0], distRange[1], self.__desiredCamDist)
        self.__desiredCamDist = self.__aimingSystem.overrideCamDist(self.__desiredCamDist)
        self.__cfg['camDist'] = self.__camDist
        return self.__desiredCamDist

    def __updateTrajectoryDrawer(self):
        shotDescr = BigWorld.player().getVehicleDescriptor().shot
        BigWorld.wg_trajectory_drawer().setParams(shotDescr.maxDistance, Vector3(0, -shotDescr.gravity, 0), self.__aimOffset)

    def __updateTime(self):
        curTime = BigWorld.timeExact()
        deltaTime = curTime - self.__prevTime
        self.__prevTime = curTime
        return deltaTime

    def __choosePitchLevel(self, aimPoint):
        useHighPitch = (aimPoint - self.__aimingSystem.hitPoint).lengthSquared > self.__cfg['highPitchThresholdSq']
        if useHighPitch:
            useHighPitch = self.__positionHysteresis.check(aimPoint) or self.__timeHysteresis.check(self.__prevTime)
        else:
            self.__positionHysteresis.update(aimPoint)
            self.__timeHysteresis.update(self.__prevTime)
        return useHighPitch

    def __getCollisionTestOrigin(self, aimPoint, direction):
        distRange = self.__cfg['distRange']
        vehiclePosition = BigWorld.player().getVehicleAttached().position
        collisionTestOrigin = Vector3(vehiclePosition)
        if direction.x * direction.x > direction.z * direction.z and not mathUtils.almostZero(direction.x):
            collisionTestOrigin.y = direction.y / direction.x * (vehiclePosition.x - aimPoint.x) + aimPoint.y
        elif not mathUtils.almostZero(direction.z):
            collisionTestOrigin.y = direction.y / direction.z * (vehiclePosition.z - aimPoint.z) + aimPoint.y
        else:
            collisionTestOrigin = aimPoint - direction.scale((distRange[1] - distRange[0]) / 2.0)
            LOG_WARNING("Can't find point on direction ray. Using half point as collision test origin")
        return collisionTestOrigin

    def __resolveCollisions(self, aimPoint, distance, direction):
        distRange = self.__cfg['distRange']
        collisionTestOrigin = self.__getCollisionTestOrigin(aimPoint, direction)
        sign = copysign(1.0, distance * distance - (aimPoint - collisionTestOrigin).lengthSquared)
        srcPoint = collisionTestOrigin
        endPoint = aimPoint - direction.scale(distance + sign * distRange[0])
        collision = collideDynamicAndStatic(srcPoint, endPoint, (BigWorld.player().playerVehicleID,))
        if collision:
            collisionDistance = (aimPoint - collision[0]).length
            if sign * (collisionDistance - distance) < distRange[0]:
                distance = collisionDistance - sign * distRange[0]
        if mathUtils.almostZero(self.__rotation):
            srcPoint = aimPoint - direction.scale(distance)
            endPoint = aimPoint
            collision = collideDynamicAndStatic(srcPoint, endPoint, (BigWorld.player().playerVehicleID,))
            if collision:
                self.__aimingSystem.aimPoint = collision[0]
                if collision[1]:
                    self.__positionHysteresis.update(aimPoint)
                    self.__timeHysteresis.update(self.__prevTime)
        return distance

    def __calculateIdealState(self, deltaTime):
        aimPoint = self.__aimingSystem.aimPoint
        direction = self.__aimingSystem.direction
        impactPitch = max(direction.pitch, self.__cfg['minimalPitch'])
        self.__rotation = max(self.__rotation, impactPitch)
        distRange = self.__cfg['distRange']
        distanceCurSq = (aimPoint - BigWorld.player().getVehicleAttached().position).lengthSquared
        distanceMinSq = distRange[0] ** 2.0
        forcedPitch = impactPitch
        if distanceCurSq < distanceMinSq:
            forcedPitch = atan2(sqrt(distanceMinSq - distanceCurSq), sqrt(distanceCurSq))
        angularShift = self.__cfg['angularSpeed'] * deltaTime
        angularShift = angularShift if self.__choosePitchLevel(aimPoint) else -angularShift
        minPitch = max(forcedPitch, impactPitch)
        maxPitch = max(forcedPitch, self.__cfg['maximalPitch'])
        self.__rotation = mathUtils.clamp(minPitch, maxPitch, self.__rotation + angularShift)
        desiredDistance = self.__getDesiredCameraDistance()
        cameraDirection = self.__getCameraDirection()
        desiredDistance = self.__resolveCollisions(aimPoint, desiredDistance, cameraDirection)
        desiredDistance = mathUtils.clamp(distRange[0], distRange[1], desiredDistance)
        translation = aimPoint - cameraDirection.scale(desiredDistance)
        rotation = Vector3(cameraDirection.yaw, -cameraDirection.pitch, 0.0)
        return (translation, rotation)

    def __interpolateStates(self, deltaTime, translation, rotation):
        lerpParam = mathUtils.clamp(0.0, 1.0, deltaTime * self.__cfg['interpolationSpeed'])
        self.__sourceMatrix = slerp(self.__sourceMatrix, rotation, lerpParam)
        self.__targetMatrix.translation = mathUtils.lerp(self.__targetMatrix.translation, translation, lerpParam)
        return (self.__sourceMatrix, self.__targetMatrix)

    def __cameraUpdate(self):
        deltaTime = self.__updateTime()
        self.__handleMovement()
        aimPoint = Vector3(self.__aimingSystem.aimPoint)
        self.__aimOffset = self.__calculateAimOffset(aimPoint)
        self.__updateTrajectoryDrawer()
        translation, rotation = self.__calculateIdealState(deltaTime)
        self.__interpolateStates(deltaTime, translation, mathUtils.createRotationMatrix(rotation))
        self.__camDist = aimPoint - self.__targetMatrix.translation
        self.__camDist = self.__camDist.length
        self.__cam.source = self.__sourceMatrix
        self.__cam.target.b = self.__targetMatrix
        self.__cam.pivotPosition = Vector3(0, 0, 0)
        BigWorld.player().positionControl.moveTo(aimPoint)
        self.__updateOscillator(deltaTime)
        self.__aimingSystem.update(deltaTime)
        if not self.__autoUpdatePosition:
            self.__dxdydz = Vector3(0, 0, 0)

    def __updateOscillator(self, deltaTime):
        if ArtyCamera.isCameraDynamic():
            self.__positionOscillator.update(deltaTime)
            self.__positionNoiseOscillator.update(deltaTime)
        else:
            self.__positionOscillator.reset()
            self.__positionNoiseOscillator.reset()
        self.__cam.target.a = mathUtils.createTranslationMatrix(self.__positionOscillator.deviation + self.__positionNoiseOscillator.deviation)

    def __readCfg(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <artyMode/camera> in avatar_input_handler.xml')
        self.__baseCfg = dict()
        bcfg = self.__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.005, 10.0, 0.025)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.005, 10.0, 0.025)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.005, 10.0, 0.025)
        bcfg['angularSpeed'] = readFloat(dataSec, 'angularSpeed', pi / 720.0, pi / 0.5, pi / 360.0)
        bcfg['distRange'] = readVec2(dataSec, 'distRange', (1.0, 1.0), (10000.0, 10000.0), (2.0, 30.0))
        bcfg['minimalPitch'] = readFloat(dataSec, 'minimalPitch', pi / 36.0, pi / 3.0, pi / 18.0)
        bcfg['maximalPitch'] = readFloat(dataSec, 'maximalPitch', pi / 6.0, pi / 3.0, pi / 3.5)
        bcfg['interpolationSpeed'] = readFloat(dataSec, 'interpolationSpeed', 0.0, 10.0, 5.0)
        bcfg['highPitchThreshold'] = readFloat(dataSec, 'highPitchThreshold', 0.1, 10.0, 3.0)
        bcfg['hTimeThreshold'] = readFloat(dataSec, 'hysteresis/timeThreshold', 0.0, 10.0, 0.5)
        bcfg['hPositionThreshold'] = readFloat(dataSec, 'hysteresis/positionThreshold', 0.0, 100.0, 7.0)
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['artyMode/camera']
        self.__userCfg = dict()
        ucfg = self.__userCfg
        ucfg['horzInvert'] = self.settingsCore.getSetting('mouseHorzInvert')
        ucfg['vertInvert'] = self.settingsCore.getSetting('mouseVertInvert')
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0.0, 10.0, 1.0)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['camDist'] = readFloat(ds, 'camDist', 0.0, 60.0, 0.0)
        self.__cfg = dict()
        cfg = self.__cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['distRange'] = bcfg['distRange']
        cfg['angularSpeed'] = bcfg['angularSpeed']
        cfg['minimalPitch'] = bcfg['minimalPitch']
        cfg['maximalPitch'] = bcfg['maximalPitch']
        cfg['interpolationSpeed'] = bcfg['interpolationSpeed']
        cfg['highPitchThresholdSq'] = bcfg['highPitchThreshold'] * bcfg['highPitchThreshold']
        cfg['hTimeThreshold'] = bcfg['hTimeThreshold']
        cfg['hPositionThresholdSq'] = bcfg['hPositionThreshold'] * bcfg['hPositionThreshold']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        cfg['camDist'] = ucfg['camDist']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        dynamicSection = dataSec['dynamics']
        self.__dynamicCfg.readImpulsesConfig(dynamicSection)
        self.__positionOscillator = createOscillatorFromSection(dynamicSection['oscillator'], False)
        self.__positionNoiseOscillator = createOscillatorFromSection(dynamicSection['randomNoiseOscillatorFlat'], False)
        return
