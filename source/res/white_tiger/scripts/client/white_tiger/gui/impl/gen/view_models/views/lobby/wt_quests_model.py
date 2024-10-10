# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_quests_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_quest_model import WtQuestModel

class QuestsTabType(Enum):
    ENGINEER = 'ENGINEER'
    HARRIER = 'HARRIER'


class WtQuestsModel(ViewModel):
    __slots__ = ('onSelectedTab',)

    def __init__(self, properties=6, commands=1):
        super(WtQuestsModel, self).__init__(properties=properties, commands=commands)

    def getActiveTab(self):
        return QuestsTabType(self._getString(0))

    def setActiveTab(self, value):
        self._setString(0, value.value)

    def getHarrierQuests(self):
        return self._getArray(1)

    def setHarrierQuests(self, value):
        self._setArray(1, value)

    @staticmethod
    def getHarrierQuestsType():
        return WtQuestModel

    def getHarrierQuestsVisited(self):
        return self._getArray(2)

    def setHarrierQuestsVisited(self, value):
        self._setArray(2, value)

    def getEngineerQuests(self):
        return self._getArray(3)

    def setEngineerQuests(self, value):
        self._setArray(3, value)

    @staticmethod
    def getEngineerQuestsType():
        return WtQuestModel

    def getEngineerQuestsVisited(self):
        return self._getArray(4)

    def setEngineerQuestsVisited(self, value):
        self._setArray(4, value)

    def getUpdateCountdown(self):
        return self._getNumber(5)

    def setUpdateCountdown(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(WtQuestsModel, self)._initialize()
        self._addStringProperty('activeTab')
        self._addArrayProperty('harrierQuests', Array())
        self._addArrayProperty('harrierQuestsVisited', Array())
        self._addArrayProperty('engineerQuests', Array())
        self._addArrayProperty('engineerQuestsVisited', Array())
        self._addNumberProperty('updateCountdown', -1)
        self.onSelectedTab = self._addCommand('onSelectedTab')
