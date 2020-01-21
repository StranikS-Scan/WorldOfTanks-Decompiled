# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/chassis_readers.py
import math
import ResMgr
from items import _xml
from items.components import chassis_components
from items.components import component_constants
from items.components.shared_components import LodSettings
from items.readers import shared_readers
from debug_utils import LOG_ERROR
from constants import IS_EDITOR

def readWheelsAndGroups(xmlCtx, section):
    wheelGroups = []
    wheels = []
    wheelId = 0
    defSyncAngle = section.readFloat('wheels/leadingWheelSyncAngle', 60)
    for sname, subsection in _xml.getChildren(xmlCtx, section, 'wheels'):
        if sname == 'group':
            ctx = (xmlCtx, 'wheels/group')
            group = chassis_components.WheelGroup(isLeft=_xml.readBool(ctx, subsection, 'isLeft'), template=intern(_xml.readNonEmptyString(ctx, subsection, 'template')), count=_xml.readInt(ctx, subsection, 'count', 1), startIndex=subsection.readInt('startIndex', 0), radius=_xml.readPositiveFloat(ctx, subsection, 'radius'))
            wheelGroups.append(group)
        if sname == 'wheel':
            from items.vehicles import _readHitTester, _readArmor
            ctx = (xmlCtx, 'wheels/wheel[{}]'.format(wheelId))
            radiusKey = 'radius' if subsection.has_key('radius') else 'geometry/radius'
            index = _xml.readIntOrNone(ctx, subsection, 'index')
            actualIndex = wheelId if index is None else index
            w = chassis_components.Wheel(index=index, isLeft=_xml.readBool(ctx, subsection, 'isLeft'), radius=_xml.readPositiveFloat(ctx, subsection, radiusKey), nodeName=intern(_xml.readNonEmptyString(ctx, subsection, 'name')), isLeading=subsection.readBool('isLeading', False), leadingSyncAngle=subsection.readFloat('syncAngle', defSyncAngle), hitTester=_readHitTester(ctx, subsection, 'hitTester', optional=True), materials=_readArmor(ctx, subsection, 'armor', optional=True, index=actualIndex), position=subsection.readVector3('wheelPos', (0, 0, 0)))
            wheels.append(w)
            wheelId += 1

    wheelIndices = [ wheel.index for wheel in wheels ]
    if sorted(wheelIndices) == range(len(wheels)):
        sortedWheels = [None] * len(wheels)
        for wheel in wheels:
            sortedWheels[wheel.index] = wheel

        wheels = sortedWheels
    elif wheelIndices == [None] * len(wheels):
        pass
    else:
        LOG_ERROR('Invalid wheel index detected', xmlCtx, wheels)
    return (tuple(wheelGroups), tuple(wheels))


def readGroundNodesAndGroups(xmlCtx, section, cache):
    if section['groundNodes'] is None:
        return (component_constants.EMPTY_TUPLE,
         component_constants.EMPTY_TUPLE,
         False,
         None)
    else:
        groundGroups = []
        groundNodes = []
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'groundNodes'):
            if sname == 'group':
                ctx = (xmlCtx, 'groundNodes/group')
                group = chassis_components.GroundNodeGroup(isLeft=_xml.readBool(ctx, subsection, 'isLeft'), minOffset=_xml.readFloat(ctx, subsection, 'minOffset'), maxOffset=_xml.readFloat(ctx, subsection, 'maxOffset'), nodesTemplate=intern(_xml.readNonEmptyString(ctx, subsection, 'template')), affectedWheelsTemplate=_xml.readStringOrNone(ctx, subsection, 'affectedWheelsTemplate'), nodesCount=_xml.readInt(ctx, subsection, 'count', 1), startIndex=subsection.readInt('startIndex', 0), collisionSamplesCount=subsection.readInt('collisionSamplesCount', 1), hasLiftMode=_xml.readBool(ctx, subsection, 'hasLiftMode', False))
                groundGroups.append(group)
            if sname == 'node':
                ctx = (xmlCtx, 'groundNodes/node')
                groundNode = chassis_components.GroundNode(nodeName=intern(_xml.readNonEmptyString(ctx, subsection, 'name')), affectedWheelName=_xml.readStringOrEmpty(ctx, subsection, 'affectedWheelName'), isLeft=_xml.readBool(ctx, subsection, 'isLeft'), minOffset=_xml.readFloat(ctx, subsection, 'minOffset'), maxOffset=_xml.readFloat(ctx, subsection, 'maxOffset'), collisionSamplesCount=_xml.readInt(ctx, subsection, 'collisionSamplesCount', 1), hasLiftMode=_xml.readBool(ctx, subsection, 'hasLiftMode', False))
                groundNodes.append(groundNode)

        activePostmortem = _xml.readBool(xmlCtx, section, 'groundNodes/activePostmortem', False)
        lodSettingsSection = section['groundNodes/lodSettings']
        if lodSettingsSection is not None:
            lodSettings = shared_readers.readLodSettings(xmlCtx, section['groundNodes'], cache)
        else:
            lodSettings = None
        return (tuple(groundGroups),
         tuple(groundNodes),
         activePostmortem,
         lodSettings)


