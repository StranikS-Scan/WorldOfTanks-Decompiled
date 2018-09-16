# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/coordinate_system.py
from Math import Vector2, Vector3
ASSERT_EPS = 0.001

def getSomeOrthogonalVector2(vector):
    return Vector2(vector[1], -vector[0])


def getBoundsFromHullPoints(hullPoints):
    coords0, coords1 = [], []
    for hullPoint in hullPoints:
        coords0.append(hullPoint[0])
        coords1.append(hullPoint[1])

    coords0.sort()
    coords1.sort()
    bottomLeft = Vector2(coords0[0], coords1[0])
    topRight = Vector2(coords0[-1], coords1[-1])
    return (bottomLeft, topRight)


class CoordinateSystem2D(object):

    def __init__(self, origin, direction1, direction2=None):
        if direction2 is None:
            direction2 = getSomeOrthogonalVector2(direction1)
        self._origin = origin
        self._direction1 = direction1
        self._direction2 = direction2
        return

    def transform(self, point):
        pointDelta = point - self._origin
        return Vector2(self._direction1.dot(pointDelta), self._direction2.dot(pointDelta))

    def invTransform(self, transformedPoint):
        pointDelta = self._direction1 * transformedPoint[0] + self._direction2 * transformedPoint[1]
        return self._origin + pointDelta

    def translateByTransformedVector(self, point, transformedVector):
        return self.invTransform(self.transform(point) + transformedVector)


class AXIS_ALIGNED_DIRECTION:
    PLUS_Z = 0
    MINUS_Z = 1
    PLUS_X = 2
    MINUS_X = 3
    RANGE = (PLUS_Z,
     MINUS_Z,
     PLUS_X,
     MINUS_X)
    FROM_NAME = {'+Z': PLUS_Z,
     '-Z': MINUS_Z,
     '+X': PLUS_X,
     '-X': MINUS_X}
    TO_COORDINATES = {PLUS_X: (1.0, 0.0),
     MINUS_X: (-1.0, 0.0),
     PLUS_Z: (0.0, 1.0),
     MINUS_Z: (0.0, -1.0)}
    OPPOSITE = {PLUS_X: MINUS_X,
     MINUS_X: PLUS_X,
     PLUS_Z: MINUS_Z,
     MINUS_Z: PLUS_Z}

    @staticmethod
    def toVector(direction):
        return Vector2(AXIS_ALIGNED_DIRECTION.TO_COORDINATES[direction])

    @staticmethod
    def getBoundingBoxSegmentByDirection(bounds, dir):
        startX, startY, endX, endY = AXIS_ALIGNED_DIRECTION.__getBoundingBoxSegmentByDirectionInternal(bounds, dir)
        return (Vector2(startX, startY), Vector2(endX, endY))

    @staticmethod
    def getBoundingBoxSegmentByDirection3D(bounds, dir):
        startX, startY, endX, endY = AXIS_ALIGNED_DIRECTION.__getBoundingBoxSegmentByDirectionInternal(bounds, dir)
        return (Vector3(startX, 0, startY), Vector3(endX, 0, endY))

    @staticmethod
    def __getBoundingBoxSegmentByDirectionInternal(bounds, direction):
        bottomLeft, topRight = bounds
        return (topRight.x if direction == AXIS_ALIGNED_DIRECTION.PLUS_X else bottomLeft.x,
         topRight.y if direction == AXIS_ALIGNED_DIRECTION.PLUS_Z else bottomLeft.y,
         bottomLeft.x if direction == AXIS_ALIGNED_DIRECTION.MINUS_X else topRight.x,
         bottomLeft.y if direction == AXIS_ALIGNED_DIRECTION.MINUS_Z else topRight.y)
