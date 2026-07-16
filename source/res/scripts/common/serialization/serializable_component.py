# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/serialization/serializable_component.py
from __future__ import absolute_import
from collections import OrderedDict
from future.utils import iteritems
from typing import MutableMapping, Any, TypeVar
import Math
from .definitions import FieldTypes, FieldFlags, FieldType
from py2to3.moves.io import FastStringIO
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
        for fname, ftype in iteritems(self.fields):
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
        for name, ftype in iteritems(self.fields):
            if ftype.flags & FieldFlags.DEPRECATED:
                continue
            v1 = getattr(self, name)
            if isinstance(v1, list):
                v1 = tuple(v1)
            if isinstance(v1, (Math.Vector2, Math.Vector3, Math.Vector4)):
                v1 = tuple(v1)
            result = (result * 31 + hash(v1)) % 18446744073709551616L

        return result

    def __repr__(self):
        buf = FastStringIO()
        self.__writeStr(buf)
        return buf.getvalue()

    def weak_eq(self, other):
        return self.__eq(other, FieldFlags.DEPRECATED | FieldFlags.WEAK_EQUAL_IGNORED)

    def copy(self):
        value = self.__class__()
        for fname in self.fields:
            setattr(value, fname, getattr(self, fname))

        return value

    def isFilled(self):
        return True

    def __writeStr(self, stream):
        stream.write('{')
        i = 0
        n = len(self.fields)
        for name, fieldInfo in iteritems(self.fields):
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
