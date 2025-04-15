# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quest_regular_tab_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class DailyQuestRegularTabViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DailyQuestRegularTabViewModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getQuests(self):
        return self._getArray(1)

    def setQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestsType():
        return DailyQuestModel

    def getUnseenCount(self):
        return self._getNumber(2)

    def setUnseenCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(DailyQuestRegularTabViewModel, self)._initialize()
        self._addBoolProperty('isEnabled', False)
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('unseenCount', 0)
