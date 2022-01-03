# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/customizations.py
from cStringIO import StringIO
from string import lower, upper
import base64
import copy
import varint
import ResMgr
import Math
from collections import namedtuple, OrderedDict, defaultdict
from soft_exception import SoftException
from items.components.c11n_constants import ApplyArea, SeasonType, Options, CustomizationType, CustomizationTypeNames, HIDDEN_CAMOUFLAGE_ID, MAX_USERS_PROJECTION_DECALS, CUSTOMIZATION_SLOTS_VEHICLE_PARTS, DEFAULT_SCALE_FACTOR_ID, EMPTY_ITEM_ID, DEFAULT_SCALE, DEFAULT_ROTATION, DEFAULT_POSITION, DEFAULT_DECAL_TINT_COLOR, ProjectionDecalMatchingTags
from items.components import c11n_components as cn
from constants import IS_CELLAPP, IS_BASEAPP, IS_EDITOR
from items import decodeEnum
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
import enum
from typing import List, Dict, Type, Tuple, Any, TypeVar, Optional, MutableMapping, TYPE_CHECKING
from wrapped_reflection_framework import ReflectionMetaclass
if TYPE_CHECKING:
    from items.vehicles import VehicleDescrType

class FieldTypes(object):
    VARINT = 2
    TAGS = 4
    OPTIONS_ENUM = 8
    FLOAT = 16
    APPLY_AREA_ENUM = 32
    TYPED_ARRAY = 64
    CUSTOM_TYPE_OFFSET = 128
    STRING = 512


@enum.unique
class FieldFlags(enum.IntEnum):
    NONE = 0
    DEPRECATED = 1
    WEAK_EQUAL_IGNORED = 2
    NON_XML = 4
    NON_BIN = 8
    NON_SERIALIZABLE = NON_XML | NON_BIN
    SAVE_AS_STRING = 16


class _C11nSerializationTypes(object):
    DEFAULT = 0
    PAINT = 1
    CAMOUFLAGE = 2
    DECAL = 3
    OUTFIT = 4
    INSIGNIA = 5
    PROJECTION_DECAL = 7
    PERSONAL_NUMBER = 8
    SEQUENCE = 9
    ATTACHMENT = 10


FieldType = namedtuple('FieldType', 'type default flags')

def arrayField(itemType, default=None, flags=FieldFlags.NONE):
    return FieldType(FieldTypes.TYPED_ARRAY | itemType, default or [], flags)


def intField(default=0, nonXml=False):
    return FieldType(FieldTypes.VARINT, default, FieldFlags.NON_XML if nonXml else FieldFlags.NONE)


def strField(default=''):
    return FieldType(FieldTypes.STRING, default, FieldFlags.NONE)


def xmlOnlyIntField(default=0):
    return FieldType(FieldTypes.VARINT, default, FieldFlags.NON_BIN)


def xmlOnlyFloatField(default=0):
    return FieldType(FieldTypes.FLOAT, default, FieldFlags.NON_BIN)


def xmlOnlyFloatArrayField(default=None):
    return FieldType(FieldTypes.TYPED_ARRAY | FieldTypes.FLOAT, default or [], FieldFlags.NON_BIN)


def applyAreaEnumField(default=0):
    return FieldType(FieldTypes.APPLY_AREA_ENUM, default, FieldFlags.WEAK_EQUAL_IGNORED)


def xmlOnlyApplyAreaEnumField(default=0, flags=FieldFlags.NONE):
    return FieldType(FieldTypes.APPLY_AREA_ENUM, default, FieldFlags.WEAK_EQUAL_IGNORED | FieldFlags.NON_BIN | flags)


def xmlOnlyTagsField(default=()):
    return FieldType(FieldTypes.TAGS, default, FieldFlags.WEAK_EQUAL_IGNORED | FieldFlags.NON_BIN)


def optionsEnumField(default=0):
    return FieldType(FieldTypes.OPTIONS_ENUM, default, FieldFlags.NONE)


def customFieldType(customType):
    return FieldType(FieldTypes.CUSTOM_TYPE_OFFSET * customType, None, FieldFlags.NONE)


def intArrayField(default=None, flags=FieldFlags.NONE):
    return arrayField(FieldTypes.VARINT, default or [], flags)


def customArrayField(customType, default=None):
    return arrayField(FieldTypes.CUSTOM_TYPE_OFFSET * customType, default)


class SerializationException(SoftException):
    pass


class FoundItemException(SoftException):
    pass


class SerializableComponent(object):
    fields = OrderedDict()
    __slots__ = ()
    customType = _C11nSerializationTypes.DEFAULT
    preview = False

    def __eq(self, o, ignoreFlags):
        if self.__class__ != o.__class__:
            return False
        for fname, ftype in self.fields.iteritems():
            if ftype.flags & ignoreFlags:
                continue
            v1 = getattr(self, fname)
            v2 = getattr(o, fname)
            if ftype.type & FieldTypes.TYPED_ARRAY:
                v1 = set(v1)
                v2 = set(v2)
            if v1 != v2:
                return False

        return True

    def __eq__(self, o):
        return self.__eq(o, FieldFlags.DEPRECATED)

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        result = 17
        for name, ftype in self.fields.iteritems():
            if ftype.flags & FieldFlags.DEPRECATED:
                continue
            v1 = getattr(self, name)
            if isinstance(v1, list):
                v1 = tuple(v1)
            if isinstance(v1, Math.Vector2) or isinstance(v1, Math.Vector3) or isinstance(v1, Math.Vector4):
                v1 = tuple(v1)
            result = (result * 31 + hash(v1)) % 18446744073709551616L

        return result

    def __repr__(self):
        buf = StringIO()
        self.__writeStr(buf)
        return buf.getvalue()

    def weak_eq(self, o):
        return self.__eq(o, FieldFlags.DEPRECATED | FieldFlags.WEAK_EQUAL_IGNORED)

    def copy(self):
        o = self.__class__()
        for fname in self.fields.iterkeys():
            setattr(o, fname, getattr(self, fname))

        return o

    def isFilled(self):
        return True

    def __writeStr(self, stream):
        stream.write('{')
        i = 0
        n = len(self.fields)
        for name, fieldInfo in self.fields.iteritems():
            if fieldInfo.flags & FieldFlags.DEPRECATED:
                continue
            v = getattr(self, name)
            stream.write('%s: %s' % (name, repr(v)))
            i += 1
            if i != n:
                stream.write(', ')

        stream.write('}')


