# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/platoon_rank_data.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class Division(IntEnum):
    A = 1
    B = 2
    C = 3
    D = 4
    E = 5


class PlatoonRankData(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PlatoonRankData, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return Rank(self._getNumber(0))

    def setRank(self, value):
        self._setNumber(0, value.value)

    def getDivision(self):
        return Division(self._getNumber(1))

    def setDivision(self, value):
        self._setNumber(1, value.value)

    def getScore(self):
        return self._getNumber(2)

    def setScore(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PlatoonRankData, self)._initialize()
        self._addNumberProperty('rank')
        self._addNumberProperty('division')
        self._addNumberProperty('score', 0)
