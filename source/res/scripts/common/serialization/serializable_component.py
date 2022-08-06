# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/serializable_component.py
from cStringIO import StringIO
from collections import OrderedDict
from typing import MutableMapping, Any, TypeVar
import Math
from .definitions import FieldTypes, FieldFlags, FieldType
__all__ = ('SerializableComponent', 'SerializableComponentChildType')

class SerializableComponent(object):
    fields = OrderedDict()
    __slots__ = ()
    customType = None
    preview = False

    def __eq(self, other, ignoreFlags):
        if self.__class__ != other.__class__:
            return False
        if id(self) == id(other):
            return True
        for fname, ftype in self.fields.iteritems():
            if ftype.flags & ignoreFlags:
                continue
            v1 = getattr(self, fname)
            v2 = getattr(other, fname)
            if ftype.type & FieldTypes.TYPED_ARRAY:
                v1 = set(v1)
                v2 = set(v2)
            if v1 != v2:
                return False

        return True

    def __eq__(self, other):
        return self.__eq(other, FieldFlags.DEPRECATED)

    def __ne__(self, other):
        return not self.__eq__(other)

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

    def weak_eq(self, other):
        return self.__eq(other, FieldFlags.DEPRECATED | FieldFlags.WEAK_EQUAL_IGNORED)

    def copy(self):
        value = self.__class__()
        for fname in self.fields.iterkeys():
            setattr(value, fname, getattr(self, fname))

        return value

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

    def to_dict(self):
        res = {}
        for fieldName in self.fields:
            res[fieldName] = getattr(self, fieldName, self.fields[fieldName].default)

        return res


SerializableComponentChildType = TypeVar('SerializableComponentChildType', bound=SerializableComponent)
