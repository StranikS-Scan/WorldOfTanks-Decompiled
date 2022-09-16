# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/main_widget_tooltip_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import DivisionInfoModel
from gui.impl.gen.view_models.views.lobby.comp7.season_model import SeasonModel

class Rank(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7


class MainWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(MainWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def seasonInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonInfoType():
        return SeasonModel

    @property
    def divisionInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getDivisionInfoType():
        return DivisionInfoModel

    def getRank(self):
        return Rank(self._getNumber(2))

    def setRank(self, value):
        self._setNumber(2, value.value)

    def getCurrentScore(self):
        return self._getNumber(3)

    def setCurrentScore(self, value):
        self._setNumber(3, value)

    def getTopPercentage(self):
        return self._getNumber(4)

    def setTopPercentage(self, value):
        self._setNumber(4, value)

    def getRankInactivityCount(self):
        return self._getNumber(5)

    def setRankInactivityCount(self, value):
        self._setNumber(5, value)

    def getHasRankInactivity(self):
        return self._getBool(6)

    def setHasRankInactivity(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(MainWidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('seasonInfo', SeasonModel())
        self._addViewModelProperty('divisionInfo', DivisionInfoModel())
        self._addNumberProperty('rank')
        self._addNumberProperty('currentScore', 0)
        self._addNumberProperty('topPercentage', 0)
        self._addNumberProperty('rankInactivityCount', -1)
        self._addBoolProperty('hasRankInactivity', False)
