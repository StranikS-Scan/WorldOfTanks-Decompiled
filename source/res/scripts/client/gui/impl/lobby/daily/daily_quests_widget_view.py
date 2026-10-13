# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_widget_view.py
import logging
import BigWorld
import typing
from account_helpers.AccountSettings import AccountSettings, SESSION_PROGRESS_REWARDS_WIDGET_LAST_SEEN_STEP
from constants import PremiumConfigs, DAILY_QUESTS_CONFIG
from frameworks.wulf import Array, ViewFlags, WindowFlags
from frameworks.wulf.view.view import ViewSettings
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_widget_view_model import DailyQuestsWidgetViewModel
from gui.impl.gen.view_models.views.lobby.daily.widget_quest_model import WidgetQuestModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.daily.daily_helpers import needToUpdateQuestsInModel, modifyPostbattleConditions
from gui.impl.lobby.daily.tooltips.daily_quests_tooltip import DailyQuestsTooltip
from gui.impl.lobby.daily.tooltips.session_progress_rewards_tooltip import SessionProgressRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showDailyQuests
from gui.server_events.events_helpers import dailyQuestsSortFunc, EventInfoModel, isPremiumQuestsEnable, isDailyQuestsEnable
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.main_wnd_state_watcher import ClientMainWindowStateWatcher
from gui.shared.missions.packers.events import getEventUIDataPacker, findFirstConditionModel
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController, IGameSessionController, ISessionProgressRewardsController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
    from gui.server_events.event_items import ServerEventAbstract, DailyQuest
    from typing import Optional, Any
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
MOUSE_BUTTON_RIGHT = 2
MOUSE_BUTTON_LEFT = 0
LARGE_WIDGET_LAYOUT_ID = 0
MARK_VISITED_TIMEOUT = 1.0
SERIAL_ENTER_QUEST_ID = 'serialEnter:session'
SERIAL_ENTER_START_ANIMATION_DELAY = 4.0
SESSION_WIDGET_UNSEEN_STEP = -1
_logger = logging.getLogger(__name__)

def predicateTooltipWindow(window):
    return window.content is not None and window.typeFlag == WindowFlags.TOOLTIP


