# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/StrategicAimingSystem.py
import BigWorld
import Math
from Math import Vector3, Matrix
import math
from AvatarInputHandler import mathUtils, AimingSystems
from AvatarInputHandler.AimingSystems import IAimingSystem
from AvatarInputHandler.cameras import _clampPoint2DInBox2D

class StrategicAimingSystem(IAimingSystem):
    _LOOK_DIR = Vector3(0, -math.cos(0.001), math.sin(0.001))
    height = property(lambda self: self.__height)

    def __init__(self, height, yaw):
        self._matrix = mathUtils.createRotationMatrix((yaw, 0, 0))
        self.__planePosition = Vector3(0, 0, 0)
        self.__height = height

    def destroy(self):
        pass

    def enable(self, targetPos):
        self.updateTargetPos(targetPos)

    def disable(self):
        pass

    def getDesiredShotPoint(self, terrainOnlyCheck = False):
        return AimingSystems.getDesiredShotPoint(self._matrix.translation, Vector3(0, -1, 0), True, True, terrainOnlyCheck)

    def handleMovement(self, dx, dy):
        shift = self._matrix.applyVector(Vector3(dx, 0, dy))
        self.__planePosition += Vector3(shift.x, 0, shift.z)
        self.__updateMatrix()

    def updateTargetPos(self, targetPos):
        self.__planePosition.x = targetPos.x
        self.__planePosition.z = targetPos.z
        self.__updateMatrix()

    def __updateMatrix(self):
        bb = BigWorld.player().arena.arenaType.boundingBox
        pos2D = _clampPoint2DInBox2D(bb[0], bb[1], Math.Vector2(self.__planePosition.x, self.__planePosition.z))
        self.__planePosition.x = pos2D[0]
        self.__planePosition.z = pos2D[1]
        collPoint = BigWorld.wg_collideSegment(BigWorld.player().spaceID, self.__planePosition + Math.Vector3(0, 1000.0, 0), self.__planePosition + Math.Vector3(0, -250.0, 0), 3)
        heightFromPlane = 0.0 if collPoint is None else collPoint[0][1]
        self._matrix.translation = self.__planePosition + Vector3(0, heightFromPlane + self.__height, 0)
        return
