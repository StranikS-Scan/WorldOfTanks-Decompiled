# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen_utils.py
from typing import Optional, Union
from frameworks.wulf import Resource

class DynAccessor(object):
    __slots__ = ()

    @classmethod
    def dyn(cls, attr, default=Resource.INVALID):
        return getattr(cls, attr, default)

    @classmethod
    def keys(cls):
        return (attr for attr in dir(cls) if attr not in dir(DynAccessor))

    @classmethod
    def values(cls):
        return (getattr(cls, attr) for attr in cls.keys())

    @classmethod
    def items(cls):
        return ((attr, getattr(cls, attr)) for attr in cls.keys())

    @classmethod
    def length(cls):
        return len(tuple(cls.keys()))
