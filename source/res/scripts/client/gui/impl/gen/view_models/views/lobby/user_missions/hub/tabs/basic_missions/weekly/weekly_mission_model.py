# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/weekly/weekly_mission_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WeeklyMissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(WeeklyMissionModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getCommonConditionId(self):
        return self._getNumber(1)

    def setCommonConditionId(self, value):
        self._setNumber(1, value)

    def getSpecialConditionIds(self):
        return self._getArray(2)

    def setSpecialConditionIds(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSpecialConditionIdsType():
        return int

    def getCurrentProgress(self):
        return self._getNumber(3)

    def setCurrentProgress(self, value):
        self._setNumber(3, value)

    def getTotalProgress(self):
        return self._getNumber(4)

    def setTotalProgress(self, value):
        self._setNumber(4, value)

    def getPreviousProgress(self):
        return self._getNumber(5)

    def setPreviousProgress(self, value):
        self._setNumber(5, value)

    def getIsRerollInProgress(self):
        return self._getBool(6)

    def setIsRerollInProgress(self, value):
        self._setBool(6, value)

    def getTimeToNextReroll(self):
        return self._getNumber(7)

    def setTimeToNextReroll(self, value):
        self._setNumber(7, value)

    def getRerollCooldown(self):
        return self._getNumber(8)

    def setRerollCooldown(self, value):
        self._setNumber(8, value)

    def getBonuses(self):
        return self._getArray(9)

    def setBonuses(self, value):
        self._setArray(9, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(WeeklyMissionModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('commonConditionId', 0)
        self._addArrayProperty('specialConditionIds', Array())
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('previousProgress', 0)
        self._addBoolProperty('isRerollInProgress', False)
        self._addNumberProperty('timeToNextReroll', 0)
        self._addNumberProperty('rerollCooldown', 0)
        self._addArrayProperty('bonuses', Array())
