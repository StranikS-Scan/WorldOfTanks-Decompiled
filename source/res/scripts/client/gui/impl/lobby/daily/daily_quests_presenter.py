# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_presenter.py
import itertools
import logging
import typing
from constants import PremiumConfigs, DAILY_QUESTS_CONFIG, DailyQuestsLevels
from frameworks.wulf import Array
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_premium_model import DailyQuestsPremiumModel
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_regular_model import DailyQuestsRegularModel
from gui.impl.lobby.daily import DailyTabs
from gui.impl.lobby.daily.daily_helpers import modifyPostbattleConditions, isRegularQuestsStateChanged
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events import settings
from gui.server_events.events_helpers import dailyQuestsSortFunc, isPremiumQuestsEnable, isDailyRegularQuestsEnabled, isRerollEnabled, isEpicQuestEnabled, EventInfoModel, getRerollTimeout, isPremiumPlusAccount
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from gui.shared.missions.packers.events import getEventUIDataPacker, packQuestBonusModelAndTooltipData
from helpers import dependency, time_utils
from shared_utils import first
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List
    from gui.impl.gen.view_models.views.lobby.daily.epic_quest_model import EpicQuestModel
_logger = logging.getLogger(__name__)
DEFAULT_DAILY_TAB = DailyTabs.QUESTS

