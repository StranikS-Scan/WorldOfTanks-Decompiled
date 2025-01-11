# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pages/pm3_quest_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_card_model import Pm3CardModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_model import Pm3QuestModel

class QuestState(Enum):
    NAPREVIOUS = 'previous_progress'
    NAPREVIOUSALL = 'previous_progress_all'
    NATECH = 'no_tech'
    AVAILABLE = 'available'
    INPROGRESS = 'in_progress'
    INPROGRESSHONOR = 'in_progress_honor'
    DONE = 'done'
    DONEBASIC = 'done_basic'
    DONEHONOR = 'done_honor'


class QuestLineType(Enum):
    HIT = 'hit'
    KILLS = 'kills'
    ASSIST = 'assist'
    BATTLE = 'battle'
    MASTER = 'master'


class Pm3QuestViewModel(ViewModel):
    __slots__ = ('applyQuest', 'switchSelected', 'backToOperation', 'nextQuest', 'prevQuest', 'getSelectionBonus', 'updateRewards')

    def __init__(self, properties=5, commands=7):
        super(Pm3QuestViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def questData(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestDataType():
        return Pm3QuestModel

    def getCardsList(self):
        return self._getArray(1)

    def setCardsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCardsListType():
        return Pm3CardModel

    def getTitleValue(self):
        return self._getString(2)

    def setTitleValue(self, value):
        self._setString(2, value)

    def getType(self):
        return QuestLineType(self._getString(3))

    def setType(self, value):
        self._setString(3, value.value)

    def getState(self):
        return QuestState(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(Pm3QuestViewModel, self)._initialize()
        self._addViewModelProperty('questData', Pm3QuestModel())
        self._addArrayProperty('cardsList', Array())
        self._addStringProperty('titleValue', '')
        self._addStringProperty('type')
        self._addStringProperty('state')
        self.applyQuest = self._addCommand('applyQuest')
        self.switchSelected = self._addCommand('switchSelected')
        self.backToOperation = self._addCommand('backToOperation')
        self.nextQuest = self._addCommand('nextQuest')
        self.prevQuest = self._addCommand('prevQuest')
        self.getSelectionBonus = self._addCommand('getSelectionBonus')
        self.updateRewards = self._addCommand('updateRewards')
