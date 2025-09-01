# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/weekly_quest_widget_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.user_missions.widget.bonus_model import BonusModel

class State(Enum):
    ACTIVE = 'active'
    WAITING = 'waiting'
    REWARD = 'reward'


class WeeklyQuestWidgetTooltipModel(ViewModel):
    __slots__ = ()
    QUESTS_PER_WEEK = 5

    def __init__(self, properties=7, commands=0):
        super(WeeklyQuestWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getQuestsPassed(self):
        return self._getNumber(3)

    def setQuestsPassed(self, value):
        self._setNumber(3, value)

    def getTotalQuests(self):
        return self._getNumber(4)

    def setTotalQuests(self, value):
        self._setNumber(4, value)

    def getQuestNumbersToRewards(self):
        return self._getArray(5)

    def setQuestNumbersToRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getQuestNumbersToRewardsType():
        return int

    def getTimeToNewQuests(self):
        return self._getNumber(6)

    def setTimeToNewQuests(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(WeeklyQuestWidgetTooltipModel, self)._initialize()
        self._addStringProperty('state')
        self._addStringProperty('description', '')
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('questsPassed', 0)
        self._addNumberProperty('totalQuests', 0)
        self._addArrayProperty('questNumbersToRewards', Array())
        self._addNumberProperty('timeToNewQuests', 0)
