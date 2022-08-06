# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/component_bin_deserializer.py
from cStringIO import StringIO
from typing import Dict, Type
import varint
from constants import IS_EDITOR
from serialization.definitions import FieldFlags, FieldTypes
from serialization.exceptions import SerializationException, FoundItemException
from serialization.serializable_component import SerializableComponent
__all__ = ('ComponentBinDeserializer',)

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
            if IS_EDITOR and t.flags & FieldFlags.SAVE_AS_EDITOR_ONLY:
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
