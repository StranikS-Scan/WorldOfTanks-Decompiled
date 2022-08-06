# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/chassis_components.py
from collections import namedtuple
from copy import deepcopy
from wrapped_reflection_framework import reflectedNamedTuple, ReflectionMetaclass
from items.components import component_constants
from items.components import path_builder
from items.components import shared_components
__all__ = ('Wheel', 'WheelGroup', 'TrackPair', 'TrackNode', 'TrackBasicVisualParams', 'TrackPairParams', 'TrackPairDebris', 'TrackDebrisParams', 'GroundNode', 'GroundNodeGroup', 'Traces', 'LeveredSuspensionConfig', 'SuspensionLever', 'SplineSegmentModelSet')
Wheel = reflectedNamedTuple('Wheel', ('index', 'isLeft', 'radius', 'nodeName', 'isLeading', 'leadingSyncAngle', 'hitTesterManager', 'materials', 'position'))
Wheel.hitTester = property(lambda self: self.hitTesterManager.activeHitTester)
WheelGroup = reflectedNamedTuple('WheelGroup', ('isLeft', 'template', 'count', 'startIndex', 'radius'))
WheelsConfig = reflectedNamedTuple('WheelsConfig', ('groups', 'wheels'))
TrackPair = namedtuple('TrackPair', ('hitTesterManager', 'materials', 'healthParams', 'breakMode'))
TrackPair.hitTester = property(lambda self: self.hitTesterManager.activeHitTester)
TrackNode = reflectedNamedTuple('TrackNode', ('name', 'isLeft', 'initialOffset', 'leftNodeName', 'rightNodeName', 'damping', 'elasticity', 'forwardElasticityCoeff', 'backwardElasticityCoeff'))
TrackBasicVisualParams = reflectedNamedTuple('TrackBasicVisualParams', ('lodDist', 'trackPairs'))
TrackPairParams = reflectedNamedTuple('TrackPairParams', ('leftMaterial', 'rightMaterial', 'textureScale', 'tracksDebris'))
TrackPairDebris = reflectedNamedTuple('TrackPairDebris', ('left', 'right'))
TrackDebrisParams = reflectedNamedTuple('TrackDebrisParams', ('destructionEffect', 'physicalParams', 'destructionEffectData', 'nodesRemap'))
TrackSplineParams = reflectedNamedTuple('TrackSplineParams', ('thickness', 'maxAmplitude', 'maxOffset', 'gravity'))
GroundNode = namedtuple('GroundNode', ('nodeName', 'affectedWheelName', 'isLeft', 'minOffset', 'maxOffset', 'collisionSamplesCount', 'hasLiftMode'))
GroundNodeGroup = namedtuple('GroundNodeGroup', ('isLeft', 'minOffset', 'maxOffset', 'nodesTemplate', 'affectedWheelsTemplate', 'nodesCount', 'startIndex', 'collisionSamplesCount', 'hasLiftMode'))
Traces = reflectedNamedTuple('Traces', ('lodDist', 'bufferPrefs', 'textureSet', 'centerOffset', 'size', 'activePostmortem'))
LeveredSuspensionConfig = reflectedNamedTuple('LeveredSuspensionConfig', ('levers', 'interpolationSpeedMul', 'lodSettings', 'activePostmortem'))
SuspensionLever = reflectedNamedTuple('SuspensionLever', ('startNodeName', 'jointNodeName', 'trackNodeName', 'minAngle', 'maxAngle', 'collisionSamplesCount', 'hasLiftMode', 'affectedWheelName'))
SplineSegmentModelSet = reflectedNamedTuple('SplineSegmentModelSet', ('left', 'right', 'secondLeft', 'secondRight'))

class SplineTrackPairDesc(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('trackPairIdx', 'segmentModelSets', 'leftDesc', 'rightDesc', 'segmentLength', 'segmentOffset', 'segment2Offset', 'atlasUTiles', 'atlasVTiles')

    def __init__(self, trackPairIdx, segmentModelSets, leftDesc, rightDesc, segmentLength, segmentOffset, segment2Offset, atlasUTiles, atlasVTiles):
        self.trackPairIdx = trackPairIdx
        self.leftDesc = leftDesc
        self.rightDesc = rightDesc
        self.segmentLength = segmentLength
        self.segmentOffset = segmentOffset
        self.segment2Offset = segment2Offset
        self.atlasUTiles = atlasUTiles
        self.atlasVTiles = atlasVTiles
        self.segmentModelSets = {}
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
            self.segmentModelSets[setName] = SplineSegmentModelSet(left, right, secondLeft, secondRight)

        return

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
        modelSet = modelSetName if modelSetName in self.segmentModelSets else 'default'
        return self.segmentModelSets[modelSet]

    def prerequisites(self, modelSet):
        res = (self.segmentModelRight(modelSet),
         self.segmentModelLeft(modelSet),
         self.segment2ModelRight(modelSet),
         self.segment2ModelLeft(modelSet),
         self.leftDesc,
         self.rightDesc)
        return res


SplineConfig = reflectedNamedTuple('SplineConfig', ('trackPairs', 'lodDist'))
