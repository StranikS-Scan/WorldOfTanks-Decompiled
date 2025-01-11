# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_quest_part_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_item_part_model import Pm3QuestItemPartModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_part_relation_model import Pm3QuestPartRelationModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_reward_item_model import Pm3RewardItemModel

class Pm3QuestPartModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(Pm3QuestPartModel, self).__init__(properties=properties, commands=commands)

    @property
    def relation(self):
        return self._getViewModel(0)

    @staticmethod
    def getRelationType():
        return Pm3QuestPartRelationModel

    def getIsDone(self):
        return self._getBool(1)

    def setIsDone(self, value):
        self._setBool(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return Pm3RewardItemModel

    def getQuests(self):
        return self._getArray(3)

    def setQuests(self, value):
        self._setArray(3, value)

    @staticmethod
    def getQuestsType():
        return Pm3QuestItemPartModel

    def _initialize(self):
        super(Pm3QuestPartModel, self)._initialize()
        self._addViewModelProperty('relation', Pm3QuestPartRelationModel())
        self._addBoolProperty('isDone', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('quests', Array())
