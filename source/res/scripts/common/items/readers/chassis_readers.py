# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/chassis_readers.py
import math
import ResMgr
from items import _xml
from items.components import chassis_components
from items.components import component_constants
from items.components.chassis_components import SplineTrackPairDesc
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
            w = chassis_components.Wheel(index=index, isLeft=_xml.readBool(ctx, subsection, 'isLeft'), radius=_xml.readPositiveFloat(ctx, subsection, radiusKey), nodeName=intern(_xml.readNonEmptyString(ctx, subsection, 'name')), isLeading=subsection.readBool('isLeading', False), leadingSyncAngle=subsection.readFloat('syncAngle', defSyncAngle), hitTesterManager=_readHitTester(ctx, subsection, 'hitTester', optional=True), materials=_readArmor(ctx, subsection, 'armor', optional=True, index=actualIndex), position=subsection.readVector3('wheelPos', (0, 0, 0)))
            if IS_EDITOR:
                w.editorData.defSyncAngle = defSyncAngle
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
    if tracksSection is None:
        return
    else:
        trackPairs = {}
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'tracks'):
            if sname == 'trackPair':
                ctx = (xmlCtx, 'tracks/trackPair')
                idx = _xml.readInt(ctx, subsection, 'trackPairIdx')
                trackPairs[idx] = chassis_components.TrackPairParams(leftMaterial=intern(_xml.readNonEmptyString(ctx, subsection, 'leftMaterial')), rightMaterial=intern(_xml.readNonEmptyString(ctx, subsection, 'rightMaterial')), textureScale=_xml.readFloat(ctx, subsection, 'textureScale'), tracksDebris=__readDebrisParams(ctx, subsection, cache))

        if len(trackPairs) == 0:
            trackPairs[component_constants.MAIN_TRACK_PAIR_IDX] = chassis_components.TrackPairParams(leftMaterial=intern(_xml.readNonEmptyString(xmlCtx, section, 'tracks/leftMaterial')), rightMaterial=intern(_xml.readNonEmptyString(xmlCtx, section, 'tracks/rightMaterial')), textureScale=_xml.readFloat(xmlCtx, section, 'tracks/textureScale'), tracksDebris=__readDebrisParams(xmlCtx, section['tracks'], cache))
        return chassis_components.TrackBasicVisualParams(lodDist=shared_readers.readLodDist(xmlCtx, section, 'tracks/lodDist', cache), trackPairs=trackPairs)


def __readDebrisParams(xmlCtx, section, cache):
    result = [None, None]
    for name, (ctx, subSection) in _xml.getItemsWithContext(xmlCtx, section, 'trackDebris'):
        isLeft = _xml.readBool(ctx, subSection, 'isLeft')
        idx = 0 if isLeft else 1
        if result[idx] is not None:
            _xml.raiseWrongXml(ctx, name, 'isLeft is the same')
        destructionEffect = _xml.readStringOrEmpty(ctx, subSection, 'destructionEffect')
        physicalParams = None
        if subSection['physicalParams'] is not None:
            hingeJointStiffness = _xml.readFloat(ctx, subSection, 'physicalParams/hingeJointStiffness')
            physicalParams = chassis_components.PhysicalTrackDebrisParams(hingeJointStiffness)
        nodesRemap = {}
        for key, value in subSection.items():
            if key == 'remapNode':
                nodeName = _xml.readString(ctx, value, 'from')
                remapNode = _xml.readString(ctx, value, 'to')
                nodesRemap[nodeName] = remapNode

        result[idx] = chassis_components.TrackDebrisParams(destructionEffect, physicalParams, cache.getVehicleEffect(destructionEffect), nodesRemap)

    return chassis_components.TrackPairDebris(result[0], result[1]) if result[0] and result[1] else None


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


def readSplineTrackPairDesc(xmlCtx, section, cache):
    splineSegmentModelSets = {'default': chassis_components.SplineSegmentModelSet(left=_xml.readNonEmptyString(xmlCtx, section, 'segmentModelLeft'), right=_xml.readNonEmptyString(xmlCtx, section, 'segmentModelRight'), secondLeft=_xml.readStringOrNone(xmlCtx, section, 'segment2ModelLeft') or '', secondRight=_xml.readStringOrNone(xmlCtx, section, 'segment2ModelRight') or '')}
    modelSetsSection = section['modelSets']
    if modelSetsSection:
        for sname, subSection in modelSetsSection.items():
            splineSegmentModelSets[sname] = chassis_components.SplineSegmentModelSet(left=_xml.readNonEmptyString(xmlCtx, subSection, 'segmentModelLeft'), right=_xml.readNonEmptyString(xmlCtx, subSection, 'segmentModelRight'), secondLeft=_xml.readStringOrNone(xmlCtx, subSection, 'segment2ModelLeft') or '', secondRight=_xml.readStringOrNone(xmlCtx, subSection, 'segment2ModelRight') or '')

    length = _xml.readFloat(xmlCtx, section, 'segmentLength')
    offset = _xml.readFloat(xmlCtx, section, 'segmentOffset', 0)
    offset2 = _xml.readFloat(xmlCtx, section, 'segment2Offset', 0)
    trackPairIdx = section.readInt('trackPairIdx', 0)
    atlasUTiles = section.readInt('atlas/UTiles', 1)
    atlasVTiles = section.readInt('atlas/VTiles', 1)
    leftDesc = _xml.readStringOrNone(xmlCtx, section, 'left')
    rightDesc = _xml.readStringOrNone(xmlCtx, section, 'right')
    return SplineTrackPairDesc(trackPairIdx, splineSegmentModelSets, leftDesc, rightDesc, length, offset, offset2, atlasUTiles, atlasVTiles)


def readSplineConfig(xmlCtx, section, cache):
    if not section.has_key('splineDesc'):
        return None
    else:
        trackPairs = {}
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'splineDesc'):
            if sname == 'trackPair':
                ctx = (xmlCtx, 'splineDesc/trackPair')
                desc = readSplineTrackPairDesc(ctx, subsection, cache)
                trackPairs[desc.trackPairIdx] = desc

        if not trackPairs:
            trackPairs[component_constants.MAIN_TRACK_PAIR_IDX] = readSplineTrackPairDesc((xmlCtx, 'splineDesc'), section['splineDesc'], cache)
        return chassis_components.SplineConfig(trackPairs, shared_readers.readLodDist(xmlCtx, section, 'splineDesc/lodDist', cache))
