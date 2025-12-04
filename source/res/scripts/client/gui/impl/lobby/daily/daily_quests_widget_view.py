# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quests_widget_view.py
import logging
import BigWorld
import typing
from account_helpers.AccountSettings import AccountSettings, PlayStreak
from constants import PremiumConfigs
from frameworks.wulf import Array, ViewFlags, WindowFlags
from frameworks.wulf.view.view import ViewSettings
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_view_model import DailyTabs
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_widget_view_model import DailyQuestsWidgetViewModel
from gui.impl.gen.view_models.views.lobby.daily.widget_quest_model import WidgetQuestModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.daily.daily_helpers import needToUpdateQuestsInModel, modifyPostbattleConditions
from gui.impl.lobby.daily.tooltips.daily_quests_tooltip import DailyQuestsTooltip
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showDailyQuests
from gui.server_events.events_helpers import dailyQuestsSortFunc, EventInfoModel, isPremiumQuestsEnable
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.main_wnd_state_watcher import ClientMainWindowStateWatcher
from gui.shared.missions.packers.events import getEventUIDataPacker, findFirstConditionModel
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController, IGameSessionController, IPlayStreakController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from new_year.skeletons.new_year import INewYearController
from new_year.gui.game_control.ny_controller import isAllNyQuestsCompleted
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
    from gui.server_events.event_items import ServerEventAbstract, DailyQuest
    from typing import Optional, Any
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.impl.gen.view_models.views.lobby.daily.play_streak.play_streak_widget_model import PlayStreakWidgetModel
    from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
MOUSE_BUTTON_RIGHT = 2
MOUSE_BUTTON_LEFT = 0
LARGE_WIDGET_LAYOUT_ID = 0
MARK_VISITED_TIMEOUT = 1.0
_logger = logging.getLogger(__name__)

def predicateTooltipWindow(window):
    return window.content is not None and window.typeFlag == WindowFlags.TOOLTIP


