# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.daily.play_streak.play_streak_widget_model import PlayStreakWidgetModel
from gui.impl.gen.view_models.views.lobby.daily.widget_quest_model import WidgetQuestModel

class DailyQuestsWidgetViewModel(ViewModel):
    __slots__ = ('onQuestClick', 'onDisappear', 'onPlayStreakClick', 'onNyQuestsClick')

    def __init__(self, properties=8, commands=4):
        super(DailyQuestsWidgetViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def playStreak(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayStreakType():
        return PlayStreakWidgetModel

    def getQuests(self):
        return self._getArray(1)

    def setQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestsType():
        return WidgetQuestModel

    def getPremiumQuests(self):
        return self._getArray(2)

    def setPremiumQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getPremiumQuestsType():
        return WidgetQuestModel

    def getCountdown(self):
        return self._getNumber(3)

    def setCountdown(self, value):
        self._setNumber(3, value)

    def getVisible(self):
        return self._getBool(4)

    def setVisible(self, value):
        self._setBool(4, value)

    def getIndicateCompleteQuests(self):
        return self._getArray(5)

    def setIndicateCompleteQuests(self, value):
        self._setArray(5, value)

    @staticmethod
    def getIndicateCompleteQuestsType():
        return bool

    def getIsAllNyQuestsComplete(self):
        return self._getBool(6)

    def setIsAllNyQuestsComplete(self, value):
        self._setBool(6, value)

    def getIsNyEnabled(self):
        return self._getBool(7)

    def setIsNyEnabled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(DailyQuestsWidgetViewModel, self)._initialize()
        self._addViewModelProperty('playStreak', PlayStreakWidgetModel())
        self._addArrayProperty('quests', Array())
        self._addArrayProperty('premiumQuests', Array())
        self._addNumberProperty('countdown', 0)
        self._addBoolProperty('visible', False)
        self._addArrayProperty('indicateCompleteQuests', Array())
        self._addBoolProperty('isAllNyQuestsComplete', False)
        self._addBoolProperty('isNyEnabled', False)
        self.onQuestClick = self._addCommand('onQuestClick')
        self.onDisappear = self._addCommand('onDisappear')
        self.onPlayStreakClick = self._addCommand('onPlayStreakClick')
        self.onNyQuestsClick = self._addCommand('onNyQuestsClick')
