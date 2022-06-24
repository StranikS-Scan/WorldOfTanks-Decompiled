# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_ranked_widget_model.py
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_rank_model import ModeSelectorRankModel

class ModeSelectorRankedWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(ModeSelectorRankedWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def rankLeft(self):
        return self._getViewModel(1)

    @staticmethod
    def getRankLeftType():
        return ModeSelectorRankModel

    @property
    def rankRight(self):
        return self._getViewModel(2)

    @staticmethod
    def getRankRightType():
        return ModeSelectorRankModel

    def getSteps(self):
        return self._getNumber(3)

    def setSteps(self, value):
        self._setNumber(3, value)

    def getStepsTotal(self):
        return self._getNumber(4)

    def setStepsTotal(self, value):
        self._setNumber(4, value)

    def getHasLeftRank(self):
        return self._getBool(5)

    def setHasLeftRank(self, value):
        self._setBool(5, value)

    def getIsFinal(self):
        return self._getBool(6)

    def setIsFinal(self, value):
        self._setBool(6, value)

    def getBonusBattles(self):
        return self._getNumber(7)

    def setBonusBattles(self, value):
        self._setNumber(7, value)

    def getQualBattles(self):
        return self._getNumber(8)

    def setQualBattles(self, value):
        self._setNumber(8, value)

    def getQualTotalBattles(self):
        return self._getNumber(9)

    def setQualTotalBattles(self, value):
        self._setNumber(9, value)

    def getLeagueID(self):
        return self._getNumber(10)

    def setLeagueID(self, value):
        self._setNumber(10, value)

    def getEfficiency(self):
        return self._getReal(11)

    def setEfficiency(self, value):
        self._setReal(11, value)

    def getEfficiencyDiff(self):
        return self._getReal(12)

    def setEfficiencyDiff(self, value):
        self._setReal(12, value)

    def getIsEfficiencyUnavailable(self):
        return self._getBool(13)

    def setIsEfficiencyUnavailable(self, value):
        self._setBool(13, value)

    def getPosition(self):
        return self._getNumber(14)

    def setPosition(self, value):
        self._setNumber(14, value)

    def getIsPositionUnavailable(self):
        return self._getBool(15)

    def setIsPositionUnavailable(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(ModeSelectorRankedWidgetModel, self)._initialize()
        self._addViewModelProperty('rankLeft', ModeSelectorRankModel())
        self._addViewModelProperty('rankRight', ModeSelectorRankModel())
        self._addNumberProperty('steps', 0)
        self._addNumberProperty('stepsTotal', 0)
        self._addBoolProperty('hasLeftRank', False)
        self._addBoolProperty('isFinal', False)
        self._addNumberProperty('bonusBattles', 0)
        self._addNumberProperty('qualBattles', 0)
        self._addNumberProperty('qualTotalBattles', 0)
        self._addNumberProperty('leagueID', -1)
        self._addRealProperty('efficiency', 0.0)
        self._addRealProperty('efficiencyDiff', 0.0)
        self._addBoolProperty('isEfficiencyUnavailable', False)
        self._addNumberProperty('position', 0)
        self._addBoolProperty('isPositionUnavailable', False)
