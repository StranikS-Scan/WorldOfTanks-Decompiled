# Embedded file name: scripts/client/AvatarInputHandler/cameras.py
import BigWorld, Math, ResMgr, Keys
import math
from AvatarInputHandler import mathUtils

class ImpulseReason:
    MY_SHOT = 0
    ME_HIT = 1
    OTHER_SHOT = 2
    SPLASH = 3
    COLLISION = 4
    VEHICLE_EXPLOSION = 5
    PROJECTILE_HIT = 6
    HE_EXPLOSION = 7


class ICamera(object):

    def create(self, **args):
        pass

    def destroy(self):
        pass

    def enable(self, **args):
        pass

    def disable(self):
        pass

    def restoreDefaultsState(self):
        pass

    def getUserConfigValue(self, name):
        pass

    def setUserConfigValue(self, name, value):
        pass

    def update(self):
        pass

    def autoUpdate(self):
        pass

    def applyImpulse(self, position, impulse, reason = ImpulseReason.ME_HIT):
        pass

    def applyDistantImpulse(self, position, impulseValue, reason = ImpulseReason.ME_HIT):
        pass

    def getReasonsAffectCameraDirectly(self):
        return ()


class FreeCamera:
    camera = property(lambda self: self.__cam)

    def __init__(self):
        self.__cam = BigWorld.FreeCamera()

    def create(self):
        pass

    def destroy(self):
        self.__cam = None
        return

    def enable(self, camMat = None):
        if camMat is not None:
            self.__cam.set(camMat)
        BigWorld.camera(self.__cam)
        return

    def disable(self):
        BigWorld.camera(None)
        return

    def setWorldMatrix(self, matrix):
        matrix = Math.Matrix(matrix)
        matrix.invert()
        self.__cam.set(matrix)

    def getWorldMatrix(self):
        return Math.Matrix(self.__cam.invViewMatrix)

    def handleKey(self, event):
        return self.__cam.handleKeyEvent(event)

    def handleMouse(self, dx, dy, dz):
        return self.__cam.handleMouseEvent(BigWorld.MouseEvent(dx, dy, dz, (0, 0)))

    def resetMovement(self):
        self.__cam.resetKeys()


