# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/customization_camera.py
import math
from copy import deepcopy
import math_utils
import BigWorld
import Math
import CGF
from AvatarInputHandler.cameras import FovExtended
from gui.hangar_cameras.hangar_camera_manager import HangarCameraYawFilter
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.hangar_cameras.hangar_camera_parallax import HangarCameraParallax
from gui.hangar_cameras.hangar_camera_idle import HangarCameraIdle
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from helpers.CallbackDelayer import CallbackDelayer
from CameraComponents import CameraComponent, CameraFlightComponent, OrbitComponent, DofComponent
from Triggers import PrismAreaComponent
from GenericComponents import TransformComponent
from new_year.ny_constants import AnchorNames
_EASE_SQUARE_OUT = 2

class _FlightPoint(object):
    __slots__ = ('anchorName', 'flightTime', 'point')

    def __init__(self, anchorName='', flightTime=0, point=Math.Vector3()):
        self.anchorName = anchorName
        self.flightTime = flightTime
        self.point = point


class _CameraParams(object):
    __slots__ = ('name', 'initMatrix', 'targetPos', 'sensitivity', 'yawConstraints', 'pitchConstraints', 'distConstraints', 'fluency', 'fov', 'dofParams', 'flightPoints')

    def __init__(self, name=None, initMatrix=None, targetPos=None, sensitivity=0.005, yawConstraints=None, pitchConstraints=None, distConstraints=None, fluency=0.05, fov=None, dofParams=None, flightPoints=None):
        self.name = name
        self.initMatrix = initMatrix
        self.targetPos = targetPos
        self.sensitivity = sensitivity
        self.yawConstraints = yawConstraints
        self.pitchConstraints = pitchConstraints
        self.distConstraints = distConstraints
        self.fluency = fluency
        self.fov = fov
        self.dofParams = dofParams
        self.flightPoints = flightPoints or []


