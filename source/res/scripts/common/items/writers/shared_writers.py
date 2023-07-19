# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/writers/shared_writers.py
import ResMgr
from debug_utils import LOG_ERROR
from items.components import shared_components, component_constants, c11n_constants
from items.components.component_constants import ALLOWED_PROJECTION_DECALS_ANCHORS, ALLOWED_SLOTS_ANCHORS, ALLOWED_EMBLEM_SLOTS, ALLOWED_MISC_SLOTS
from items import _xml
import typing
from constants import IS_UE_EDITOR
if IS_UE_EDITOR:
    from combined_data_section import CombinedDataSection

def writeProjectionSlots(slotDS, slot):
    if slot.type == 'projectionDecal':
        slotDS.write('tags', ' '.join(slot.tags))
    if len(slot.compatibleModels) == 1 and slot.compatibleModels[0] == 'default':
        slotDS.deleteSection('compatibleModels')
    else:
        slotDS.write('compatibleModels', ' '.join(slot.compatibleModels))
    slotDS.writeVector3('position', slot.position)
    slotDS.writeVector3('rotation', slot.rotation)
    slotDS.writeVector3('scale', slot.scale)
    _xml.rewriteBool(slotDS, 'doubleSided', slot.doubleSided, False)
    _xml.rewriteBool(slotDS, 'hiddenForUser', slot.hiddenForUser, False)
    slotDS.write('showOn', slot.showOn)
    _xml.rewriteFloat(slotDS, 'clipAngle', slot.clipAngle, c11n_constants.DEFAULT_DECAL_CLIP_ANGLE)
    _xml.rewriteBool(slotDS, 'verticalMirror', slot.canBeMirroredVertically, False)
    if slot.type == 'projectionDecal':
        _xml.rewriteFloat(slotDS, 'anchorShift', slot.anchorShift, c11n_constants.DEFAULT_DECAL_ANCHOR_SHIFT)
    elif slot.type == 'fixedProjectionDecal':
        slotDS.write('itemId', slot.itemId)
        slotDS.write('options', slot.options)


def writeAnchorSlots(slotDS, slot):
    slotDS.deleteSection('tags')
    if slot.anchorPosition is not None:
        slotDS.write('anchorPosition', slot.anchorPosition)
    if slot.anchorDirection is not None:
        slotDS.write('anchorDirection', slot.anchorDirection)
    if slot.applyTo is not None:
        slotDS.write('applyTo', slot.applyTo)
    return


def writeEmblemSlots(slotDS, slot):
    if slot.type not in ('attachment', 'sequence', 'paint', 'camouflage', 'style', 'effect', 'projectionDecal', 'fixedProjectionDecal'):
        _xml.rewriteBool(slotDS, 'isMirrored', slot.isMirrored, False)
        slotDS.writeVector3('rayStart', slot.rayStart)
        slotDS.writeVector3('rayEnd', slot.rayEnd)
        slotDS.writeVector3('rayUp', slot.rayUp)
    if slot.type in ('fixedEmblem', 'fixedInscription'):
        slotDS.write('emblemId', slot.emblemId)
    if slot.type == 'insigniaOnGun':
        _xml.rewriteBool(slotDS, 'applyToFabric', slot.applyToFabric, True)
        _xml.rewriteString(slotDS, 'compatibleModels', ' '.join(slot.compatibleModels), '')
    slotDS.write('size', slot.size)
    _xml.rewriteBool(slotDS, 'hideIfDamaged', slot.hideIfDamaged, False)
    _xml.rewriteBool(slotDS, 'isUVProportional', slot.isUVProportional, True)


def writeMiscSlots(slotDS, slot):
    slotDS.write('position', slot.position)
    slotDS.write('rotation', slot.rotation)
    _xml.rewriteString(slotDS, 'attachNode', slot.attachNode, '')


def writeCustomizationSlots(slots, section, subsectionName):
    section.deleteSection(subsectionName)
    if not slots:
        return
    subsection = section.insertSection(subsectionName, section.getFirstIndex('customization'))
    slots.sort(key=lambda x: x.slotId)
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
    _xml.rewriteFloat(section, 'sensitivityToImpulse', item.sensitivityToImpulse)
    _xml.rewriteTupleOfFloats(section, 'pitchParams', item.pitchParams)
    _xml.rewriteTupleOfFloats(section, 'rollParams', item.rollParams)


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
