# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/tooltips/battle_matters_entry_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.tooltips.battle_matters_entry_tooltip_view_model import BattleMattersEntryTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.battle_matters.battle_matters_bonus_packer import BattleMattersEntitlementsBonusUIPacker

class BattleMattersEntryTooltipView(ViewImpl):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_matters.tooltips.BattleMattersEntryTooltipView())
        settings.model = BattleMattersEntryTooltipViewModel()
        super(BattleMattersEntryTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersEntryTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleMattersEntryTooltipView, self)._onLoading()
        currentQuest = self.__battleMattersController.getCurrentQuest()
        questsCount = self.__battleMattersController.getCountBattleMattersQuests()
        isWithToken = self.__battleMattersController.hasDelayedRewards()
        with self.viewModel.transaction() as tx:
            tx.setIsPaused(self.__battleMattersController.isPaused())
            tx.setHasToken(isWithToken)
            tx.setCurrentQuest(currentQuest.getOrder() if currentQuest else questsCount + 1)
            tx.setQuestsCount(questsCount)
            if isWithToken and self.__battleMattersController.isFinished():
                tx.setEndDate(self.__itemsCache.items.tokens.getTokenInfo(self.__battleMattersController.getDelayedRewardCurrencyToken())[0])
            if currentQuest is not None:
                tx.setTitle(currentQuest.getUserName())
                tx.setCondition(currentQuest.getConditionLbl())
                currentProgress, maxProgress = self.__battleMattersController.getQuestProgress(currentQuest)
                tx.setCurrentProgress(currentProgress)
                tx.setMaxProgress(maxProgress)
                rewards = currentQuest.getBonuses()
                packer = self.__getBonusBacker()
                rewardsVMs = tx.getRewards()
                rewardsVMs.clear()
                for reward in rewards:
                    packedRewards = packer.pack(reward)
                    for rewardVM in packedRewards:
                        rewardsVMs.addViewModel(rewardVM)

                rewardsVMs.invalidate()
        return

    @staticmethod
    def __getBonusBacker():
        packer = getDefaultBonusPacker()
        packer.getPackers().update({'entitlements': BattleMattersEntitlementsBonusUIPacker()})
        return packer
