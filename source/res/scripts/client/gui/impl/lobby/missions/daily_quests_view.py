# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/daily_quests_view.py
import typing
import logging
from constants import PREMIUM_TYPE, PremiumConfigs, DAILY_QUESTS_CONFIG
from frameworks.wulf import Array, ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.battle_pass.battle_pass_helpers import showBattlePassDailyQuestsIntro
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.shared.event_dispatcher import showShop
from shared_utils import first
from gui import SystemMessages
from gui.impl.backport.backport_tooltip import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.daily_quests_view_model import DailyQuestsViewModel
from gui.impl.lobby.reroll_tooltip import RerollTooltip
from gui.impl.pub import ViewImpl
from gui.impl.gui_decorators import args2params
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.server_events import settings, daily_quests
from gui.server_events.events_helpers import premMissionsSortFunc, dailyQuestsSortFunc, isPremiumQuestsEnable, isDailyQuestsEnable, isRerollEnabled, isEpicQuestEnabled, EventInfoModel, getRerollTimeout
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from gui.shared.missions.packers.events import getEventUIDataPacker, packQuestBonusModelAndTooltipData
from gui.shared.utils import decorators
from helpers import dependency, time_utils
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IGameSessionController, IBattlePassController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, List
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.impl.gen.view_models.views.lobby.missions.epic_quest_model import EpicQuestModel
    from gui.server_events.event_items import Quest
    from frameworks.wulf.view.view_event import ViewEvent
    from frameworks.wulf.windows_system.window import Window
_logger = logging.getLogger(__name__)

class DailyTabs(object):
    QUESTS = 0
    PREMIUM_MISSIONS = 1


DEFAULT_DAILY_TAB = DailyTabs.QUESTS

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isPremiumPlusAccount(itemsCache=None):
    return itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)


class DailyQuestsView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    gameSession = dependency.descriptor(IGameSessionController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    battlePassController = dependency.descriptor(IBattlePassController)
    __slots__ = ('__tooltipData', '__proxyMissionsPage')

    def __init__(self, layoutID=R.views.lobby.missions.Daily()):
        viewSettings = ViewSettings(layoutID, ViewFlags.COMPONENT, DailyQuestsViewModel())
        super(DailyQuestsView, self).__init__(viewSettings)
        self.__tooltipData = {}
        self.__proxyMissionsPage = None
        return

    @property
    def viewModel(self):
        return super(DailyQuestsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        _logger.debug('DailyQuests::createToolTipContent')
        if contentID == R.views.lobby.missions.RerollTooltip():
            return RerollTooltip(self.__getCountdown(), getRerollTimeout())
        return RerollTooltip(self.__getCountdown(), getRerollTimeout(), True) if contentID == R.views.lobby.missions.RerollTooltipWithCountdown() else super(DailyQuestsView, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        missionParam = event.getArgument('tooltipId', '')
        if not missionParam:
            return super(DailyQuestsView, self).createToolTip(event)
        else:
            missionParams = missionParam.rsplit(':', 1)
            if len(missionParams) != 2:
                _logger.error('TooltipId argument has invalid format.')
                return
            missionId, tooltipId = missionParams
            _logger.debug('CreateTooltip: %s, %s', missionId, tooltipId)
            tooltipsData = self.__tooltipData.get(missionId, {})
            tooltipData = tooltipsData.get(int(tooltipId))
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
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
        with self.viewModel.transaction() as tx:
            self._updateQuestsTitles(tx)
            self._updateModel(tx)
            self._updateCountDowns(tx)
            tx.setPremMissionsTabDiscovered(settings.getDQSettings().premMissionsTabDiscovered)
            tx.setIsBattlePassActive(self.battlePassController.isActive())

    def _onLoaded(self, *args, **kwargs):
        showBattlePassDailyQuestsIntro()

    def _initialize(self, *args, **kwargs):
        super(DailyQuestsView, self)._initialize()
        self.__addListeners()

    def _finalize(self):
        self.__proxyMissionsPage = None
        self.__removeListeners()
        super(DailyQuestsView, self)._finalize()
        return

    def _updateModel(self, model):
        self._updatePremiumMissionsModel(model)
        self._updateDailyQuestModel(model)
        self._updateEpicQuestModel(model)

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
            isTokeCountChanged = self.itemsCache.items.tokens.hasTokenCountChanged(dqToken.getID())
            isTokenNeededChanged = dqToken.getNeededCount() != tx.getTotal()
            isEpicQuestIdChanged = epicQuestId != tx.getId()
            if not fullUpdate and not isTokeCountChanged and not isEpicQuestIdChanged and not isTokenNeededChanged:
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

    def _onPremiumTypeChanged(self, _):
        with self.viewModel.transaction() as tx:
            self._updatePremiumMissionsModel(tx)
            self._updateCountDowns(tx)
            self._markVisited(tx.getCurrentTabIdx(), tx)

    def _onSyncCompleted(self, *_):
        with self.viewModel.transaction() as tx:
            self._updateModel(tx)
            self._markVisited(tx.getCurrentTabIdx(), tx)

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
        if PremiumConfigs.PREM_QUESTS in diff:
            premDiff = diff[PremiumConfigs.PREM_QUESTS]
            stateChanged = 'enabled' in premDiff and premDiff['enabled'] is not self.viewModel.premiumMissions.getIsEnabled()
            if stateChanged:
                with self.viewModel.transaction() as tx:
                    self._updatePremiumMissionsModel(tx)
                    if not premDiff['enabled']:
                        self.__setCurrentTab(DailyTabs.QUESTS, tx)

    def _updateQuestsTitles(self, model):
        model.premiumMissions.setTitle(R.strings.quests.premiumQuests.header.title())
        model.dailyQuests.setTitle(R.strings.quests.dailyQuests.header.title())

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

    @decorators.process('dailyQuests/waitReroll')
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

    def __addListeners(self):
        self.viewModel.onBuyPremiumBtnClick += self.__onBuyPremiumBtn
        self.viewModel.onTabClick += self.__onTabClick
        self.viewModel.onInfoToggle += self.__onInfoToggle
        self.viewModel.onClose += self.__onCloseView
        self.viewModel.onReroll += self.__onReRoll
        self.viewModel.onRerollEnabled += self.__onRerollEnabled
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self.gameSession.onPremiumTypeChanged += self._onPremiumTypeChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChanged

    def __removeListeners(self):
        self.viewModel.onBuyPremiumBtnClick -= self.__onBuyPremiumBtn
        self.viewModel.onTabClick -= self.__onTabClick
        self.viewModel.onInfoToggle -= self.__onInfoToggle
        self.viewModel.onClose -= self.__onCloseView
        self.viewModel.onReroll -= self.__onReRoll
        self.viewModel.onRerollEnabled -= self.__onRerollEnabled
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.gameSession.onPremiumTypeChanged -= self._onPremiumTypeChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChanged

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