def readTrackNodes(xmlCtx, section):
    if section['trackNodes'] is None:
        return component_constants.EMPTY_TUPLE
    else:
        defElasticity = _xml.readFloat(xmlCtx, section, 'trackNodes/elasticity', 1500.0)
        defDamping = _xml.readFloat(xmlCtx, section, 'trackNodes/damping', 1.0)
        defForwardElastK = _xml.readFloat(xmlCtx, section, 'trackNodes/forwardElastK', 1.0)
        defBackwardElastK = _xml.readFloat(xmlCtx, section, 'trackNodes/backwardElastK', 1.0)
        defOffset = _xml.readFloat(xmlCtx, section, 'trackNodes/offset', 0.0)
        trackNodes = []
        xmlCtx = (xmlCtx, 'trackNodes')
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'trackNodes'):
            if sname == 'node':
                ctx = (xmlCtx, 'trackNodes/node')
                name = _xml.readStringOrNone(ctx, subsection, 'leftSibling')
                if name is not None:
                    leftNodeName = intern(name)
                else:
                    leftNodeName = None
                name = _xml.readStringOrNone(ctx, subsection, 'rightSibling')
                if name is not None:
                    rightNodeName = intern(name)
                else:
                    rightNodeName = None
                trackNode = chassis_components.TrackNode(name=intern(_xml.readNonEmptyString(ctx, subsection, 'name')), isLeft=_xml.readBool(ctx, subsection, 'isLeft'), initialOffset=_xml.readFloat(ctx, subsection, 'offset', defOffset), leftNodeName=leftNodeName, rightNodeName=rightNodeName, damping=_xml.readFloat(ctx, subsection, 'damping', defDamping), elasticity=_xml.readFloat(ctx, subsection, 'elasticity', defElasticity), forwardElasticityCoeff=_xml.readFloat(ctx, subsection, 'forwardElastK', defForwardElastK), backwardElasticityCoeff=_xml.readFloat(ctx, subsection, 'backwardElastK', defBackwardElastK))
                trackNodes.append(trackNode)

        return tuple(trackNodes)


def readTrackSplineParams(xmlCtx, section):
    trackSplineParams = None
    if IS_EDITOR:
        if not section.has_key('trackThickness'):
            return
    if section['trackNodes'] is not None:
        ctx = (xmlCtx, 'trackNodes')
        trackSplineParams = chassis_components.TrackSplineParams(thickness=_xml.readFloat(ctx, section, 'trackThickness'), maxAmplitude=_xml.readFloat(ctx, section, 'trackNodes/maxAmplitude'), maxOffset=_xml.readFloat(ctx, section, 'trackNodes/maxOffset'), gravity=_xml.readFloat(ctx, section, 'trackNodes/gravity'))
        if IS_EDITOR:
            trackSplineParams.editorData._enable = _xml.readBool(ctx, section, 'trackNodes/enable', True)
            trackSplineParams.editorData.elasticity = _xml.readFloat(ctx, section, 'trackNodes/elasticity', 1500.0)
            trackSplineParams.editorData.linkBones = _xml.readBool(ctx, section, 'trackNodes/linkBones', False)
    elif section['splineDesc'] is not None or section['physicalTracks'] is not None:
        trackSplineParams = chassis_components.TrackSplineParams(thickness=_xml.readFloat(xmlCtx, section, 'trackThickness'), maxAmplitude=component_constants.ZERO_FLOAT, maxOffset=component_constants.ZERO_FLOAT, gravity=component_constants.ZERO_FLOAT)
    return trackSplineParams


def readTraces(xmlCtx, section, centerOffset, cache):
    return chassis_components.Traces(lodDist=shared_readers.readLodDist(xmlCtx, section, 'traces/lodDist', cache), bufferPrefs=intern(_xml.readNonEmptyString(xmlCtx, section, 'traces/bufferPrefs')), textureSet=intern(_xml.readNonEmptyString(xmlCtx, section, 'traces/textureSet')), centerOffset=centerOffset, size=_xml.readPositiveVector2(xmlCtx, section, 'traces/size'), activePostmortem=_xml.readBool(xmlCtx, section, 'traces/activePostmortem', False))


def readTrackBasicParams(xmlCtx, section, cache):
    tracksSection = section['tracks']
    return None if tracksSection is None else chassis_components.TrackBasicParams(lodDist=shared_readers.readLodDist(xmlCtx, section, 'tracks/lodDist', cache), leftMaterial=intern(_xml.readNonEmptyString(xmlCtx, section, 'tracks/leftMaterial')), rightMaterial=intern(_xml.readNonEmptyString(xmlCtx, section, 'tracks/rightMaterial')), textureScale=_xml.readFloat(xmlCtx, section, 'tracks/textureScale'), pairsCount=section.readInt('tracks/pairsCount', 1))


