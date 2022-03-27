# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ModelHitTester.py
import typing
from collections import namedtuple
from enum import Enum
import math
import logging
import BigWorld
from Math import Vector2, Matrix, Vector3
from constants import IS_DEVELOPMENT, IS_CLIENT, IS_BOT
from soft_exception import SoftException
from constants import IS_EDITOR
from wrapped_reflection_framework import ReflectionMetaclass
from items import _xml
_logger = logging.getLogger(__name__)

class ModelHitStatus(Enum):
    NORMAL = 0
    CRASHED = 1


class HitTesterManager(object):
    __metaclass__ = ReflectionMetaclass
    NORMAL_MODEL_TAG = 'normal'
    CRASHED_MODEL_TAG = 'crashed'
    CLIENT_MODEL_TAG = 'collisionModelClient'
    SERVER_MODEL_TAG = 'collisionModelServer'

    def __init__(self, dataSection=None):
        self.__hitTesters = {ModelHitStatus.NORMAL: None,
         ModelHitStatus.CRASHED: None}
        if dataSection:
            self.initHitTesters(dataSection)
        return

    @property
    def modelHitTester(self):
        return self.__hitTesters[ModelHitStatus.NORMAL]

    @modelHitTester.setter
    def modelHitTester(self, hitTester):
        self.__hitTesters[ModelHitStatus.NORMAL] = hitTester

    @property
    def crashedModelHitTester(self):
        return self.__hitTesters[ModelHitStatus.CRASHED]

    @crashedModelHitTester.setter
    def crashedModelHitTester(self, hitTester):
        self.__hitTesters[ModelHitStatus.CRASHED] = hitTester

    def getHitTester(self, modelStatus):
        requested = self.__hitTesters[modelStatus]
        return requested if requested is not None else self.__hitTesters[ModelHitStatus.NORMAL]

    def initHitTesters(self, dataSection):
        if dataSection.has_key(self.CRASHED_MODEL_TAG):
            self.__hitTesters[ModelHitStatus.CRASHED] = self.__createHitTester(dataSection, self.CRASHED_MODEL_TAG)
        normalModelSection = dataSection
        if dataSection.has_key(self.NORMAL_MODEL_TAG):
            normalModelSection = _xml.getSubsection(None, dataSection, self.NORMAL_MODEL_TAG)
        modelHitTester = self.__createHitTester(normalModelSection)
        self.__hitTesters[ModelHitStatus.NORMAL] = modelHitTester
        return

    def loadHitTesters(self):
        for _, hitTester in self.__hitTesters.iteritems():
            if hitTester and not hitTester.isBspModelLoaded():
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
        elif bspModelName.lower() == 'none':
            return NoneHitTester()
        modelTagDown = modelTag + 'Down'
        bspModelNameDown = section.readString(modelTagDown)
        modelTagUp = modelTag + 'Up'
        bspModelNameUp = section.readString(modelTagUp)
        return ModelHitTester(bspModelName, bspModelNameDown, bspModelNameUp)


class IHitTester(object):
    __slots__ = ('bbox',)

    def __init__(self):
        self.bbox = None
        return

    def loadBspModel(self):
        raise NotImplementedError

    def getBspModel(self):
        raise NotImplementedError

    def isBspModelLoaded(self):
        raise NotImplementedError

    def releaseBspModel(self):
        raise NotImplementedError

    def localAnyHitTest(self, start, stop, value=0):
        raise NotImplementedError

    def localHitTest(self, start, stop, value=0):
        raise NotImplementedError

    def localNearestHitTest(self, start, stop, value=0):
        raise NotImplementedError

    def localHitTestFull_debug(self, start, stop, value=0):
        raise NotImplementedError

    def worldHitTest(self, start, stop, worldMatrix, value=0):
        raise NotImplementedError

    def localSphericHitTest(self, center, radius, bOutsidePolygonsOnly=True, value=0):
        raise NotImplementedError

    def localCollidesWithTriangle(self, triangle, hitDir, value=0):
        raise NotImplementedError

    def getModel(self, value):
        raise NotImplementedError


