# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/abc.py
import types
from _weakrefset import WeakSet

class _C:
    pass


_InstanceType = type(_C())

def abstractmethod(funcobj):
    funcobj.__isabstractmethod__ = True
    return funcobj


class abstractproperty(property):
    __isabstractmethod__ = True


class ABCMeta(type):
    _abc_invalidation_counter = 0

    def __new__(mcls, name, bases, namespace):
        cls = super(ABCMeta, mcls).__new__(mcls, name, bases, namespace)
        abstracts = set((name for name, value in namespace.items() if getattr(value, '__isabstractmethod__', False)))
        for base in bases:
            for name in getattr(base, '__abstractmethods__', set()):
                value = getattr(cls, name, None)
                if getattr(value, '__isabstractmethod__', False):
                    abstracts.add(name)

        cls.__abstractmethods__ = frozenset(abstracts)
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        return cls

    def register(cls, subclass):
        if not isinstance(subclass, (type, types.ClassType)):
            raise TypeError('Can only register classes')
        if issubclass(subclass, cls):
            return
        if issubclass(cls, subclass):
            raise RuntimeError('Refusing to create an inheritance cycle')
        cls._abc_registry.add(subclass)
        ABCMeta._abc_invalidation_counter += 1

    def _dump_registry(cls, file=None):
        print >> file, 'Class: %s.%s' % (cls.__module__, cls.__name__)
        print >> file, 'Inv.counter: %s' % ABCMeta._abc_invalidation_counter
        for name in sorted(cls.__dict__.keys()):
            if name.startswith('_abc_'):
                value = getattr(cls, name)
                print >> file, '%s: %r' % (name, value)

    def __instancecheck__(cls, instance):
        subclass = getattr(instance, '__class__', None)
        if subclass is not None and subclass in cls._abc_cache:
            return True
        subtype = type(instance)
        if subtype is _InstanceType:
            subtype = subclass
        if subtype is subclass or subclass is None:
            if cls._abc_negative_cache_version == ABCMeta._abc_invalidation_counter and subtype in cls._abc_negative_cache:
                return False
            return cls.__subclasscheck__(subtype)
        else:
            return cls.__subclasscheck__(subclass) or cls.__subclasscheck__(subtype)

    def __subclasscheck__(cls, subclass):
        if subclass in cls._abc_cache:
            return True
        if cls._abc_negative_cache_version < ABCMeta._abc_invalidation_counter:
            cls._abc_negative_cache = WeakSet()
            cls._abc_negative_cache_version = ABCMeta._abc_invalidation_counter
        elif subclass in cls._abc_negative_cache:
            return False
        ok = cls.__subclasshook__(subclass)
        if ok is not NotImplemented:
            if ok:
                cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        if cls in getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            return True
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True

        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True

        cls._abc_negative_cache.add(subclass)
        return False
