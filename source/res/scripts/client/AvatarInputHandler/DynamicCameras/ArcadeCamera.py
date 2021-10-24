from collections import namedtuple
import logging
import math
import GUI
import Keys
import Math
import BattleReplay
import Settings
import constants
import math_utils
import BigWorld
from Math import Vector2
from Math import Vector3
from Math import Vector4
from Math import Matrix
from AvatarInputHandler import cameras
from AvatarInputHandler import aih_global_binding
from AvatarInputHandler.AimingSystems.ArcadeAimingSystem import ArcadeAimingSystem
from AvatarInputHandler.AimingSystems.ArcadeAimingSystem import ShotPointCalculatorPlanar
from AvatarInputHandler.AimingSystems.ArcadeAimingSystemRemote import ArcadeAimingSystemRemote
from AvatarInputHandler.DynamicCameras import createOscillatorFromSection
from AvatarInputHandler.DynamicCameras import CameraDynamicConfig
from AvatarInputHandler.DynamicCameras import AccelerationSmoother
from AvatarInputHandler.DynamicCameras import CameraWithSettings
from AvatarInputHandler.DynamicCameras import calcYawPitchDelta
from AvatarInputHandler.VideoCamera import KeySensor
from AvatarInputHandler.cameras import readFloat
from AvatarInputHandler.cameras import readVec2
from AvatarInputHandler.cameras import ImpulseReason
from AvatarInputHandler.cameras import FovExtended
from debug_utils import LOG_WARNING
from debug_utils import LOG_ERROR
from helpers.CallbackDelayer import CallbackDelayer
from helpers.CallbackDelayer import TimeDeltaMeter
from gui.battle_control import event_dispatcher
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCache
from account_helpers.settings_core.settings_constants import GAME
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import EScrollDir
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import EXPONENTIAL_EASING
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import CollideAnimatorEasing
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import OverScrollProtector
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import ZoomStateSwitcher
from AvatarInputHandler.DynamicCameras.arcade_camera_helper import MinMax
from skeletons.gui.game_control import IBootcampController
_logger = logging.getLogger(__name__)
def getCameraAsSettingsHolder(settingsDataSec):
    return ArcadeCamera(settingsDataSec, None)

_DEFAULT_ZOOM_DURATION = 0.5
_COLLIDE_ANIM_DIST = 1.0
_COLLIDE_ANIM_INTERVAL = 0.2
class CollisionVolumeGroup(namedtuple('CollisionVolumeGroup', ('minVolume', 'lowSpeedLimit', 'vehicleVisibilityLimit', 'approachSpeed', 'cameraSpeedFactor', 'criticalDistance', 'canSkip'))):
    @staticmethod
    def fromSection(dataSection):
        it = iter(CollisionVolumeGroup._fields)
        return CollisionVolumeGroup(dataSection.readFloat(next(it), 0.0), dataSection.readFloat(next(it), 0.0), dataSection.readFloat(next(it), 0.0), dataSection.readVector2(next(it), Math.Vector2(1.5, 10000.0)), dataSection.readFloat(next(it), 0.1), dataSection.readFloat(next(it), 5.0), dataSection.readBool(next(it), False))

VOLUME_GROUPS_NAMES = ['tiny', 'small', 'medium', 'large']
_INERTIA_EASING = math_utils.Easing.exponentialEasing
ENABLE_INPUT_ROTATION_INERTIA = False
class _InputInertia(object):
    positionDelta = property((lambda self: self._InputInertia__deltaEasing.value))
    fovZoomMultiplier = property((lambda self: self._InputInertia__zoomMultiplierEasing.value))
    endZoomMultiplier = property((lambda self: self._InputInertia__zoomMultiplierEasing.b))
    def __init__(self, minMaxZoomMultiplier, relativeFocusDist, duration = _DEFAULT_ZOOM_DURATION):
        self._InputInertia__deltaEasing = EXPONENTIAL_EASING(Vector3(0.0), Vector3(0.0), duration)
        fovMultiplier = math_utils.lerp(minMaxZoomMultiplier.min, minMaxZoomMultiplier.max, relativeFocusDist)
        self._InputInertia__zoomMultiplierEasing = EXPONENTIAL_EASING(fovMultiplier, fovMultiplier, duration)
        self._InputInertia__minMaxZoomMultiplier = minMaxZoomMultiplier

    def glide(self, posDelta, duration = _DEFAULT_ZOOM_DURATION, easing = EXPONENTIAL_EASING):
        self._InputInertia__deltaEasing = easing(posDelta, Vector3(0.0), duration)

    def isGliding(self):
        return (self._InputInertia__deltaEasing != Vector3(0.0)) and (not self._InputInertia__deltaEasing.stopped)

    def glideFov(self, newRelativeFocusDist, duration = _DEFAULT_ZOOM_DURATION):
        minMult, maxMult = self._InputInertia__minMaxZoomMultiplier
        endMult = math_utils.lerp(minMult, maxMult, newRelativeFocusDist)
        self._InputInertia__zoomMultiplierEasing.reset(self._InputInertia__zoomMultiplierEasing.value, endMult, duration)

    def teleport(self, relativeFocusDist, minMaxZoomMultiplier = None, duration = _DEFAULT_ZOOM_DURATION):
        if minMaxZoomMultiplier is not None:
            self._InputInertia__minMaxZoomMultiplier = minMaxZoomMultiplier
        self._InputInertia__deltaEasing.reset(Vector3(0.0), Vector3(0.0), duration)
        fovMultiplier = math_utils.lerp(self._InputInertia__minMaxZoomMultiplier.min, self._InputInertia__minMaxZoomMultiplier.max, relativeFocusDist)
        self._InputInertia__zoomMultiplierEasing.reset(fovMultiplier, fovMultiplier, duration)

    def update(self, deltaTime):
        self._InputInertia__deltaEasing.update(deltaTime)
        self._InputInertia__zoomMultiplierEasing.update(deltaTime)

    def calcWorldPos(self, idealBasisMatrix):
        return idealBasisMatrix.translation + idealBasisMatrix.applyVector(self._InputInertia__deltaEasing.value)

