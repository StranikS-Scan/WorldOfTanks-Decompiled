# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/mascot_quest_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class State(IntEnum):
    IN_PROGRESS = 0
    CLAIM_REWARD = 1
    CLAIM_PREVIOUS_REWARD = 2
    WAIT_NEXT_CYCLE = 3
    ALL_COMPLETED = 4


class Phase(IntEnum):
    MOUSE = 0
    CAT = 1
    DEER = 2


class MascotQuestModel(ViewModel):
    __slots__ = ('claimReward',)

    def __init__(self, properties=8, commands=1):
        super(MascotQuestModel, self).__init__(properties=properties, commands=commands)

    @property
    def battle_quest(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattle_questType():
        return QuestModel

    def getState(self):
        return State(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def getActivePhase(self):
        return Phase(self._getNumber(2))

    def setActivePhase(self, value):
        self._setNumber(2, value.value)

    def getCurrentProgress(self):
        return self._getNumber(3)

    def setCurrentProgress(self, value):
        self._setNumber(3, value)

    def getIsWaitingRewards(self):
        return self._getBool(4)

    def setIsWaitingRewards(self, value):
        self._setBool(4, value)

    def getTotalProgress(self):
        return self._getNumber(5)

    def setTotalProgress(self, value):
        self._setNumber(5, value)

    def getEndTime(self):
        return self._getNumber(6)

    def setEndTime(self, value):
        self._setNumber(6, value)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(MascotQuestModel, self)._initialize()
        self._addViewModelProperty('battle_quest', QuestModel())
        self._addNumberProperty('state')
        self._addNumberProperty('activePhase')
        self._addNumberProperty('currentProgress', 0)
        self._addBoolProperty('isWaitingRewards', False)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('endTime', 0)
        self._addArrayProperty('rewards', Array())
        self.claimReward = self._addCommand('claimReward')