class DailyQuestsPresenterRegular(SubModelPresenter):
    __slots__ = ('__tooltipData', '_isActive')
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    subscriptionController = dependency.descriptor(IWotPlusController)

    def __init__(self, viewModel, view):
        super(DailyQuestsPresenterRegular, self).__init__(viewModel, view)
        self._isActive = None
        self.__tooltipData = view.tooltipData
        return

    @property
    def viewModel(self):
        return super(DailyQuestsPresenterRegular, self).getViewModel()

    def initialize(self, *args, **kwargs):
        if self._isActive:
            return
        super(DailyQuestsPresenterRegular, self).initialize(*args, **kwargs)
        self._isActive = True
        self._update()

    def finalize(self):
        super(DailyQuestsPresenterRegular, self).finalize()
        self._isActive = False

    def _isTabActive(self):
        return self.parentView.currentTabIdx == DailyTabs.QUESTS

    def _update(self):
        if not self._isActive or not self._isTabActive():
            return
        with self.viewModel.transaction() as model:
            self._updateModel(model=model)
            self._updateCountDowns(model)
            self._markVisited(self.parentView.currentTabIdx)

    @replaceNoneKwargsModel
    def _updateModel(self, model=None):
        isEnabled = isDailyRegularQuestsEnabled()
        model.setIsEnabled(isEnabled)
        if not isEnabled:
            return
        quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        self._updateRerollEnabledFlag(model)
        self._updateQuestsInModel(model.getQuests(), quests)
        self.__updateDailyQuestSubscriptionModel(model)

    def _updateQuestsInModel(self, questsInModelToUpdate, sortedNewQuests):
        for mission in questsInModelToUpdate:
            self.__tooltipData.pop(mission.getId(), None)

        questsInModelToUpdate.clear()
        questsInModelToUpdate.reserve(len(sortedNewQuests))
        for quest in sortedNewQuests:
            packer = getEventUIDataPacker(quest)
            questModel = packer.pack()
            modifyPostbattleConditions(quest, questModel)
            questsInModelToUpdate.addViewModel(questModel)
            tooltipData = packer.getTooltipData()
            self.__tooltipData[quest.getID()] = tooltipData

        questsInModelToUpdate.invalidate()
        return

    def __updateDailyQuestSubscriptionModel(self, model):
        isEnableSubsQuest = self.lobbyContext.getServerSettings().isDailyQuestsExtraRewardsEnabled()
        if not isEnableSubsQuest:
            return
        quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        questsSub = {quest.getID():first(self.eventsCache.getDailyQuestsSub(lambda q, qu=quest: not qu.isPremium() and q.getLevel() == DailyQuestsLevels.MAP_DAILY_QUESTS.get(qu.getLevel())).values()) for quest in quests}
        self.__addSubscriptionQuestsInModel(model.getQuests(), quests, questsSub)

    def _onSyncCompleted(self, *_):
        with self.viewModel.transaction() as model:
            self._updateModel(model=model)
            self._markVisited(self.parentView.currentTabIdx)

    def _onServerSettingsChanged(self, diff=None):
        if not self._isActive or not self._isTabActive():
            return
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff:
            dqDiff = diff[DAILY_QUESTS_CONFIG]
            rerollStateChanged = 'rerollEnabled' in dqDiff and dqDiff['rerollEnabled'] is not self.viewModel.getRerollEnabled()
            rerollTimeoutChanged = 'rerollTimeout' in dqDiff and dqDiff['rerollTimeout'] != getRerollTimeout()
            with self.viewModel.transaction() as model:
                if rerollStateChanged:
                    self._updateRerollEnabledFlag(model)
                if rerollTimeoutChanged:
                    self._updateCountdownUntilNextReroll(model)
                if isRegularQuestsStateChanged(self.viewModel.getIsEnabled(), dqDiff):
                    self._updateModel(model=model)

    def _updateRerollEnabledFlag(self, model):
        _isComplited = all((quest.isCompleted() for quest in self.eventsCache.getDailyQuests(filterLevels=DailyQuestsLevels.DAILY_SIMPLE).itervalues()))
        model.setRerollEnabled(isRerollEnabled() and not self.eventsCache.dailyQuests.isRerollInCooldown() and not _isComplited)

    def _updateCountDowns(self, model):
        self._updateCountdownUntilNextDay(model)
        self._updateCountdownUntilNextReroll(model=model)

    def _updateCountdownUntilNextDay(self, model):
        dailyResetTimeDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        model.setCountDown(int(dailyResetTimeDelta))

    @replaceNoneKwargsModel
    def _updateCountdownUntilNextReroll(self, model=None):
        countdown = self._getCountdown()
        model.setRerollCountDown(countdown)

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted), ('dailyQuests', self._onRerrollUpdate))

    def _onRerrollUpdate(self, diff):
        if any((i in diff for i in ('last_rerol_prem', 'last_reroll'))):
            self._updateCountdownUntilNextReroll()
            with self.viewModel.transaction() as model:
                self._updateRerollEnabledFlag(model)

    def _onSubscriptionUpdate(self, diff):
        if self._isTabActive():
            self._updateModel()

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted), (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged), (self.subscriptionController.onDataChanged, self._onSubscriptionUpdate))

    def _getCountdown(self):
        return int(max(self.eventsCache.dailyQuests.getNextAvailableRerollTimestamp() - time_utils.getCurrentLocalServerTimestamp(), 0))

    def __addSubscriptionQuestsInModel(self, questsInModelToUpdate, sortedQuests, subQuests):
        subscriptionEnable = self.subscriptionController.isWotPlusEnabled()
        subscriptionActive = self.subscriptionController.isEnabled()
        for questModel, quest in itertools.izip(questsInModelToUpdate, sortedQuests):
            questSub = subQuests.get(quest.getID())
            if questSub:
                packer = getEventUIDataPacker(questSub, self.__tooltipData[quest.getID()])
                packer.pack(model=questModel)
                self.__tooltipData[quest.getID()] = packer.getTooltipData()
                questModel.setIsEnabledSubscription(subscriptionEnable)
                questModel.setIsActiveSubscription(subscriptionActive)
                if quest.isCompleted() and not questSub.isCompleted():
                    questModel.setStatus(EventStatus.UNDONESUBSCRIPTION)

        questsInModelToUpdate.invalidate()

    def _markVisited(self, tabIdx):
        if not isDailyRegularQuestsEnabled():
            return
        if not self._isActive:
            return
        seenQuests = []
        if tabIdx == DailyTabs.QUESTS:
            dailyQuests = self.eventsCache.getDailyQuests().values()
            seenQuests = dailyQuests
        for seenQuest in seenQuests:
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuest.getID())

        _isComplited = all((quest.isCompleted() for quest in self.eventsCache.getDailyQuests(filterLevels=DailyQuestsLevels.DAILY_SIMPLE).itervalues()))
        bonusQuest = first(self.eventsCache.getDailyQuests(filterLevels=(DailyQuestsLevels.BONUS,)).values())
        if bonusQuest:
            with settings.dailyQuestSettings() as dq:
                if _isComplited and dq.lastBonusMissionVisited != bonusQuest.getID() and not bonusQuest.isCompleted():
                    self.viewModel.setFirstSeenNewBonusMissions(True)
                    dq.setLastBonusMissionVisited(bonusQuest.getID())
                else:
                    self.viewModel.setFirstSeenNewBonusMissions(False)