class ComponentBinSerializer(object):

    def __init__(self):
        super(ComponentBinSerializer, self).__init__()

    def serialize(self, target):
        a = varint.encode(target.customType)
        b = self.__serializeCustomType(target)
        return a + b

    def __serializeCustomType(self, obj):
        hasValue = 0
        offset = 1
        result = ['\x00']
        for fieldName, fieldInfo in obj.fields.iteritems():
            if fieldInfo.flags & FieldFlags.DEPRECATED:
                offset <<= 1
                continue
            if fieldInfo.flags & FieldFlags.NON_BIN:
                continue
            value = getattr(obj, fieldName)
            if value != fieldInfo.default:
                hasValue |= offset
                result.append(self.__serialize(value, fieldInfo.type))
            offset <<= 1

        result[0] = varint.encode(hasValue)
        return ''.join(result)

    def __serializeArray(self, value, itemType):
        result = [ self.__serialize(item, itemType) for item in value ]
        return varint.encode(len(value)) + ''.join(result)

    def __serializeString(self, value):
        return varint.encode(len(value)) + value

    def __serialize(self, value, itemType):
        if itemType == FieldTypes.VARINT:
            return varint.encode(value)
        if itemType == FieldTypes.STRING:
            return self.__serializeString(value)
        if itemType == FieldTypes.APPLY_AREA_ENUM:
            return varint.encode(value)
        if itemType == FieldTypes.OPTIONS_ENUM:
            return varint.encode(value)
        if itemType & FieldTypes.TYPED_ARRAY:
            return self.__serializeArray(value, itemType ^ FieldTypes.TYPED_ARRAY)
        if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
            return self.__serializeCustomType(value)
        raise SerializationException('Unsupported field type %d' % (itemType,))


class ComponentBinDeserializer(object):

    def __init__(self, customTypes):
        self.__stream = None
        self.customTypes = customTypes
        super(ComponentBinDeserializer, self).__init__()
        return

    def decode(self, data):
        self.__stream = StringIO(data)
        try:
            code = varint.decode_stream(self.__stream)
            obj = self.__decodeCustomType(code)
        except EOFError:
            raise SerializationException('Cannot parse given stream')

        return obj

    def hasItem(self, data, path, value):
        self.__stream = StringIO(data)
        try:
            code = varint.decode_stream(self.__stream)
            self.__decodeCustomType(code, path, value)
        except EOFError:
            raise SerializationException('Cannot parse given stream')
        except FoundItemException:
            return True

        return False

    def __decodeCustomType(self, itemType, path=None, wanted=None):
        cls = self.customTypes.get(itemType, None)
        if wanted is None:
            obj = cls()
        else:
            obj = None
        fields = cls.fields
        io = self.__stream
        valueMap = varint.decode_stream(io)
        offset = 1
        for k, t in fields.iteritems():
            if t.flags & FieldFlags.NON_BIN:
                continue
            next = None if not path or path[0] != k else path[1]
            if valueMap & offset:
                ftype = t.type
                if ftype == FieldTypes.VARINT:
                    value = varint.decode_stream(io)
                elif ftype == FieldTypes.STRING:
                    value = self.__decodeString()
                elif ftype == FieldTypes.APPLY_AREA_ENUM:
                    value = varint.decode_stream(io)
                elif ftype == FieldTypes.OPTIONS_ENUM:
                    value = varint.decode_stream(io)
                elif ftype & FieldTypes.TYPED_ARRAY:
                    value = self.__decodeArray(ftype ^ FieldTypes.TYPED_ARRAY, k, path, next, wanted)
                elif ftype >= FieldTypes.CUSTOM_TYPE_OFFSET:
                    value = self.__decodeCustomType(ftype / FieldTypes.CUSTOM_TYPE_OFFSET, next, wanted)
                else:
                    raise SerializationException('Unsupported field type index')
                if not t.flags & FieldFlags.DEPRECATED or hasattr(obj, k) or obj is None:
                    if wanted is None:
                        setattr(obj, k, value)
                    elif path and path[1] is None and path[0] == k and value == wanted:
                        raise FoundItemException()
            offset <<= 1

        return obj

    def __decodeArray(self, itemType, k, path, next, wanted):
        io = self.__stream
        n = varint.decode_stream(io)
        if itemType == FieldTypes.VARINT:
            array = [ varint.decode_stream(io) for _ in xrange(n) ]
            if path and path[1] is None and path[0] == k and wanted in array:
                raise FoundItemException()
            return array
        elif itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
            customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
            return [ self.__decodeCustomType(customType, next, wanted) for _ in xrange(n) ]
        else:
            raise SerializationException('Unsupported item type')
            return

    def __decodeString(self):
        stream = self.__stream
        return stream.read(varint.decode_stream(stream))


