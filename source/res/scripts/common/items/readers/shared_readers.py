# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/shared_readers.py
import itertools
import logging
from collections import defaultdict
import typing
import ResMgr
from constants import IS_CLIENT, IS_BOT, ITEM_DEFS_PATH, IS_EDITOR, DeviceRepairMode
from items import _xml, getTypeInfoByName
from items.components import component_constants
from items.components import shared_components
from items.components import c11n_constants
_ALLOWED_EMBLEM_SLOTS = component_constants.ALLOWED_EMBLEM_SLOTS
_ALLOWED_SLOTS_ANCHORS = component_constants.ALLOWED_SLOTS_ANCHORS
_ALLOWED_MISC_SLOTS = component_constants.ALLOWED_MISC_SLOTS
_ALLOWED_PROJECTION_DECALS_ANCHORS = component_constants.ALLOWED_PROJECTION_DECALS_ANCHORS
_CUSTOMIZATION_CONSTANTS_PATH = ITEM_DEFS_PATH + '/customization/constants.xml'
_logger = logging.getLogger(__name__)

def _readEmblemSlot(ctx, subsection, slotType):
    descr = shared_components.EmblemSlot(_xml.readVector3(ctx, subsection, 'rayStart'), _xml.readVector3(ctx, subsection, 'rayEnd'), _xml.readVector3(ctx, subsection, 'rayUp'), _xml.readPositiveFloat(ctx, subsection, 'size'), subsection.readBool('hideIfDamaged', False), slotType, subsection.readBool('isMirrored', False), subsection.readBool('isUVProportional', True), _xml.readIntOrNone(ctx, subsection, 'emblemId'), _xml.readInt(ctx, subsection, 'slotId'), subsection.readBool('applyToFabric', True), _readCompatibleModels(subsection, ctx))
    _verifySlotId(ctx, slotType, descr.slotId)
    return descr


def _readMiscSlot(ctx, subsection, slotType):
    descr = shared_components.MiscSlot(type=slotType, slotId=_xml.readInt(ctx, subsection, 'slotId'), position=_xml.readVector3OrNone(ctx, subsection, 'position'), rotation=_xml.readVector3OrNone(ctx, subsection, 'rotation'), attachNode=_xml.readStringOrNone(ctx, subsection, 'attachNode'))
    _verifySlotId(ctx, slotType, descr.slotId)
    return descr


def _customizationSlotTagsValidator(tag):
    availableTags = c11n_constants.ProjectionDecalDirectionTags.ALL + c11n_constants.ProjectionDecalFormTags.ALL + c11n_constants.ProjectionDecalPreferredTags.ALL + c11n_constants.ProjectionDecalMatchingTags.ALL
    return tag in availableTags


def _readCustomizationSlot(ctx, subsection, slotType):
    descr = shared_components.CustomizationSlotDescription(slotType=slotType, anchorPosition=_xml.readVector3OrNone(ctx, subsection, 'anchorPosition'), anchorDirection=_xml.readVector3OrNone(ctx, subsection, 'anchorDirection'), applyTo=_xml.readIntOrNone(ctx, subsection, 'applyTo'), slotId=_xml.readInt(ctx, subsection, 'slotId'))
    if descr.applyTo is not None and descr.applyTo not in c11n_constants.ApplyArea.RANGE:
        _xml.raiseWrongSection(ctx, 'applyTo')
    return descr


