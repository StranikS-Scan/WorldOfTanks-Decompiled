# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/quests_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_model import QuestModel

class QuestsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(QuestsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def finalQuest(self):
        return self._getViewModel(0)

    @staticmethod
    def getFinalQuestType():
        return QuestModel

    def getFrontName(self):
        return self._getString(1)

    def setFrontName(self, value):
        self._setString(1, value)

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsType():
        return QuestModel

    def _initialize(self):
        super(QuestsViewModel, self)._initialize()
        self._addViewModelProperty('finalQuest', QuestModel())
        self._addStringProperty('frontName', '')
        self._addArrayProperty('quests', Array())