class ComponentXmlDeserializer(object):
    __slots__ = ('customTypes',)

    def __init__(self, customTypes):
        self.customTypes = customTypes
        super(ComponentXmlDeserializer, self).__init__()

    def decode(self, itemType, xmlCtx, section):
        obj = self.__decodeCustomType(itemType, xmlCtx, section)
        return obj

    def __decodeCustomType(self, customType, ctx, section):
        cls = self.customTypes[customType]
        instance = cls()
        for fname, finfo in cls.fields.iteritems():
            if finfo.flags & FieldFlags.NON_XML:
                continue
            if not section.has_key(fname):
                continue
            ftype = finfo.type
            if ftype == FieldTypes.VARINT:
                value = section.readInt(fname)
            elif ftype == FieldTypes.FLOAT:
                value = section.readFloat(fname)
            elif ftype == FieldTypes.APPLY_AREA_ENUM:
                value = self.__decodeEnum(section.readString(fname), ApplyArea)
            elif ftype == FieldTypes.TAGS:
                value = tuple(section.readString(fname).split())
            elif ftype == FieldTypes.STRING:
                value = section.readString(fname)
            elif ftype == FieldTypes.OPTIONS_ENUM:
                value = self.__decodeEnum(section.readString(fname), Options)
            elif ftype & FieldTypes.TYPED_ARRAY:
                itemType = ftype ^ FieldTypes.TYPED_ARRAY
                value = self.__decodeArray(itemType, (ctx, fname), section[fname])
            elif ftype >= FieldTypes.CUSTOM_TYPE_OFFSET:
                ftype = ftype / FieldTypes.CUSTOM_TYPE_OFFSET
                value = self.__decodeCustomType(ftype, (ctx, fname), section[fname])
            else:
                raise SerializationException('Unsupported item type')
            if not finfo.flags & FieldFlags.DEPRECATED or hasattr(instance, fname):
                setattr(instance, fname, value)

        return instance

    def __decodeArray(self, itemType, ctx, section):
        result = []
        for i, (iname, isection) in enumerate(section.items()):
            if itemType == FieldTypes.VARINT:
                result.append(isection.asInt)
            if itemType == FieldTypes.FLOAT:
                result.append(isection.asFloat)
            if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
                customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
                ictx = (ctx, '{0} {1}'.format(iname, isection))
                result.append(self.__decodeCustomType(customType, ictx, isection))
            raise SerializationException('Unsupported item type')

        return result

    def __decodeEnum(self, value, enum):
        return decodeEnum(value, enum)[0]


class EmptyComponent(SerializableComponent):
    pass


class PaintComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.PAINT
    fields = OrderedDict((('id', intField()), ('appliedTo', applyAreaEnumField(ApplyArea.PAINT_REGIONS_VALUE))))
    __slots__ = ('id', 'appliedTo')

    def __init__(self, id=0, appliedTo=ApplyArea.PAINT_REGIONS_VALUE):
        self.id = id
        self.appliedTo = appliedTo
        super(PaintComponent, self).__init__()

    def toDict(self):
        at = self.appliedTo
        p = self.id
        return {i:p for i in ApplyArea.RANGE if i & at}


class CamouflageComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.CAMOUFLAGE
    fields = OrderedDict((('id', intField()),
     ('patternSize', intField(1)),
     ('appliedTo', applyAreaEnumField(ApplyArea.CAMOUFLAGE_REGIONS_VALUE)),
     ('palette', intField())))
    __slots__ = ('id', 'patternSize', 'appliedTo', 'palette')

    def __init__(self, id=0, patternSize=1, appliedTo=ApplyArea.CAMOUFLAGE_REGIONS_VALUE, palette=0):
        self.id = id
        self.patternSize = patternSize
        self.appliedTo = appliedTo
        self.palette = palette
        super(CamouflageComponent, self).__init__()


class DecalComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.DECAL
    fields = OrderedDict((('id', intField()), ('appliedTo', applyAreaEnumField(ApplyArea.NONE)), ('progressionLevel', intField(0))))
    __slots__ = ('id', 'appliedTo', 'progressionLevel')

    def __init__(self, id=0, appliedTo=ApplyArea.NONE, progressionLevel=0):
        self.id = id
        self.appliedTo = appliedTo
        self.progressionLevel = progressionLevel
        super(DecalComponent, self).__init__()


class InsigniaComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.INSIGNIA
    fields = OrderedDict((('id', xmlOnlyIntField()), ('appliedTo', xmlOnlyApplyAreaEnumField(ApplyArea.NONE))))
    __slots__ = ('id', 'appliedTo')

    def __init__(self, id=0, appliedTo=ApplyArea.NONE):
        self.id = id
        self.appliedTo = appliedTo
        super(InsigniaComponent, self).__init__()


class ProjectionDecalComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.PROJECTION_DECAL
    fields = OrderedDict((('id', intField()),
     ('options', optionsEnumField(Options.NONE)),
     ('slotId', intField(0)),
     ('scaleFactorId', intField(DEFAULT_SCALE_FACTOR_ID)),
     ('showOn', xmlOnlyApplyAreaEnumField(ApplyArea.NONE, FieldFlags.SAVE_AS_STRING)),
     ('scale', xmlOnlyFloatArrayField()),
     ('rotation', xmlOnlyFloatArrayField()),
     ('position', xmlOnlyFloatArrayField()),
     ('tintColor', intArrayField(flags=FieldFlags.NON_BIN if not IS_EDITOR else FieldFlags.NONE)),
     ('doubleSided', xmlOnlyIntField(0)),
     ('tags', xmlOnlyTagsField(())),
     ('preview', xmlOnlyIntField(0)),
     ('progressionLevel', intField(0))))
    __slots__ = ('id', 'options', 'slotId', 'scaleFactorId', 'showOn', 'scale', 'rotation', 'position', 'tintColor', 'doubleSided', 'tags', 'preview', 'progressionLevel')

    def __init__(self, id=0, options=Options.NONE, slotId=0, scaleFactorId=DEFAULT_SCALE_FACTOR_ID, showOn=ApplyArea.NONE, scale=DEFAULT_SCALE, rotation=DEFAULT_ROTATION, position=DEFAULT_POSITION, tintColor=DEFAULT_DECAL_TINT_COLOR, doubleSided=0, tags=None, preview=False, progressionLevel=0):
        self.id = id
        self.options = options
        self.slotId = slotId
        self.scaleFactorId = scaleFactorId
        self.showOn = showOn
        self.scale = scale
        self.rotation = rotation
        self.position = position
        self.tintColor = tintColor
        self.doubleSided = doubleSided
        self.tags = tags
        self.preview = preview
        self.progressionLevel = progressionLevel
        super(ProjectionDecalComponent, self).__init__()

    def __str__(self):
        return 'ProjectionDecalComponent(id={0}, options={1}, slotId={2}, scaleFactorId={3}, showOn={4}, scale={5}, rotation={6}, position={7}, tintColor={8}, doubleSided={9}, preview={10}, progressionLevel={11})'.format(self.id, self.options, self.slotId, self.scaleFactorId, self.showOn, self.scale, self.rotation, self.position, self.tintColor, self.doubleSided, self.preview, self.progressionLevel)

    def isMirroredHorizontally(self):
        return self.options & Options.MIRRORED_HORIZONTALLY

    def isMirroredVertically(self):
        return self.options & Options.MIRRORED_VERTICALLY

    def isFilled(self):
        return (any(self.position) or bool(self.slotId)) and not self.preview

    @property
    def matchingTag(self):
        if self.tags:
            for tag in self.tags:
                if tag in ProjectionDecalMatchingTags.ALL:
                    return tag

        return None


class PersonalNumberComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.PERSONAL_NUMBER
    fields = OrderedDict((('id', intField()), ('number', strField()), ('appliedTo', applyAreaEnumField(ApplyArea.NONE))))
    __slots__ = ('id', 'number', 'appliedTo')

    def __init__(self, id=0, number=None, appliedTo=ApplyArea.NONE):
        self.id = id
        self.number = number or ''
        self.appliedTo = appliedTo
        super(PersonalNumberComponent, self).__init__()

    def isFilled(self):
        return bool(self.number)


class SequenceComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.SEQUENCE
    if IS_EDITOR:
        slotIdFieldType = intField()
    else:
        slotIdFieldType = xmlOnlyIntField(0)
    fields = OrderedDict((('id', intField()),
     ('slotId', slotIdFieldType),
     ('position', xmlOnlyFloatArrayField()),
     ('rotation', xmlOnlyFloatArrayField())))
    __slots__ = ('id', 'slotId', 'position', 'rotation')

    def __init__(self, id=0, slotId=0, position=None, rotation=None):
        self.id = id
        self.slotId = slotId
        self.position = position or [0, 0, 0]
        self.rotation = rotation or [0, 0, 0]
        super(SequenceComponent, self).__init__()


class AttachmentComponent(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.ATTACHMENT
    if IS_EDITOR:
        slotIdFieldType = intField()
    else:
        slotIdFieldType = xmlOnlyIntField(0)
    fields = OrderedDict((('id', intField()),
     ('slotId', slotIdFieldType),
     ('position', xmlOnlyFloatArrayField()),
     ('rotation', xmlOnlyFloatArrayField())))
    __slots__ = ('id', 'slotId', 'position', 'rotation')

    def __init__(self, id=0, slotId=0, position=None, rotation=None):
        self.id = id
        self.slotId = slotId
        self.position = position or [0, 0, 0]
        self.rotation = rotation or [0, 0, 0]
        super(AttachmentComponent, self).__init__()


class CustomizationOutfit(SerializableComponent):
    __metaclass__ = ReflectionMetaclass
    customType = _C11nSerializationTypes.OUTFIT
    fields = OrderedDict((('modifications', intArrayField()),
     ('paints', customArrayField(PaintComponent.customType)),
     ('camouflages', customArrayField(CamouflageComponent.customType)),
     ('decals', customArrayField(DecalComponent.customType)),
     ('styleId', intField(nonXml=True)),
     ('projection_decals', customArrayField(ProjectionDecalComponent.customType)),
     ('insignias', customArrayField(InsigniaComponent.customType)),
     ('personal_numbers', customArrayField(PersonalNumberComponent.customType)),
     ('sequences', customArrayField(SequenceComponent.customType)),
     ('attachments', customArrayField(AttachmentComponent.customType)),
     ('styleProgressionLevel', intField())))
    __slots__ = ('modifications', 'paints', 'camouflages', 'decals', 'styleId', 'projection_decals', 'insignias', 'personal_numbers', 'sequences', 'attachments', 'styleProgressionLevel')

    def __init__(self, modifications=None, paints=None, camouflages=None, decals=None, projection_decals=None, personal_numbers=None, styleId=0, insignias=None, sequences=None, attachments=None, styleProgressionLevel=0):
        self.modifications = modifications or []
        self.paints = paints or []
        self.camouflages = camouflages or []
        self.decals = decals or []
        self.styleId = styleId or 0
        self.insignias = insignias or []
        self.projection_decals = projection_decals or []
        self.personal_numbers = personal_numbers or []
        self.sequences = sequences or []
        self.attachments = attachments or []
        self.styleProgressionLevel = styleProgressionLevel or 0
        super(CustomizationOutfit, self).__init__()

    def __nonzero__(self):
        for v in getattr(type(self), '__slots__'):
            if getattr(self, v):
                return True

        return False

    def getInvisibilityCamouflageId(self):
        for ce in self.camouflages:
            if ce.appliedTo & ApplyArea.HULL:
                return ce.id

        return None

    def makeCompDescr(self):
        if not self:
            return ''
        for typeId in CustomizationType.APPLIED_TO_TYPES:
            componentsAttrName = '{}s'.format(lower(CustomizationTypeNames[typeId]))
            components = CustomizationOutfit.applyAreaBitmaskToDict(getattr(self, componentsAttrName))
            setattr(self, componentsAttrName, CustomizationOutfit.shrinkAreaBitmask(components))

        return makeCompDescr(self)

    @property
    def empty(self):
        return not self

    @staticmethod
    def applyAreaBitmaskToDict(components):
        res = {}
        for c in components:
            i = 1
            while i <= c.appliedTo:
                if c.appliedTo & i:
                    cpy = c.copy()
                    cpy.appliedTo = 0
                    res.setdefault(i, []).append(cpy)
                i *= 2

        return res

    @staticmethod
    def slotIdToDict(components):
        res = {}
        for c in components:
            cpy = c.copy()
            slotId = cpy.slotId
            cpy.slotId = 0
            res.setdefault(slotId, []).append(cpy)

        return res

    @staticmethod
    def shrinkAreaBitmask(components):
        grouped = {}
        for at, lst in components.iteritems():
            for i in lst:
                grouped.setdefault(i, []).append(at)

        res = []
        for item, group in grouped.iteritems():
            curItem = item.copy()
            curItem.appliedTo = reduce(int.__or__, group, 0)
            res.append(curItem)

        return res

    def applyDiff(self, outfit):
        resultOutfit = self.copy()
        resultOutfit.styleProgressionLevel = outfit.styleProgressionLevel
        for itemType in CustomizationType.RANGE:
            typeName = lower(CustomizationTypeNames[itemType])
            componentsAttrName = '{}s'.format(typeName)
            if componentsAttrName not in self.__slots__:
                continue
            modifiedComponents = getattr(outfit, componentsAttrName, None)
            baseComponents = getattr(resultOutfit, componentsAttrName, None)
            components = []
            if itemType == CustomizationType.MODIFICATION:
                if EMPTY_ITEM_ID not in modifiedComponents:
                    components = modifiedComponents or baseComponents
            else:
                isAppliedTo = itemType in CustomizationType.APPLIED_TO_TYPES
                toDict = self.applyAreaBitmaskToDict if isAppliedTo else self.slotIdToDict
                modifiedComponents = toDict(modifiedComponents)
                baseComponents = toDict(baseComponents)
                modifiedRegions = set(modifiedComponents)
                baseRegions = set(baseComponents)
                for region in baseRegions - modifiedRegions:
                    for component in baseComponents[region]:
                        component = component.copy()
                        _setComponentsRegion(component, region)
                        components.append(component)

                for region in modifiedRegions - baseRegions:
                    for component in modifiedComponents[region]:
                        component = component.copy()
                        _setComponentsRegion(component, region)
                        components.append(component)

                for region in modifiedRegions & baseRegions:
                    for component in modifiedComponents[region]:
                        component = component.copy()
                        if component.id != EMPTY_ITEM_ID:
                            _setComponentsRegion(component, region)
                            components.append(component)

                if isAppliedTo:
                    components = self.applyAreaBitmaskToDict(components)
                    components = self.shrinkAreaBitmask(components)
            setattr(resultOutfit, componentsAttrName, components)

        return resultOutfit

    def getDiff(self, outfit):
        resultOutfit = self.copy()
        for itemType in CustomizationType.FULL_RANGE:
            typeName = lower(CustomizationTypeNames[itemType])
            componentsAttrName = '{}s'.format(typeName)
            if componentsAttrName not in self.__slots__:
                continue
            modifiedComponents = getattr(resultOutfit, componentsAttrName, None)
            baseComponents = getattr(outfit, componentsAttrName, None)
            components = []
            if itemType == CustomizationType.MODIFICATION:
                if modifiedComponents != baseComponents:
                    components = modifiedComponents or [EMPTY_ITEM_ID]
            else:
                isAppliedTo = itemType in CustomizationType.APPLIED_TO_TYPES
                toDict = self.applyAreaBitmaskToDict if isAppliedTo else self.slotIdToDict
                modifiedComponents = toDict(modifiedComponents)
                baseComponents = toDict(baseComponents)
                modifiedRegions = set(modifiedComponents)
                baseRegions = set(baseComponents)
                for region in baseRegions - modifiedRegions:
                    component = baseComponents[region][0].copy()
                    if itemType == CustomizationType.PROJECTION_DECAL and component.matchingTag:
                        continue
                    component.id = EMPTY_ITEM_ID
                    _setComponentsRegion(component, region)
                    components.append(component)

            for region in modifiedRegions - baseRegions:
                component = modifiedComponents[region][0].copy()
                if itemType == CustomizationType.PROJECTION_DECAL and component.matchingTag:
                    continue
                _setComponentsRegion(component, region)
                components.append(component)

            for region in modifiedRegions & baseRegions:
                component = modifiedComponents[region][0].copy()
                if itemType == CustomizationType.PROJECTION_DECAL and component.matchingTag:
                    continue
                if component != baseComponents[region][0]:
                    _setComponentsRegion(component, region)
                    components.append(component)

            setattr(resultOutfit, componentsAttrName, components)

        return resultOutfit

    def dismountComponents(self, applyArea, dismountTypes=CustomizationType.DISMOUNT_TYPE):
        toMove = defaultdict(int)
        areas = [ i for i in ApplyArea.RANGE if i & applyArea ]
        for c11nType in dismountTypes:
            if c11nType is CustomizationType.STYLE:
                continue
            components = getattr(self, '{}s'.format(lower(CustomizationTypeNames[c11nType])))
            if c11nType in CustomizationType.APPLIED_TO_TYPES:
                for component in components:
                    for area in areas:
                        if component.appliedTo & area:
                            component.appliedTo &= ~area
                            if c11nType == CustomizationType.CAMOUFLAGE and component.id == HIDDEN_CAMOUFLAGE_ID:
                                continue
                            toMove[(c11nType, component.id)] += 1

                components[:] = [ c for c in components if c.appliedTo != 0 ]
            if c11nType == CustomizationType.PROJECTION_DECAL:
                for projectionDecal in self.projection_decals:
                    toMove[(CustomizationType.PROJECTION_DECAL, projectionDecal.id)] += 1

                self.projection_decals = []
            if c11nType == CustomizationType.MODIFICATION:
                for modification in self.modifications:
                    toMove[(CustomizationType.MODIFICATION, modification)] += 1

                self.modifications = []

        return dict(toMove)

    def dismountUnsuitableComponents(self, vehDescr, oldVehDescr):
        toMove = NamedVector()
        projectionDecals = self.projection_decals
        differPartNames = _getDifferVehiclePartNames(vehDescr, oldVehDescr)
        if differPartNames:
            newProjectionDecals = []
            for projectionDecal in projectionDecals:
                if not cn.getVehicleProjectionDecalSlotParams(oldVehDescr, projectionDecal.slotId, differPartNames):
                    newProjectionDecals.append(projectionDecal)
                    continue
                toMove[(CustomizationType.PROJECTION_DECAL, projectionDecal.id)] += 1

            if toMove:
                self.projection_decals = newProjectionDecals
        for regionValue, vehiclePart in ((ApplyArea.HULL_REGIONS_VALUE, vehDescr.hull),
         (ApplyArea.CHASSIS_REGIONS_VALUE, vehDescr.chassis),
         (ApplyArea.TURRET_REGIONS_VALUE, vehDescr.turret),
         (ApplyArea.GUN_REGIONS_VALUE, vehDescr.gun)):
            for componentName, (area, _) in vehiclePart.customizableVehicleAreas.iteritems():
                components = getattr(self, '{}s'.format(lower(componentName)))
                componentType = getattr(CustomizationType, upper(componentName))
                for component in components:
                    if componentType == CustomizationType.CAMOUFLAGE and component.id == HIDDEN_CAMOUFLAGE_ID:
                        continue
                    appliedTo = regionValue & component.appliedTo
                    if not appliedTo:
                        continue
                    dismountArea = appliedTo & ~(area & appliedTo)
                    if not dismountArea:
                        continue
                    toMove += self.dismountComponents(dismountArea, (componentType,))

        return dict(toMove)

    def countComponents(self, componentId, typeId):
        result = 0
        if typeId in CustomizationType.APPLIED_TO_TYPES:
            outfitComponents = getattr(self, '{}s'.format(lower(CustomizationTypeNames[typeId])))
            for component in outfitComponents:
                if componentId == component.id:
                    result += ApplyArea.getAppliedCount(component.appliedTo)

        elif typeId in CustomizationType.SIMPLE_TYPES:
            if typeId == CustomizationType.STYLE and self.styleId == componentId:
                result += 1
            elif typeId == CustomizationType.PROJECTION_DECAL:
                result += len([ component for component in self.projection_decals if componentId == component.id ])
            elif typeId == CustomizationType.PERSONAL_NUMBER:
                result += len([ component for component in self.personal_numbers if componentId == component.id ])
            elif typeId == CustomizationType.MODIFICATION and componentId in self.modifications:
                result += 1
        return result

    def removeComponent(self, componentId, typeId, count):
        countBefore = count
        if count > 0:
            if typeId in CustomizationType.APPLIED_TO_TYPES:
                attr = '{}s'.format(lower(CustomizationTypeNames[typeId]))
                outfitComponents = getattr(self, attr)
                for component in outfitComponents:
                    if componentId == component.id:
                        for area in ApplyArea.RANGE:
                            if area & component.appliedTo:
                                component.appliedTo &= ~area
                                count -= 1
                                if not count:
                                    break

                    if not count:
                        break

                if count != countBefore:
                    setattr(self, attr, [ component for component in outfitComponents if component.appliedTo ])
            elif typeId in CustomizationType.SIMPLE_TYPES:
                if typeId == CustomizationType.STYLE and self.styleId == componentId:
                    self.styleId = 0
                    self.styleProgressionLevel = 0
                    count -= 1
                elif typeId == CustomizationType.PROJECTION_DECAL:
                    projection_decals = []
                    for component in self.projection_decals:
                        if componentId != component.id or count == 0:
                            projection_decals.append(component)
                            continue
                        count -= 1

                    self.projection_decals = projection_decals
                elif typeId == CustomizationType.MODIFICATION and componentId in self.modifications:
                    self.modifications.remove(componentId)
                    count -= 1
        return countBefore - count

    def wipe(self, gameParams, cache, getGroupedComponentPrice, vehType=None):
        outfitItems = getAllItemsFromOutfit(cache, self)
        for itemDescr, count in outfitItems.items():
            cid, itemId = cn.splitIntDescr(itemDescr)
            isNeedRemove = False
            item = cache.itemTypes[cid][itemId]
            if cid == CustomizationType.STYLE and item.isRent or item.isProgressive():
                isNeedRemove = True
            elif not (vehType is not None and cid == CustomizationType.DECAL and itemId == vehType.defaultPlayerEmblemID):
                try:
                    getGroupedComponentPrice(gameParams, itemDescr, True)
                except SoftException:
                    if not self.styleId or 'styleOnly' not in item.tags:
                        isNeedRemove = True

            if isNeedRemove:
                self.removeComponent(itemId, cid, count)
            outfitItems.pop(itemDescr)

        return outfitItems


_CUSTOMIZATION_CLASSES = {t.customType:t for t in SerializableComponent.__subclasses__()}

def makeCompDescr(customizationItem):
    return ComponentBinSerializer().serialize(customizationItem)


def parseCompDescr(customizationElementCompDescr):
    return ComponentBinDeserializer(_CUSTOMIZATION_CLASSES).decode(customizationElementCompDescr)


def checkItemInCompDescr(item, customizationElementCompDescr):
    item = cn.splitIntDescr(item) if isinstance(item, int) else item
    itemType = item[0]
    if itemType == CustomizationType.STYLE:
        path = ('styleId', None)
    elif itemType == CustomizationType.MODIFICATION:
        path = ('modifications', None)
    else:
        path = ('{}s'.format(lower(CustomizationTypeNames[itemType])), ('id', None))
    return ComponentBinDeserializer(_CUSTOMIZATION_CLASSES).hasItem(customizationElementCompDescr, path, item[1])


def parseOutfitDescr(outfitDescr):
    if not outfitDescr:
        return CustomizationOutfit()
    try:
        outfit = parseCompDescr(outfitDescr)
    except SerializationException:
        LOG_CURRENT_EXCEPTION()
        LOG_ERROR('Bad outfit descr', base64.b64encode(outfitDescr))
        outfit = CustomizationOutfit()

    if outfit.customType != CustomizationOutfit.customType:
        raise SoftException('Wrong customization item type')
    return outfit


if IS_CELLAPP or IS_BASEAPP:
    _itemType = TypeVar('_itemType', bound=cn.BaseCustomizationItem)

def getAllItemsFromOutfit(cc, outfit, ignoreHiddenCamouflage=True, ignoreEmpty=True, ignoreStyleOnly=True, skipStyle=False):
    result = defaultdict(int)
    for i in outfit.modifications:
        if __ignoreItem(i, cc.modifications, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.ModificationItem.makeIntDescr(i)] = 1

    for d in outfit.decals:
        decalId = d.id
        if __ignoreItem(decalId, cc.decals, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.DecalItem.makeIntDescr(decalId)] += ApplyArea.getAppliedCount(d.appliedTo)

    for d in outfit.projection_decals:
        decalId = d.id
        if __ignoreItem(decalId, cc.projection_decals, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.ProjectionDecalItem.makeIntDescr(decalId)] += 1

    for number in outfit.personal_numbers:
        numberId = number.id
        if __ignoreItem(numberId, cc.personal_numbers, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.PersonalNumberItem.makeIntDescr(numberId)] += ApplyArea.getAppliedCount(number.appliedTo)

    for p in outfit.paints:
        paintId = p.id
        if paintId != EMPTY_ITEM_ID:
            if ignoreStyleOnly and cc.paints[paintId].isStyleOnly:
                continue
            count = cc.paints[paintId].getAmount(p.appliedTo)
        elif not ignoreEmpty:
            count = ApplyArea.getAppliedCount(p.appliedTo)
        else:
            continue
        result[cn.PaintItem.makeIntDescr(paintId)] += count

    for ce in outfit.camouflages:
        camouflageId = ce.id
        if ce.id == HIDDEN_CAMOUFLAGE_ID:
            if ignoreHiddenCamouflage:
                continue
        elif __ignoreItem(camouflageId, cc.camouflages, ignoreEmpty, ignoreStyleOnly):
            continue
        result[cn.CamouflageItem.makeIntDescr(camouflageId)] += ApplyArea.getAppliedCount(ce.appliedTo)

    if outfit.styleId and not skipStyle:
        result[cn.StyleItem.makeIntDescr(outfit.styleId)] = 1
    return dict(result)


def isEditedStyle(outfit):
    styleId = outfit.styleId
    styleProgressLvl = outfit.styleProgressionLevel
    outfit.styleId = 0
    outfit.styleProgressionLevel = 0
    isEmpty = not outfit
    outfit.styleId = styleId
    outfit.styleProgressionLevel = styleProgressLvl
    return not isEmpty


def getNationalEmblemsOutfit(vehDescr):
    decals = createNationalEmblemComponents(vehDescr)
    outfit = CustomizationOutfit(decals=decals)
    return outfit


def __ignoreItem(itemId, cache, ignoreEmpty, ignoreStyleOnly):
    if itemId != EMPTY_ITEM_ID:
        if ignoreStyleOnly and cache[itemId].isStyleOnly:
            return True
    elif ignoreEmpty:
        return True
    return False


def _setComponentsRegion(component, region):
    if hasattr(component, 'appliedTo'):
        setattr(component, 'appliedTo', region)
    elif hasattr(component, 'slotId'):
        setattr(component, 'slotId', region)
    else:
        LOG_ERROR('Unable to set region {0} for component {1}'.format(region, component))


def getOutfitType(arenaKind, bonusType):
    return SeasonType.fromArenaKind(arenaKind)


def getBattleOutfit(getter, vehType, arenaKind, bonusType):
    styleOutfitDescr = getter(vehType, SeasonType.EVENT)
    if styleOutfitDescr:
        return parseOutfitDescr(styleOutfitDescr)
    season = getOutfitType(arenaKind, bonusType)
    seasonOutfitDescr = getter(vehType, season)
    if seasonOutfitDescr:
        return parseOutfitDescr(seasonOutfitDescr)
    styleOutfitDescr = getter(vehType, SeasonType.ALL)
    return parseOutfitDescr(styleOutfitDescr)


def parseBattleOutfit(outfit, cache, arenaKind):
    if not outfit.styleId:
        return outfit
    styleOutfit = cache.styles[outfit.styleId].outfits[SeasonType.fromArenaKind(arenaKind)]
    return styleOutfit if not isEditedStyle(outfit) else copy.deepcopy(styleOutfit).applyDiff(outfit)


class OutfitLogEntry(object):

    def __init__(self, outfit):
        self.style_cd = cn.StyleItem.makeIntDescr(outfit.styleId) if outfit.styleId else 0
        self.modification_cd = cn.ModificationItem.makeIntDescr(outfit.modifications[0]) if outfit.modifications else 0
        self._paints = CustomizationOutfit.applyAreaBitmaskToDict(outfit.paints)
        self._decals = CustomizationOutfit.applyAreaBitmaskToDict(outfit.decals)
        self._projection_decals = outfit.projection_decals
        self._camouflages = CustomizationOutfit.applyAreaBitmaskToDict(outfit.camouflages)
        self._personal_numbers = CustomizationOutfit.applyAreaBitmaskToDict(outfit.personal_numbers)
        self.chassis_paint_cd = self.__getPaintCd(ApplyArea.CHASSIS)
        self.hull_paint_cd = self.__getPaintCd(ApplyArea.HULL)
        self.turret_paint_cd = self.__getPaintCd(ApplyArea.TURRET)
        self.gun_paint_cd0 = self.__getPaintCd(ApplyArea.GUN)
        self.gun_paint_cd1 = self.__getPaintCd(ApplyArea.GUN_1)
        self.hull_camouflage_cd = self.__getCamouflageCd(ApplyArea.HULL)
        self.turret_camouflage_cd = self.__getCamouflageCd(ApplyArea.TURRET)
        self.gun_camouflage_cd = self.__getCamouflageCd(ApplyArea.GUN)
        self.hull_decal_cd0, self.hull_decal_progression_level0 = self.__getDecalCd(ApplyArea.HULL)
        self.hull_decal_cd1, self.hull_decal_progression_level1 = self.__getDecalCd(ApplyArea.HULL_1)
        self.hull_decal_cd2, self.hull_decal_progression_level2 = self.__getDecalCd(ApplyArea.HULL_2)
        self.hull_decal_cd3, self.hull_decal_progression_level3 = self.__getDecalCd(ApplyArea.HULL_3)
        self.turret_decal_cd0, self.turret_decal_progression_level0 = self.__getDecalCd(ApplyArea.TURRET)
        self.turret_decal_cd1, self.turret_decal_progression_level1 = self.__getDecalCd(ApplyArea.TURRET_1)
        self.turret_decal_cd2, self.turret_decal_progression_level2 = self.__getDecalCd(ApplyArea.TURRET_2)
        self.turret_decal_cd3, self.turret_decal_progression_level3 = self.__getDecalCd(ApplyArea.TURRET_3)
        self.hull_personal_number0 = self.__getPersonalNumberData(ApplyArea.HULL_2)
        self.hull_personal_number1 = self.__getPersonalNumberData(ApplyArea.HULL_3)
        self.turret_personal_number0 = self.__getPersonalNumberData(ApplyArea.TURRET_2)
        self.turret_personal_number1 = self.__getPersonalNumberData(ApplyArea.TURRET_3)
        self.gun_personal_number0 = self.__getPersonalNumberData(ApplyArea.GUN_2)
        self.gun_personal_number1 = self.__getPersonalNumberData(ApplyArea.GUN_3)
        for number in xrange(0, MAX_USERS_PROJECTION_DECALS):
            setattr(self, 'projection_decal{0}'.format(number), self.__getProjectionDecalData(number))

        self.style_progression_level = outfit.styleProgressionLevel

    @staticmethod
    def __getItemCompDescr(storage, area, cdFormatter):
        i = storage.get(area)
        return 0 if not i else cdFormatter(i[0].id)

    @staticmethod
    def __getItemCompDescrWithProgression(storage, area, cdFormatter):
        i = storage.get(area)
        return (0, 0) if not i else (cdFormatter(i[0].id), i[0].progressionLevel)

    def __getPaintCd(self, area):
        return OutfitLogEntry.__getItemCompDescr(self._paints, area, cn.PaintItem.makeIntDescr)

    def __getCamouflageCd(self, area):
        return OutfitLogEntry.__getItemCompDescr(self._camouflages, area, cn.CamouflageItem.makeIntDescr)

    def __getDecalCd(self, area):
        return OutfitLogEntry.__getItemCompDescrWithProgression(self._decals, area, cn.DecalItem.makeIntDescr)

    def __getPersonalNumberCd(self, area):
        return OutfitLogEntry.__getItemCompDescr(self._personal_numbers, area, cn.PersonalNumberItem.makeIntDescr)

    def __getProjectionDecalData(self, number):
        value = {'projection_decal_slot': 0,
         'projection_decal_cd': 0,
         'projection_decal_options': 0,
         'projection_decal_scaleFactorId': 0,
         'projection_decal_progression_level': 0}
        try:
            projectionDecal = self._projection_decals[number]
            value['projection_decal_slot'] = projectionDecal.slotId
            value['projection_decal_cd'] = cn.ProjectionDecalItem.makeIntDescr(projectionDecal.id)
            value['projection_decal_options'] = projectionDecal.options
            value['projection_decal_scaleFactorId'] = projectionDecal.scaleFactorId
            value['projection_decal_progression_level'] = projectionDecal.progressionLevel
        except IndexError:
            pass

        return value

    def __getPersonalNumberData(self, area):
        value = {}
        value['personal_number_cd'] = self.__getPersonalNumberCd(area)
        number = self._personal_numbers.get(area)
        value['number'] = number[0].number if number else ''
        return value

    def toDict(self):
        return {k:v for k, v in self.__dict__.iteritems() if not k.startswith('_')}


class NamedVector(defaultdict):

    def __init__(self, default_factory=int, args=None):
        super(NamedVector, self).__init__(default_factory, args or [])

    def __add__(self, other):
        r = NamedVector(self.default_factory, self.iteritems())
        r += other
        return r

    def __iadd__(self, other):
        for k, v in other.iteritems():
            self[k] += v

        return self

    __radd__ = __add__

    def __sub__(self, other):
        r = NamedVector(self.default_factory, self.iteritems())
        r -= other
        return r

    def __isub__(self, other):
        for k, v in other.iteritems():
            self[k] -= v

        return self

    def __rsub__(self, other):
        r = NamedVector(self.default_factory, other.iteritems)
        r -= self
        return r


def makeLogOutfitValues(outfitDescr):
    outfit = parseOutfitDescr(outfitDescr)
    return OutfitLogEntry(outfit).toDict()


def getVehicleOutfit(outfits, vehTypeDescr, outfitType):
    return outfits.get(vehTypeDescr, {}).get(outfitType, '')


def createNationalEmblemComponents(vehDescr):
    decals = []
    nationalEmblemId = vehDescr.type.defaultPlayerEmblemID
    emblemRegions, _ = cn.getAvailableDecalRegions(vehDescr)
    if emblemRegions:
        decals.append(DecalComponent(id=nationalEmblemId, appliedTo=emblemRegions))
    return decals


def _clamp(value, minValue, maxValue, limit):
    value = int(round((min(max(float(value), minValue), maxValue) - minValue) / (maxValue - minValue) * limit))
    return value


def _unclamp(value, minValue, maxValue, limit):
    return float(value) * (maxValue - minValue) / limit + minValue


def _clamp16(value, minValue, maxValue):
    return _clamp(value, minValue, maxValue, 65535)


def _unclamp16(value, minValue, maxValue):
    return _unclamp(value, minValue, maxValue, 65535)


def _getDifferVehiclePartNames(newVehDescr, oldVehDescr):
    differPartNames = []
    for partName in CUSTOMIZATION_SLOTS_VEHICLE_PARTS:
        if getattr(newVehDescr, partName).compactDescr != getattr(oldVehDescr, partName).compactDescr:
            differPartNames.append(partName)

    return differPartNames
