# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/post_battle_rewards_view_model.py
from frameworks.wulf import Array, ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_reward_model import FrontlineRewardModel

class PostBattleRewardsViewModel(ViewModel):
    __slots__ = ('onClaimRewards', 'onContinue', 'onClose', 'onIntroStartsPlaying', 'onRibbonStartsPlaying', 'onProgressBarAnimationStart', 'onProgressBarAnimationComplete')

    def __init__(self, properties=8, commands=7):
        super(PostBattleRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return self._getNumber(0)

    def setRank(self, value):
        self._setNumber(0, value)

    def getPrevProgress(self):
        return self._getReal(1)

    def setPrevProgress(self, value):
        self._setReal(1, value)

    def getCurrProgress(self):
        return self._getReal(2)

    def setCurrProgress(self, value):
        self._setReal(2, value)

    def getAchievedPoints(self):
        return self._getNumber(3)

    def setAchievedPoints(self, value):
        self._setNumber(3, value)

    def getAmountRewardsToClaim(self):
        return self._getNumber(4)

    def setAmountRewardsToClaim(self, value):
        self._setNumber(4, value)

    def getMaxLevel(self):
        return self._getNumber(5)

    def setMaxLevel(self, value):
        self._setNumber(5, value)

    def getIsMaxLevel(self):
        return self._getBool(6)

    def setIsMaxLevel(self, value):
        self._setBool(6, value)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return FrontlineRewardModel

    def _initialize(self):
        super(PostBattleRewardsViewModel, self)._initialize()
        self._addNumberProperty('rank', 0)
        self._addRealProperty('prevProgress', 0.0)
        self._addRealProperty('currProgress', 0.0)
        self._addNumberProperty('achievedPoints', 0)
        self._addNumberProperty('amountRewardsToClaim', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addBoolProperty('isMaxLevel', False)
        self._addArrayProperty('rewards', Array())
        self.onClaimRewards = self._addCommand('onClaimRewards')
        self.onContinue = self._addCommand('onContinue')
        self.onClose = self._addCommand('onClose')
        self.onIntroStartsPlaying = self._addCommand('onIntroStartsPlaying')
        self.onRibbonStartsPlaying = self._addCommand('onRibbonStartsPlaying')
        self.onProgressBarAnimationStart = self._addCommand('onProgressBarAnimationStart')
        self.onProgressBarAnimationComplete = self._addCommand('onProgressBarAnimationComplete')
