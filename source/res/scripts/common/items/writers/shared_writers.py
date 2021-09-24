# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/shared_writers.py
import ResMgr
from debug_utils import LOG_ERROR
from items.components import shared_components, component_constants, c11n_constants
from items.components.component_constants import ALLOWED_PROJECTION_DECALS_ANCHORS, ALLOWED_SLOTS_ANCHORS, ALLOWED_EMBLEM_SLOTS, ALLOWED_MISC_SLOTS
from items import _xml
import typing

def writeProjectionSlots(slotDS, slot):
    slotDS.write('compatibleModels', ' '.join(slot.compatibleModels))
    slotDS.write('position', slot.position)
    slotDS.write('rotation', slot.rotation)
    slotDS.write('scale', slot.scale)
    slotDS.write('showOn', slot.showOn)
    if slot.type != 'fixedProjectionDecal':
        slotDS.write('verticalMirror', slot.canBeMirroredVertically)
    _xml.rewriteBool(slotDS, 'doubleSided', slot.doubleSided, False)
    _xml.rewriteFloat(slotDS, 'clipAngle', slot.clipAngle, 0.0)
    if slot.type == 'projectionDecal':
        writeProjectionSlotsNotFixed(slotDS, slot)
    elif slot.type == 'fixedProjectionDecal':
        writeProjectionSlotsFixed(slotDS, slot)


def writeProjectionSlotsFixed(slotDS, slot):
    slotDS.write('itemId', slot.itemId)
    slotDS.write('options', slot.options)


def writeProjectionSlotsNotFixed(slotDS, slot):
    slotDS.write('anchorPosition', slot.anchorPosition)
    slotDS.write('anchorDirection', slot.anchorDirection)
    slotDS.write('tags', ' '.join(slot.tags))


def writeAnchorSlots(slotDS, slot):
    slotDS.deleteSection('tags')
    if slot.applyTo is not None:
        slotDS.write('applyTo', slot.applyTo)
    if slot.anchorPosition is not None:
        slotDS.write('anchorPosition', slot.anchorPosition)
    if slot.anchorDirection is not None:
        slotDS.write('anchorDirection', slot.anchorDirection)
    return


def writeEmblemSlots(slotDS, slot):
    slotDS.write('rayStart', slot.rayStart)
    slotDS.write('rayEnd', slot.rayEnd)
    slotDS.write('rayUp', slot.rayUp)
    if slot.type == 'insigniaOnGun':
        _xml.rewriteBool(slotDS, 'applyToFabric', slot.applyToFabric, True)
        _xml.rewriteString(slotDS, 'compatibleModels', ' '.join(slot.compatibleModels), '')
    else:
        _xml.rewriteBool(slotDS, 'isMirrored', slot.isMirrored, False)
    if slot.type in ('fixedEmblem', 'fixedInscription'):
        slotDS.write('emblemId', slot.emblemId)
    slotDS.write('size', slot.size)
    _xml.rewriteBool(slotDS, 'hideIfDamaged', slot.hideIfDamaged, False)
    _xml.rewriteBool(slotDS, 'isUVProportional', slot.isUVProportional, True)
    _xml.rewriteBool(slotDS, 'isMirrored', slot.isMirrored, False)


def writeMiscSlots(slotDS, slot):
    if slot.position is not None:
        slotDS.write('position', slot.position)
    if slot.rotation is not None:
        slotDS.write('rotation', slot.rotation)
    if slot.attachNode is not None:
        slotDS.write('attachNode', slot.attachNode)
    return


def writeCustomizationSlots(slots, section, subsectionName):
    section.deleteSection(subsectionName)
    if not slots:
        return
    subsection = section.createSection(subsectionName)
    for slot in slots:
        slotDS = subsection.createSection('slot')
        slotDS.write('slotType', slot.type)
        slotDS.write('slotId', slot.slotId)
        if slot.type in ALLOWED_PROJECTION_DECALS_ANCHORS:
            writeProjectionSlots(slotDS, slot)
        if slot.type in ALLOWED_SLOTS_ANCHORS:
            writeAnchorSlots(slotDS, slot)
        if slot.type in ALLOWED_EMBLEM_SLOTS:
            writeEmblemSlots(slotDS, slot)
        if slot.type in component_constants.ALLOWED_MISC_SLOTS:
            writeMiscSlots(slotDS, slot)
        LOG_ERROR('unexpected slot type: {}'.format(slot.type))


def writeModelsSets(item, section):
    if item is None:
        return
    else:
        setsSection = section['sets'] if section.has_key('sets') else None
        if setsSection is not None:
            for setName in setsSection.keys():
                if setName not in item.keys():
                    setsSection.deleteSection(setName)

        if len(item) > 1:
            if not section.has_key('sets'):
                setsSection = section.createSection('sets')
            else:
                setsSection = section['sets']
        for key in item:
            if key == 'default':
                setSection = section
            elif setsSection.has_key(key):
                setSection = setsSection[key]
            else:
                setSection = setsSection.createSection(key)
            if item[key] is not None:
                _xml.rewriteString(setSection, 'undamaged', item[key].undamaged)
                _xml.rewriteString(setSection, 'destroyed', item[key].destroyed)
                _xml.rewriteString(setSection, 'exploded', item[key].exploded)

        return


def writeSwingingSettings(item, section):

    def paramsToString(floatTuple):
        return ' '.join([ '{:.2f}'.format(x) for x in floatTuple ])

    _xml.rewriteFloat(section, 'sensitivityToImpulse', item.sensitivityToImpulse)
    _xml.rewriteString(section, 'pitchParams', paramsToString(item.pitchParams))
    _xml.rewriteString(section, 'rollParams', paramsToString(item.rollParams))


def writeLodDist(dist, section, subsectionName, cache):
    reversedLodLevels = {value:key for key, value in cache.commonConfig['lodLevels'].items()}
    return _xml.rewriteString(section, subsectionName, reversedLodLevels[dist])


def writeBuilders(builders, section, subsectionName):
    currentBuilderIndex = 0
    for node in section.items():
        if node[0] == subsectionName:
            if currentBuilderIndex > len(builders):
                _xml.raiseWrongXml(None, subsectionName, 'Unexpected builders count')
            builders[currentBuilderIndex].save(node[1])
            currentBuilderIndex += 1

    if currentBuilderIndex + 1 < len(builders):
        _xml.raiseWrongXml(None, subsectionName, 'Unexpected builders count')
    return
