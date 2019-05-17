# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ModelHitTester.py
from collections import namedtuple
import math
import BigWorld
from Math import Vector2, Matrix
from constants import IS_DEVELOPMENT, IS_CLIENT, IS_BOT
from debug_utils import LOG_DEBUG
from soft_exception import SoftException

class ModelHitTester(object):
    __slots__ = ('__bspModel', '__bspModelName', '__bspModelDown', '__bspModelNameDown', '__bspModelUp', '__bspModelNameUp', 'bbox', 'bboxDown', 'bboxUp')

    def __init__(self, dataSection=None):
        self.bbox = None
        self.__bspModel = None
        self.__bspModelName = None
        self.__bspModelDown = None
        self.__bspModelNameDown = None
        self.__bspModelUp = None
        self.__bspModelNameUp = None
        if dataSection is not None:
            modelTag = 'collisionModelClient' if IS_CLIENT or IS_BOT else 'collisionModelServer'
            self.__bspModelName = dataSection.readString(modelTag)
            if not self.__bspModelName:
                raise SoftException('<%s> is missing or wrong' % modelTag)
            modelTagDown = modelTag + 'Down'
            self.__bspModelNameDown = dataSection.readString(modelTagDown)
            modelTagUp = modelTag + 'Up'
            self.__bspModelNameUp = dataSection.readString(modelTagUp)
        return

    @property
    def bspModelName(self):
        return self.__bspModelName

    @bspModelName.setter
    def bspModelName(self, name):
        self.releaseBspModel()
        self.__bspModelName = name

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
                raise SoftException("wrong collision model '%s'" % self.bspModelName)
            self.__bspModel = bspModel
            self.bbox = bspModel.getBoundingBox()
            if self.__bspModelNameDown:
                bspModel = BigWorld.WGBspCollisionModel()
                if not bspModel.setModelName(self.__bspModelNameDown):
                    raise SoftException("wrong collision model '%s'" % self.__bspModelNameDown)
                self.__bspModelDown = bspModel
                self.bboxDown = bspModel.getBoundingBox()
            if self.__bspModelNameUp:
                bspModel = BigWorld.WGBspCollisionModel()
                if not bspModel.setModelName(self.__bspModelNameUp):
                    raise SoftException("wrong collision model '%s'" % self.__bspModelNameUp)
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


def coneMayHitVolume(boundingRadius, center, segmentStart, segmentEnd, startDeviation, endDeviation, do2DTest=True):
    segmentStart = segmentStart - center
    segmentEnd = segmentEnd - center
    if do2DTest:
        ao = Vector2(-segmentStart.x, -segmentStart.z)
        bo = Vector2(-segmentEnd.x, -segmentEnd.z)
    else:
        ao = segmentStart.scale(-1.0)
        bo = segmentEnd.scale(-1.0)
    ab = ao - bo
    e = ao.dot(ab)
    if e <= 0.0:
        return ao.lengthSquared <= (boundingRadius + startDeviation) ** 2
    if e >= ab.lengthSquared:
        return bo.lengthSquared <= (boundingRadius + endDeviation) ** 2
    d = math.sqrt(e / ab.lengthSquared)
    radiusSquared = (boundingRadius + (1.0 - d) * startDeviation + d * endDeviation) ** 2
    return ao.lengthSquared - e * e / ab.lengthSquared <= radiusSquared


def segmentMayHitVehicle(vehicleDescr, segmentStart, segmentEnd, vehicleCenter):
    return segmentMayHitVolume(vehicleDescr.boundingRadius, vehicleCenter, segmentStart, segmentEnd)


SegmentCollisionResult = namedtuple('SegmentCollisionResult', ('dist', 'hitAngleCos', 'armor'))
