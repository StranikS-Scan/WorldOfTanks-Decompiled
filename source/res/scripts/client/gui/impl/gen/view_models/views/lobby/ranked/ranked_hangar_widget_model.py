# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_hangar_widget_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.ranked.widget_rank_model import WidgetRankModel

class RankedHangarWidgetModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=15, commands=1):
        super(RankedHangarWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def rankLeft(self):
        return self._getViewModel(0)

    @staticmethod
    def getRankLeftType():
        return WidgetRankModel

    @property
    def rankRight(self):
        return self._getViewModel(1)

    @staticmethod
    def getRankRightType():
        return WidgetRankModel

    def getSteps(self):
        return self._getNumber(2)

    def setSteps(self, value):
        self._setNumber(2, value)

    def getStepsTotal(self):
        return self._getNumber(3)

    def setStepsTotal(self, value):
        self._setNumber(3, value)

    def getHasLeftRank(self):
        return self._getBool(4)

    def setHasLeftRank(self, value):
        self._setBool(4, value)

    def getIsFinal(self):
        return self._getBool(5)

    def setIsFinal(self, value):
        self._setBool(5, value)

    def getBonusBattles(self):
        return self._getNumber(6)

    def setBonusBattles(self, value):
        self._setNumber(6, value)

    def getLeagueID(self):
        return self._getNumber(7)

    def setLeagueID(self, value):
        self._setNumber(7, value)

    def getEfficiency(self):
        return self._getReal(8)

    def setEfficiency(self, value):
        self._setReal(8, value)

    def getEfficiencyDiff(self):
        return self._getReal(9)

    def setEfficiencyDiff(self, value):
        self._setReal(9, value)

    def getIsEfficiencyUnavailable(self):
        return self._getBool(10)

    def setIsEfficiencyUnavailable(self, value):
        self._setBool(10, value)

    def getPosition(self):
        return self._getNumber(11)

    def setPosition(self, value):
        self._setNumber(11, value)

    def getIsPositionUnavailable(self):
        return self._getBool(12)

    def setIsPositionUnavailable(self, value):
        self._setBool(12, value)

    def getMaxRank(self):
        return self._getNumber(13)

    def setMaxRank(self, value):
        self._setNumber(13, value)

    def getBattlesTotal(self):
        return self._getNumber(14)

    def setBattlesTotal(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(RankedHangarWidgetModel, self)._initialize()
        self._addViewModelProperty('rankLeft', WidgetRankModel())
        self._addViewModelProperty('rankRight', WidgetRankModel())
        self._addNumberProperty('steps', 0)
        self._addNumberProperty('stepsTotal', 0)
        self._addBoolProperty('hasLeftRank', False)
        self._addBoolProperty('isFinal', False)
        self._addNumberProperty('bonusBattles', 0)
        self._addNumberProperty('leagueID', -1)
        self._addRealProperty('efficiency', 0.0)
        self._addRealProperty('efficiencyDiff', 0.0)
        self._addBoolProperty('isEfficiencyUnavailable', False)
        self._addNumberProperty('position', 0)
        self._addBoolProperty('isPositionUnavailable', False)
        self._addNumberProperty('maxRank', 0)
        self._addNumberProperty('battlesTotal', 0)
        self.onClick = self._addCommand('onClick')
