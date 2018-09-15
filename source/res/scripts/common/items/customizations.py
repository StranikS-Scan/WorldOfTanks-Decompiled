# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/customizations.py
"""
Customization uses custom serialisation mechanism described below.

There are 3 basic types:
 - intField - integer value encoded by varint
 - arrayField - fixed type array encoded like: varint(size) + [encode(item) for item in items]
 - customFieldType - class with set of fields of different types. Encoded like:
     varint(customType) + varint(hasValue) + [encode(field) for field in fields],
     where customType is unique id of type and hasValue is a bitmask defining if i-th
     field has stored value (encode is performed only if field has non default value).

All customization components are customFieldType inherited from SerializableComponent that allow
to pack and unpack these components with help of ComponentBinSerializer and ComponentBinDeserializer.

Creating new customization component.
You need to inherit from SerializableComponent
assign UNIQUE customType and define fields. Order of fields is fixed and couldn't be changed in future.

Modification existing customization component.
If you want to delete existing field just mark it as deprecated.
If you want to add new field just add it to the end of fields list.
"""
from cStringIO import StringIO
import varint
import ResMgr
from collections import namedtuple, OrderedDict, defaultdict
from items.components.c11n_constants import ApplyArea, SeasonType
from items.components import c11n_components as cn
from constants import IS_CELLAPP, IS_BASEAPP
if IS_CELLAPP or IS_BASEAPP:
    from typing import List, Dict, Type, Tuple, Any, TypeVar, Optional, MutableMapping
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

class FieldTypes(object):
    VARINT = 2
    CUSTOM_TYPE_OFFSET = 128
    TYPED_ARRAY = 64


FieldType = namedtuple('FieldType', 'type default deprecated')

def arrayField(itemType, default=None):
    return FieldType(FieldTypes.TYPED_ARRAY | itemType, default or [], False)


def intField(default=0):
    return FieldType(FieldTypes.VARINT, default, False)


def customFieldType(customType):
    return FieldType(FieldTypes.CUSTOM_TYPE_OFFSET * customType, None, False)


def intArrayField(default=None):
    return arrayField(FieldTypes.VARINT, default or [])


def customArrayField(customType, default=None):
    return arrayField(FieldTypes.CUSTOM_TYPE_OFFSET * customType, default)


class SerializationException(Exception):
    pass


class SerializableComponent(object):
    """
    Base class for serializable classes.
    Fields which should be serialized are added to class.fields dictionary.
    Each serializable class must have unique customType
    Currently supported types are:
      * int
      * array[int]
      * ComplexType (should be derived from SerializableComponent)
      * array[ComplexType]
      Note: no support for dict for a while. Dict is Huge and unstructured type. It can be easily supported but
      we avoid it.
      Order of fields does matter. Class declaration is backward compatible with some restrictions:
        a) all new fields are added to the end of list.
        b) no fields are removed from the middle. If field is deprecated - mark it with
        FieldType.deprecated and value will be purged at next save
    
    """
    fields = OrderedDict()
    __slots__ = ()
    customType = 0

    def __eq__(self, o):
        if self.__class__ != o.__class__:
            return False
        for name, ftype in self.fields.iteritems():
            if ftype.deprecated:
                continue
            v1 = getattr(self, name)
            v2 = getattr(o, name)
            if ftype.type & FieldTypes.TYPED_ARRAY:
                v1 = set(v1)
                v2 = set(v2)
            if v1 != v2:
                return False

        return True

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        result = 17
        for name, ftype in self.fields.iteritems():
            if ftype.deprecated:
                continue
            v1 = getattr(self, name)
            result = (result * 31 + hash(v1)) % 18446744073709551616L

        return result

    def __repr__(self):
        buf = StringIO()
        self.__writeStr(buf)
        return buf.getvalue()

    def copy(self):
        o = self.__class__()
        for fname in self.fields.iterkeys():
            setattr(o, fname, getattr(self, fname))

        return o

    def __writeStr(self, stream):
        stream.write('{')
        i = 0
        n = len(self.fields)
        for name, fieldInfo in self.fields.iteritems():
            if fieldInfo.deprecated:
                continue
            v = getattr(self, name)
            stream.write('%s: %s' % (name, repr(v)))
            i += 1
            if i != n:
                stream.write(', ')

        stream.write('}')