def _readProjectionDecalSlot(ctx, subsection, slotType):
    descr = shared_components.ProjectionDecalSlotDescription(slotType=slotType, slotId=_xml.readInt(ctx, subsection, 'slotId'), position=_xml.readVector3OrNone(ctx, subsection, 'position'), rotation=_xml.readVector3OrNone(ctx, subsection, 'rotation'), scale=_xml.readVector3OrNone(ctx, subsection, 'scale'), scaleFactors=_xml.readVector3(ctx, subsection, 'scaleFactors', c11n_constants.DEFAULT_DECAL_SCALE_FACTORS), doubleSided=_xml.readBool(ctx, subsection, 'doubleSided', False), hiddenForUser=_xml.readBool(ctx, subsection, 'hiddenForUser', False), canBeMirroredVertically=_xml.readBool(ctx, subsection, 'verticalMirror', False), showOn=_xml.readIntOrNone(ctx, subsection, 'showOn'), tags=readOrderedTagsOrEmpty(ctx, subsection, _customizationSlotTagsValidator), clipAngle=_xml.readFloat(ctx, subsection, 'clipAngle', c11n_constants.DEFAULT_DECAL_CLIP_ANGLE), anchorShift=_xml.readFloat(ctx, subsection, 'anchorShift', c11n_constants.DEFAULT_DECAL_ANCHOR_SHIFT))
    _verifySlotId(ctx, slotType, descr.slotId)
    _verifyMatchingSlotSettings(ctx, descr)
    if descr.showOn is not None:
        availableShowOnRegions = c11n_constants.ApplyArea.HULL | c11n_constants.ApplyArea.TURRET | c11n_constants.ApplyArea.GUN
        if descr.showOn | availableShowOnRegions != availableShowOnRegions:
            _xml.raiseWrongSection(ctx, 'showOn')
    if subsection.has_key('compatibleModels'):
        descr.compatibleModels = _xml.readTupleOfStrings(ctx, subsection, 'compatibleModels')
    if subsection.has_key('itemId'):
        descr.itemId = _xml.readInt(ctx, subsection, 'itemId')
    if subsection.has_key('options'):
        descr.options = _xml.readNonNegativeInt(ctx, subsection, 'options')
    return descr


def _readCompatibleModels(subsection, ctx):
    compatibleModels = component_constants.EMPTY_TUPLE
    if IS_CLIENT:
        if subsection.has_key('compatibleModels'):
            compatibleModels = _xml.readTupleOfStrings(ctx, subsection, 'compatibleModels')
    return compatibleModels


__customizationSlotIdRanges = None

def __getInitedSlotIdRanges():
    global __customizationSlotIdRanges
    if __customizationSlotIdRanges is None:
        __customizationSlotIdRanges = defaultdict(dict)
        _readCustomizationSlotIdRanges()
    return __customizationSlotIdRanges


def getCustomizationSlotIdRanges():
    return __getInitedSlotIdRanges() if IS_EDITOR else None


def _readCustomizationSlotIdRanges():
    filePath = _CUSTOMIZATION_CONSTANTS_PATH
    section = ResMgr.openSection(filePath)
    if section is None:
        _xml.raiseWrongXml(None, filePath, 'can not open or read')
    xmlCtx = (None, filePath)
    slots = _xml.getSubsection(xmlCtx, section, 'slot_id_ranges')
    for partName, part in _xml.getChildren(xmlCtx, section, 'slot_id_ranges'):
        partIds = __customizationSlotIdRanges[partName]
        for itemName, item in _xml.getChildren(xmlCtx, slots, partName):
            range_min = _xml.readInt(xmlCtx, item, 'range_min')
            range_max = _xml.readInt(xmlCtx, item, 'range_max')
            partIds[itemName] = (range_min, range_max)

    return


def _verifySlotId(ctx, slotType, slotId):
    tankPart = ctx[0][1]
    if tankPart == 'hull':
        tankArea = tankPart
    elif tankPart.startswith('gun'):
        tankArea = 'gun'
    elif tankPart.startswith('turret'):
        tankArea = 'turret'
    elif tankPart.startswith('chassis'):
        tankArea = 'chassis'
    else:
        return
    slotIdRanges = __getInitedSlotIdRanges()
    minSlotId, maxSlotId = slotIdRanges[tankArea][slotType]
    if not minSlotId <= slotId <= maxSlotId:
        xmlContext, fileName = ctx
        while xmlContext is not None:
            xmlContext, fileName = xmlContext

        _logger.error('Wrong customization slot ID%s for %s', slotId, fileName)
    return


