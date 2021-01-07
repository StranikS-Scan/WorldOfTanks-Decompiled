# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ModelHitTester.py
from collections import namedtuple
import math
import BigWorld
from Math import Vector2, Matrix
from constants import IS_DEVELOPMENT, IS_CLIENT, IS_BOT
from soft_exception import SoftException
from constants import IS_EDITOR
from wrapped_reflection_framework import ReflectionMetaclass
from items import _xml

class HitTesterManager(object):
    __metaclass__ = ReflectionMetaclass
    NORMAL_MODEL_TAG = 'normal'
    CRASHED_MODEL_TAG = 'crashed'
    CLIENT_MODEL_TAG = 'collisionModelClient'
    SERVER_MODEL_TAG = 'collisionModelServer'

    class ModelStatus:
        NORMAL = 0
        CRASHED = 1

    def __init__(self, dataSection=None):
        self.__hitTesters = {self.ModelStatus.NORMAL: None,
         self.ModelStatus.CRASHED: None}
        self.__status = self.ModelStatus.NORMAL
        if dataSection:
            self.initHitTesters(dataSection)
        return

    @property
    def modelHitTester(self):
        return self.__hitTesters[self.ModelStatus.NORMAL]

    @modelHitTester.setter
    def modelHitTester(self, hitTester):
        self.__hitTesters[self.ModelStatus.NORMAL] = hitTester

    @property
    def crashedModelHitTester(self):
        return self.__hitTesters[self.ModelStatus.CRASHED]

    @crashedModelHitTester.setter
    def crashedModelHitTester(self, hitTester):
        self.__hitTesters[self.ModelStatus.CRASHED] = hitTester

    @property
    def activeHitTester(self):
        return self.__hitTesters[self.__status]

    def initHitTesters(self, dataSection):
        if dataSection.has_key(self.CRASHED_MODEL_TAG):
            self.__hitTesters[self.ModelStatus.CRASHED] = self.__createHitTester(dataSection, self.CRASHED_MODEL_TAG)
        normalModelSection = dataSection
        if dataSection.has_key(self.NORMAL_MODEL_TAG):
            normalModelSection = _xml.getSubsection(None, dataSection, self.NORMAL_MODEL_TAG)
        modelHitTester = self.__createHitTester(normalModelSection)
        self.__hitTesters[self.ModelStatus.NORMAL] = modelHitTester
        return

    def setStatus(self, modelStatus):
        if self.__hitTesters[modelStatus]:
            self.__status = modelStatus

    def loadHitTesters(self):
        for _, hitTester in self.__hitTesters.iteritems():
            if hitTester:
                hitTester.loadBspModel()

    def save(self, section):
        if IS_EDITOR:
            section.writeString(self.CLIENT_MODEL_TAG, self.edClientBspModel)
            section.writeString(self.SERVER_MODEL_TAG, self.edServerBspModel)
            if self.edCrashBspModel is not '':
                section.writeString(self.CRASHED_MODEL_TAG, self.edCrashBspModel)
            elif section.has_key(self.CRASHED_MODEL_TAG):
                section.deleteSection(self.CRASHED_MODEL_TAG)

    def __createHitTester(self, section, modelTag=None):
        if modelTag is None:
            modelTag = self.CLIENT_MODEL_TAG if IS_CLIENT or IS_EDITOR or IS_BOT else self.SERVER_MODEL_TAG
        bspModelName = section.readString(modelTag)
        if not bspModelName:
            raise SoftException('<%s> is missing or wrong' % modelTag)
        modelTagDown = modelTag + 'Down'
        bspModelNameDown = section.readString(modelTagDown)
        modelTagUp = modelTag + 'Up'
        bspModelNameUp = section.readString(modelTagUp)
        return ModelHitTester(bspModelName, bspModelNameDown, bspModelNameUp)


class ModelHitTester(object):
    __slots__ = ('__bspModel', '__bspModelName', '__bspModelDown', '__bspModelNameDown', '__bspModelUp', '__bspModelNameUp', 'bbox', 'bboxDown', 'bboxUp')

    def __init__(self, bspModelName=None, bspModelNameDown=None, bspModelNameUp=None):
        self.bbox = None
        self.__bspModel = None
        self.__bspModelName = bspModelName
        self.__bspModelDown = None
        self.__bspModelNameDown = bspModelNameDown
        self.__bspModelUp = None
        self.__bspModelNameUp = bspModelNameUp
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
        if self.__bspModel is not None or self.bspModelName is None:
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

    def localNearestHitTest(self, start, stop, value=0):
        return self.__getBspModel(value).collideSegmentNearest(start, stop)

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

    def getModel(self, value):
        return self.__getBspModel(value)


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
