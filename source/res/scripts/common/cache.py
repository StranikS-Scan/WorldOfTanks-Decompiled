# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cache.py
from functools import wraps
from wotdecorators import singleton

class cached_property(object):

    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        else:
            res = instance.__dict__[self.name] = self.func(instance)
            return res


class class_cached_property(object):

    def __init__(self, func):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = func.__name__

    def __get__(self, owner, cls):
        result = self.func(cls)
        setattr(cls, self.name, result)
        return result


@singleton
class NotMemoized(object):
    pass


def memoized_method(method=None, isClassCache=False, external=None, key=None):
    if method is None:
        return lambda m: memoized_method(method=m, isClassCache=isClassCache, external=external, key=key)
    else:
        external = external() if callable(external) else external

        @wraps(method)
        def wrapper(this, *args):
            storage = external
            if storage is None:
                storage = this.__class__ if isClassCache else this
                if not hasattr(storage, '__cache__'):
                    storage.__cache__ = {}
                storage = storage.__cache__.setdefault(method.__name__, {})
            skey = key(*args) if callable(key) else args
            result = storage.get(skey, NotMemoized)
            if result is NotMemoized:
                storage[skey] = result = method(this, *args)
            return result

        return wrapper