class ComponentBinSerializer(object):
    """
    SerializableComponent binary serializer
    Serialization format is based on google's protobuf (more or less). Only non-default values are stored
    """

    def __init__(self):
        super(ComponentBinSerializer, self).__init__()

    def serialize(self, target):
        assert hasattr(target, 'customType')
        assert hasattr(target, 'fields')
        a = varint.encode(target.customType)
        b = self.__serializeCustomType(target)
        return a + b

    def __serializeCustomType(self, obj):
        assert hasattr(obj, 'customType')
        assert hasattr(obj, 'fields')
        hasValue = 0
        offset = 1
        result = ['\x00']
        for fieldName, fieldInfo in obj.fields.iteritems():
            if fieldInfo.deprecated:
                offset <<= 1
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

    def __serialize(self, value, itemType):
        if itemType == FieldTypes.VARINT:
            return varint.encode(value)
        if itemType & FieldTypes.TYPED_ARRAY:
            return self.__serializeArray(value, itemType ^ FieldTypes.TYPED_ARRAY)
        if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
            return self.__serializeCustomType(value)
        raise SerializationException('Unsupported field type %d' % (itemType,))


class ComponentBinDeserializer(object):
    """
    SerializableComponent deserializer from binary presentation produced by ComponentBinSerializer
    """

    def __init__(self, customTypes):
        self.__stream = None
        self.customTypes = customTypes
        super(ComponentBinDeserializer, self).__init__()
        return

    def decode(self, data):
        self.__stream = StringIO(data)
        code = varint.decode_stream(self.__stream)
        obj = self.__decodeCustomType(code)
        return obj

    def __decodeCustomType(self, itemType):
        cls = self.customTypes.get(itemType, None)
        assert cls
        obj = cls()
        fields = cls.fields
        io = self.__stream
        valueMap = varint.decode_stream(io)
        offset = 1
        for k, t in fields.iteritems():
            if valueMap & offset:
                ftype = t.type
                if ftype == FieldTypes.VARINT:
                    value = varint.decode_stream(io)
                elif ftype & FieldTypes.TYPED_ARRAY:
                    value = self.__decodeArray(ftype ^ FieldTypes.TYPED_ARRAY)
                elif ftype >= FieldTypes.CUSTOM_TYPE_OFFSET:
                    value = self.__decodeCustomType(ftype / FieldTypes.CUSTOM_TYPE_OFFSET)
                else:
                    raise SerializationException('Unsupported field type index')
                if not t.deprecated or hasattr(obj, k):
                    setattr(obj, k, value)
            offset <<= 1

        return obj

    def __decodeArray(self, itemType):
        n = varint.decode_stream(self.__stream)
        if itemType == FieldTypes.VARINT:
            return [ varint.decode_stream(self.__stream) for _ in xrange(n) ]
        if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
            customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
            return [ self.__decodeCustomType(customType) for _ in xrange(n) ]
        raise SerializationException('Unsupported item type')


class ComponentXmlSerializer(object):
    """ SerializableComponent xml serializer."""

    def __init__(self):
        super(ComponentXmlSerializer, self).__init__()

    def serialize(self, parent, target):
        assert hasattr(target, 'customType')
        assert hasattr(target, 'fields')
        self.__serializeCustomType(parent, target)

    def __serializeCustomType(self, xmlObj, obj):
        assert hasattr(obj, 'customType')
        assert hasattr(obj, 'fields')
        for fieldName, fieldinfo in obj.fields.iteritems():
            if fieldinfo.deprecated:
                continue
            value = getattr(obj, fieldName)
            if value != fieldinfo.default:
                child = ET.SubElement(xmlObj, fieldName)
                self.__serialize(child, value, fieldinfo.type)

        return xmlObj

    def __serializeArray(self, parent, value, itemType):
        for item in value:
            child = ET.SubElement(parent, 'item')
            self.__serialize(child, item, itemType)

    def __serialize(self, current, value, itemType):
        if itemType == FieldTypes.VARINT:
            current.text = str(value)
        elif itemType & FieldTypes.TYPED_ARRAY:
            self.__serializeArray(current, value, itemType ^ FieldTypes.TYPED_ARRAY)
        elif itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
            self.__serializeCustomType(current, value)
        else:
            raise SerializationException('Unsupported field type %d' % (itemType,))


