# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/ny_components.py
import typing
from collections import namedtuple

class SlotDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        try:
            return self.__cfg[name]
        except KeyError:
            raise AttributeError

    def __cmp__(self, other):
        return self.id - other.id


class LevelDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        try:
            return self.__cfg[name]
        except KeyError:
            raise AttributeError


VariadicDiscount = namedtuple('VariadicDiscount', ['id', 'goodiesRange', 'level'])
