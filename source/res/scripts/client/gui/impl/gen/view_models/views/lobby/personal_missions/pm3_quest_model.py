# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_quest_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_part_model import Pm3QuestPartModel

class Pm3QuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(Pm3QuestModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getMainQuestsType():
        return Pm3QuestPartModel

    @property
    def addQuests(self):
        return self._getViewModel(1)

    @staticmethod
    def getAddQuestsType():
        return Pm3QuestPartModel

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getIsFinal(self):
        return self._getBool(4)

    def setIsFinal(self, value):
        self._setBool(4, value)

    def getQuestLevelFrom(self):
        return self._getString(5)

    def setQuestLevelFrom(self, value):
        self._setString(5, value)

    def getQuestLevelTo(self):
        return self._getString(6)

    def setQuestLevelTo(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(Pm3QuestModel, self)._initialize()
        self._addViewModelProperty('mainQuests', Pm3QuestPartModel())
        self._addViewModelProperty('addQuests', Pm3QuestPartModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addBoolProperty('isFinal', False)
        self._addStringProperty('questLevelFrom', '')
        self._addStringProperty('questLevelTo', '')