class ComponentXmlDeserializer(object):
    """
    SerializableComponent deserializer from xml presentation produced by ComponentXmlSerializer.
    """
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
            ftype = finfo.type
            if not section.has_key(fname):
                continue
            if ftype == FieldTypes.VARINT:
                value = section.readInt(fname)
            elif ftype & FieldTypes.TYPED_ARRAY:
                itemType = ftype ^ FieldTypes.TYPED_ARRAY
                value = self.__decodeArray(itemType, (ctx, fname), section[fname])
            elif ftype >= FieldTypes.CUSTOM_TYPE_OFFSET:
                ftype = ftype / FieldTypes.CUSTOM_TYPE_OFFSET
                value = self.__decodeCustomType(ftype, (ctx, fname), section[fname])
            else:
                raise SerializationException('Unsupported item type')
            if not finfo.deprecated or hasattr(instance, fname):
                setattr(instance, fname, value)

        return instance

    def __decodeArray(self, itemType, ctx, section):
        result = []
        for i, (iname, isection) in enumerate(section.items()):
            if itemType == FieldTypes.VARINT:
                result.append(isection.asInt)
            if itemType >= FieldTypes.CUSTOM_TYPE_OFFSET:
                customType = itemType / FieldTypes.CUSTOM_TYPE_OFFSET
                ictx = (ctx, '{0} {1}'.format(iname, isection))
                result.append(self.__decodeCustomType(customType, ictx, isection))
            raise SerializationException('Unsupported item type')

        return result


class PaintComponent(SerializableComponent):
    customType = 1
    fields = OrderedDict((('id', intField()), ('appliedTo', intField(ApplyArea.USER_PAINT_ALLOWED_REGIONS_VALUE))))
    __slots__ = ('id', 'appliedTo')

    def __init__(self, id=0, appliedTo=ApplyArea.USER_PAINT_ALLOWED_REGIONS_VALUE):
        self.id = id
        self.appliedTo = appliedTo
        super(PaintComponent, self).__init__()

    def toDict(self):
        """Split appliedTo bitmask to dictionary {part: paintId}"""
        at = self.appliedTo
        p = self.id
        return {i:p for i in ApplyArea.RANGE if i & at}


class CamouflageComponent(SerializableComponent):
    customType = 2
    fields = OrderedDict((('id', intField()),
     ('patternSize', intField(1)),
     ('appliedTo', intField(ApplyArea.CAMOUFLAGE_REGIONS_VALUE)),
     ('palette', intField())))
    __slots__ = ('id', 'patternSize', 'appliedTo', 'palette')

    def __init__(self, id=0, patternSize=1, appliedTo=ApplyArea.CAMOUFLAGE_REGIONS_VALUE, palette=0):
        self.id = id
        self.patternSize = patternSize
        self.appliedTo = appliedTo
        self.palette = palette
        super(CamouflageComponent, self).__init__()


class DecalComponent(SerializableComponent):
    customType = 3
    fields = OrderedDict((('id', intField()), ('appliedTo', intField(ApplyArea.NONE))))
    __slots__ = ('id', 'appliedTo')

    def __init__(self, id=0, appliedTo=ApplyArea.NONE):
        self.id = id
        self.appliedTo = appliedTo
        super(DecalComponent, self).__init__()


