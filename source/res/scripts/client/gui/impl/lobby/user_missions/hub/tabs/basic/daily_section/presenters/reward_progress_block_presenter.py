# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/daily_section/presenters/reward_progress_block_presenter.py
import typing
from constants import OFFERS_ENABLED_KEY, DAILY_QUESTS_CONFIG
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.reward_progress_block_model import RewardProgressTypes, RewardProgressBlockModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.win_back_progress import WinBackProgress, OffersState
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.win_back_quest_model import WinBackQuestModel
from gui.impl.lobby.missions.missions_helpers import getDailyEpicQuestToken, getRewardProgressType
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.base_block_presenter import BaseBlockPresenter
from gui.impl.lobby.winback.tooltips.main_reward_tooltip import MainRewardTooltip
from gui.impl.lobby.winback.tooltips.selectable_reward_tooltip import SelectableRewardTooltip
from gui.impl.lobby.winback.winback_bonus_packer import getWinbackBonusPacker, packWinbackBonusModelAndTooltipData
from gui.impl.lobby.winback.winback_bonuses import getWinbackRewardsTimeLeft
from gui.impl.lobby.winback.winback_helpers import getWinbackCompletedQuestsCount, getSortedWinbackQuests, getWinbackQuestsData, getLastWinbackQuestData
from gui.server_events.settings import visitEventsGUI
from gui.shared.event_dispatcher import showWinbackSelectRewardView
from gui.shared.missions.packers.bonus import getDailyMissionsBonusPacker
from gui.shared.missions.packers.events import packQuestBonusModelAndTooltipData
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController, IWinbackController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from typing import Dict
    from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.epic_quest_progress import EpicQuestProgress

