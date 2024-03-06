# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/data_structures.py
from collections import defaultdict
from soft_exception import SoftException

class DictObj(dict):

    def __getattr__(self, name):
        return self[name] if name in self else None

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]


class OrderedSet(set):

    def __init__(self, d=None):
        set.__init__(self)
        self._list = []
        if d is not None:
            self.update(d)
        return

    def add(self, element):
        if element not in self:
            self._list.append(element)
        set.add(self, element)

    def remove(self, element):
        set.remove(self, element)
        self._list.remove(element)

    def insert(self, pos, element):
        if element not in self:
            self._list.insert(pos, element)
        set.add(self, element)

    def discard(self, element):
        if element in self:
            self._list.remove(element)
            set.remove(self, element)

    def clear(self):
        set.clear(self)
        self._list = []

    def __getitem__(self, key):
        return self._list[key]

    def __iter__(self):
        return iter(self._list)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._list)

    __str__ = __repr__

    def update(self, iterable):
        add = self.add
        for i in iterable:
            add(i)

        return self

    __ior__ = update

    def union(self, other):
        result = self.__class__(self)
        result.update(other)
        return result

    __or__ = union

    def intersection(self, other):
        other = set(other)
        return self.__class__((a for a in self if a in other))

    __and__ = intersection

    def symmetric_difference(self, other):
        other = set(other)
        result = self.__class__((a for a in self if a not in other))
        result.update((a for a in other if a not in self))
        return result

    __xor__ = symmetric_difference

    def difference(self, other):
        other = set(other)
        return self.__class__((a for a in self if a not in other))

    __sub__ = difference

    def intersection_update(self, other):
        other = set(other)
        set.intersection_update(self, other)
        self._list = [ a for a in self._list if a in other ]
        return self

    __iand__ = intersection_update

    def symmetric_difference_update(self, other):
        set.symmetric_difference_update(self, other)
        self._list = [ a for a in self._list if a in self ]
        self._list += [ a for a in other._list if a in self ]
        return self

    __ixor__ = symmetric_difference_update

    def difference_update(self, other):
        set.difference_update(self, other)
        self._list = [ a for a in self._list if a in self ]
        return self

    __isub__ = difference_update


class ParametrisedFactoryDefaultDict(defaultdict):

    def __missing__(self, key):
        self[key] = value = self.default_factory(key)
        return value


class DynamicFactorCollectorKeyError(SoftException):
    pass


class VariableState(object):
    __slots__ = ('_description',)

    def __init__(self, description='unknown'):
        self._description = description

    def __bool__(self):
        return False

    __nonzero__ = __bool__

    def __copy__(self):
        return self

    def __deepcopy__(self, _):
        return self

    def __repr__(self):
        return '<state.{}>'.format(self._description)