class CustomizationOutfit(SerializableComponent):
    """Vehicle customization set descriptor.
    Contains all information required to represent tank on battle.
    
    Class fields:
        modifications: List[int] -- various id per vehicle appearance effects (DamageLevel, Aging)
        paints: List[PaintComponent] -- vehicle model coloring
        camouflages: List[CamouflageComponent] -- mounted camouflages with configured pattern size and palette
        decals: List[DecalComponent] -- decals (emblems and inscriptions)
        styleId: int -- predefined outfit Id from xml or 0 if custom
    """
    customType = 4
    fields = OrderedDict((('modifications', intArrayField()),
     ('paints', customArrayField(PaintComponent.customType)),
     ('camouflages', customArrayField(CamouflageComponent.customType)),
     ('decals', customArrayField(DecalComponent.customType)),
     ('styleId', intField())))
    __slots__ = ('modifications', 'paints', 'camouflages', 'decals', 'styleId')

    def __init__(self, modifications=None, paints=None, camouflages=None, decals=None, styleId=0):
        self.modifications = modifications or []
        self.paints = paints or []
        self.camouflages = camouflages or []
        self.decals = decals or []
        self.styleId = styleId or 0
        super(CustomizationOutfit, self).__init__()

    def __nonzero__(self):
        return bool(self.modifications or self.paints or self.decals or self.styleId or self.camouflages)

    def mergeOutfit(self, otherOutfit, inverse=False):
        """Apply another outfit replacing items from this outfit if conflict occurs
        
        :param otherOutfit: outfit to merge with
        :param inverse: True to store result in otherOutfit
        """
        selfOutfit = self if not inverse else otherOutfit
        otherOutfit = otherOutfit if not inverse else self
        selfOutfit.styleId = otherOutfit.styleId
        if otherOutfit.modifications:
            selfOutfit.modifications[:] = otherOutfit.modifications
        CustomizationOutfit.__overwrite(selfOutfit.paints, otherOutfit.paints, ApplyArea.RANGE)
        CustomizationOutfit.__overwrite(selfOutfit.decals, otherOutfit.decals, ApplyArea.DECAL_REGIONS)
        CustomizationOutfit.__overwrite(selfOutfit.camouflages, otherOutfit.camouflages, ApplyArea.CAMOUFLAGE_REGIONS)

    def getInvisibilityCamouflageId(self):
        """Return camouflage id which provides invisibility bonus to vehicle."""
        for ce in self.camouflages:
            if ce.appliedTo & ApplyArea.HULL:
                return ce.id

        return None

    def makeCompDescr(self):
        return makeCompDescr(self)

    @property
    def empty(self):
        return not self

    @staticmethod
    def applyAreaBitmaskToDict(components):
        """Convert list of objects with AppliedTo property to dict {ApplyArea: Item}"""
        res = {}
        for c in components:
            i = 1
            while i <= c.appliedTo:
                if c.appliedTo & i:
                    res[i] = c.copy()
                    res[i].appliedTo = 0
                i *= 2

        return res

    @staticmethod
    def shrinkAreaBitmask(components):
        grouped = {}
        for at, i in components.iteritems():
            grouped.setdefault(i, []).append(at)

        res = []
        for item, group in grouped.iteritems():
            curItem = item.copy()
            curItem.appliedTo = reduce(int.__or__, group, 0)
            res.append(curItem)

        return res

    @staticmethod
    def __overwrite(selfItems, otherItems, applyRange):
        """Unset bits from applied to in selfItems if otherItems have this bit set,
        remove empty items and add all other items
        """
        for o in otherItems:
            for i in applyRange:
                if o.appliedTo & i:
                    for s in selfItems:
                        if s.appliedTo & i:
                            s.appliedTo &= ~i

        selfItems[:] = [ i for i in selfItems if i.appliedTo != 0 ]
        selfItems.extend(otherItems)


_CUSTOMIZATION_CLASSES = {t.customType:t for t in SerializableComponent.__subclasses__()}
assert len(_CUSTOMIZATION_CLASSES) == len(SerializableComponent.__subclasses__()), 'customType duplication'

def makeCompDescr(customizationItem):
    return ComponentBinSerializer().serialize(customizationItem)


def parseCompDescr(customizationElementCompDescr):
    return ComponentBinDeserializer(_CUSTOMIZATION_CLASSES).decode(customizationElementCompDescr)


def parseOutfitDescr(outfitDescr):
    """Parse outfit and perform basic validation"""
    if not outfitDescr:
        return CustomizationOutfit()
    outfit = parseCompDescr(outfitDescr)
    if outfit.customType != CustomizationOutfit.customType:
        raise ValueError('Wrong customization item type')
    return outfit


def parseBattleOutfit(outfit, cache, arenaKind, bonusType):
    """Parse outfit and substitute predefined style with items"""
    if not outfit.styleId:
        return outfit
    style = cache.styles[outfit.styleId]
    return style.outfits[SeasonType.fromArenaKind(arenaKind)]


if IS_CELLAPP or IS_BASEAPP:
    _itemType = TypeVar('_itemType', bound=cn.BaseCustomizationItem)

def getAllItemsFromOutfit(cc, outfit):
    """Get amount of items required to fully equip given outfit.
    :return: dict{itemIntDescr, amount}
    """
    result = defaultdict(int)
    for i in outfit.modifications:
        result[cn.ModificationItem.makeIntDescr(i)] = 1

    for d in outfit.decals:
        for i in ApplyArea.RANGE:
            if i & d.appliedTo:
                result[cn.DecalItem.makeIntDescr(d.id)] += 1

    for p in outfit.paints:
        result[cn.PaintItem.makeIntDescr(p.id)] += cc.paints[p.id].getAmount(p.appliedTo)

    for ce in outfit.camouflages:
        for i in ApplyArea.RANGE:
            if i & ce.appliedTo:
                result[cn.CamouflageItem.makeIntDescr(ce.id)] += 1

    if outfit.styleId:
        result[cn.StyleItem.makeIntDescr(outfit.styleId)] = 1
    return dict(result)


