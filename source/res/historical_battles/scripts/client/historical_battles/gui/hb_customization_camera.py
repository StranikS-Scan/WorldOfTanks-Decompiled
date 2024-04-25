# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/hb_customization_camera.py
import math
from functools import partial
import BigWorld
import Math
import math_utils
from AvatarInputHandler.cameras import FovExtended
from gui.hangar_cameras.hangar_camera_manager import HangarCameraYawFilter
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class _CameraParams(object):
    __slots__ = ('sensitivity', 'pitchConstraints', 'distConstraints', 'fluency')

    def __init__(self, sensitivity=0.005, pitchConstraints=tuple(), distConstraints=tuple(), fluency=0.05):
        self.sensitivity = sensitivity
        self.pitchConstraints = pitchConstraints
        self.distConstraints = distConstraints
        self.fluency = fluency


class CustomizationCamera(object):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self.__params = None
        self.__yawCameraFilter = None
        self.__cam = None
        self.__prevCam = None
        self.__prevVerticalFov = None
        self.__nativeVerticalFov = None
        self.__currentVerticalFov = None
        self.__isActive = False
        self.__onSpaceCreatedCallback = None
        return

    @property
    def isActive(self):
        return self.__isActive

    def init(self):
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.deactivate()
        self.__cam = None
        self.__params = None
        self.__yawCameraFilter = None
        self.__onSpaceCreatedCallback = None
        return

    def activate(self, targetPos, cameraParams):
        if self.__isActive:
            return
        elif self.__cam is None:
            self.__onSpaceCreatedCallback = partial(self.activate, targetPos, cameraParams)
            return
        else:
            self.__prevCam = BigWorld.camera()
            self.__prevVerticalFov = BigWorld.projection().fov
            self.__cam.spaceID = self.__prevCam.spaceID
            self.__yawCameraFilter = HangarCameraYawFilter(math.radians(cameraParams.yawConstraints[0]), math.radians(cameraParams.yawConstraints[1]), self.__params.sensitivity)
            self.__params.pitchConstraints = cameraParams.pitchConstraints
            self.__params.distConstraints = cameraParams.distanceConstraints
            pivotY, pivotMaxDist, initYaw, initPitch = self.__calculateCursorCameraParams(targetPos, cameraParams)
            self.__cam.target.setTranslate(targetPos)
            self.__cam.pivotPosition = Math.Vector3(0.0, pivotY, 0.0)
            self.__cam.pivotMaxDist = pivotMaxDist
            sourceMat = Math.Matrix()
            sourceMat.setRotateYPR(Math.Vector3(initYaw, initPitch, 0.0))
            self.__cam.source = sourceMat
            self.__cam.forceUpdate()
            BigWorld.camera(self.__cam)
            self.__setHorizontalFov(float(cameraParams.fov))
            self.__currentVerticalFov = self.__nativeVerticalFov = BigWorld.projection().fov
            g_eventBus.addListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            self.__isActive = True
            self.__processMouseEvent(1, 1, 1)
            return

    def deactivate(self):
        if not self.__isActive:
            return
        else:
            self.__isActive = False
            g_eventBus.removeListener(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, self.__handleLobbyViewMouseEvent)
            if self.__prevCam is not None:
                if self.__prevCam.spaceID != BigWorld.camera().spaceID:
                    return
                BigWorld.camera(self.__prevCam)
                self.__prevCam = None
            self.__restorePreviousFov()
            return

    def handleMouseEvent(self, dx, dy, dz):
        if self.__isActive:
            self.__processMouseEvent(dx, dy, dz)

    def __readHangarCameraCfg(self):
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__params = _CameraParams(sensitivity=cfg.get('cam_sens', 0.005), pitchConstraints=cfg.get('cam_pitch_constr', [-70.0, -5.0]), distConstraints=cfg.get('cam_dist_constr', [5.0, 11.0]), fluency=cfg.get('cam_fluency', 0.05))

    def __onSpaceCreated(self):
        self.__readHangarCameraCfg()
        if self.__cam is None:
            self.__cam = BigWorld.CursorCamera()
            self.__cam.isHangar = True
        self.__cam.pivotMaxDist = 0
        self.__cam.pivotMinDist = 0
        self.__cam.maxDistHalfLife = self.__params.fluency
        self.__cam.turningHalfLife = self.__params.fluency
        self.__cam.movementHalfLife = self.__params.fluency
        self.__cam.pivotPosition = Math.Vector3()
        self.__cam.source = Math.Matrix()
        self.__cam.target = Math.Matrix()
        self.__cam.forceUpdate()
        if callable(self.__onSpaceCreatedCallback):
            self.__onSpaceCreatedCallback()
            self.__onSpaceCreatedCallback = None
        return

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
        pitch -= dy * self.__params.sensitivity
        dist -= dz * self.__params.sensitivity
        pitch = math_utils.clamp(math.radians(self.__params.pitchConstraints[0]), math.radians(self.__params.pitchConstraints[1]), pitch)
        dist = math_utils.clamp(self.__params.distConstraints[0], self.__params.distConstraints[1], dist)
        mat = Math.Matrix()
        mat.setRotateYPR(Math.Vector3(yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist

    @staticmethod
    def __calculateCursorCameraParams(targetPos, cameraParams):
        initMatrix = Math.Matrix(cameraParams.initMatrix)
        initDirection = initMatrix.applyToAxis(2)
        startPoint = initMatrix.translation
        xPlanePoint = startPoint + initMatrix.applyToAxis(0)
        zPlanePoint = startPoint + initDirection
        camHorizontalPlane = Math.Plane()
        camHorizontalPlane.init(startPoint, xPlanePoint, zPlanePoint)
        intersectedPoint = camHorizontalPlane.intersectRay(targetPos, Math.Vector3(0.0, 1.0, 0.0))
        correctedCamDirection = intersectedPoint - startPoint
        pivotVec = intersectedPoint - targetPos
        pivotY = pivotVec.y
        yawCorrection = correctedCamDirection.yaw - initDirection.yaw
        yawCorrectionMatrix = Math.Matrix()
        yawCorrectionMatrix.setRotateYPR(Math.Vector3(yawCorrection, 0.0, 0.0))
        initMatrix.postMultiply(yawCorrectionMatrix)
        return (pivotY,
         correctedCamDirection.length,
         initMatrix.yaw,
         -initMatrix.pitch)

    @staticmethod
    def __setHorizontalFov(horizontalFov):
        FovExtended.instance().setFovByAbsoluteValue(horizontalFov)

    def __restorePreviousFov(self):
        if self.__prevVerticalFov is None:
            return
        else:
            if math.fabs(self.__currentVerticalFov - self.__nativeVerticalFov) > 1e-06:
                FovExtended.instance().resetFov()
            else:
                BigWorld.projection().fov = self.__prevVerticalFov
            self.__prevVerticalFov = None
            self.__currentVerticalFov = None
            self.__nativeVerticalFov = None
            return
