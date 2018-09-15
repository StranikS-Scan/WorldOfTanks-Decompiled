# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/chassis_readers.py
import math
import ResMgr
from items import _xml
from items.components import chassis_components
from items.components import component_constants
from items.readers import shared_readers

def readWheelsAndGroups(xmlCtx, section):
    """Reads sections 'wheels/group' and 'wheels/wheel' for each chassis.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :return: tuple(sequence of groups, sequence of wheels).
    """
    wheelGroups = []
    wheels = []
    defSyncAngle = section.readFloat('wheels/leadingWheelSyncAngle', 60)
    for sname, subsection in _xml.getChildren(xmlCtx, section, 'wheels'):
        if sname == 'group':
            ctx = (xmlCtx, 'wheels/group')
            group = chassis_components.WheelGroup(isLeft=_xml.readBool(ctx, subsection, 'isLeft'), template=_xml.readNonEmptyString(ctx, subsection, 'template'), count=_xml.readInt(ctx, subsection, 'count', 1), startIndex=subsection.readInt('startIndex', 0), radius=_xml.readPositiveFloat(ctx, subsection, 'radius'))
            wheelGroups.append(group)
        if sname == 'wheel':
            ctx = (xmlCtx, 'wheels/wheel')
            w = chassis_components.Wheel(isLeft=_xml.readBool(ctx, subsection, 'isLeft'), radius=_xml.readPositiveFloat(ctx, subsection, 'radius'), nodeName=_xml.readNonEmptyString(ctx, subsection, 'name'), isLeading=subsection.readBool('isLeading', False), leadingSyncAngle=subsection.readFloat('syncAngle', defSyncAngle))
            wheels.append(w)

    return (tuple(wheelGroups), tuple(wheels))


def readGroundNodesAndGroups(xmlCtx, section):
    """Reads section 'groundNodes' for each chassis if it has.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :return: tuple(sequence of groups, sequence of nodes).
    """
    if section['groundNodes'] is None:
        return (component_constants.EMPTY_TUPLE, component_constants.EMPTY_TUPLE)
    else:
        groundGroups = []
        groundNodes = []
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'groundNodes'):
            if sname == 'group':
                ctx = (xmlCtx, 'groundNodes/group')
                group = chassis_components.GroundNodeGroup(isLeft=_xml.readBool(ctx, subsection, 'isLeft'), minOffset=_xml.readFloat(ctx, subsection, 'minOffset'), maxOffset=_xml.readFloat(ctx, subsection, 'maxOffset'), template=_xml.readNonEmptyString(ctx, subsection, 'template'), count=_xml.readInt(ctx, subsection, 'count', 1), startIndex=subsection.readInt('startIndex', 0))
                groundGroups.append(group)
            if sname == 'node':
                ctx = (xmlCtx, 'groundNodes/node')
                groundNode = chassis_components.GroundNode(name=_xml.readNonEmptyString(ctx, subsection, 'name'), isLeft=_xml.readBool(ctx, subsection, 'isLeft'), minOffset=_xml.readFloat(ctx, subsection, 'minOffset'), maxOffset=_xml.readFloat(ctx, subsection, 'maxOffset'))
                groundNodes.append(groundNode)

        return (tuple(groundGroups), tuple(groundNodes))


def readTrackNodes(xmlCtx, section):
    """Reads section 'trackNodes' for each chassis if it has.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :return: tuple containing TrackNode items.
    """
    if section['trackNodes'] is None:
        return component_constants.EMPTY_TUPLE
    else:
        xmlCtx = (xmlCtx, 'trackNodes')
        trackNodes = []
        defElasticity = section.readFloat('trackNodes/elasticity', 1500.0)
        defDamping = section.readFloat('trackNodes/damping', 1.0)
        defForwardElastK = section.readFloat('trackNodes/forwardElastK', 1.0)
        defBackwardElastK = section.readFloat('trackNodes/backwardElastK', 1.0)
        defOffset = section.readFloat('trackNodes/offset')
        for sname, subsection in _xml.getChildren(xmlCtx, section, 'trackNodes'):
            if sname == 'node':
                ctx = (xmlCtx, 'trackNodes/node')
                trackNode = chassis_components.TrackNode(name=_xml.readNonEmptyString(ctx, subsection, 'name'), isLeft=_xml.readBool(ctx, subsection, 'isLeft'), initialOffset=subsection.readFloat('offset', defOffset), leftNodeName=_xml.readStringOrNone(ctx, subsection, 'leftSibling'), rightNodeName=_xml.readStringOrNone(ctx, subsection, 'rightSibling'), damping=subsection.readFloat('damping', defDamping), elasticity=subsection.readFloat('elasticity', defElasticity), forwardElasticityCoeff=subsection.readFloat('forwardElastK', defForwardElastK), backwardElasticityCoeff=subsection.readFloat('backwardElastK', defBackwardElastK))
                trackNodes.append(trackNode)

        return tuple(trackNodes)


