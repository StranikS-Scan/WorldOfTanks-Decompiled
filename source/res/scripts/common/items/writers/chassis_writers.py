# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/chassis_writers.py
from items import _xml
from . import shared_writers
from items.components import component_constants
from Math import Vector3
import ResMgr

def writeWheelsAndGroups(wheelsConfig, section, materialData, chassisName):
    wheelId = 0
    groupId = 0
    defSyncAngle = section.readFloat('wheels/leadingWheelSyncAngle', 60)
    for sname, subsection in _xml.getChildren(None, section, 'wheels'):
        if sname == 'group':
            group = wheelsConfig.groups[groupId]
            radiusKey = 'radius' if subsection.has_key('radius') else 'geometry/radius'
            _xml.rewriteString(subsection, 'template', group.template)
            _xml.rewriteInt(subsection, 'count', group.count)
            _xml.rewriteInt(subsection, 'startIndex', group.startIndex)
            _xml.rewriteFloat(subsection, radiusKey, group.radius)
            groupId += 1
        if sname == 'wheel':
            from items.vehicles import _writeHitTester, _writeArmor
            index = _xml.readIntOrNone(None, subsection, 'index')
            if index is not None:
                wheelId = index
            wheel = wheelsConfig.wheels[wheelId]
            radiusKey = 'radius' if subsection.has_key('radius') else 'geometry/radius'
            _xml.rewriteInt(subsection, 'index', wheelId, createNew=False)
            _xml.rewriteFloat(subsection, radiusKey, wheel.radius)
            _xml.rewriteString(subsection, 'name', wheel.nodeName)
            _xml.rewriteBool(subsection, 'isLeading', wheel.isLeading, False)
            _xml.rewriteFloat(subsection, 'syncAngle', wheel.leadingSyncAngle, defSyncAngle)
            _xml.rewriteVector3(subsection, 'wheelPos', wheel.position, Vector3(0, 0, 0))
            _writeHitTester(wheel.hitTesterManager, None, subsection, 'hitTester')
            wheelMatData = materialData.get('wheel' + str(wheelId), None)
            wheelMatData = wheelMatData.get(chassisName, None) if wheelMatData is not None else None
            _writeArmor(wheel.materials, subsection, wheelMatData)
            wheelId += 1

    return


def writeTraces(tracesConfig, section, cache):
    tracesSection = section['traces']
    if tracesSection is None:
        tracesSection = section.createSection('traces')
    else:
        for childSectionName, _ in tracesSection.items():
            tracesSection.deleteSection(childSectionName)

    shared_writers.writeLodDist(tracesConfig.lodDist, tracesSection, 'lodDist', cache)
    _xml.rewriteBool(tracesSection, 'activePostmortem', tracesConfig.activePostmortem)
    for _, tracesParams in tracesConfig.tracesParams.iteritems():
        tracesParamsSection = tracesSection.createSection('tracesParams')
        _xml.rewriteInt(tracesParamsSection, 'trackPairIdx', tracesParams.trackPairIdx)
        _xml.rewriteString(tracesParamsSection, 'bufferPrefs', tracesParams.bufferPrefs)
        _xml.rewriteString(tracesParamsSection, 'textureSet', tracesParams.textureSet)
        _xml.rewriteVector2(tracesParamsSection, 'size', tracesParams.size)
        _xml.rewriteVector2(tracesParamsSection, 'offset', tracesParams.offset)
        _xml.rewriteVector2(tracesParamsSection, 'centerOffsetFactor', tracesParams.centerOffsetFactor)

    return


def writeTrackBasicParams(trackBasicParams, section, cache):
    if trackBasicParams is None:
        return
    else:
        tracksSection = section['tracks']
        for childSectionName, childSection in tracksSection.items():
            tracksSection.deleteSection(childSectionName)

        shared_writers.writeLodDist(trackBasicParams.lodDist, section, 'tracks/lodDist', cache)
        for idx, trackPair in enumerate(trackBasicParams.trackPairs.values()):
            trackPairSection = tracksSection.createSection('trackPair')
            trackPairSection.writeInt('trackPairIdx', idx)
            __writeTrackPairParams(trackPair, trackPairSection)

        return


