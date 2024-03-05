# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/daily_quests_view.py
import logging
from collections import defaultdict, OrderedDict
from copy import deepcopy
import typing
from constants import PREMIUM_TYPE, PremiumConfigs, DAILY_QUESTS_CONFIG, OFFERS_ENABLED_KEY
from frameworks.wulf import Array, ViewFlags, ViewSettings
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.impl.backport.backport_tooltip import BackportTooltipWindow, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.daily_quests_view_model import DailyQuestsViewModel, DailyTypes, OffersState
from gui.impl.gen.view_models.views.lobby.missions.winback_quest_model import WinbackQuestModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.impl.lobby.reroll_tooltip import RerollTooltip
from gui.impl.lobby.winback.tooltips.main_reward_tooltip import MainRewardTooltip
from gui.impl.lobby.winback.tooltips.selectable_reward_tooltip import SelectableRewardTooltip
from gui.impl.lobby.winback.winback_bonus_packer import getWinbackBonusPacker, getWinbackBonuses, packWinBackBonusModelAndTooltipData, cutWinbackTokens
from gui.impl.lobby.winback.winback_helpers import WinbackQuestTypes, getWinbackCompletedQuestsCount
from gui.impl.pub import ViewImpl
from gui.selectable_reward.common import WinbackSelectableRewardManager
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events import settings, daily_quests, conditions
from gui.server_events.bonuses import mergeBonuses, getMergedBonusesFromDicts
from gui.server_events.events_helpers import premMissionsSortFunc, dailyQuestsSortFunc, isPremiumQuestsEnable, isDailyQuestsEnable, isRerollEnabled, isEpicQuestEnabled, EventInfoModel, getRerollTimeout
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showShop, showWinbackSelectRewardView
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from gui.shared.missions.packers.events import getEventUIDataPacker, packQuestBonusModelAndTooltipData
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from shared_utils import first, findFirst
from skeletons.gui.game_control import IGameSessionController, IBattlePassController, IWinbackController, IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.impl.gen.view_models.views.lobby.missions.epic_quest_model import EpicQuestModel
    from gui.impl.gen.view_models.views.lobby.missions.winback_progression_model import WinbackProgressionModel
    from gui.server_events.bonuses import SimpleBonus, SelectableBonus
    from gui.server_events.event_items import Quest
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from frameworks.wulf.view.view_event import ViewEvent
    from frameworks.wulf.windows_system.window import Window
_logger = logging.getLogger(__name__)

class DailyTabs(object):
    QUESTS = 0
    PREMIUM_MISSIONS = 1


DEFAULT_DAILY_TAB = DailyTabs.QUESTS
ONE_MONTH = time_utils.ONE_DAY * 30

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isPremiumPlusAccount(itemsCache=None):
    return itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)


