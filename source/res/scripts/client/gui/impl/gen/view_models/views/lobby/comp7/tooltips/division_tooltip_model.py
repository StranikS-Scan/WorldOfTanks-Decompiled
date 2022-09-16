# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/division_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Rank(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7


class Division(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3


class DivisionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DivisionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return Rank(self._getNumber(0))

    def setRank(self, value):
        self._setNumber(0, value.value)

    def getDivision(self):
        return Division(self._getNumber(1))

    def setDivision(self, value):
        self._setNumber(1, value.value)

    def getFrom(self):
        return self._getNumber(2)

    def setFrom(self, value):
        self._setNumber(2, value)

    def getTo(self):
        return self._getNumber(3)

    def setTo(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(DivisionTooltipModel, self)._initialize()
        self._addNumberProperty('rank')
        self._addNumberProperty('division')
        self._addNumberProperty('from', 800)
        self._addNumberProperty('to', 900)
