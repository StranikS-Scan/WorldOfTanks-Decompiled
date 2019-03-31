# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ModelHitTester.py
# Compiled at: 2011-07-14 15:46:00
import math, random
import BigWorld, ResMgr
from Math import Vector3, Vector2, Matrix
from debug_utils import *

class ModelHitTester(object):
    bbox = None
    bspModelName = None

    def __init__(self, dataSection):
        self.__bspModel = None
        self.bspModelName = dataSection.readString('collisionModel')
        if not self.bspModelName:
            raise Exception, '<collisionModel> is missing or wrong'
        return

    def isBspModelLoaded(self):
        return self.__bspModel is not None

    def loadBspModel(self):
        if self.__bspModel is not None:
            return
        else:
            bspModel = BigWorld.WGBspCollisionModel()
            if not bspModel.setModelName(self.bspModelName):
                raise Exception, "wrong collision model '%s'" % self.bspModelName
            self.__bspModel = bspModel
            self.bbox = bspModel.getBoundingBox()
            return

    def releaseBspModel(self):
        if self.__bspModel is not None:
            self.__bspModel = None
            del self.bbox
        return

    def localAnyHitTest(self, start, stop):
        return self.__bspModel.collideSegmentAny(start, stop)

    def localHitTest(self, start, stop):
        return self.__bspModel.collideSegment(start, stop)

    def worldHitTest(self, start, stop, worldMatrix):
        worldToLocal = Matrix(worldMatrix)
        worldToLocal.invert()
        testRes = self.__bspModel.collideSegment(worldToLocal.applyPoint(start), worldToLocal.applyPoint(stop))
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

    def localSphericHitTest(self, center, radius, bOutsidePolygonsOnly=True):
        return self.__bspModel.collideSphere(center, radius, bOutsidePolygonsOnly)


class VehicleHitTester(object):

    def __init__(self, chassisHt, hullHt, hullOffset):
        self.__args = (chassisHt, hullHt, hullOffset)
        self.__bbox = None
        self.__boundingRadiusSquared = None
        return

    def mayHit(self, start, stop, center=Vector3()):
        radiusSquared = self.__boundingRadiusSquared
        if radiusSquared is None:
            self.__getBbox()
            radiusSquared = self.__boundingRadiusSquared
        start = start - center
        stop = stop - center
        ao = Vector2(-start.x, -start.z)
        bo = Vector2(-stop.x, -stop.z)
        ab = ao - bo
        e = ao.dot(ab)
        if e <= 0.0:
            return ao.lengthSquared <= radiusSquared
        elif e >= ab.lengthSquared:
            return bo.length <= radiusSquared
        else:
            return ao.lengthSquared - e * e / ab.lengthSquared <= radiusSquared

    def __getBbox(self):
        if self.__bbox is None:
            bbox1, bbox2, offs = self.__args
            bbox1 = bbox1.bbox
            bbox2 = bbox2.bbox
            minPt = _combineChassisHullCorners(bbox1[0], bbox2[0], offs, min)
            maxPt = _combineChassisHullCorners(bbox1[1], bbox2[1], offs, max)
            p0 = Vector3()
            radiusSquared = max(minPt.flatDistSqrTo(p0), maxPt.flatDistSqrTo(p0))
            self.__bbox = (minPt, maxPt, math.sqrt(radiusSquared))
            self.__boundingRadiusSquared = radiusSquared
        return self.__bbox

    bbox = property(__getBbox)


def _combineChassisHullCorners(c, h, hullOffs, selector):
    return Vector3(selector(c.x, h.x + hullOffs.x), c.y, selector(c.z, h.z + hullOffs.z))