class RewardProgressBlockPresenter(BaseBlockPresenter[RewardProgressBlockModel]):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    battlePassController = dependency.descriptor(IBattlePassController)
    winbackController = dependency.descriptor(IWinbackController)

    def __init__(self):
        self._winbackData = {}
        super(RewardProgressBlockPresenter, self).__init__(model=RewardProgressBlockModel)

    @property
    def viewModel(self):
        return super(RewardProgressBlockPresenter, self).getViewModel()

    @property
    def progressType(self):
        return getRewardProgressType(self._winbackData)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.winback.tooltips.SelectableRewardTooltip():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = self._tooltipData.get(tooltipId)
            if tooltipData:
                return SelectableRewardTooltip(**tooltipData)
        return MainRewardTooltip(self._winbackData.get('lastQuest', {}).get('bonuses', [])) if contentID == R.views.lobby.winback.tooltips.MainRewardTooltip() else super(RewardProgressBlockPresenter, self).createToolTipContent(event, contentID)

    def _markQuestsAsVisited(self):
        if self.progressType == RewardProgressTypes.EPICQUEST:
            epicQuest = self.eventsCache.getDailyEpicQuest()
            if epicQuest:
                dqToken = getDailyEpicQuestToken(epicQuest)
                if dqToken:
                    self.itemsCache.items.tokens.markTokenProgressAsViewed(dqToken.getID())
                visitEventsGUI([epicQuest])

    def _onSyncCompleted(self, *_):
        self._updateWinbackData()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
            self._updateCommonData(tx)
        super(RewardProgressBlockPresenter, self)._onSyncCompleted(*_)

    def _onLoading(self, *args, **kwargs):
        super(RewardProgressBlockPresenter, self)._onLoading()
        self._updateWinbackData()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
            self._updateCommonData(tx)

    def _getEvents(self):
        vm = self.viewModel
        eventsTuple = super(RewardProgressBlockPresenter, self)._getEvents()
        return eventsTuple + ((vm.winBackProgress.onTakeReward, self._onTakeReward),
         (vm.winBackProgress.onTakeAllRewards, self._onTakeAllReward),
         (vm.epicQuestProgress.onTakeWinBackReward, self._onTakeAllReward),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged),
         (self.battlePassController.onBattlePassSettingsChange, self._onUpdateBattlePassData),
         (self.winbackController.onConfigUpdated, self._onWinbackConfigUpdated))

    def _updateModel(self, model):
        progressType = getRewardProgressType(self._winbackData)
        model.setProgressType(progressType)
        if progressType == RewardProgressTypes.WINBACK:
            self._updateWinbackQuestProgress(model.winBackProgress)
        elif progressType == RewardProgressTypes.EPICQUEST:
            self._updateEpicQuestProgress(model.epicQuestProgress)

    def _updateCommonData(self, vm):
        self._updateBattlePassData(vm)
        self._updateOffersData(vm)

    def _updateWinbackData(self):
        if self._winbackData:
            self._winbackData.clear()
        if not self.winbackController.isProgressionAvailable():
            return
        winbackQuests = self.winbackController.winbackQuests
        if not winbackQuests:
            return
        dailyQuestTokensCount = getWinbackCompletedQuestsCount()
        self._winbackData['dailyQuestTokensCount'] = dailyQuestTokensCount
        sortedQuests = getSortedWinbackQuests(winbackQuests, dailyQuestTokensCount)
        questsData = getWinbackQuestsData(sortedQuests, dailyQuestTokensCount)
        self._winbackData['quests'] = questsData
        lastQuestData = getLastWinbackQuestData(sortedQuests, self._winbackData)
        self._winbackData['lastQuest'] = lastQuestData

    def _updateWinbackQuestProgress(self, vm):
        currTokenCount = self._winbackData.get('dailyQuestTokensCount', 0)
        lastQuestToken = self._winbackData.get('lastQuest').get('token')
        questID = lastQuestToken.getID()
        lastViewedTokenCount = self.itemsCache.items.tokens.getLastViewedProgress(questID)
        earned = currTokenCount - lastViewedTokenCount if currTokenCount >= lastViewedTokenCount else currTokenCount
        vm.setId(questID)
        vm.setCurrent(currTokenCount)
        vm.setTotal(lastQuestToken.getNeededCount())
        vm.setEarned(earned)
        winbackQuests = vm.getQuests()
        winbackQuests.clear()
        packer = getWinbackBonusPacker()
        for winbackQuestNumber, winbackQuestData in self._winbackData.get('quests', {}).items():
            winbackQuests.addViewModel(self._createWinbackQuestModel(winbackQuestNumber, winbackQuestData, packer))

        winbackQuests.invalidate()

    def _createWinbackQuestModel(self, questNumber, questData, packer):
        winbackQuestModel = WinBackQuestModel()
        winbackQuestModel.setQuestNumber(questNumber)
        rewardsModel = winbackQuestModel.getRewards()
        rewardsModel.clear()
        packWinbackBonusModelAndTooltipData(questData['bonuses'], packer, rewardsModel, self._tooltipData)
        return winbackQuestModel

    def _updateEpicQuestProgress(self, model, fullUpdate=False):
        epicQuest = self.eventsCache.getDailyEpicQuest()
        epicQuestId = epicQuest.getID()
        dqToken = getDailyEpicQuestToken(epicQuest)
        if dqToken is None:
            return
        else:
            isTokenCountChanged = self.itemsCache.items.tokens.hasTokenCountChanged(dqToken.getID())
            isTokenNeededChanged = dqToken.getNeededCount() != model.getTotal()
            isEpicQuestIdChanged = epicQuestId != model.getId()
            if not fullUpdate and not isTokenCountChanged and not isEpicQuestIdChanged and not isTokenNeededChanged:
                return
            lastViewedTokenCount = self.itemsCache.items.tokens.getLastViewedProgress(dqToken.getID())
            currTokenCount = self.eventsCache.questsProgress.getTokenCount(dqToken.getID())
            earned = currTokenCount - lastViewedTokenCount if currTokenCount >= lastViewedTokenCount else currTokenCount
            model.setId(epicQuestId)
            model.setTotal(dqToken.getNeededCount())
            model.setCurrent(currTokenCount)
            model.setEarned(earned)
            epicQuestBonusesModel = model.getBonuses()
            epicQuestBonusesModel.clear()
            self._tooltipData[epicQuestId] = {}
            self._rewardsGetterByQuestID[epicQuestId] = self.viewModel.epicQuestProgress.getBonuses
            packQuestBonusModelAndTooltipData(getDailyMissionsBonusPacker(), epicQuestBonusesModel, epicQuest, tooltipData=self._tooltipData[epicQuestId])
            return

    def _updateBattlePassData(self, vm):
        if self._winbackData:
            isBattlePassActive = self.battlePassController.isActive()
            vm.winBackProgress.setIsBattlePassActive(isBattlePassActive)

    def _updateOffersData(self, vm):
        wrtl = getWinbackRewardsTimeLeft(winbackController=self.winbackController)
        vm.epicQuestProgress.setWinBackTimeLeft(wrtl)
        if self._winbackData:
            offersState = self._getWinbackOffersState()
            vm.winBackProgress.setOffersState(offersState)
            vm.winBackProgress.setTimeLeftToClaim(wrtl)

    def _getWinbackOffersState(self):
        if self.winbackController.hasWinbackOfferToken() and self.winbackController.winbackConfig.isEnabled:
            if self.lobbyContext.getServerSettings().isOffersEnabled() and self.winbackController.winbackConfig.isProgressionEnabled:
                return OffersState.AVAILABLE
            return OffersState.DISABLED
        return OffersState.NO_OFFERS

    def _onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff:
            dqDiff = diff[DAILY_QUESTS_CONFIG]
            epicRewardEnabled = self.viewModel.getProgressType() == RewardProgressTypes.EPICQUEST
            epicRewardEnabledChanged = 'epicRewardEnabled' in dqDiff and dqDiff['epicRewardEnabled'] != epicRewardEnabled
            with self.viewModel.transaction() as tx:
                if epicRewardEnabledChanged:
                    self._updateModel(tx)
        if OFFERS_ENABLED_KEY in diff:
            with self.viewModel.transaction() as tx:
                self._updateOffersData(tx)

    def _onWinbackConfigUpdated(self, *_):
        self._updateWinbackData()
        with self.viewModel.transaction() as vm:
            self._updateModel(vm)
            self._updateCommonData(vm)

    def _onUpdateBattlePassData(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            self._updateBattlePassData(vm)

    def _onTakeAllReward(self):
        showWinbackSelectRewardView()

    def _onTakeReward(self, args):
        questNumber = args.get('questNumber')
        if not questNumber:
            return
        else:
            offer = self._winbackData.get('quests', {}).get(int(questNumber), {}).get('offer')
            if offer is not None:
                showWinbackSelectRewardView([offer.token])
            return
