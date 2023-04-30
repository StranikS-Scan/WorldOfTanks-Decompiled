# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/ArtyCamera.py
from math import pi, copysign, atan2, sqrt
import BigWorld
from Math import slerp, Vector2, Vector3, Matrix, MatrixProduct
import BattleReplay
import Settings
import math_utils
from AvatarInputHandler import aih_global_binding, cameras
from BigWorld import ArtyAimingSystem, ArtyAimingSystemRemote
from AvatarInputHandler.DynamicCameras import createOscillatorFromSection, CameraDynamicConfig, CameraWithSettings, SPGScrollSmoother
from AvatarInputHandler.DynamicCameras.camera_switcher import CameraSwitcher, SwitchTypes, CameraSwitcherCollection, SwitchToPlaces, TRANSITION_DIST_HYSTERESIS
from AvatarInputHandler.cameras import readFloat, readVec2, ImpulseReason
from ProjectileMover import collideDynamicAndStatic
from account_helpers.settings_core.settings_constants import GAME, SPGAim
from aih_constants import CTRL_MODE_NAME
from debug_utils import LOG_WARNING
from helpers.CallbackDelayer import CallbackDelayer
_SEARCH_COLLISION_DEPTH = 1
_OFFSET_FROM_NEAR_PLANE = 0.01

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


