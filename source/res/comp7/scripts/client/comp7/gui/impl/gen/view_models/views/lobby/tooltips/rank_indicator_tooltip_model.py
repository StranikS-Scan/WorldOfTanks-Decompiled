# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/rank_indicator_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank, SeasonName, StatisticsMode
from frameworks.wulf import ViewModel

class RankIndicatorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(RankIndicatorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStatisticsMode(self):
        return StatisticsMode(self._getNumber(0))

    def setStatisticsMode(self, value):
        self._setNumber(0, value.value)

    def getSeasonName(self):
        return SeasonName(self._getString(1))

    def setSeasonName(self, value):
        self._setString(1, value.value)

    def getRank(self):
        return Rank(self._getNumber(2))

    def setRank(self, value):
        self._setNumber(2, value.value)

    def getDivision(self):
        return Division(self._getNumber(3))

    def setDivision(self, value):
        self._setNumber(3, value.value)

    def getRatingPoints(self):
        return self._getNumber(4)

    def setRatingPoints(self, value):
        self._setNumber(4, value)

    def getDiff(self):
        return self._getNumber(5)

    def setDiff(self, value):
        self._setNumber(5, value)

    def getMaxAchievedRatingPoints(self):
        return self._getNumber(6)

    def setMaxAchievedRatingPoints(self, value):
        self._setNumber(6, value)

    def getDayOfMaxRatingIndex(self):
        return self._getNumber(7)

    def setDayOfMaxRatingIndex(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(RankIndicatorTooltipModel, self)._initialize()
        self._addNumberProperty('statisticsMode')
        self._addStringProperty('seasonName')
        self._addNumberProperty('rank')
        self._addNumberProperty('division')
        self._addNumberProperty('ratingPoints', 0)
        self._addNumberProperty('diff', 0)
        self._addNumberProperty('maxAchievedRatingPoints', 0)
        self._addNumberProperty('dayOfMaxRatingIndex', 0)
