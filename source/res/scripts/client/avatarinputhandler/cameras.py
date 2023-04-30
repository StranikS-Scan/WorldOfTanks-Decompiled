# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/cameras.py
import math
import BigWorld
import Math
import math_utils

class ImpulseReason(object):
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

    def getConfigValue(self, name):
        pass

    def getUserConfigValue(self, name):
        pass

    def setUserConfigValue(self, name, value):
        pass

    def update(self, dx, dy, dz, updatedByKeyboard):
        pass

    def autoUpdate(self):
        pass

    def applyImpulse(self, position, impulse, reason=ImpulseReason.ME_HIT):
        pass

    def applyDistantImpulse(self, position, impulseValue, reason=ImpulseReason.ME_HIT):
        pass

    def getReasonsAffectCameraDirectly(self):
        pass


class FreeCamera(object):
    camera = property(lambda self: self.__cam)

    def __init__(self):
        self.__cam = BigWorld.FreeCamera()

    def create(self):
        pass

    def destroy(self):
        self.__cam = None
        return

    def enable(self, camMat=None):
        if camMat is not None:
            self.__cam.set(camMat)
        BigWorld.camera(self.__cam)
        BigWorld.enableFreeCameraModeForShadowManager(True)
        return

    def disable(self):
        BigWorld.enableFreeCameraModeForShadowManager(False)

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

    def set(self, matrix):
        self.__cam.set(matrix)

    def isEnabled(self):
        return BigWorld.camera() is self.__cam


def readBool(dataSec, name, defaultVal):
    return defaultVal if dataSec is None else dataSec.readBool(name, defaultVal)


def readInt(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        value = dataSec.readInt(name, defaultVal)
        value = math_utils.clamp(minVal, maxVal, value)
        return value


def readFloat(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return defaultVal
    else:
        value = dataSec.readFloat(name, defaultVal)
        value = math_utils.clamp(minVal, maxVal, value)
        return value


def readVec2(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return Math.Vector2(defaultVal)
    else:
        value = dataSec.readVector2(name, Math.Vector2(defaultVal))
        for i in xrange(2):
            value[i] = math_utils.clamp(minVal[i], maxVal[i], value[i])

        return value


def readVec3(dataSec, name, minVal, maxVal, defaultVal):
    if dataSec is None:
        return Math.Vector3(defaultVal)
    else:
        value = dataSec.readVector3(name, Math.Vector3(defaultVal))
        for i in xrange(3):
            value[i] = math_utils.clamp(minVal[i], maxVal[i], value[i])

        return value


def readString(dataSec, name, defaultVal):
    return defaultVal if dataSec is None else dataSec.readString(name, defaultVal)


def getScreenAspectRatio():
    return BigWorld.getAspectRatio()


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
    return posInClip.w != 0 and -1 <= posInClip.x / posInClip.w <= 1 and (True if -1 <= posInClip.y / posInClip.w <= 1 else False)


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


def getAimMatrix(x, y, fov=None):
    if fov is None:
        fov = BigWorld.projection().fov
    near = BigWorld.projection().nearPlane
    aspect = getScreenAspectRatio()
    yLength = near * math.tan(fov * 0.5)
    xLength = yLength * aspect
    result = math_utils.createRotationMatrix(Math.Vector3(math.atan2(xLength * x, near), math.atan2(yLength * y, near), 0))
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


def get2DAngleFromCamera(vector):
    modifiedVector = Math.Vector3(vector.x, 0, vector.z)
    direction = Math.Vector3(BigWorld.camera().direction)
    direction.y = 0
    if direction.length and modifiedVector.length:
        direction.normalise()
        modifiedVector.normalise()
    else:
        return math.pi
    dot = max(min(direction.dot(modifiedVector), 1), -1)
    return math.acos(dot)


class FovExtended(object):
    __instance = None
    arWide = 16.0 / 9.0
    vFovNarrow = {70: 44.2105,
     75: 47.3684,
     80: 50.5263,
     85: 53.6842,
     90: 56.8421,
     95: 60,
     100: 63.1579,
     105: 66.3158,
     110: 69.4737,
     115: 72.6316,
     120: 75.7895}
    vFovWide = {70: 39.375,
     75: 42.1875,
     80: 45,
     85: 47.8125,
     90: 50.625,
     95: 53.4375,
     100: 56.25,
     105: 59.0625,
     110: 61.875,
     115: 64.6875,
     120: 67.5}

    @staticmethod
    def lookupVerticalFov(horizontalFovValue):
        lookupDict = FovExtended.vFovWide if BigWorld.getAspectRatio() > FovExtended.arWide else FovExtended.vFovNarrow
        if horizontalFovValue not in lookupDict.keys():
            horizontalFovValue = (int(horizontalFovValue / 5) + 1) * 5
            horizontalFovValue = math_utils.clamp(lookupDict.keys()[0], lookupDict.keys()[-1], horizontalFovValue)
        return math.radians(lookupDict[horizontalFovValue])

    @staticmethod
    def clampFov(fov):
        return math_utils.clamp(0.017, 3.12, fov)

    @staticmethod
    def instance():
        if FovExtended.__instance is None:
            FovExtended.__instance = FovExtended()
        return FovExtended.__instance

    def __setEnabled(self, value):
        self.__enabled = value
        self.refreshFov()

    enabled = property(lambda self: self.__enabled, __setEnabled)

    def __setHorizontalFov(self, value):
        self.__horizontalFov = value
        self.__verticalFov = FovExtended.lookupVerticalFov(value)
        self.setFovByMultiplier(self.__multiplier)

    horizontalFov = property(lambda self: self.__horizontalFov, __setHorizontalFov)

    def __getActualDefaultVerticalFov(self):
        return FovExtended.lookupVerticalFov(self.horizontalFov)

    actualDefaultVerticalFov = property(__getActualDefaultVerticalFov)

    def __init__(self):
        self.__multiplier = 1.0
        self.__enabled = True
        BigWorld.addWatcher('Render/Fov(horizontal, deg)', lambda : self.__horizontalFov)
        BigWorld.addWatcher('Render/Fov(vertical, deg)', lambda : math.degrees(self.__verticalFov))
        self.horizontalFov = 90
        self.defaultVerticalFov = FovExtended.lookupVerticalFov(self.horizontalFov)
        from gui import g_guiResetters
        g_guiResetters.add(self.refreshFov)

    def resetFov(self):
        self.setFovByMultiplier(1.0)

    def setFovByMultiplier(self, multiplier, rampTime=None):
        self.__multiplier = multiplier
        if not self.__enabled:
            return
        else:
            verticalFov = self.actualDefaultVerticalFov
            finalFov = FovExtended.clampFov(verticalFov * self.__multiplier)
            if rampTime is None:
                BigWorld.projection().fov = finalFov
            else:
                BigWorld.projection().rampFov(finalFov, rampTime)
            return

    def setFovByAbsoluteValue(self, horizontalFov, rampTime=None):
        multiplier = horizontalFov / self.horizontalFov
        self.setFovByMultiplier(multiplier, rampTime)

    def refreshFov(self):
        self.__verticalFov = self.actualDefaultVerticalFov
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
