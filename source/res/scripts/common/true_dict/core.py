# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/true_dict/core.py
from __future__ import absolute_import
import itertools
from builtins import zip
from future.utils import iteritems, PY2
try:
    from collections.abc import KeysView, ValuesView, ItemsView
except ImportError:
    from collections import KeysView, ValuesView, ItemsView

from typing import Any, Dict, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar, Union
KT = TypeVar('KT')
VT = TypeVar('VT')

class TrueDict(Generic[KT, VT]):
    __hash__ = None

    def __init__(self, keys, values):
        self.__keys = keys
        self.__values = values

    def __setitem__(self, key, value):
        i = self.__findIndex(key)
        if i >= 0:
            self.__values[i] = value
        else:
            self.__keys.append(key)
            self.__values.append(value)

    def __findIndex(self, key):
        try:
            return self.__keys.index(key)
        except ValueError:
            return -1

    def __getitem__(self, key):
        i = self.__findIndex(key)
        if i >= 0:
            return self.__values[i]
        raise KeyError(key)

    def __delitem__(self, key):
        i = self.__findIndex(key)
        if i >= 0:
            del self.__keys[i]
            del self.__values[i]
        else:
            raise KeyError(key)

    def __contains__(self, key):
        return self.__findIndex(key) >= 0

    def __len__(self):
        return len(self.__keys)

    def __iter__(self):
        return iter(self.__keys)

    def __repr__(self):
        return repr(self.toDict())

    def __eq__(self, other):
        if isinstance(other, (TrueDict, dict)):
            if len(self) != len(other):
                return False
            if isinstance(other, TrueDict):
                other = other.toDict()
            for k, v in zip(self.__keys, self.__values):
                if k not in other:
                    return False
                if v != other[k]:
                    return False

            return True
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    @classmethod
    def fromDict(cls, other=None):
        res = TrueDict([], [])
        res.update(other)
        return res

    def toDict(self):
        return dict(zip(self.__keys, self.__values))

    def get(self, key, default=None):
        i = self.__findIndex(key)
        return self.__values[i] if i >= 0 else default

    def keys(self):
        return list(self.__keys) if PY2 else KeysView(self)

    def values(self):
        return list(self.__values) if PY2 else ValuesView(self)

    def items(self):
        return list(zip(self.__keys, self.__values)) if PY2 else ItemsView(self)

    def positionalSlice(self, start, end):
        return (self.__keys[start:end], self.__values[start:end])

    def pop(self, key, *args):
        if len(args) > 1:
            raise TypeError('pop expected at most 2 arguments, got %d' % (1 + len(args)))
        i = self.__findIndex(key)
        if i >= 0:
            self.__keys.pop(i)
            return self.__values.pop(i)
        if args:
            return args[0]
        raise KeyError(key)

    def popitem(self):
        if not self.__keys:
            raise KeyError('popitem(): dict is empty')
        k = self.__keys.pop(0)
        v = self.__values.pop(0)
        return (k, v)

    def setdefault(self, key, default=None):
        i = self.__findIndex(key)
        if i >= 0:
            return self.__values[i]
        self.__keys.append(key)
        self.__values.append(default)
        return default

    def update(self, other=None, **kwargs):
        iterables = []
        if other is not None:
            if isinstance(other, TrueDict):
                iterables.append(other.iter_items())
            elif isinstance(other, dict):
                iterables.append(iteritems(other))
            else:
                iterables.append(list(other))
        if kwargs:
            iterables.append(iteritems(kwargs))
        self.__updatePairs(itertools.chain(*iterables))
        return

    def __updatePairs(self, pairs):
        index = {k:i for i, k in enumerate(self.__keys)}
        for k, v in pairs:
            i = index.get(k, -1)
            if i >= 0:
                self.__values[i] = v
            index[k] = len(self.__keys)
            self.__keys.append(k)
            self.__values.append(v)

    def clear(self):
        del self.__keys[:]
        del self.__values[:]

    def copy(self):
        return TrueDict(list(self.__keys), list(self.__values))

    def iter_keys(self):
        return iter(self.__keys)

    def iter_values(self):
        return iter(self.__values)

    def iter_items(self):
        return iter(zip(self.__keys, self.__values))

    if PY2:

        def has_key(self, key):
            return key in self

        iterkeys = iter_keys
        itervalues = iter_values
        iteritems = iter_items
