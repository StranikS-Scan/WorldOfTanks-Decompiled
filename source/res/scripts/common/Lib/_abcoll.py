# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/_abcoll.py
from abc import ABCMeta, abstractmethod
import sys
__all__ = ['Hashable',
 'Iterable',
 'Iterator',
 'Sized',
 'Container',
 'Callable',
 'Set',
 'MutableSet',
 'Mapping',
 'MutableMapping',
 'MappingView',
 'KeysView',
 'ItemsView',
 'ValuesView',
 'Sequence',
 'MutableSequence']

def _hasattr(C, attr):
    try:
        return any((attr in B.__dict__ for B in C.__mro__))
    except AttributeError:
        return hasattr(C, attr)


class Hashable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __hash__(self):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Hashable:
            try:
                for B in C.__mro__:
                    if '__hash__' in B.__dict__:
                        if B.__dict__['__hash__']:
                            return True
                        break

            except AttributeError:
                if getattr(C, '__hash__', None):
                    return True

        return NotImplemented


class Iterable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        while False:
            yield

        return

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Iterable:
            if _hasattr(C, '__iter__'):
                return True
        return NotImplemented


Iterable.register(str)

class Iterator(Iterable):

    @abstractmethod
    def next(self):
        raise StopIteration

    def __iter__(self):
        return self

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Iterator:
            if _hasattr(C, 'next') and _hasattr(C, '__iter__'):
                return True
        return NotImplemented


class Sized:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __len__(self):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Sized:
            if _hasattr(C, '__len__'):
                return True
        return NotImplemented


class Container:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __contains__(self, x):
        return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Container:
            if _hasattr(C, '__contains__'):
                return True
        return NotImplemented


class Callable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, *args, **kwds):
        return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Callable:
            if _hasattr(C, '__call__'):
                return True
        return NotImplemented


class Set(Sized, Iterable, Container):

    def __le__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        if len(self) > len(other):
            return False
        for elem in self:
            if elem not in other:
                return False

        return True

    def __lt__(self, other):
        return NotImplemented if not isinstance(other, Set) else len(self) < len(other) and self.__le__(other)

    def __gt__(self, other):
        return NotImplemented if not isinstance(other, Set) else len(self) > len(other) and self.__ge__(other)

    def __ge__(self, other):
        if not isinstance(other, Set):
            return NotImplemented
        if len(self) < len(other):
            return False
        for elem in other:
            if elem not in self:
                return False

        return True

    def __eq__(self, other):
        return NotImplemented if not isinstance(other, Set) else len(self) == len(other) and self.__le__(other)

    def __ne__(self, other):
        return not self == other

    @classmethod
    def _from_iterable(cls, it):
        return cls(it)

    def __and__(self, other):
        return NotImplemented if not isinstance(other, Iterable) else self._from_iterable((value for value in other if value in self))

    __rand__ = __and__

    def isdisjoint(self, other):
        for value in other:
            if value in self:
                return False

        return True

    def __or__(self, other):
        if not isinstance(other, Iterable):
            return NotImplemented
        chain = (e for s in (self, other) for e in s)
        return self._from_iterable(chain)

    __ror__ = __or__

    def __sub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable((value for value in self if value not in other))

    def __rsub__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self._from_iterable((value for value in other if value not in self))

    def __xor__(self, other):
        if not isinstance(other, Set):
            if not isinstance(other, Iterable):
                return NotImplemented
            other = self._from_iterable(other)
        return self - other | other - self

    __rxor__ = __xor__
    __hash__ = None

    def _hash(self):
        MAX = sys.maxint
        MASK = 2 * MAX + 1
        n = len(self)
        h = 1927868237 * (n + 1)
        h &= MASK
        for x in self:
            hx = hash(x)
            h ^= (hx ^ hx << 16 ^ 89869747) * 3644798167L
            h &= MASK

        h = h * 69069 + 907133923
        h &= MASK
        if h > MAX:
            h -= MASK + 1
        if h == -1:
            h = 590923713
        return h


Set.register(frozenset)

class MutableSet(Set):

    @abstractmethod
    def add(self, value):
        raise NotImplementedError

    @abstractmethod
    def discard(self, value):
        raise NotImplementedError

    def remove(self, value):
        if value not in self:
            raise KeyError(value)
        self.discard(value)

    def pop(self):
        it = iter(self)
        try:
            value = next(it)
        except StopIteration:
            raise KeyError

        self.discard(value)
        return value

    def clear(self):
        try:
            while True:
                self.pop()

        except KeyError:
            pass

    def __ior__(self, it):
        for value in it:
            self.add(value)

        return self

    def __iand__(self, it):
        for value in self - it:
            self.discard(value)

        return self

    def __ixor__(self, it):
        if it is self:
            self.clear()
        else:
            if not isinstance(it, Set):
                it = self._from_iterable(it)
            for value in it:
                if value in self:
                    self.discard(value)
                self.add(value)

        return self

    def __isub__(self, it):
        if it is self:
            self.clear()
        else:
            for value in it:
                self.discard(value)

        return self


