# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_rewards_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_model import Pm3QuestModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_reward_item_model import Pm3RewardItemModel

class CompletedQuestsType(Enum):
    COMPLETE = 'complete'
    COMPLETE_WITH_HONOR = 'completeWithHonor'
    COMPLETE_ADD = 'completeAdd'
    COMPLETE_BASIC = 'completeBasic'


class LineType(Enum):
    HIT = 'hit'
    KILLS = 'kills'
    ASSIST = 'assist'
    BATTLE = 'battle'
    MASTER = 'master'


class PersonalMissionsRewardsViewModel(ViewModel):
    __slots__ = ('onApply', 'onClose', 'onOpenQuest', 'onChooseReward')

    def __init__(self, properties=15, commands=4):
        super(PersonalMissionsRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def questModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestModelType():
        return Pm3QuestModel

    def getType(self):
        return LineType(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getIsOperationAddRewards(self):
        return self._getBool(2)

    def setIsOperationAddRewards(self, value):
        self._setBool(2, value)

    def getIsSelectedRewards(self):
        return self._getBool(3)

    def setIsSelectedRewards(self, value):
        self._setBool(3, value)

    def getQuestID(self):
        return self._getNumber(4)

    def setQuestID(self, value):
        self._setNumber(4, value)

    def getNextQuestID(self):
        return self._getNumber(5)

    def setNextQuestID(self, value):
        self._setNumber(5, value)

    def getValue(self):
        return self._getNumber(6)

    def setValue(self, value):
        self._setNumber(6, value)

    def getMaxValue(self):
        return self._getNumber(7)

    def setMaxValue(self, value):
        self._setNumber(7, value)

    def getDelta(self):
        return self._getNumber(8)

    def setDelta(self, value):
        self._setNumber(8, value)

    def getIsFullChainComplete(self):
        return self._getBool(9)

    def setIsFullChainComplete(self, value):
        self._setBool(9, value)

    def getOperationName(self):
        return self._getString(10)

    def setOperationName(self, value):
        self._setString(10, value)

    def getCurrentTaskName(self):
        return self._getString(11)

    def setCurrentTaskName(self, value):
        self._setString(11, value)

    def getNextTaskName(self):
        return self._getString(12)

    def setNextTaskName(self, value):
        self._setString(12, value)

    def getQuestTypeComplete(self):
        return CompletedQuestsType(self._getString(13))

    def setQuestTypeComplete(self, value):
        self._setString(13, value.value)

    def getRewards(self):
        return self._getArray(14)

    def setRewards(self, value):
        self._setArray(14, value)

    @staticmethod
    def getRewardsType():
        return Pm3RewardItemModel

    def _initialize(self):
        super(PersonalMissionsRewardsViewModel, self)._initialize()
        self._addViewModelProperty('questModel', Pm3QuestModel())
        self._addStringProperty('type')
        self._addBoolProperty('isOperationAddRewards', False)
        self._addBoolProperty('isSelectedRewards', False)
        self._addNumberProperty('questID', 0)
        self._addNumberProperty('nextQuestID', 0)
        self._addNumberProperty('value', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('delta', 0)
        self._addBoolProperty('isFullChainComplete', False)
        self._addStringProperty('operationName', '')
        self._addStringProperty('currentTaskName', '')
        self._addStringProperty('nextTaskName', '')
        self._addStringProperty('questTypeComplete')
        self._addArrayProperty('rewards', Array())
        self.onApply = self._addCommand('onApply')
        self.onClose = self._addCommand('onClose')
        self.onOpenQuest = self._addCommand('onOpenQuest')
        self.onChooseReward = self._addCommand('onChooseReward')
