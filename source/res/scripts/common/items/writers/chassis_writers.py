# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/chassis_writers.py
from items import _xml
from . import shared_writers
from items.components import component_constants
from Math import Vector3

def writeWheelsAndGroups(wheelsConfig, section):
    wheelId = 0
    groupId = 0
    defSyncAngle = section.readFloat('wheels/leadingWheelSyncAngle', 60)
    for sname, subsection in _xml.getChildren(None, section, 'wheels'):
        if sname == 'group':
            group = wheelsConfig.groups[groupId]
            _xml.rewriteString(subsection, 'template', group.template)
            _xml.rewriteInt(subsection, 'count', group.count, 1)
            _xml.rewriteInt(subsection, 'startIndex', group.startIndex, 0)
            _xml.rewriteFloat(subsection, 'radius', group.radius)
            groupId += 1
        if sname == 'wheel':
            index = _xml.readIntOrNone(None, subsection, 'index')
            if index is not None:
                wheelId = index
            wheel = wheelsConfig.wheels[wheelId]
            radiusKey = 'radius' if subsection.has_key('radius') else 'geometry/radius'
            _xml.rewriteInt(subsection, 'index', wheelId, createNew=False)
            _xml.rewriteFloat(subsection, radiusKey, wheel.radius)
            _xml.rewriteString(subsection, 'name', wheel.nodeName)
            _xml.rewriteBool(subsection, 'isLeading', wheel.isLeading)
            _xml.rewriteFloat(subsection, 'syncAngle', wheel.leadingSyncAngle, defSyncAngle)
            _xml.rewriteVector3(subsection, 'wheelPos', wheel.position, Vector3(0, 0, 0))
            wheelId += 1

    return


def writeTraces(traces, section, cache):
    shared_writers.writeLodDist(traces.lodDist, section, 'traces/lodDist', cache)
    _xml.rewriteString(section, 'traces/bufferPrefs', traces.bufferPrefs)
    _xml.rewriteString(section, 'traces/textureSet', traces.textureSet)
    _xml.rewriteVector2(section, 'traces/size', traces.size)
    _xml.rewriteBool(section, 'traces/activePostmortem', traces.activePostmortem, defaultValue=False)


def writeTrackBasicParams(trackBasicParams, section, cache):
    if trackBasicParams is None:
        return
    else:
        shared_writers.writeLodDist(trackBasicParams.lodDist, section, 'tracks/lodDist', cache)
        _xml.rewriteString(section, 'tracks/leftMaterial', trackBasicParams.leftMaterial)
        _xml.rewriteString(section, 'tracks/rightMaterial', trackBasicParams.rightMaterial)
        _xml.rewriteFloat(section, 'tracks/textureScale', trackBasicParams.textureScale)
        return


def writeTrackSplineParams(trackSplineParams, section):
    if trackSplineParams is None:
        return
    else:
        if not section.has_key('trackNodes'):
            section.createSection('trackNodes')
        _xml.rewriteFloat(section, 'trackThickness', trackSplineParams.thickness)
        _xml.rewriteBool(section, 'trackNodes/enable', trackSplineParams.editorData._enable)
        _xml.rewriteBool(section, 'trackNodes/linkBones', trackSplineParams.editorData.linkBones)
        _xml.rewriteFloat(section, 'trackNodes/maxAmplitude', trackSplineParams.maxAmplitude)
        _xml.rewriteFloat(section, 'trackNodes/maxOffset', trackSplineParams.maxOffset)
        _xml.rewriteFloat(section, 'trackNodes/gravity', trackSplineParams.gravity)
        _xml.rewriteFloat(section, 'trackNodes/elasticity', trackSplineParams.editorData.elasticity)
        _xml.rewriteFloat(section, 'trackNodes/damping', trackSplineParams.editorData.damping)
        return


