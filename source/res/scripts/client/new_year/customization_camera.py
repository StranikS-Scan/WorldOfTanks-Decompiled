# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/customization_camera.py
import BigWorld
import Math
import math
from AvatarInputHandler import mathUtils
from AvatarInputHandler.cameras import FovExtended
from gui.ClientHangarSpace import HangarCameraYawFilter, getHangarSpaceConfig
from Event import Event

class CustomizationCamera(object):

    def __init__(self):
        self.__cfg = getHangarSpaceConfig()
        self.__camSens = self.__cfg['cam_sens']
        self.__pitchConstraints = self.__cfg['cam_pitch_constr']
        self.__distConstraints = self.__cfg['cam_dist_constr']
        self.__yawCameraFilter = HangarCameraYawFilter(math.radians(self.__cfg['cam_yaw_constr'][0]), math.radians(self.__cfg['cam_yaw_constr'][1]), self.__camSens)
        self.__cam = None
        self.__prevCam = None
        self.__prevVerticalFov = None
        self.__nativeVerticalFov = None
        self.__currentVerticalFov = None
        self.__isActive = False
        self.__scrollEvent = Event()
        return

    def init(self):
        self.__cam = BigWorld.CursorCamera()
        self.__cam.pivotMaxDist = 0
        self.__cam.pivotMinDist = 0
        self.__cam.turningHalfLife = self.__cam.maxDistHalfLife = self.__cfg['cam_fluency']
        self.__cam.movementHalfLife = 0.0
        self.__cam.pivotPosition = Math.Vector3()
        self.__cam.source = Math.Matrix()
        self.__cam.target = Math.Matrix()
        self.__cam.wg_applyParams()

    def destroy(self):
        self.deactivate()
        self.__cam = None
        self.__cfg = None
        self.__camSens = None
        self.__pitchConstraints = None
        self.__distConstraints = None
        self.__yawCameraFilter = None
        self.__scrollEvent.clear()
        return

    def activate(self, targetPos, cameraParams):
        if self.__isActive:
            return
        self.__prevCam = BigWorld.camera()
        self.__prevVerticalFov = BigWorld.projection().fov
        self.__cam.spaceID = self.__prevCam.spaceID
        self.__yawCameraFilter = HangarCameraYawFilter(math.radians(cameraParams.yawConstraints[0]), math.radians(cameraParams.yawConstraints[1]), self.__camSens)
        self.__pitchConstraints = cameraParams.pitchConstraints
        self.__distConstraints = cameraParams.distanceConstraints
        pivotY, pivotMaxDist, initYaw, initPitch = self.__calculateCursorCameraParams(targetPos, cameraParams)
        self.__cam.target.setTranslate(targetPos)
        self.__cam.pivotPosition = Math.Vector3(0.0, pivotY, 0.0)
        self.__cam.pivotMaxDist = pivotMaxDist
        sourceMat = Math.Matrix()
        sourceMat.setRotateYPR(Math.Vector3(initYaw, initPitch, 0.0))
        self.__cam.source = sourceMat
        self.__cam.wg_applyParams()
        BigWorld.camera(self.__cam)
        horizontalFov = math.radians(cameraParams.fov)
        self.__setHorizontalFov(horizontalFov)
        self.__currentVerticalFov = self.__nativeVerticalFov = BigWorld.projection().fov
        FovExtended.instance().onSetFovSettingEvent += self.__onSetFovSetting
        FovExtended.instance().onRefreshFovEvent += self.__onRefreshFov
        self.__isActive = True

    def deactivate(self):
        if not self.__isActive:
            return
        else:
            self.__isActive = False
            FovExtended.instance().onSetFovSettingEvent -= self.__onSetFovSetting
            FovExtended.instance().onRefreshFovEvent -= self.__onRefreshFov
            if self.__prevCam is not None:
                if self.__prevCam.spaceID != BigWorld.camera().spaceID:
                    return
                BigWorld.camera(self.__prevCam)
                self.__prevCam = None
            self.__restorePreviousFov()
            return

    def addScrollListener(self, listener):
        self.__scrollEvent += listener

    def removeScrollListener(self, listener):
        self.__scrollEvent -= listener

    def handleMouseEvent(self, dx, dy, dz):
        if self.__isActive:
            self.__processMouseEvent(dx, dy, dz)

    def __processMouseEvent(self, dx, dy, dz):
        sourceMat = Math.Matrix(self.__cam.source)
        yaw = sourceMat.yaw
        pitch = sourceMat.pitch
        dist = self.__cam.pivotMaxDist
        currentMatrix = Math.Matrix(self.__cam.invViewMatrix)
        currentYaw = currentMatrix.yaw
        yaw = self.__yawCameraFilter.getNextYaw(currentYaw, yaw, dx)
        prevDist = dist
        pitch -= dy * self.__camSens
        dist -= dz * self.__camSens
        pitch = mathUtils.clamp(math.radians(self.__pitchConstraints[0]), math.radians(self.__pitchConstraints[1]), pitch)
        dist = mathUtils.clamp(self.__distConstraints[0], self.__distConstraints[1], dist)
        mat = Math.Matrix()
        mat.setRotateYPR(Math.Vector3(yaw, pitch, 0.0))
        self.__cam.source = mat
        self.__cam.pivotMaxDist = dist
        deltaDist = math.fabs(dist - prevDist)
        if dz != 0 and deltaDist > 0.01:
            self.__scrollEvent()

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

    def __onSetFovSetting(self):
        self.__prevVerticalFov = BigWorld.projection().fov
        BigWorld.projection().fov = self.__currentVerticalFov

    def __onRefreshFov(self):
        self.__currentVerticalFov = BigWorld.projection().fov

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
