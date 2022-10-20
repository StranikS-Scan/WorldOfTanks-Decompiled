# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/bonus_quest_model.py
from frameworks.wulf import ViewModel

class BonusQuestModel(ViewModel):
    __slots__ = ('onGoToTasks',)

    def __init__(self, properties=6, commands=1):
        super(BonusQuestModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getAbilityIcon(self):
        return self._getString(2)

    def setAbilityIcon(self, value):
        self._setString(2, value)

    def getAbilityName(self):
        return self._getString(3)

    def setAbilityName(self, value):
        self._setString(3, value)

    def getNumberOfBoostersAward(self):
        return self._getNumber(4)

    def setNumberOfBoostersAward(self, value):
        self._setNumber(4, value)

    def getTimesCompleted(self):
        return self._getNumber(5)

    def setTimesCompleted(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(BonusQuestModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addStringProperty('abilityIcon', '')
        self._addStringProperty('abilityName', '')
        self._addNumberProperty('numberOfBoostersAward', 0)
        self._addNumberProperty('timesCompleted', 0)
        self.onGoToTasks = self._addCommand('onGoToTasks')
