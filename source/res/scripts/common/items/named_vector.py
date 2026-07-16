# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/named_vector.py
from __future__ import absolute_import
from collections import defaultdict
from future.utils import iteritems
__all__ = ('NamedVector',)

class NamedVector(defaultdict):

    def __init__(self, default_factory=int, args=None):
        super(NamedVector, self).__init__(default_factory, args or [])

    def __add__(self, other):
        r = NamedVector(self.default_factory, iteritems(self))
        r += other
        return r

    def __iadd__(self, other):
        for k, v in iteritems(other):
            self[k] += v

        return self

    __radd__ = __add__

    def __sub__(self, other):
        r = NamedVector(self.default_factory, iteritems(self))
        r -= other
        return r

    def __isub__(self, other):
        for k, v in iteritems(other):
            self[k] -= v

        return self

    __rsub__ = __sub__