def readTrackParams(xmlCtx, section):
    """Reads section 'trackNodes' for each chassis if it has.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :return: instance of TrackParams or None.
    """
    trackParams = None
    if section['trackNodes'] is not None:
        ctx = (xmlCtx, 'trackNodes')
        trackParams = chassis_components.TrackParams(thickness=_xml.readFloat(ctx, section, 'trackThickness'), maxAmplitude=_xml.readFloat(ctx, section, 'trackNodes/maxAmplitude'), maxOffset=_xml.readFloat(ctx, section, 'trackNodes/maxOffset'), gravity=_xml.readFloat(ctx, section, 'trackNodes/gravity'))
    if section['trackNodes'] is None and section['splineDesc'] is not None:
        trackParams = chassis_components.TrackParams(thickness=_xml.readFloat(xmlCtx, section, 'trackThickness'), maxAmplitude=component_constants.ZERO_FLOAT, maxOffset=component_constants.ZERO_FLOAT, gravity=component_constants.ZERO_FLOAT)
    return trackParams


def readTraces(xmlCtx, section, centerOffset, cache):
    """Reads section 'traces' for each chassis.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :param centerOffset: float containing offset by x coordinate.
    :param cache: instance of vehicles.Cache.
    :return: instance of Traces.
    """
    return chassis_components.Traces(lodDist=shared_readers.readLodDist(xmlCtx, section, 'traces/lodDist', cache), bufferPrefs=_xml.readNonEmptyString(xmlCtx, section, 'traces/bufferPrefs'), textureSet=_xml.readNonEmptyString(xmlCtx, section, 'traces/textureSet'), centerOffset=centerOffset, size=_xml.readPositiveVector2(xmlCtx, section, 'traces/size'))


def readTrackMaterials(xmlCtx, section, cache):
    """Reads section 'tracks' for each chassis to fetch configuration of materials.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :param cache: instance of vehicles.Cache.
    :return: instance of TrackMaterials.
    """
    return chassis_components.TrackMaterials(lodDist=shared_readers.readLodDist(xmlCtx, section, 'tracks/lodDist', cache), leftMaterial=_xml.readNonEmptyString(xmlCtx, section, 'tracks/leftMaterial'), rightMaterial=_xml.readNonEmptyString(xmlCtx, section, 'tracks/rightMaterial'), textureScale=_xml.readFloat(xmlCtx, section, 'tracks/textureScale'))


def readLeveredSuspension(xmlCtx, section, cache):
    """Reads levered suspension section.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :param cache: instance of vehicles.Cache.
    :return: instance of SuspensionLever for levered suspension or None.
    """
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
            lever = chassis_components.SuspensionLever(startNodeName=_xml.readNonEmptyString(ctx, subsection, 'startNode'), jointNodeName=_xml.readNonEmptyString(ctx, subsection, 'jointNode'), trackNodeName=_xml.readNonEmptyString(ctx, subsection, 'trackNode'), minAngle=math.radians(limits.x), maxAngle=math.radians(limits.y))
            levers.append(lever)

        ctx = (xmlCtx, 'leveredSuspension')
        leveredSuspensionConfig = chassis_components.LeveredSuspensionConfig(levers=levers, interpolationSpeedMul=leveredSection.readFloat('interpolationSpeedMul', 10.0), lodSettings=shared_readers.readLodSettings(ctx, leveredSection, cache))
        return leveredSuspensionConfig


def readSplineConfig(xmlCtx, section, cache):
    """Reads levered suspension section.
    :param xmlCtx: tuple(root ctx or None, path to section).
    :param section: instance of DataSection.
    :param cache: instance of vehicles.Cache.
    :return: instance of SplineConfig or None.
    """
    return None if section['splineDesc'] is None else chassis_components.SplineConfig(segmentModelLeft=_xml.readNonEmptyString(xmlCtx, section, 'splineDesc/segmentModelLeft'), segmentModelRight=_xml.readNonEmptyString(xmlCtx, section, 'splineDesc/segmentModelRight'), segmentLength=_xml.readFloat(xmlCtx, section, 'splineDesc/segmentLength'), leftDesc=_xml.readStringOrNone(xmlCtx, section, 'splineDesc/left'), rightDesc=_xml.readStringOrNone(xmlCtx, section, 'splineDesc/right'), lodDist=shared_readers.readLodDist(xmlCtx, section, 'splineDesc/lodDist', cache), segmentOffset=section.readFloat('splineDesc/segmentOffset', 0), segment2ModelLeft=_xml.readStringOrNone(xmlCtx, section, 'splineDesc/segment2ModelLeft'), segment2ModelRight=_xml.readStringOrNone(xmlCtx, section, 'splineDesc/segment2ModelRight'), segment2Offset=section.readFloat('splineDesc/segment2Offset', 0), atlasUTiles=section.readInt('splineDesc/atlas/UTiles', 1), atlasVTiles=section.readInt('splineDesc/atlas/VTiles', 1))