def _verifyMatchingSlotSettings(xmlCtx, descr):

    def findTag(function, sequence):
        return next(itertools.ifilter(function, sequence), None)

    matchingTag = findTag(lambda tag: tag in c11n_constants.ProjectionDecalMatchingTags.ALL, descr.tags)
    if descr.hiddenForUser:
        if matchingTag is None:
            _xml.raiseWrongXml(xmlCtx, 'tags', 'matching tag for hidden slot is missed!')
    if matchingTag is not None:
        if not descr.hiddenForUser:
            _xml.raiseWrongXml(xmlCtx, 'hiddenForUser', 'slot:%s with matching tag must be hiddenForUser!' % descr.slotId)
        formFactorTag = findTag(lambda tag: tag in c11n_constants.ProjectionDecalFormTags.ALL, descr.tags)
        if formFactorTag is None:
            _xml.raiseWrongXml(xmlCtx, 'tags', 'slot:%s with matching tag must have form factor tag!' % descr.slotId)
        if matchingTag != c11n_constants.ProjectionDecalMatchingTags.COVER:
            directionTags = (c11n_constants.ProjectionDecalDirectionTags.LEFT, c11n_constants.ProjectionDecalDirectionTags.RIGHT, c11n_constants.ProjectionDecalDirectionTags.FRONT)
            directionTag = findTag(lambda tag: tag in directionTags, descr.tags)
            if directionTag is None:
                _xml.raiseWrongXml(xmlCtx, 'tags', 'slot:%s with matching tag must have direction tag!' % descr.slotId)
    return


def readTags(xmlCtx, section, allowedTagNames, subsectionName='tags'):
    tagNames = _xml.readString(xmlCtx, section, subsectionName).split()
    res = set()
    for tagName in tagNames:
        if tagName not in allowedTagNames:
            _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
        res.add(intern(tagName))

    return frozenset(res)


def readAllowedTags(xmlCtx, section, subsectionName, itemTypeName):
    allowedTagNames = getTypeInfoByName(itemTypeName)['tags']
    return readTags(xmlCtx, section, allowedTagNames, subsectionName)


def readTagsOrEmpty(xmlCtx, section, allowedTagNames, subsectionName='tags'):
    tags = _xml.readStringOrNone(xmlCtx, section, subsectionName)
    res = set()
    if tags is not None:
        tagNames = tags.split()
        for tagName in tagNames:
            if tagName not in allowedTagNames:
                _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
            res.add(intern(tagName))

    return frozenset(res)


def readOrderedTagsOrEmpty(xmlCtx, section, allowedTagValidator, subsectionName='tags'):
    tags = _xml.readStringOrNone(xmlCtx, section, subsectionName)
    res = []
    if tags is not None:
        tagNames = tags.split()
        for tagName in tagNames:
            if not allowedTagValidator(tagName):
                _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
            res.append(intern(tagName))

    return tuple(res)


def readCustomizationSlots(xmlCtx, section, subsectionName):
    slots = []
    anchors = []
    slot_tag_name = 'slot'
    slotIDs = set()
    for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        if sname != slot_tag_name:
            _xml.raiseWrongXml(xmlCtx, 'customizationSlots/{}'.format(sname), 'expected {}'.format(slot_tag_name))
        ctx = (xmlCtx, 'customizationSlots/{}'.format(sname))
        slotType = _xml.readString(ctx, subsection, 'slotType')
        descr = None
        if slotType in component_constants.ALLOWED_EMBLEM_SLOTS:
            descr = _readEmblemSlot(ctx, subsection, slotType)
            slots.append(descr)
        elif slotType in component_constants.ALLOWED_PROJECTION_DECALS_ANCHORS:
            descr = _readProjectionDecalSlot(ctx, subsection, slotType)
            anchors.append(descr)
        elif slotType in component_constants.ALLOWED_SLOTS_ANCHORS:
            descr = _readCustomizationSlot(ctx, subsection, slotType)
            anchors.append(descr)
        elif slotType in component_constants.ALLOWED_MISC_SLOTS:
            descr = _readMiscSlot(ctx, subsection, slotType)
            anchors.append(descr)
        else:
            _xml.raiseWrongXml(xmlCtx, 'customizationSlots/{}/{}'.format(sname, slotType), 'expected value is {}'.format(_ALLOWED_EMBLEM_SLOTS + _ALLOWED_SLOTS_ANCHORS + _ALLOWED_MISC_SLOTS + _ALLOWED_PROJECTION_DECALS_ANCHORS))
        if descr is not None and descr.slotId not in slotIDs:
            slotIDs.add(descr.slotId)
        xmlContext, fileName = xmlCtx
        while xmlContext is not None:
            xmlContext, fileName = xmlContext

        _logger.error('Repeated customization slot ID%s for %s', descr.slotId, fileName)

    return (tuple(slots), tuple(anchors))


