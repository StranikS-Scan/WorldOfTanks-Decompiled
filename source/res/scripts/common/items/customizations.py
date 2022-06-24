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

def getEditorOnlySection(section, createNewSection=False):
    editorOnlySection = section['editorOnly']
    if editorOnlySection is None and createNewSection:
        from items.writers.c11n_writers import findOrCreate
        editorOnlySection = findOrCreate(section, 'editorOnly')
    return editorOnlySection


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
    SAVE_AS_EDITOR_ONLY = 32


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


if IS_EDITOR:
    FieldType = namedtuple('FieldType', 'type default flags saveTag')
    FieldType.__new__.func_defaults = (None,) * len(FieldType._fields)
else:
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
        typedArray = FieldTypes.TYPED_ARRAY
        for fname, ftype in self.fields.iteritems():
            if ftype.flags & ignoreFlags:
                continue
            v1 = getattr(self, fname)
            v2 = getattr(o, fname)
            if ftype.type & typedArray:
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
        deprecated = FieldFlags.DEPRECATED
        for name, ftype in self.fields.iteritems():
            if ftype.flags & deprecated:
                continue
            v1 = getattr(self, name)
            if isinstance(v1, list) or isinstance(v1, Math.Vector2) or isinstance(v1, Math.Vector3) or isinstance(v1, Math.Vector4):
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
        serialize = self.__serialize
        encode = varint.encode
        for fieldName, fieldInfo in obj.fields.iteritems():
            if fieldInfo.flags & FieldFlags.DEPRECATED:
                offset <<= 1
                continue
            if fieldInfo.flags & FieldFlags.NON_BIN:
                continue
            if IS_EDITOR and fieldInfo.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
                continue
            value = getattr(obj, fieldName)
            if value != fieldInfo.default:
                hasValue |= offset
                result.append(serialize(value, fieldInfo.type))
            offset <<= 1

        result[0] = encode(hasValue)
        return ''.join(result)

    def __serializeArray(self, value, itemType):
        serialize = self.__serialize
        result = [ serialize(item, itemType) for item in value ]
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
        decode_stream = varint.decode_stream
        valueMap = decode_stream(io)
        offset = 1
        for k, t in fields.iteritems():
            if t.flags & FieldFlags.NON_BIN:
                continue
            if IS_EDITOR and t.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
                continue
            next = None if not path or path[0] != k else path[1]
            if valueMap & offset:
                ftype = t.type
                if ftype == FieldTypes.VARINT:
                    value = decode_stream(io)
                elif ftype == FieldTypes.STRING:
                    value = self.__decodeString()
                elif ftype == FieldTypes.APPLY_AREA_ENUM:
                    value = decode_stream(io)
                elif ftype == FieldTypes.OPTIONS_ENUM:
                    value = decode_stream(io)
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
        decode_stream = varint.decode_stream
        n = decode_stream(io)
        if itemType == FieldTypes.VARINT:
            array = [ decode_stream(io) for _ in xrange(n) ]
            if path and path[1] is None and path[0] == k and wanted in array:
                raise FoundItemException()
            return array
        elif itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
            customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
            decodeCustomType = self.__decodeCustomType
            return [ decodeCustomType(customType, next, wanted) for _ in xrange(n) ]
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

    def __decodeCustomType--- This code section failed: ---

 458       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'customTypes'
           6	LOAD_FAST         'customType'
           9	BINARY_SUBSCR     ''
          10	STORE_FAST        'cls'

 459      13	LOAD_FAST         'cls'
          16	CALL_FUNCTION_0   ''
          19	STORE_FAST        'instance'

 460      22	SETUP_LOOP        '644'
          25	LOAD_FAST         'cls'
          28	LOAD_ATTR         'fields'
          31	LOAD_ATTR         'iteritems'
          34	CALL_FUNCTION_0   ''
          37	GET_ITER          ''
          38	FOR_ITER          '643'
          41	UNPACK_SEQUENCE_2 ''
          44	STORE_FAST        'fname'
          47	STORE_FAST        'finfo'

 461      50	LOAD_FAST         'finfo'
          53	LOAD_ATTR         'flags'
          56	LOAD_GLOBAL       'FieldFlags'
          59	LOAD_ATTR         'NON_XML'
          62	BINARY_AND        ''
          63	POP_JUMP_IF_FALSE '72'

 462      66	CONTINUE          '38'
          69	JUMP_FORWARD      '72'
        72_0	COME_FROM         '69'

 464      72	LOAD_FAST         'section'
          75	LOAD_ATTR         'has_key'
          78	LOAD_FAST         'fname'
          81	CALL_FUNCTION_1   ''
          84	POP_JUMP_IF_TRUE  '175'

 465      87	LOAD_GLOBAL       'IS_EDITOR'
          90	POP_JUMP_IF_FALSE '38'
          93	LOAD_FAST         'finfo'
          96	LOAD_ATTR         'flags'
          99	LOAD_GLOBAL       'FieldFlags'
         102	LOAD_ATTR         'SAVE_AS_EDITOR_ONLY'
         105	BINARY_AND        ''
       106_0	COME_FROM         '90'
         106	POP_JUMP_IF_FALSE '38'

 466     109	LOAD_GLOBAL       'getEditorOnlySection'
         112	LOAD_FAST         'section'
         115	CALL_FUNCTION_1   ''
         118	STORE_FAST        'editorOnlySection'

 467     121	LOAD_FAST         'editorOnlySection'
         124	LOAD_CONST        ''
         127	COMPARE_OP        'is not'
         130	POP_JUMP_IF_FALSE '38'

 468     133	LOAD_FAST         'editorOnlySection'
         136	LOAD_ATTR         'has_key'
         139	LOAD_FAST         'fname'
         142	CALL_FUNCTION_1   ''
       145_0	COME_FROM         '130'
         145	POP_JUMP_IF_FALSE '38'

 469     148	LOAD_FAST         'editorOnlySection'
         151	STORE_FAST        'section'
         154	JUMP_ABSOLUTE     '166'

 471     157	CONTINUE          '38'
         160	JUMP_ABSOLUTE     '172'

 473     163	CONTINUE          '38'
         166	JUMP_ABSOLUTE     '175'

 475     169	CONTINUE          '38'
         172	JUMP_FORWARD      '175'
       175_0	COME_FROM         '172'

 477     175	LOAD_FAST         'finfo'
         178	LOAD_ATTR         'type'
         181	STORE_FAST        'ftype'

 478     184	LOAD_FAST         'ftype'
         187	LOAD_GLOBAL       'FieldTypes'
         190	LOAD_ATTR         'VARINT'
         193	COMPARE_OP        '=='
         196	POP_JUMP_IF_FALSE '217'

 479     199	LOAD_FAST         'section'
         202	LOAD_ATTR         'readInt'
         205	LOAD_FAST         'fname'
         208	CALL_FUNCTION_1   ''
         211	STORE_FAST        'value'
         214	JUMP_FORWARD      '552'

 480     217	LOAD_FAST         'ftype'
         220	LOAD_GLOBAL       'FieldTypes'
         223	LOAD_ATTR         'FLOAT'
         226	COMPARE_OP        '=='
         229	POP_JUMP_IF_FALSE '250'

 481     232	LOAD_FAST         'section'
         235	LOAD_ATTR         'readFloat'
         238	LOAD_FAST         'fname'
         241	CALL_FUNCTION_1   ''
         244	STORE_FAST        'value'
         247	JUMP_FORWARD      '552'

 482     250	LOAD_FAST         'ftype'
         253	LOAD_GLOBAL       'FieldTypes'
         256	LOAD_ATTR         'APPLY_AREA_ENUM'
         259	COMPARE_OP        '=='
         262	POP_JUMP_IF_FALSE '295'

 483     265	LOAD_FAST         'self'
         268	LOAD_ATTR         '__decodeEnum'
         271	LOAD_FAST         'section'
         274	LOAD_ATTR         'readString'
         277	LOAD_FAST         'fname'
         280	CALL_FUNCTION_1   ''
         283	LOAD_GLOBAL       'ApplyArea'
         286	CALL_FUNCTION_2   ''
         289	STORE_FAST        'value'
         292	JUMP_FORWARD      '552'

 484     295	LOAD_FAST         'ftype'
         298	LOAD_GLOBAL       'FieldTypes'
         301	LOAD_ATTR         'TAGS'
         304	COMPARE_OP        '=='
         307	POP_JUMP_IF_FALSE '340'

 485     310	LOAD_GLOBAL       'tuple'
         313	LOAD_FAST         'section'
         316	LOAD_ATTR         'readString'
         319	LOAD_FAST         'fname'
         322	CALL_FUNCTION_1   ''
         325	LOAD_ATTR         'split'
         328	CALL_FUNCTION_0   ''
         331	CALL_FUNCTION_1   ''
         334	STORE_FAST        'value'
         337	JUMP_FORWARD      '552'

 486     340	LOAD_FAST         'ftype'
         343	LOAD_GLOBAL       'FieldTypes'
         346	LOAD_ATTR         'STRING'
         349	COMPARE_OP        '=='
         352	POP_JUMP_IF_FALSE '373'

 487     355	LOAD_FAST         'section'
         358	LOAD_ATTR         'readString'
         361	LOAD_FAST         'fname'
         364	CALL_FUNCTION_1   ''
         367	STORE_FAST        'value'
         370	JUMP_FORWARD      '552'

 488     373	LOAD_FAST         'ftype'
         376	LOAD_GLOBAL       'FieldTypes'
         379	LOAD_ATTR         'OPTIONS_ENUM'
         382	COMPARE_OP        '=='
         385	POP_JUMP_IF_FALSE '418'

 489     388	LOAD_FAST         'self'
         391	LOAD_ATTR         '__decodeEnum'
         394	LOAD_FAST         'section'
         397	LOAD_ATTR         'readString'
         400	LOAD_FAST         'fname'
         403	CALL_FUNCTION_1   ''
         406	LOAD_GLOBAL       'Options'
         409	CALL_FUNCTION_2   ''
         412	STORE_FAST        'value'
         415	JUMP_FORWARD      '552'

 490     418	LOAD_FAST         'ftype'
         421	LOAD_GLOBAL       'FieldTypes'
         424	LOAD_ATTR         'TYPED_ARRAY'
         427	BINARY_AND        ''
         428	POP_JUMP_IF_FALSE '478'

 491     431	LOAD_FAST         'ftype'
         434	LOAD_GLOBAL       'FieldTypes'
         437	LOAD_ATTR         'TYPED_ARRAY'
         440	BINARY_XOR        ''
         441	STORE_FAST        'itemType'

 492     444	LOAD_FAST         'self'
         447	LOAD_ATTR         '__decodeArray'
         450	LOAD_FAST         'itemType'
         453	LOAD_FAST         'ctx'
         456	LOAD_FAST         'fname'
         459	BUILD_TUPLE_2     ''
         462	LOAD_FAST         'section'
         465	LOAD_FAST         'fname'
         468	BINARY_SUBSCR     ''
         469	CALL_FUNCTION_3   ''
         472	STORE_FAST        'value'
         475	JUMP_FORWARD      '552'

 493     478	LOAD_FAST         'ftype'
         481	LOAD_GLOBAL       'FieldTypes'
         484	LOAD_ATTR         'CUSTOM_TYPE_OFFSET'
         487	COMPARE_OP        '>='
         490	POP_JUMP_IF_FALSE '540'

 494     493	LOAD_FAST         'ftype'
         496	LOAD_GLOBAL       'FieldTypes'
         499	LOAD_ATTR         'CUSTOM_TYPE_OFFSET'
         502	BINARY_DIVIDE     ''
         503	STORE_FAST        'ftype'

 495     506	LOAD_FAST         'self'
         509	LOAD_ATTR         '__decodeCustomType'
         512	LOAD_FAST         'ftype'
         515	LOAD_FAST         'ctx'
         518	LOAD_FAST         'fname'
         521	BUILD_TUPLE_2     ''
         524	LOAD_FAST         'section'
         527	LOAD_FAST         'fname'
         530	BINARY_SUBSCR     ''
         531	CALL_FUNCTION_3   ''
         534	STORE_FAST        'value'
         537	JUMP_FORWARD      '552'

 497     540	LOAD_GLOBAL       'SerializationException'
         543	LOAD_CONST        'Unsupported item type'
         546	CALL_FUNCTION_1   ''
         549	RAISE_VARARGS_1   ''
       552_0	COME_FROM         '214'
       552_1	COME_FROM         '247'
       552_2	COME_FROM         '292'
       552_3	COME_FROM         '337'
       552_4	COME_FROM         '370'
       552_5	COME_FROM         '415'
       552_6	COME_FROM         '475'
       552_7	COME_FROM         '537'

 498     552	LOAD_FAST         'finfo'
         555	LOAD_ATTR         'flags'
         558	LOAD_GLOBAL       'FieldFlags'
         561	LOAD_ATTR         'DEPRECATED'
         564	BINARY_AND        ''
         565	UNARY_NOT         ''
         566	POP_JUMP_IF_TRUE  '584'
         569	LOAD_GLOBAL       'hasattr'
         572	LOAD_FAST         'instance'
         575	LOAD_FAST         'fname'
         578	CALL_FUNCTION_2   ''
       581_0	COME_FROM         '566'
         581	POP_JUMP_IF_FALSE '603'

 499     584	LOAD_GLOBAL       'setattr'
         587	LOAD_FAST         'instance'
         590	LOAD_FAST         'fname'
         593	LOAD_FAST         'value'
         596	CALL_FUNCTION_3   ''
         599	POP_TOP           ''
         600	JUMP_FORWARD      '603'
       603_0	COME_FROM         '600'

 501     603	LOAD_GLOBAL       'IS_EDITOR'
         606	POP_JUMP_IF_FALSE '38'
         609	LOAD_FAST         'finfo'
         612	LOAD_ATTR         'flags'
         615	LOAD_GLOBAL       'FieldFlags'
         618	LOAD_ATTR         'SAVE_AS_EDITOR_ONLY'
         621	BINARY_AND        ''
       622_0	COME_FROM         '606'
         622	POP_JUMP_IF_FALSE '38'

 502     625	LOAD_FAST         'section'
         628	LOAD_ATTR         'parentSection'
         631	CALL_FUNCTION_0   ''
         634	STORE_FAST        'section'
         637	JUMP_BACK         '38'
         640	JUMP_BACK         '38'
         643	POP_BLOCK         ''
       644_0	COME_FROM         '22'

 503     644	LOAD_FAST         'instance'
         647	RETURN_VALUE      ''

