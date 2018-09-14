# Source Generated with Gray Magic
# File: strategiccamera.pyc (Python 2.7)

import BigWorld
import Math
from Math import Vector2, Vector3, Matrix
from _functools import partial
import math
import random
from AvatarInputHandler import mathUtils, cameras
from AvatarInputHandler.AimingSystems.StrategicAimingSystem import StrategicAimingSystem
from AvatarInputHandler.CallbackDelayer import CallbackDelayer
from AvatarInputHandler.DynamicCameras import createOscillatorFromSection, CameraDynamicConfig
from AvatarInputHandler.Oscillator import Oscillator
from AvatarInputHandler.cameras import ICamera, getWorldRayAndPoint, readFloat, readBool, readVec2, ImpulseReason, readVec3, FovExtended
import BattleReplay
from ClientArena import Plane
import Settings
import constants
from debug_utils import LOG_WARNING, LOG_ERROR

def getCameraAsSettingsHolder(settingsDataSec):
    return StrategicCamera(settingsDataSec, None)


class StrategicCamera(ICamera, CallbackDelayer):
    _CAMERA_YAW = 0
    _DYNAMIC_ENABLED = True
    ABSOLUTE_VERTICAL_FOV = math.radians(60)
    
    def enableDynamicCamera(enable):
        StrategicCamera._DYNAMIC_ENABLED = enable

    enableDynamicCamera = staticmethod(enableDynamicCamera)
    
    def isCameraDynamic():
        return StrategicCamera._DYNAMIC_ENABLED

    isCameraDynamic = staticmethod(isCameraDynamic)
    camera = property(lambda self: self._StrategicCamera__cam)
    aimingSystem = property(lambda self: self._StrategicCamera__aimingSystem)
    
    def __init__(self, dataSec, aim):
        CallbackDelayer.__init__(self)
        self._StrategicCamera__positionOscillator = None
        self._StrategicCamera__positionNoiseOscillator = None
        self._StrategicCamera__dynamicCfg = CameraDynamicConfig()
        self._StrategicCamera__readCfg(dataSec)
        if aim is None:
            return None
        self._StrategicCamera__cam = None.CursorCamera()
        self._StrategicCamera__curSense = self._StrategicCamera__cfg['sensitivity']
        self._StrategicCamera__onChangeControlMode = None
        self._StrategicCamera__aimingSystem = StrategicAimingSystem(self._StrategicCamera__cfg['distRange'][0], StrategicCamera._CAMERA_YAW)
        self._StrategicCamera__prevTime = BigWorld.time()
        self._StrategicCamera__aim = aim
        self._StrategicCamera__autoUpdatePosition = False
        self._StrategicCamera__dxdydz = Vector3(0, 0, 0)
        self._StrategicCamera__needReset = 0

    
    def create(self, onChangeControlMode = None):
        self._StrategicCamera__onChangeControlMode = onChangeControlMode
        self._StrategicCamera__camDist = self._StrategicCamera__cfg['camDist']
        self._StrategicCamera__cam.pivotMaxDist = 0
        self._StrategicCamera__cam.maxDistHalfLife = 0.01
        self._StrategicCamera__cam.movementHalfLife = 0
        self._StrategicCamera__cam.turningHalfLife = -1
        self._StrategicCamera__cam.pivotPosition = Math.Vector3(0, self._StrategicCamera__camDist, 0)

    
    def destroy(self):
        CallbackDelayer.destroy(self)
        self.disable()
        self._StrategicCamera__onChangeControlMode = None
        self._StrategicCamera__cam = None
        self._writeUserPreferences()
        self._StrategicCamera__aimingSystem.destroy()
        self._StrategicCamera__aimingSystem = None

    
    def enable(self, targetPos, saveDist):
        self._StrategicCamera__prevTime = BigWorld.time()
        self._StrategicCamera__aimingSystem.enable(targetPos)
        srcMat = mathUtils.createRotationMatrix((0, -(math.pi) * 0.499, 0))
        self._StrategicCamera__cam.source = srcMat
        if not saveDist:
            self._StrategicCamera__camDist = self._StrategicCamera__cfg['camDist']
        self._StrategicCamera__cam.pivotPosition = Math.Vector3(0, self._StrategicCamera__camDist, 0)
        camTarget = Math.MatrixProduct()
        camTarget.b = self._StrategicCamera__aimingSystem.matrix
        self._StrategicCamera__cam.target = camTarget
        BigWorld.camera(self._StrategicCamera__cam)
        BigWorld.player().positionControl.moveTo(self._StrategicCamera__aimingSystem.matrix.translation)
        BigWorld.player().positionControl.followCamera(True)
        FovExtended.instance().enabled = False
        BigWorld.projection().fov = StrategicCamera.ABSOLUTE_VERTICAL_FOV
        self._StrategicCamera__cameraUpdate()
        self.delayCallback(0, self._StrategicCamera__cameraUpdate)
        self._StrategicCamera__needReset = 1

    
    def disable(self):
        self._StrategicCamera__aimingSystem.disable()
        self.stopCallback(self._StrategicCamera__cameraUpdate)
        BigWorld.camera(None)
        BigWorld.player().positionControl.followCamera(False)
        self._StrategicCamera__positionOscillator.reset()
        FovExtended.instance().resetFov()
        FovExtended.instance().enabled = True

    
    def teleport(self, pos):
        self.moveToPosition(pos)

    
    def restoreDefaultsState(self):
        LOG_ERROR('StrategiCamera::restoreDefaultState is obsolete!')
        return None
        vPos = BigWorld.player().getOwnVehiclePosition()
        self._StrategicCamera__camDist = self._StrategicCamera__cfg['camDist']
        self._StrategicCamera__cam.pivotMaxDist = 0
        self._StrategicCamera__cam.maxDistHalfLife = 0.01
        self._StrategicCamera__cam.movementHalfLife = 0
        self._StrategicCamera__cam.turningHalfLife = 0.01
        self._StrategicCamera__cam.pivotPosition = Math.Vector3(0, self._StrategicCamera__camDist, 0)
        self._StrategicCamera__cam.target = trgMat
        BigWorld.player().positionControl.moveTo(self._StrategicCamera__totalMove)

    
    def getUserConfigValue(self, name):
        return self._StrategicCamera__userCfg.get(name)

    
    def setUserConfigValue(self, name, value):
        if name not in self._StrategicCamera__userCfg:
            return None
        self._StrategicCamera__userCfg[name] = None
        if name not in ('keySensitivity', 'sensitivity', 'scrollSensitivity'):
            self._StrategicCamera__cfg[name] = self._StrategicCamera__userCfg[name]
        else:
            self._StrategicCamera__cfg[name] = self._StrategicCamera__baseCfg[name] * self._StrategicCamera__userCfg[name]

    
    def update(self, dx, dy, dz, updatedByKeyboard = False):
        if updatedByKeyboard:
            pass
        self._StrategicCamera__curSense = self._StrategicCamera__cfg['sensitivity']
        self._StrategicCamera__autoUpdatePosition = updatedByKeyboard
        self._StrategicCamera__dxdydz = Vector3(dx, dy, dz)

    
    def moveToPosition(self, pos):
        self._StrategicCamera__aimingSystem.enable(pos)
        self.update(0, 0, 0)

    
    def calcVisibleAreaRatio(self):
        points = [
            Math.Vector2(1, 1),
            Math.Vector2(1, -1),
            Math.Vector2(-1, -1),
            Math.Vector2(-1, 1)]
        continue
        dirsPos = [ getWorldRayAndPoint(point.x, point.y) for point in points ]
        planeXZ = Plane(Math.Vector3(0, 1, 0), 0)
        collisionPoints = []
        for (dir, begPos) in dirsPos:
            endPos = begPos + dir * 1000
            testResult = BigWorld.wg_collideSegment(BigWorld.player().spaceID, begPos, endPos, 3)
            collPoint = Math.Vector3(0, 0, 0)
            if collPoint is not None:
                collPoint = testResult[0]
            else:
                collPoint = planeXZ.intersectSegment(begPos, endPos)
            collisionPoints.append(collPoint)
        
        x0 = abs(collisionPoints[1].x - collisionPoints[2].x)
        x1 = abs(collisionPoints[0].x - collisionPoints[3].x)
        z0 = abs(collisionPoints[0].z - collisionPoints[1].z)
        z1 = abs(collisionPoints[3].z - collisionPoints[2].z)
        bb = BigWorld.player().arena.arenaType.boundingBox
        arenaBottomLeft = bb[0]
        arenaUpperRight = bb[1]
        arenaX = arenaUpperRight[0] - arenaBottomLeft[0]
        arenaZ = arenaUpperRight[1] - arenaBottomLeft[1]
        return ((x0 + x1) * 0.5 / arenaX, (z0 + z1) * 0.5 / arenaZ)

    
    def applyImpulse(self, position, impulse, reason = ImpulseReason.ME_HIT):
        (adjustedImpulse, noiseMagnitude) = self._StrategicCamera__dynamicCfg.adjustImpulse(impulse, reason)
        impulseFlatDir = Vector3(adjustedImpulse.x, 0, adjustedImpulse.z)
        impulseFlatDir.normalise()
        cameraYawMat = mathUtils.createRotationMatrix(Vector3(-(StrategicCamera._CAMERA_YAW), 0, 0))
        impulseLocal = cameraYawMat.applyVector(impulseFlatDir * -1 * adjustedImpulse.length)
        self._StrategicCamera__positionOscillator.applyImpulse(impulseLocal)
        self._StrategicCamera__applyNoiseImpulse(noiseMagnitude)

    
    def applyDistantImpulse(self, position, impulseValue, reason = ImpulseReason.ME_HIT):
        if reason != ImpulseReason.SPLASH and reason != ImpulseReason.PROJECTILE_HIT:
            return None
        impulse = None.player().getOwnVehiclePosition() - position
        distance = impulse.length
        if distance <= 1:
            distance = 1
        impulse.normalise()
        if reason == ImpulseReason.PROJECTILE_HIT:
            if not cameras.isPointOnScreen(position):
                return None
            distance = None
        impulse *= impulseValue / distance
        self.applyImpulse(position, impulse, reason)

    
    def _StrategicCamera__applyNoiseImpulse(self, noiseMagnitude):
        noiseImpulse = mathUtils.RandomVectors.random3Flat(noiseMagnitude)
        self._StrategicCamera__positionNoiseOscillator.applyImpulse(noiseImpulse)

    
    def _writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self._StrategicCamera__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeFloat('strategicMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('strategicMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('strategicMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('strategicMode/camera/camDist', self._StrategicCamera__cfg['camDist'])

    
    def _StrategicCamera__cameraUpdate(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            aimOffset = replayCtrl.getAimClipPosition()
        else:
            aimOffset = self._StrategicCamera__calcAimOffset()
            if replayCtrl.isRecording:
                replayCtrl.setAimClipPosition(aimOffset)
        self._StrategicCamera__aim.offset((aimOffset.x, aimOffset.y))
        shotDescr = BigWorld.player().vehicleTypeDescriptor.shot
        BigWorld.wg_trajectory_drawer().setParams(shotDescr['maxDistance'], Math.Vector3(0, -shotDescr['gravity'], 0), self._StrategicCamera__aim.offset())
        curTime = BigWorld.time()
        deltaTime = curTime - self._StrategicCamera__prevTime
        self._StrategicCamera__prevTime = curTime
        if replayCtrl.isPlaying:
            if self._StrategicCamera__needReset != 0:
                if self._StrategicCamera__needReset > 1:
                    isPlayerAvatar = isPlayerAvatar
                    import helpers
                    player = BigWorld.player()
                    if isPlayerAvatar() and player.inputHandler.ctrl is not None:
                        player.inputHandler.ctrl.resetGunMarkers()
                    
                self._StrategicCamera__needReset = 0
            else:
                self._StrategicCamera__needReset += 1
        if replayCtrl.isControllingCamera:
            self._StrategicCamera__aimingSystem.updateTargetPos(replayCtrl.getGunRotatorTargetPoint())
        else:
            self._StrategicCamera__aimingSystem.handleMovement(self._StrategicCamera__dxdydz.x * self._StrategicCamera__curSense, -(self._StrategicCamera__dxdydz.y) * self._StrategicCamera__curSense)
            if self._StrategicCamera__dxdydz.x != 0 and self._StrategicCamera__dxdydz.y != 0 or self._StrategicCamera__dxdydz.z != 0:
                self._StrategicCamera__needReset = 2
            
        self._StrategicCamera__aimingSystem.handleMovement(self._StrategicCamera__dxdydz.x * self._StrategicCamera__curSense, -(self._StrategicCamera__dxdydz.y) * self._StrategicCamera__curSense)
        distRange = self._StrategicCamera__cfg['distRange']
        self._StrategicCamera__camDist -= self._StrategicCamera__dxdydz.z * float(self._StrategicCamera__curSense)
        maxPivotHeight = distRange[1] - distRange[0]
        self._StrategicCamera__camDist = mathUtils.clamp(0, maxPivotHeight, self._StrategicCamera__camDist)
        self._StrategicCamera__cfg['camDist'] = self._StrategicCamera__camDist
        self._StrategicCamera__cam.pivotPosition = Math.Vector3(0, self._StrategicCamera__camDist, 0)
        if self._StrategicCamera__dxdydz.z != 0 and self._StrategicCamera__onChangeControlMode is not None and mathUtils.almostZero(self._StrategicCamera__camDist - maxPivotHeight):
            self._StrategicCamera__onChangeControlMode()
        self._StrategicCamera__updateOscillator(deltaTime)
        if not self._StrategicCamera__autoUpdatePosition:
            self._StrategicCamera__dxdydz = Vector3(0, 0, 0)
        return 0

    
    def _StrategicCamera__calcAimOffset(self):
        aimWorldPos = self._StrategicCamera__aimingSystem.matrix.applyPoint(Vector3(0, -(self._StrategicCamera__aimingSystem.height), 0))
        aimOffset = cameras.projectPoint(aimWorldPos)
        return Vector2(mathUtils.clamp(-0.95, 0.95, aimOffset.x), mathUtils.clamp(-0.95, 0.95, aimOffset.y))

    
    def _StrategicCamera__updateOscillator(self, deltaTime):
        if StrategicCamera.isCameraDynamic():
            self._StrategicCamera__positionOscillator.update(deltaTime)
            self._StrategicCamera__positionNoiseOscillator.update(deltaTime)
        else:
            self._StrategicCamera__positionOscillator.reset()
            self._StrategicCamera__positionNoiseOscillator.reset()
        self._StrategicCamera__cam.target.a = mathUtils.createTranslationMatrix(self._StrategicCamera__positionOscillator.deviation + self._StrategicCamera__positionNoiseOscillator.deviation)

    
    def reload(self):
        if not constants.IS_DEVELOPMENT:
            return None
        import ResMgr as ResMgr
        ResMgr.purge('gui/avatar_input_handler.xml')
        cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/strategicMode/camera/')
        self._StrategicCamera__readCfg(cameraSec)

    
    def _StrategicCamera__readCfg(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <strategicMode/camera> in avatar_input_handler.xml')
        self._StrategicCamera__baseCfg = dict()
        bcfg = self._StrategicCamera__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.005, 10, 0.025)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.005, 10, 0.025)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.005, 10, 0.025)
        bcfg['distRange'] = readVec2(dataSec, 'distRange', (1, 1), (10000, 10000), (2, 30))
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['strategicMode/camera']
        self._StrategicCamera__userCfg = dict()
        ucfg = self._StrategicCamera__userCfg
        g_settingsCore = g_settingsCore
        import account_helpers.settings_core.SettingsCore
        ucfg['horzInvert'] = g_settingsCore.getSetting('mouseHorzInvert')
        ucfg['vertInvert'] = g_settingsCore.getSetting('mouseVertInvert')
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0, 10, 1)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0, 10, 1)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0, 10, 1)
        ucfg['camDist'] = readFloat(ds, 'camDist', 0, 60, 0)
        self._StrategicCamera__cfg = dict()
        cfg = self._StrategicCamera__cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['distRange'] = bcfg['distRange']
        cfg['camDist'] = ucfg['camDist']
        cfg['keySensitivity'] *= ucfg['keySensitivity']
        cfg['sensitivity'] *= ucfg['sensitivity']
        cfg['scrollSensitivity'] *= ucfg['scrollSensitivity']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        dynamicsSection = dataSec['dynamics']
        self._StrategicCamera__dynamicCfg.readImpulsesConfig(dynamicsSection)
        self._StrategicCamera__positionOscillator = createOscillatorFromSection(dynamicsSection['oscillator'], False)
        self._StrategicCamera__positionNoiseOscillator = createOscillatorFromSection(dynamicsSection['randomNoiseOscillatorFlat'], False)



