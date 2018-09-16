# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/chassis_components.py
from collections import namedtuple
from items.components import component_constants
from items.components import path_builder
from items.components import shared_components
__all__ = ('Wheel', 'WheelGroup', 'TrackNode', 'TrackMaterials', 'GroundNode', 'GroundNodeGroup', 'Traces', 'LeveredSuspensionConfig', 'SuspensionLever')
Wheel = namedtuple('Wheel', ('isLeft', 'radius', 'nodeName', 'isLeading', 'leadingSyncAngle'))
WheelGroup = namedtuple('WheelGroup', ('isLeft', 'template', 'count', 'startIndex', 'radius'))
WheelsConfig = namedtuple('WheelsConfig', ('lodDist', 'groups', 'wheels'))
TrackNode = namedtuple('TrackNode', ('name', 'isLeft', 'initialOffset', 'leftNodeName', 'rightNodeName', 'damping', 'elasticity', 'forwardElasticityCoeff', 'backwardElasticityCoeff'))
TrackMaterials = namedtuple('TrackNode', ('lodDist', 'leftMaterial', 'rightMaterial', 'textureScale'))
TrackParams = namedtuple('TrackNode', ('thickness', 'maxAmplitude', 'maxOffset', 'gravity'))
GroundNode = namedtuple('GroundNode', ('name', 'isLeft', 'minOffset', 'maxOffset'))
GroundNodeGroup = namedtuple('GroundNodeGroup', ('isLeft', 'minOffset', 'maxOffset', 'template', 'count', 'startIndex'))
Traces = namedtuple('Traces', ('lodDist', 'bufferPrefs', 'textureSet', 'centerOffset', 'size'))
LeveredSuspensionConfig = namedtuple('LeveredSuspensionConfig', ('levers', 'interpolationSpeedMul', 'lodSettings'))
SuspensionLever = namedtuple('SuspensionLever', ('startNodeName', 'jointNodeName', 'trackNodeName', 'minAngle', 'maxAngle'))

class SplineConfig(object):
    __slots__ = ('__segmentModelLeft', '__segmentModelRight', '__segmentLength', '__leftDesc', '__rightDesc', '__lodDist', '__segmentOffset', '__segment2ModelLeft', '__segment2ModelRight', '__segment2Offset', '__atlasUTiles', '__atlasVTiles')

    def __init__(self, segmentModelLeft=component_constants.EMPTY_STRING, segmentModelRight=component_constants.EMPTY_STRING, segmentLength=component_constants.ZERO_FLOAT, leftDesc=None, rightDesc=None, lodDist=None, segmentOffset=component_constants.ZERO_FLOAT, segment2ModelLeft=None, segment2ModelRight=None, segment2Offset=component_constants.ZERO_FLOAT, atlasUTiles=component_constants.ZERO_INT, atlasVTiles=component_constants.ZERO_INT):
        super(SplineConfig, self).__init__()
        self.__segmentModelLeft = tuple(path_builder.makeIndexes(segmentModelLeft))
        self.__segmentModelRight = tuple(path_builder.makeIndexes(segmentModelRight))
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
        if segment2ModelLeft is not None:
            self.__segment2ModelLeft = tuple(path_builder.makeIndexes(segment2ModelLeft))
        else:
            self.__segment2ModelLeft = component_constants.EMPTY_TUPLE
        if segment2ModelRight is not None:
            self.__segment2ModelRight = tuple(path_builder.makeIndexes(segment2ModelRight))
        else:
            self.__segment2ModelRight = component_constants.EMPTY_TUPLE
        self.__segment2Offset = segment2Offset
        self.__atlasUTiles = atlasUTiles
        self.__atlasVTiles = atlasVTiles
        return

    @property
    def segmentModelLeft(self):
        return path_builder.makePath(*self.__segmentModelLeft)

    @property
    def segmentModelRight(self):
        return path_builder.makePath(*self.__segmentModelRight)

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
    def segment2ModelLeft(self):
        return path_builder.makePath(*self.__segment2ModelLeft) if self.__segment2ModelLeft else None

    @property
    def segment2ModelRight(self):
        return path_builder.makePath(*self.__segment2ModelRight) if self.__segment2ModelRight else None

    @property
    def segment2Offset(self):
        return self.__segment2Offset

    @property
    def atlasUTiles(self):
        return self.__atlasUTiles

    @property
    def atlasVTiles(self):
        return self.__atlasVTiles
