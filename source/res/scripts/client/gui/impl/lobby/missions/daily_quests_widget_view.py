# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/daily_quests_widget_view.py
import logging
import typing
import BigWorld
from frameworks.wulf import Array, ViewFlags, WindowFlags
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.widget.daily_quests_widget_view_model import DailyQuestsWidgetViewModel
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.main_wnd_state_watcher import ClientMainWindowStateWatcher
from gui.shared.missions.packers.events import getEventUIDataPacker
from gui.shared.events import LobbySimpleEvent
from gui.server_events.events_dispatcher import showDailyQuests
from gui.server_events.events_helpers import dailyQuestsSortFunc, EventInfoModel
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.impl import IGuiLoader
from gui.impl.gen.view_models.views.lobby.rts.rts_quest_model import RtsQuestModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
    from gui.server_events.event_items import ServerEventAbstract, DailyQuest
    from typing import Any
MOUSE_BUTTON_RIGHT = 2
MOUSE_BUTTON_LEFT = 0
LARGE_WIDGET_LAYOUT_ID = 0
MARK_VISITED_TIMEOUT = 1.0
_logger = logging.getLogger(__name__)

def predicateTooltipWindow(window):
    return window.content is not None and window.typeFlag == WindowFlags.TOOLTIP


class DailyQuestsWidgetView(ViewImpl, ClientMainWindowStateWatcher):
    __slots__ = ('__parentId', '__tooltipEnabled', '__layout', '__visitedQuests', '__markVisitedCallbackID')
    eventsCache = dependency.descriptor(IEventsCache)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, event_settings=None):
        settings = ViewSettings(R.views.lobby.missions.DailyQuestsWidget(), ViewFlags.COMPONENT, DailyQuestsWidgetViewModel())
        super(DailyQuestsWidgetView, self).__init__(event_settings or settings)
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
        else:
            if contentID == R.views.lobby.missions.DailyQuestsTooltip():
                missionId = event.getArgument('missionId')
                quests = self._getQuests()
                for quest in quests:
                    if quest.getID() == missionId:
                        questUIPacker = getEventUIDataPacker(quest)
                        model = questUIPacker.pack()
                        self.eventsCache.questsProgress.markQuestProgressAsViewed(missionId)
                        return ViewImpl(ViewSettings(R.views.lobby.missions.DailyQuestsTooltip(), model=model))

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
                quests = sorted(self._getQuests(), key=dailyQuestsSortFunc)
                self.__updateQuestsToBeIndicatedCompleted(tx, quests, True)
            tx.setVisible(value)

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel()

    def _initialize(self, *args, **kwargs):
        self.__addListeners()
        self.mainWindowWatcherInit()

    def _finalize(self):
        self.mainWindowWatcherDestroy()
        self.__removeListeners()
        if self.__markVisitedCallbackID != 0:
            BigWorld.cancelCallback(self.__markVisitedCallbackID)

    def _updateViewModel(self):
        _logger.debug('DailyQuests::UpdatingViewModel')
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        quests = sorted(self._getQuests(), key=dailyQuestsSortFunc)
        if not needToUpdateQuestsInModel(quests, self.getViewModel().getQuests()):
            return
        else:
            with self.getViewModel().transaction() as tx:
                tx.setCountdown(newCountdownVal)
                modelQuests = tx.getQuests()
                modelQuests.clear()
                modelQuests.reserve(len(quests))
                for quest in quests:
                    questUIPacker = getEventUIDataPacker(quest)
                    fullQuestModel = questUIPacker.pack()
                    questModel = WidgetQuestModel()
                    conditionModel = questUIPacker.getFirstAvailableCondition(fullQuestModel)
                    if conditionModel is not None:
                        questModel.setCurrentProgress(conditionModel.getCurrent())
                        questModel.setTotalProgress(conditionModel.getTotal())
                        questModel.setEarned(conditionModel.getEarned())
                        description = conditionModel.getDescrData() or conditionModel.getTitleData()
                        questModel.setDescription(description)
                    questModel.setId(fullQuestModel.getId())
                    questModel.setIcon(fullQuestModel.getIcon())
                    questModel.setCompleted(fullQuestModel.getStatus() == MISSIONS_STATES.COMPLETED)
                    questModel.setCompletedCount(fullQuestModel.getCompletedCount())
                    questModel.setTotalCount(fullQuestModel.getTotalCount())
                    questModel.setIsRTS(isinstance(fullQuestModel, RtsQuestModel))
                    modelQuests.addViewModel(questModel)
                    fullQuestModel.unbind()

                modelQuests.invalidate()
                self.__updateQuestsToBeIndicatedCompleted(tx, quests, self.viewModel.getVisible())
            return

    def _markVisited(self):
        if self.__layout == LARGE_WIDGET_LAYOUT_ID:
            for quest in self._getQuests():
                self._scheduleMarkVisited(quest.getID())

    def _executeMarkVisited(self):
        for qid in self.__visitedQuests:
            self.eventsCache.questsProgress.markQuestProgressAsViewed(qid)

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

    def _onQuestClick(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)

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

    def __updateQuestsToBeIndicatedCompleted(self, viewModelTransaction, sortedQuests, markViewed):
        indicateCompleteQuests = viewModelTransaction.getIndicateCompleteQuests()
        indicateCompleteQuests.clear()
        indicateCompleteQuests.reserve(len(sortedQuests))
        for quest in sortedQuests:
            questCompletionChanged = self.eventsCache.questsProgress.getQuestCompletionChanged(quest.getID())
            if questCompletionChanged and markViewed:
                self._scheduleMarkVisited(quest.getID())
            indicateCompleteQuests.addBool(quest.isCompleted())

        indicateCompleteQuests.invalidate()

    def __addListeners(self):
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.viewModel.onQuestClick += self._onQuestClick
        g_eventBus.addListener(LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__onHelpLayoutHide, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.SHOW_HELPLAYOUT, self.__onHelpLayoutShow, scope=EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.viewModel.onQuestClick -= self._onQuestClick
        g_eventBus.removeListener(LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__onHelpLayoutHide, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.SHOW_HELPLAYOUT, self.__onHelpLayoutShow, scope=EVENT_BUS_SCOPE.LOBBY)

    def _getQuests(self):
        return self.eventsCache.getDailyQuests().values()
