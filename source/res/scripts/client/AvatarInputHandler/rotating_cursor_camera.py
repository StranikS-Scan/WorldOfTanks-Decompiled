# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/rotating_cursor_camera.py
import math
import BigWorld
import math_utils

class RotatingCoursorCamera(object):

    def __init__(self, cfg):
        self.__camera = None
        self.__minPitch, self.__maxPitch = cfg.readVector2('pitchLimits')
        self.__minDist, self.__maxDist = cfg.readVector2('distanceLimits')
        self.__sensitivity = cfg.readFloat('sensitivity')
        self.__maxDistHalfLife = cfg.readFloat('maxDistHalfLife', 0.0)
        self.__pivotOffset = cfg.readVector3('pivotOffset')
        return

    @property
    def sourceMatrix(self):
        return self.__camera.source

    @property
    def pivotDistance(self):
        return self.__camera.pivotMaxDist

    @property
    def aimingSystem(self):
        return None

    def setup(self, targetPosition, initialRotations, distanceToTarget):
        if not self.__camera:
            self.__createCamera()
        self.__camera.pivotMaxDist = self.clampDistance(distanceToTarget)
        self.__camera.target = math_utils.createTranslationMatrix(targetPosition)
        self.__camera.source = initialRotations
        self.__camera.forceUpdate()

    def move(self, rotations, distance):
        if self.__camera is None:
            return
        else:
            self.__camera.source = rotations
            self.__camera.pivotMaxDist = distance
            self.__camera.forceUpdate()
            return

    def destroy(self):
        self.__camera = None
        return

    def handleMouseEvent(self, dx, dy, dz):
        if self.__camera is None:
            return
        else:
            currYaw, currPitch = self.__camera.source.yaw, self.__camera.source.pitch
            newYaw = (currYaw + math.radians(dx * self.__sensitivity)) % (2 * math.pi)
            newPitch = currPitch + math.radians(-dy * self.__sensitivity)
            newPitch = math_utils.clamp(-self.__maxPitch, -self.__minPitch, newPitch)
            self.__camera.source = math_utils.createRotationMatrix((newYaw, newPitch, 0))
            self.__camera.pivotMaxDist = self.clampDistance(self.__camera.pivotMaxDist - dz)
            self.__camera.forceUpdate()
            return

    def clampDistance(self, value):
        return math_utils.clamp(self.__minDist, self.__maxDist, value)

    def __createCamera(self):
        self.__camera = BigWorld.CursorCamera()
        self.__camera.maxDistHalfLife = self.__maxDistHalfLife
        self.__camera.pivotPosition = self.__pivotOffset
        self.__camera.enableAdvancedCollider(True)
        BigWorld.camera(self.__camera)
