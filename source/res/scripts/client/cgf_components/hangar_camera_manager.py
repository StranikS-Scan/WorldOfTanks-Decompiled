# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hangar_camera_manager.py
import math
import logging
from collections import namedtuple
import math_utils
import Event
import BigWorld
import Math
import CGF
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from GenericComponents import TransformComponent
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import tickGroup, onAddedQuery
from CameraComponents import CameraComponent, CameraFlightComponent, OrbitComponent, DofComponent, IdleComponent, ParallaxComponent, FovComponent, ShiftComponent
from constants import IS_CLIENT
if IS_CLIENT:
    from AvatarInputHandler.cameras import FovExtended
    from gui.hangar_cameras.hangar_camera_yaw_filter import HangarCameraYawFilter
    from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
    from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
    from gui.hangar_cameras.hangar_camera_flyby import HangarCameraFlyby
_EASE_SQUARE_INOUT = 3
_MIN_DURATION_ = 2.0
_MAX_DURATION_ = 3.0
_DEFAULT_MOTION_BLUR_ = 0.12
_DOF_START_PROGRESS_ = 0.5
_logger = logging.getLogger(__name__)
DOFParams = namedtuple('DOFParams', ['nearStart',
 'nearDist',
 'farStart',
 'farDist'])

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
    __slots__ = ('minDuration', 'maxDuration', 'positionEasing', 'rotationEasing', 'motionBlur', 'route')

    def __init__(self, minDuration=_MIN_DURATION_, maxDuration=_MAX_DURATION_, positionEasing=_EASE_SQUARE_INOUT, rotationEasing=_EASE_SQUARE_INOUT, motionBlur=_DEFAULT_MOTION_BLUR_, route=None):
        self.minDuration = minDuration
        self.maxDuration = maxDuration
        self.positionEasing = positionEasing
        self.rotationEasing = rotationEasing
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


@registerComponent
class CurrentCameraObject(object):
    domain = CGF.DomainOption.DomainClient


