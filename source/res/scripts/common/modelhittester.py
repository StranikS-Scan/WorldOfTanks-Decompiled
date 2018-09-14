# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ModelHitTester.py
from collections import namedtuple
import math
import BigWorld
from Math import Vector3, Vector2, Matrix
from debug_utils import *
from constants import IS_DEVELOPMENT, IS_CLIENT

class ModelHitTester(object):
    bbox = None

    def __setBspModelName(self, value):
        self.releaseBspModel()
        self.__bspModelName = value

    bspModelName = property(lambda self: self.__bspModelName, __setBspModelName)

    def __init__(self, dataSection=None):
        self.__bspModel = None
        self.__bspModelName = None
        self.__bspModelDown = None
        self.__bspModelNameDown = None
        self.__bspModelUp = None
        self.__bspModelNameUp = None
        if dataSection is not None:
            modelTag = 'collisionModelClient' if IS_CLIENT else 'collisionModelServer'
            self.__bspModelName = dataSection.readString(modelTag)
            if not self.__bspModelName:
                raise Exception('<%s> is missing or wrong' % modelTag)
            modelTagDown = modelTag + 'Down'
            self.__bspModelNameDown = dataSection.readString(modelTagDown)
            modelTagUp = modelTag + 'Up'
            self.__bspModelNameUp = dataSection.readString(modelTagUp)
        return

    def getBspModel(self):
        return self.__bspModel

    def isBspModelLoaded(self):
        return self.__bspModel is not None

    def loadBspModel(self):
        if self.__bspModel is not None:
            return
        else:
            bspModel = BigWorld.WGBspCollisionModel()
            if not bspModel.setModelName(self.bspModelName):
                raise Exception("wrong collision model '%s'" % self.bspModelName)
            self.__bspModel = bspModel
            self.bbox = bspModel.getBoundingBox()
            if self.__bspModelNameDown:
                bspModel = BigWorld.WGBspCollisionModel()
                if not bspModel.setModelName(self.__bspModelNameDown):
                    raise Exception("wrong collision model '%s'" % self.__bspModelNameDown)
                self.__bspModelDown = bspModel
                self.bboxDown = bspModel.getBoundingBox()
            if self.__bspModelNameUp:
                bspModel = BigWorld.WGBspCollisionModel()
                if not bspModel.setModelName(self.__bspModelNameUp):
                    raise Exception("wrong collision model '%s'" % self.__bspModelNameUp)
                self.__bspModelUp = bspModel
                self.bboxUp = bspModel.getBoundingBox()
            return

    def releaseBspModel(self):
        if self.__bspModel is not None:
            self.__bspModel = None
            del self.bbox
            if self.__bspModelDown is not None:
                self.__bspModelDown = None
                del self.bboxDown
            if self.__bspModelUp is not None:
                self.__bspModelUp = None
                del self.bboxUp
        return

    def localAnyHitTest(self, start, stop, value=0):
        return self.__getBspModel(value).collideSegmentAny(start, stop)

    def localHitTest(self, start, stop, value=0):
        return self.__getBspModel(value).collideSegment(start, stop)

    def localHitTestFull_debug(self, start, stop, value=0):
        assert IS_DEVELOPMENT
        LOG_DEBUG('localHitTestFull_debug', self.bspModelName, start, stop)
        return self.__getBspModel(value).collideSegmentFull_debug(start, stop)

    def worldHitTest(self, start, stop, worldMatrix, value=0):
        worldToLocal = Matrix(worldMatrix)
        worldToLocal.invert()
        testRes = self.__getBspModel(value).collideSegment(worldToLocal.applyPoint(start), worldToLocal.applyPoint(stop))
        if testRes is None:
            return
        else:
            res = []
            for dist, normal, hitAngleCos, matKind in testRes:
                res.append((dist,
                 worldMatrix.applyVector(normal),
                 hitAngleCos,
                 matKind))

            return res

    def localSphericHitTest(self, center, radius, bOutsidePolygonsOnly=True, value=0):
        return self.__getBspModel(value).collideSphere(center, radius, bOutsidePolygonsOnly)

    def localCollidesWithTriangle(self, triangle, hitDir, value=0):
        return self.__getBspModel(value).collidesWithTriangle(triangle, hitDir)

    def __getBspModel(self, value):
        if value > 0.5 and self.__bspModelUp:
            return self.__bspModelUp
        elif value < -0.5 and self.__bspModelDown:
            return self.__bspModelDown
        else:
            return self.__bspModel


def segmentMayHitVolume(boundingRadius, center, segmentStart, segmentEnd):
    radiusSquared = boundingRadius
    radiusSquared *= radiusSquared
    segmentStart = segmentStart - center
    segmentEnd = segmentEnd - center
    ao = Vector2(-segmentStart.x, -segmentStart.z)
    bo = Vector2(-segmentEnd.x, -segmentEnd.z)
    ab = ao - bo
    e = ao.dot(ab)
    if e <= 0.0:
        return ao.lengthSquared <= radiusSquared
    return bo.lengthSquared <= radiusSquared if e >= ab.lengthSquared else ao.lengthSquared - e * e / ab.lengthSquared <= radiusSquared


def segmentMayHitVehicle(vehicleDescr, segmentStart, segmentEnd, vehicleCenter):
    return segmentMayHitVolume(vehicleDescr.boundingRadius, vehicleCenter, segmentStart, segmentEnd)


SegmentCollisionResult = namedtuple('SegmentCollisionResult', ('dist', 'hitAngleCos', 'armor'))