class CustomizationCamera(CallbackDelayer):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__yawCameraFilter = None
        self.__defaultParams = None
        self.__currentParams = None
        self.__prevParams = None
        self.__defaultFlightTime = None
        self.__instantly = False
        self.__cam = None
        self.__cameraParallax = None
        self.__cameraIdle = None
        self.__flightCam = None
        self.__initialCam = None
        self.__prevHorizontalFov = None
        self.__currentHorizontalFov = None
        self.__isActive = False
        self.__dofHelper = None
        CallbackDelayer.__init__(self)
        return

    def init(self):
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy
        self.__defaultFlightTime = 2.0

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.deactivate()
        self.__cam = None
        self.__cameraParallax = None
        self.__flightCam = None
        self.__initialCam = None
        self.__defaultParams = None
        self.__currentParams = None
        self.__prevParams = None
        self.__defaultFlightTime = None
        self.__instantly = False
        self.__yawCameraFilter = None
        CallbackDelayer.destroy(self)
        return

    def isActive(self):
        return self.__isActive

    def activate(self):
        space = self.hangarSpace.space
        if space is None:
            return
        else:
            self.__initialCam = space.camera
            if self.__initialCam is None:
                return
            if self.__flightCam is None:
                self.__flightCam = BigWorld.TransitionCamera()
            self.__flightCam.spaceID = self.__initialCam.spaceID
            FovExtended.instance().onSetFovSettingEvent += self.__onSetFovSetting
            g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            self.delayCallback(0.01, self.__checkFlightCamera)
            self.__isActive = True
            return

    def deactivate(self, instantly=True):
        if not self.__isActive:
            return
        else:
            if self.__cameraParallax:
                self.__cameraParallax.deactivate()
                self.__cameraParallax.destroy()
                self.__cameraParallax = None
            if self.__cameraIdle:
                self.__cameraIdle.destroy()
                self.__cameraIdle = None
            space = self.hangarSpace.space
            if space is not None:
                initialCameraIdle = space.getCameraManager().getCameraIdle()
                if initialCameraIdle:
                    initialCameraIdle.setDefaultStartDelay()
            self.__cam = self.__initialCam
            self.moveToGameObject(None, instantly)
            vEntity = self.hangarSpace.getVehicleEntity()
            if vEntity is not None:
                vEntity.setState(CameraMovementStates.ON_OBJECT)
            FovExtended.instance().onSetFovSettingEvent -= self.__onSetFovSetting
            g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            self.__isActive = False
            self.__prevParams = None
            return

    def moveToGameObject(self, gameObject=None, instantly=False):
        if not self.__isActive:
            return
        else:
            self.__instantly = instantly
            self.__prevParams = deepcopy(self.__currentParams)
            if gameObject:
                self.__readCameraParamsFromGameObject(gameObject)
                self.__setupCamera()
            else:
                self.__currentParams = deepcopy(self.__defaultParams)
            if self.__currentParams.dofParams:
                self.__dofHelper = BigWorld.PyCustomizationHelper(None, 0, False, None)
                self.__dofHelper.setDOFparams(*self.__currentParams.dofParams)
                self.__dofHelper.setDOFenabled(True)
            elif self.__dofHelper is not None:
                self.__dofHelper.setDOFenabled(False)
                self.__dofHelper = None
            if self.__flightCam.isInTransition():
                tempCam = BigWorld.FreeCamera()
                tempCam.set(self.__flightCam.matrix)
                BigWorld.camera(tempCam)
                self.__flightCam.finish()
                if gameObject:
                    self.__moveToCamera()
                else:
                    point = self.__initialCam.target.translation + Math.Vector3(0, self.__initialCam.pivotMaxDist, 0)
                    self.__moveToCamera(point)
            else:
                self.__moveThroughFlightPoint()
            self.__prevHorizontalFov = FovExtended.instance().getLastSetHorizontalFov()
            self.__currentHorizontalFov = self.__currentParams.fov
            if not self.__currentHorizontalFov:
                self.__currentHorizontalFov = FovExtended.instance().horizontalFov
            if self.__instantly:
                self.__setHorizontalFov(self.__currentHorizontalFov)
            return

    def handleMouseEvent(self, dx, dy, dz):
        if self.__flightCam and self.__flightCam.isInTransition():
            return
        if self.__isActive:
            self.__processMouseEvent(dx, dy, dz)

    def __readHangarCameraCfg(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__defaultParams = _CameraParams(name='Tank', sensitivity=cfg['cam_sens'], pitchConstraints=cfg['cam_pitch_constr'], distConstraints=cfg['cam_dist_constr'], fluency=cfg['cam_fluency'])
        self.__currentParams = deepcopy(self.__defaultParams)

    def __onSpaceCreated(self):
        self.__readHangarCameraCfg()

    def __onSpaceDestroy(self, inited):
        self.deactivate()

    def __handleLobbyViewMouseEvent(self, event):
        ctx = event.ctx
        self.handleMouseEvent(ctx['dx'], ctx['dy'], ctx['dz'])

    def __processMouseEvent(self, dx, dy, dz):
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        dist = self.__cam.pivotMaxDist
        currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
        currentYaw = currentMatrix.yaw
        yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, dx)
        pitch -= dy * self.__currentParams.sensitivity
        dist -= dz * self.__currentParams.sensitivity
        pitch = math_utils.clamp(self.__currentParams.pitchConstraints[0], self.__currentParams.pitchConstraints[1], pitch)
        dist = math_utils.clamp(self.__currentParams.distConstraints[0], self.__currentParams.distConstraints[1], dist)
        mat = Math.Matrix()
        mat.setRotateYPR(Math.Vector3(yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist

    @staticmethod
    def __setHorizontalFov(horizontalFov):
        FovExtended.instance().setFovByAbsoluteValue(horizontalFov)

    def __onSetFovSetting(self):
        self.__setHorizontalFov(self.__currentHorizontalFov)

    def __moveThroughFlightPoint(self):
        point = None
        flightTime = None
        if not self.__prevParams.flightPoints:
            if self.__initialCam and self.__initialCam.target and self.__initialCam.pivotMaxDist:
                point = self.__initialCam.target.translation + Math.Vector3(0, self.__initialCam.pivotMaxDist, 0)
            self.__moveToCamera(point)
        currentPosition = BigWorld.camera().position
        minDist = 9999
        for flightPoint in self.__prevParams.flightPoints:
            if flightPoint.anchorName == self.__currentParams.name:
                flightTime = flightPoint.flightTime
                dist = flightPoint.point.distTo(currentPosition)
                if dist < minDist:
                    minDist = dist
                    point = flightPoint.point

        self.__moveToCamera(point, flightTime)
        return

    def __moveToCamera(self, point=None, flightTime=None):
        if not flightTime:
            flightTime = self.__defaultFlightTime
        if self.__instantly:
            flightTime = 0.0
        if point:
            self.__flightCam.startThroughPoint(BigWorld.camera().matrix, self.__cam, flightTime, point, _EASE_SQUARE_OUT)
        else:
            self.__flightCam.start(BigWorld.camera().matrix, self.__cam, flightTime, _EASE_SQUARE_OUT)
        if self.__flightCam != BigWorld.camera():
            BigWorld.camera(self.__flightCam)

    def __checkFlightCamera(self):
        if BigWorld.camera() != self.__cam and BigWorld.camera().position == self.__cam.position:
            BigWorld.camera(self.__cam)
            self.__flightCam.finish()
            if not self.__isActive:
                return
        elif self.__flightCam.isInTransition() and not self.__instantly and self.__currentHorizontalFov and self.__prevHorizontalFov:
            if self.__prevHorizontalFov is not self.__currentHorizontalFov:
                progress = self.__flightCam.easedProgress()
                newFov = self.__prevHorizontalFov + progress * (self.__currentHorizontalFov - self.__prevHorizontalFov)
                self.__setHorizontalFov(newFov)

    def __setupCamera(self):
        if self.__cam:
            self.__cam = None
        if self.__cameraIdle:
            self.__cameraIdle.destroy()
            self.__cameraIdle = None
        self.__cam = BigWorld.CursorCamera()
        self.__cam.isHangar = True
        self.__cam.spaceID = self.__initialCam.spaceID
        self.__cam.maxDistHalfLife = 0
        self.__cam.pivotPosition = Math.Vector3(0.0, 0.0, 0.0)
        self.__yawCameraFilter = HangarCameraYawFilter(self.__currentParams.yawConstraints[0], self.__currentParams.yawConstraints[1], self.__currentParams.sensitivity)
        targetMatrix = Math.Matrix()
        targetMatrix.setTranslate(self.__currentParams.targetPos)
        self.__cam.target = targetMatrix
        distance = self.__currentParams.initMatrix.translation.distTo(self.__currentParams.targetPos)
        self.__cam.pivotMaxDist = distance
        sourceMatrix = Math.Matrix()
        sourceMatrix.setRotateYPR(Math.Vector3(self.__currentParams.initMatrix.yaw, -self.__currentParams.initMatrix.pitch, 0.0))
        self.__cam.source = sourceMatrix
        if self.__currentParams.name == AnchorNames.HEROTANK:
            self.__cam.setDynamicCollisions(True)
            self.__cameraIdle = HangarCameraIdle(self.__cam)
            self.__cameraIdle.setDefaultStartDelay()
        self.__cam.forceUpdate()
        if self.__cameraParallax:
            self.__cameraParallax.deactivate()
            self.__cameraParallax.destroy()
            self.__cameraParallax = None
        self.__cameraParallax = HangarCameraParallax(self.__cam)
        self.__cameraParallax.activate()
        return

    def __normaliseAngle(self, angle):
        if angle > math.pi:
            return angle - 2 * math.pi
        return angle + 2 * math.pi if angle < -math.pi else angle

    def __readCameraParamsFromGameObject(self, gameObject):
        hierarchy = CGF.HierarchyManager(BigWorld.player().hangarSpace.spaceID)
        cameraComponent = gameObject.findComponentByType(CameraComponent)
        if cameraComponent:
            self.__currentParams.name = cameraComponent.name
            self.__currentParams.fov = math.degrees(cameraComponent.fov)
        orbitComponent = gameObject.findComponentByType(OrbitComponent)
        parent = hierarchy.getParent(gameObject)
        parentTransform = parent.findComponentByType(TransformComponent)
        if orbitComponent and parentTransform:
            worldYaw = parentTransform.worldTransform.yaw
            worldPitch = parentTransform.worldTransform.pitch
            yawLimits = orbitComponent.yawLimits + Math.Vector2(worldYaw, worldYaw) + Math.Vector2(math.pi, math.pi)
            pitchLimits = orbitComponent.pitchLimits + Math.Vector2(worldPitch, worldPitch)
            self.__currentParams.yawConstraints = Math.Vector2(self.__normaliseAngle(yawLimits.x), self.__normaliseAngle(yawLimits.y))
            self.__currentParams.pitchConstraints = Math.Vector2(self.__normaliseAngle(pitchLimits.x), self.__normaliseAngle(pitchLimits.y))
            self.__currentParams.distConstraints = orbitComponent.distLimits
        if parentTransform:
            self.__currentParams.targetPos = parentTransform.worldTransform.translation
        transformComponent = gameObject.findComponentByType(TransformComponent)
        if transformComponent:
            self.__currentParams.initMatrix = transformComponent.worldTransform
        dofComponent = gameObject.findComponentByType(DofComponent)
        if dofComponent:
            self.__currentParams.dofParams = (dofComponent.nearStart,
             dofComponent.nearDist,
             dofComponent.farStart,
             dofComponent.farDist)
        else:
            self.__currentParams.dofParams = None
        children = hierarchy.getChildrenRecursively(gameObject)
        self.__currentParams.flightPoints = []
        for child in children:
            cameraFlightComponent = child.findComponentByType(CameraFlightComponent)
            prismAreaComponent = child.findComponentByType(PrismAreaComponent)
            transformComponent = child.findComponentByType(TransformComponent)
            if cameraFlightComponent and prismAreaComponent and transformComponent:
                for planePoint in prismAreaComponent.points:
                    point = transformComponent.worldTransform.applyPoint((planePoint.x, 0, planePoint.y))
                    self.__currentParams.flightPoints.append(_FlightPoint(cameraFlightComponent.anchorName, cameraFlightComponent.flightTime, point))

        return