class DailyQuestsPresenterPremium(DailyQuestsPresenterRegular):

    def _isTabActive(self):
        return self.parentView.currentTabIdx == DailyTabs.PREMIUM

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted), (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged), (self.gameSession.onPremiumTypeChanged, self.__onPremiumChanged))

    @replaceNoneKwargsModel
    def _updateModel(self, model=None):
        isEnabled = isPremiumQuestsEnable()
        hasPremAcc = isPremiumPlusAccount()
        with model.transaction() as tx:
            tx.setHasPremiumAccount(hasPremAcc)
            tx.setIsEnabled(isEnabled)
            questsModel = tx.getQuests()
            if not isEnabled:
                questsModel.clear()
                questsModel.invalidate()
                return
            quests = sorted(self.eventsCache.getDailyPremiumQuests().values(), key=dailyQuestsSortFunc)
            self._updateQuestsInModel(questsModel, quests)
            self._updateRerollEnabledFlag(tx)

    def _getCountdown(self):
        return int(max(self.eventsCache.dailyQuests.getNextAvailableRerollTimestampPrem() - time_utils.getCurrentLocalServerTimestamp(), 0))

    def _updateRerollEnabledFlag(self, model):
        _isComplited = all((quest.isCompleted() for quest in self.eventsCache.getDailyPremiumQuests().itervalues()))
        model.setRerollEnabled(not self.eventsCache.dailyQuests.isRerollInCooldownPrem() and not _isComplited and isPremiumPlusAccount() and isPremiumQuestsEnable() and isRerollEnabled())

    def _onServerSettingsChanged(self, diff=None):
        if not self._isActive or not self._isTabActive():
            return
        super(DailyQuestsPresenterPremium, self)._onServerSettingsChanged(diff)
        diff = diff or {}
        if PremiumConfigs.PREM_QUESTS in diff:
            premDiff = diff[PremiumConfigs.PREM_QUESTS]
            stateChanged = 'enabled' in premDiff and premDiff['enabled'] is not self.viewModel.getIsEnabled()
            if stateChanged:
                with self.viewModel.transaction() as model:
                    self._updateModel(model=model)

    def __onPremiumChanged(self, _):
        self._update()
        self._markVisited(self.parentView.currentTabIdx)

    def _markVisited(self, tabIdx):
        if not isPremiumQuestsEnable():
            return
        if not self._isActive:
            return
        seenQuests = []
        if tabIdx == DailyTabs.PREMIUM:
            if isPremiumPlusAccount():
                premiumQuests = self.eventsCache.getDailyPremiumQuests().values()
                seenQuests = premiumQuests
        for seenQuest in seenQuests:
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuest.getID())

        _isComplited = any((quest.isCompleted() for quest in self.eventsCache.getDailyPremiumQuests().itervalues()))
        with settings.dailyQuestSettings() as dq:
            if isPremiumQuestsEnable() and isPremiumPlusAccount() and not dq.premMissionsTabDiscovered and not _isComplited:
                dq.setPremMissionsTabDiscovered(True)
                self.getViewModel().setPremMissionsTabDiscovered(True)
            elif not isPremiumPlusAccount():
                dq.setPremMissionsTabDiscovered(False)


