# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/map.py
import typing as t
from collections import Mapping
from ..py_object_binder import PyObjectEntity
from ..py_object_wrappers import PyObjectMap, ValueType
if t.TYPE_CHECKING:
    from types import TracebackType
KT = t.TypeVar('KT')
VT = t.TypeVar('VT')

def toValueType(pyType):
    from .. import Array, ViewModel
    if pyType == int:
        return ValueType.NUMBER
    if pyType == bool:
        return ValueType.BOOL
    if pyType == float:
        return ValueType.REAL
    if pyType == Map:
        return ValueType.MAP
    if pyType == Array:
        return ValueType.ARRAY
    if issubclass(pyType, (str, unicode)):
        return ValueType.STRING
    return ValueType.VIEW_MODEL if issubclass(pyType, ViewModel) else ValueType.NONE


class Map(PyObjectEntity, t.MutableMapping[KT, VT]):
    __slots__ = ('__keyType', '__valueType')

    def __init__(self, keyType, valueType):
        self.__keyType = keyType
        self.__valueType = valueType
        super(Map, self).__init__(PyObjectMap.create(toValueType(keyType), toValueType(valueType)))

    def __repr__(self):
        return u'Map({})'.format(dict(self.items()))

    def __str__(self):
        return self.proxy.toString()

    def __len__(self):
        return self.proxy.getSize()

    def __getitem__(self, key):
        if not self.proxy.contains(key):
            raise KeyError('Map key {} is absent'.format(key))
        return self.proxy.getValue(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, key):
        res = self.proxy.removeItem(key)
        if not res:
            raise KeyError(key)

    def __iter__(self):
        for key in self.proxy:
            yield key

    def __contains__(self, key):
        return self.proxy.contains(key)

    def __enter__(self):
        self.proxy.hold()
        return self

    def __exit__(self, excType, _, traceback):
        if excType is None:
            self.proxy.commit()
        else:
            self.proxy.rollback()
        return False

    @property
    def keyType(self):
        return self.__keyType

    @property
    def valueType(self):
        return self.__valueType

    def items(self):
        for key in self.proxy:
            yield (key, self.proxy.getValue(key))

    def values(self):
        for key in self.proxy:
            yield self.proxy.getValue(key)

    def keys(self):
        for key in self.proxy:
            yield key

    def clear(self):
        self.proxy.clear()

    def get(self, key, default=None):
        return default if not self.proxy.contains(key) else self.proxy.getValue(key)

    def set(self, key, value):
        if isinstance(value, PyObjectEntity):
            self.proxy.setValue(key, value.proxy)
        else:
            self.proxy.setValue(key, value)

    def remove(self, key):
        return self.proxy.removeItem(key)

    def update(self, *args, **kwargs):
        if args:
            other = args[0]
            if isinstance(other, Mapping):
                for key, value in other.items():
                    self.set(key, value)

            else:
                try:
                    for key, value in other:
                        self.set(key, value)

                except TypeError:
                    raise TypeError('Argument must be a dictionary or iterable of key-value pairs')

        for key, value in kwargs.items():
            self.set(key, value)
