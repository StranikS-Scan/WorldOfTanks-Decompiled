# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/sets.py
from itertools import ifilter, ifilterfalse
__all__ = ['BaseSet', 'Set', 'ImmutableSet']
import warnings
warnings.warn('the sets module is deprecated', DeprecationWarning, stacklevel=2)

class BaseSet(object):
    __slots__ = ['_data']

    def __init__(self):
        if self.__class__ is BaseSet:
            raise TypeError, 'BaseSet is an abstract class.  Use Set or ImmutableSet.'

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return self._repr()

    __str__ = __repr__

    def _repr(self, sorted=False):
        elements = self._data.keys()
        if sorted:
            elements.sort()
        return '%s(%r)' % (self.__class__.__name__, elements)

    def __iter__(self):
        return self._data.iterkeys()

    def __cmp__(self, other):
        raise TypeError, "can't compare sets using cmp()"

    def __eq__(self, other):
        if isinstance(other, BaseSet):
            return self._data == other._data
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, BaseSet):
            return self._data != other._data
        else:
            return True

    def copy(self):
        result = self.__class__()
        result._data.update(self._data)
        return result

    __copy__ = copy

    def __deepcopy__(self, memo):
        from copy import deepcopy
        result = self.__class__()
        memo[id(self)] = result
        data = result._data
        value = True
        for elt in self:
            data[deepcopy(elt, memo)] = value

        return result

    def __or__(self, other):
        return NotImplemented if not isinstance(other, BaseSet) else self.union(other)

    def union(self, other):
        result = self.__class__(self)
        result._update(other)
        return result

    def __and__(self, other):
        return NotImplemented if not isinstance(other, BaseSet) else self.intersection(other)

    def intersection(self, other):
        if not isinstance(other, BaseSet):
            other = Set(other)
        if len(self) <= len(other):
            little, big = self, other
        else:
            little, big = other, self
        common = ifilter(big._data.__contains__, little)
        return self.__class__(common)

    def __xor__(self, other):
        return NotImplemented if not isinstance(other, BaseSet) else self.symmetric_difference(other)

    def symmetric_difference(self, other):
        result = self.__class__()
        data = result._data
        value = True
        selfdata = self._data
        try:
            otherdata = other._data
        except AttributeError:
            otherdata = Set(other)._data

        for elt in ifilterfalse(otherdata.__contains__, selfdata):
            data[elt] = value

        for elt in ifilterfalse(selfdata.__contains__, otherdata):
            data[elt] = value

        return result

    def __sub__(self, other):
        return NotImplemented if not isinstance(other, BaseSet) else self.difference(other)

    def difference(self, other):
        result = self.__class__()
        data = result._data
        try:
            otherdata = other._data
        except AttributeError:
            otherdata = Set(other)._data

        value = True
        for elt in ifilterfalse(otherdata.__contains__, self):
            data[elt] = value

        return result

    def __contains__(self, element):
        try:
            return element in self._data
        except TypeError:
            transform = getattr(element, '__as_temporarily_immutable__', None)
            if transform is None:
                raise
            return transform() in self._data

        return

    def issubset(self, other):
        self._binary_sanity_check(other)
        if len(self) > len(other):
            return False
        for elt in ifilterfalse(other._data.__contains__, self):
            return False

        return True

    def issuperset(self, other):
        self._binary_sanity_check(other)
        if len(self) < len(other):
            return False
        for elt in ifilterfalse(self._data.__contains__, other):
            return False

        return True

    __le__ = issubset
    __ge__ = issuperset

    def __lt__(self, other):
        self._binary_sanity_check(other)
        return len(self) < len(other) and self.issubset(other)

    def __gt__(self, other):
        self._binary_sanity_check(other)
        return len(self) > len(other) and self.issuperset(other)

    __hash__ = None

    def _binary_sanity_check(self, other):
        if not isinstance(other, BaseSet):
            raise TypeError, 'Binary operation only permitted between sets'

    def _compute_hash(self):
        result = 0
        for elt in self:
            result ^= hash(elt)

        return result

    def _update(self, iterable):
        data = self._data
        if isinstance(iterable, BaseSet):
            data.update(iterable._data)
            return
        else:
            value = True
            if type(iterable) in (list, tuple, xrange):
                it = iter(iterable)
                while True:
                    try:
                        for element in it:
                            data[element] = value

                        return
                    except TypeError:
                        transform = getattr(element, '__as_immutable__', None)
                        if transform is None:
                            raise
                        data[transform()] = value

            else:
                for element in iterable:
                    try:
                        data[element] = value
                    except TypeError:
                        transform = getattr(element, '__as_immutable__', None)
                        if transform is None:
                            raise
                        data[transform()] = value

            return


class ImmutableSet(BaseSet):
    __slots__ = ['_hashcode']

    def __init__(self, iterable=None):
        self._hashcode = None
        self._data = {}
        if iterable is not None:
            self._update(iterable)
        return

    def __hash__(self):
        if self._hashcode is None:
            self._hashcode = self._compute_hash()
        return self._hashcode

    def __getstate__(self):
        return (self._data, self._hashcode)

    def __setstate__(self, state):
        self._data, self._hashcode = state


class Set(BaseSet):
    __slots__ = []

    def __init__(self, iterable=None):
        self._data = {}
        if iterable is not None:
            self._update(iterable)
        return

    def __getstate__(self):
        return (self._data,)

    def __setstate__(self, data):
        self._data = data

    def __ior__(self, other):
        self._binary_sanity_check(other)
        self._data.update(other._data)
        return self

    def union_update(self, other):
        self._update(other)

    def __iand__(self, other):
        self._binary_sanity_check(other)
        self._data = (self & other)._data
        return self

    def intersection_update(self, other):
        if isinstance(other, BaseSet):
            self &= other
        else:
            self._data = self.intersection(other)._data

    def __ixor__(self, other):
        self._binary_sanity_check(other)
        self.symmetric_difference_update(other)
        return self

    def symmetric_difference_update(self, other):
        data = self._data
        value = True
        if not isinstance(other, BaseSet):
            other = Set(other)
        if self is other:
            self.clear()
        for elt in other:
            if elt in data:
                del data[elt]
            data[elt] = value

    def __isub__(self, other):
        self._binary_sanity_check(other)
        self.difference_update(other)
        return self

    def difference_update(self, other):
        data = self._data
        if not isinstance(other, BaseSet):
            other = Set(other)
        if self is other:
            self.clear()
        for elt in ifilter(data.__contains__, other):
            del data[elt]

    def update(self, iterable):
        self._update(iterable)

    def clear(self):
        self._data.clear()

    def add(self, element):
        try:
            self._data[element] = True
        except TypeError:
            transform = getattr(element, '__as_immutable__', None)
            if transform is None:
                raise
            self._data[transform()] = True

        return

    def remove(self, element):
        try:
            del self._data[element]
        except TypeError:
            transform = getattr(element, '__as_temporarily_immutable__', None)
            if transform is None:
                raise
            del self._data[transform()]

        return

    def discard(self, element):
        try:
            self.remove(element)
        except KeyError:
            pass

    def pop(self):
        return self._data.popitem()[0]

    def __as_immutable__(self):
        return ImmutableSet(self)

    def __as_temporarily_immutable__(self):
        return _TemporarilyImmutableSet(self)


class _TemporarilyImmutableSet(BaseSet):

    def __init__(self, set):
        self._set = set
        self._data = set._data

    def __hash__(self):
        return self._set._compute_hash()