def __writeTrackPairParams(trackPairParams, section):
    _xml.rewriteString(section, 'leftMaterial', trackPairParams.leftMaterial)
    _xml.rewriteString(section, 'rightMaterial', trackPairParams.rightMaterial)
    _xml.rewriteFloat(section, 'textureScale', trackPairParams.textureScale)
    __writeDebris(trackPairParams.tracksDebris, section)


def __writeDebris(tracksDebris, section):
    if tracksDebris is None:
        return
    else:
        for sname, subsection in section.items():
            if sname == 'trackDebris':
                section.deleteSection(sname)

        leftDebrisSection = section.createSection('trackDebris')
        leftDebrisSection.writeBool('isLeft', True)
        leftDebris = tracksDebris.left
        if leftDebris is not None:
            _xml.rewriteString(leftDebrisSection, 'destructionEffect', leftDebris.destructionEffect)
            for key, value in leftDebris.nodesRemap.items():
                remapNodeSection = leftDebrisSection.createSection('remapNode')
                remapNodeSection.writeString('from', key)
                remapNodeSection.writeString('to', value)

            if leftDebris.physicalParams is not None:
                physicalParamsSection = leftDebrisSection.createSection('physicalParams')
                leftDebris.physicalParams.save(physicalParamsSection)
        rightDebrisSection = section.createSection('trackDebris')
        rightDebrisSection.writeBool('isLeft', False)
        rightDebris = tracksDebris.right
        if rightDebris is not None:
            _xml.rewriteString(rightDebrisSection, 'destructionEffect', rightDebris.destructionEffect)
            if rightDebris.nodesRemap is not None:
                for key, value in rightDebris.nodesRemap.items():
                    remapNodeSection = rightDebrisSection.createSection('remapNode')
                    remapNodeSection.writeString('from', key)
                    remapNodeSection.writeString('to', value)

            if rightDebris.physicalParams is not None:
                physicalParamsSection = rightDebrisSection.createSection('physicalParams')
                rightDebris.physicalParams.save(physicalParamsSection)
        return


def writeTrackNodesAndSplineParams(nodes, trackSplineParams, section):
    if trackSplineParams is None:
        return
    elif len(nodes) == 0:
        if section.has_key('trackNodes'):
            section.deleteSection('trackNodes')
        return
    else:
        if section.has_key('trackThickness'):
            section.deleteSection('trackThickness')
        trackNodesSection = section['trackNodes'] if section.has_key('trackNodes') else section.createSection('trackNodes')
        for childSectionName, _ in trackNodesSection.items():
            trackNodesSection.deleteSection(childSectionName)

        def writeSplineParams(params, curSection):
            _xml.rewriteFloat(curSection, 'trackPairIdx', params.trackPairIdx)
            _xml.rewriteFloat(curSection, 'trackThickness', params.thickness)
            _xml.rewriteFloat(curSection, 'maxAmplitude', params.maxAmplitude)
            _xml.rewriteFloat(curSection, 'maxOffset', params.maxOffset)
            _xml.rewriteFloat(curSection, 'gravity', params.gravity)
            _xml.rewriteFloat(curSection, 'damping', params.editorData.damping)
            _xml.rewriteBool(curSection, 'enable', params.editorData._enable)
            _xml.rewriteBool(curSection, 'linkBones', params.editorData.linkBones)
            _xml.rewriteFloat(curSection, 'elasticity', params.editorData.elasticity)

        def writeTrackNode(curNode, curSection):
            _xml.rewriteBool(curSection, 'isLeft', curNode.isLeft)
            _xml.rewriteString(curSection, 'name', curNode.name)
            _xml.rewriteFloat(curSection, 'forwardElastK', curNode.forwardElasticityCoeff, 1.0)
            _xml.rewriteFloat(curSection, 'backwardElastK', curNode.backwardElasticityCoeff, 1.0)
            _xml.rewriteFloat(curSection, 'offset', curNode.initialOffset, 0.0)
            _xml.rewriteFloat(curSection, 'trackPairIdx', curNode.trackPairIndex)
            if curNode.leftNodeName:
                _xml.rewriteString(curSection, 'leftSibling', curNode.leftNodeName)
            if curNode.rightNodeName:
                _xml.rewriteString(curSection, 'rightSibling', curNode.rightNodeName)

        for _, params in trackSplineParams.iteritems():
            pairSection = trackNodesSection.createSection('trackPair')
            writeSplineParams(params, pairSection)
            for node in nodes:
                if node.trackPairIndex != params.trackPairIdx:
                    continue
                for childSectionName, childSection in pairSection.items():
                    if childSectionName == 'node' and node.name == childSection.readString('name'):
                        sectionToSave = childSection
                        break
                else:
                    sectionToSave = pairSection.createSection('node')

                writeTrackNode(node, sectionToSave)

        return


