# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/tooltips/daily_quest_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class DailyQuestTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(DailyQuestTooltipModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return DailyQuestModel

    def getTimeToUpdate(self):
        return self._getReal(1)

    def setTimeToUpdate(self, value):
        self._setReal(1, value)

    def getIsSubscriptionActive(self):
        return self._getBool(2)

    def setIsSubscriptionActive(self, value):
        self._setBool(2, value)

    def getIsPremiumActive(self):
        return self._getBool(3)

    def setIsPremiumActive(self, value):
        self._setBool(3, value)

    def getGroupId(self):
        return self._getNumber(4)

    def setGroupId(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(DailyQuestTooltipModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self._addRealProperty('timeToUpdate', 0.0)
        self._addBoolProperty('isSubscriptionActive', False)
        self._addBoolProperty('isPremiumActive', False)
        self._addNumberProperty('groupId', 0)