def writeTrackNodes(nodes, section):
    defForwardElastK = section.readFloat('trackNodes/forwardElastK', 1.0)
    defBackwardElastK = section.readFloat('trackNodes/backwardElastK', 1.0)
    defOffset = section.readFloat('trackNodes/offset', 0.0)

    def writeTrackNode(curNode, curSection):
        _xml.rewriteBool(curSection, 'isLeft', curNode.isLeft)
        _xml.rewriteString(curSection, 'name', curNode.name)
        _xml.rewriteFloat(curSection, 'forwardElastK', curNode.forwardElasticityCoeff, defForwardElastK)
        _xml.rewriteFloat(curSection, 'backwardElastK', curNode.backwardElasticityCoeff, defBackwardElastK)
        _xml.rewriteFloat(curSection, 'offset', curNode.initialOffset, defOffset)
        if curNode.leftNodeName:
            _xml.rewriteString(curSection, 'leftSibling', curNode.leftNodeName)
        if curNode.rightNodeName:
            _xml.rewriteString(curSection, 'rightSibling', curNode.rightNodeName)

    if len(nodes) == 0:
        return
    else:
        sectionParent = section['trackNodes'] if section.has_key('trackNodes') else section.createSection('trackNodes')
        sectionToSave = None
        for node in nodes:
            for childSectionName, childSection in sectionParent.items():
                if childSectionName == 'node' and node.name == childSection.readString('name'):
                    sectionToSave = childSection
                    break
            else:
                sectionToSave = sectionParent.createSection('node')

            writeTrackNode(node, sectionToSave)

        return


def writeGroundNodes(groups, section):

    def writeGroundNode(curGroup, curSection):
        _xml.rewriteString(curSection, 'template', curGroup.nodesTemplate)
        _xml.rewriteInt(curSection, 'startIndex', curGroup.startIndex)
        _xml.rewriteInt(curSection, 'count', curGroup.nodesCount)
        _xml.rewriteBool(curSection, 'isLeft', curGroup.isLeft)
        _xml.rewriteFloat(curSection, 'minOffset', curGroup.minOffset)
        _xml.rewriteFloat(curSection, 'maxOffset', curGroup.maxOffset)

    sectionParent = section['groundNodes'] if section.has_key('groundNodes') else section.createSection('groundNodes')
    sectionToSave = None
    for node in groups:
        for childSectionName, childSection in sectionParent.items():
            if childSectionName == 'group' and node.nodesTemplate == childSection.readString('template'):
                sectionToSave = childSection
                break
        else:
            sectionToSave = sectionParent.createSection('group')

        writeGroundNode(node, sectionToSave)

    return


def writeSplineDesc(splineDesc, section, cache):
    if splineDesc is None:
        return
    else:

        def writeOneSectionParams(item, sect):
            segment2ModelLeft = item.segment2ModelLeft()
            segment2ModelRight = item.segment2ModelRight()
            _xml.rewriteString(sect, 'segmentModelLeft', item.segmentModelLeft())
            _xml.rewriteString(sect, 'segmentModelRight', item.segmentModelRight())
            if segment2ModelLeft is not None:
                _xml.rewriteString(sect, 'segment2ModelLeft', segment2ModelLeft)
            if segment2ModelRight is not None:
                _xml.rewriteString(sect, 'segment2ModelRight', segment2ModelRight)
            _xml.rewriteString(sect, 'left', item.leftDesc[0][0])
            _xml.rewriteString(sect, 'right', item.rightDesc[0][0])
            _xml.rewriteFloat(sect, 'segmentLength', item.editorData.leftDesc[0][2])
            _xml.rewriteFloat(sect, 'segmentOffset', item.editorData.leftDesc[0][3])
            if item.editorData.leftDesc[0][4] != 0.0:
                _xml.rewriteFloat(sect, 'segment2Offset', item.editorData.leftDesc[0][4])
            shared_writers.writeLodDist(item.lodDist, sect, 'lodDist', cache)
            _xml.rewriteInt(sect, 'atlas/UTiles', item.atlasUTiles)
            _xml.rewriteInt(sect, 'atlas/VTiles', item.atlasVTiles)
            return

        newSection = section['splineDesc'] if section.has_key('splineDesc') else section.createSection('splineDesc')
        if len(splineDesc.editorData.leftDesc) == 1:
            writeOneSectionParams(splineDesc, newSection)
        else:
            if newSection.has_key('multipleTracks'):
                multipleTracks = newSection['multipleTracks']
            else:
                multipleTracks = newSection.createSection('multipleTracks')
            for sname, node in multipleTracks.items():
                writeOneSectionParams(splineDesc, node)

        return