MutableSet.register(set)

class Mapping(Sized, Iterable, Container):

    @abstractmethod
    def __getitem__(self, key):
        raise KeyError

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False

        return True

    def iterkeys(self):
        return iter(self)

    def itervalues(self):
        for key in self:
            yield self[key]

    def iteritems(self):
        for key in self:
            yield (key, self[key])

    def keys(self):
        return list(self)

    def items(self):
        return [ (key, self[key]) for key in self ]

    def values(self):
        return [ self[key] for key in self ]

    __hash__ = None

    def __eq__(self, other):
        return NotImplemented if not isinstance(other, Mapping) else dict(self.items()) == dict(other.items())

    def __ne__(self, other):
        return not self == other


class MappingView(Sized):

    def __init__(self, mapping):
        self._mapping = mapping

    def __len__(self):
        return len(self._mapping)

    def __repr__(self):
        return '{0.__class__.__name__}({0._mapping!r})'.format(self)


class KeysView(MappingView, Set):

    @classmethod
    def _from_iterable(self, it):
        return set(it)

    def __contains__(self, key):
        return key in self._mapping

    def __iter__(self):
        for key in self._mapping:
            yield key


KeysView.register(type({}.viewkeys()))

class ItemsView(MappingView, Set):

    @classmethod
    def _from_iterable(self, it):
        return set(it)

    def __contains__(self, item):
        key, value = item
        try:
            v = self._mapping[key]
        except KeyError:
            return False

        return v == value

    def __iter__(self):
        for key in self._mapping:
            yield (key, self._mapping[key])


ItemsView.register(type({}.viewitems()))

class ValuesView(MappingView):

    def __contains__(self, value):
        for key in self._mapping:
            if value == self._mapping[key]:
                return True

        return False

    def __iter__(self):
        for key in self._mapping:
            yield self._mapping[key]


ValuesView.register(type({}.viewvalues()))

class MutableMapping(Mapping):

    @abstractmethod
    def __setitem__(self, key, value):
        raise KeyError

    @abstractmethod
    def __delitem__(self, key):
        raise KeyError

    __marker = object()

    def pop(self, key, default=__marker):
        try:
            value = self[key]
        except KeyError:
            if default is self.__marker:
                raise
            return default

        del self[key]
        return value

    def popitem(self):
        try:
            key = next(iter(self))
        except StopIteration:
            raise KeyError

        value = self[key]
        del self[key]
        return (key, value)

    def clear(self):
        try:
            while True:
                self.popitem()

        except KeyError:
            pass

    def update(*args, **kwds):
        if not args:
            raise TypeError("descriptor 'update' of 'MutableMapping' object needs an argument")
        self = args[0]
        args = args[1:]
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got %d' % len(args))
        if args:
            other = args[0]
            if isinstance(other, Mapping):
                for key in other:
                    self[key] = other[key]

            elif hasattr(other, 'keys'):
                for key in other.keys():
                    self[key] = other[key]

            else:
                for key, value in other:
                    self[key] = value

        for key, value in kwds.items():
            self[key] = value

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default

        return default


MutableMapping.register(dict)

class Sequence(Sized, Iterable, Container):

    @abstractmethod
    def __getitem__(self, index):
        raise IndexError

    def __iter__(self):
        i = 0
        try:
            while True:
                v = self[i]
                yield v
                i += 1

        except IndexError:
            return

    def __contains__(self, value):
        for v in self:
            if v == value:
                return True

        return False

    def __reversed__(self):
        for i in reversed(range(len(self))):
            yield self[i]

    def index(self, value):
        for i, v in enumerate(self):
            if v == value:
                return i

        raise ValueError

    def count(self, value):
        return sum((1 for v in self if v == value))


Sequence.register(tuple)
Sequence.register(basestring)
Sequence.register(buffer)
Sequence.register(xrange)

class MutableSequence(Sequence):

    @abstractmethod
    def __setitem__(self, index, value):
        raise IndexError

    @abstractmethod
    def __delitem__(self, index):
        raise IndexError

    @abstractmethod
    def insert(self, index, value):
        raise IndexError

    def append(self, value):
        self.insert(len(self), value)

    def reverse(self):
        n = len(self)
        for i in range(n // 2):
            self[i], self[n - i - 1] = self[n - i - 1], self[i]

    def extend(self, values):
        for v in values:
            self.append(v)

    def pop(self, index=-1):
        v = self[index]
        del self[index]
        return v

    def remove(self, value):
        del self[self.index(value)]

    def __iadd__(self, values):
        self.extend(values)
        return self


MutableSequence.register(list)
