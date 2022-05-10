# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/widget/daily_quests_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel

class DailyQuestsWidgetViewModel(ViewModel):
    __slots__ = ('onQuestClick', 'onDisappear')

    def __init__(self, properties=4, commands=2):
        super(DailyQuestsWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    def getCountdown(self):
        return self._getNumber(1)

    def setCountdown(self, value):
        self._setNumber(1, value)

    def getVisible(self):
        return self._getBool(2)

    def setVisible(self, value):
        self._setBool(2, value)

    def getIndicateCompleteQuests(self):
        return self._getArray(3)

    def setIndicateCompleteQuests(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(DailyQuestsWidgetViewModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('countdown', 0)
        self._addBoolProperty('visible', False)
        self._addArrayProperty('indicateCompleteQuests', Array())
        self.onQuestClick = self._addCommand('onQuestClick')
        self.onDisappear = self._addCommand('onDisappear')
