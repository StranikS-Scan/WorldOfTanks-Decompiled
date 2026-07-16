# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hangar_camera_manager.py
from __future__ import absolute_import, division
import math
import logging
from functools import partial
import typing
from collections import namedtuple
import math_utils
import Event
import BigWorld
import Math
import CGF
from WeakMethod import WeakMethodProxy
from shared_utils import first
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.hangar_cameras.hangar_camera_flyby import FlyByComponent
from gui.shared import g_eventBus
from helpers import dependency
from math_common import isAlmostEqual
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.components.vehicle_to_camera_alignment_components import VehicleToCameraAlignmentComponent
from CameraComponents import CameraComponent, ActiveCameraComponent, CameraFlightComponent, OrbitComponent, DofComponent, IdleComponent, ParallaxComponent, FovComponent, ShiftComponent
from constants import IS_CLIENT
if IS_CLIENT:
    from AvatarInputHandler.cameras import FovExtended
    from gui.hangar_cameras.hangar_camera_yaw_filter import HangarCameraYawFilter
    from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
    from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
    from gui.hangar_cameras.hangar_camera_flyby import HangarCameraFlyby
if typing.TYPE_CHECKING:
    from typing import Optional
_EASE_SQUARE_OUT = 2
_DURATION_ = 2.0
_DEFAULT_MOTION_BLUR_ = 0.12
_DOF_START_PROGRESS_ = 0.5
_logger = logging.getLogger(__name__)
DOFParams = namedtuple('DOFParams', ['nearStart',
 'nearDist',
 'farStart',
 'farDist'])
TANK_CAMERA_NAMES = ('Tank', 'Platoon', 'Customization')

class CameraMode(object):
    DEFAULT = 'Tank'
    PLATOON = 'Platoon'
    ALL = (DEFAULT, PLATOON)


class _MouseMoveParams(object):
    __slots__ = ('rotationSensitivity', 'zoomSensitivity', 'yawConstraints', 'pitchConstraints', 'distConstraints', 'distLength', 'shiftPivotLows', 'shiftPivotDistances')

    def __init__(self, rotationSensitivity=0.005, zoomSensitivity=0.003, yawConstraints=Math.Vector2(0, 0), pitchConstraints=Math.Vector2(0, 0), distConstraints=Math.Vector2(0, 0)):
        self.rotationSensitivity = rotationSensitivity
        self.zoomSensitivity = zoomSensitivity
        self.yawConstraints = yawConstraints
        self.pitchConstraints = pitchConstraints
        self.distConstraints = distConstraints
        self.distLength = 0
        self.shiftPivotDistances = Math.Vector3(0, 0, 0)
        self.shiftPivotLows = Math.Vector3(0, 0, 0)
        self.updateLength()

    def updateLength(self):
        self.distLength = 0 if self.distConstraints is None else self.distConstraints[1] - self.distConstraints[0]
        return

    def setPivotShifts(self, shiftPivotLows, shiftPivotDistances):
        self.shiftPivotLows = shiftPivotLows
        self.shiftPivotDistances = shiftPivotDistances


class _FlightParams(object):
    __slots__ = ('duration', 'easing', 'motionBlur', 'route')

    def __init__(self, duration=_DURATION_, easing=_EASE_SQUARE_OUT, motionBlur=_DEFAULT_MOTION_BLUR_, route=None):
        self.duration = duration
        self.easing = easing
        self.motionBlur = motionBlur
        self.route = route


class _DOFParams(object):
    __slots__ = ('active', 'nearStart', 'nearDist', 'farStart', 'farDist')

    def __init__(self, active=False, nearStart=0.0, nearDist=0.0, farStart=0.0, farDist=0.0):
        self.active = active
        self.nearStart = nearStart
        self.nearDist = nearDist
        self.farStart = farStart
        self.farDist = farDist


