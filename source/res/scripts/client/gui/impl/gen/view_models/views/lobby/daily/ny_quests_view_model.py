# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/ny_quests_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class NyQuestsViewModel(ViewModel):
    __slots__ = ('onTypeSelect',)

    def __init__(self, properties=7, commands=1):
        super(NyQuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentTabIdx(self):
        return self._getNumber(0)

    def setCurrentTabIdx(self, value):
        self._setNumber(0, value)

    def getFirstSeenNewBonusMissions(self):
        return self._getBool(1)

    def setFirstSeenNewBonusMissions(self, value):
        self._setBool(1, value)

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsType():
        return DailyQuestModel

    def getCountDown(self):
        return self._getNumber(3)

    def setCountDown(self, value):
        self._setNumber(3, value)

    def getMinLevel(self):
        return self._getNumber(4)

    def setMinLevel(self, value):
        self._setNumber(4, value)

    def getMaxLevel(self):
        return self._getNumber(5)

    def setMaxLevel(self, value):
        self._setNumber(5, value)

    def getPersonTextNumber(self):
        return self._getNumber(6)

    def setPersonTextNumber(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(NyQuestsViewModel, self)._initialize()
        self._addNumberProperty('currentTabIdx', 0)
        self._addBoolProperty('firstSeenNewBonusMissions', False)
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('countDown', 0)
        self._addNumberProperty('minLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addNumberProperty('personTextNumber', 1)
        self.onTypeSelect = self._addCommand('onTypeSelect')
