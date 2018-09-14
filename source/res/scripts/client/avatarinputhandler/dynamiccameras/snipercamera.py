# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/SniperCamera.py
import BigWorld
import Math
from Math import Vector2, Vector3, Matrix
import math
import random
import weakref
from AvatarInputHandler import mathUtils, DynamicCameras, AimingSystems, cameras
from AvatarInputHandler.DynamicCameras import createCrosshairMatrix, createOscillatorFromSection, AccelerationSmoother
from AvatarInputHandler.AimingSystems.SniperAimingSystem import SniperAimingSystem
from helpers.CallbackDelayer import CallbackDelayer
from AvatarInputHandler.Oscillator import Oscillator
from AvatarInputHandler.cameras import ICamera, readFloat, readVec3, readBool, ImpulseReason, FovExtended
import BattleReplay
import Settings
import constants
from debug_utils import LOG_WARNING, LOG_DEBUG
from AvatarInputHandler.DynamicCameras import CameraDynamicConfig

def getCameraAsSettingsHolder(settingsDataSec):
    return SniperCamera(settingsDataSec, None, None)


class SniperCamera(ICamera, CallbackDelayer):
    _DYNAMIC_ENABLED = True

    @staticmethod
    def enableDynamicCamera(enable):
        SniperCamera._DYNAMIC_ENABLED = enable

    @staticmethod
    def isCameraDynamic():
        return SniperCamera._DYNAMIC_ENABLED

    _FILTER_LENGTH = 5
    _DEFAULT_MAX_ACCELERATION_DURATION = 1.5
    _MIN_REL_SPEED_ACC_SMOOTHING = 0.7
    camera = property(lambda self: self.__cam)
    aimingSystem = property(lambda self: self.__aimingSystem)

    def __init__(self, dataSec, aim, binoculars):
        CallbackDelayer.__init__(self)
        self.__impulseOscillator = None
        self.__movementOscillator = None
        self.__noiseOscillator = None
        self.__dynamicCfg = CameraDynamicConfig()
        self.__accelerationSmoother = None
        self.__readCfg(dataSec)
        if aim is None or binoculars is None:
            return
        else:
            self.__cam = BigWorld.FreeCamera()
            self.__zoom = self.__cfg['zoom']
            self.__curSense = 0
            self.__curScrollSense = 0
            self.__waitVehicleCallbackId = None
            self.__onChangeControlMode = None
            self.__aimingSystem = SniperAimingSystem(dataSec)
            self.__aim = weakref.proxy(aim)
            self.__binoculars = binoculars
            self.__defaultAimOffset = self.__aim.offset()
            self.__defaultAimOffset = (self.__defaultAimOffset[0], self.__defaultAimOffset[1])
            self.__crosshairMatrix = createCrosshairMatrix(offsetFromNearPlane=self.__dynamicCfg['aimMarkerDistance'])
            self.__prevTime = BigWorld.time()
            self.__autoUpdateDxDyDz = Vector3(0, 0, 0)
            return

    def create(self, onChangeControlMode = None):
        self.__onChangeControlMode = onChangeControlMode

    def destroy(self):
        self.disable()
        self.__onChangeControlMode = None
        self.__cam = None
        self._writeUserPreferences()
        self.__aimingSystem.destroy()
        self.__aimingSystem = None
        self.__aim = None
        CallbackDelayer.destroy(self)
        return

    def enable(self, targetPos, saveZoom):
        self.__prevTime = BigWorld.time()
        player = BigWorld.player()
        if saveZoom:
            self.__zoom = self.__cfg['zoom']
        else:
            self.__cfg['zoom'] = self.__zoom = self.__cfg['zooms'][0]
        self.__applyZoom(self.__zoom)
        self.__setupCamera(targetPos)
        vehicle = BigWorld.entity(player.playerVehicleID)
        if self.__waitVehicleCallbackId is not None:
            BigWorld.cancelCallback(self.__waitVehicleCallbackId)
        if vehicle is None:
            self.__whiteVehicleCallbackId = BigWorld.callback(0.1, self.__waitVehicle)
        else:
            self.__showVehicle(False)
        BigWorld.camera(self.__cam)
        if self.__cameraUpdate(False) >= 0.0:
            self.delayCallback(0.0, self.__cameraUpdate)
        return

    def disable(self):
        BigWorld.camera(None)
        if self.__waitVehicleCallbackId is not None:
            BigWorld.cancelCallback(self.__waitVehicleCallbackId)
            self.__waitVehicleCallbackId = None
        self.__showVehicle(True)
        self.stopCallback(self.__cameraUpdate)
        self.__aimingSystem.disable()
        self.__movementOscillator.reset()
        self.__impulseOscillator.reset()
        self.__noiseOscillator.reset()
        self.__accelerationSmoother.reset()
        self.__autoUpdateDxDyDz.set(0)
        FovExtended.instance().resetFov()
        return

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

    def update(self, dx, dy, dz, updatedByKeyboard = False):
        self.__curSense = self.__cfg['keySensitivity'] if updatedByKeyboard else self.__cfg['sensitivity']
        self.__curScrollSense = self.__cfg['keySensitivity'] if updatedByKeyboard else self.__cfg['scrollSensitivity']
        self.__curSense *= 1.0 / self.__zoom
        if updatedByKeyboard:
            self.__autoUpdateDxDyDz.set(dx, dy, dz)
        else:
            self.__autoUpdateDxDyDz.set(0, 0, 0)
            self.__rotateAndZoom(dx, dy, dz)

    def onRecreateDevice(self):
        self.__applyZoom(self.__zoom)

    def applyImpulse(self, position, impulse, reason = ImpulseReason.ME_HIT):
        adjustedImpulse, noiseMagnitude = self.__dynamicCfg.adjustImpulse(impulse, reason)
        camMatrix = Matrix(self.__cam.matrix)
        impulseLocal = camMatrix.applyVector(adjustedImpulse)
        impulseAsYPR = Vector3(impulseLocal.x, -impulseLocal.y + impulseLocal.z, 0)
        rollPart = self.__dynamicCfg['impulsePartToRoll']
        impulseAsYPR.z = -rollPart * impulseAsYPR.x
        impulseAsYPR.x *= 1 - rollPart
        self.__impulseOscillator.applyImpulse(impulseAsYPR)
        self.__applyNoiseImpulse(noiseMagnitude)

    def applyDistantImpulse(self, position, impulseValue, reason = ImpulseReason.ME_HIT):
        impulse = self.__cam.position - position
        distance = impulse.length
        if distance < 1.0:
            distance = 1.0
        impulse.normalise()
        if reason == ImpulseReason.OTHER_SHOT and distance <= self.__dynamicCfg['maxShotImpulseDistance']:
            impulse *= impulseValue / distance
        elif reason == ImpulseReason.SPLASH or reason == ImpulseReason.HE_EXPLOSION:
            impulse *= impulseValue / distance
        elif reason == ImpulseReason.VEHICLE_EXPLOSION and distance <= self.__dynamicCfg['maxExplosionImpulseDistance']:
            impulse *= impulseValue / distance
        else:
            return
        self.applyImpulse(position, impulse, reason)

    def __applyNoiseImpulse(self, noiseMagnitude):
        noiseImpulse = mathUtils.RandomVectors.random3(noiseMagnitude)
        self.__noiseOscillator.applyImpulse(noiseImpulse)

    def __rotateAndZoom(self, dx, dy, dz):
        self.__aimingSystem.handleMovement(*self.__calcYawPitchDelta(dx, dy))
        self.__setupZoom(dz)

    def __calcYawPitchDelta(self, dx, dy):
        return (dx * self.__curSense * (-1 if self.__cfg['horzInvert'] else 1), dy * self.__curSense * (-1 if self.__cfg['vertInvert'] else 1))

    def __showVehicle(self, show):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is not None:
            vehicle.show(show)
        return

    def __setupCamera(self, targetPos):
        self.__aimingSystem.enable(targetPos)

    def __waitVehicle(self):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            self.__waitVehicleCallbackId = None
        else:
            self.__waitVehicleCallbackId = BigWorld.callback(0.1, self.__waitVehicle)
            return
        self.__showVehicle(False)
        return

    def __applyZoom(self, zoomFactor):
        FovExtended.instance().setFovByMultiplier(1 / zoomFactor)

    def __setupZoom(self, dz):
        if dz == 0:
            return
        else:
            zooms = self.__cfg['zooms']
            prevZoom = self.__zoom
            if self.__zoom == zooms[0] and dz < 0 and self.__onChangeControlMode is not None:
                self.__onChangeControlMode(True)
            if dz > 0:
                for elem in zooms:
                    if self.__zoom < elem:
                        self.__zoom = elem
                        self.__cfg['zoom'] = self.__zoom
                        break

            elif dz < 0:
                for i in range(len(zooms) - 1, -1, -1):
                    if self.__zoom > zooms[i]:
                        self.__zoom = zooms[i]
                        self.__cfg['zoom'] = self.__zoom
                        break

            if prevZoom != self.__zoom:
                self.__applyZoom(self.__zoom)
            return

    def __cameraUpdate(self, allowModeChange = True):
        curTime = BigWorld.time()
        deltaTime = curTime - self.__prevTime
        self.__prevTime = curTime
        if not self.__autoUpdateDxDyDz.x == self.__autoUpdateDxDyDz.y == self.__autoUpdateDxDyDz.z == 0.0:
            self.__rotateAndZoom(self.__autoUpdateDxDyDz.x, self.__autoUpdateDxDyDz.y, self.__autoUpdateDxDyDz.z)
        self.__aimingSystem.update(deltaTime)
        localTransform, impulseTransform = self.__updateOscillators(deltaTime)
        aimMatrix = cameras.getAimMatrix(*self.__defaultAimOffset)
        camMat = Matrix(aimMatrix)
        rodMat = mathUtils.createTranslationMatrix(-self.__dynamicCfg['pivotShift'])
        antiRodMat = mathUtils.createTranslationMatrix(self.__dynamicCfg['pivotShift'])
        camMat.postMultiply(rodMat)
        camMat.postMultiply(localTransform)
        camMat.postMultiply(antiRodMat)
        camMat.postMultiply(self.__aimingSystem.matrix)
        camMat.invert()
        self.__cam.set(camMat)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            aimOffset = replayCtrl.getAimClipPosition()
            binocularsOffset = aimOffset
        else:
            aimOffset = self.__calcAimOffset(impulseTransform)
            binocularsOffset = self.__calcAimOffset()
            if replayCtrl.isRecording:
                replayCtrl.setAimClipPosition(aimOffset)
        self.__aim.offset(aimOffset)
        self.__binoculars.setMaskCenter(binocularsOffset.x, binocularsOffset.y)
        player = BigWorld.player()
        if allowModeChange and (self.__isPositionUnderwater(self.__aimingSystem.matrix.translation) or player.isGunLocked):
            self.__onChangeControlMode(False)
            return -1
        return 0.0

    def __calcAimOffset(self, aimLocalTransform = None):
        worldCrosshair = Matrix(self.__crosshairMatrix)
        aimingSystemMatrix = self.__aimingSystem.matrix
        if aimLocalTransform is not None:
            worldCrosshair.postMultiply(aimLocalTransform)
        worldCrosshair.postMultiply(aimingSystemMatrix)
        aimOffset = cameras.projectPoint(worldCrosshair.translation)
        return Vector2(mathUtils.clamp(-0.95, 0.95, aimOffset.x), mathUtils.clamp(-0.95, 0.95, aimOffset.y))

    def __calcCurOscillatorAcceleration(self, deltaTime):
        vehicle = BigWorld.player().vehicle
        if vehicle is None or not vehicle.isAlive():
            return Vector3(0, 0, 0)
        else:
            curVelocity = vehicle.filter.velocity
            relativeSpeed = curVelocity.length / vehicle.typeDescriptor.physics['speedLimits'][0]
            if relativeSpeed >= SniperCamera._MIN_REL_SPEED_ACC_SMOOTHING:
                self.__accelerationSmoother.maxAllowedAcceleration = self.__dynamicCfg['accelerationThreshold']
            else:
                self.__accelerationSmoother.maxAllowedAcceleration = self.__dynamicCfg['accelerationMax']
            acceleration = self.__accelerationSmoother.update(vehicle, deltaTime)
            camMat = Matrix(self.__cam.matrix)
            acceleration = camMat.applyVector(-acceleration)
            accelSensitivity = self.__dynamicCfg['accelerationSensitivity']
            acceleration.x *= accelSensitivity.x
            acceleration.y *= accelSensitivity.y
            acceleration.z *= accelSensitivity.z
            oscillatorAcceleration = Vector3(0, -acceleration.y + acceleration.z, -acceleration.x)
            return oscillatorAcceleration

    def __updateOscillators(self, deltaTime):
        if not SniperCamera.isCameraDynamic():
            self.__impulseOscillator.reset()
            self.__movementOscillator.reset()
            self.__noiseOscillator.reset()
            return (mathUtils.createRotationMatrix(Vector3(0, 0, 0)), mathUtils.createRotationMatrix(Vector3(0, 0, 0)))
        oscillatorAcceleration = self.__calcCurOscillatorAcceleration(deltaTime)
        self.__movementOscillator.externalForce += oscillatorAcceleration
        self.__impulseOscillator.update(deltaTime)
        self.__movementOscillator.update(deltaTime)
        self.__noiseOscillator.update(deltaTime)
        noiseDeviation = Vector3(self.__noiseOscillator.deviation)
        deviation = self.__impulseOscillator.deviation + self.__movementOscillator.deviation + noiseDeviation
        oscVelocity = self.__impulseOscillator.velocity + self.__movementOscillator.velocity + self.__noiseOscillator.velocity
        if abs(deviation.x) < 1e-05 and abs(oscVelocity.x) < 0.0001:
            deviation.x = 0
        if abs(deviation.y) < 1e-05 and abs(oscVelocity.y) < 0.0001:
            deviation.y = 0
        if abs(deviation.z) < 1e-05 and abs(oscVelocity.z) < 0.0001:
            deviation.z = 0
        curZoomIdx = 0
        zooms = self.__cfg['zooms']
        for idx in xrange(len(zooms)):
            if self.__zoom == zooms[idx]:
                curZoomIdx = idx
                break

        zoomExposure = self.__zoom * self.__dynamicCfg['zoomExposure'][curZoomIdx]
        deviation /= zoomExposure
        impulseDeviation = (self.__impulseOscillator.deviation + noiseDeviation) / zoomExposure
        self.__impulseOscillator.externalForce.set(0, 0, 0)
        self.__movementOscillator.externalForce.set(0, 0, 0)
        self.__noiseOscillator.externalForce.set(0, 0, 0)
        return (mathUtils.createRotationMatrix(Vector3(deviation.x, deviation.y, deviation.z)), mathUtils.createRotationMatrix(impulseDeviation))

    def __isPositionUnderwater(self, position):
        return BigWorld.wg_collideWater(position, position + Vector3(0, 1, 0), False) > -1.0

    def reload(self):
        if not constants.IS_DEVELOPMENT:
            return
        import ResMgr
        ResMgr.purge('gui/avatar_input_handler.xml')
        cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/sniperMode/camera/')
        self.__readCfg(cameraSec)

    def __readCfg(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <sniperMode/camera> in avatar_input_handler.xml')
        self.__baseCfg = dict()
        bcfg = self.__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0, 10, 0.005)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0, 10, 0.005)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0, 10, 0.005)
        zooms = readVec3(dataSec, 'zooms', (0, 0, 0), (10, 10, 10), (2, 4, 8))
        bcfg['zooms'] = [zooms.x, zooms.y, zooms.z]
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['sniperMode/camera']
        self.__userCfg = dict()
        ucfg = self.__userCfg
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        ucfg['horzInvert'] = g_settingsCore.getSetting('mouseHorzInvert')
        ucfg['vertInvert'] = g_settingsCore.getSetting('mouseVertInvert')
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0.0, 10.0, 1.0)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['zoom'] = readFloat(ds, 'zoom', 0.0, 10.0, bcfg['zooms'][0])
        self.__cfg = dict()
        cfg = self.__cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['zooms'] = bcfg['zooms']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        cfg['zoom'] = ucfg['zoom']
        dynamicsSection = dataSec['dynamics']
        self.__impulseOscillator = createOscillatorFromSection(dynamicsSection['impulseOscillator'])
        self.__movementOscillator = createOscillatorFromSection(dynamicsSection['movementOscillator'])
        self.__noiseOscillator = createOscillatorFromSection(dynamicsSection['randomNoiseOscillatorSpherical'])
        self.__dynamicCfg.readImpulsesConfig(dynamicsSection)
        self.__dynamicCfg['accelerationSensitivity'] = readVec3(dynamicsSection, 'accelerationSensitivity', (-1000, -1000, -1000), (1000, 1000, 1000), (0.5, 0.5, 0.5))
        accelerationThreshold = readFloat(dynamicsSection, 'accelerationThreshold', 0.0, 1000.0, 0.1)
        self.__dynamicCfg['accelerationThreshold'] = accelerationThreshold
        self.__dynamicCfg['accelerationMax'] = readFloat(dynamicsSection, 'accelerationMax', 0.0, 1000.0, 0.1)
        self.__dynamicCfg['maxShotImpulseDistance'] = readFloat(dynamicsSection, 'maxShotImpulseDistance', 0.0, 1000.0, 10.0)
        self.__dynamicCfg['maxExplosionImpulseDistance'] = readFloat(dynamicsSection, 'maxExplosionImpulseDistance', 0.0, 1000.0, 10.0)
        self.__dynamicCfg['impulsePartToRoll'] = readFloat(dynamicsSection, 'impulsePartToRoll', 0.0, 1000.0, 0.3)
        self.__dynamicCfg['pivotShift'] = Vector3(0, readFloat(dynamicsSection, 'pivotShift', -1000, 1000, -0.5), 0)
        self.__dynamicCfg['aimMarkerDistance'] = readFloat(dynamicsSection, 'aimMarkerDistance', -1000, 1000, 1.0)
        self.__dynamicCfg['zoomExposure'] = readVec3(dynamicsSection, 'zoomExposure', (0.1, 0.1, 0.1), (10, 10, 10), (0.5, 0.5, 0.5))
        accelerationFilter = mathUtils.RangeFilter(self.__dynamicCfg['accelerationThreshold'], self.__dynamicCfg['accelerationMax'], 100, mathUtils.SMAFilter(SniperCamera._FILTER_LENGTH))
        maxAccelerationDuration = readFloat(dynamicsSection, 'maxAccelerationDuration', 0.0, 10000.0, SniperCamera._DEFAULT_MAX_ACCELERATION_DURATION)
        self.__accelerationSmoother = AccelerationSmoother(accelerationFilter, maxAccelerationDuration)
        return

    def _writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self.__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('sniperMode/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('sniperMode/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('sniperMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('sniperMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('sniperMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('sniperMode/camera/zoom', self.__cfg['zoom'])