class HangarCameraSystem(CGF.System):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    CameraActivated = CGF.ActivateReaction(CGF.ReactRo(CameraComponent), CGF.Has(CGF.TransformComponent))
    OrbitActivated = CGF.ActivateReaction(CGF.ReactRo(OrbitComponent), CGF.Ro(CameraComponent))
    ActiveCameraIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(ActiveCameraComponent))
    CameraIterate = CGF.IterateReaction(CGF.GameObject, CGF.Ro(CameraComponent))
    OrbitIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Ro(OrbitComponent), CGF.Ro(CameraComponent))
    ActiveCameraAccess = CGF.AccessReaction(CGF.Ro(ActiveCameraComponent))
    VehicleToCameraAlignmentAccess = CGF.AccessReaction(CGF.Ro(VehicleToCameraAlignmentComponent))
    TransformAccess = CGF.AccessReaction(CGF.Ro(CGF.TransformComponent))
    OrbitAccess = CGF.AccessReaction(CGF.ActiveOnly, CGF.Ro(OrbitComponent))
    CameraAccess = CGF.AccessReaction(CGF.Ro(CameraComponent))
    FovAccess = CGF.AccessReaction(CGF.Ro(FovComponent))
    DofAccess = CGF.AccessReaction(CGF.Ro(DofComponent))
    IdleAccess = CGF.AccessReaction(CGF.Ro(IdleComponent))
    ParallaxAccess = CGF.AccessReaction(CGF.Ro(ParallaxComponent))
    CameraFlightAccess = CGF.AccessReaction(CGF.Ro(CameraFlightComponent))
    ShiftAccess = CGF.AccessReaction(CGF.Ro(ShiftComponent))
    FlyByAccess = CGF.AccessReaction(CGF.Ro(FlyByComponent))
    Reactions = CGF.Reactions(CameraActivated, OrbitActivated, ActiveCameraIterate, OrbitIterate, CameraIterate, ActiveCameraAccess, TransformAccess, OrbitAccess, CameraAccess, FovAccess, ShiftAccess, DofAccess, IdleAccess, ParallaxAccess, CameraFlightAccess, FlyByAccess, VehicleToCameraAlignmentAccess)

    def update(self):
        for cameraComponent in self.reaction(self.CameraActivated):
            self.onCameraAdded(cameraComponent)

        for _, cameraComponent in self.reaction(self.OrbitActivated):
            self.onOrbitCameraActivated(cameraComponent)

        self.tick()

    def __init__(self):
        super(HangarCameraSystem, self).__init__()
        self.__cam = None
        self.__flightCam = None
        self.__customizationHelper = None
        self.__yawCameraFilter = None
        self.__cameraIdle = None
        self.__cameraParallax = None
        self.__cameraFlyby = None
        self.__mouseMoveParams = _MouseMoveParams()
        self.__flightParams = _FlightParams()
        self.__vehicleToCameraCompIsActive = False
        self.__minDist = None
        self.__prevHorizontalFov = None
        self.__currentHorizontalFov = None
        self.__customFov = False
        self.__prevDOFParams = None
        self.__currentDOFParams = None
        self.__rotationEnabled = True
        self.__zoomEnabled = True
        self.__cameraMode = CameraMode.DEFAULT
        self.__cameraName = None
        self.__orbitCameraMap = {}
        self.__isActive = False
        self.__flybyCallback = None
        self.onCameraSwitched = Event.Event()
        self.onNewCameraAdded = Event.Event()
        return

    def onMappingLoaded(self):
        if not self._hangarSpace.inited or self.__isActive:
            return
        else:
            self.__cam = BigWorld.SphericalTransitionCamera()
            self.__cam.isHangar = True
            self.__cam.spaceID = self._hangarSpace.spaceID
            self.__cam.pivotMinDist = 0.0
            self.__cam.pivotPosition = Math.Vector3(0.0, 0.0, 0.0)
            self.__cam.setDynamicCollisions(True)
            self.__cameraParallax = HangarCameraParallax(self.__cam)
            self.__cameraIdle = HangarCameraIdle(self.__cam)
            self.__cameraFlyby = HangarCameraFlyby(self.__cam)
            self.__customizationHelper = BigWorld.PyCustomizationHelper(None, 0, False, None)
            g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            fovInstance = FovExtended.instance()
            fovInstance.onSetFovSettingEvent += self.__onSetFovSetting
            fovInstance.refreshFov()
            self.__prevDOFParams = _DOFParams()
            self.__currentDOFParams = _DOFParams()
            self.__currentHorizontalFov = fovInstance.horizontalFov
            self.__isActive = True
            _logger.info('HangarCameraSystem::activate')
            return

    def onMappingUnloaded(self):
        if not self.__isActive:
            return
        else:
            self.__cam = None
            self.__customizationHelper = None
            g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            FovExtended.instance().onSetFovSettingEvent -= self.__onSetFovSetting
            activeCameraIterate = self.reaction(self.ActiveCameraIterate)
            q = CGF.CommandQueue(self.gom)
            for gameObject, _ in activeCameraIterate:
                q.removeComponent(gameObject, ActiveCameraComponent)

            self.__deactivateCameraComponents()
            self.__cameraParallax.destroy()
            self.__cameraParallax = None
            self.__cameraIdle.destroy()
            self.__cameraIdle = None
            self.__cameraFlyby.fini()
            self.__cameraFlyby = None
            self.__isActive = False
            self.__flybyCallback = None
            return

    def onCameraAdded(self, cameraComponent):
        if not self.__isActive:
            return
        self.onNewCameraAdded(cameraComponent.name)
        if cameraComponent.name == self.__cameraMode:
            if not self.isCameraSwitching():
                self.switchToTank()
            _logger.info('HangarCameraSystem::onTankCameraAdded')

    def onOrbitCameraActivated(self, cameraComponent):
        if cameraComponent.name in self.__orbitCameraMap:
            self.__orbitCameraMap[cameraComponent.name]()

    def isCameraAdded(self, cameraName):
        cameraIterate = self.reaction(self.CameraIterate)
        for _, cameraComponent in cameraIterate:
            if cameraComponent.name == cameraName:
                return True

        return False

    def isCameraSwitching(self):
        return self.__flightCam and self.__flightCam.isInTransition()

    def getCurrentCameraName(self):
        return self.__cameraName

    def switchToTank(self, instantly=True, resetTransform=True):
        self.switchByCameraName(self.__cameraMode, instantly, resetTransform)

    def cameraExists(self, cameraName):
        cameraIterate = self.reaction(self.CameraIterate)
        for _, cameraComponent in cameraIterate:
            if cameraComponent.name == cameraName:
                return True

        return False

    def findCameraGameObjectByName(self, name):
        cameraIterate = self.reaction(self.CameraIterate)
        gameObject = None
        for go, cameraComponent in cameraIterate:
            if cameraComponent.name == name:
                gameObject = go
                break

        return gameObject

    def getCameraFlyBy(self):
        flyByComponent = None
        activeCameraIterate = self.reaction(self.ActiveCameraIterate)
        go, _ = first(activeCameraIterate)
        if go is not None:
            flyByAccess = self.reaction(self.FlyByAccess)
            flyByComponent = flyByAccess.find(go)
        return flyByComponent

    def activateCamera(self, name):
        gameObject = None
        prevCameraName = None
        self.__vehicleToCameraCompIsActive = False
        q = CGF.CommandQueue(self.gom)
        activeCameraAccess = self.reaction(self.ActiveCameraAccess)
        vehicleToCameraAlignmentAccess = self.reaction(self.VehicleToCameraAlignmentAccess)
        cameraIterate = self.reaction(self.CameraIterate)
        for go, cameraComponent in cameraIterate:
            isActive = activeCameraAccess.contains(go)
            if isActive:
                prevCameraName = cameraComponent.name
                if cameraComponent.name != name:
                    q.removeComponent(go, ActiveCameraComponent)
            if cameraComponent.name == name:
                gameObject = go
                if not isActive:
                    q.createComponent(go, ActiveCameraComponent)
                if vehicleToCameraAlignmentAccess.contains(go):
                    self.__vehicleToCameraCompIsActive = True

        if gameObject is not None:
            self.__cameraName = name
        return (gameObject, prevCameraName)

    def switchByCameraName(self, name, instantly=True, resetTransform=True, forceUpdate=True):
        if self.__cameraName == name:
            _logger.debug('Camera is already installed: %s', name)
            self.onCameraSwitched(self.__cameraName)
            return
        orbitIterate = self.reaction(self.OrbitIterate)
        for _, __, cameraComponent in orbitIterate:
            if cameraComponent.name == name:
                self.__switchByCameraName(name, instantly, resetTransform, forceUpdate)
                return

        self.__orbitCameraMap[name] = partial(WeakMethodProxy(self.__switchByCameraName), name, instantly, resetTransform, forceUpdate)

    def __switchByCameraName(self, name, instantly=True, resetTransform=True, forceUpdate=True):
        gameObject, prevCameraName = self.activateCamera(name)
        if gameObject is None:
            _logger.warning("Can't find camera: %s", name)
            return
        else:
            self.__cam.stop()
            if instantly:
                self.__setupCamera(gameObject, resetTransform, forceUpdate)
                BigWorld.camera(self.__cam)
                self.__onCameraSwitched()
            else:
                matrix = Math.Matrix(BigWorld.camera().matrix)
                tempCam = BigWorld.FreeCamera()
                tempCam.set(matrix)
                BigWorld.camera(tempCam)
                self.__setupCamera(gameObject, resetTransform, forceUpdate)
                self.__setupFlightParams(gameObject, prevCameraName)
                self.__customizationHelper.setMotionBlurAmount(self.__flightParams.motionBlur)
                self.__startFlight(matrix, Math.Matrix(self.__cam.matrix))
            return

    def resetCameraTarget(self, duration=0, resetRotation=True, resetDistance=True):
        if BigWorld.camera() != self.__cam:
            return
        else:
            targetPos, yaw, pitch, distance, distConstraints = (None, None, None, None, None)
            activeCameraIterate = self.reaction(self.ActiveCameraIterate)
            transformAccess = self.reaction(self.TransformAccess)
            orbitAccess = self.reaction(self.OrbitAccess)
            shiftAccess = self.reaction(self.ShiftAccess)
            for gameObject, _ in activeCameraIterate:
                parent = self.hierarchy.getParent(gameObject)
                parentTransformComponent = transformAccess.find(parent)
                transformComponent = transformAccess.find(gameObject)
                orbitComponent = orbitAccess.find(gameObject)
                if not orbitComponent or not parentTransformComponent or not transformComponent:
                    return
                targetPos = parentTransformComponent.worldTransform.translation
                worldYaw = parentTransformComponent.worldTransform.yaw
                worldPitch = parentTransformComponent.worldTransform.pitch
                yaw = self.__normaliseAngle(orbitComponent.currentYaw + worldYaw + math.pi) if resetRotation else None
                pitch = self.__normaliseAngle(orbitComponent.currentPitch + worldPitch) if resetRotation else None
                distance = orbitComponent.currentDist if resetDistance else None
                distConstraints = orbitComponent.distLimits
                self.__setCameraShift(shiftAccess.find(gameObject))

            self.moveCamera(targetPos, yaw=yaw, pitch=pitch, distance=distance, duration=duration, distConstraints=distConstraints)
            return

    def enableMovementByMouse(self, enableRotation=True, enableZoom=True):
        self.__cameraParallax.setEnabled(enableRotation)
        self.__rotationEnabled = enableRotation
        self.__zoomEnabled = enableZoom

    def enablePlatoonMode(self, enable=True):
        cameraMode = CameraMode.PLATOON if enable else CameraMode.DEFAULT
        if self.__cameraMode != cameraMode and self.__cameraName in CameraMode.ALL:
            self.__cameraMode = cameraMode
            self.switchToTank(False, False)

    def setDOFParams(self, enabled, dofParams=None):
        if dofParams:
            self.__customizationHelper.setDOFparams(*dofParams)
        self.__customizationHelper.setDOFenabled(enabled)

    def setMinDist(self, value):
        if not self.__isActive or self.__cameraName is None:
            self.__minDist = value
            return
        elif self.__cameraName not in TANK_CAMERA_NAMES:
            return
        else:
            self.__mouseMoveParams.distConstraints[0] = math_utils.clamp(self.__mouseMoveParams.distConstraints[0], self.__mouseMoveParams.distConstraints[1], value)
            self.__mouseMoveParams.updateLength()
            dist = math_utils.clamp(self.__mouseMoveParams.distConstraints[0], self.__mouseMoveParams.distConstraints[1], self.__cam.pivotMaxDist)
            self.__cam.pivotMaxDist = dist
            dynamicFov = self.__calculateDynamicFov()
            if dynamicFov:
                self.__currentHorizontalFov = dynamicFov
            return

    def moveCamera(self, targetPos=None, yaw=None, pitch=None, distance=None, duration=0, distConstraints=None):
        targetMatrix = Math.Matrix(self.__cam.target)
        sourceMatrix = Math.Matrix(self.__cam.source)
        pivotMaxDist = self.__cam.pivotMaxDist
        cameraYaw = sourceMatrix.yaw
        cameraPitch = sourceMatrix.pitch
        if self.__vehicleToCameraCompIsActive:
            from vehicle_systems.components.vehicle_to_camera_alignment_components import VehicleToCameraAlignmentSystem
            vehicleToCameraAlignmentSystem = CGF.getSystem(self._hangarSpace.spaceID, VehicleToCameraAlignmentSystem)
            if vehicleToCameraAlignmentSystem and vehicleToCameraAlignmentSystem.getTargetPosition():
                targetPos = vehicleToCameraAlignmentSystem.getTargetPosition()
        if targetPos is not None:
            targetMatrix.setTranslate(targetPos)
        if yaw is not None:
            cameraYaw = self.__yawCameraFilter.toLimit(yaw)
        if pitch is not None:
            cameraPitch = math_utils.clamp(self.__mouseMoveParams.pitchConstraints[0], self.__mouseMoveParams.pitchConstraints[1], pitch)
        if distConstraints is not None:
            self.__mouseMoveParams.distConstraints = distConstraints
            self.__mouseMoveParams.updateLength()
            self.setMinDist(distConstraints[0])
        if distance is not None:
            pivotMaxDist = math_utils.clamp(self.__mouseMoveParams.distConstraints[0], self.__mouseMoveParams.distConstraints[1], distance)
        sourceMatrix.setRotateYPR(Math.Vector3(cameraYaw, cameraPitch, 0.0))
        self.__cam.moveTo(targetMatrix, sourceMatrix, pivotMaxDist, duration)
        return

    def activateCameraFlyby(self, callback=None):
        if self.__cameraFlyby is not None:
            self.enableMovementByMouse(False, False)
            self.__cameraFlyby.activate(self.__onFlybyFinished)
            self.__flybyCallback = callback
        else:
            _logger.warning('Could not start camera fly-by, camera manager is not activated')
        return

    def deactivateCameraFlyby(self):
        if self.__cameraFlyby is not None:
            self.__cameraFlyby.deactivate()
            if self.__flybyCallback is not None:
                self.__flybyCallback()
                self.__flybyCallback = None
        else:
            _logger.warning('Could not interact camera fly-by, camera manager is not activated')
        return

    def __onFlybyFinished(self):
        self.enableMovementByMouse(True, True)
        if self.__flybyCallback is not None:
            self.__flybyCallback()
            self.__flybyCallback = None
        return

    def __startFlight(self, prevMatrix, targetMatrix):
        if self.__flightParams.route:
            self.__flightCam = BigWorld.RouteTransitionCamera()
            self.__flightCam.spaceID = self._hangarSpace.spaceID
            route = []
            invertMatrix = prevMatrix
            invertMatrix.invert()
            route.append(invertMatrix)
            route.extend(self.__flightParams.route)
            invertMatrix = targetMatrix
            invertMatrix.invert()
            route.append(invertMatrix)
            self.__flightCam.startAlongRoute(route, self.__flightParams.duration, self.__flightParams.easing)
        else:
            self.__flightCam = BigWorld.CollidableTransitionCamera()
            self.__flightCam.spaceID = self._hangarSpace.spaceID
            self.__flightCam.start(prevMatrix, targetMatrix, self.__flightParams.duration, self.__flightParams.easing)
        BigWorld.camera(self.__flightCam)

    def __handleLobbyViewMouseEvent(self, event):
        if self.isCameraSwitching() or self.__cam.isInTransition():
            return
        ctx = event.ctx
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        if self.__rotationEnabled:
            currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
            currentYaw = currentMatrix.yaw
            yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, ctx['dx'])
            pitch -= ctx['dy'] * self.__mouseMoveParams.rotationSensitivity
            pitch = math_utils.clamp(self.__mouseMoveParams.pitchConstraints[0], self.__mouseMoveParams.pitchConstraints[1], pitch)
            mat = Math.Matrix()
            mat.setRotateYPR((yaw, pitch, 0.0))
            self.__cam.source = mat
        if self.__zoomEnabled:
            if ctx['dz'] < 0.0:
                dist = self.__cam.pivotMaxDist
            else:
                dist = self.__cam.targetMaxDist
            dist -= ctx['dz'] * self.__mouseMoveParams.zoomSensitivity
            dist = math_utils.clamp(self.__mouseMoveParams.distConstraints[0], self.__mouseMoveParams.distConstraints[1], dist)
            if self.__mouseMoveParams.distLength > 0.0:
                prc = (dist - self.__mouseMoveParams.distConstraints[0]) / self.__mouseMoveParams.distLength
                pivotPos = self.__mouseMoveParams.shiftPivotDistances * prc
            else:
                pivotPos = Math.Vector3(0.0, 0.0, 0.0)
            if not self.__vehicleToCameraCompIsActive:
                self.__cam.pivotPosition = pivotPos + self.__mouseMoveParams.shiftPivotLows
            self.__cam.pivotMaxDist = dist

    def __calculateDynamicFov(self):
        minDist, maxDist = self.__mouseMoveParams.distConstraints
        if self.__customFov or not self._settingsCore.getSetting('dynamicFov') or abs(maxDist - minDist) <= 0.001:
            return None
        else:
            relativeDist = (self.__cam.pivotMaxDist - minDist) / (maxDist - minDist)
            _, minFov, maxFov = self._settingsCore.getSetting('fov')
            return math_utils.lerp(minFov, maxFov, relativeDist)

    def __normaliseAngle(self, angle):
        eps = 0.001
        if angle > math.pi + eps:
            return angle - 2 * math.pi
        return angle + 2 * math.pi if angle < -math.pi - eps else angle

    def __setupCamera(self, gameObject, resetTransform=True, forceUpdate=True):
        cameraAccess = self.reaction(self.CameraAccess)
        transformAccess = self.reaction(self.TransformAccess)
        orbitAccess = self.reaction(self.OrbitAccess)
        cameraComponent = cameraAccess.find(gameObject)
        parent = self.hierarchy.getParent(gameObject)
        parentTransformComponent = transformAccess.find(parent)
        orbitComponent = orbitAccess.find(gameObject)
        if not cameraComponent or not orbitComponent or not parentTransformComponent:
            return
        else:
            worldYaw = parentTransformComponent.worldTransform.yaw
            worldPitch = parentTransformComponent.worldTransform.pitch
            yawLimits = orbitComponent.yawLimits + Math.Vector2(worldYaw, worldYaw) + Math.Vector2(math.pi, math.pi)
            pitchLimits = orbitComponent.pitchLimits + Math.Vector2(worldPitch, worldPitch)
            yawConstraints = Math.Vector2(self.__normaliseAngle(yawLimits.x), self.__normaliseAngle(yawLimits.y))
            pitchConstraints = Math.Vector2(self.__normaliseAngle(pitchLimits.x), self.__normaliseAngle(pitchLimits.y))
            distConstraints = orbitComponent.distLimits
            self.__mouseMoveParams = _MouseMoveParams(cameraComponent.rotationSensitivity, cameraComponent.zoomSensitivity, yawConstraints, pitchConstraints, distConstraints)
            self.__yawCameraFilter = HangarCameraYawFilter(yawConstraints[0], orbitComponent.yawLimits.y - orbitComponent.yawLimits.x, cameraComponent.rotationSensitivity)
            if not self.__vehicleToCameraCompIsActive:
                shiftAccess = self.reaction(self.ShiftAccess)
                self.__setCameraShift(shiftAccess.find(gameObject))
            if resetTransform:
                targetPos = parentTransformComponent.worldTransform.translation
                yaw = self.__normaliseAngle(orbitComponent.currentYaw + worldYaw + math.pi)
                pitch = self.__normaliseAngle(orbitComponent.currentPitch + worldPitch)
                distance = orbitComponent.currentDist
            else:
                targetPos = Math.Matrix(self.__cam.target).translation
                source = Math.Matrix(self.__cam.source)
                yaw = self.__yawCameraFilter.toLimit(source.yaw)
                pitch = math_utils.clamp(pitchConstraints[0], pitchConstraints[1], source.pitch)
                distance = math_utils.clamp(distConstraints[0], distConstraints[1], self.__cam.pivotMaxDist)
            targetMatrix = Math.Matrix()
            targetMatrix.setTranslate(targetPos)
            if self.__vehicleToCameraCompIsActive:
                from vehicle_systems.components.vehicle_to_camera_alignment_components import VehicleToCameraAlignmentSystem
                vehicleToCameraAlignmentSystem = CGF.getSystem(self._hangarSpace.spaceID, VehicleToCameraAlignmentSystem)
                if vehicleToCameraAlignmentSystem and vehicleToCameraAlignmentSystem.getTargetPosition():
                    targetMatrix.setTranslate(vehicleToCameraAlignmentSystem.getTargetPosition())
            self.__cam.target = targetMatrix
            sourceMatrix = Math.Matrix()
            sourceMatrix.setRotateYPR(Math.Vector3(yaw, pitch, 0.0))
            self.__cam.source = sourceMatrix
            self.__cam.maxDistHalfLife = cameraComponent.fluency
            self.__cam.turningHalfLife = cameraComponent.fluency
            self.__cam.movementHalfLife = cameraComponent.fluency
            self.__cam.pivotMaxDist = distance
            if forceUpdate:
                self.__cam.forceUpdate()
            self.__prevHorizontalFov = FovExtended.instance().getFovAbsoluteValue()
            fovAccess = self.reaction(self.FovAccess)
            fovComponent = fovAccess.find(gameObject)
            if fovComponent:
                self.__customFov = True
                self.__currentHorizontalFov = math.degrees(fovComponent.value)
            else:
                self.__customFov = False
                dynamicFov = self.__calculateDynamicFov()
                if dynamicFov:
                    self.__currentHorizontalFov = dynamicFov
                else:
                    self.__currentHorizontalFov = FovExtended.instance().horizontalFov
            self.__prevDOFParams = self.__currentDOFParams
            dofAccess = self.reaction(self.DofAccess)
            dofComponent = dofAccess.find(gameObject)
            if dofComponent:
                self.__currentDOFParams = _DOFParams(True, dofComponent.nearStart, dofComponent.nearDist, dofComponent.farStart, dofComponent.farDist)
                if not self.__prevDOFParams.active:
                    farDist = targetPos.distTo(BigWorld.camera().position) + dofComponent.nearStart + dofComponent.nearDist + dofComponent.farStart + dofComponent.farDist
                    self.__prevDOFParams = _DOFParams(active=False, farDist=farDist)
            else:
                self.__currentDOFParams = _DOFParams()
                self.__customizationHelper.setDOFenabled(False)
            self.__deactivateCameraComponents()
            idleAccess = self.reaction(self.IdleAccess)
            idleComponent = idleAccess.find(gameObject)
            if idleComponent:
                pitchParams = HangarCameraIdle.IdleParams()
                distParams = HangarCameraIdle.IdleParams()
                pitchParams.minValue = idleComponent.pitchLimits[0]
                pitchParams.maxValue = idleComponent.pitchLimits[1]
                pitchParams.period = idleComponent.pitchPeriod
                distParams.minValue = idleComponent.distLimits[0]
                distParams.maxValue = idleComponent.distLimits[1]
                distParams.period = idleComponent.distPeriod
                self.__cameraIdle.initialize(idleComponent.easingInTime, pitchParams, distParams, idleComponent.yawPeriod)
            parallaxAccess = self.reaction(self.ParallaxAccess)
            parallaxComponent = parallaxAccess.find(gameObject)
            if parallaxComponent:
                self.__cameraParallax.initialize(parallaxComponent.distanceDelta, parallaxComponent.angelsDelta, parallaxComponent.smoothing)
            if self.__minDist is not None:
                self.setMinDist(self.__minDist)
                self.__minDist = None
            self.enableMovementByMouse()
            return

    def __setCameraShift(self, shiftComponent):
        if shiftComponent:
            shiftPivotDistances = shiftComponent.shiftPivotDistances
            shiftPivotLows = shiftComponent.shiftPivotLows
            movementHalfLifeMultiplier = shiftComponent.pivotHalfTimeMultiplier
        else:
            shiftPivotDistances = Math.Vector3(0.0, 0.0, 0.0)
            shiftPivotLows = Math.Vector3(0.0, 0.0, 0.0)
            movementHalfLifeMultiplier = 2.0
        self.__cam.movementHalfLifeMultiplier = movementHalfLifeMultiplier
        self.__cam.pivotPosition = shiftPivotLows + shiftPivotDistances
        self.__mouseMoveParams.setPivotShifts(shiftPivotLows, shiftPivotDistances)

    def __setupFlightParams(self, gameObject, prevCameraName):
        self.__flightParams = _FlightParams()
        if not prevCameraName:
            return
        else:
            children = self.hierarchy.getDirectChildren(gameObject)
            if not children:
                return
            cameraFlightComponent = None
            flightAccess = self.reaction(self.CameraFlightAccess)
            for child in children:
                flightComponent = flightAccess.find(child)
                if flightComponent and flightComponent.cameraName and flightComponent.cameraName == prevCameraName:
                    cameraFlightComponent = flightComponent
                    break

            if not cameraFlightComponent:
                return
            transforms = []
            transformAccess = self.reaction(self.TransformAccess)
            cameraAccess = self.reaction(self.CameraAccess)
            for point in cameraFlightComponent.points:
                cameraComponent = cameraAccess.find(point)
                transformComponent = transformAccess.find(point)
                if cameraComponent and transformComponent:
                    transforms.append(transformComponent.worldTransform)

            self.__flightParams = _FlightParams(cameraFlightComponent.duration, cameraFlightComponent.easing, cameraFlightComponent.motionBlur, transforms)
            return

    def __onSetFovSetting(self):
        if self.__customFov:
            FovExtended.instance().setFovByAbsoluteValue(self.__currentHorizontalFov)
        else:
            self.__currentHorizontalFov = FovExtended.instance().horizontalFov

    def __deactivateCameraComponents(self):
        self.__cameraIdle.deactivate()
        self.__cameraParallax.deactivate()
        if self.__cameraFlyby.isActive:
            self.__cameraFlyby.deactivate()

    def __activateDOF(self):
        self.__customizationHelper.setDOFenabled(self.__currentDOFParams.active)
        self.__customizationHelper.setDOFparams(self.__currentDOFParams.nearStart, self.__currentDOFParams.nearDist, self.__currentDOFParams.farStart, self.__currentDOFParams.farDist)

    def __onCameraSwitched(self):
        self.onCameraSwitched(self.__cameraName)
        self.__customizationHelper.setMotionBlurAmount(_DEFAULT_MOTION_BLUR_)
        self.__activateDOF()
        self.__cameraIdle.activate()
        self.__cameraParallax.activate()
        if self.__flightCam:
            self.__flightCam.finish()
            self.__flightCam = None
        return

    def tick(self):
        if not self.__flightCam:
            if self.__cam and self.__cam.isInTransition():
                progress = self.__cam.easingProgress()
                self.__interpolateFOV(progress)
                self.__interpolateDOF(progress)
            else:
                dynamicFov = self.__calculateDynamicFov()
                fovInstance = FovExtended.instance()
                if dynamicFov:
                    self.__currentHorizontalFov = dynamicFov
                    fovInstance.setFovByAbsoluteValue(dynamicFov, 0.1)
                elif not isAlmostEqual(fovInstance.getFovAbsoluteValue(), self.__currentHorizontalFov, epsilon=0.1):
                    self.__interpolateFOV(1.0)
            return
        if BigWorld.camera() == self.__cam:
            return
        if self.isCameraSwitching():
            progress = self.__flightCam.easingProgress()
            self.__interpolateFOV(progress)
            self.__interpolateDOF(progress)
        else:
            BigWorld.camera(self.__cam)
            self.__onCameraSwitched()

    def __interpolateFOV(self, progress):
        if self.__prevHorizontalFov != self.__currentHorizontalFov:
            newFov = self.__prevHorizontalFov + progress * (self.__currentHorizontalFov - self.__prevHorizontalFov)
            FovExtended.instance().setFovByAbsoluteValue(newFov)
            if isAlmostEqual(newFov, self.__currentHorizontalFov, epsilon=0.01):
                self.__prevHorizontalFov = self.__currentHorizontalFov

    def __interpolateDOF(self, progress):
        if self.__currentDOFParams.active and (self.__prevDOFParams.active or progress > _DOF_START_PROGRESS_):
            nearStart = self.__prevDOFParams.nearStart + progress * (self.__currentDOFParams.nearStart - self.__prevDOFParams.nearStart)
            nearDist = self.__prevDOFParams.nearDist + progress * (self.__currentDOFParams.nearDist - self.__prevDOFParams.nearDist)
            farStart = self.__prevDOFParams.farStart + progress * (self.__currentDOFParams.farStart - self.__prevDOFParams.farStart)
            farDist = self.__prevDOFParams.farDist + progress * (self.__currentDOFParams.farDist - self.__prevDOFParams.farDist)
            self.__customizationHelper.setDOFenabled(True)
            self.__customizationHelper.setDOFparams(nearStart, nearDist, farStart, farDist)
