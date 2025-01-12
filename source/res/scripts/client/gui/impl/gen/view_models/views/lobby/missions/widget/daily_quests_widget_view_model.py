# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/widget/daily_quests_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.missions.widget.comp7_daily_quest_model import Comp7DailyQuestModel
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel

class DailyQuestsWidgetViewModel(ViewModel):
    __slots__ = ('onQuestClick', 'onDisappear')

    def __init__(self, properties=6, commands=2):
        super(DailyQuestsWidgetViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def comp7DailyQuest(self):
        return self._getViewModel(0)

    @staticmethod
    def getComp7DailyQuestType():
        return Comp7DailyQuestModel

    def getQuests(self):
        return self._getArray(1)

    def setQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getQuestsType():
        return WidgetQuestModel

    def getCountdown(self):
        return self._getNumber(2)

    def setCountdown(self, value):
        self._setNumber(2, value)

    def getIsComp7Hangar(self):
        return self._getBool(3)

    def setIsComp7Hangar(self, value):
        self._setBool(3, value)

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

    def _initialize(self):
        super(DailyQuestsWidgetViewModel, self)._initialize()
        self._addViewModelProperty('comp7DailyQuest', Comp7DailyQuestModel())
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('countdown', 0)
        self._addBoolProperty('isComp7Hangar', False)
        self._addBoolProperty('visible', False)
        self._addArrayProperty('indicateCompleteQuests', Array())
        self.onQuestClick = self._addCommand('onQuestClick')
        self.onDisappear = self._addCommand('onDisappear')
