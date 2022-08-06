# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/component_bin_serializer.py
import varint
from constants import IS_EDITOR
from serialization.definitions import FieldFlags, FieldTypes
from serialization.exceptions import SerializationException
__all__ = ('ComponentBinSerializer',)

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
            if IS_EDITOR and fieldInfo.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
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
