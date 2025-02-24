# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/missions/comp7_widget_quest_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel

class State(Enum):
    ACTIVE = 'active'
    WAITING = 'waiting'
    REWARD = 'reward'
    HIDE = 'hide'


class Comp7WidgetQuestModel(WidgetQuestModel):
    __slots__ = ('onClick', 'onViewLoaded')

    def __init__(self, properties=11, commands=2):
        super(Comp7WidgetQuestModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(7))

    def setState(self, value):
        self._setString(7, value.value)

    def getQuestsCompleted(self):
        return self._getNumber(8)

    def setQuestsCompleted(self, value):
        self._setNumber(8, value)

    def getTotalQuestsCount(self):
        return self._getNumber(9)

    def setTotalQuestsCount(self, value):
        self._setNumber(9, value)

    def getTimeLeftToNewQuests(self):
        return self._getNumber(10)

    def setTimeLeftToNewQuests(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(Comp7WidgetQuestModel, self)._initialize()
        self._addStringProperty('state', State.HIDE.value)
        self._addNumberProperty('questsCompleted', 0)
        self._addNumberProperty('totalQuestsCount', 0)
        self._addNumberProperty('timeLeftToNewQuests', 0)
        self.onClick = self._addCommand('onClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