class DailyQuestsView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    battlePassController = dependency.descriptor(IBattlePassController)
    __winbackController = dependency.descriptor(IWinbackController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __slots__ = ('__tooltipData', '__proxyMissionsPage', '__winbackData')

    def __init__(self, layoutID=R.views.lobby.missions.Daily()):
        viewSettings = ViewSettings(layoutID, ViewFlags.VIEW, DailyQuestsViewModel())
        super(DailyQuestsView, self).__init__(viewSettings)
        self.__tooltipData = {}
        self.__proxyMissionsPage = None
        self.__winbackData = {}
        return

    @property
    def viewModel(self):
        return super(DailyQuestsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        _logger.debug('DailyQuests::createToolTipContent')
        if contentID == R.views.lobby.missions.RerollTooltip():
            return RerollTooltip(self.__getCountdown(), getRerollTimeout())
        if contentID == R.views.lobby.missions.RerollTooltipWithCountdown():
            return RerollTooltip(self.__getCountdown(), getRerollTimeout(), True)
        if contentID == R.views.lobby.winback.tooltips.SelectableRewardTooltip():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = self.__tooltipData.get(tooltipId)
            if tooltipData:
                return SelectableRewardTooltip(**tooltipData)
        if contentID == R.views.lobby.winback.tooltips.MainRewardTooltip():
            return MainRewardTooltip(self.__winbackData.get('lastQuest', {}).get('bonuses', []))
        lootBoxRes = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')
        if lootBoxRes.exists() and contentID == lootBoxRes():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            missionId, tooltipId = event.getArgument('tooltipId', '').rsplit(':', 1)
            tooltipData = self.__tooltipData.get(missionId, {}).get(tooltipId)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        return super(DailyQuestsView, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        missionParam = event.getArgument('tooltipId', '')
        if not missionParam:
            return super(DailyQuestsView, self).createToolTip(event)
        else:
            missionParams = missionParam.rsplit(':', 1)
            if len(missionParams) != 2:
                tooltipData = self.__tooltipData.get(missionParam)
            else:
                missionId, tooltipId = missionParams
                _logger.debug('CreateTooltip: %s, %s', missionId, tooltipId)
                tooltipsData = self.__tooltipData.get(missionId, {})
                tooltipData = tooltipsData.get(tooltipId)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
                if window is not None:
                    window.load()
            else:
                window = super(DailyQuestsView, self).createToolTip(event)
            return window

    def setDefaultTab(self, tabIdx):
        dq = settings.getDQSettings()
        if tabIdx is None:
            tabIdx = dq.lastVisitedDQTabIdx if dq.lastVisitedDQTabIdx is not None else DEFAULT_DAILY_TAB
        if tabIdx == DailyTabs.QUESTS and not isDailyQuestsEnable():
            tabIdx = DailyTabs.PREMIUM_MISSIONS
        elif tabIdx == DailyTabs.PREMIUM_MISSIONS and not isPremiumQuestsEnable():
            tabIdx = DailyTabs.QUESTS
        _logger.debug('PremiumMissionsView:setDefaultTab: tabIdx=%s', tabIdx)
        self.__setCurrentTab(tabIdx, self.viewModel)
        return

    def changeTab(self, tabIdx):
        with self.viewModel.transaction() as tx:
            if tabIdx == DailyTabs.QUESTS:
                self._updateDailyQuestModel(tx, True)
            elif tabIdx == DailyTabs.PREMIUM_MISSIONS:
                self._updatePremiumMissionsModel(tx, True)
            self._updateCountDowns(tx)
            self.__setCurrentTab(tabIdx, tx)

    def markVisited(self):
        self._markVisited(self.viewModel.getCurrentTabIdx(), self.viewModel)

    def resetInfoPageVisibility(self):
        if self.viewModel.getInfoVisible():
            self.viewModel.setInfoVisible(False)

    def setProxy(self, proxy):
        self.__proxyMissionsPage = proxy

    def _onLoading(self, *args, **kwargs):
        _logger.info('DailyQuestsView::_onLoading')
        super(DailyQuestsView, self)._onLoading()
        self.__updateWinbackData()
        with self.viewModel.transaction() as tx:
            self._updateQuestsTitles(tx)
            self._updateModel(tx)
            self._updateCountDowns(tx)
            tx.setPremMissionsTabDiscovered(settings.getDQSettings().premMissionsTabDiscovered)
        self.__updateCommonData()

    def _finalize(self):
        self.__proxyMissionsPage = None
        super(DailyQuestsView, self)._finalize()
        return

    def _updateModel(self, model):
        self._updatePremiumMissionsModel(model)
        self._updateDailyQuestModel(model)
        self._updateEpicQuestModel(model)
        self._updateWinbackProgressionModel(model)

    def _updateDailyQuestModel(self, model, fullUpdate=False):
        _logger.debug('DailyQuestsView::_updateDailyQuestModel')
        isEnabled = isDailyQuestsEnable()
        quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        newBonusQuests = settings.getNewCommonEvents([ q for q in quests if q.isBonus() ])
        self._updateRerollEnabledFlag(model)
        with model.dailyQuests.transaction() as tx:
            tx.setIsEnabled(isEnabled)
            if not isEnabled:
                return
            if not fullUpdate and not needToUpdateQuestsInModel(quests + newBonusQuests, tx.getQuests()):
                return
            self.__updateQuestsInModel(tx.getQuests(), quests)
            self.__updateMissionVisitedArray(tx.getMissionsCompletedVisited(), quests)
            tx.setBonusMissionVisited(not newBonusQuests)

    def _updateEpicQuestModel(self, model, fullUpdate=False):
        _logger.debug('DailyQuestsView::_updateEpicQuestModel')
        epicQuest = self.eventsCache.getDailyEpicQuest()
        isEnabled = isEpicQuestEnabled() and epicQuest is not None
        with model.epicQuest.transaction() as tx:
            tx.setIsEnabled(isEnabled)
            if not isEnabled:
                _logger.info('Daily Quest Screen: Epic quest is not enabled.')
                return
            epicQuestId = epicQuest.getID()
            dqToken = first((t for t in epicQuest.accountReqs.getTokens() if t.isDailyQuest()))
            if dqToken is None:
                _logger.error('Epic quest does not require any dq tokens to complete.')
                return
            isTokenCountChanged = self.itemsCache.items.tokens.hasTokenCountChanged(dqToken.getID())
            isTokenNeededChanged = dqToken.getNeededCount() != tx.getTotal()
            isEpicQuestIdChanged = epicQuestId != tx.getId()
            if not fullUpdate and not isTokenCountChanged and not isEpicQuestIdChanged and not isTokenNeededChanged:
                return
            _logger.debug('DailyQuestsView::__updateQuestInModel')
            lastViewedTokenCount = self.itemsCache.items.tokens.getLastViewedProgress(dqToken.getID())
            currTokenCount = self.eventsCache.questsProgress.getTokenCount(dqToken.getID())
            earned = currTokenCount - lastViewedTokenCount if currTokenCount >= lastViewedTokenCount else currTokenCount
            tx.setId(epicQuestId)
            tx.setTotal(dqToken.getNeededCount())
            tx.setCurrent(currTokenCount)
            tx.setEarned(earned)
            epicQuestBonusesModel = tx.getBonuses()
            epicQuestBonusesModel.clear()
            self.__tooltipData[epicQuestId] = {}
            packQuestBonusModelAndTooltipData(getDefaultBonusPacker(), epicQuestBonusesModel, epicQuest, tooltipData=self.__tooltipData[epicQuestId])
            epicQuestBonusesModel.invalidate()
        return

    def _updatePremiumMissionsModel(self, model, fullUpdate=False):
        _logger.debug('DailyQuestsView::_updatePremiumMissionsModel')
        quests = sorted(self.eventsCache.getPremiumQuests().values(), cmp=premMissionsSortFunc)
        isPremAcc = _isPremiumPlusAccount()
        isEnabled = isPremiumQuestsEnable()
        with model.premiumMissions.transaction() as tx:
            tx.setIsPremiumAccount(isPremAcc)
            tx.setIsEnabled(isEnabled)
            if not isPremAcc or not isEnabled:
                return
            missionsModel = tx.getMissions()
            if not fullUpdate and not needToUpdateQuestsInModel(quests, missionsModel):
                return
            self.__updateQuestsInModel(missionsModel, quests)
            self.__updateMissionVisitedArray(tx.getMissionsCompletedVisited(), quests)

    def _updateWinbackProgressionModel(self, model, fullUpdate=False):
        if self.__winbackData:
            model.winbackProgression.setCountCompleted(self.__winbackData.get('dailyQuestTokensCount', 0))
            self.__setWinbackTotalQuestsCount(model.winbackProgression, fullUpdate)
            self.__updateWinbackQuests(model.winbackProgression)

    def _onPremiumTypeChanged(self, _):
        with self.viewModel.transaction() as tx:
            self._updatePremiumMissionsModel(tx)
            self._updateCountDowns(tx)
            self._markVisited(tx.getCurrentTabIdx(), tx)

    def _onSyncCompleted(self, *_):
        self.__updateWinbackData()
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
            self._markVisited(tx.getCurrentTabIdx(), tx)
        self.__updateCommonData()

    def _onServerSettingsChanged(self, diff=None):
        diff = diff or {}
        if DAILY_QUESTS_CONFIG in diff:
            dqDiff = diff[DAILY_QUESTS_CONFIG]
            rerollStateChanged = 'rerollEnabled' in dqDiff and dqDiff['rerollEnabled'] is not self.viewModel.dailyQuests.getRerollEnabled()
            stateChanged = 'enabled' in dqDiff and dqDiff['enabled'] is not self.viewModel.dailyQuests.getIsEnabled()
            rerollTimeoutChanged = 'rerollTimeout' in dqDiff and dqDiff['rerollTimeout'] != self.viewModel.dailyQuests.getRerollTimeout()
            epicRewardEnabledChanged = 'epicRewardEnabled' in dqDiff and dqDiff['epicRewardEnabled'] != self.viewModel.epicQuest.getIsEnabled()
            with self.viewModel.transaction() as tx:
                if epicRewardEnabledChanged:
                    self._updateEpicQuestModel(tx)
                if rerollStateChanged:
                    self._updateRerollEnabledFlag(tx)
                if rerollTimeoutChanged:
                    self._updateCountdownUntilNextReroll(tx)
                if stateChanged:
                    self._updateDailyQuestModel(tx)
                    if not dqDiff['enabled']:
                        self.__setCurrentTab(DailyTabs.PREMIUM_MISSIONS, tx)
                self.__triggerSyncInitiator(self.viewModel.dailyQuests)
        if PremiumConfigs.PREM_QUESTS in diff:
            premDiff = diff[PremiumConfigs.PREM_QUESTS]
            stateChanged = 'enabled' in premDiff and premDiff['enabled'] is not self.viewModel.premiumMissions.getIsEnabled()
            if stateChanged:
                with self.viewModel.transaction() as tx:
                    self._updatePremiumMissionsModel(tx)
                    if not premDiff['enabled']:
                        self.__setCurrentTab(DailyTabs.QUESTS, tx)
                    self.__triggerSyncInitiator(self.viewModel.premiumMissions)
        if OFFERS_ENABLED_KEY in diff:
            self.__updateOffersData()

    def __triggerSyncInitiator(self, model):
        model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)

    def _updateQuestsTitles(self, model):
        dailyType = DailyTypes.WINBACK.value if self.__winbackData else DailyTypes.DEFAULT.value
        model.dailyQuests.setTitle(R.strings.quests.dailyQuests.header.dyn(dailyType)())
        model.premiumMissions.setTitle(R.strings.quests.premiumQuests.header.dyn(dailyType)())

    def _updateRerollEnabledFlag(self, model):
        model.dailyQuests.setRerollEnabled(isRerollEnabled())

    def _updateCountDowns(self, model):
        _logger.debug('DailyQuestsView::__updateCountDowns')
        self._updateCountdownUntilNextDay(model)
        self._updateCountdownUntilNextReroll(model)

    def _updateCountdownUntilNextDay(self, model):
        dailyResetTimeDelta = EventInfoModel.getDailyProgressResetTimeDelta()
        model.setCountDown(int(dailyResetTimeDelta))

    def _updateCountdownUntilNextReroll(self, model):
        countdown = self.__getCountdown()
        timeout = getRerollTimeout()
        with model.dailyQuests.transaction() as tx:
            tx.setRerollCountDown(countdown)
            tx.setRerollTimeout(timeout)

    def _markVisited(self, tabIdx, model):
        if not self.__proxyMissionsPage or self.__proxyMissionsPage.getCurrentTabAlias() != QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS:
            return
        seenQuests = []
        if tabIdx == DailyTabs.QUESTS:
            dailyQuests = self.eventsCache.getDailyQuests().values()
            seenQuests = dailyQuests
        elif tabIdx == DailyTabs.PREMIUM_MISSIONS:
            if _isPremiumPlusAccount():
                premiumQuests = self.eventsCache.getPremiumQuests().values()
                seenQuests = premiumQuests
            with settings.dailyQuestSettings() as dq:
                if isPremiumQuestsEnable() and not dq.premMissionsTabDiscovered:
                    dq.onPremMissionsTabDiscovered()
                    model.setPremMissionsTabDiscovered(dq.premMissionsTabDiscovered)
        for seenQuest in seenQuests:
            self.eventsCache.questsProgress.markQuestProgressAsViewed(seenQuest.getID())

        if isEpicQuestEnabled():
            epicQuest = self.eventsCache.getDailyEpicQuest()
            if epicQuest:
                seenQuests.append(epicQuest)
                dqToken = first((token for token in epicQuest.accountReqs.getTokens() if token.isDailyQuest()))
                if dqToken:
                    self.itemsCache.items.tokens.markTokenProgressAsViewed(dqToken.getID())
        settings.visitEventsGUI(seenQuests)
        self.__updateMissionsNotification()

    def _getCallbacks(self):
        return (('tokens', self._onSyncCompleted),)

    def _getEvents(self):
        return ((self.viewModel.onBuyPremiumBtnClick, self.__onBuyPremiumBtn),
         (self.viewModel.onTabClick, self.__onTabClick),
         (self.viewModel.onInfoToggle, self.__onInfoToggle),
         (self.viewModel.onClose, self.__onCloseView),
         (self.viewModel.onReroll, self.__onReRoll),
         (self.viewModel.onRerollEnabled, self.__onRerollEnabled),
         (self.viewModel.onClaimRewards, self.__onClaimRewards),
         (self.viewModel.winbackProgression.onTakeReward, self.__onTakeReward),
         (self.eventsCache.onSyncCompleted, self._onSyncCompleted),
         (self.gameSession.onPremiumTypeChanged, self._onPremiumTypeChanged),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged),
         (self.battlePassController.onBattlePassSettingsChange, self.__updateBattlePassData),
         (self.__comp7Controller.onComp7ConfigChanged, self.__updateComp7Data),
         (self.__winbackController.onConfigUpdated, self.__onWinbackConfigUpdated))

    def __onBuyPremiumBtn(self):
        showShop(getBuyPremiumUrl())

    @args2params(int)
    def __onTabClick(self, tabIdx):
        self.changeTab(tabIdx)

    def __onInfoToggle(self):
        with self.viewModel.transaction() as tx:
            isVisible = tx.getInfoVisible()
            if not isVisible:
                tabIdx = self.viewModel.getCurrentTabIdx()
                if tabIdx == DailyTabs.QUESTS:
                    self._updateDailyQuestModel(tx, True)
                elif tabIdx == DailyTabs.PREMIUM_MISSIONS:
                    self._updatePremiumMissionsModel(tx, True)
                self._updateEpicQuestModel(tx, True)
                self._updateWinbackProgressionModel(tx, True)
            self._updateCountDowns(tx)
            tx.setInfoVisible(not isVisible)

    def __onCloseView(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)

    def __setCurrentTab(self, tabIdx, model):
        model.setCurrentTabIdx(tabIdx)
        self._markVisited(tabIdx, model)
        with settings.dailyQuestSettings() as dq:
            dq.setLastVisitedDQTab(tabIdx)

    def __updateMissionsNotification(self):
        quests = self.eventsCache.getAdvisableQuests()
        counter = len(settings.getNewCommonEvents(quests.values()))
        self.eventsCache.onEventsVisited({'missions': counter})

    @decorators.adisp_process('dailyQuests/waitReroll')
    @args2params(str)
    def __onReRoll(self, questId):
        quests = self.eventsCache.getDailyQuests()
        if questId not in quests:
            _logger.error('Attempted to reroll quest which does not exist, reroll cancelled.')
            return
        quest = quests[questId]
        result = yield daily_quests.DailyQuestReroll(quest).request()
        if result.success:
            with self.viewModel.transaction() as tx:
                self._markVisited(tx.getCurrentTabIdx(), tx)
                self._updateCountdownUntilNextReroll(tx)
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __getCountdown(self):
        return int(max(self.eventsCache.dailyQuests.getNextAvailableRerollTimestamp() - time_utils.getCurrentLocalServerTimestamp(), 0))

    def __onRerollEnabled(self):
        self.viewModel.dailyQuests.setRerollCountDown(0)

    def __updateQuestsInModel(self, questsInModelToUpdate, sortedNewQuests):
        _logger.debug('DailyQuestsView::__updateQuestsInModel')
        for mission in questsInModelToUpdate:
            self.__tooltipData.pop(mission.getId(), None)

        questsInModelToUpdate.clear()
        questsInModelToUpdate.reserve(len(sortedNewQuests))
        for quest in sortedNewQuests:
            packer = getEventUIDataPacker(quest)
            questsInModelToUpdate.addViewModel(packer.pack())
            tooltipData = packer.getTooltipData()
            self.__tooltipData[quest.getID()] = tooltipData

        questsInModelToUpdate.invalidate()
        return

    def __updateMissionVisitedArray(self, missionVisitedArray, quests):
        missionVisitedArray.clear()
        missionVisitedArray.reserve(len(quests))
        for quest in quests:
            missionCompletedVisited = not self.eventsCache.questsProgress.getQuestCompletionChanged(quest.getID())
            missionVisitedArray.addBool(missionCompletedVisited)

        missionVisitedArray.invalidate()

    def __updateCommonData(self, *_):
        self.__updateDailyType()
        self.__updateBattlePassData()
        self.__updateComp7Data()
        self.__updateOffersData()

    def __updateDailyType(self, *_):
        if self.__winbackData:
            self.viewModel.setDailyType(DailyTypes.WINBACK)
        else:
            self.viewModel.setDailyType(DailyTypes.DEFAULT)

    def __updateBattlePassData(self, *_):
        isBattlePassActive = self.battlePassController.isActive()
        self.viewModel.setIsBattlePassActive(isBattlePassActive)
        if self.__winbackData:
            self.viewModel.winbackProgression.setIsBattlePassActive(isBattlePassActive)

    def __updateComp7Data(self, *_):
        self.viewModel.setIsComp7Active(self.__comp7Controller.isEnabled())

    def __updateOffersData(self, *_):
        offersState = self.__getWinbackOffersState()
        self.viewModel.setOffersState(offersState)
        self.viewModel.setGetRewardsTimeLeft(self.__getWinbackRewardsTimeLeft())
        if self.__winbackData:
            self.viewModel.winbackProgression.setOffersState(offersState)

    def __onWinbackConfigUpdated(self, *_):
        self.__updateWinbackData()
        with self.viewModel.transaction() as tx:
            self._updateWinbackProgressionModel(tx)
        self.__updateCommonData()

    def __updateWinbackData(self):
        if self.__winbackData:
            self.__winbackData.clear()
        if not self.__winbackController.isProgressionAvailable():
            return
        winbackQuests = self.__winbackController.winbackQuests
        if not winbackQuests:
            return
        dailyQuestTokensCount = getWinbackCompletedQuestsCount()
        self.__winbackData['dailyQuestTokensCount'] = dailyQuestTokensCount
        sortedQuests = self.__getSortedWinbackQuests(winbackQuests, dailyQuestTokensCount)
        questsData = self.__getWinbackQuestsData(sortedQuests, dailyQuestTokensCount)
        self.__winbackData['quests'] = questsData
        lastQuestData = self.__getLastWinbackQuestData(sortedQuests)
        self.__winbackData['lastQuest'] = lastQuestData

    def __getSortedWinbackQuests(self, winbackQuests, dailyQuestTokensCount):
        questsPairs = defaultdict(lambda : {WinbackQuestTypes.NORMAL: [],
         WinbackQuestTypes.COMPENSATION: []})
        for quest in winbackQuests.values():
            questNumber = self.__winbackController.getQuestIdx(quest)
            if questNumber > 0:
                questType = self.__winbackController.getQuestType(quest.getID())
                questsPairs[questNumber][questType].append(quest)

        quests = self.__filterWinbackQuests(questsPairs, dailyQuestTokensCount)
        return OrderedDict(sorted(quests, key=lambda item: item[0]))

    def __getWinbackQuestsData(self, sortedQuests, dailyQuestTokensCount):
        questsData = OrderedDict()
        for questNumber, quest in sortedQuests.iteritems():
            bonusesData = None
            received = True if dailyQuestTokensCount >= questNumber else False
            questsData[questNumber] = {}
            selectableBonus = findFirst(lambda b: b.getName() == SELECTABLE_BONUS_NAME, quest.getBonuses())
            if selectableBonus is not None:
                offer = WinbackSelectableRewardManager.getBonusOffer(selectableBonus)
                questsData[questNumber]['offer'] = offer
                if dailyQuestTokensCount >= questNumber and offer is not None and not offer.isOfferAvailable:
                    bonusesData = first(WinbackSelectableRewardManager.getBonusReceivedOptions(selectableBonus, WinbackSelectableRewardManager.giftRawBonusesExtractor))
                    rawQuestBonusesData = quest.getData().get('bonus', {})
                    questBonusesData = deepcopy(rawQuestBonusesData)
                    questBonusesData, _ = cutWinbackTokens(questBonusesData)
                    if bonusesData and questBonusesData:
                        bonusesData = getMergedBonusesFromDicts([bonusesData, questBonusesData])
            if bonusesData is None:
                bonusesData = quest.getData().get('bonus', {})
            questsData[questNumber]['bonuses'] = getWinbackBonuses(bonusesData, received=received)

        return questsData

    def __getLastWinbackQuestData(self, sortedQuests):
        lastQuestData = {}
        if not sortedQuests:
            return {}
        lastQuestNumber = max(sortedQuests)
        lastQuest = sortedQuests[lastQuestNumber]
        bonuses = self.__winbackData.get('quests', {}).get(lastQuestNumber, {}).get('bonuses', [])
        if bonuses:
            self.__extendLastQuestBonuses(bonuses)
        lastQuestData['bonuses'] = bonuses
        self.__winbackData['quests'][lastQuestNumber]['bonuses'] = []
        lastQuestDailyToken = first((t for t in lastQuest.accountReqs.getTokens() if t.isDailyQuest()))
        lastQuestData['token'] = lastQuestDailyToken
        return lastQuestData

    def __setWinbackTotalQuestsCount(self, model, fullUpdate=False):
        lastQuestToken = self.__winbackData.get('lastQuest').get('token')
        isTokenCountChanged = self.itemsCache.items.tokens.hasTokenCountChanged(lastQuestToken.getID())
        isTokenNeededChanged = lastQuestToken.getNeededCount() != model.getTotalQuests()
        if isTokenCountChanged or isTokenNeededChanged or fullUpdate:
            model.setTotalQuests(lastQuestToken.getNeededCount())
            model.setPreviousCompletedQuests(self.itemsCache.items.tokens.getLastViewedProgress(lastQuestToken.getID()))

    def __updateWinbackQuests(self, model):
        winbackQuests = model.getQuests()
        winbackQuests.clear()
        packer = getWinbackBonusPacker()
        for winbackQuestNumber, winbackQuestData in self.__winbackData.get('quests', {}).iteritems():
            winbackQuests.addViewModel(self.__createWinbackQuestModel(winbackQuestNumber, winbackQuestData, packer))

        winbackQuests.invalidate()

    def __createWinbackQuestModel(self, questNumber, questData, packer):
        winbackQuestModel = WinbackQuestModel()
        winbackQuestModel.setQuestNumber(questNumber)
        rewardsModel = winbackQuestModel.getRewards()
        rewardsModel.clear()
        packWinBackBonusModelAndTooltipData(questData['bonuses'], packer, rewardsModel, self.__tooltipData)
        rewardsModel.invalidate()
        return winbackQuestModel

    @staticmethod
    def __filterWinbackQuests(questsPairs, countCompletedQuests):
        result = []
        for questNumber, questPair in questsPairs.items():
            normal = first(questPair.get(WinbackQuestTypes.NORMAL))
            compensation = first(questPair.get(WinbackQuestTypes.COMPENSATION))
            if compensation is not None and compensation.getProgressData():
                result.append((questNumber, compensation))
            if normal is not None:
                if questNumber > countCompletedQuests:
                    for cond in normal.accountReqs.getConditions().items:
                        if isinstance(cond, conditions.VehiclesUnlocked):
                            if not cond.isAvailable():
                                result.append((questNumber, compensation))
                                break
                    else:
                        result.append((questNumber, normal))

                else:
                    result.append((questNumber, normal))

        return result

    def __extendLastQuestBonuses(self, winbackBonuses):
        epicQuest = self.eventsCache.getDailyEpicQuest()
        winbackBonuses.extend(epicQuest.getBonuses())
        mergeBonuses(winbackBonuses)
        return winbackBonuses

    def __onClaimRewards(self):
        showWinbackSelectRewardView()

    def __onTakeReward(self, args):
        questNumber = args.get('questNumber')
        if not questNumber:
            return
        else:
            offer = self.__winbackData.get('quests', {}).get(int(questNumber), {}).get('offer')
            if offer is not None:
                showWinbackSelectRewardView([offer.token])
            return

    def __getWinbackOffersState(self):
        if self.__winbackController.hasWinbackOfferToken() and self.__winbackController.winbackConfig.isEnabled:
            if self.lobbyContext.getServerSettings().isOffersEnabled() and self.__winbackController.winbackConfig.isProgressionEnabled:
                return OffersState.AVAILABLE
            return OffersState.DISABLED
        return OffersState.NO_OFFERS

    def __getWinbackRewardsTimeLeft(self):
        selectableBonus = first(WinbackSelectableRewardManager.getAvailableSelectableBonuses())
        if selectableBonus is None:
            return 0
        else:
            winbackOffer = WinbackSelectableRewardManager.getBonusOffer(selectableBonus)
            return max(0, min(winbackOffer.expiration - time_utils.getServerUTCTime(), ONE_MONTH)) if winbackOffer and self.__winbackController.isEnabled() and not self.__winbackController.isProgressionAvailable() else 0
