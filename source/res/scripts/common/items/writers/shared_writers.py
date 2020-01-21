# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/shared_writers.py
import ResMgr
from debug_utils import LOG_ERROR
from items.components import shared_components, component_constants
from items import _xml
import typing

def writeCustomizationSlots(slots, section, subsectionName):
    section.deleteSection(subsectionName)
    if not slots:
        return
    else:
        subsection = section.createSection(subsectionName)
        for slot in slots:
            slotDS = subsection.createSection('slot')
            slotDS.write('slotType', slot.type)
            slotDS.write('slotId', slot.slotId)
            if slot.type in component_constants.ALLOWED_SLOTS_ANCHORS:
                if slot.tags:
                    slotDS.write('tags', ' '.join(slot.tags))
                else:
                    slotDS.deleteSection('tags')
                slotDS.write('anchorPosition', slot.anchorPosition)
                slotDS.write('anchorDirection', slot.anchorDirection)
                if slot.type == 'projectionDecal':
                    if slot.attachedParts is not None:
                        partTypeToNames = slot.attachedParts.items()
                        partTypeToName = ((pType, pName) for pType, pNames in partTypeToNames for pName in pNames)
                        attachedParts = ' '.join((':'.join((str(pType), pName)) for pType, pName in partTypeToName))
                        if attachedParts:
                            slotDS.write('attachedPart', attachedParts)
                    slotDS.write('position', slot.position)
                    slotDS.write('rotation', slot.rotation)
                    slotDS.write('scale', slot.scale)
                    slotDS.write('showOn', slot.showOn)
                    _xml.rewriteBool(slotDS, 'doubleSided', slot.doubleSided, False)
                    _xml.rewriteFloat(slotDS, 'clipAngle', slot.clipAngle, 0.0)
                elif slot.applyTo:
                    slotDS.write('applyTo', slot.applyTo)
            if slot.type in component_constants.ALLOWED_EMBLEM_SLOTS:
                slotDS.write('rayStart', slot.rayStart)
                slotDS.write('rayEnd', slot.rayEnd)
                slotDS.write('rayUp', slot.rayUp)
                if slot.type == 'insigniaOnGun':
                    _xml.rewriteBool(slotDS, 'applyToFabric', slot.applyToFabric, True)
                else:
                    _xml.rewriteBool(slotDS, 'isMirrored', slot.isMirrored, False)
                if slot.type in ('fixedEmblem', 'fixedInscription'):
                    slotDS.write('emblemId', slot.emblemId)
                slotDS.write('size', slot.size)
                _xml.rewriteBool(slotDS, 'hideIfDamaged', slot.hideIfDamaged, False)
                _xml.rewriteBool(slotDS, 'isUVProportional', slot.isUVProportional, True)
            if slot.type in component_constants.ALLOWED_MISC_SLOTS:
                if slot.position is not None:
                    slotDS.write('position', slot.position)
                if slot.rotation is not None:
                    slotDS.write('rotation', slot.rotation)
                if slot.attachNode is not None:
                    slotDS.write('attachNode', slot.attachNode)
            LOG_ERROR('unexpected slot type: {}'.format(slot.type))

        return


def writeModelsSets(item, section):
    if item is None:
        return
    else:
        defaultModelPaths = item['default']
        if defaultModelPaths is None:
            return
        _xml.rewriteString(section, 'undamaged', defaultModelPaths.undamaged)
        _xml.rewriteString(section, 'destroyed', defaultModelPaths.destroyed)
        _xml.rewriteString(section, 'exploded', defaultModelPaths.exploded)
        return


def writeSwingingSettings(item, section):

    def paramsToString(floatTuple):
        return ' '.join([ '{:.2f}'.format(x) for x in floatTuple ])

    _xml.rewriteFloat(section, 'sensitivityToImpulse', item.sensitivityToImpulse)
    _xml.rewriteString(section, 'pitchParams', paramsToString(item.pitchParams))
    _xml.rewriteString(section, 'rollParams', paramsToString(item.rollParams))


def writeLodDist(dist, section, subsectionName, cache):
    reversedLodLevels = {value:key for key, value in cache.commonConfig['lodLevels'].items()}
    _xml.rewriteString(section, subsectionName, reversedLodLevels[dist])


def writeBuilders(builders, section, subsectionName):
    currentBuilderIndex = 0
    for node in section.items():
        if node[0] == subsectionName:
            if currentBuilderIndex > len(builders):
                _xml.raiseWrongXml(None, subsectionName, 'Unexpected builders count')
            builders[currentBuilderIndex].save(node[1])

    if currentBuilderIndex + 1 < len(builders):
        _xml.raiseWrongXml(None, subsectionName, 'Unexpected builders count')
    return
