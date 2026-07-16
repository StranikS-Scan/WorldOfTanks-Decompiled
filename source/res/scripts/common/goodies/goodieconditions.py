# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/GoodieConditions.py
from __future__ import absolute_import
from typing import TypeVar

class Condition(object):

    def check(self, other):
        return self == other

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    __hash__ = None


class MaxVehicleLevel(Condition):

    def __init__(self, level):
        self.level = level

    def __lt__(self, other):
        return self.level < other.level


GoodieConditionType = TypeVar('GoodieConditionType', bound=Condition)
