# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/StrategicCamera.py
import BigWorld
import Math
from Math import Vector2, Vector3, Matrix
from _functools import partial
import math
import random
from AvatarInputHandler import mathUtils, cameras
from AvatarInputHandler.AimingSystems.StrategicAimingSystem import StrategicAimingSystem
from helpers.CallbackDelayer import CallbackDelayer
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
    _CAMERA_YAW = 0.0
    _DYNAMIC_ENABLED = True
    ABSOLUTE_VERTICAL_FOV = math.radians(60.0)

    @staticmethod
    def enableDynamicCamera(enable):
        StrategicCamera._DYNAMIC_ENABLED = enable

    @staticmethod
    def isCameraDynamic():
        return StrategicCamera._DYNAMIC_ENABLED

    camera = property(lambda self: self.__cam)
    aimingSystem = property(lambda self: self.__aimingSystem)

    def __init__(self, dataSec, aim):
        CallbackDelayer.__init__(self)
        self.__positionOscillator = None
        self.__positionNoiseOscillator = None
        self.__dynamicCfg = CameraDynamicConfig()
        self.__readCfg(dataSec)
        self.__cam = BigWorld.CursorCamera()
        self.__curSense = self.__cfg['sensitivity']
        self.__onChangeControlMode = None
        self.__aimingSystem = StrategicAimingSystem(self.__cfg['distRange'][0], StrategicCamera._CAMERA_YAW)
        self.__prevTime = BigWorld.time()
        self.__aimOffsetFunc = None
        if aim is None:
            self.__aimOffsetFunc = lambda x=None: (0, 0)
        else:
            self.__aimOffsetFunc = aim.offset
        self.__autoUpdatePosition = False
        self.__dxdydz = Vector3(0, 0, 0)
        self.__needReset = 0
        return

    def create(self, onChangeControlMode=None):
        self.__onChangeControlMode = onChangeControlMode
        self.__camDist = self.__cfg['camDist']
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = -1
        self.__cam.pivotPosition = Math.Vector3(0.0, self.__camDist, 0.0)

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
        self.__prevTime = BigWorld.time()
        self.__aimingSystem.enable(targetPos)
        srcMat = mathUtils.createRotationMatrix((0.0, -math.pi * 0.499, 0.0))
        self.__cam.source = srcMat
        if not saveDist:
            self.__camDist = self.__cfg['camDist']
        self.__cam.pivotPosition = Math.Vector3(0.0, self.__camDist, 0.0)
        camTarget = Math.MatrixProduct()
        camTarget.b = self.__aimingSystem.matrix
        self.__cam.target = camTarget
        BigWorld.camera(self.__cam)
        BigWorld.player().positionControl.moveTo(self.__aimingSystem.matrix.translation)
        BigWorld.player().positionControl.followCamera(True)
        FovExtended.instance().enabled = False
        BigWorld.projection().fov = StrategicCamera.ABSOLUTE_VERTICAL_FOV
        self.__cameraUpdate()
        self.delayCallback(0.0, self.__cameraUpdate)
        self.__needReset = 1

    def disable(self):
        self.__aimingSystem.disable()
        self.stopCallback(self.__cameraUpdate)
        BigWorld.camera(None)
        BigWorld.player().positionControl.followCamera(False)
        self.__positionOscillator.reset()
        FovExtended.instance().resetFov()
        FovExtended.instance().enabled = True
        return

    def teleport(self, pos):
        self.moveToPosition(pos)

    def setMaxDist(self):
        distRange = self.__cfg['distRange']
        if len(distRange) > 1:
            self.__camDist = distRange[1]

    def restoreDefaultsState(self):
        LOG_ERROR('StrategiCamera::restoreDefaultState is obsolete!')
        return None

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

    def update(self, dx, dy, dz, updatedByKeyboard=False):
        self.__curSense = self.__cfg['keySensitivity'] if updatedByKeyboard else self.__cfg['sensitivity']
        self.__autoUpdatePosition = updatedByKeyboard
        self.__dxdydz = Vector3(dx, dy, dz)

    def moveToPosition(self, pos):
        self.__aimingSystem.enable(pos)
        self.update(0.0, 0.0, 0.0)

    def calcVisibleAreaRatio(self):
        points = [Math.Vector2(1, 1),
         Math.Vector2(1, -1),
         Math.Vector2(-1, -1),
         Math.Vector2(-1, 1)]
        dirsPos = [ getWorldRayAndPoint(point.x, point.y) for point in points ]
        planeXZ = Plane(Math.Vector3(0, 1, 0), 0)
        collisionPoints = []
        for dir, begPos in dirsPos:
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

    def applyImpulse(self, position, impulse, reason=ImpulseReason.ME_HIT):
        adjustedImpulse, noiseMagnitude = self.__dynamicCfg.adjustImpulse(impulse, reason)
        impulseFlatDir = Vector3(adjustedImpulse.x, 0, adjustedImpulse.z)
        impulseFlatDir.normalise()
        cameraYawMat = mathUtils.createRotationMatrix(Vector3(-StrategicCamera._CAMERA_YAW, 0.0, 0.0))
        impulseLocal = cameraYawMat.applyVector(impulseFlatDir * (-1 * adjustedImpulse.length))
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

    def __applyNoiseImpulse(self, noiseMagnitude):
        noiseImpulse = mathUtils.RandomVectors.random3Flat(noiseMagnitude)
        self.__positionNoiseOscillator.applyImpulse(noiseImpulse)

    def writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self.__userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeFloat('strategicMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('strategicMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('strategicMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('strategicMode/camera/camDist', self.__cfg['camDist'])

    def __cameraUpdate(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            aimOffset = replayCtrl.getAimClipPosition()
        else:
            aimOffset = self.__calcAimOffset()
            if replayCtrl.isRecording:
                replayCtrl.setAimClipPosition(aimOffset)
        self.__aimOffsetFunc(aimOffset)
        shotDescr = BigWorld.player().vehicleTypeDescriptor.shot
        BigWorld.wg_trajectory_drawer().setParams(shotDescr['maxDistance'], Math.Vector3(0, -shotDescr['gravity'], 0), self.__aimOffsetFunc())
        curTime = BigWorld.time()
        deltaTime = curTime - self.__prevTime
        self.__prevTime = curTime
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
        distRange = self.__cfg['distRange']
        self.__camDist -= self.__dxdydz.z * float(self.__curSense)
        maxPivotHeight = distRange[1] - distRange[0]
        self.__camDist = mathUtils.clamp(0, maxPivotHeight, self.__camDist)
        self.__cfg['camDist'] = self.__camDist
        self.__cam.pivotPosition = Math.Vector3(0.0, self.__camDist, 0.0)
        if self.__dxdydz.z != 0 and self.__onChangeControlMode is not None and mathUtils.almostZero(self.__camDist - maxPivotHeight):
            self.__onChangeControlMode()
        self.__updateOscillator(deltaTime)
        if not self.__autoUpdatePosition:
            self.__dxdydz = Vector3(0, 0, 0)
        return 0.0

    def __calcAimOffset(self):
        aimWorldPos = self.__aimingSystem.matrix.applyPoint(Vector3(0, -self.__aimingSystem.height, 0))
        aimOffset = cameras.projectPoint(aimWorldPos)
        return Vector2(mathUtils.clamp(-0.95, 0.95, aimOffset.x), mathUtils.clamp(-0.95, 0.95, aimOffset.y))

    def __updateOscillator(self, deltaTime):
        if StrategicCamera.isCameraDynamic():
            self.__positionOscillator.update(deltaTime)
            self.__positionNoiseOscillator.update(deltaTime)
        else:
            self.__positionOscillator.reset()
            self.__positionNoiseOscillator.reset()
        self.__cam.target.a = mathUtils.createTranslationMatrix(self.__positionOscillator.deviation + self.__positionNoiseOscillator.deviation)

    def reload(self):
        if not constants.IS_DEVELOPMENT:
            return
        import ResMgr
        ResMgr.purge('gui/avatar_input_handler.xml')
        cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/strategicMode/camera/')
        self.__readCfg(cameraSec)

    def __readCfg(self, dataSec):
        if not dataSec:
            LOG_WARNING('Invalid section <strategicMode/camera> in avatar_input_handler.xml')
        self.__baseCfg = dict()
        bcfg = self.__baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.005, 10, 0.025)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.005, 10, 0.025)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.005, 10, 0.025)
        bcfg['distRange'] = readVec2(dataSec, 'distRange', (1, 1), (10000, 10000), (2, 30))
        ds = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if ds is not None:
            ds = ds['strategicMode/camera']
        self.__userCfg = dict()
        ucfg = self.__userCfg
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        ucfg['horzInvert'] = g_settingsCore.getSetting('mouseHorzInvert')
        ucfg['vertInvert'] = g_settingsCore.getSetting('mouseVertInvert')
        ucfg['keySensitivity'] = readFloat(ds, 'keySensitivity', 0.0, 10.0, 1.0)
        ucfg['sensitivity'] = readFloat(ds, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(ds, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['camDist'] = readFloat(ds, 'camDist', 0.0, 60.0, 0)
        self.__cfg = dict()
        cfg = self.__cfg
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
        self.__dynamicCfg.readImpulsesConfig(dynamicsSection)
        self.__positionOscillator = createOscillatorFromSection(dynamicsSection['oscillator'], False)
        self.__positionNoiseOscillator = createOscillatorFromSection(dynamicsSection['randomNoiseOscillatorFlat'], False)
        return