def readEmblemSlots(xmlCtx, section, subsectionName):
    slots = []
    for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        if sname not in component_constants.ALLOWED_EMBLEM_SLOTS:
            _xml.raiseWrongXml(xmlCtx, 'emblemSlots/{}'.format(sname), 'expected {}'.format(_ALLOWED_EMBLEM_SLOTS))
        ctx = (xmlCtx, 'emblemSlots/{}'.format(sname))
        descr = shared_components.EmblemSlot(_xml.readVector3(ctx, subsection, 'rayStart'), _xml.readVector3(ctx, subsection, 'rayEnd'), _xml.readVector3(ctx, subsection, 'rayUp'), _xml.readPositiveFloat(ctx, subsection, 'size'), subsection.readBool('hideIfDamaged', False), _ALLOWED_EMBLEM_SLOTS[_ALLOWED_EMBLEM_SLOTS.index(sname)], subsection.readBool('isMirrored', False), subsection.readBool('isUVProportional', True), _xml.readIntOrNone(ctx, subsection, 'emblemId'), _readCompatibleModels(subsection, ctx))
        slots.append(descr)

    return (tuple(slots), tuple())


def readLodDist(xmlCtx, section, subsectionName, cache):
    name = _xml.readNonEmptyString(xmlCtx, section, subsectionName)
    dist = cache.commonConfig['lodLevels'].get(name)
    if dist is None:
        _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown lod level '%s'" % name)
    return dist


def readLodSettings(xmlCtx, section, cache):
    return shared_components.LodSettings(maxLodDistance=readLodDist(xmlCtx, section, 'lodSettings/maxLodDistance', cache), maxPriority=_xml.readIntOrNone(xmlCtx, section, 'lodSettings/maxPriority'))


def readSwingingSettings(xmlCtx, section, cache):
    return shared_components.SwingingSettings(readLodDist(xmlCtx, section, 'swinging/lodDist', cache), _xml.readNonNegativeFloat(xmlCtx, section, 'swinging/sensitivityToImpulse'), _xml.readTupleOfFloats(xmlCtx, section, 'swinging/pitchParams', 6), _xml.readTupleOfFloats(xmlCtx, section, 'swinging/rollParams', 7))


def readModelsSets(xmlCtx, section, subsectionName):
    undamaged = _xml.readNonEmptyString(xmlCtx, section, subsectionName + '/undamaged')
    destroyed = _xml.readNonEmptyString(xmlCtx, section, subsectionName + '/destroyed')
    exploded = _xml.readNonEmptyString(xmlCtx, section, subsectionName + '/exploded')
    modelsSets = {'default': shared_components.ModelStatesPaths(undamaged, destroyed, exploded)}
    subsection = section[subsectionName]
    if subsection:
        setSection = subsection['sets'] or {}
        for k, v in setSection.items():
            modelsSets[k] = shared_components.ModelStatesPaths(_xml.readStringOrNone(xmlCtx, v, 'undamaged') or undamaged, _xml.readStringOrNone(xmlCtx, v, 'destroyed') or destroyed, _xml.readStringOrNone(xmlCtx, v, 'exploded') or exploded)

    return modelsSets


def readUserText(section):
    return shared_components.I18nComponent(section.readString('userString'), section.readString('description'), section.readString('shortUserString'), section.readString('shortDescriptionSpecial'), section.readString('longDescriptionSpecial'))