class DailyQuestsWidgetView(ViewImpl, ClientMainWindowStateWatcher):
    __slots__ = ('__parentId', '__tooltipEnabled', '__layout', '__visitedQuests', '__markVisitedCallbackID')
    __eventsCache = dependency.descriptor(IEventsCache)
    subscriptionController = dependency.descriptor(IWotPlusController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    gameSession = dependency.descriptor(IGameSessionController)
    itemsCache = dependency.descriptor(IItemsCache)
    __gui = dependency.descriptor(IGuiLoader)
    __playStreakController = dependency.descriptor(IPlayStreakController)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.daily.DailyQuestWidget(), ViewFlags.VIEW, DailyQuestsWidgetViewModel())
        super(DailyQuestsWidgetView, self).__init__(settings)
        self.__parentId = None
        self.__tooltipEnabled = True
        self.__layout = 0
        self.__visitedQuests = set()
        self.__markVisitedCallbackID = 0
        return

    def setParentId(self, parentId):
        self.__parentId = parentId

    def createToolTipContent(self, event, contentID):
        _logger.debug('DailyQuests::createToolTipContent')
        if not self.__tooltipEnabled:
            return None
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
                quests = sorted(self.__eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
                premiumQuests = sorted(self.__eventsCache.getDailyPremiumQuests().values(), key=dailyQuestsSortFunc) if isPremiumQuestsEnable() else []
                self.__updateQuestsToBeIndicatedCompleted(tx, quests + premiumQuests, True)
            tx.setVisible(value)

    def _onLoading(self, *args, **kwargs):
        super(DailyQuestsWidgetView, self)._onLoading(*args, **kwargs)
        self._updateViewModel()
        self.__onPlayStreakUpdated()

    def _initialize(self, *args, **kwargs):
        self.mainWindowWatcherInit()

    def _getEvents(self):
        return ((self.__eventsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.viewModel.onQuestClick, self.__onQuestClick),
         (self.viewModel.onPlayStreakClick, self.__onPlayStreakClick),
         (self.gameSession.onPremiumTypeChanged, self._onPremiumTypeChanged),
         (self.__playStreakController.onDataUpdated, self.__onPlayStreakUpdated),
         (self.viewModel.onNyQuestsClick, self.__onNyQuestsClick),
         (self.lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__nyController.onStateChanged, self.__updateNY))

    def _getListeners(self):
        return ((LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__onHelpLayoutHide, EVENT_BUS_SCOPE.LOBBY), (LobbySimpleEvent.SHOW_HELPLAYOUT, self.__onHelpLayoutShow, EVENT_BUS_SCOPE.LOBBY))

    def __setIsFirstAppearance(self, streakProgress, model):
        freezeProgress = self.itemsCache.items.playStreak.getRedemptionDay()
        lastSeenCount = AccountSettings.getPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_SEEN_WIDGET)
        lastFreezeSeenCount = AccountSettings.getPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_FREEZE_SEEN_WIDGET)
        if streakProgress != lastSeenCount and streakProgress:
            AccountSettings.setPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_SEEN_WIDGET, streakProgress)
            model.setIsFirstAppearance(True)
        elif lastFreezeSeenCount != freezeProgress and self.itemsCache.items.playStreak.getDailyConditionCompleted():
            AccountSettings.setPlayStreak(PlayStreak.PLAY_STREAK_LAST_LEVEL_FREEZE_SEEN_WIDGET, freezeProgress)
            if freezeProgress > 0:
                model.setIsFirstAppearanceRedemptionDay(True)
            else:
                model.setIsLastDayRedemption(True)
        else:
            model.setIsFirstAppearance(False)
            model.setIsLastDayRedemption(False)
            model.setIsFirstAppearanceRedemptionDay(False)

    def _finalize(self):
        self.mainWindowWatcherDestroy()
        if self.__markVisitedCallbackID != 0:
            BigWorld.cancelCallback(self.__markVisitedCallbackID)
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

    def __onPlayStreakUpdated(self):
        with self.viewModel.transaction() as tx:
            self._updataPlayStreakModel(tx)

    def _updateViewModel(self):
        _logger.debug('DailyQuests::UpdatingViewModel')
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        quests = sorted(self.__eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        premiumQuests = sorted(self.__eventsCache.getDailyPremiumQuests().values(), key=dailyQuestsSortFunc) if isPremiumQuestsEnable() else []
        if not (needToUpdateQuestsInModel(quests, self.getViewModel().getQuests()) or needToUpdateQuestsInModel(premiumQuests, self.getViewModel().getPremiumQuests())):
            return
        with self.getViewModel().transaction() as tx:
            tx.setCountdown(newCountdownVal)
            modelQuests = tx.getQuests()
            modelPremiumQuests = tx.getPremiumQuests()
            self.__packQuestsModel(modelQuests, quests)
            self.__packQuestsModel(modelPremiumQuests, premiumQuests)
            self.__updateQuestsToBeIndicatedCompleted(tx, quests + premiumQuests, self.viewModel.getVisible())
            self.__updateNyQuests(tx)

    def _markVisited(self):
        if self.__layout == LARGE_WIDGET_LAYOUT_ID:
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

    @args2params(int)
    def __onQuestClick(self, tabIdx):
        showDailyQuests(subTab=tabIdx)

    def __onPlayStreakClick(self):
        showDailyQuests(subTab=DailyTabs.SERIAL)

    def __onNyQuestsClick(self):
        if not self.__nyController.isEnabled():
            return
        showDailyQuests(subTab=DailyTabs.NYQUESTS)

    def __updateNyQuests(self, model):
        isNYEnabled = self.__nyController.isEnabled()
        model.setIsNyEnabled(isNYEnabled)
        model.setIsAllNyQuestsComplete(isNYEnabled and isAllNyQuestsCompleted(self.__eventsCache))

    def __updateNY(self):
        with self.viewModel.transaction() as tx:
            self.__updateNyQuests(tx)

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
        with self.viewModel.transaction() as vm:
            self.__updateNyQuests(vm)
        if PremiumConfigs.PREM_QUESTS not in diff:
            return
        diffConfig = diff.get(PremiumConfigs.PREM_QUESTS)
        if 'enabled' in diffConfig:
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

    def _updataPlayStreakModel(self, model):
        with model.playStreak.transaction() as tx:
            streakProgress = self.__playStreakController.getStreakProgress()
            tx.setStreakLength(streakProgress)
            self.__setIsFirstAppearance(streakProgress, tx)
            tx.setSkipDayCount(self.__playStreakController.getSkipDayCount())
            tx.setDailyWin(self.itemsCache.items.playStreak.getDailyConditionCompleted())
            tx.setIsPaused(self.lobbyContext.getServerSettings().playStreakConfig.isPaused)
            tx.setRedemptionDayCount(self.itemsCache.items.playStreak.getRedemptionDay())
            tx.setIsBlocked(self.__playStreakController.getIsBlocked())
            tx.setRedemptionMaxDayCount(self.lobbyContext.getServerSettings().playStreakConfig.daySkipSettings.get('freezeModeLength'))
            tx.setIsEnabled(self.lobbyContext.getServerSettings().playStreakConfig.isEnabled)