class NoneHitTester(IHitTester):
    __slots__ = ()

    def __init__(self):
        super(NoneHitTester, self).__init__()
        self.bbox = (Vector3(-0.1, -0.1, -0.1), Vector3(0.1, 0.1, 0.1), 0.0)

    @property
    def bspModelName(self):
        return None

    @bspModelName.setter
    def bspModelName(self, name):
        pass

    def getBspModel(self):
        return None

    def isBspModelLoaded(self):
        return True

    def loadBspModel(self):
        pass

    def releaseBspModel(self):
        pass

    def localAnyHitTest(self, start, stop, value=0):
        return None

    def localHitTest(self, start, stop, value=0):
        return None

    def localNearestHitTest(self, start, stop, value=0):
        return None

    def localHitTestFull_debug(self, start, stop, value=0):
        return None

    def worldHitTest(self, start, stop, worldMatrix, value=0):
        return None

    def localSphericHitTest(self, center, radius, bOutsidePolygonsOnly=True, value=0):
        return None

    def localCollidesWithTriangle(self, triangle, hitDir, value=0):
        return None

    def getModel(self, value):
        return None


class ModelHitTester(IHitTester):
    __slots__ = ('__bspModel', '__bspModelName', '__bspModelDown', '__bspModelNameDown', '__bspModelUp', '__bspModelNameUp', 'bboxDown', 'bboxUp')

    def __init__(self, bspModelName=None, bspModelNameDown=None, bspModelNameUp=None):
        super(ModelHitTester, self).__init__()
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
        if name != self.__bspModelName:
            self.releaseBspModel()
            self.__bspModelName = name

    def getBspModel(self):
        return self.__bspModel

    def isBspModelLoaded(self):
        return self.__bspModel is not None

    def loadBspModel(self):
        if self.__bspModel is not None:
            _logger.error('Can not load bsp model, because it is already loaded!')
            return
        elif self.bspModelName is None:
            _logger.error('Can not load bsp model, bspModelName is None')
            return
        else:
            bspModel = BigWorld.WGBspCollisionModel()
            if not bspModel.setModelName(self.bspModelName):
                raise SoftException("wrong collision model '%s'" % self.bspModelName)
            self.__bspModel = bspModel
            self.bbox = bspModel.getBoundingBox()
            if not self.bbox:
                _logger.error("Couldn't find bounding box for the part the name '%s'", self.bspModelName)
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
        _logger.debug('localHitTestFull_debug %s %s %s', self.bspModelName, start, stop)
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


class BoundingBoxManager(object):

    def __init__(self, normalBBox=None, crashedBBox=None):
        self.__bboxes = {ModelHitStatus.NORMAL: normalBBox,
         ModelHitStatus.CRASHED: crashedBBox}

    @property
    def normalBBox(self):
        return self.__bboxes[ModelHitStatus.NORMAL]

    @normalBBox.setter
    def normalBBox(self, bbox):
        self.__bboxes[ModelHitStatus.NORMAL] = bbox

    @property
    def crashedBBox(self):
        return self.__bboxes[ModelHitStatus.CRASHED]

    @crashedBBox.setter
    def crashedBBox(self, bbox):
        self.__bboxes[ModelHitStatus.CRASHED] = bbox

    def getBBox(self, modelStatus):
        requested = self.__bboxes[modelStatus]
        return requested if requested is not None else self.__bboxes[ModelHitStatus.NORMAL]


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


def combineBBoxes(bboxes):
    bboxesCount = len(bboxes)
    if bboxesCount == 0:
        return None
    elif bboxesCount == 1:
        return bboxes[0]
    else:
        minBound, maxBound = bboxes[0][0], bboxes[0][1]
        for bbox in bboxes[1:]:
            minBound.x = min(minBound.x, bbox[0].x)
            minBound.y = min(minBound.y, bbox[0].y)
            minBound.z = min(minBound.z, bbox[0].z)
            maxBound.x = max(maxBound.x, bbox[1].x)
            maxBound.y = max(maxBound.y, bbox[1].y)
            maxBound.z = max(maxBound.z, bbox[1].z)

        maxDelta = math.sqrt(max(minBound.lengthSquared, maxBound.lengthSquared))
        return (minBound, maxBound, maxDelta)


def createBBoxManagerForModels(hitTesterManagers):
    normalBBoxes = []
    crashedBBoxes = []
    for manager in hitTesterManagers:
        if manager.modelHitTester and manager.modelHitTester.bbox:
            normalBBoxes.append(manager.modelHitTester.bbox)
        if manager.crashedModelHitTester and manager.crashedModelHitTester.bbox:
            crashedBBoxes.append(manager.crashedModelHitTester.bbox)

    return BoundingBoxManager(combineBBoxes(normalBBoxes), combineBBoxes(crashedBBoxes))


SegmentCollisionResult = namedtuple('SegmentCollisionResult', ('dist', 'hitAngleCos', 'armor'))
