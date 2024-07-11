# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/progression_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ProgressionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ProgressionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getProgressionLevel(self):
        return self._getNumber(0)

    def setProgressionLevel(self, value):
        self._setNumber(0, value)

    def getCurrentPoints(self):
        return self._getNumber(1)

    def setCurrentPoints(self, value):
        self._setNumber(1, value)

    def getIsProgressionFinished(self):
        return self._getBool(2)

    def setIsProgressionFinished(self, value):
        self._setBool(2, value)

    def getCurrentLevelRewards(self):
        return self._getArray(3)

    def setCurrentLevelRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getCurrentLevelRewardsType():
        return BonusModel

    def getScorePoint(self):
        return self._getArray(4)

    def setScorePoint(self, value):
        self._setArray(4, value)

    @staticmethod
    def getScorePointType():
        return int

    def _initialize(self):
        super(ProgressionTooltipModel, self)._initialize()
        self._addNumberProperty('progressionLevel', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addBoolProperty('isProgressionFinished', False)
        self._addArrayProperty('currentLevelRewards', Array())
        self._addArrayProperty('scorePoint', Array())