class DailyQuestsWidgetView(ViewImpl, ClientMainWindowStateWatcher):
    __slots__ = ('__parentId', '__tooltipEnabled', '__layout', '__visitedQuests', '__markVisitedCallbackID', '__sessionWidgetMarkVisitedCallbackID', '__sessionWidgetStartAnimationCallbackID')
    __eventsCache = dependency.descriptor(IEventsCache)
    subscriptionController = dependency.descriptor(IWotPlusController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    gameSession = dependency.descriptor(IGameSessionController)
    itemsCache = dependency.descriptor(IItemsCache)
    __sessionProgressRewardsController = dependency.descriptor(ISessionProgressRewardsController)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.daily.DailyQuestWidget(), ViewFlags.VIEW, DailyQuestsWidgetViewModel())
        super(DailyQuestsWidgetView, self).__init__(settings)
        self.__parentId = None
        self.__tooltipEnabled = True
        self.__layout = 0
        self.__visitedQuests = set()
        self.__markVisitedCallbackID = 0
        self.__sessionWidgetMarkVisitedCallbackID = 0
        self.__sessionWidgetStartAnimationCallbackID = 0
        return

    def setParentId(self, parentId):
        self.__parentId = parentId

    def createToolTipContent(self, event, contentID):
        _logger.debug('DailyQuests::createToolTipContent')
        if not self.__tooltipEnabled:
            return None
        elif contentID == R.views.lobby.daily.tooltips.SessionProgressRewardsTooltip():
            return SessionProgressRewardsTooltip()
        elif contentID == R.views.lobby.daily.tooltips.DailyQuestTooltip():
            groupID = event.getArgument('groupID')
            return DailyQuestsTooltip(groupID)
        else:
            return super(DailyQuestsWidgetView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(DailyQuestsWidgetView, self).getViewModel()

    def setLayout(self, value):
        self.__layout = value
        if self.getViewModel().getVisible():
            self._markVisited()

    def setVisible(self, value):
        if value == self.getViewModel().getVisible():
            return
        with self.getViewModel().transaction() as tx:
            if value:
                quests, premiumQuests = self.__getDailyAndPremiumQuests()
                self.__updateQuestsToBeIndicatedCompleted(tx, quests + premiumQuests, True)
                self.__packQuestsModel(tx.getQuests(), quests)
                self.__packQuestsModel(tx.getPremiumQuests(), premiumQuests)
                self.__packSerialEnterQuests(tx.getSerialEnterQuests())
            tx.setVisible(value)

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsWidgetView, self)._onLoading(*args, **kwargs)
        self._updateViewModel()

    def _initialize(self, *args, **kwargs):
        self.mainWindowWatcherInit()

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.viewModel.onQuestClick, self.__onQuestClick),
         (self.gameSession.onPremiumTypeChanged, self._onPremiumTypeChanged),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__sessionProgressRewardsController.onDataUpdated, self.__onSessionProgressRewardsDataUpdated))

    def _getListeners(self):
        return ((LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__onHelpLayoutHide, EVENT_BUS_SCOPE.LOBBY), (LobbySimpleEvent.SHOW_HELPLAYOUT, self.__onHelpLayoutShow, EVENT_BUS_SCOPE.LOBBY))

    def _finalize(self):
        self.mainWindowWatcherDestroy()
        if self.__markVisitedCallbackID != 0:
            BigWorld.cancelCallback(self.__markVisitedCallbackID)
        self.__cancelSessionWidgetMarkVisited()
        self.__cancelSessionWidgetStartAnimation()
        super(DailyQuestsWidgetView, self)._finalize()

    @classmethod
    def _getFirstConditionModelFromQuestModel(cls, dailyQuestModel):
        postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel

    def _onPremiumTypeChanged(self, *_):
        if not isPremiumQuestsEnable():
            return
        premiumQuests = sorted(self.__eventsCache.getDailyPremiumQuests().values(), key=dailyQuestsSortFunc)
        with self.getViewModel().transaction() as tx:
            modelPremiumQuests = tx.getPremiumQuests()
            self.__packQuestsModel(modelPremiumQuests, premiumQuests)

    def _updateViewModel(self):
        _logger.debug('DailyQuests::UpdatingViewModel')
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        quests, premiumQuests = self.__getDailyAndPremiumQuests()
        needUpdateQuests = needToUpdateQuestsInModel(quests, self.getViewModel().getQuests()) or needToUpdateQuestsInModel(premiumQuests, self.getViewModel().getPremiumQuests())
        with self.getViewModel().transaction() as tx:
            tx.setCountdown(newCountdownVal)
            self.__packSerialEnterQuests(tx.getSerialEnterQuests())
            if not needUpdateQuests:
                return
            modelQuests = tx.getQuests()
            modelPremiumQuests = tx.getPremiumQuests()
            self.__packQuestsModel(modelQuests, quests)
            self.__packQuestsModel(modelPremiumQuests, premiumQuests)
            self.__updateQuestsToBeIndicatedCompleted(tx, quests + premiumQuests, self.viewModel.getVisible())

    def _markVisited(self):
        if not isDailyQuestsEnable() or self.__layout != LARGE_WIDGET_LAYOUT_ID:
            return
        for quest in self.__eventsCache.getDailyQuests().values():
            self._scheduleMarkVisited(quest.getID())

    def _executeMarkVisited(self):
        for qid in self.__visitedQuests:
            self.__eventsCache.questsProgress.markQuestProgressAsViewed(qid)

        self.__visitedQuests.clear()
        self.__markVisitedCallbackID = 0

    def _scheduleMarkVisited(self, qid):
        self.__visitedQuests.add(qid)
        if self.__markVisitedCallbackID != 0:
            return
        self.__markVisitedCallbackID = BigWorld.callback(MARK_VISITED_TIMEOUT, self._executeMarkVisited)

    def _onClientMainWindowStateChanged(self, isWindowVisible):
        if isWindowVisible:
            with self.viewModel.transaction() as tx:
                newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
                tx.setCountdown(newCountdownVal)
                self.__packSerialEnterQuests(tx.getSerialEnterQuests())

    @args2params(int)
    def __onQuestClick(self, tabIdx):
        showDailyQuests(subTab=tabIdx)

    def __onHelpLayoutShow(self, _):
        windows = self.__gui.windowsManager.findWindows(predicateTooltipWindow)
        for window in windows:
            window.destroy()

        self.__tooltipEnabled = False

    def __onHelpLayoutHide(self, _):
        self.__tooltipEnabled = True

    def __onSyncCompleted(self, *_):
        self._updateViewModel()
        self._markVisited()

    def __onServerSettingsChanged(self, diff=None):
        if not diff:
            return
        if PremiumConfigs.PREM_QUESTS in diff:
            diffConfig = diff.get(PremiumConfigs.PREM_QUESTS)
            if 'enabled' in diffConfig:
                self._updateViewModel()
                return
        if DAILY_QUESTS_CONFIG in diff:
            self._updateViewModel()

    def __updateQuestsToBeIndicatedCompleted(self, viewModelTransaction, sortedQuests, markViewed):
        indicateCompleteQuests = viewModelTransaction.getIndicateCompleteQuests()
        indicateCompleteQuests.clear()
        indicateCompleteQuests.reserve(len(sortedQuests))
        for quest in sortedQuests:
            questCompletionChanged = self.__eventsCache.questsProgress.getQuestCompletionChanged(quest.getID())
            if questCompletionChanged and markViewed:
                self._scheduleMarkVisited(quest.getID())
            indicateCompleteQuests.addBool(questCompletionChanged)

        indicateCompleteQuests.invalidate()

    def __onSessionProgressRewardsDataUpdated(self):
        with self.getViewModel().transaction() as tx:
            self.__packSerialEnterQuests(tx.getSerialEnterQuests())

    def __getDailyAndPremiumQuests(self):
        if not isDailyQuestsEnable():
            return ([], [])
        quests = sorted(self.__eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        premiumQuests = sorted(self.__eventsCache.getDailyPremiumQuests().values(), key=dailyQuestsSortFunc) if isPremiumQuestsEnable() else []
        return (quests, premiumQuests)

    def __packSerialEnterQuests(self, model, startAnimation=False):
        if not self.__sessionProgressRewardsController.isAvailable:
            if model:
                model.clear()
                model.invalidate()
            return
        isRewardWasReceivedToday = self.__sessionProgressRewardsController.isRewardWasReceivedToday
        currentStep = self.__sessionProgressRewardsController.currentStep
        finalStep = self.__sessionProgressRewardsController.finalStep
        lastSeenStep = AccountSettings.getSettings(SESSION_PROGRESS_REWARDS_WIDGET_LAST_SEEN_STEP)
        isFirstSeen = lastSeenStep == SESSION_WIDGET_UNSEEN_STEP
        shouldIndicateComplete = isRewardWasReceivedToday and currentStep != lastSeenStep and not isFirstSeen
        expectedEarned = 1 if shouldIndicateComplete else 0
        expectedCurrentProgress = 1 if startAnimation else 0
        tabTexts = R.strings.quests.serialEnter.tab
        isLastStageCompleted = currentStep > finalStep
        if isLastStageCompleted:
            title = backport.text(tabTexts.final.title())
            description = backport.text(tabTexts.final.description())
        elif isRewardWasReceivedToday:
            title = backport.text(tabTexts.completed.title())
            description = backport.text(tabTexts.completed.description())
        else:
            title = backport.text(tabTexts.label())
            description = backport.text(tabTexts.description())
        packedDescription = '{}\n{}'.format(title, description)
        if shouldIndicateComplete:
            if startAnimation:
                self.__scheduleSessionWidgetMarkVisited()
            else:
                self.__scheduleSessionWidgetStartAnimation()
        elif isRewardWasReceivedToday and isFirstSeen:
            self.__markSessionWidgetVisited()
        if len(model) == 1:
            existing = model[0]
            if existing.getId() == SERIAL_ENTER_QUEST_ID and existing.getCompleted() == isRewardWasReceivedToday and existing.getDescription() == packedDescription and existing.getEarned() == expectedEarned and existing.getCurrentProgress() == expectedCurrentProgress:
                return
        questModel = WidgetQuestModel()
        questModel.setId(SERIAL_ENTER_QUEST_ID)
        questModel.setDescription(packedDescription)
        questModel.setCompleted(isRewardWasReceivedToday or isLastStageCompleted)
        questModel.setEarned(expectedEarned)
        questModel.setCurrentProgress(expectedCurrentProgress)
        model.clear()
        model.reserve(1)
        model.addViewModel(questModel)
        model.invalidate()

    def __scheduleSessionWidgetMarkVisited(self):
        if self.__sessionWidgetMarkVisitedCallbackID:
            return
        self.__sessionWidgetMarkVisitedCallbackID = BigWorld.callback(MARK_VISITED_TIMEOUT, self.__markSessionWidgetVisited)

    def __cancelSessionWidgetMarkVisited(self):
        if self.__sessionWidgetMarkVisitedCallbackID:
            BigWorld.cancelCallback(self.__sessionWidgetMarkVisitedCallbackID)
            self.__sessionWidgetMarkVisitedCallbackID = 0

    def __markSessionWidgetVisited(self):
        self.__sessionWidgetMarkVisitedCallbackID = 0
        AccountSettings.setSettings(SESSION_PROGRESS_REWARDS_WIDGET_LAST_SEEN_STEP, self.__sessionProgressRewardsController.currentStep)

    def __scheduleSessionWidgetStartAnimation(self):
        if self.__sessionWidgetStartAnimationCallbackID:
            return
        self.__sessionWidgetStartAnimationCallbackID = BigWorld.callback(SERIAL_ENTER_START_ANIMATION_DELAY, self.__startSessionWidgetAnimation)

    def __cancelSessionWidgetStartAnimation(self):
        if self.__sessionWidgetStartAnimationCallbackID:
            BigWorld.cancelCallback(self.__sessionWidgetStartAnimationCallbackID)
            self.__sessionWidgetStartAnimationCallbackID = 0

    def __startSessionWidgetAnimation(self):
        self.__sessionWidgetStartAnimationCallbackID = 0
        with self.getViewModel().transaction() as tx:
            self.__packSerialEnterQuests(tx.getSerialEnterQuests(), startAnimation=True)

    def __packQuestsModel(self, model, quests):
        model.clear()
        model.reserve(len(quests))
        for quest in quests:
            questUIPacker = getEventUIDataPacker(quest)
            fullQuestModel = questUIPacker.pack()
            questModel = WidgetQuestModel()
            modifyPostbattleConditions(quest, fullQuestModel)
            preFormattedConditionModel = self._getFirstConditionModelFromQuestModel(fullQuestModel)
            if preFormattedConditionModel is not None:
                questModel.setCurrentProgress(preFormattedConditionModel.getCurrent())
                questModel.setTotalProgress(preFormattedConditionModel.getTotal())
                questModel.setEarned(preFormattedConditionModel.getEarned())
                questModel.setDescription(preFormattedConditionModel.getDescrData())
            questModel.setId(fullQuestModel.getId())
            questModel.setIcon(fullQuestModel.getIcon())
            questModel.setCompleted(fullQuestModel.getStatus().value == MISSIONS_STATES.COMPLETED)
            questModel.setHasPremium(fullQuestModel.getHasPremium())
            model.addViewModel(questModel)
            fullQuestModel.unbind()

        model.invalidate()
        return
