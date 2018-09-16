# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/legacy_stuff.py
from constants import IS_CLIENT, IS_CELLAPP, IS_BASEAPP
from soft_exception import SoftException
_IS_LEGACY_STUFF_SUPPORTED = not IS_CLIENT and not IS_CELLAPP and not IS_BASEAPP

class SupportedLegacyStuff(object):
    __slots__ = ()

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, item):
        return hasattr(self, item)

    def __iter__(self):
        raise NotImplementedError

    def keys(self):
        raise NotImplementedError

    def values(self):
        raise NotImplementedError

    def items(self):
        raise NotImplementedError

    def get(self, k, d=None):
        return getattr(self, k, d)

    def copy(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def has_key(self, k):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def pop(self, *args):
        raise NotImplementedError


class NoLegacyStuff(object):
    __slots__ = ()

    def __getitem__(self, item):
        raise SoftException('Operation is not allowed')

    def __setitem__(self, key, value):
        raise SoftException('Operation is not allowed')

    def __contains__(self, item):
        raise SoftException('Operation is not allowed')

    def __iter__(self):
        raise SoftException('Operation is not allowed')

    def keys(self):
        raise SoftException('Operation is not supported')

    def values(self):
        raise SoftException('Operation is not supported')

    def items(self):
        raise SoftException('Operation is not supported')

    def get(self, k, d=None):
        raise SoftException('Operation is not allowed')

    def copy(self):
        raise NotImplementedError

    def clear(self):
        raise SoftException('Operation is not allowed')

    def has_key(self, k):
        raise SoftException('Operation is not allowed')

    def update(self, *args, **kwargs):
        raise SoftException('Operation is not allowed')

    def pop(self, *args):
        raise SoftException('Operation is not allowed')


if _IS_LEGACY_STUFF_SUPPORTED:
    LegacyStuff = SupportedLegacyStuff
else:
    LegacyStuff = NoLegacyStuff
