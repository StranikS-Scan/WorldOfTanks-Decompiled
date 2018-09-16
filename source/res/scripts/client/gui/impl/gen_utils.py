# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen_utils.py
from typing import Optional, Union
INVALID_RESOURCE_ID = -1

class DynAccessor(object):
    __slots__ = ()

    @classmethod
    def dyn(cls, attr, default=INVALID_RESOURCE_ID):
        return getattr(cls, attr, default)

    @classmethod
    def generator(cls):
        return (getattr(cls, attr) for attr in dir(cls) if not attr.startswith('_'))

    @classmethod
    def length(cls):
        return len(tuple(cls.generator()))