class EpicQuestsPresenter(SubModelPresenter):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel, view):
        super(EpicQuestsPresenter, self).__init__(viewModel, view)
        self.__isActive = None
        self.__tooltipData = view.tooltipData
        return

    @property
    def viewModel(self):
        return super(EpicQuestsPresenter, self).getViewModel()

    def initialize(self, *args, **kwargs):
        if self.__isActive:
            return
        super(EpicQuestsPresenter, self).initialize(*args, **kwargs)
        self.__isActive = True
        self._update()

    def finalize(self):
        super(EpicQuestsPresenter, self).finalize()
        self.__isActive = False

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self._onSyncCompleted), (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _update(self):
        if not self.__isActive:
            return
        with self.viewModel.transaction() as model:
            self._updateModel(model)
            self._markVisited(self.parentView.currentTabIdx)

    def _updateModel(self, model):
        epicQuest = self.eventsCache.getDailyEpicQuest()
        isEnabled = isEpicQuestEnabled() and epicQuest is not None
        model.setIsEnabled(isEnabled)
        if not isEnabled:
            return
        else:
            model.setIsCompleted(epicQuest.isCompleted())
            epicQuestId = epicQuest.getID()
            dqToken = first((t for t in epicQuest.accountReqs.getTokens() if t.isDailyQuest()))
            if dqToken is None:
                return
            isTokenCountChanged = self.itemsCache.items.tokens.hasTokenCountChanged(dqToken.getID())
            isTokenNeededChanged = dqToken.getNeededCount() != model.getTotal()
            isEpicQuestIdChanged = epicQuestId != model.getId()
            if not isTokenCountChanged and not isEpicQuestIdChanged and not isTokenNeededChanged:
                return
            lastViewedTokenCount = self.itemsCache.items.tokens.getLastViewedProgress(dqToken.getID())
            currTokenCount = self.eventsCache.questsProgress.getTokenCount(dqToken.getID())
            earned = currTokenCount - lastViewedTokenCount if currTokenCount >= lastViewedTokenCount else currTokenCount
            model.setId(epicQuestId)
            model.setTotal(dqToken.getNeededCount())
            model.setCurrent(currTokenCount)
            model.setEarned(earned)
            weeklyResetTimeDelta = EventInfoModel.getWeeklyProgressResetTimeDelta()
            model.setCountDown(int(weeklyResetTimeDelta))
            epicQuestBonusesModel = model.getBonuses()
            epicQuestBonusesModel.clear()
            self.__tooltipData[epicQuestId] = {}
            packQuestBonusModelAndTooltipData(getDefaultBonusPacker(), epicQuestBonusesModel, epicQuest, tooltipData=self.__tooltipData[epicQuestId])
            epicQuestBonusesModel.invalidate()
            return

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted),)

    def _onSyncCompleted(self, *_):
        with self.viewModel.transaction() as model:
            self._updateModel(model)
            self._markVisited()

    def __onServerSettingsChanged(self, diff=None):
        if not self.__isActive:
            return
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff:
            dqDiff = diff[DAILY_QUESTS_CONFIG]
            epicRewardEnabledChanged = 'epicRewardEnabled' in dqDiff and dqDiff['epicRewardEnabled'] != self.viewModel.getIsEnabled()
            if epicRewardEnabledChanged:
                self._update()

    def _markVisited(self, tabIdx=None):
        if not isEpicQuestEnabled():
            return
        if not self.__isActive:
            return
        seenQuests = []
        if isEpicQuestEnabled():
            epicQuest = self.eventsCache.getDailyEpicQuest()
            if epicQuest:
                seenQuests.append(epicQuest)
                dqToken = first((token for token in epicQuest.accountReqs.getTokens() if token.isDailyQuest()))
                if dqToken:
                    self.itemsCache.items.tokens.markTokenProgressAsViewed(dqToken.getID())
