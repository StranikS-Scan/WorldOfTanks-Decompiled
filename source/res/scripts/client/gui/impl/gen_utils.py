# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen_utils.py
from __future__ import absolute_import
from typing import Optional, Tuple, Iterator
INVALID_RES_ID = -1

class DynAccessor(object):
    __slots__ = ('__resId',)

    def __init__(self, value=0):
        self.__resId = value

    def __call__(self):
        return self.__resId

    def __bool__(self):
        return self.__resId >= 0

    __nonzero__ = __bool__

    def dyn(self, attr, default=None):
        return getattr(self, attr, default or _g_invalid)

    def num(self, attr, default=None):
        return getattr(self, 'c_{}'.format(attr), default or _g_invalid)

    def keys(self):
        for attr in dir(self):
            if attr not in dir(DynAccessor) and not attr.startswith('_'):
                yield attr

    def values(self):
        for attr in self.keys():
            yield getattr(self, attr)

    def items(self):
        for attr in self.keys():
            yield (attr, getattr(self, attr))

    def length(self):
        return sum((1 for _ in self.keys()))

    def exists(self):
        return self.__resId > 0

    def isValid(self):
        return True


class _InvalidDynAccessor(DynAccessor):

    def keys(self):
        return iter(())

    def isValid(self):
        return False


_g_invalid = _InvalidDynAccessor(INVALID_RES_ID)