class ArcadeCamera(CameraWithSettings, CallbackDelayer, TimeDeltaMeter):
    _ArcadeCamera__settingsCache = dependency.descriptor(ISettingsCache)
    _ArcadeCamera__bootcampCtrl = dependency.descriptor(IBootcampController)
    REASONS_AFFECT_CAMERA_DIRECTLY = (ImpulseReason.MY_SHOT, ImpulseReason.OTHER_SHOT, ImpulseReason.VEHICLE_EXPLOSION, ImpulseReason.HE_EXPLOSION)
    _DYNAMIC_ENABLED = True
    @staticmethod
    def enableDynamicCamera(enable):
        ArcadeCamera._DYNAMIC_ENABLED = enable

    @staticmethod
    def isCameraDynamic():
        return ArcadeCamera._DYNAMIC_ENABLED

    _FILTER_LENGTH = 5
    _DEFAULT_MAX_ACCELERATION_DURATION = 1.5
    _FOCAL_POINT_CHANGE_SPEED = 100.0
    _FOCAL_POINT_MIN_DIFF = 5.0
    _MIN_REL_SPEED_ACC_SMOOTHING = 0.7
    def getReasonsAffectCameraDirectly(self):
        return ArcadeCamera.REASONS_AFFECT_CAMERA_DIRECTLY

    def __getVehicleMProv(self):
        refinedMProv = self._ArcadeCamera__aimingSystem.vehicleMProv
        return refinedMProv.b.source

    def __setVehicleMProv(self, vehicleMProv):
        prevAimRel = self._ArcadeCamera__cam.aimPointProvider.a if self._ArcadeCamera__cam.aimPointProvider is not None else None
        refinedVehicleMProv = self._ArcadeCamera__refineVehicleMProv(vehicleMProv)
        self._ArcadeCamera__aimingSystem.vehicleMProv = refinedVehicleMProv
        self._ArcadeCamera__setupCameraProviders(refinedVehicleMProv)
        self._ArcadeCamera__cam.speedTreeTarget = self._ArcadeCamera__aimingSystem.vehicleMProv
        self._ArcadeCamera__aimingSystem.update(0.0)
        if prevAimRel is not None:
            self._ArcadeCamera__cam.aimPointProvider.a = prevAimRel
        baseTranslation = Matrix(refinedVehicleMProv).translation
        relativePosition = self._ArcadeCamera__aimingSystem.matrix.translation - baseTranslation
        self._ArcadeCamera__setCameraPosition(relativePosition)

    camera = property((lambda self: self._ArcadeCamera__cam))
    angles = property((lambda self: (self._ArcadeCamera__aimingSystem.yaw, self._ArcadeCamera__aimingSystem.pitch)))
    aimingSystem = property((lambda self: self._ArcadeCamera__aimingSystem))
    vehicleMProv = property(_ArcadeCamera__getVehicleMProv, _ArcadeCamera__setVehicleMProv)
    _ArcadeCamera__aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)
    def __init__(self, dataSec, defaultOffset = None):
        super(ArcadeCamera, self).__init__()
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self._ArcadeCamera__shiftKeySensor = None
        self._ArcadeCamera__movementOscillator = None
        self._ArcadeCamera__impulseOscillator = None
        self._ArcadeCamera__noiseOscillator = None
        self._ArcadeCamera__dynamicCfg = CameraDynamicConfig()
        self._ArcadeCamera__accelerationSmoother = None
        self._ArcadeCamera__zoomStateSwitcher = ZoomStateSwitcher()
        self._readConfigs(dataSec)
        self._ArcadeCamera__onChangeControlMode = None
        self._ArcadeCamera__aimingSystem = None
        self._ArcadeCamera__curSense = 0
        self._ArcadeCamera__curScrollSense = 0
        self._ArcadeCamera__postmortemMode = False
        self._ArcadeCamera__focalPointDist = 1.0
        self._ArcadeCamera__autoUpdateDxDyDz = Vector3(0.0)
        self._ArcadeCamera__updatedByKeyboard = False
        self._ArcadeCamera__isCamInTransition = False
        self._ArcadeCamera__collideAnimatorEasing = CollideAnimatorEasing()
        if defaultOffset is not None:
            self._ArcadeCamera__defaultAimOffset = defaultOffset
            self._ArcadeCamera__cam = BigWorld.HomingCamera(self._ArcadeCamera__adCfg['enable'])
            if self._ArcadeCamera__adCfg['enable']:
                self._ArcadeCamera__cam.initAdvancedCollider(self._ArcadeCamera__adCfg['fovRatio'], self._ArcadeCamera__adCfg['rollbackSpeed'], self._ArcadeCamera__adCfg['minimalCameraDistance'], self._ArcadeCamera__adCfg['speedThreshold'], self._ArcadeCamera__adCfg['minimalVolume'])
                for group_name in VOLUME_GROUPS_NAMES:
                    self._ArcadeCamera__cam.addVolumeGroup(self._ArcadeCamera__adCfg['volumeGroups'][group_name])
                else:
                    pass
            self._ArcadeCamera__cam.aimPointClipCoords = defaultOffset
        else:
            self._ArcadeCamera__defaultAimOffset = Vector2()
            self._ArcadeCamera__cam = None
        self._ArcadeCamera__cameraTransition = BigWorld.TransitionCamera()
        self._ArcadeCamera__overScrollProtector = OverScrollProtector()
        self._ArcadeCamera__updateProperties(state = None)

    @staticmethod
    def _getConfigsKey():
        return ArcadeCamera.__name__

    def create(self, onChangeControlMode = None, postmortemMode = False):
        super(ArcadeCamera, self).create()
        self._ArcadeCamera__onChangeControlMode = onChangeControlMode
        self._ArcadeCamera__postmortemMode = postmortemMode
        targetMat = self.getTargetMProv()
        aimingSystemClass = ArcadeAimingSystemRemote if BigWorld.player().isObserver() else ArcadeAimingSystem
        self._ArcadeCamera__aimingSystem = aimingSystemClass(self._ArcadeCamera__refineVehicleMProv(targetMat), self._cfg['heightAboveBase'], self._cfg['focusRadius'], self._ArcadeCamera__calcAimMatrix(), self._cfg['angleRange'], not postmortemMode)
        if self._ArcadeCamera__adCfg['enable']:
            self._ArcadeCamera__aimingSystem.initAdvancedCollider(self._ArcadeCamera__adCfg['fovRatio'], self._ArcadeCamera__adCfg['rollbackSpeed'], self._ArcadeCamera__adCfg['minimalCameraDistance'], self._ArcadeCamera__adCfg['speedThreshold'], self._ArcadeCamera__adCfg['minimalVolume'])
            for group_name in VOLUME_GROUPS_NAMES:
                self._ArcadeCamera__aimingSystem.addVolumeGroup(self._ArcadeCamera__adCfg['volumeGroups'][group_name])
            else:
                pass
        self.setCameraDistance(self._cfg['startDist'])
        self._ArcadeCamera__aimingSystem.pitch = self._cfg['startAngle']
        self._ArcadeCamera__aimingSystem.yaw = Math.Matrix(targetMat).yaw
        self._ArcadeCamera__aimingSystem.cursorShouldCheckCollisions(True)
        self._ArcadeCamera__updateAngles(0, 0)
        cameraPosProvider = Math.Vector4Translation(self._ArcadeCamera__aimingSystem.matrix)
        self._ArcadeCamera__cam.cameraPositionProvider = cameraPosProvider

    def getTargetMProv(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.playerVehicleID != 0:
            vehicleID = replayCtrl.playerVehicleID
        else:
            vehicleID = BigWorld.player().playerVehicleID
        return BigWorld.entity(vehicleID).matrix

    def reinitMatrix(self):
        self._ArcadeCamera__setVehicleMProv(self.getTargetMProv())

    def setToVehicleDirection(self):
        matrix = Math.Matrix(self.getTargetMProv())
        self.setYawPitch(matrix.yaw, matrix.pitch)

    def destroy(self):
        self.disable()
        self._ArcadeCamera__onChangeControlMode = None
        self._ArcadeCamera__cam = None
        self._ArcadeCamera__cameraTransition = None
        if self._ArcadeCamera__aimingSystem is not None:
            self._ArcadeCamera__aimingSystem.destroy()
            self._ArcadeCamera__aimingSystem = None
        CallbackDelayer.destroy(self)
        CameraWithSettings.destroy(self)

    def getPivotSettings(self):
        return self._ArcadeCamera__aimingSystem.getPivotSettings()

    def setPivotSettings(self, heightAboveBase, focusRadius):
        self._ArcadeCamera__aimingSystem.setPivotSettings(heightAboveBase, focusRadius)

    def __setDynamicCollisions(self, enable):
        if self._ArcadeCamera__cam is not None:
            self._ArcadeCamera__cam.setDynamicCollisions(enable)
        if self._ArcadeCamera__aimingSystem is not None:
            self._ArcadeCamera__aimingSystem.setDynamicCollisions(enable)

    def focusOnPos(self, preferredPos):
        self._ArcadeCamera__aimingSystem.focusOnPos(preferredPos)

    def shiftCamPos(self, shift = None):
        matrixProduct = self._ArcadeCamera__aimingSystem.vehicleMProv
        shiftMat = matrixProduct.a
        if shift is not None:
            camDirection = Math.Vector3(math.sin(self.angles[0]), 0, math.cos(self.angles[0]))
            normal = Math.Vector3(camDirection)
            normal.x = camDirection.z
            normal.z = -camDirection.x
            shiftMat.translation = shiftMat.translation + camDirection * shift.z + Math.Vector3(0, 1, 0) * shift.y + normal * shift.x
        else:
            shiftMat.setIdentity()

    def enable(self, preferredPos = None, closesDist = False, postmortemParams = None, turretYaw = None, gunPitch = None, camTransitionParams = None, initialVehicleMatrix = None):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setAimClipPosition(self._ArcadeCamera__aimOffset)
        self.measureDeltaTime()
        camDist = None
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if player.observerSeesAll() and player.arena.period == constants.ARENA_PERIOD.BATTLE and vehicle and vehicle.id == player.playerVehicleID:
            self.delayCallback(0.0, self.enable, preferredPos, closesDist, postmortemParams, turretYaw, gunPitch, camTransitionParams, initialVehicleMatrix)
            return
        elif initialVehicleMatrix is None:
            initialVehicleMatrix = player.getOwnVehicleMatrix(self.vehicleMProv) if vehicle is None else vehicle.matrix
        vehicleMProv = initialVehicleMatrix
        if self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM):
            self._ArcadeCamera__updateProperties(state = None)
            self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.max)
            self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
            self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
        if self._ArcadeCamera__postmortemMode:
            if postmortemParams is not None:
                self._ArcadeCamera__aimingSystem.yaw = postmortemParams[0][0]
                self._ArcadeCamera__aimingSystem.pitch = postmortemParams[0][1]
                camDist = postmortemParams[1]
            else:
                camDist = self._ArcadeCamera__distRange.max
        elif closesDist:
            camDist = self._ArcadeCamera__distRange.min
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            camDist = None
            vehicle = BigWorld.entity(replayCtrl.playerVehicleID)
            if vehicle is not None:
                vehicleMProv = vehicle.matrix
        if camDist is not None:
            self.setCameraDistance(camDist)
        else:
            self._ArcadeCamera__inputInertia.teleport(self._ArcadeCamera__calcRelativeDist())
        self.vehicleMProv = vehicleMProv
        self._ArcadeCamera__setDynamicCollisions(True)
        self._ArcadeCamera__aimingSystem.enable(preferredPos, turretYaw, gunPitch)
        self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
        if camTransitionParams is not None and BigWorld.camera() is not self._ArcadeCamera__cam:
            cameraTransitionDuration = camTransitionParams.get('cameraTransitionDuration', -1)
            if cameraTransitionDuration > 0:
                self._ArcadeCamera__setupCameraTransition(cameraTransitionDuration)
            else:
                BigWorld.camera(self._ArcadeCamera__cam)
        else:
            BigWorld.camera(self._ArcadeCamera__cam)
        self._ArcadeCamera__cameraUpdate()
        self.delayCallback(0.0, self._ArcadeCamera__cameraUpdate)
        from gui import g_guiResetters
        g_guiResetters.add(self._ArcadeCamera__onRecreateDevice)
        self._ArcadeCamera__updateAdvancedCollision()
        self._ArcadeCamera__updateLodBiasForTanks()

    def __setupCameraTransition(self, duration):
        self._ArcadeCamera__cameraTransition.start(BigWorld.camera().matrix, self._ArcadeCamera__cam, duration)
        BigWorld.camera(self._ArcadeCamera__cameraTransition)
        invMatrix = Math.Matrix()
        invMatrix.set(BigWorld.camera().invViewMatrix)
        previousAimVector = invMatrix.applyToAxis(2)
        self.setYawPitch(previousAimVector.yaw, -previousAimVector.pitch)
        self._ArcadeCamera__isCamInTransition = True

    def _handleSettingsChange(self, diff):
        if 'fov' in diff or 'dynamicFov' in diff:
            self._ArcadeCamera__inputInertia.teleport(self._ArcadeCamera__calcRelativeDist(), self._ArcadeCamera__calculateInputInertiaMinMax())
        if GAME.PRE_COMMANDER_CAM in diff or GAME.COMMANDER_CAM in diff:
            self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())

    def _updateSettingsFromServer(self):
        super(ArcadeCamera, self)._updateSettingsFromServer()
        if self.settingsCore.isReady:
            ucfg = self._userCfg
            ucfg['sniperModeByShift'] = self.settingsCore.getSetting('sniperModeByShift')
            cfg = self._cfg
            cfg['sniperModeByShift'] = ucfg['sniperModeByShift']

    def __calculateInputInertiaMinMax(self):
        if self.settingsCore.getSetting('dynamicFov'):
            _, minFov, maxFov = self.settingsCore.getSetting('fov')
            kMin = minFov / maxFov
        else:
            kMin = 1.0
        return MinMax(kMin, 1.0)

    def restartCameraTransition(self, duration):
        if self._ArcadeCamera__cam is not None and not self._ArcadeCamera__cameraTransition.isInTransition():
            self._ArcadeCamera__isCamInTransition = True
            self._ArcadeCamera__cameraTransition.start(BigWorld.camera().matrix, self._ArcadeCamera__cam, duration)

    def __refineVehicleMProv(self, vehicleMProv):
        vehicleTranslationOnly = Math.WGTranslationOnlyMP()
        vehicleTranslationOnly.source = vehicleMProv
        refinedMatrixProvider = Math.MatrixProduct()
        refinedMatrixProvider.a = math_utils.createIdentityMatrix()
        refinedMatrixProvider.b = vehicleTranslationOnly
        return refinedMatrixProvider

    def __setupCameraProviders(self, vehicleMProv):
        vehiclePos = Math.Vector4Translation(vehicleMProv)
        cameraPositionProvider = Math.Vector4Combiner()
        cameraPositionProvider.fn = 'ADD'
        cameraPositionProvider.a = Vector4(0, 0, 0, 0)
        cameraPositionProvider.b = vehiclePos
        cameraAimPointProvider = Math.Vector4Combiner()
        cameraAimPointProvider.fn = 'ADD'
        cameraAimPointProvider.a = Vector4(0, 0, 1, 0)
        cameraAimPointProvider.b = vehiclePos
        self._ArcadeCamera__cam.cameraPositionProvider = cameraPositionProvider
        self._ArcadeCamera__cam.aimPointProvider = cameraAimPointProvider
        self._ArcadeCamera__cam.pivotPositionProvider = self._ArcadeCamera__aimingSystem.positionAboveVehicleProv

    def __setCameraPosition(self, relativeToVehiclePosition):
        self._ArcadeCamera__cam.cameraPositionProvider.a = Vector4(relativeToVehiclePosition.x, relativeToVehiclePosition.y, relativeToVehiclePosition.z, 1.0)

    def __setCameraAimPoint(self, relativeToVehiclePosition):
        self._ArcadeCamera__cam.aimPointProvider.a = Vector4(relativeToVehiclePosition.x, relativeToVehiclePosition.y, relativeToVehiclePosition.z, 1.0)

    def disable(self):
        from gui import g_guiResetters
        if self._ArcadeCamera__onRecreateDevice in g_guiResetters:
            g_guiResetters.remove(self._ArcadeCamera__onRecreateDevice)
        self._ArcadeCamera__setDynamicCollisions(False)
        self._ArcadeCamera__cam.speedTreeTarget = None
        if self._ArcadeCamera__shiftKeySensor is not None:
            self._ArcadeCamera__shiftKeySensor.reset(Math.Vector3())
        self.clearCallbacks()
        self._ArcadeCamera__movementOscillator.reset()
        self._ArcadeCamera__impulseOscillator.reset()
        self._ArcadeCamera__noiseOscillator.reset()
        self._ArcadeCamera__accelerationSmoother.reset()
        self._ArcadeCamera__autoUpdateDxDyDz.set(0)
        self._ArcadeCamera__updatedByKeyboard = False
        dist = self._ArcadeCamera__calcRelativeDist()
        if dist is not None:
            self._ArcadeCamera__inputInertia.teleport(dist)
        FovExtended.instance().resetFov()
        BigWorld.setMinLodBiasForTanks(0.0)
        self._ArcadeCamera__collideAnimatorEasing.stop()
        self._ArcadeCamera__cam.shiftCamera(Vector3(0.0))

    def update(self, dx, dy, dz, rotateMode = True, zoomMode = True, updatedByKeyboard = False):
        eScrollDirection = EScrollDir.convertDZ(dz)
        if eScrollDirection:
            self._ArcadeCamera__overScrollProtector.updateOnScroll(eScrollDirection)
        self._ArcadeCamera__curSense = self._cfg['keySensitivity'] if updatedByKeyboard else self._ArcadeCamera__sensitivity
        self._ArcadeCamera__curScrollSense = self._cfg['keySensitivity'] if updatedByKeyboard else self._ArcadeCamera__scrollSensitivity
        self._ArcadeCamera__updatedByKeyboard = updatedByKeyboard
        if updatedByKeyboard:
            self._ArcadeCamera__autoUpdateDxDyDz.set(dx, dy, dz)
        else:
            self._ArcadeCamera__autoUpdateDxDyDz.set(0)
            self._ArcadeCamera__update(dx, dy, dz, rotateMode, zoomMode)

    def setUserConfigValue(self, name, value):
        if name not in self._userCfg:
            return
        else:
            self._userCfg[name] = value
            if name not in ('keySensitivity', 'sensitivity', 'scrollSensitivity'):
                self._cfg[name] = self._userCfg[name]
                if name == 'fovMultMinMaxDist' and getattr(self, '_ArcadeCamera__aimingSystem', None) is not None:
                    self._ArcadeCamera__inputInertia.teleport(self._ArcadeCamera__calcRelativeDist(), value)
            else:
                self._cfg[name] = self._baseCfg[name] * self._userCfg[name]
            zoomState = self._ArcadeCamera__zoomStateSwitcher.getCurrentState()
            self._ArcadeCamera__updateProperties(zoomState)
            return

    def setCameraDistance(self, distance):
        distRange = self._ArcadeCamera__distRange
        clampedDist = math_utils.clamp(distRange.min, distRange.max, distance)
        self._ArcadeCamera__aimingSystem.distanceFromFocus = clampedDist
        self._ArcadeCamera__inputInertia.teleport(self._ArcadeCamera__calcRelativeDist())

    def getCameraDistance(self):
        return self._ArcadeCamera__aimingSystem.distanceFromFocus

    def setYawPitch(self, yaw, pitch):
        self._ArcadeCamera__aimingSystem.yaw = yaw
        self._ArcadeCamera__aimingSystem.pitch = pitch

    def __updateAngles(self, dx, dy):
        yawDelta, pitchDelta = calcYawPitchDelta(self._cfg, self._ArcadeCamera__curSense, dx, dy)
        self._ArcadeCamera__aimingSystem.handleMovement(yawDelta, -pitchDelta)
        return (self._ArcadeCamera__aimingSystem.yaw, self._ArcadeCamera__aimingSystem.pitch, 0)

    def __update(self, dx, dy, dz, rotateMode = True, zoomMode = True):
        if self._ArcadeCamera__aimingSystem:
            eScrollDir = EScrollDir.convertDZ(dz)
            prevPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrix)
            prevDist = self._ArcadeCamera__aimingSystem.distanceFromFocus
            distMinMax = self._ArcadeCamera__distRange
            if self._ArcadeCamera__isCamInTransition:
                self._ArcadeCamera__isCamInTransition = self._ArcadeCamera__cameraTransition.isInTransition()
            isColliding = self._ArcadeCamera__cam.hasCollision()
            collisionWhileGlide = False
            if self._ArcadeCamera__inputInertia.isGliding() and not isColliding and eScrollDir is EScrollDir.OUT and not self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM):
                cameraPos = self._ArcadeCamera__aimingSystem.matrix.translation
                collisionWhileGlide = self._ArcadeCamera__cam.isColliding(BigWorld.player().spaceID, cameraPos)
            preventScrollOut = (isColliding or collisionWhileGlide) and (eScrollDir is EScrollDir.OUT) and (not self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM))
            if preventScrollOut and prevDist == distMinMax.max and self._ArcadeCamera__isSettingsEnabled(GAME.COMMANDER_CAM) and ((self._ArcadeCamera__isInArcadeZoomState() and not self._ArcadeCamera__isSettingsEnabled(GAME.PRE_COMMANDER_CAM)) or self._ArcadeCamera__compareCurrStateSettingsKey(GAME.PRE_COMMANDER_CAM)):
                preventScrollOut = False
            if isColliding and eScrollDir is EScrollDir.OUT:
                self._ArcadeCamera__collideAnimatorEasing.start(_COLLIDE_ANIM_DIST, _COLLIDE_ANIM_INTERVAL)
            distChanged = False
            if zoomMode and eScrollDir and not self._ArcadeCamera__overScrollProtector.isProtecting() and not preventScrollOut:
                if eScrollDir is EScrollDir.OUT and not self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM) and self._ArcadeCamera__isSettingsEnabled(GAME.COMMANDER_CAM):
                    event_dispatcher.showCommanderCamHint(show = True)
                distDelta = dz * float(self._ArcadeCamera__curScrollSense)
                newDist = math_utils.clamp(distMinMax.min, distMinMax.max, prevDist - distDelta)
                floatEps = 0.001
                if abs(newDist - prevDist) > floatEps:
                    self._ArcadeCamera__updateCameraSettings(newDist)
                    self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                    self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                    distChanged = True
                if abs(newDist - prevDist) < floatEps and math_utils.almostZero(newDist - distMinMax.min):
                    if self._ArcadeCamera__isInArcadeZoomState() and self._ArcadeCamera__onChangeControlMode and not self._ArcadeCamera__updatedByKeyboard:
                        self._ArcadeCamera__onChangeControlMode()
                        return
                    else:
                        self._ArcadeCamera__changeZoomState(EScrollDir.IN)
                elif abs(newDist - prevDist) < floatEps and math_utils.almostZero(newDist - distMinMax.max):
                    self._ArcadeCamera__changeZoomState(EScrollDir.OUT)
            if rotateMode and not self._ArcadeCamera__isCamInTransition:
                self._ArcadeCamera__updateAngles(dx, dy)
            if ENABLE_INPUT_ROTATION_INERTIA and not distChanged:
                self._ArcadeCamera__aimingSystem.update(0.0)
            if ENABLE_INPUT_ROTATION_INERTIA or distChanged:
                self._ArcadeCamera__startInputInertiaTransition(prevPos)
            return
        else:
            return

    def __adjustMinDistForShotPointCalc(self):
        if self._ArcadeCamera__aimingSystem:
            vehPos = Matrix(self._ArcadeCamera__aimingSystem.vehicleMProv).translation
            camPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrix)
            vehCamDiff = vehPos.distTo(camPos)
            minDist = ShotPointCalculatorPlanar.MIN_DIST + vehCamDiff
            self._ArcadeCamera__aimingSystem.setMinDistanceForShotPointCalc(minDist)

    def __startInputInertiaTransition(self, prevPos, duration = _DEFAULT_ZOOM_DURATION, easing = EXPONENTIAL_EASING):
        worldDeltaPos = prevPos - self._ArcadeCamera__aimingSystem.matrix.translation
        matInv = Matrix(self._ArcadeCamera__aimingSystem.matrix)
        matInv.invert()
        self._ArcadeCamera__inputInertia.glide(matInv.applyVector(worldDeltaPos), duration = duration, easing = easing)

    def __checkNewDistance(self, newDistance):
        distMinMax = self._ArcadeCamera__distRange
        return math_utils.clamp(distMinMax.min, distMinMax.max, newDistance)

    def __updateProperties(self, state = None):
        self._ArcadeCamera__zoomStateSwitcher.setCurrentState(state)
        self._ArcadeCamera__distRange = state.distRange if state else self._cfg['distRange']
        self._ArcadeCamera__overScrollProtectOnMax = state.overScrollProtectOnMax if state else self._cfg['overScrollProtectOnMax']
        self._ArcadeCamera__overScrollProtectOnMin = state.overScrollProtectOnMin if state else self._cfg['overScrollProtectOnMin']
        self._ArcadeCamera__sensitivity = state.sensitivity * self._userCfg['sensitivity'] if state else self._cfg['sensitivity']
        self._ArcadeCamera__scrollSensitivity = state.scrollSensitivity if state else self._cfg['scrollSensitivity']
        if state is None:
            if self._ArcadeCamera__isSettingsEnabled(GAME.PRE_COMMANDER_CAM):
                self._ArcadeCamera__overScrollProtectOnMax = 0.0
            self._ArcadeCamera__zoomStateSwitcher.reset()
        self._ArcadeCamera__updateLodBiasForTanks()

    def __changeZoomState(self, eScrollDirection):
        if eScrollDirection not in (EScrollDir.IN, EScrollDir.OUT):
            return
        elif self._ArcadeCamera__zoomStateSwitcher.isEmpty() or self._ArcadeCamera__bootcampCtrl.isInBootcamp():
            self._ArcadeCamera__updateProperties(state = None)
            return
        else:
            state = None
            if eScrollDirection is EScrollDir.OUT:
                state = self._ArcadeCamera__zoomStateSwitcher.getNextState()
                if state is None:
                    return
                else:
                    self._ArcadeCamera__updateProperties(state = state)
                    prevPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrix)
                    if eScrollDirection is EScrollDir.OUT:
                        if self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM):
                            self.delayCallback(2, self._ArcadeCamera__hideCommanderCamHint)
                        self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.min)
                        self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                        self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                        if not self._ArcadeCamera__updatedByKeyboard:
                            interval = self._ArcadeCamera__overScrollProtectOnMin
                            self._ArcadeCamera__overScrollProtector.start(eScrollDirection = EScrollDir.OUT, interval = interval)
                        duration = state.transitionDurationOut if state else _DEFAULT_ZOOM_DURATION
                        easing = state.transitionEasingOut if state else EXPONENTIAL_EASING
                        self._ArcadeCamera__startInputInertiaTransition(prevPos, duration, easing)
                    elif eScrollDirection is EScrollDir.IN:
                        self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.max)
                        self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                        self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                        duration = state.transitionDurationIn if state else _DEFAULT_ZOOM_DURATION
                        easing = state.transitionEasingIn if state else EXPONENTIAL_EASING
                        self._ArcadeCamera__startInputInertiaTransition(prevPos, duration, easing)
                    self._ArcadeCamera__updateAdvancedCollision()
                    return
            else:
                if eScrollDirection is EScrollDir.IN:
                    state = self._ArcadeCamera__zoomStateSwitcher.getPrevState()
                    if self._ArcadeCamera__isInArcadeZoomState() and state is None:
                        return
                    else:
                        self._ArcadeCamera__updateProperties(state = state)
                        prevPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrix)
                        if eScrollDirection is EScrollDir.OUT:
                            if self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM):
                                self.delayCallback(2, self._ArcadeCamera__hideCommanderCamHint)
                            self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.min)
                            self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                            self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                            if not self._ArcadeCamera__updatedByKeyboard:
                                interval = self._ArcadeCamera__overScrollProtectOnMin
                                self._ArcadeCamera__overScrollProtector.start(eScrollDirection = EScrollDir.OUT, interval = interval)
                            duration = state.transitionDurationOut if state else _DEFAULT_ZOOM_DURATION
                            easing = state.transitionEasingOut if state else EXPONENTIAL_EASING
                            self._ArcadeCamera__startInputInertiaTransition(prevPos, duration, easing)
                        elif eScrollDirection is EScrollDir.IN:
                            self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.max)
                            self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                            self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                            duration = state.transitionDurationIn if state else _DEFAULT_ZOOM_DURATION
                            easing = state.transitionEasingIn if state else EXPONENTIAL_EASING
                            self._ArcadeCamera__startInputInertiaTransition(prevPos, duration, easing)
                else:
                    self._ArcadeCamera__updateProperties(state = state)
                    prevPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrix)
                    if eScrollDirection is EScrollDir.OUT:
                        if self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM):
                            self.delayCallback(2, self._ArcadeCamera__hideCommanderCamHint)
                        self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.min)
                        self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                        self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                        if not self._ArcadeCamera__updatedByKeyboard:
                            interval = self._ArcadeCamera__overScrollProtectOnMin
                            self._ArcadeCamera__overScrollProtector.start(eScrollDirection = EScrollDir.OUT, interval = interval)
                        duration = state.transitionDurationOut if state else _DEFAULT_ZOOM_DURATION
                        easing = state.transitionEasingOut if state else EXPONENTIAL_EASING
                        self._ArcadeCamera__startInputInertiaTransition(prevPos, duration, easing)
                    elif eScrollDirection is EScrollDir.IN:
                        self._ArcadeCamera__updateCameraSettings(self._ArcadeCamera__distRange.max)
                        self._ArcadeCamera__inputInertia.glideFov(self._ArcadeCamera__calcRelativeDist())
                        self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()
                        duration = state.transitionDurationIn if state else _DEFAULT_ZOOM_DURATION
                        easing = state.transitionEasingIn if state else EXPONENTIAL_EASING
                        self._ArcadeCamera__startInputInertiaTransition(prevPos, duration, easing)
                self._ArcadeCamera__updateAdvancedCollision()
                return

    def __hideCommanderCamHint(self):
        event_dispatcher.showCommanderCamHint(show = False)

    def __updateCameraSettings(self, newDist):
        distMinMax = self._ArcadeCamera__distRange
        state = self._ArcadeCamera__zoomStateSwitcher.getCurrentState()
        if state:
            totalDiff = distMinMax.max - distMinMax.min
            ratio = ((newDist - distMinMax.min) / totalDiff) if totalDiff is not 0 else 0
            angle = Math.Vector2(state.angleRangeOnMinDist)
            angle = angle + (state.angleRangeOnMaxDist - angle) * ratio
            heightAboveBaseTotalDiff = state.heightAboveBaseOnMinMaxDist.max - state.heightAboveBaseOnMinMaxDist.min
            heightAboveBase = state.heightAboveBaseOnMinMaxDist.min + heightAboveBaseTotalDiff * ratio
            focusRadiusTotalDiff = state.focusRadiusOnMinMaxDist.max - state.focusRadiusOnMinMaxDist.min
            focusRadius = state.focusRadiusOnMinMaxDist.min + focusRadiusTotalDiff * ratio
            self.aimingSystem.setAnglesRange(angle)
            self.setPivotSettings(heightAboveBase, focusRadius)
        else:
            self.aimingSystem.setAnglesRange(self._cfg['angleRange'])
            self.setPivotSettings(self._cfg['heightAboveBase'], self._cfg['focusRadius'])
        if newDist == distMinMax.max and not self._ArcadeCamera__updatedByKeyboard:
            interval = self._ArcadeCamera__overScrollProtectOnMax
            self._ArcadeCamera__overScrollProtector.start(eScrollDirection = EScrollDir.OUT, interval = interval)
        self._ArcadeCamera__aimingSystem.distanceFromFocus = newDist
        if self._ArcadeCamera__isInArcadeZoomState():
            self._userCfg['startDist'] = newDist
        heightAboveBase, _ = self.getPivotSettings()
        diff = heightAboveBase - self._cfg['heightAboveBase']
        self._ArcadeCamera__cam.shiftPivotPos(Vector3(0, -diff, 0))

    def __isInArcadeZoomState(self):
        return self._ArcadeCamera__zoomStateSwitcher.getCurrentState() is None

    def __compareCurrStateSettingsKey(self, key):
        state = self._ArcadeCamera__zoomStateSwitcher.getCurrentState()
        if state:
            return state.settingsKey == key
        else:
            return False

    def __isSettingsEnabled(self, settingsKey):
        if settingsKey and self._ArcadeCamera__settingsCache.isSynced():
            option = self.settingsCore.options.getSetting(settingsKey)
            if option:
                return bool(option.get())
            else:
                return False
        else:
            return False

    def __updateAdvancedCollision(self):
        enable = self._ArcadeCamera__compareCurrStateSettingsKey(GAME.COMMANDER_CAM)
        self._ArcadeCamera__cam.setCollisionCheckOnlyAtPos(enable)
        self._ArcadeCamera__aimingSystem.cursorShouldCheckCollisions(not enable)

    def __updateLodBiasForTanks(self):
        state = self._ArcadeCamera__zoomStateSwitcher.getCurrentState()
        minLodBias = state.minLODBiasForTanks if state else 0.0
        BigWorld.setMinLodBiasForTanks(minLodBias)

    def __cameraUpdate(self):
        if not ((self._ArcadeCamera__autoUpdateDxDyDz.x == 0.0) and ((self._ArcadeCamera__autoUpdateDxDyDz.y == 0.0) and (self._ArcadeCamera__autoUpdateDxDyDz.z == 0.0))):
            self._ArcadeCamera__update(self._ArcadeCamera__autoUpdateDxDyDz.x, self._ArcadeCamera__autoUpdateDxDyDz.y, self._ArcadeCamera__autoUpdateDxDyDz.z)
        inertDt = self.measureDeltaTime()
        deltaTime = self.measureDeltaTime()
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            repSpeed = replayCtrl.playbackSpeed
            if repSpeed == 0.0:
                inertDt = 0.01
                deltaTime = 0.0
            else:
                inertDt = deltaTime / repSpeed
                deltaTime = deltaTime / repSpeed
        self._ArcadeCamera__aimingSystem.update(deltaTime)
        virginShotPoint = self._ArcadeCamera__aimingSystem.getThirdPersonShotPoint()
        delta = self._ArcadeCamera__inputInertia.positionDelta
        sign = delta.dot(Vector3(0, 0, 1))
        self._ArcadeCamera__inputInertia.update(inertDt)
        delta = (delta - self._ArcadeCamera__inputInertia.positionDelta).length
        if delta != 0.0:
            self._ArcadeCamera__cam.setScrollDelta(math.copysign(delta, sign))
        FovExtended.instance().setFovByMultiplier(self._ArcadeCamera__inputInertia.fovZoomMultiplier)
        unshakenPos = self._ArcadeCamera__inputInertia.calcWorldPos(self._ArcadeCamera__aimingSystem.matrix)
        vehMatrix = Math.Matrix(self._ArcadeCamera__aimingSystem.vehicleMProv)
        vehiclePos = vehMatrix.translation
        fromVehicleToUnshakedPos = unshakenPos - vehiclePos
        deviationBasis = math_utils.createRotationMatrix(Vector3(self._ArcadeCamera__aimingSystem.yaw, 0, 0))
        impulseDeviation, movementDeviation, oscillationsZoomMultiplier = self._ArcadeCamera__updateOscillators(deltaTime)
        relCamPosMatrix = math_utils.createTranslationMatrix(impulseDeviation + movementDeviation)
        relCamPosMatrix.postMultiply(deviationBasis)
        relCamPosMatrix.translation = relCamPosMatrix.translation + fromVehicleToUnshakedPos
        upRotMat = math_utils.createRotationMatrix(Vector3(0, 0, -impulseDeviation.x * self._ArcadeCamera__dynamicCfg['sideImpulseToRollRatio'] - self._ArcadeCamera__noiseOscillator.deviation.z))
        upRotMat.postMultiply(relCamPosMatrix)
        self._ArcadeCamera__cam.up = upRotMat.applyVector(Vector3(0, 1, 0))
        relTranslation = relCamPosMatrix.translation
        if self._ArcadeCamera__inputInertia.isGliding():
            self._ArcadeCamera__adjustMinDistForShotPointCalc()
            shotPoint = virginShotPoint
        else:
            shotPoint = self._ArcadeCamera__calcFocalPoint(virginShotPoint, deltaTime)
        vehToShotPoint = shotPoint - vehiclePos
        self._ArcadeCamera__setCameraAimPoint(vehToShotPoint)
        self._ArcadeCamera__setCameraPosition(relTranslation)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            aimOffset = replayCtrl.getAimClipPosition()
            if not BigWorld.player().isForcedGuiControlMode() and GUI.mcursor().inFocus:
                GUI.mcursor().position = aimOffset
        else:
            aimOffset = self._ArcadeCamera__calcAimOffset(oscillationsZoomMultiplier)
            if replayCtrl.isRecording:
                replayCtrl.setAimClipPosition(aimOffset)
        self._ArcadeCamera__cam.aimPointClipCoords = aimOffset
        self._ArcadeCamera__aimOffset = aimOffset
        if self._ArcadeCamera__shiftKeySensor is not None:
            self._ArcadeCamera__shiftKeySensor.update(1.0)
            if self._ArcadeCamera__shiftKeySensor.currentVelocity.lengthSquared > 0.0:
                self.shiftCamPos(self._ArcadeCamera__shiftKeySensor.currentVelocity)
                self._ArcadeCamera__shiftKeySensor.currentVelocity = Math.Vector3()
        self._ArcadeCamera__updateCollideAnimator(deltaTime)
        return 0.0

    def __updateCollideAnimator(self, deltaTime):
        result = self._ArcadeCamera__collideAnimatorEasing.update(deltaTime)
        posOnVehicleProv = self._ArcadeCamera__aimingSystem.positionAboveVehicleProv.value
        pivotPos = Vector3(posOnVehicleProv.x, posOnVehicleProv.y, posOnVehicleProv.z)
        camPosition = self._ArcadeCamera__aimingSystem.matrix.translation
        zAxis = camPosition - pivotPos
        zAxis.normalise()
        if self._ArcadeCamera__cam:
            self._ArcadeCamera__cam.shiftCamera(result * zAxis)

    def __calcFocalPoint(self, shotPoint, deltaTime):
        aimStartPoint = self._ArcadeCamera__aimingSystem.matrix.translation
        aimDir = shotPoint - aimStartPoint
        distToShotPoint = aimDir.length
        if distToShotPoint < 0.001:
            return shotPoint
        else:
            aimDir = aimDir / distToShotPoint
            absDiff = abs(distToShotPoint - self._ArcadeCamera__focalPointDist)
            if absDiff < ArcadeCamera._FOCAL_POINT_MIN_DIFF or absDiff <= ArcadeCamera._FOCAL_POINT_CHANGE_SPEED * deltaTime:
                self._ArcadeCamera__focalPointDist = distToShotPoint
                return shotPoint
            else:
                changeDir = (distToShotPoint - self._ArcadeCamera__focalPointDist) / absDiff
                self._ArcadeCamera__focalPointDist = self._ArcadeCamera__focalPointDist + changeDir * ArcadeCamera._FOCAL_POINT_CHANGE_SPEED * deltaTime
                return aimStartPoint + aimDir * self._ArcadeCamera__focalPointDist

    def __calcAimOffset(self, oscillationsZoomMultiplier):
        fov = BigWorld.projection().fov
        aspect = cameras.getScreenAspectRatio()
        yTan = math.tan(fov * 0.5)
        xTan = yTan * aspect
        defaultX = self._ArcadeCamera__defaultAimOffset[0]
        defaultY = self._ArcadeCamera__defaultAimOffset[1]
        yawFromImpulse = self._ArcadeCamera__impulseOscillator.deviation.x * self._ArcadeCamera__dynamicCfg['sideImpulseToYawRatio']
        xImpulseDeviationTan = math.tan(-(yawFromImpulse + self._ArcadeCamera__noiseOscillator.deviation.x) * oscillationsZoomMultiplier)
        pitchFromImpulse = self._ArcadeCamera__impulseOscillator.deviation.z * self._ArcadeCamera__dynamicCfg['frontImpulseToPitchRatio']
        yImpulseDeviationTan = math.tan((pitchFromImpulse + self._ArcadeCamera__noiseOscillator.deviation.y) * oscillationsZoomMultiplier)
        totalOffset = Vector2((defaultX * xTan + xImpulseDeviationTan) / (xTan * (1 - defaultX * xTan * xImpulseDeviationTan)), (defaultY * yTan + yImpulseDeviationTan) / (yTan * (1 - defaultY * yTan * yImpulseDeviationTan)))
        return totalOffset

    def __calcRelativeDist(self):
        if self._ArcadeCamera__aimingSystem is not None:
            distRange = self._ArcadeCamera__getAbsoluteDistRange()
            curDist = self._ArcadeCamera__aimingSystem.distanceFromFocus
            return (curDist - distRange.min) / (distRange.max - distRange.min)
        else:
            return

    def __getAbsoluteDistRange(self):
        minDist = self._cfg['distRange'].min
        maxDist = self._cfg['distRange'].max
        for state in self._ArcadeCamera__zoomStateSwitcher:
            if not state.settingsKey or self._ArcadeCamera__isSettingsEnabled(state.settingsKey):
                minDist = min(minDist, state.distRange.min)
                maxDist = max(maxDist, state.distRange.max)
                continue
        return MinMax(minDist, maxDist)

    def __calcCurOscillatorAcceleration(self, deltaTime):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None:
            return Vector3(0, 0, 0)
        else:
            vehFilter = vehicle.filter
            curVelocity = getattr(vehFilter, 'velocity', Vector3(0.0))
            relativeSpeed = curVelocity.length / vehicle.typeDescriptor.physics['speedLimits'][0]
            if relativeSpeed >= ArcadeCamera._MIN_REL_SPEED_ACC_SMOOTHING:
                self._ArcadeCamera__accelerationSmoother.maxAllowedAcceleration = self._ArcadeCamera__dynamicCfg['accelerationThreshold']
            else:
                self._ArcadeCamera__accelerationSmoother.maxAllowedAcceleration = self._ArcadeCamera__dynamicCfg['accelerationMax']
            acceleration = self._ArcadeCamera__accelerationSmoother.update(vehicle, deltaTime)
            yawMat = math_utils.createRotationMatrix((-self._ArcadeCamera__aimingSystem.yaw, 0, 0))
            acceleration = yawMat.applyVector(-acceleration)
            oscillatorAcceleration = Vector3(acceleration.x, acceleration.y, acceleration.z)
            return oscillatorAcceleration * self._ArcadeCamera__dynamicCfg['accelerationSensitivity']

    def __updateOscillators(self, deltaTime):
        if ArcadeCamera.isCameraDynamic():
            oscillatorAcceleration = self._ArcadeCamera__calcCurOscillatorAcceleration(deltaTime)
            self._ArcadeCamera__movementOscillator.externalForce = self._ArcadeCamera__movementOscillator.externalForce + oscillatorAcceleration
            self._ArcadeCamera__impulseOscillator.update(deltaTime)
            self._ArcadeCamera__movementOscillator.update(deltaTime)
            self._ArcadeCamera__noiseOscillator.update(deltaTime)
            self._ArcadeCamera__impulseOscillator.externalForce = Vector3(0)
            self._ArcadeCamera__movementOscillator.externalForce = Vector3(0)
            self._ArcadeCamera__noiseOscillator.externalForce = Vector3(0)
            relDist = self._ArcadeCamera__calcRelativeDist()
            zoomMultiplier = math_utils.lerp(1.0, self._ArcadeCamera__dynamicCfg['zoomExposure'], relDist)
            impulseDeviation = Vector3(self._ArcadeCamera__impulseOscillator.deviation)
            impulseDeviation.set(impulseDeviation.x * zoomMultiplier, impulseDeviation.y * zoomMultiplier, impulseDeviation.z * zoomMultiplier)
            movementDeviation = Vector3(self._ArcadeCamera__movementOscillator.deviation)
            movementDeviation.set(movementDeviation.x * zoomMultiplier, movementDeviation.y * zoomMultiplier, movementDeviation.z * zoomMultiplier)
            return (impulseDeviation, movementDeviation, zoomMultiplier)
        else:
            self._ArcadeCamera__impulseOscillator.reset()
            self._ArcadeCamera__movementOscillator.reset()
            self._ArcadeCamera__noiseOscillator.reset()
            return (Vector3(0), Vector3(0), 1.0)

    def applyImpulse(self, position, impulse, reason = ImpulseReason.ME_HIT):
        adjustedImpulse, noiseMagnitude = self._ArcadeCamera__dynamicCfg.adjustImpulse(impulse, reason)
        yawMat = math_utils.createRotationMatrix((-self._ArcadeCamera__aimingSystem.yaw, 0, 0))
        impulseLocal = yawMat.applyVector(adjustedImpulse)
        self._ArcadeCamera__impulseOscillator.applyImpulse(impulseLocal)
        self._ArcadeCamera__applyNoiseImpulse(noiseMagnitude)

    def applyDistantImpulse(self, position, impulseValue, reason = ImpulseReason.ME_HIT):
        applicationPosition = self._ArcadeCamera__cam.position
        if reason == ImpulseReason.SPLASH:
            applicationPosition = Matrix(self.vehicleMProv).translation
        impulse = applicationPosition - position
        distance = impulse.length
        if distance < 1.0:
            distance = 1.0
        impulse.normalise()
        if (reason == ImpulseReason.OTHER_SHOT and distance <= self._ArcadeCamera__dynamicCfg['maxShotImpulseDistance']) or (reason == ImpulseReason.SPLASH or reason == ImpulseReason.HE_EXPLOSION or (reason == ImpulseReason.VEHICLE_EXPLOSION and distance <= self._ArcadeCamera__dynamicCfg['maxExplosionImpulseDistance'])):
            impulse = impulse * impulseValue / distance
        else:
            return
        self.applyImpulse(position, impulse, reason)

    def __applyNoiseImpulse(self, noiseMagnitude):
        noiseImpulse = math_utils.RandomVectors.random3(noiseMagnitude)
        self._ArcadeCamera__noiseOscillator.applyImpulse(noiseImpulse)

    def handleKeyEvent(self, isDown, key, mods, event = None):
        if self._ArcadeCamera__shiftKeySensor is None:
            return False
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and mods & 4:
            if key == Keys.KEY_C:
                self.shiftCamPos()
            return self._ArcadeCamera__shiftKeySensor.handleKeyEvent(key, isDown)
        else:
            self._ArcadeCamera__shiftKeySensor.reset(Math.Vector3())
            return False

    def reload(self):
        if constants.IS_DEVELOPMENT:
            import ResMgr
            ResMgr.purge('gui/avatar_input_handler.xml')
            cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/arcadeMode/camera/')
            self._reloadConfigs(cameraSec)
            return
        else:
            return

    def __calcAimMatrix(self):
        endMult = self._ArcadeCamera__inputInertia.endZoomMultiplier
        fov = FovExtended.instance().actualDefaultVerticalFov * endMult
        offset = self._ArcadeCamera__defaultAimOffset
        return cameras.getAimMatrix(-offset[0], -offset[1], fov)

    def _readConfigs(self, dataSec):
        if dataSec is None:
            LOG_WARNING('Invalid section <arcadeMode/camera> in avatar_input_handler.xml')
        super(ArcadeCamera, self)._readConfigs(dataSec)
        enableShift = dataSec.readBool('shift', False)
        if enableShift:
            movementMappings = dict()
            movementMappings[Keys.KEY_A] = Math.Vector3(-1, 0, 0)
            movementMappings[Keys.KEY_D] = Math.Vector3(1, 0, 0)
            movementMappings[Keys.KEY_Q] = Math.Vector3(0, 1, 0)
            movementMappings[Keys.KEY_E] = Math.Vector3(0, -1, 0)
            movementMappings[Keys.KEY_W] = Math.Vector3(0, 0, 1)
            movementMappings[Keys.KEY_S] = Math.Vector3(0, 0, -1)
            shiftSensitivity = dataSec.readFloat('shiftSensitivity', 0.5)
            self._ArcadeCamera__shiftKeySensor = KeySensor(movementMappings, shiftSensitivity)
            self._ArcadeCamera__shiftKeySensor.reset(Math.Vector3())
        dynamicsSection = dataSec['dynamics']
        self._ArcadeCamera__impulseOscillator = createOscillatorFromSection(dynamicsSection['impulseOscillator'], False)
        self._ArcadeCamera__movementOscillator = createOscillatorFromSection(dynamicsSection['movementOscillator'], False)
        self._ArcadeCamera__movementOscillator = Math.PyCompoundOscillator(self._ArcadeCamera__movementOscillator, Math.PyOscillator(1.0, Vector3(50), Vector3(20), Vector3(0.01, 0.0, 0.01)))
        self._ArcadeCamera__noiseOscillator = createOscillatorFromSection(dynamicsSection['randomNoiseOscillatorSpherical'])
        self._ArcadeCamera__dynamicCfg.readImpulsesConfig(dynamicsSection)
        self._ArcadeCamera__dynamicCfg['accelerationSensitivity'] = readFloat(dynamicsSection, 'accelerationSensitivity', -1000, 1000, 0.1)
        self._ArcadeCamera__dynamicCfg['frontImpulseToPitchRatio'] = math.radians(readFloat(dynamicsSection, 'frontImpulseToPitchRatio', -1000, 1000, 0.1))
        self._ArcadeCamera__dynamicCfg['sideImpulseToRollRatio'] = math.radians(readFloat(dynamicsSection, 'sideImpulseToRollRatio', -1000, 1000, 0.1))
        self._ArcadeCamera__dynamicCfg['sideImpulseToYawRatio'] = math.radians(readFloat(dynamicsSection, 'sideImpulseToYawRatio', -1000, 1000, 0.1))
        accelerationThreshold = readFloat(dynamicsSection, 'accelerationThreshold', 0.0, 1000.0, 0.1)
        self._ArcadeCamera__dynamicCfg['accelerationThreshold'] = accelerationThreshold
        self._ArcadeCamera__dynamicCfg['accelerationMax'] = readFloat(dynamicsSection, 'accelerationMax', 0.0, 1000.0, 0.1)
        self._ArcadeCamera__dynamicCfg['maxShotImpulseDistance'] = readFloat(dynamicsSection, 'maxShotImpulseDistance', 0.0, 1000.0, 10.0)
        self._ArcadeCamera__dynamicCfg['maxExplosionImpulseDistance'] = readFloat(dynamicsSection, 'maxExplosionImpulseDistance', 0.0, 1000.0, 10.0)
        self._ArcadeCamera__dynamicCfg['zoomExposure'] = readFloat(dynamicsSection, 'zoomExposure', 0.0, 1000.0, 0.25)
        accelerationFilter = math_utils.RangeFilter(self._ArcadeCamera__dynamicCfg['accelerationThreshold'], self._ArcadeCamera__dynamicCfg['accelerationMax'], 100, math_utils.SMAFilter(ArcadeCamera._FILTER_LENGTH))
        maxAccelerationDuration = readFloat(dynamicsSection, 'maxAccelerationDuration', 0.0, 10000.0, ArcadeCamera._DEFAULT_MAX_ACCELERATION_DURATION)
        self._ArcadeCamera__accelerationSmoother = AccelerationSmoother(accelerationFilter, maxAccelerationDuration)
        self._ArcadeCamera__inputInertia = _InputInertia(self._ArcadeCamera__calculateInputInertiaMinMax(), 0.0)
        advancedCollider = dataSec['advancedCollider']
        self._ArcadeCamera__adCfg = dict()
        cfg = self._ArcadeCamera__adCfg
        if advancedCollider is None:
            LOG_ERROR('<advancedCollider> dataSection is not found!')
            cfg['enable'] = False
        else:
            cfg['enable'] = advancedCollider.readBool('enable', False)
            cfg['fovRatio'] = advancedCollider.readFloat('fovRatio', 2.0)
            cfg['rollbackSpeed'] = advancedCollider.readFloat('rollbackSpeed', 1.0)
            cfg['minimalCameraDistance'] = self._cfg['distRange'][0]
            cfg['speedThreshold'] = advancedCollider.readFloat('speedThreshold', 0.1)
            cfg['minimalVolume'] = advancedCollider.readFloat('minimalVolume', 200.0)
            cfg['volumeGroups'] = dict()
            for group in VOLUME_GROUPS_NAMES:
                groups = advancedCollider['volumeGroups']
                cfg['volumeGroups'][group] = CollisionVolumeGroup.fromSection(groups[group])
        self._ArcadeCamera__zoomStateSwitcher.loadConfig(dataSec['additionalZoomStates'])

    def _readBaseCfg(self, dataSec):
        bcfg = self._baseCfg
        bcfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0, 10, 0.01)
        bcfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0, 10, 0.01)
        bcfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0, 10, 0.01)
        bcfg['angleRange'] = readVec2(dataSec, 'angleRange', (0, 0), (180, 180), (10, 110))
        distRangeVec = readVec2(dataSec, 'distRange', (1, 1), (100, 100), (2, 20))
        bcfg['distRange'] = MinMax(distRangeVec.x, distRangeVec.y)
        bcfg['minStartDist'] = readFloat(dataSec, 'minStartDist', bcfg['distRange'][0], bcfg['distRange'][1], bcfg['distRange'][0])
        bcfg['optimalStartDist'] = readFloat(dataSec, 'optimalStartDist', bcfg['distRange'][0], bcfg['distRange'][1], bcfg['distRange'][0])
        bcfg['angleRange'][0] = math.radians(bcfg['angleRange'][0]) - math.pi * 0.5
        bcfg['angleRange'][1] = math.radians(bcfg['angleRange'][1]) - math.pi * 0.5
        bcfg['fovMultMinMaxDist'] = MinMax(readFloat(dataSec, 'fovMultMinDist', 0.1, 100, 1.0), readFloat(dataSec, 'fovMultMaxDist', 0.1, 100, 1.0))
        bcfg['focusRadius'] = readFloat(dataSec, 'focusRadius', -100, 100, 3)
        bcfg['heightAboveBase'] = readFloat(dataSec, 'heightAboveBase', 0, 100, 4)
        bcfg['overScrollProtectOnMax'] = readFloat(dataSec, 'overScrollProtectOnMax', 0, 10, 0)
        bcfg['overScrollProtectOnMin'] = readFloat(dataSec, 'overScrollProtectOnMin', 0, 10, 0)

    def _readUserCfg(self):
        bcfg = self._baseCfg
        ucfg = self._userCfg
        dataSec = Settings.g_instance.userPrefs[Settings.KEY_CONTROL_MODE]
        if dataSec is not None:
            dataSec = dataSec['arcadeMode/camera']
        ucfg['horzInvert'] = False
        ucfg['vertInvert'] = False
        ucfg['sniperModeByShift'] = False
        ucfg['keySensitivity'] = readFloat(dataSec, 'keySensitivity', 0.0, 10.0, 1.0)
        ucfg['sensitivity'] = readFloat(dataSec, 'sensitivity', 0.0, 10.0, 1.0)
        ucfg['scrollSensitivity'] = readFloat(dataSec, 'scrollSensitivity', 0.0, 10.0, 1.0)
        ucfg['startDist'] = readFloat(dataSec, 'startDist', bcfg['distRange'][0], 500, bcfg['optimalStartDist'])
        if ucfg['startDist'] < bcfg['minStartDist']:
            ucfg['startDist'] = bcfg['optimalStartDist']
        ucfg['startAngle'] = readFloat(dataSec, 'startAngle', 5, 180, 60)
        ucfg['startAngle'] = math.radians(ucfg['startAngle']) - math.pi * 0.5
        ucfg['fovMultMinMaxDist'] = MinMax(readFloat(dataSec, 'fovMultMinDist', 0.1, 100, bcfg['fovMultMinMaxDist'].min), readFloat(dataSec, 'fovMultMaxDist', 0.1, 100, bcfg['fovMultMinMaxDist'].max))

    def _makeCfg(self):
        bcfg = self._baseCfg
        ucfg = self._userCfg
        cfg = self._cfg
        cfg['keySensitivity'] = bcfg['keySensitivity']
        cfg['sensitivity'] = bcfg['sensitivity']
        cfg['scrollSensitivity'] = bcfg['scrollSensitivity']
        cfg['angleRange'] = bcfg['angleRange']
        cfg['distRange'] = bcfg['distRange']
        cfg['minStartDist'] = bcfg['minStartDist']
        cfg['focusRadius'] = bcfg['focusRadius']
        cfg['heightAboveBase'] = bcfg['heightAboveBase']
        cfg['overScrollProtectOnMax'] = bcfg['overScrollProtectOnMax']
        cfg['overScrollProtectOnMin'] = bcfg['overScrollProtectOnMin']
        cfg['horzInvert'] = ucfg['horzInvert']
        cfg['vertInvert'] = ucfg['vertInvert']
        cfg['keySensitivity'] = cfg['keySensitivity'] * ucfg['keySensitivity']
        cfg['sensitivity'] = cfg['sensitivity'] * ucfg['sensitivity']
        cfg['scrollSensitivity'] = cfg['scrollSensitivity'] * ucfg['scrollSensitivity']
        cfg['startDist'] = ucfg['startDist']
        cfg['startAngle'] = ucfg['startAngle']
        cfg['fovMultMinMaxDist'] = ucfg['fovMultMinMaxDist']
        cfg['sniperModeByShift'] = ucfg['sniperModeByShift']

    def writeUserPreferences(self):
        ds = Settings.g_instance.userPrefs
        if not ds.has_key(Settings.KEY_CONTROL_MODE):
            ds.write(Settings.KEY_CONTROL_MODE, '')
        ucfg = self._userCfg
        ds = ds[Settings.KEY_CONTROL_MODE]
        ds.writeBool('arcadeMode/camera/horzInvert', ucfg['horzInvert'])
        ds.writeBool('arcadeMode/camera/vertInvert', ucfg['vertInvert'])
        ds.writeFloat('arcadeMode/camera/keySensitivity', ucfg['keySensitivity'])
        ds.writeFloat('arcadeMode/camera/sensitivity', ucfg['sensitivity'])
        ds.writeFloat('arcadeMode/camera/scrollSensitivity', ucfg['scrollSensitivity'])
        ds.writeFloat('arcadeMode/camera/startDist', ucfg['startDist'])
        ds.writeFloat('arcadeMode/camera/fovMultMinDist', ucfg['fovMultMinMaxDist'].min)
        ds.writeFloat('arcadeMode/camera/fovMultMaxDist', ucfg['fovMultMinMaxDist'].max)
        startAngle = math.degrees(ucfg['startAngle'] + math.pi * 0.5)
        ds.writeFloat('arcadeMode/camera/startAngle', startAngle)

    def __onRecreateDevice(self):
        self._ArcadeCamera__aimingSystem.aimMatrix = self._ArcadeCamera__calcAimMatrix()

class ArcadeCameraEpic(ArcadeCamera):
    @staticmethod
    def _getConfigsKey():
        return ArcadeCameraEpic.__name__

    def reload(self):
        if constants.IS_DEVELOPMENT:
            import ResMgr
            ResMgr.purge('gui/avatar_input_handler.xml')
            cameraSec = ResMgr.openSection('gui/avatar_input_handler.xml/arcadeEpicMinefieldMode/camera/')
            self._reloadConfigs(cameraSec)
            return
        else:
            return