def writeGroundNodes(nodes, section):
    if len(nodes) == 0:
        return
    sectionParent = section['groundNodes'] if section.has_key('groundNodes') else section.createSection('groundNodes')
    for _, childSection in sectionParent.items():
        sectionParent.deleteSection(childSection)

    def writeGroundNode(curNode, curSection):
        _xml.rewriteString(curSection, 'name', curNode.nodeName)
        _xml.rewriteString(curSection, 'affectedWheelName', curNode.affectedWheelName, '')
        _xml.rewriteInt(curSection, 'collisionSamplesCount', curNode.collisionSamplesCount)
        _xml.rewriteBool(curSection, 'isLeft', curNode.isLeft)
        _xml.rewriteFloat(curSection, 'minOffset', curNode.minOffset)
        _xml.rewriteFloat(curSection, 'maxOffset', curNode.maxOffset)
        _xml.rewriteInt(curSection, 'trackPairIdx', curNode.trackPairIdx)

    for node in nodes:
        sectionToSave = sectionParent.createSection('node')
        writeGroundNode(node, sectionToSave)


def writeSplineDesc(splineDesc, section, cache):
    if splineDesc is None:
        return
    else:

        def writeTrackPairParams(item, section):
            segment2ModelLeft = item.segment2ModelLeft()
            segment2ModelRight = item.segment2ModelRight()
            _xml.rewriteInt(section, 'trackPairIdx', item.trackPairIdx)
            _xml.rewriteString(section, 'segmentModelLeft', item.segmentModelLeft())
            _xml.rewriteString(section, 'segmentModelRight', item.segmentModelRight())
            if segment2ModelLeft is not None:
                _xml.rewriteString(section, 'segment2ModelLeft', segment2ModelLeft)
            if segment2ModelRight is not None:
                _xml.rewriteString(section, 'segment2ModelRight', segment2ModelRight)
            _xml.rewriteString(section, 'left', item.leftDesc)
            _xml.rewriteString(section, 'right', item.rightDesc)
            _xml.rewriteFloat(section, 'segmentLength', item.segmentLength)
            _xml.rewriteFloat(section, 'segmentOffset', item.segmentOffset)
            if item.segment2Offset != 0.0:
                _xml.rewriteFloat(section, 'segment2Offset', item.segment2Offset)
            _xml.rewriteInt(section, 'atlas/UTiles', item.atlasUTiles)
            _xml.rewriteInt(section, 'atlas/VTiles', item.atlasVTiles)
            return

        def writeModelSets(item, section):
            if len(item.segmentModelSets) < 2:
                return
            modelSetsSection = section.createSection('modelSets')
            for modelSetName, modelSet in item.segmentModelSets.iteritems():
                if modelSetName == 'default':
                    continue
                currentModelSetSection = modelSetsSection.createSection(modelSetName)
                _xml.rewriteString(currentModelSetSection, 'segmentModelLeft', modelSet.editorLeft)
                _xml.rewriteString(currentModelSetSection, 'segmentModelRight', modelSet.editorRight)
                _xml.rewriteString(currentModelSetSection, 'segment2ModelLeft', modelSet.editorSecondLeft, '')
                _xml.rewriteString(currentModelSetSection, 'segment2ModelRight', modelSet.editorSecondRight, '')

        if section.has_key('splineDesc'):
            section.deleteSection('splineDesc')
        newSplineDescSection = section.insertSection('splineDesc', section.getFirstIndex('physicalTracks'))
        for trackPair in splineDesc.trackPairs.values():
            pairSection = newSplineDescSection.createSection('trackPair')
            writeTrackPairParams(trackPair, pairSection)
            writeModelSets(trackPair, pairSection)

        shared_writers.writeLodDist(splineDesc.lodDist, newSplineDescSection, 'lodDist', cache)
        return


def writeMudEffect(effect, cache, section, subsectionName):
    for n, e in cache._customEffects['slip'].iteritems():
        if e is effect:
            return _xml.rewriteString(section, subsectionName, n)

    return False