def readLeveredSuspension(xmlCtx, section, cache):
    leveredSection = section['leveredSuspension']
    if leveredSection is None:
        return
    else:
        levers = []
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'leveredSuspension'):
            if sname != 'lever':
                continue
            ctx = (xmlCtx, 'leveredSuspension/lever')
            limits = _xml.readVector2(ctx, subsection, 'limits')
            lever = chassis_components.SuspensionLever(startNodeName=intern(_xml.readNonEmptyString(ctx, subsection, 'startNode')), jointNodeName=intern(_xml.readNonEmptyString(ctx, subsection, 'jointNode')), trackNodeName=intern(_xml.readNonEmptyString(ctx, subsection, 'trackNode')), minAngle=math.radians(limits.x), maxAngle=math.radians(limits.y), collisionSamplesCount=subsection.readInt('collisionSamplesCount', 1), hasLiftMode=_xml.readBool(ctx, subsection, 'hasLiftMode', False), affectedWheelName=_xml.readStringOrEmpty(ctx, subsection, 'affectedWheelName'))
            levers.append(lever)

        ctx = (xmlCtx, 'leveredSuspension')
        leveredSuspensionConfig = chassis_components.LeveredSuspensionConfig(levers=levers, interpolationSpeedMul=_xml.readFloat(ctx, leveredSection, 'interpolationSpeedMul', 10.0), lodSettings=shared_readers.readLodSettings(ctx, leveredSection, cache), activePostmortem=_xml.readBool(ctx, leveredSection, 'activePostmortem', False))
        return leveredSuspensionConfig


def readSplineConfig(xmlCtx, section, cache):
    if not section.has_key('splineDesc'):
        return
    else:
        splineSegmentModelSets = {'default': chassis_components.SplineSegmentModelSet(left=_xml.readNonEmptyString(xmlCtx, section, 'splineDesc/segmentModelLeft'), right=_xml.readNonEmptyString(xmlCtx, section, 'splineDesc/segmentModelRight'), secondLeft=_xml.readStringOrNone(xmlCtx, section, 'splineDesc/segment2ModelLeft') or '', secondRight=_xml.readStringOrNone(xmlCtx, section, 'splineDesc/segment2ModelRight') or '')}
        modelSetsSection = section['splineDesc/modelSets']
        if modelSetsSection:
            for sname, subSection in modelSetsSection.items():
                splineSegmentModelSets[sname] = chassis_components.SplineSegmentModelSet(left=_xml.readNonEmptyString(xmlCtx, subSection, 'segmentModelLeft'), right=_xml.readNonEmptyString(xmlCtx, subSection, 'segmentModelRight'), secondLeft=_xml.readStringOrNone(xmlCtx, subSection, 'segment2ModelLeft') or '', secondRight=_xml.readStringOrNone(xmlCtx, subSection, 'segment2ModelRight') or '')

        leftDescs = []
        rightDescs = []
        multipleTracks = section['splineDesc/multipleTracks']
        if multipleTracks is not None:
            for node in multipleTracks.items():
                desc = _xml.readNonEmptyString(xmlCtx, node[1], 'desc')
                pairIdx = _xml.readNonNegativeInt(xmlCtx, node[1], 'trackPairIdx')
                length = _xml.readFloat(xmlCtx, node[1], 'segmentLength')
                offset = _xml.readFloat(xmlCtx, node[1], 'segmentOffset', 0)
                offset2 = _xml.readFloat(xmlCtx, node[1], 'segment2Offset', 0)
                descList = [desc,
                 pairIdx,
                 length,
                 offset,
                 offset2]
                if node[0] == 'left':
                    leftDescs.append(descList)
                if node[0] == 'right':
                    rightDescs.append(descList)

        else:
            length = _xml.readFloat(xmlCtx, section, 'splineDesc/segmentLength')
            offset = _xml.readFloat(xmlCtx, section, 'splineDesc/segmentOffset', 0)
            offset2 = _xml.readFloat(xmlCtx, section, 'splineDesc/segment2Offset', 0)
            leftTuple = [_xml.readStringOrNone(xmlCtx, section, 'splineDesc/left'),
             0,
             length,
             offset,
             offset2]
            rightTuple = [_xml.readStringOrNone(xmlCtx, section, 'splineDesc/right'),
             0,
             length,
             offset,
             offset2]
            leftDescs.append(leftTuple)
            rightDescs.append(rightTuple)
        return chassis_components.SplineConfig(segmentModelSets=splineSegmentModelSets, leftDesc=leftDescs, rightDesc=rightDescs, lodDist=shared_readers.readLodDist(xmlCtx, section, 'splineDesc/lodDist', cache), atlasUTiles=section.readInt('splineDesc/atlas/UTiles', 1), atlasVTiles=section.readInt('splineDesc/atlas/VTiles', 1))