def readDeviceHealthParams(xmlCtx, section, subsectionName='', withHysteresis=True):
    if subsectionName:
        section = _xml.getSubsection(xmlCtx, section, subsectionName)
        xmlCtx = (xmlCtx, subsectionName)
    component = shared_components.DeviceHealth(_xml.readInt(xmlCtx, section, 'maxHealth', 1), _xml.readNonNegativeFloat(xmlCtx, section, 'repairCost'), _xml.readInt(xmlCtx, section, 'maxRegenHealth', 0))
    if component.maxRegenHealth > component.maxHealth:
        _xml.raiseWrongSection(xmlCtx, 'maxRegenHealth')
    if not IS_CLIENT and not IS_BOT:
        component.healthRegenPerSec = _xml.readNonNegativeFloat(xmlCtx, section, 'healthRegenPerSec')
        component.healthBurnPerSec = _xml.readNonNegativeFloat(xmlCtx, section, 'healthBurnPerSec')
        if section.has_key('chanceToHit'):
            component.chanceToHit = _xml.readFraction(xmlCtx, section, 'chanceToHit')
        else:
            component.chanceToHit = None
        if withHysteresis:
            hysteresisHealth = _xml.readInt(xmlCtx, section, 'hysteresisHealth', 0)
            if hysteresisHealth > component.maxRegenHealth:
                _xml.raiseWrongSection(xmlCtx, 'hysteresisHealth')
            component.hysteresisHealth = hysteresisHealth
        component.invulnerable = _xml.readBool(xmlCtx, section, 'invulnerable', False)
        component.repairSpeedLimiter = _readRepairSpeedLimiter(xmlCtx, section)
    if IS_CLIENT:
        if section.has_key('repairTime'):
            component.repairTime = _xml.readFloat(xmlCtx, section, 'repairTime')
    return component


def _readRepairSpeedLimiter(xmlCtx, section):
    if not section.has_key('repairSpeedLimiter'):
        return None
    else:
        ctx, subsection = _xml.getSubSectionWithContext(xmlCtx, section, 'repairSpeedLimiter')
        repairSpeedModifier = _xml.readNonNegativeFloat(ctx, subsection, 'repairSpeedModifier')
        return {'repairSpeedModifier': repairSpeedModifier,
         'speedToStartLimitedRepair': component_constants.KMH_TO_MS * _xml.readNonNegativeFloat(ctx, subsection, 'speedToStartLimitedRepair'),
         'speedToStopLimitedRepair': component_constants.KMH_TO_MS * _xml.readNonNegativeFloat(ctx, subsection, 'speedToStopLimitedRepair'),
         'repairMode': DeviceRepairMode.SLOWED if repairSpeedModifier > 0.0 else DeviceRepairMode.SUSPENDED}


def readCamouflage(xmlCtx, section, sectionName, default=None):
    tiling, mask, density, aoTextureSize = (None, None, None, None)
    tilingKey = sectionName + '/tiling'
    if section.has_key(tilingKey):
        readTiling = _xml.readTupleOfFloats(xmlCtx, section, tilingKey, 4)
        if readTiling[0] > 0 and readTiling[1] > 0:
            tiling = readTiling
    if tiling is None:
        if default is not None:
            tiling = default[0]
        else:
            _xml.raiseWrongSection(xmlCtx, tilingKey)
    maskKey = sectionName + '/exclusionMask'
    mask = section.readString(maskKey)
    if not mask and default is not None:
        mask = default[1]
    densityKey = sectionName + '/density'
    if section.has_key(densityKey):
        density = _xml.readTupleOfFloats(xmlCtx, section, densityKey, 2)
    if density is None and default is not None:
        density = default[2]
    aoTextureSizeKey = sectionName + '/aoTextureSize'
    if section.has_key(aoTextureSizeKey):
        aoTextureSize = _xml.readTupleOfFloats(xmlCtx, section, aoTextureSizeKey, 2)
    if aoTextureSize is None and default is not None:
        aoTextureSize = default[3]
    return shared_components.Camouflage(tiling, mask, density, aoTextureSize)


def readBuilder(xmlCtx, section, subsectionName, builderType):
    subsection = section[subsectionName]
    if subsection is not None:
        product = builderType(subsection)
        if product is not None:
            return product
        _xml.raiseWrongXml(xmlCtx, subsectionName, 'Failed builder {0} loading from {1}'.format(builderType, subsectionName))
    else:
        _xml.raiseWrongSection(xmlCtx, subsectionName)
    return


def readBuilders(xmlCtx, section, subsectionName, builderType):
    products = []
    for node in section.items():
        if node[0] == subsectionName:
            product = builderType(node[1])
            if product is not None:
                products.append(product)
            else:
                _xml.raiseWrongXml(xmlCtx, subsectionName, 'Failed builder {0} loading from {1}'.format(builderType, subsectionName))

    if not products:
        _xml.raiseWrongSection(xmlCtx, subsectionName)
    return products
