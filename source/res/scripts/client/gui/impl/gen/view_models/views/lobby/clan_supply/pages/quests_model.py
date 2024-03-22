# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/pages/quests_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.clan_supply.pages.quest_model import QuestModel

class ScreenStatus(IntEnum):
    PENDING = 0
    ERROR = 1
    PLAYER_NOT_IN_CLAN = 2
    REWARD_AVAILABLE = 3
    PREVIOUS_REWARDS = 4
    IN_PROGRESS = 5


class QuestsModel(ViewModel):
    __slots__ = ('onClaimReward', 'onGoToClans', 'onRefresh')

    def __init__(self, properties=6, commands=3):
        super(QuestsModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return ScreenStatus(self._getNumber(0))

    def setStatus(self, value):
        self._setNumber(0, value.value)

    def getCycleDuration(self):
        return self._getNumber(1)

    def setCycleDuration(self, value):
        self._setNumber(1, value)

    def getUpdateTime(self):
        return self._getNumber(2)

    def setUpdateTime(self, value):
        self._setNumber(2, value)

    def getIsRewardsLoading(self):
        return self._getBool(3)

    def setIsRewardsLoading(self, value):
        self._setBool(3, value)

    def getQuests(self):
        return self._getArray(4)

    def setQuests(self, value):
        self._setArray(4, value)

    @staticmethod
    def getQuestsType():
        return QuestModel

    def getPreviousRewards(self):
        return self._getArray(5)

    def setPreviousRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getPreviousRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(QuestsModel, self)._initialize()
        self._addNumberProperty('status')
        self._addNumberProperty('cycleDuration', 0)
        self._addNumberProperty('updateTime', 0)
        self._addBoolProperty('isRewardsLoading', False)
        self._addArrayProperty('quests', Array())
        self._addArrayProperty('previousRewards', Array())
        self.onClaimReward = self._addCommand('onClaimReward')
        self.onGoToClans = self._addCommand('onGoToClans')
        self.onRefresh = self._addCommand('onRefresh')
