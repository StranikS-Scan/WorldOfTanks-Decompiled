# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/StrategicAimingSystem.py
import math
import BigWorld
import Math
from Math import Vector3
import math_utils
from AvatarInputHandler import AimingSystems
from AvatarInputHandler.AimingSystems import IAimingSystem
from AvatarInputHandler.cameras import _clampPoint2DInBox2D

class BaseStrategicAimingSystem(IAimingSystem):
    _LOOK_DIR = Vector3(0, -math.cos(0.001), math.sin(0.001))
    heightFromPlane = property(lambda self: self.__heightFromPlane)
    planePosition = property(lambda self: self._planePosition)

    def __init__(self, height, yaw):
        super(BaseStrategicAimingSystem, self).__init__()
        self._matrix = math_utils.createRotationMatrix((yaw, 0, 0))
        self._planePosition = Vector3(0, 0, 0)
        self.__camDist = 0.0
        self.__height = height
        self.__heightFromPlane = 0.0

    def destroy(self):
        pass

    def enable(self, targetPos):
        self.updateTargetPos(targetPos)

    def disable(self):
        pass

    def getDesiredShotPoint(self, terrainOnlyCheck=False):
        return AimingSystems.getDesiredShotPoint(self._matrix.translation, Vector3(0, -1, 0), True, True, terrainOnlyCheck)

    def handleMovement(self, dx, dy):
        shift = self._matrix.applyVector(Vector3(dx, 0, dy))
        self._planePosition += Vector3(shift.x, 0, shift.z)
        self._updateMatrix()

    def updateTargetPos(self, targetPos):
        self._planePosition.x = targetPos.x
        self._planePosition.z = targetPos.z
        self._updateMatrix()

    def setYaw(self, yaw):
        self._matrix = math_utils.createRotationMatrix((yaw, 0, 0))
        self._updateMatrix()

    def getCamDist(self):
        return self.__camDist

    def overrideCamDist(self, camDist):
        self.__camDist = camDist
        return camDist

    def getShotPoint(self):
        desiredShotPoint = self.getDesiredShotPoint()
        return Vector3(desiredShotPoint.x, self.getCamDist(), desiredShotPoint.z)

    def getZoom(self):
        pass

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.__height = value

    def _clampToArenaBB(self):
        bb = BigWorld.player().arena.arenaType.boundingBox
        pos2D = _clampPoint2DInBox2D(bb[0], bb[1], Math.Vector2(self._planePosition.x, self._planePosition.z))
        self._planePosition.x = pos2D[0]
        self._planePosition.z = pos2D[1]

    def _updateMatrix(self):
        self._clampToArenaBB()
        collPoint = BigWorld.wg_collideSegment(BigWorld.player().spaceID, self._planePosition + Math.Vector3(0, 1000.0, 0), self._planePosition + Math.Vector3(0, -250.0, 0), 3)
        self.__heightFromPlane = 0.0 if collPoint is None else collPoint.closestPoint[1]
        self._matrix.translation = self._planePosition + Vector3(0, self.__heightFromPlane + self.__height, 0)
        return


class StrategicAimingSystem(BaseStrategicAimingSystem):

    def __init__(self, height, yaw):
        super(StrategicAimingSystem, self).__init__(height, yaw)
        self.__defaultYaw = yaw
        self.__parallaxModeEnabled = False

    def setParallaxModeEnabled(self, isEnabled):
        self.__parallaxModeEnabled = isEnabled
        if not isEnabled:
            self._matrix.setRotateYPR((self.__defaultYaw, 0, 0))

    def handleMovement(self, dx, dy):
        self._updateYaw()
        super(StrategicAimingSystem, self).handleMovement(dx, dy)

    def updateTargetPos(self, targetPos):
        self._updateYaw()
        super(StrategicAimingSystem, self).updateTargetPos(targetPos)

    def getCamYaw(self):
        return self._matrix.yaw

    def _updateYaw(self):
        if self.__parallaxModeEnabled:
            vehicle = BigWorld.player().getVehicleAttached()
            vehiclePosition = Vector3(vehicle.position) if vehicle is not None else None
            if vehiclePosition is not None:
                vehiclePosition.y = self._planePosition.y
                direction = self._planePosition - vehiclePosition
                if direction.lengthSquared < AimingSystems.SPG_MINIMAL_AIMING_RADIUS_SQ:
                    direction.normalise()
                    self._planePosition = vehiclePosition + direction * AimingSystems.SPG_MINIMAL_AIMING_RADIUS
                else:
                    direction.normalise()
                self._matrix.setRotateYPR((direction.yaw, 0, 0))
        return
