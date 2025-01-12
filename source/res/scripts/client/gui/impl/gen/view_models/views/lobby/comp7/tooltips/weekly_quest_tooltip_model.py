# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/weekly_quest_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel

class State(Enum):
    ACTIVE = 'active'
    WAITING = 'waiting'
    REWARD = 'reward'


class WeeklyQuestTooltipModel(ViewModel):
    __slots__ = ()
    QUESTS_PER_WEEK = 5

    def __init__(self, properties=10, commands=0):
        super(WeeklyQuestTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getTotalProgress(self):
        return self._getNumber(2)

    def setTotalProgress(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getQuestType(self):
        return self._getString(4)

    def setQuestType(self, value):
        self._setString(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def getQuestsPassed(self):
        return self._getNumber(6)

    def setQuestsPassed(self, value):
        self._setNumber(6, value)

    def getTotalQuests(self):
        return self._getNumber(7)

    def setTotalQuests(self, value):
        self._setNumber(7, value)

    def getQuestNumbersToRewards(self):
        return self._getArray(8)

    def setQuestNumbersToRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getQuestNumbersToRewardsType():
        return int

    def getTimeToNewQuests(self):
        return self._getNumber(9)

    def setTimeToNewQuests(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(WeeklyQuestTooltipModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addStringProperty('description', '')
        self._addStringProperty('questType', '')
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('questsPassed', 0)
        self._addNumberProperty('totalQuests', 0)
        self._addArrayProperty('questNumbersToRewards', Array())
        self._addNumberProperty('timeToNewQuests', 0)
