# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.advanced_achievement_model import AdvancedAchievementModel
from gui.impl.gen.view_models.views.lobby.achievements.views.reward_view_rewards_model import RewardViewRewardsModel

class RewardViewModel(ViewModel):
    __slots__ = ('onGoToDogTag', 'onGoToAchievement', 'onOpenNextReward', 'onOpenAchievementsPage', 'onClose')

    def __init__(self, properties=4, commands=5):
        super(RewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsFirstEntry(self):
        return self._getBool(0)

    def setIsFirstEntry(self, value):
        self._setBool(0, value)

    def getRewardsBalance(self):
        return self._getNumber(1)

    def setRewardsBalance(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return RewardViewRewardsModel

    def getAchievements(self):
        return self._getArray(3)

    def setAchievements(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAchievementsType():
        return AdvancedAchievementModel

    def _initialize(self):
        super(RewardViewModel, self)._initialize()
        self._addBoolProperty('isFirstEntry', False)
        self._addNumberProperty('rewardsBalance', 0)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('achievements', Array())
        self.onGoToDogTag = self._addCommand('onGoToDogTag')
        self.onGoToAchievement = self._addCommand('onGoToAchievement')
        self.onOpenNextReward = self._addCommand('onOpenNextReward')
        self.onOpenAchievementsPage = self._addCommand('onOpenAchievementsPage')
        self.onClose = self._addCommand('onClose')
