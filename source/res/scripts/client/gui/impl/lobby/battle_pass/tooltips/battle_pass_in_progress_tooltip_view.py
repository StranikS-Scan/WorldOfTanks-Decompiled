# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tooltips/battle_pass_in_progress_tooltip_view.py
from battle_pass_common import BattlePassState, BattlePassConsts
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view_model import BattlePassInProgressTooltipViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.reward_points_model import RewardPointsModel
from gui.impl.pub import ViewImpl
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_helpers import isSeasonEndingSoon, getFormattedTimeLeft
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class BattlePassInProgressTooltipView(ViewImpl):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView())
        settings.model = BattlePassInProgressTooltipViewModel()
        super(BattlePassInProgressTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassInProgressTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassInProgressTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            items = model.rewardPoints.getItems()
            for points in self.__battlePassController.getPerBattlePoints():
                item = RewardPointsModel()
                item.setTopCount(points.label)
                item.setPointsWin(points.winPoint)
                item.setPointsLose(points.losePoint)
                items.addViewModel(item)

            curLevel = self.__battlePassController.getCurrentLevel()
            curPoints, limitPoints = self.__battlePassController.getLevelProgression()
            isPostProgression = self.__battlePassController.getState() == BattlePassState.POST
            model.setLevel(curLevel)
            model.setCurrentPoints(curPoints)
            model.setMaxPoints(limitPoints)
            model.setIsBattlePassPurchased(self.__battlePassController.isBought())
            model.setIsPostProgression(isPostProgression)
            model.setCanPlay(self.__battlePassController.canPlayerParticipate())
            timeTillEnd = ''
            if isSeasonEndingSoon() and not self.__battlePassController.isBought():
                timeTillEnd = getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft())
            model.setTimeTillEnd(timeTillEnd)
            if isPostProgression:
                self.__getAwards(model.rewardsCommon, curLevel, BattlePassConsts.REWARD_POST)
            else:
                self.__getAwards(model.rewardsCommon, curLevel, BattlePassConsts.REWARD_FREE)
                self.__getAwards(model.rewardsElite, curLevel, BattlePassConsts.REWARD_PAID)

    def __getAwards(self, rewardsList, level, bonusType):
        finalLevel = self.__battlePassController.getMaxLevel()
        if level == finalLevel - 1 and bonusType != BattlePassConsts.REWARD_POST:
            freeReward, paidReward = self.__battlePassController.getSplitFinalAwards()
            if bonusType == BattlePassConsts.REWARD_FREE:
                bonuses = freeReward
            else:
                bonuses = paidReward
        else:
            bonuses = self.__battlePassController.getSingleAward(level + 1, bonusType)
        packBonusModelAndTooltipData(bonuses, rewardsList)
