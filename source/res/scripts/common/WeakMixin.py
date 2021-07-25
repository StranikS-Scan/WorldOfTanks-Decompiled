# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/WeakMixin.py
import new
import weakref
from inspect import getmodule

class Tapped(object):
    __slots__ = ()

    def tap(self, *appliers, **props):
        for applier in appliers:
            if callable(applier):
                applier(self)

        for p, v in props.iteritems():
            try:
                setattr(self, p, v)
            except (AttributeError, TypeError):
                pass

        return self


class WeakMixin(object):

    def __new__(cls, src, *args, **kwargs):
        kls = None
        srcKlass = src.__class__
        for k in cls.__subclasses__():
            if issubclass(k, srcKlass):
                kls = k
                break

        if not kls:
            mixinName = '_{}_weakMixin'.format(srcKlass.__name__)
            module = getmodule(cls)
            kls = new.classobj(mixinName, (cls, srcKlass), {})
            if module is not None:
                setattr(module, mixinName, kls)
        obj = object.__new__(kls)
        obj.__target__ = weakref.proxy(src)
        return obj

    def __init__(self, src, *args, **kwargs):
        pass

    def __getattribute__(self, name):
        ogetattribute = object.__getattribute__
        try:
            return ogetattribute(self, name)
        except AttributeError:
            return self.__target__.__getattribute__(name)