class ArtyCamera(CameraWithSettings, CallbackDelayer):
    _DYNAMIC_ENABLED = True

    @staticmethod
    def enableDynamicCamera(enable):
        ArtyCamera._DYNAMIC_ENABLED = enable

    @staticmethod
    def isCameraDynamic():
        return ArtyCamera._DYNAMIC_ENABLED

    camera = property(lambda self: self.__cam)
    aimingSystem = property(lambda self: self.__aimingSystem)
    __aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def __init__(self, dataSec):
        super(ArtyCamera, self).__init__()
        CallbackDelayer.__init__(self)
        self.isAimOffsetEnabled = True
        self.__positionOscillator = None
        self.__positionNoiseOscillator = None
        self.__switchers = CameraSwitcherCollection(cameraSwitchers=[CameraSwitcher(switchType=SwitchTypes.FROM_TRANSITION_DIST_AS_MAX, switchToName=CTRL_MODE_NAME.STRATEGIC, switchToPos=0.0)], isEnabled=True)
        self.__dynamicCfg = CameraDynamicConfig()
        self._readConfigs(dataSec)
        self.__cam = BigWorld.CursorCamera()
        self.__curSense = self._cfg['sensitivity']
        self.__onChangeControlMode = None
        self.__camDist = 0.0
        self.__desiredCamDist = 0.0
        self.__aimingSystem = None
        self.__prevTime = 0.0
        self.__prevAimPoint = Vector3()
        self.__dxdydz = Vector3(0.0, 0.0, 0.0)
        self.__autoUpdatePosition = False
        self.__needReset = 0
        self.__sourceMatrix = None
        self.__targetMatrix = None
        self.__rotation = 0.0
        self.__positionHysteresis = None
        self.__timeHysteresis = None
        self.__transitionEnabled = True
        self.__scrollSmoother = SPGScrollSmoother(0.3)
        self.__collisionDist = 0.0
        self.__camViewPoint = Vector3()
        return

    @staticmethod
    def _getConfigsKey():
        return ArtyCamera.__name__

    def create(self, onChangeControlMode=None):
        super(ArtyCamera, self).create()
        self.__onChangeControlMode = onChangeControlMode
        aimingSystemClass = ArtyAimingSystemRemote if BigWorld.player().isObserver() else ArtyAimingSystem
        self.__aimingSystem = aimingSystemClass()
        self.__camDist = self._cfg['camDist']
        self.__desiredCamDist = self.__camDist
        self.__positionHysteresis = PositionHysteresis(self._cfg['hPositionThresholdSq'])
        self.__timeHysteresis = TimeHysteresis(self._cfg['hTimeThreshold'])
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = -1
        self.__cam.pivotPosition = Vector3(0.0, 0.0, 0.0)
        self.__sourceMatrix = Matrix()
        self.__targetMatrix = Matrix()
        self.__rotation = 0.0
        self.__enableSwitchers()
        self.__scrollSmoother.setTime(self._cfg['scrollSmoothingTime'])

    def destroy(self):
        self.disable()
        self.__onChangeControlMode = None
        self.__cam = None
        if self.__aimingSystem is not None:
            self.__aimingSystem.destroy()
            self.__aimingSystem = None
        CallbackDelayer.destroy(self)
        CameraWithSettings.destroy(self)
        return

    def enable(self, targetPos, saveDist, switchToPos=None, switchToPlace=None):
        BigWorld.wg_trajectory_drawer().setStrategicMode(False)
        self.__prevTime = 0.0
        if switchToPlace == SwitchToPlaces.TO_TRANSITION_DIST:
            self.__camDist = math_utils.clamp(self._cfg['distRange'][0], self._cfg['distRange'][1], self._cfg['transitionDist'])
        elif switchToPlace == SwitchToPlaces.TO_RELATIVE_POS and switchToPos is not None:
            minDist, maxDist = self._cfg['distRange']
            self.__camDist = (maxDist - minDist) * switchToPos + minDist
        elif switchToPlace == SwitchToPlaces.TO_NEAR_POS and switchToPos is not None:
            minDist, maxDist = self._cfg['distRange']
            self.__camDist = math_utils.clamp(minDist, maxDist, switchToPos)
        elif self.settingsCore.getSetting(SPGAim.AUTO_CHANGE_AIM_MODE):
            self.__camDist = math_utils.clamp(self._cfg['distRange'][0], self._cfg['transitionDist'], self.__camDist)
        self.__desiredCamDist = self.__camDist
        self.__scrollSmoother.start(self.__desiredCamDist)
        self.__enableSwitchers()
        self.__aimingSystem.enable(targetPos)
        self.__positionHysteresis.update(Vector3(0.0, 0.0, 0.0))
        self.__timeHysteresis.update(BigWorld.timeExact())
        camTarget = MatrixProduct()
        self.__rotation = max(self.__aimingSystem.direction.pitch, self._cfg['minimalPitch'])
        cameraDirection = self.__getCameraDirection()
        self.__targetMatrix.translation = self.aimingSystem.aimPoint - cameraDirection.scale(self.__camDist)
        self.__cam.target = camTarget
        self.__cam.target.b = self.__targetMatrix
        self.__sourceMatrix = math_utils.createRotationMatrix((cameraDirection.yaw, -cameraDirection.pitch, 0.0))
        self.__cam.source = self.__sourceMatrix
        self.__cam.forceUpdate()
        BigWorld.camera(self.__cam)
        BigWorld.player().positionControl.moveTo(self.__aimingSystem.hitPoint)
        BigWorld.player().positionControl.followCamera(False)
        self.__cameraUpdate()
        self.delayCallback(0.01, self.__cameraUpdate)
        self.__needReset = 1
        return

    def disable(self):
        self.__scrollSmoother.stop()
        if self.__aimingSystem is not None:
            self.__aimingSystem.disable()
        self.stopCallback(self.__cameraUpdate)
        self.__switchers.clear()
        self.__positionOscillator.reset()
        return

    def teleport(self, pos):
        self.__aimingSystem.updateTargetPos(pos)
        self.update(0.0, 0.0, 0.0)

    def getDistRatio(self):
        minDist, maxDist = self._cfg['distRange']
        return (self.__desiredCamDist - minDist) / (maxDist - minDist)

    def getCurrentCamDist(self):
        return self.__desiredCamDist

    def getCamDistRange(self):
        return self._cfg['distRange']

    def getCamTransitionDist(self):
        return self._cfg['transitionDist']

    def update(self, dx, dy, dz, updateByKeyboard=False):
        self.__curSense = self._cfg['keySensitivity'] if updateByKeyboard else self._cfg['sensitivity']
        self.__autoUpdatePosition = updateByKeyboard
        self.__dxdydz = Vector3(dx if not self._cfg['horzInvert'] else -dx, dy if not self._cfg['vertInvert'] else -dy, dz)

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
        ucfg = self._userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('artyMode/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('artyMode/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('artyMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('artyMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('artyMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('artyMode/camera/camDist', self._cfg['camDist'])

    def __applyNoiseImpulse(self, noiseMagnitude):
        noiseImpulse = math_utils.RandomVectors.random3Flat(noiseMagnitude)
        self.__positionNoiseOscillator.applyImpulse(noiseImpulse)

    def __calculateAimOffset(self, aimWorldPos):
        if not self.isAimOffsetEnabled:
            return Vector2(0.0, 0.0)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            aimOffset = replayCtrl.getAimClipPosition()
        else:
            proj = BigWorld.projection()
            aimLocalPos = Matrix(self.__cam.matrix).applyPoint(aimWorldPos)
            if aimLocalPos.z < 0:
                aimLocalPos.z = max(0.0, proj.nearPlane - _OFFSET_FROM_NEAR_PLANE)
                aimWorldPos = Matrix(self.__cam.invViewMatrix).applyPoint(aimLocalPos)
            aimOffset = cameras.projectPoint(aimWorldPos)
            aimOffset = Vector2(math_utils.clamp(-0.95, 0.95, aimOffset.x), math_utils.clamp(-0.95, 0.95, aimOffset.y))
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
        distRange = self.__switchersDistRange()
        self.__desiredCamDist -= self.__dxdydz.z * self.__curSense
        self.__desiredCamDist = math_utils.clamp(distRange[0], distRange[1], self.__desiredCamDist)
        self.__desiredCamDist = self.__aimingSystem.overrideCamDist(self.__desiredCamDist)
        self._cfg['camDist'] = self.__camDist
        self.__scrollSmoother.moveTo(self.__desiredCamDist, distRange)
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
        useHighPitch = (aimPoint - self.__aimingSystem.hitPoint).lengthSquared > self._cfg['highPitchThresholdSq']
        if useHighPitch:
            useHighPitch = self.__positionHysteresis.check(aimPoint) or self.__timeHysteresis.check(self.__prevTime)
        else:
            self.__positionHysteresis.update(aimPoint)
            self.__timeHysteresis.update(self.__prevTime)
        return useHighPitch

    def __getCollisionTestOrigin(self, aimPoint, direction):
        distRange = self.__switchersDistRange()
        vehiclePosition = BigWorld.player().getVehicleAttached().position
        collisionTestOrigin = Vector3(vehiclePosition)
        if direction.x * direction.x > direction.z * direction.z and not math_utils.almostZero(direction.x):
            collisionTestOrigin.y = direction.y / direction.x * (vehiclePosition.x - aimPoint.x) + aimPoint.y
        elif not math_utils.almostZero(direction.z):
            collisionTestOrigin.y = direction.y / direction.z * (vehiclePosition.z - aimPoint.z) + aimPoint.y
        else:
            collisionTestOrigin = aimPoint - direction.scale((distRange[1] - distRange[0]) / 2.0)
            LOG_WARNING("Can't find point on direction ray. Using half point as collision test origin")
        return collisionTestOrigin

    def __resolveCollisions(self, aimPoint, distance, direction):
        distRange = self.__switchersDistRange()
        collisionDist = 0.0
        collisionTestOrigin = self.__getCollisionTestOrigin(aimPoint, direction)
        sign = copysign(1.0, distance * distance - (aimPoint - collisionTestOrigin).lengthSquared)
        srcPoint = collisionTestOrigin
        endPoint = aimPoint - direction.scale(distance + sign * (distRange[0] + _SEARCH_COLLISION_DEPTH))
        collision = collideDynamicAndStatic(srcPoint, endPoint, (BigWorld.player().playerVehicleID,))
        if collision:
            collisionDistance = (aimPoint - collision[0]).length
            collisionDist = collisionDistance - sign * distRange[0]
            if sign * (collisionDistance - distance) < distRange[0]:
                distance = collisionDist
        if math_utils.almostZero(self.__rotation):
            srcPoint = aimPoint - direction.scale(distance)
            endPoint = aimPoint
            collision = collideDynamicAndStatic(srcPoint, endPoint, (BigWorld.player().playerVehicleID,))
            if collision:
                self.__aimingSystem.aimPoint = collision[0]
                if collision[1]:
                    self.__positionHysteresis.update(aimPoint)
                    self.__timeHysteresis.update(self.__prevTime)
        return collisionDist

    def __calculateIdealState(self, deltaTime):
        aimPoint = self.__aimingSystem.aimPoint
        direction = self.__aimingSystem.direction
        impactPitch = max(direction.pitch, self._cfg['minimalPitch'])
        self.__rotation = max(self.__rotation, impactPitch)
        distRange = self.__switchersDistRange()
        distanceCurSq = (aimPoint - BigWorld.player().getVehicleAttached().position).lengthSquared
        distanceMinSq = distRange[0] ** 2.0
        forcedPitch = impactPitch
        if distanceCurSq < distanceMinSq:
            forcedPitch = atan2(sqrt(distanceMinSq - distanceCurSq), sqrt(distanceCurSq))
        angularShift = self._cfg['angularSpeed'] * deltaTime
        angularShift = angularShift if self.__choosePitchLevel(aimPoint) else -angularShift
        minPitch = max(forcedPitch, impactPitch)
        maxPitch = max(forcedPitch, self._cfg['maximalPitch'])
        self.__rotation = math_utils.clamp(minPitch, maxPitch, self.__rotation + angularShift)
        desiredDistance = self.__getDesiredCameraDistance()
        cameraDirection = self.__getCameraDirection()
        collisionDist = self.__resolveCollisions(aimPoint, desiredDistance, cameraDirection)
        collisionDist = max(distRange[0], collisionDist)
        desiredDistance = self.__scrollSmoother.update(deltaTime)
        rotation = Vector3(cameraDirection.yaw, -cameraDirection.pitch, 0.0)
        return (rotation, desiredDistance, collisionDist)

    def __interpolateStates(self, deltaTime, rotation, desiredDistance, collisionDist):
        lerpParam = math_utils.clamp(0.0, 1.0, deltaTime * self._cfg['interpolationSpeed'])
        collisionLerpParam = math_utils.clamp(0.0, 1.0, deltaTime * self._cfg['distInterpolationSpeed'])
        self.__sourceMatrix = slerp(self.__sourceMatrix, rotation, lerpParam)
        camDirection = Vector3()
        camDirection.setPitchYaw(-self.__sourceMatrix.pitch, self.__sourceMatrix.yaw)
        camDirection.normalise()
        self.__camViewPoint = math_utils.lerp(self.__camViewPoint, self.__aimingSystem.aimPoint, lerpParam)
        self.__collisionDist = math_utils.lerp(self.__collisionDist, collisionDist, collisionLerpParam)
        desiredDistance = max(desiredDistance, self.__collisionDist)
        self.__targetMatrix.translation = self.__camViewPoint - camDirection.scale(desiredDistance)
        return (self.__sourceMatrix, self.__targetMatrix)

    def __cameraUpdate(self):
        deltaTime = self.__updateTime()
        self.__aimOffset = self.__calculateAimOffset(self.__aimingSystem.aimPoint)
        self.__handleMovement()
        aimPoint = Vector3(self.__aimingSystem.aimPoint)
        self.__updateTrajectoryDrawer()
        rotation, desiredDistance, collisionDist = self.__calculateIdealState(deltaTime)
        self.__interpolateStates(deltaTime, math_utils.createRotationMatrix(rotation), desiredDistance, collisionDist)
        self.__camDist = aimPoint - self.__targetMatrix.translation
        self.__camDist = self.__camDist.length
        self.__cam.source = self.__sourceMatrix
        self.__cam.target.b = self.__targetMatrix
        self.__cam.pivotPosition = Vector3(0, 0, 0)
        if aimPoint.distSqrTo(self.__prevAimPoint) > 0.010000000000000002:
            BigWorld.player().positionControl.moveTo(aimPoint)
            self.__prevAimPoint = aimPoint
        self.__updateOscillator(deltaTime)
        self.__aimingSystem.update(deltaTime)
        if self.__onChangeControlMode is not None and self.__switchers.needToSwitch(self.__dxdydz.z, self.__desiredCamDist, self._cfg['distRange'][0], self._cfg['distRange'][1], self._cfg['transitionDist']):
            self.__onChangeControlMode(*self.__switchers.getSwitchParams())
        if not self.__transitionEnabled and self.__desiredCamDist - TRANSITION_DIST_HYSTERESIS <= self._cfg['transitionDist']:
            self.__transitionEnabled = True
            self.__enableSwitchers(False)
        if not self.__autoUpdatePosition:
            self.__dxdydz = Vector3(0, 0, 0)
        return 0.01

    def __updateOscillator(self, deltaTime):
        if ArtyCamera.isCameraDynamic():
            self.__positionOscillator.update(deltaTime)
            self.__positionNoiseOscillator.update(deltaTime)
        else:
            self.__positionOscillator.reset()
            self.__positionNoiseOscillator.reset()
        self.__cam.target.a = math_utils.createTranslationMatrix(self.__positionOscillator.deviation + self.__positionNoiseOscillator.deviation)

    def __switchersDistRange(self):
        distRange = self._cfg['distRange']
        if self.__switchers.isEnabled():
            distRange = self.__switchers.getDistLimitationForSwitch(distRange[0], distRange[1], self._cfg['transitionDist'])
        return distRange

    def _readConfigs(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <artyMode/camera> in avatar_input_handler.xml')
        super(ArtyCamera, self)._readConfigs(dataSec)
        dynamicSection = dataSec['dynamics']
        self.__dynamicCfg.readImpulsesConfig(dynamicSection)
        self.__positionOscillator = createOscillatorFromSection(dynamicSection['oscillator'], False)
        self.__positionNoiseOscillator = createOscillatorFromSection(dynamicSection['randomNoiseOscillatorFlat'])

    def _readBaseCfg(self, dataSec):
        bcfg = self._baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.005, 10.0, 0.025)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.005, 10.0, 0.025)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.005, 10.0, 0.025)
        bcfg['angularSpeed'] = readFloat(dataSec, 'angularSpeed', pi / 720.0, pi / 0.5, pi / 360.0)
        bcfg['distRange'] = readVec2(dataSec, 'distRange', (1.0, 1.0), (10000.0, 10000.0), (2.0, 30.0))
        bcfg['transitionDist'] = readFloat(dataSec, 'transitionDist', 1.0, 10000.0, 60.0)
        bcfg['minimalPitch'] = readFloat(dataSec, 'minimalPitch', pi / 36.0, pi / 3.0, pi / 18.0)
        bcfg['maximalPitch'] = readFloat(dataSec, 'maximalPitch', pi / 6.0, pi / 3.0, pi / 3.5)
        bcfg['interpolationSpeed'] = readFloat(dataSec, 'interpolationSpeed', 0.0, 100.0, 5.0)
        bcfg['distInterpolationSpeed'] = readFloat(dataSec, 'distInterpolationSpeed', 0.0, 10.0, 5.0)
        bcfg['highPitchThreshold'] = readFloat(dataSec, 'highPitchThreshold', 0.1, 10.0, 3.0)
        bcfg['hTimeThreshold'] = readFloat(dataSec, 'hysteresis/timeThreshold', 0.0, 10.0, 0.5)
        bcfg['hPositionThreshold'] = readFloat(dataSec, 'hysteresis/positionThreshold', 0.0, 100.0, 7.0)
        bcfg['scrollSmoothingTime'] = readFloat(dataSec, 'scrollSmoothingTime', 0.0, 1.0, 0.3)

    def _readUserCfg(self):
        ucfg = self._userCfg
        dataSec = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if dataSec is not None:
            dataSec = dataSec['artyMode/camera']
        ucfg['horzInvert'] = False
        ucfg['vertInvert'] = False
        ucfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.0, 10.0, 1.0)
        ucfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['camDist'] = readFloat(dataSec, 'camDist', 0.0, 60.0, 0.0)
        return

    def _makeCfg(self):
        bcfg = self._baseCfg
        ucfg = self._userCfg
        cfg = self._cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['distRange'] = bcfg['distRange']
        cfg['transitionDist'] = bcfg['transitionDist']
        cfg['angularSpeed'] = bcfg['angularSpeed']
        cfg['minimalPitch'] = bcfg['minimalPitch']
        cfg['maximalPitch'] = bcfg['maximalPitch']
        cfg['interpolationSpeed'] = bcfg['interpolationSpeed']
        cfg['distInterpolationSpeed'] = bcfg['distInterpolationSpeed']
        cfg['highPitchThresholdSq'] = bcfg['highPitchThreshold'] * bcfg['highPitchThreshold']
        cfg['hTimeThreshold'] = bcfg['hTimeThreshold']
        cfg['hPositionThresholdSq'] = bcfg['hPositionThreshold'] * bcfg['hPositionThreshold']
        cfg['scrollSmoothingTime'] = bcfg['scrollSmoothingTime']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        cfg['camDist'] = ucfg['camDist']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']

    def _handleSettingsChange(self, diff):
        super(ArtyCamera, self)._handleSettingsChange(diff)
        if SPGAim.AUTO_CHANGE_AIM_MODE in diff:
            self.__enableSwitchers()
        if GAME.SCROLL_SMOOTHING in diff:
            self.__scrollSmoother.setIsEnabled(self.settingsCore.getSetting(GAME.SCROLL_SMOOTHING))

    def _updateSettingsFromServer(self):
        super(ArtyCamera, self)._updateSettingsFromServer()
        if self.settingsCore.isReady:
            self.__enableSwitchers()
            self.__scrollSmoother.setIsEnabled(self.settingsCore.getSetting(GAME.SCROLL_SMOOTHING))

    def __enableSwitchers(self, updateTransitionEnabled=True):
        if updateTransitionEnabled and self.__desiredCamDist - TRANSITION_DIST_HYSTERESIS >= self._cfg['transitionDist']:
            self.__transitionEnabled = False
        if self.settingsCore.isReady:
            self.__switchers.setIsEnabled(self.settingsCore.getSetting(SPGAim.AUTO_CHANGE_AIM_MODE) and self.__transitionEnabled)
