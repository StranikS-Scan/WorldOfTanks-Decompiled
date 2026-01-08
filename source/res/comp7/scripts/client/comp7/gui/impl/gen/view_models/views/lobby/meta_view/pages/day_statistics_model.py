# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/day_statistics_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.statistics_model import StatisticsModel

class DayStatisticsModel(StatisticsModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(DayStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getIsQualification(self):
        return self._getBool(14)

    def setIsQualification(self, value):
        self._setBool(14, value)

    def getHasBattles(self):
        return self._getBool(15)

    def setHasBattles(self, value):
        self._setBool(15, value)

    def getRatingPoints(self):
        return self._getNumber(16)

    def setRatingPoints(self, value):
        self._setNumber(16, value)

    def getDiff(self):
        return self._getNumber(17)

    def setDiff(self, value):
        self._setNumber(17, value)

    def getRankInactivityPenalty(self):
        return self._getNumber(18)

    def setRankInactivityPenalty(self, value):
        self._setNumber(18, value)

    def getDivision(self):
        return Division(self._getNumber(19))

    def setDivision(self, value):
        self._setNumber(19, value.value)

    def _initialize(self):
        super(DayStatisticsModel, self)._initialize()
        self._addBoolProperty('isQualification', False)
        self._addBoolProperty('hasBattles', False)
        self._addNumberProperty('ratingPoints', 0)
        self._addNumberProperty('diff', 0)
        self._addNumberProperty('rankInactivityPenalty', 0)
        self._addNumberProperty('division')
