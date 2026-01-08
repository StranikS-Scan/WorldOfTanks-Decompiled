# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/weekly_quest_progress_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WeeklyQuestProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(WeeklyQuestProgressModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getCurrentProgress(self):
        return self._getNumber(2)

    def setCurrentProgress(self, value):
        self._setNumber(2, value)

    def getTotalProgress(self):
        return self._getNumber(3)

    def setTotalProgress(self, value):
        self._setNumber(3, value)

    def getEarned(self):
        return self._getNumber(4)

    def setEarned(self, value):
        self._setNumber(4, value)

    def getNavigationEnabled(self):
        return self._getBool(5)

    def setNavigationEnabled(self, value):
        self._setBool(5, value)

    def getCommonConditionId(self):
        return self._getNumber(6)

    def setCommonConditionId(self, value):
        self._setNumber(6, value)

    def getBonuses(self):
        return self._getArray(7)

    def setBonuses(self, value):
        self._setArray(7, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(WeeklyQuestProgressModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('earned', 0)
        self._addBoolProperty('navigationEnabled', False)
        self._addNumberProperty('commonConditionId', 0)
        self._addArrayProperty('bonuses', Array())
