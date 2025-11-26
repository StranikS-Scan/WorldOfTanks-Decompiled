# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_results/sub_presenters/fun_progression.py
from __future__ import absolute_import
import typing
from collections import namedtuple
from future.utils import viewitems
from frameworks.wulf.view.array import fillIntsArray
from fun_random.gui.battle_results.packers.fun_progression_helpers import FunPbsProgressionHelper, FunPbsUnlimitedProgressionHelper
from fun_random.gui.feature.util.fun_helpers import isFunProgressionUnlimitedTrigger
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher
from fun_random.gui.impl.gen.view_models.views.lobby.feature.battle_results.fun_random_progress_model import FunRandomProgressModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import packBonuses, packStageRewards, sortFunProgressionBonuses
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults
_RewardsData = namedtuple('_RewardsData', ('tooltips', 'bonuses'))

class FunProgressionSubPresenter(BattleResultsSubPresenter, FunProgressionWatcher, FunAssetPacksMixin):

    def __init__(self, viewModel, parentView):
        super(FunProgressionSubPresenter, self).__init__(viewModel, parentView)
        self.__rewardsData = _RewardsData(tooltips={}, bonuses=[])

    def finalize(self):
        self.__rewardsData = None
        super(FunProgressionSubPresenter, self).finalize()
        return

    @classmethod
    def getViewModelType(cls):
        return FunRandomProgressModel

    def packBattleResults(self, battleResults):
        with self.getViewModel().transaction() as model:
            progression = FunProgressionWatcher.getActiveProgression()
            if progression is None:
                model.setHasProgress(False)
                return
            personalInfo = battleResults.reusable.personal
            questsProgress = personalInfo.getQuestsProgress()
            questsTokens = personalInfo.getQuestTokensCount()
            helper = self.__createProgressionHelper(questsProgress)
            progressionData = helper.getProgressionData(progression, questsProgress, questsTokens)
            if progressionData is None:
                model.setHasProgress(False)
                return
            self.__packModel(model, progressionData)
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.fun_random.mono.lobby.tooltips.loot_box_tooltip():
            tooltipData = self.__getTooltipData(event)
            lootboxID = tooltipData.specialArgs[0] if tooltipData and tooltipData.specialArgs else None
            from fun_random.gui.impl.lobby.tooltips.fun_random_loot_box_tooltip_view import FunRandomLootBoxTooltipView
            if lootboxID:
                return FunRandomLootBoxTooltipView(lootboxID)
            return
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = max(0, int(event.getArgument('showCount')) - 1)
            bonuses = packBonuses(self.__rewardsData.bonuses, showCount, isSpecial=True)
            if bonuses:
                return AdditionalRewardsTooltip(bonuses)
            return
        elif contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            return createBackportTooltipContent(specialAlias=tooltipId, tooltipData=self.__getTooltipData(event))
        else:
            return super(FunProgressionSubPresenter, self).createToolTipContent(event, contentID)

    def __getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__rewardsData.tooltips.get(tooltipId)

    def __packModel(self, model, progressionData):
        model.setHasProgress(True)
        model.setAssetsPointer(self.getModeAssetsPointer())
        model.setIsInUnlimitedProgression(progressionData.isUnlimitedProgression)
        model.setDescription(progressionData.description)
        model.setPreviousPoints(progressionData.previousPoints)
        model.setCurrentPoints(progressionData.currentPoints)
        model.setMaximumPoints(progressionData.maximumPoints)
        model.setEarnedPoints(progressionData.earnedPoints)
        model.setPreviousStage(progressionData.previousStage)
        model.setCurrentStage(progressionData.currentStage)
        model.setMaximumStage(progressionData.maximumStage)
        stageRequiredCounters = model.getStageRequiredCounters()
        fillIntsArray(progressionData.stageRequiredCounters, stageRequiredCounters)
        bonuses = progressionData.bonuses
        rewardsData = self.__rewardsData
        if bonuses and rewardsData is not None:
            bonuses = sortFunProgressionBonuses(bonuses)
            packStageRewards(bonuses, model.getRewards(), isSpecial=True, tooltips=rewardsData.tooltips)
            rewardsData.bonuses.extend(bonuses)
        return

    @staticmethod
    def __createProgressionHelper(questsProgress):
        unlimitedTriggers = {qID:p for qID, p in viewitems(questsProgress) if isFunProgressionUnlimitedTrigger(qID)}
        helperCls = FunPbsUnlimitedProgressionHelper if unlimitedTriggers else FunPbsProgressionHelper
        return helperCls()