def getOutfitType(arenaKind, bonusType):
    """Calculate SeasonType from arena parameters.
    Support of event season could be here."""
    return SeasonType.fromArenaKind(arenaKind)


def getBattleOutfit(getter, vehType, arenaKind, bonusType):
    """Calculate resulting outfit based arena parameters
    Order is following:
        1) All season outfit
        2) arena kind outfit
    """
    styleOutfitDescr, enabled = getter(vehType, SeasonType.ALL)
    if styleOutfitDescr and enabled:
        return parseOutfitDescr(styleOutfitDescr)
    season = getOutfitType(arenaKind, bonusType)
    seasonOutfitDescr, _ = getter(vehType, season)
    resultOutfit = parseOutfitDescr(seasonOutfitDescr)
    return resultOutfit if resultOutfit else resultOutfit


class OutfitLogEntry(object):
    """Class containing outfit information for log_arena_results. Must be equal to arena_vehicle_outfit.asvc schema"""

    def __init__(self, outfit):
        self.style_cd = cn.StyleItem.makeIntDescr(outfit.styleId) if outfit.styleId else 0
        self.modification_cd = cn.ModificationItem.makeIntDescr(outfit.modifications[0]) if outfit.modifications else 0
        self._paints = CustomizationOutfit.applyAreaBitmaskToDict(outfit.paints)
        self._decals = CustomizationOutfit.applyAreaBitmaskToDict(outfit.decals)
        self._camouflages = CustomizationOutfit.applyAreaBitmaskToDict(outfit.camouflages)
        self.chassis_paint_cd = self.__getPaintCd(ApplyArea.CHASSIS)
        self.hull_paint_cd = self.__getPaintCd(ApplyArea.HULL)
        self.turret_paint_cd = self.__getPaintCd(ApplyArea.TURRET)
        self.gun_paint_cd0 = self.__getPaintCd(ApplyArea.GUN)
        self.gun_paint_cd1 = self.__getPaintCd(ApplyArea.GUN_1)
        self.hull_camouflage_cd = self.__getCamouflageCd(ApplyArea.HULL)
        self.turret_camouflage_cd = self.__getCamouflageCd(ApplyArea.TURRET)
        self.gun_camouflage_cd = self.__getCamouflageCd(ApplyArea.GUN)
        self.hull_decal_cd0 = self.__getDecalCd(ApplyArea.HULL)
        self.hull_decal_cd1 = self.__getDecalCd(ApplyArea.HULL_1)
        self.hull_decal_cd2 = self.__getDecalCd(ApplyArea.HULL_2)
        self.hull_decal_cd3 = self.__getDecalCd(ApplyArea.HULL_3)
        self.turret_decal_cd0 = self.__getDecalCd(ApplyArea.TURRET)
        self.turret_decal_cd1 = self.__getDecalCd(ApplyArea.TURRET_1)
        self.turret_decal_cd2 = self.__getDecalCd(ApplyArea.TURRET_2)
        self.turret_decal_cd3 = self.__getDecalCd(ApplyArea.TURRET_3)

    @staticmethod
    def __getItemCompDescr(storage, area, cdFormatter):
        i = storage.get(area)
        return 0 if not i else cdFormatter(i.id)

    def __getPaintCd(self, area):
        return OutfitLogEntry.__getItemCompDescr(self._paints, area, cn.PaintItem.makeIntDescr)

    def __getCamouflageCd(self, area):
        return OutfitLogEntry.__getItemCompDescr(self._camouflages, area, cn.CamouflageItem.makeIntDescr)

    def __getDecalCd(self, area):
        return OutfitLogEntry.__getItemCompDescr(self._decals, area, cn.DecalItem.makeIntDescr)

    def toDict(self):
        return {k:v for k, v in self.__dict__.iteritems() if not k.startswith('_')}


class NamedVector(defaultdict):
    """Dict with support of fieldwise arithmetic operations:
    d1 +- d2 ->  {d1[i] +- d2[i]}
    """

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
