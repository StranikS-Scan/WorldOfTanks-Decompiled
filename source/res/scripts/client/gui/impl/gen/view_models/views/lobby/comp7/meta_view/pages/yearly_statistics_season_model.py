# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/yearly_statistics_season_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonModel

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


class YearlyStatisticsSeasonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(YearlyStatisticsSeasonModel, self).__init__(properties=properties, commands=commands)

    @property
    def season(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonType():
        return SeasonModel

    def getRating(self):
        return self._getNumber(1)

    def setRating(self, value):
        self._setNumber(1, value)

    def getSingleBattlesCount(self):
        return self._getNumber(2)

    def setSingleBattlesCount(self, value):
        self._setNumber(2, value)

    def getSingleBattlesWinRate(self):
        return self._getReal(3)

    def setSingleBattlesWinRate(self, value):
        self._setReal(3, value)

    def getSuperPlatoonBattlesCount(self):
        return self._getNumber(4)

    def setSuperPlatoonBattlesCount(self, value):
        self._setNumber(4, value)

    def getSuperPlatoonBattlesWinRate(self):
        return self._getReal(5)

    def setSuperPlatoonBattlesWinRate(self, value):
        self._setReal(5, value)

    def getHasRankReceived(self):
        return self._getBool(6)

    def setHasRankReceived(self, value):
        self._setBool(6, value)

    def getHasStatisticsCalculated(self):
        return self._getBool(7)

    def setHasStatisticsCalculated(self, value):
        self._setBool(7, value)

    def getRank(self):
        return Rank(self._getNumber(8))

    def setRank(self, value):
        self._setNumber(8, value.value)

    def getDivision(self):
        return Division(self._getNumber(9))

    def setDivision(self, value):
        self._setNumber(9, value.value)

    def _initialize(self):
        super(YearlyStatisticsSeasonModel, self)._initialize()
        self._addViewModelProperty('season', SeasonModel())
        self._addNumberProperty('rating', 0)
        self._addNumberProperty('singleBattlesCount', 0)
        self._addRealProperty('singleBattlesWinRate', 0.0)
        self._addNumberProperty('superPlatoonBattlesCount', 0)
        self._addRealProperty('superPlatoonBattlesWinRate', 0.0)
        self._addBoolProperty('hasRankReceived', False)
        self._addBoolProperty('hasStatisticsCalculated', False)
        self._addNumberProperty('rank')
        self._addNumberProperty('division')
