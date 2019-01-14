# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/shared_readers.py
import ResMgr
from constants import IS_CLIENT, IS_BOT
from debug_utils import LOG_ERROR
from items import _xml
from items.components import component_constants
from items.components import shared_components
from items.components import c11n_constants
_ALLOWED_EMBLEM_SLOTS = component_constants.ALLOWED_EMBLEM_SLOTS
_ALLOWED_SLOTS_ANCHORS = component_constants.ALLOWED_SLOTS_ANCHORS

def _readEmblemSlot(ctx, subsection, slotType):
    slotId = _xml.readInt(ctx, subsection, 'slotId')
    _verifySlotId(ctx, slotType, slotId)
    descr = shared_components.EmblemSlot(_xml.readVector3(ctx, subsection, 'rayStart'), _xml.readVector3(ctx, subsection, 'rayEnd'), _xml.readVector3(ctx, subsection, 'rayUp'), _xml.readPositiveFloat(ctx, subsection, 'size'), subsection.readBool('hideIfDamaged', False), slotType, subsection.readBool('isMirrored', False), subsection.readBool('isUVProportional', True), _xml.readIntOrNone(ctx, subsection, 'emblemId'), slotId, subsection.readBool('applyToFabric', True))
    return descr


def _readCustomizationSlot(ctx, subsection, slotType):
    applyTo = _xml.readIntOrNone(ctx, subsection, 'applyTo')
    if applyTo is not None:
        if applyTo not in c11n_constants.ApplyArea.RANGE:
            _xml.raiseWrongSection(ctx, 'applyTo')
    showOn = _xml.readIntOrNone(ctx, subsection, 'showOn')
    if showOn is not None:
        availableShowOnRegions = c11n_constants.ApplyArea.HULL | c11n_constants.ApplyArea.TURRET | c11n_constants.ApplyArea.GUN
        if showOn | availableShowOnRegions != availableShowOnRegions:
            _xml.raiseWrongSection(ctx, 'showOn')
    availableTags = c11n_constants.ProjectionDecalDirectionTags.ALL + c11n_constants.ProjectionDecalFormTags.ALL + c11n_constants.ProjectionDecalPositionTags.ALL
    tags = readOrderedTagsOrEmpty(ctx, subsection, availableTags)
    slotId = _xml.readInt(ctx, subsection, 'slotId')
    parentSlotId = _xml.readIntOrNone(ctx, subsection, 'parentSlotId')
    if slotType == 'projectionDecal' and parentSlotId is None:
        formTags = [ tag for tag in tags if tag in c11n_constants.ProjectionDecalFormTags.ALL ]
        if formTags and formTags != [c11n_constants.ProjectionDecalFormTags.ANY]:
            _xml.raiseWrongXml(ctx, 'tags', 'wrong formfactor for slot ID%i' % slotId)
    slotId = _xml.readInt(ctx, subsection, 'slotId')
    _verifySlotId(ctx, slotType, slotId)
    descr = shared_components.CustomizationSlotDescription(type=slotType, anchorPosition=_xml.readVector3(ctx, subsection, 'anchorPosition'), anchorDirection=_xml.readVector3(ctx, subsection, 'anchorDirection'), applyTo=applyTo, slotId=slotId, position=_xml.readVector3OrNone(ctx, subsection, 'position'), rotation=_xml.readVector3OrNone(ctx, subsection, 'rotation'), scale=_xml.readVector3OrNone(ctx, subsection, 'scale'), scaleFactors=_xml.readVector3OrNone(ctx, subsection, 'scaleFactors'), doubleSided=_xml.readBool(ctx, subsection, 'doubleSided', False), showOn=showOn, tags=tags, parentSlotId=parentSlotId, clipAngle=_xml.readFloat(ctx, subsection, 'clipAngle', 0.0))
    return descr


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
    minSlotId, maxSlotId = c11n_constants.customizationSlotIds[tankArea][slotType]
    if not minSlotId <= slotId <= maxSlotId:
        xmlContext, fileName = ctx
        while xmlContext is not None:
            xmlContext, fileName = xmlContext

        LOG_ERROR('Wrong customization slot ID{} for {}'.format(slotId, fileName))
    return


def readTags(xmlCtx, section, allowedTagNames, subsectionName='tags'):
    tagNames = _xml.readString(xmlCtx, section, subsectionName).split()
    res = set()
    for tagName in tagNames:
        if tagName not in allowedTagNames:
            _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
        res.add(intern(tagName))

    return frozenset(res)


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


def readOrderedTagsOrEmpty(xmlCtx, section, allowedTagNames, subsectionName='tags'):
    tags = _xml.readStringOrNone(xmlCtx, section, subsectionName)
    res = []
    if tags is not None:
        tagNames = tags.split()
        for tagName in tagNames:
            if tagName not in allowedTagNames:
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
        elif slotType in component_constants.ALLOWED_SLOTS_ANCHORS:
            descr = _readCustomizationSlot(ctx, subsection, slotType)
            anchors.append(descr)
        else:
            _xml.raiseWrongXml(xmlCtx, 'customizationSlots/{}/{}'.format(sname, slotType), 'expected value is {}'.format(_ALLOWED_EMBLEM_SLOTS + _ALLOWED_SLOTS_ANCHORS))
        if descr is not None and descr.slotId not in slotIDs:
            slotIDs.add(descr.slotId)
        xmlContext, fileName = xmlCtx
        while xmlContext is not None:
            xmlContext, fileName = xmlContext

        LOG_ERROR('Repeated customization slot ID{} for {}'.format(descr.slotId, fileName))

    return (tuple(slots), tuple(anchors))


def readEmblemSlots(xmlCtx, section, subsectionName):
    slots = []
    for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        if sname not in component_constants.ALLOWED_EMBLEM_SLOTS:
            _xml.raiseWrongXml(xmlCtx, 'emblemSlots/{}'.format(sname), 'expected {}'.format(_ALLOWED_EMBLEM_SLOTS))
        ctx = (xmlCtx, 'emblemSlots/{}'.format(sname))
        descr = shared_components.EmblemSlot(_xml.readVector3(ctx, subsection, 'rayStart'), _xml.readVector3(ctx, subsection, 'rayEnd'), _xml.readVector3(ctx, subsection, 'rayUp'), _xml.readPositiveFloat(ctx, subsection, 'size'), subsection.readBool('hideIfDamaged', False), _ALLOWED_EMBLEM_SLOTS[_ALLOWED_EMBLEM_SLOTS.index(sname)], subsection.readBool('isMirrored', False), subsection.readBool('isUVProportional', True), _xml.readIntOrNone(ctx, subsection, 'emblemId'))
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
    return component


def readCamouflage(xmlCtx, section, sectionName, default=None):
    tilingKey = sectionName + '/tiling'
    if default is None or section.has_key(tilingKey):
        tiling = _xml.readTupleOfFloats(xmlCtx, section, tilingKey, 4)
        if tiling[0] <= 0 or tiling[1] <= 0:
            if default is None:
                _xml.raiseWrongSection(xmlCtx, tilingKey)
            else:
                tiling = default[0]
    else:
        tiling = default[0]
    maskKey = sectionName + '/exclusionMask'
    mask = section.readString(maskKey)
    if not mask and default is not None:
        mask = default[1]
    return shared_components.Camouflage(tiling, mask)


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