class HangarCameraManager(CGF.ComponentManager):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args):
        super(HangarCameraManager, self).__init__(*args)
        self.__cam = None
        self.__flightCam = None
        self.onCameraSwitched = None
        self.onCameraSwitchCancel = None
        self.__isInSwitching = False
        self.__customizationHelper = None
        self.__yawCameraFilter = None
        self.__cameraIdle = None
        self.__cameraParallax = None
        self.__cameraFlyby = None
        self.__mouseMoveParams = _MouseMoveParams()
        self.__flightParams = _FlightParams()
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
        self.__isActive = False
        self.__flybyCallback = None
        return

    def activate(self):
        if not self._hangarSpace.inited or self.__isActive:
            return
        else:
            self.__cam = BigWorld.SphericalTransitionCamera()
            self.__cam.isHangar = True
            self.__cam.spaceID = self._hangarSpace.spaceID
            self.__cam.pivotMinDist = 0.0
            self.__cam.pivotPosition = Math.Vector3(0.0, 0.0, 0.0)
            self.__cam.setDynamicCollisions(True)
            BigWorld.camera(self.__cam)
            self.__cameraParallax = HangarCameraParallax(self.__cam)
            self.__cameraIdle = HangarCameraIdle(self.__cam)
            self.__cameraFlyby = HangarCameraFlyby(self.__cam)
            self.__customizationHelper = BigWorld.PyCustomizationHelper(None, 0, False, None)
            g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            FovExtended.instance().onSetFovSettingEvent += self.__onSetFovSetting
            self.__prevDOFParams = _DOFParams()
            self.__currentDOFParams = _DOFParams()
            self.onCameraSwitched = Event.Event()
            self.onCameraSwitchCancel = Event.Event()
            self.__currentHorizontalFov = FovExtended.instance().horizontalFov
            self.__isActive = True
            _logger.info('HangarCameraManager::activate')
            return

    def deactivate(self):
        if not self.__isActive:
            return
        else:
            self.__cam = None
            self.__customizationHelper = None
            g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            FovExtended.instance().onSetFovSettingEvent -= self.__onSetFovSetting
            self.onCameraSwitched.clear()
            self.onCameraSwitched = None
            self.onCameraSwitchCancel.clear()
            self.onCameraSwitchCancel = None
            currentCameraQuery = CGF.Query(self.spaceID, (CGF.GameObject, CurrentCameraObject))
            for gameObject, _ in currentCameraQuery:
                gameObject.removeComponentByType(CurrentCameraObject)

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

    @onAddedQuery(CGF.GameObject, CameraComponent, TransformComponent, tickGroup='postHierarchyUpdate')
    def onCameraAdded(self, go, cameraComponent, transformComponent):
        if not self.__isActive:
            return
        if cameraComponent.name == self.__cameraMode:
            self.switchToTank()
            _logger.info('HangarCameraManager::onCameraAdded')

    def getCurrentCameraName(self):
        return self.__cameraName

    def getCurrentCameraPosition(self):
        return self.__cam.position

    def getCurrentCameraDirection(self):
        return self.__cam.direction

    def switchToTank(self, instantly=True, resetTransform=True):
        self.switchByCameraName(self.__cameraMode, instantly, resetTransform)

    def switchByCameraName(self, name, instantly=True, resetTransform=True):
        self.__onCameraSwitchCancel(name)
        self.__cameraName = name
        self.__isInSwitching = True
        cameraQuery = CGF.Query(self._hangarSpace.spaceID, (CGF.GameObject, CameraComponent))
        gameObject = None
        prevCameraName = None
        for go, cameraComponent in cameraQuery:
            if cameraComponent.name == name:
                if go.findComponentByType(CurrentCameraObject) is None:
                    go.createComponent(CurrentCameraObject)
                    gameObject = go
                elif self.__flightCam and self.__flightCam.isInTransition() and self.__flightCam == BigWorld.camera():
                    _logger.warning('Camera is already flying: %s', name)
                    return
                else:
                    _logger.warning('Camera already installed: %s', name)
                    self.__onCameraSwitched()
                    return

            if go.findComponentByType(CurrentCameraObject) is not None:
                prevCameraName = cameraComponent.name
                go.removeComponentByType(CurrentCameraObject)

        if gameObject is None:
            _logger.warning("Can't find camera: %s", name)
            self.__onCameraSwitchCancel(name)
            return
        else:
            self.__cam.stop()
            if instantly:
                self.__setupCamera(gameObject, resetTransform)
                FovExtended.instance().setFovByAbsoluteValue(self.__currentHorizontalFov)
                if self.__flightCam:
                    self.__flightCam.finish()
                    self.__flightCam = None
                BigWorld.camera(self.__cam)
                self.__onCameraSwitched()
            else:
                matrix = Math.Matrix(BigWorld.camera().matrix)
                tempCam = BigWorld.FreeCamera()
                tempCam.set(matrix)
                BigWorld.camera(tempCam)
                self.__setupCamera(gameObject, resetTransform)
                self.__setupFlightParams(gameObject, prevCameraName)
                self.__customizationHelper.setMotionBlurAmount(self.__flightParams.motionBlur)
                self.__startFlight(matrix, Math.Matrix(self.__cam.matrix))
            return

    def resetCameraTarget(self, duration=0, resetRotation=True):
        if BigWorld.camera() != self.__cam:
            return
        else:
            currentCameraQuery = CGF.Query(self.spaceID, (CGF.GameObject, CurrentCameraObject))
            targetPos, yaw, pitch, distance, distConstraints = (None, None, None, None, None)
            for gameObject, _ in currentCameraQuery:
                hierarchy = CGF.HierarchyManager(self._hangarSpace.spaceID)
                parent = hierarchy.getParent(gameObject)
                parentTransformComponent = parent.findComponentByType(TransformComponent)
                transformComponent = gameObject.findComponentByType(TransformComponent)
                orbitComponent = gameObject.findComponentByType(OrbitComponent)
                if not orbitComponent or not parentTransformComponent or not transformComponent:
                    return
                targetPos = parentTransformComponent.worldTransform.translation
                worldYaw = parentTransformComponent.worldTransform.yaw
                worldPitch = parentTransformComponent.worldTransform.pitch
                yaw = self.__normaliseAngle(orbitComponent.currentYaw + worldYaw + math.pi) if resetRotation else None
                pitch = self.__normaliseAngle(orbitComponent.currentPitch + worldPitch) if resetRotation else None
                distance = orbitComponent.currentDist if resetRotation else None
                distConstraints = orbitComponent.distLimits
                self.__setCameraShift(gameObject.findComponentByType(ShiftComponent))

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
        else:
            self.__mouseMoveParams.distConstraints[0] = min(value, self.__mouseMoveParams.distConstraints[1])
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
            self.__flightCam.startAlongRoute(route, self.__flightParams.minDuration, self.__flightParams.maxDuration, self.__flightParams.positionEasing)
        else:
            self.__flightCam = BigWorld.CollidableTransitionCamera()
            self.__flightCam.spaceID = self._hangarSpace.spaceID
            self.__flightCam.start(prevMatrix, targetMatrix, self.__flightParams.minDuration, self.__flightParams.maxDuration, self.__flightParams.positionEasing, self.__flightParams.rotationEasing)
        BigWorld.camera(self.__flightCam)

    def __handleLobbyViewMouseEvent(self, event):
        if self.__flightCam and self.__flightCam.isInTransition() or self.__cam.isInTransition():
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

    def __setupCamera(self, gameObject, resetTransform=True):
        hierarchy = CGF.HierarchyManager(self._hangarSpace.spaceID)
        cameraComponent = gameObject.findComponentByType(CameraComponent)
        parent = hierarchy.getParent(gameObject)
        parentTransformComponent = parent.findComponentByType(TransformComponent)
        orbitComponent = gameObject.findComponentByType(OrbitComponent)
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
            self.__setCameraShift(gameObject.findComponentByType(ShiftComponent))
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
            self.__cam.target = targetMatrix
            sourceMatrix = Math.Matrix()
            sourceMatrix.setRotateYPR(Math.Vector3(yaw, pitch, 0.0))
            self.__cam.source = sourceMatrix
            self.__cam.pivotMaxDist = distance
            self.__cam.maxDistHalfLife = cameraComponent.fluency
            self.__cam.turningHalfLife = cameraComponent.fluency
            self.__cam.movementHalfLife = cameraComponent.fluency
            self.__cam.forceUpdate()
            self.__prevHorizontalFov = self.__currentHorizontalFov
            fovComponent = gameObject.findComponentByType(FovComponent)
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
            dofComponent = gameObject.findComponentByType(DofComponent)
            if dofComponent:
                self.__currentDOFParams = _DOFParams(True, dofComponent.nearStart, dofComponent.nearDist, dofComponent.farStart, dofComponent.farDist)
                if not self.__prevDOFParams.active:
                    farDist = targetPos.distTo(BigWorld.camera().position) + dofComponent.nearStart + dofComponent.nearDist + dofComponent.farStart + dofComponent.farDist
                    self.__prevDOFParams = _DOFParams(active=False, farDist=farDist)
            else:
                self.__currentDOFParams = _DOFParams()
                self.__customizationHelper.setDOFenabled(False)
            self.__deactivateCameraComponents()
            idleComponent = gameObject.findComponentByType(IdleComponent)
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
            parallaxComponent = gameObject.findComponentByType(ParallaxComponent)
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
            hierarchy = CGF.HierarchyManager(self._hangarSpace.spaceID)
            children = hierarchy.getChildren(gameObject)
            if not children:
                return
            flightHolder = None
            cameraFlightComponent = None
            for child in children:
                cameraFlightComponent = child.findComponentByType(CameraFlightComponent)
                if cameraFlightComponent and cameraFlightComponent.cameraName and cameraFlightComponent.cameraName == prevCameraName:
                    flightHolder = child
                    break

            if not flightHolder:
                return
            route = {}
            points = hierarchy.getChildren(flightHolder)
            if points:
                for p in points:
                    cameraComponent = p.findComponentByType(CameraComponent)
                    transformComponent = p.findComponentByType(TransformComponent)
                    if cameraComponent and transformComponent:
                        route[int(cameraComponent.name)] = transformComponent.worldTransform

            transforms = [ route[key] for key in sorted(route.keys()) ]
            self.__flightParams = _FlightParams(cameraFlightComponent.minDuration, cameraFlightComponent.maxDuration, cameraFlightComponent.positionEasing, cameraFlightComponent.rotationEasing, cameraFlightComponent.motionBlur, transforms)
            return

    def __onSetFovSetting(self):
        if self.__customFov:
            FovExtended.instance().setFovByAbsoluteValue(self.__currentHorizontalFov)
        else:
            self.__currentHorizontalFov = FovExtended.instance().horizontalFov

    def __deactivateCameraComponents(self):
        if self.__cameraIdle.isActive():
            self.__cameraIdle.deactivate()
        if self.__cameraParallax.isActive():
            self.__cameraParallax.deactivate()
        if self.__cameraFlyby.isActive:
            self.__cameraFlyby.deactivate()

    def __activateDOF(self):
        self.__customizationHelper.setDOFenabled(self.__currentDOFParams.active)
        self.__customizationHelper.setDOFparams(self.__currentDOFParams.nearStart, self.__currentDOFParams.nearDist, self.__currentDOFParams.farStart, self.__currentDOFParams.farDist)

    def __onCameraSwitched(self):
        if self.__isInSwitching:
            self.__isInSwitching = False
            self.onCameraSwitched(self.__cameraName)
            self.__customizationHelper.setMotionBlurAmount(_DEFAULT_MOTION_BLUR_)
            self.__activateDOF()
            self.__cameraIdle.activate()
            self.__cameraParallax.activate()

    def __onCameraSwitchCancel(self, toCamName):
        if self.__isInSwitching:
            self.__isInSwitching = False
            self.onCameraSwitchCancel(self.__cameraName, toCamName)

    @tickGroup(groupName='Simulation')
    def tick(self):
        if not self.__flightCam:
            dynamicFov = self.__calculateDynamicFov()
            if dynamicFov:
                self.__currentHorizontalFov = dynamicFov
                FovExtended.instance().setFovByAbsoluteValue(dynamicFov, 0.1)
            return
        else:
            if BigWorld.camera() != self.__cam and not self.__flightCam.isInTransition():
                self.__flightCam = None
                BigWorld.camera(self.__cam)
                self.__onCameraSwitched()
            elif self.__flightCam.isInTransition():
                progress = self.__flightCam.positionEasingProgress()
                if self.__prevHorizontalFov != self.__currentHorizontalFov:
                    newFov = self.__prevHorizontalFov + progress * (self.__currentHorizontalFov - self.__prevHorizontalFov)
                    FovExtended.instance().setFovByAbsoluteValue(newFov)
                if self.__currentDOFParams.active and (self.__prevDOFParams.active or progress > _DOF_START_PROGRESS_):
                    nearStart = self.__prevDOFParams.nearStart + progress * (self.__currentDOFParams.nearStart - self.__prevDOFParams.nearStart)
                    nearDist = self.__prevDOFParams.nearDist + progress * (self.__currentDOFParams.nearDist - self.__prevDOFParams.nearDist)
                    farStart = self.__prevDOFParams.farStart + progress * (self.__currentDOFParams.farStart - self.__prevDOFParams.farStart)
                    farDist = self.__prevDOFParams.farDist + progress * (self.__currentDOFParams.farDist - self.__prevDOFParams.farDist)
                    self.__customizationHelper.setDOFenabled(True)
                    self.__customizationHelper.setDOFparams(nearStart, nearDist, farStart, farDist)
            return
