# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/chassis_components.py
from collections import namedtuple
from copy import deepcopy
from wrapped_reflection_framework import reflectedNamedTuple, ReflectionMetaclass
from items.components import component_constants
from items.components import path_builder
from items.components import shared_components
__all__ = ('Wheel', 'WheelGroup', 'TrackNode', 'TrackBasicParams', 'GroundNode', 'GroundNodeGroup', 'Traces', 'LeveredSuspensionConfig', 'SuspensionLever', 'SplineSegmentModelSet')
Wheel = reflectedNamedTuple('Wheel', ('index', 'isLeft', 'radius', 'nodeName', 'isLeading', 'leadingSyncAngle', 'hitTester', 'materials', 'position'))
WheelGroup = reflectedNamedTuple('WheelGroup', ('isLeft', 'template', 'count', 'startIndex', 'radius'))
WheelsConfig = reflectedNamedTuple('WheelsConfig', ('groups', 'wheels'))
TrackNode = reflectedNamedTuple('TrackNode', ('name', 'isLeft', 'initialOffset', 'leftNodeName', 'rightNodeName', 'damping', 'elasticity', 'forwardElasticityCoeff', 'backwardElasticityCoeff'))
TrackBasicParams = reflectedNamedTuple('TrackBasicParams', ('lodDist', 'leftMaterial', 'rightMaterial', 'textureScale', 'pairsCount'))
TrackSplineParams = reflectedNamedTuple('TrackSplineParams', ('thickness', 'maxAmplitude', 'maxOffset', 'gravity'))
GroundNode = namedtuple('GroundNode', ('nodeName', 'affectedWheelName', 'isLeft', 'minOffset', 'maxOffset', 'collisionSamplesCount', 'hasLiftMode'))
GroundNodeGroup = namedtuple('GroundNodeGroup', ('isLeft', 'minOffset', 'maxOffset', 'nodesTemplate', 'affectedWheelsTemplate', 'nodesCount', 'startIndex', 'collisionSamplesCount', 'hasLiftMode'))
Traces = reflectedNamedTuple('Traces', ('lodDist', 'bufferPrefs', 'textureSet', 'centerOffset', 'size', 'activePostmortem'))
LeveredSuspensionConfig = namedtuple('LeveredSuspensionConfig', ('levers', 'interpolationSpeedMul', 'lodSettings', 'activePostmortem'))
SuspensionLever = namedtuple('SuspensionLever', ('startNodeName', 'jointNodeName', 'trackNodeName', 'minAngle', 'maxAngle', 'collisionSamplesCount', 'hasLiftMode', 'affectedWheelName'))
SplineSegmentModelSet = reflectedNamedTuple('SplineSegmentModelSet', ('left', 'right', 'secondLeft', 'secondRight'))

class SplineConfig(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('__segmentModelSets', '__leftDesc', '__rightDesc', '__lodDist', '__atlasUTiles', '__atlasVTiles')

    def __init__(self, segmentModelSets=None, leftDesc=None, rightDesc=None, lodDist=None, atlasUTiles=component_constants.ZERO_INT, atlasVTiles=component_constants.ZERO_INT):
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

        self.__leftDesc = []
        if len(leftDesc) > 0:
            for desc in leftDesc:
                desc[0] = tuple(path_builder.makeIndexes(desc[0]))
                self.__leftDesc.append(desc)

        else:
            self.__leftDesc = component_constants.EMPTY_TUPLE
        self.__rightDesc = []
        if len(rightDesc) > 0:
            for desc in rightDesc:
                desc[0] = tuple(path_builder.makeIndexes(desc[0]))
                self.__rightDesc.append(desc)

        else:
            self.__rightDesc = component_constants.EMPTY_TUPLE
        self.__lodDist = lodDist
        self.__atlasUTiles = atlasUTiles
        self.__atlasVTiles = atlasVTiles
        return

    @property
    def leftDesc(self):
        ret = []
        if self.__leftDesc:
            for desc in self.__leftDesc:
                unpackedTuple = deepcopy(desc)
                unpackedTuple[0] = path_builder.makePath(*unpackedTuple[0])
                ret.append(unpackedTuple)

        return ret

    @property
    def rightDesc(self):
        ret = []
        if self.__rightDesc:
            for desc in self.__rightDesc:
                unpackedTuple = deepcopy(desc)
                unpackedTuple[0] = path_builder.makePath(*unpackedTuple[0])
                ret.append(unpackedTuple)

        return ret

    @property
    def lodDist(self):
        return self.__lodDist

    @property
    def atlasUTiles(self):
        return self.__atlasUTiles

    @property
    def atlasVTiles(self):
        return self.__atlasVTiles

    @property
    def segmentModelSets(self):
        return self.__segmentModelSets

    def segmentModelLeft(self, modelSetName=''):
        modelSet = self._getModelSet(modelSetName)
        return path_builder.makePath(*modelSet.left)

    def segmentModelRight(self, modelSetName=''):
        modelSet = self._getModelSet(modelSetName)
        return path_builder.makePath(*modelSet.right)

    def segment2ModelLeft(self, modelSetName=''):
        modelSet = self._getModelSet(modelSetName)
        return path_builder.makePath(*modelSet.secondLeft) if modelSet.secondLeft else None

    def segment2ModelRight(self, modelSetName=''):
        modelSet = self._getModelSet(modelSetName)
        return path_builder.makePath(*modelSet.secondRight) if modelSet.secondRight else None

    def _getModelSet(self, modelSetName):
        modelSet = modelSetName if modelSetName in self.__segmentModelSets else 'default'
        return self.__segmentModelSets[modelSet]
