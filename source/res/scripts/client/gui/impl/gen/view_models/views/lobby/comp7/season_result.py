# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/season_result.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel

class SeasonName(Enum):
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class Rank(IntEnum):
    FIRST = 6
    SECOND = 5
    THIRD = 4
    FOURTH = 3
    FIFTH = 2
    SIXTH = 1


class SeasonResult(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SeasonResult, self).__init__(properties=properties, commands=commands)

    def getSeasonName(self):
        return SeasonName(self._getString(0))

    def setSeasonName(self, value):
        self._setString(0, value.value)

    def getRank(self):
        return Rank(self._getNumber(1))

    def setRank(self, value):
        self._setNumber(1, value.value)

    def getSeasonPointsCount(self):
        return self._getNumber(2)

    def setSeasonPointsCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(SeasonResult, self)._initialize()
        self._addStringProperty('seasonName')
        self._addNumberProperty('rank')
        self._addNumberProperty('seasonPointsCount', 0)
