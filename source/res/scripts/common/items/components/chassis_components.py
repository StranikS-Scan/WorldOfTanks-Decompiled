# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/chassis_components.py
from collections import namedtuple
from items.components import component_constants
from items.components import path_builder
from items.components import shared_components
__all__ = ('Wheel', 'WheelGroup', 'TrackNode', 'TrackMaterials', 'GroundNode', 'GroundNodeGroup', 'Traces', 'LeveredSuspensionConfig', 'SuspensionLever', 'SplineSegmentModelSet')
Wheel = namedtuple('Wheel', ('index', 'isLeft', 'radius', 'nodeName', 'isLeading', 'leadingSyncAngle', 'hitTester', 'materials', 'position'))
WheelGroup = namedtuple('WheelGroup', ('isLeft', 'template', 'count', 'startIndex', 'radius'))
WheelsConfig = namedtuple('WheelsConfig', ('groups', 'wheels'))
TrackNode = namedtuple('TrackNode', ('name', 'isLeft', 'initialOffset', 'leftNodeName', 'rightNodeName', 'damping', 'elasticity', 'forwardElasticityCoeff', 'backwardElasticityCoeff'))
TrackMaterials = namedtuple('TrackNode', ('lodDist', 'leftMaterial', 'rightMaterial', 'textureScale'))
TrackParams = namedtuple('TrackNode', ('thickness', 'maxAmplitude', 'maxOffset', 'gravity'))
GroundNode = namedtuple('GroundNode', ('nodeName', 'affectedWheelName', 'isLeft', 'minOffset', 'maxOffset', 'collisionSamplesCount', 'hasLiftMode'))
GroundNodeGroup = namedtuple('GroundNodeGroup', ('isLeft', 'minOffset', 'maxOffset', 'nodesTemplate', 'affectedWheelsTemplate', 'nodesCount', 'startIndex', 'collisionSamplesCount', 'hasLiftMode'))
Traces = namedtuple('Traces', ('lodDist', 'bufferPrefs', 'textureSet', 'centerOffset', 'size', 'activePostmortem'))
LeveredSuspensionConfig = namedtuple('LeveredSuspensionConfig', ('levers', 'interpolationSpeedMul', 'lodSettings', 'activePostmortem'))
SuspensionLever = namedtuple('SuspensionLever', ('startNodeName', 'jointNodeName', 'trackNodeName', 'minAngle', 'maxAngle', 'collisionSamplesCount', 'hasLiftMode', 'affectedWheelName'))
SplineSegmentModelSet = namedtuple('SplineSegmentModelSet', ('left', 'right', 'secondLeft', 'secondRight'))

class SplineConfig(object):
    __slots__ = ('__segmentModelSets', '__segmentLength', '__leftDesc', '__rightDesc', '__lodDist', '__segmentOffset', '__segment2Offset', '__atlasUTiles', '__atlasVTiles')

    def __init__(self, segmentModelSets=None, segmentLength=component_constants.ZERO_FLOAT, leftDesc=None, rightDesc=None, lodDist=None, segmentOffset=component_constants.ZERO_FLOAT, segment2Offset=component_constants.ZERO_FLOAT, atlasUTiles=component_constants.ZERO_INT, atlasVTiles=component_constants.ZERO_INT):
        super(SplineConfig, self).__init__()
        self.__segmentModelSets = {}
        segmentModelSets = segmentModelSets or {}
        for setName, setPaths in segmentModelSets.iteritems():
            left = tuple(path_builder.makeIndexes(setPaths.left))
            right = tuple(path_builder.makeIndexes(setPaths.right))
            if setPaths.secondLeft:
                secondLeft = tuple(path_builder.makeIndexes(setPaths.secondLeft))
            else:
                secondLeft = None
            if setPaths.secondRight:
                secondRight = tuple(path_builder.makeIndexes(setPaths.secondRight))
            else:
                secondRight = None
            self.__segmentModelSets[setName] = SplineSegmentModelSet(left, right, secondLeft, secondRight)

        self.__segmentLength = segmentLength
        if leftDesc is not None:
            self.__leftDesc = tuple(path_builder.makeIndexes(leftDesc))
        else:
            self.__leftDesc = component_constants.EMPTY_TUPLE
        if rightDesc is not None:
            self.__rightDesc = tuple(path_builder.makeIndexes(rightDesc))
        else:
            self.__rightDesc = component_constants.EMPTY_TUPLE
        self.__lodDist = lodDist
        self.__segmentOffset = segmentOffset
        self.__segment2Offset = segment2Offset
        self.__atlasUTiles = atlasUTiles
        self.__atlasVTiles = atlasVTiles
        return

    @property
    def segmentLength(self):
        return self.__segmentLength

    @property
    def leftDesc(self):
        return path_builder.makePath(*self.__leftDesc) if self.__leftDesc else None

    @property
    def rightDesc(self):
        return path_builder.makePath(*self.__rightDesc) if self.__rightDesc else None

    @property
    def lodDist(self):
        return self.__lodDist

    @property
    def segmentOffset(self):
        return self.__segmentOffset

    @property
    def segment2Offset(self):
        return self.__segment2Offset

    @property
    def atlasUTiles(self):
        return self.__atlasUTiles

    @property
    def atlasVTiles(self):
        return self.__atlasVTiles

    def segmentModelLeft(self, modelSet=''):
        set = self._getModelSet(modelSet)
        return path_builder.makePath(*set.left)

    def segmentModelRight(self, modelSet=''):
        set = self._getModelSet(modelSet)
        return path_builder.makePath(*set.right)

    def segment2ModelLeft(self, modelSet=''):
        set = self._getModelSet(modelSet)
        return path_builder.makePath(*set.secondLeft) if set.secondLeft else None

    def segment2ModelRight(self, modelSet=''):
        set = self._getModelSet(modelSet)
        return path_builder.makePath(*set.secondRight) if set.secondRight else None

    def _getModelSet(self, modelSet):
        set = modelSet if modelSet in self.__segmentModelSets else 'default'
        return self.__segmentModelSets[set]
