# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/weekly_quests_widget_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.weekly_quest_model import WeeklyQuestModel

class State(Enum):
    HIDE = 'hide'
    ACTIVE = 'active'
    WAITING = 'waiting'
    REWARD = 'reward'


class WeeklyQuestsWidgetModel(ViewModel):
    __slots__ = ('onGoToWeeklyQuests', 'onMissionClick', 'onMarkAsViewed', 'onGoToRewardsSelection', 'onPollServerTime')

    def __init__(self, properties=6, commands=5):
        super(WeeklyQuestsWidgetModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return WeeklyQuestModel

    def getState(self):
        return State(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getQuestsCompleted(self):
        return self._getNumber(2)

    def setQuestsCompleted(self, value):
        self._setNumber(2, value)

    def getTotalQuestsCount(self):
        return self._getNumber(3)

    def setTotalQuestsCount(self, value):
        self._setNumber(3, value)

    def getLeftToNewQuestsTimestamp(self):
        return self._getNumber(4)

    def setLeftToNewQuestsTimestamp(self, value):
        self._setNumber(4, value)

    def getServerTimestamp(self):
        return self._getNumber(5)

    def setServerTimestamp(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(WeeklyQuestsWidgetModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self._addStringProperty('state')
        self._addNumberProperty('questsCompleted', 0)
        self._addNumberProperty('totalQuestsCount', 0)
        self._addNumberProperty('leftToNewQuestsTimestamp', 0)
        self._addNumberProperty('serverTimestamp', 0)
        self.onGoToWeeklyQuests = self._addCommand('onGoToWeeklyQuests')
        self.onMissionClick = self._addCommand('onMissionClick')
        self.onMarkAsViewed = self._addCommand('onMarkAsViewed')
        self.onGoToRewardsSelection = self._addCommand('onGoToRewardsSelection')
        self.onPollServerTime = self._addCommand('onPollServerTime')
