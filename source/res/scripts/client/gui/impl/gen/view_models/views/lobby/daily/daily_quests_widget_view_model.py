# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.daily.widget_quest_model import WidgetQuestModel

class DailyQuestsWidgetViewModel(ViewModel):
    __slots__ = ('onQuestClick', 'onDisappear')

    def __init__(self, properties=6, commands=2):
        super(DailyQuestsWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getQuests(self):
        return self._getArray(0)

    def setQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getQuestsType():
        return WidgetQuestModel

    def getPremiumQuests(self):
        return self._getArray(1)

    def setPremiumQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getPremiumQuestsType():
        return WidgetQuestModel

    def getSerialEnterQuests(self):
        return self._getArray(2)

    def setSerialEnterQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSerialEnterQuestsType():
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

    def _initialize(self):
        super(DailyQuestsWidgetViewModel, self)._initialize()
        self._addArrayProperty('quests', Array())
        self._addArrayProperty('premiumQuests', Array())
        self._addArrayProperty('serialEnterQuests', Array())
        self._addNumberProperty('countdown', 0)
        self._addBoolProperty('visible', False)
        self._addArrayProperty('indicateCompleteQuests', Array())
        self.onQuestClick = self._addCommand('onQuestClick')
        self.onDisappear = self._addCommand('onDisappear')
