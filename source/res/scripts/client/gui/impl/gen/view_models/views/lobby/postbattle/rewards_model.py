# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/rewards_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.postbattle.currency_model import CurrencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.exp_bonus_model import ExpBonusModel
from gui.impl.gen.view_models.views.lobby.postbattle.progressive_reward_model import ProgressiveRewardModel

class RewardsModel(ViewModel):
    __slots__ = ('onAppliedPremiumBonus',)

    def __init__(self, properties=8, commands=1):
        super(RewardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def progressiveReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressiveRewardType():
        return ProgressiveRewardModel

    @property
    def expBonus(self):
        return self._getViewModel(1)

    @staticmethod
    def getExpBonusType():
        return ExpBonusModel

    def getExperience(self):
        return self._getNumber(2)

    def setExperience(self, value):
        self._setNumber(2, value)

    def getCredits(self):
        return self._getNumber(3)

    def setCredits(self, value):
        self._setNumber(3, value)

    def getCrystals(self):
        return self._getNumber(4)

    def setCrystals(self, value):
        self._setNumber(4, value)

    def getAchievements(self):
        return self._getArray(5)

    def setAchievements(self, value):
        self._setArray(5, value)

    @staticmethod
    def getAchievementsType():
        return AchievementModel

    def getIsPremiumBought(self):
        return self._getBool(6)

    def setIsPremiumBought(self, value):
        self._setBool(6, value)

    def getPremiumBonus(self):
        return self._getArray(7)

    def setPremiumBonus(self, value):
        self._setArray(7, value)

    @staticmethod
    def getPremiumBonusType():
        return CurrencyModel

    def _initialize(self):
        super(RewardsModel, self)._initialize()
        self._addViewModelProperty('progressiveReward', ProgressiveRewardModel())
        self._addViewModelProperty('expBonus', ExpBonusModel())
        self._addNumberProperty('experience', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('crystals', 0)
        self._addArrayProperty('achievements', Array())
        self._addBoolProperty('isPremiumBought', False)
        self._addArrayProperty('premiumBonus', Array())
        self.onAppliedPremiumBonus = self._addCommand('onAppliedPremiumBonus')
