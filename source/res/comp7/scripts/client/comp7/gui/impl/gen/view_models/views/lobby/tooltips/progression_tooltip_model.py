# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/progression_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Rank, SeasonName
from frameworks.wulf import ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.division_info_model import DivisionInfoModel
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.progression_qualification_model import ProgressionQualificationModel

class ProgressionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(ProgressionTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def divisionInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getDivisionInfoType():
        return DivisionInfoModel

    @property
    def qualificationModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getQualificationModelType():
        return ProgressionQualificationModel

    def getSeasonName(self):
        return SeasonName(self._getString(2))

    def setSeasonName(self, value):
        self._setString(2, value.value)

    def getRank(self):
        return Rank(self._getNumber(3))

    def setRank(self, value):
        self._setNumber(3, value.value)

    def getCurrentScore(self):
        return self._getNumber(4)

    def setCurrentScore(self, value):
        self._setNumber(4, value)

    def getTopPercentage(self):
        return self._getNumber(5)

    def setTopPercentage(self, value):
        self._setNumber(5, value)

    def getHasRankInactivity(self):
        return self._getBool(6)

    def setHasRankInactivity(self, value):
        self._setBool(6, value)

    def getRankInactivityCount(self):
        return self._getNumber(7)

    def setRankInactivityCount(self, value):
        self._setNumber(7, value)

    def getRankInactivityPointsCount(self):
        return self._getNumber(8)

    def setRankInactivityPointsCount(self, value):
        self._setNumber(8, value)

    def getEarnedRankInactivityPerBattle(self):
        return self._getNumber(9)

    def setEarnedRankInactivityPerBattle(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(ProgressionTooltipModel, self)._initialize()
        self._addViewModelProperty('divisionInfo', DivisionInfoModel())
        self._addViewModelProperty('qualificationModel', ProgressionQualificationModel())
        self._addStringProperty('seasonName')
        self._addNumberProperty('rank')
        self._addNumberProperty('currentScore', 0)
        self._addNumberProperty('topPercentage', 0)
        self._addBoolProperty('hasRankInactivity', False)
        self._addNumberProperty('rankInactivityCount', -1)
        self._addNumberProperty('rankInactivityPointsCount', 0)
        self._addNumberProperty('earnedRankInactivityPerBattle', 0)
