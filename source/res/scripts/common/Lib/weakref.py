# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/weakref.py
import UserDict
from _weakref import getweakrefcount, getweakrefs, ref, proxy, CallableProxyType, ProxyType, ReferenceType
from _weakrefset import WeakSet, _IterationGuard
from exceptions import ReferenceError
ProxyTypes = (ProxyType, CallableProxyType)
__all__ = ['ref',
 'proxy',
 'getweakrefcount',
 'getweakrefs',
 'WeakKeyDictionary',
 'ReferenceError',
 'ReferenceType',
 'ProxyType',
 'CallableProxyType',
 'ProxyTypes',
 'WeakValueDictionary',
 'WeakSet']

class WeakValueDictionary(UserDict.UserDict):

    def __init__(self, *args, **kw):

        def remove(wr, selfref=ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(wr.key)
                else:
                    del self.data[wr.key]
            return

        self._remove = remove
        self._pending_removals = []
        self._iterating = set()
        UserDict.UserDict.__init__(self, *args, **kw)

    def _commit_removals(self):
        l = self._pending_removals
        d = self.data
        while l:
            del d[l.pop()]

    def __getitem__(self, key):
        o = self.data[key]()
        if o is None:
            raise KeyError, key
        else:
            return o
        return

    def __delitem__(self, key):
        if self._pending_removals:
            self._commit_removals()
        del self.data[key]

    def __contains__(self, key):
        try:
            o = self.data[key]()
        except KeyError:
            return False

        return o is not None

    def has_key(self, key):
        try:
            o = self.data[key]()
        except KeyError:
            return False

        return o is not None

    def __repr__(self):
        return '<WeakValueDictionary at %s>' % id(self)

    def __setitem__(self, key, value):
        if self._pending_removals:
            self._commit_removals()
        self.data[key] = KeyedRef(value, self._remove, key)

    def clear(self):
        if self._pending_removals:
            self._commit_removals()
        self.data.clear()

    def copy(self):
        new = WeakValueDictionary()
        for key, wr in self.data.items():
            o = wr()
            if o is not None:
                new[key] = o

        return new

    __copy__ = copy

    def __deepcopy__(self, memo):
        from copy import deepcopy
        new = self.__class__()
        for key, wr in self.data.items():
            o = wr()
            if o is not None:
                new[deepcopy(key, memo)] = o

        return new

    def get(self, key, default=None):
        try:
            wr = self.data[key]
        except KeyError:
            return default

        o = wr()
        if o is None:
            return default
        else:
            return o
            return

    def items(self):
        L = []
        for key, wr in self.data.items():
            o = wr()
            if o is not None:
                L.append((key, o))

        return L

    def iteritems(self):
        with _IterationGuard(self):
            for wr in self.data.itervalues():
                value = wr()
                if value is not None:
                    yield (wr.key, value)

        return

    def iterkeys(self):
        with _IterationGuard(self):
            for k in self.data.iterkeys():
                yield k

    __iter__ = iterkeys

    def itervaluerefs(self):
        with _IterationGuard(self):
            for wr in self.data.itervalues():
                yield wr

    def itervalues(self):
        with _IterationGuard(self):
            for wr in self.data.itervalues():
                obj = wr()
                if obj is not None:
                    yield obj

        return

    def popitem(self):
        if self._pending_removals:
            self._commit_removals()
        while 1:
            key, wr = self.data.popitem()
            o = wr()
            if o is not None:
                return (key, o)

        return

    def pop(self, key, *args):
        if self._pending_removals:
            self._commit_removals()
        try:
            o = self.data.pop(key)()
        except KeyError:
            if args:
                return args[0]
            raise

        if o is None:
            raise KeyError, key
        else:
            return o
        return

    def setdefault(self, key, default=None):
        try:
            wr = self.data[key]
        except KeyError:
            if self._pending_removals:
                self._commit_removals()
            self.data[key] = KeyedRef(default, self._remove, key)
            return default

        return wr()

    def update(self, dict=None, **kwargs):
        if self._pending_removals:
            self._commit_removals()
        d = self.data
        if dict is not None:
            if not hasattr(dict, 'items'):
                dict = type({})(dict)
            for key, o in dict.items():
                d[key] = KeyedRef(o, self._remove, key)

        if len(kwargs):
            self.update(kwargs)
        return

    def valuerefs(self):
        return self.data.values()

    def values(self):
        L = []
        for wr in self.data.values():
            o = wr()
            if o is not None:
                L.append(o)

        return L


class KeyedRef(ref):
    __slots__ = ('key',)

    def __new__(type, ob, callback, key):
        self = ref.__new__(type, ob, callback)
        self.key = key
        return self

    def __init__(self, ob, callback, key):
        super(KeyedRef, self).__init__(ob, callback)


class WeakKeyDictionary(UserDict.UserDict):

    def __init__(self, dict=None):
        self.data = {}

        def remove(k, selfref=ref(self)):
            self = selfref()
            if self is not None:
                if self._iterating:
                    self._pending_removals.append(k)
                else:
                    del self.data[k]
            return

        self._remove = remove
        self._pending_removals = []
        self._iterating = set()
        if dict is not None:
            self.update(dict)
        return

    def _commit_removals(self):
        l = self._pending_removals
        d = self.data
        while l:
            try:
                del d[l.pop()]
            except KeyError:
                pass

    def __delitem__(self, key):
        del self.data[ref(key)]

    def __getitem__(self, key):
        return self.data[ref(key)]

    def __repr__(self):
        return '<WeakKeyDictionary at %s>' % id(self)

    def __setitem__(self, key, value):
        self.data[ref(key, self._remove)] = value

    def copy(self):
        new = WeakKeyDictionary()
        for key, value in self.data.items():
            o = key()
            if o is not None:
                new[o] = value

        return new

    __copy__ = copy

    def __deepcopy__(self, memo):
        from copy import deepcopy
        new = self.__class__()
        for key, value in self.data.items():
            o = key()
            if o is not None:
                new[o] = deepcopy(value, memo)

        return new

    def get(self, key, default=None):
        return self.data.get(ref(key), default)

    def has_key(self, key):
        try:
            wr = ref(key)
        except TypeError:
            return 0

        return wr in self.data

    def __contains__(self, key):
        try:
            wr = ref(key)
        except TypeError:
            return 0

        return wr in self.data

    def items(self):
        L = []
        for key, value in self.data.items():
            o = key()
            if o is not None:
                L.append((o, value))

        return L

    def iteritems(self):
        with _IterationGuard(self):
            for wr, value in self.data.iteritems():
                key = wr()
                if key is not None:
                    yield (key, value)

        return

    def iterkeyrefs(self):
        with _IterationGuard(self):
            for wr in self.data.iterkeys():
                yield wr

    def iterkeys(self):
        with _IterationGuard(self):
            for wr in self.data.iterkeys():
                obj = wr()
                if obj is not None:
                    yield obj

        return

    __iter__ = iterkeys

    def itervalues(self):
        with _IterationGuard(self):
            for value in self.data.itervalues():
                yield value

    def keyrefs(self):
        return self.data.keys()

    def keys(self):
        L = []
        for wr in self.data.keys():
            o = wr()
            if o is not None:
                L.append(o)

        return L

    def popitem(self):
        while 1:
            key, value = self.data.popitem()
            o = key()
            if o is not None:
                return (o, value)

        return

    def pop(self, key, *args):
        return self.data.pop(ref(key), *args)

    def setdefault(self, key, default=None):
        return self.data.setdefault(ref(key, self._remove), default)

    def update(self, dict=None, **kwargs):
        d = self.data
        if dict is not None:
            if not hasattr(dict, 'items'):
                dict = type({})(dict)
            for key, value in dict.items():
                d[ref(key, self._remove)] = value

        if len(kwargs):
            self.update(kwargs)
        return
