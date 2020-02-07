# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cache.py


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