def readBool(dataSec, name, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        return dataSec.readBool(name, defaultVal)


def readFloat(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        value = dataSec.readFloat(name, defaultVal)
        value = mathUtils.clamp(minVal, maxVal, value)
        return value


def readVec2(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return Math.Vector2(defaultVal)
    else:
        value = dataSec.readVector2(name, Math.Vector2(defaultVal))
        for i in xrange(2):
            value[i] = mathUtils.clamp(minVal[i], maxVal[i], value[i])

        return value


def readVec3(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return Math.Vector3(defaultVal)
    else:
        value = dataSec.readVector3(name, Math.Vector3(defaultVal))
        for i in xrange(3):
            value[i] = mathUtils.clamp(minVal[i], maxVal[i], value[i])

        return value


def getScreenAspectRatio():
    if BigWorld.isVideoWindowed():
        size = BigWorld.screenSize()
        return size[0] / size[1]
    else:
        return BigWorld.getFullScreenAspectRatio()


def getProjectionMatrix():
    proj = BigWorld.projection()
    aspect = getScreenAspectRatio()
    result = Math.Matrix()
    result.perspectiveProjection(proj.fov, aspect, proj.nearPlane, proj.farPlane)
    return result


def getViewProjectionMatrix():
    result = Math.Matrix(BigWorld.camera().matrix)
    result.postMultiply(getProjectionMatrix())
    return result


def isPointOnScreen(point):
    if point.lengthSquared == 0.0:
        return False
    posInClip = Math.Vector4(point.x, point.y, point.z, 1)
    posInClip = getViewProjectionMatrix().applyV4Point(posInClip)
    if posInClip.w != 0 and -1 <= posInClip.x / posInClip.w <= 1 and -1 <= posInClip.y / posInClip.w <= 1:
        return True
    return False


def projectPoint(point):
    posInClip = Math.Vector4(point.x, point.y, point.z, 1)
    posInClip = getViewProjectionMatrix().applyV4Point(posInClip)
    if posInClip.w != 0:
        posInClip = posInClip.scale(1 / posInClip.w)
    return posInClip


def getWorldRayAndPoint(x, y):
    fov = BigWorld.projection().fov
    near = BigWorld.projection().nearPlane
    aspect = getScreenAspectRatio()
    yLength = near * math.tan(fov * 0.5)
    xLength = yLength * aspect
    point = Math.Vector3(xLength * x, yLength * y, near)
    inv = Math.Matrix(BigWorld.camera().invViewMatrix)
    ray = inv.applyVector(point)
    wPoint = inv.applyPoint(point)
    return (ray, wPoint)


def getAimMatrix(x, y, fov = None):
    if fov is None:
        fov = BigWorld.projection().fov
    near = BigWorld.projection().nearPlane
    aspect = getScreenAspectRatio()
    yLength = near * math.tan(fov * 0.5)
    xLength = yLength * aspect
    result = mathUtils.createRotationMatrix(Math.Vector3(math.atan2(xLength * x, near), math.atan2(yLength * y, near), 0))
    return result


def overrideCameraMatrix(position, direction):
    overridenCameraMatrix = Math.Matrix()
    overridenCameraMatrix.setTranslate(position)
    rotationMatrix = Math.Matrix()
    rotationMatrix.setRotateYPR(direction)
    overridenCameraMatrix.preMultiply(rotationMatrix)
    overridenCameraMatrix.invert()
    freeCamera = FreeCamera()
    freeCamera.enable(overridenCameraMatrix)


class FovExtended(object):
    __instance = None
    __HOR_TO_VERT_RATIO = 60.0 / 95.0
    __TO_HORIZONTAL_THRESHOLD = 3.0 / 2.0 + 0.001
    __HOR_TO_BIG_HOR_RATIO = 2.0
    __BIG_ASPECT_THRESHOLD = 11.0 / 3.0

    @staticmethod
    def clampFov(fov):
        return mathUtils.clamp(0.017, 3.12, fov)

    @staticmethod
    def calcVerticalFov(horizontalFovValue):
        return horizontalFovValue / getScreenAspectRatio()

    @staticmethod
    def calcHorizontalFov(verticalFovValue):
        return verticalFovValue * getScreenAspectRatio()

    @staticmethod
    def instance():
        if FovExtended.__instance is None:
            FovExtended.__instance = FovExtended()
        return FovExtended.__instance

    isHorizontalFovFixed = property(lambda self: self.__isHorizontalFovFixed)

    def __setEnabled(self, value):
        self.__enabled = value
        self.refreshFov()

    enabled = property(lambda self: self.__enabled, __setEnabled)

    def __setHorizontalFov(self, value):
        self.__defaultHorizontalFov = value
        self.__defaultVerticalFov = value * FovExtended.__HOR_TO_VERT_RATIO
        self.__defaultHorizontalFovBig = value * FovExtended.__HOR_TO_BIG_HOR_RATIO
        self.setFovByMultiplier(self.__multiplier)

    defaultHorizontalFov = property(lambda self: self.__defaultHorizontalFov, __setHorizontalFov)

    def __getActualDefaultVerticalFov(self):
        verticalFov = self.__defaultVerticalFov
        if self.__isHorizontalFovFixed:
            horizontalFov = self.__defaultHorizontalFov
            if getScreenAspectRatio() >= FovExtended.__BIG_ASPECT_THRESHOLD:
                horizontalFov = self.__defaultHorizontalFovBig
            verticalFov = FovExtended.calcVerticalFov(horizontalFov)
        return verticalFov

    actualDefaultVerticalFov = property(__getActualDefaultVerticalFov)

    def __init__(self):
        self.__isHorizontalFovFixed = getScreenAspectRatio() > FovExtended.__TO_HORIZONTAL_THRESHOLD
        self.__multiplier = 1.0
        self.__enabled = True
        initialVerticalFov = math.radians(60)
        self.defaultHorizontalFov = initialVerticalFov * getScreenAspectRatio()
        from gui import g_guiResetters
        g_guiResetters.add(self.refreshFov)

    def resetFov(self):
        self.setFovByMultiplier(1.0)

    def setFovByMultiplier(self, multiplier, rampTime = None):
        self.__multiplier = multiplier
        if not self.__enabled:
            return
        else:
            defaultFov = self.actualDefaultVerticalFov
            finalFov = FovExtended.clampFov(defaultFov * self.__multiplier)
            if rampTime is None:
                BigWorld.projection().fov = finalFov
            else:
                BigWorld.projection().rampFov(finalFov, rampTime)
            return

    def setFovByAbsoluteValue(self, horizontalFov, rampTime = None):
        multiplier = horizontalFov / self.defaultHorizontalFov
        self.setFovByMultiplier(multiplier, rampTime)

    def refreshFov(self):
        self.__isHorizontalFovFixed = getScreenAspectRatio() > FovExtended.__TO_HORIZONTAL_THRESHOLD
        self.setFovByMultiplier(self.__multiplier)


def _clampPoint2DInBox2D(bottomLeft, upperRight, point):
    retPoint = Math.Vector2(0, 0)
    retPoint[0] = max(bottomLeft[0], point[0])
    retPoint[0] = min(retPoint[0], upperRight[0])
    retPoint[1] = max(bottomLeft[1], point[1])
    retPoint[1] = min(retPoint[1], upperRight[1])
    return retPoint


def _vec3fFromYawPitch(yaw, pitch):
    cosPitch = math.cos(+pitch)
    sinPitch = math.sin(-pitch)
    cosYaw = math.cos(yaw)
    sinYaw = math.sin(yaw)
    return Math.Vector3(cosPitch * sinYaw, sinPitch, cosPitch * cosYaw)