Syntax error at or near 'CONTINUE' token at offset 169

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
     ('styleProgressionLevel', intField()),
     ('serial_number', strField())))
    __slots__ = ('modifications', 'paints', 'camouflages', 'decals', 'styleId', 'projection_decals', 'insignias', 'personal_numbers', 'sequences', 'attachments', 'styleProgressionLevel', 'serial_number')

    def __init__(self, modifications=None, paints=None, camouflages=None, decals=None, projection_decals=None, personal_numbers=None, styleId=0, insignias=None, sequences=None, attachments=None, styleProgressionLevel=0, serial_number=None):
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
        self.serial_number = serial_number or ''
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
        applyAreaBitmaskToDict = CustomizationOutfit.applyAreaBitmaskToDict
        shrinkAreaBitmask = CustomizationOutfit.shrinkAreaBitmask
        for typeId in CustomizationType.APPLIED_TO_TYPES:
            componentsAttrName = '{}s'.format(lower(CustomizationTypeNames[typeId]))
            components = applyAreaBitmaskToDict(getattr(self, componentsAttrName))
            setattr(self, componentsAttrName, shrinkAreaBitmask(components))

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
                    if i not in res:
                        res[i] = [cpy]
                    else:
                        res[i].append(cpy)
                i *= 2

        return res

    @staticmethod
    def slotIdToDict(components):
        res = {}
        for c in components:
            cpy = c.copy()
            slotId = cpy.slotId
            cpy.slotId = 0
            if slotId not in res:
                res[slotId] = [cpy]
            res[slotId].append(cpy)

        return res

    @staticmethod
    def shrinkAreaBitmask(components):
        grouped = {}
        for at, lst in components.iteritems():
            for i in lst:
                if i not in grouped:
                    grouped[i] = [at]
                grouped[i].append(at)

        res = []
        orOp = int.__or__
        for item, group in grouped.iteritems():
            curItem = item.copy()
            curItem.appliedTo = reduce(orOp, group, 0)
            res.append(curItem)

        return res

    def applyDiff(self, outfit):
        resultOutfit = self.copy()
        resultOutfit.styleProgressionLevel = outfit.styleProgressionLevel
        resultOutfit.serial_number = outfit.serial_number
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
        getVehicleProjectionDecalSlotParams = cn.getVehicleProjectionDecalSlotParams
        if differPartNames:
            newProjectionDecals = []
            for projectionDecal in projectionDecals:
                if not getVehicleProjectionDecalSlotParams(oldVehDescr, projectionDecal.slotId, differPartNames):
                    newProjectionDecals.append(projectionDecal)
                    continue
                toMove[(CustomizationType.PROJECTION_DECAL, projectionDecal.id)] += 1

            if toMove:
                self.projection_decals = newProjectionDecals
        dismountComponents = self.dismountComponents
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
                    toMove += dismountComponents(dismountArea, (componentType,))

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
                    self.serial_number = ''
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
    styleSerialNumber = outfit.serial_number
    outfit.styleId = 0
    outfit.styleProgressionLevel = 0
    outfit.serial_number = ''
    isEmpty = not outfit
    outfit.styleId = styleId
    outfit.styleProgressionLevel = styleProgressLvl
    outfit.serial_number = styleSerialNumber
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
        applyAreaBitmaskToDict = CustomizationOutfit.applyAreaBitmaskToDict
        getPaintCd = self.__getPaintCd
        getCamouflageCd = self.__getCamouflageCd
        getDecalCd = self.__getDecalCd
        getPersonalNumberData = self.__getPersonalNumberData
        self.style_cd = cn.StyleItem.makeIntDescr(outfit.styleId) if outfit.styleId else 0
        self.modification_cd = cn.ModificationItem.makeIntDescr(outfit.modifications[0]) if outfit.modifications else 0
        self._paints = applyAreaBitmaskToDict(outfit.paints)
        self._decals = applyAreaBitmaskToDict(outfit.decals)
        self._projection_decals = outfit.projection_decals
        self._camouflages = applyAreaBitmaskToDict(outfit.camouflages)
        self._personal_numbers = applyAreaBitmaskToDict(outfit.personal_numbers)
        self.chassis_paint_cd = getPaintCd(ApplyArea.CHASSIS)
        self.hull_paint_cd = getPaintCd(ApplyArea.HULL)
        self.turret_paint_cd = getPaintCd(ApplyArea.TURRET)
        self.gun_paint_cd0 = getPaintCd(ApplyArea.GUN)
        self.gun_paint_cd1 = getPaintCd(ApplyArea.GUN_1)
        self.hull_camouflage_cd = getCamouflageCd(ApplyArea.HULL)
        self.turret_camouflage_cd = getCamouflageCd(ApplyArea.TURRET)
        self.gun_camouflage_cd = getCamouflageCd(ApplyArea.GUN)
        self.hull_decal_cd0, self.hull_decal_progression_level0 = getDecalCd(ApplyArea.HULL)
        self.hull_decal_cd1, self.hull_decal_progression_level1 = getDecalCd(ApplyArea.HULL_1)
        self.hull_decal_cd2, self.hull_decal_progression_level2 = getDecalCd(ApplyArea.HULL_2)
        self.hull_decal_cd3, self.hull_decal_progression_level3 = getDecalCd(ApplyArea.HULL_3)
        self.turret_decal_cd0, self.turret_decal_progression_level0 = getDecalCd(ApplyArea.TURRET)
        self.turret_decal_cd1, self.turret_decal_progression_level1 = getDecalCd(ApplyArea.TURRET_1)
        self.turret_decal_cd2, self.turret_decal_progression_level2 = getDecalCd(ApplyArea.TURRET_2)
        self.turret_decal_cd3, self.turret_decal_progression_level3 = getDecalCd(ApplyArea.TURRET_3)
        self.hull_personal_number0 = getPersonalNumberData(ApplyArea.HULL_2)
        self.hull_personal_number1 = getPersonalNumberData(ApplyArea.HULL_3)
        self.turret_personal_number0 = getPersonalNumberData(ApplyArea.TURRET_2)
        self.turret_personal_number1 = getPersonalNumberData(ApplyArea.TURRET_3)
        self.gun_personal_number0 = getPersonalNumberData(ApplyArea.GUN_2)
        self.gun_personal_number1 = getPersonalNumberData(ApplyArea.GUN_3)
        getProjectionDecalData = self.__getProjectionDecalData
        for number in xrange(0, MAX_USERS_PROJECTION_DECALS):
            setattr(self, 'projection_decal{}'.format(number), getProjectionDecalData(number))

        self.style_progression_level = outfit.styleProgressionLevel
        self.serial_number = outfit.serial_number

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
    return OutfitLogEntry(parseOutfitDescr(outfitDescr)).toDict()


def getHullCamouflageCd(outfitDescr):
    i = CustomizationOutfit.applyAreaBitmaskToDict(parseOutfitDescr(outfitDescr).camouflages).get(ApplyArea.HULL)
    return 0 if not i else cn.CamouflageItem.makeIntDescr(i[0].id)


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

    if 'turret' in differPartNames:
        if 'gun' not in differPartNames:
            differPartNames.append('gun')
    elif 'gun' in differPartNames:
        differPartNames.append('turret')
    return differPartNames