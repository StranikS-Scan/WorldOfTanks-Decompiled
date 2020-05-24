# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/missions/daily_quests_widget_view.py
import logging
import typing
from frameworks.wulf import Array, ViewFlags, WindowFlags
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.widget.daily_quests_widget_view_model import DailyQuestsWidgetViewModel
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_mission_model import WidgetMissionModel
from gui.impl.lobby.missions.missions_helpers import needToUpdateQuestsInModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.main_wnd_state_watcher import ClientMainWindowStateWatcher
from gui.shared.missions.packers.events import getEventUIDataPacker, findFirstConditionModel
from gui.shared.events import LobbySimpleEvent
from gui.server_events.events_dispatcher import showDailyQuests
from gui.server_events.events_helpers import dailyQuestsSortFunc, EventInfoModel
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import ServerEventAbstract, DailyQuest
    from typing import Optional, Any
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
MOUSE_BUTTON_RIGHT = 2
MOUSE_BUTTON_LEFT = 0
LARGE_WIDGET_LAYOUT_ID = 0
_logger = logging.getLogger(__name__)

def predicateTooltipWindow(window):
    return window.content is not None and window.windowFlags == WindowFlags.TOOLTIP


class DailyQuestsWidgetView(ViewImpl, ClientMainWindowStateWatcher):
    __slots__ = ('__parentId', '__tooltipEnabled', '__layout')
    eventsCache = dependency.descriptor(IEventsCache)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.missions.DailyQuestsWidget(), ViewFlags.COMPONENT, DailyQuestsWidgetViewModel())
        super(DailyQuestsWidgetView, self).__init__(settings)
        self.__parentId = None
        self.__tooltipEnabled = True
        self.__layout = 0
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
                quests = self.eventsCache.getDailyQuests().values()
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
        if self.getViewModel().getIsVisible():
            self._markVisited()

    def setIsVisible(self, value):
        if value == self.getViewModel().getIsVisible():
            return
        with self.getViewModel().transaction() as tx:
            if value:
                quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
                self.__updateModelMissionCompletedVisitedArray(tx, quests, True)
            tx.setIsVisible(value)

    def _onLoading(self, *args, **kwargs):
        self._updateViewModel()

    def _initialize(self, *args, **kwargs):
        self.__addListeners()
        self.mainWindowWatcherInit()

    def _finalize(self):
        self.mainWindowWatcherDestroy()
        self.__removeListeners()

    @classmethod
    def _getFirstConditionModelFromQuestModel(cls, dailyQuestModel):
        postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel

    def _updateViewModel(self):
        _logger.debug('DailyQuests::UpdatingViewModel')
        newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
        quests = sorted(self.eventsCache.getDailyQuests().values(), key=dailyQuestsSortFunc)
        if not needToUpdateQuestsInModel(quests, self.getViewModel().getMissions()):
            return
        else:
            with self.getViewModel().transaction() as tx:
                tx.setCountDown(newCountdownVal)
                modelMissionsArray = tx.getMissions()
                modelMissionsArray.clear()
                modelMissionsArray.reserve(len(quests))
                for quest in quests:
                    questUIPacker = getEventUIDataPacker(quest)
                    fullQuestModel = questUIPacker.pack()
                    questModel = WidgetMissionModel()
                    preFormattedConditionModel = self._getFirstConditionModelFromQuestModel(fullQuestModel)
                    if preFormattedConditionModel is not None:
                        questModel.setCurrentProgress(preFormattedConditionModel.getCurrent())
                        questModel.setTotalProgress(preFormattedConditionModel.getTotal())
                        questModel.setEarned(preFormattedConditionModel.getEarned())
                        questModel.setDescription(preFormattedConditionModel.getDescrData())
                    questModel.setId(fullQuestModel.getId())
                    questModel.setIcon(fullQuestModel.getIcon())
                    questModel.setIsCompleted(fullQuestModel.getStatus() == MISSIONS_STATES.COMPLETED)
                    modelMissionsArray.addViewModel(questModel)
                    fullQuestModel.unbind()

                modelMissionsArray.invalidate()
                self.__updateModelMissionCompletedVisitedArray(tx, quests, self.viewModel.getIsVisible())
            return

    def _markVisited(self):
        if self.__layout == LARGE_WIDGET_LAYOUT_ID:
            for quest in self.eventsCache.getDailyQuests().values():
                self.eventsCache.questsProgress.markQuestProgressAsViewed(quest.getID())

    def _onClientMainWindowStateChanged(self, isWindowVisible):
        if isWindowVisible:
            with self.viewModel.transaction() as tx:
                newCountdownVal = EventInfoModel.getDailyProgressResetTimeDelta()
                tx.setCountDown(newCountdownVal)

    def __onMissionClick(self):
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

    def __updateModelMissionCompletedVisitedArray(self, viewModelTransaction, sortedQuests, markViewed):
        modelMissionsCompletedVisitedArray = viewModelTransaction.getMissionsCompletedVisited()
        modelMissionsCompletedVisitedArray.clear()
        modelMissionsCompletedVisitedArray.reserve(len(sortedQuests))
        for quest in sortedQuests:
            questCompletionChanged = self.eventsCache.questsProgress.getQuestCompletionChanged(quest.getID())
            if questCompletionChanged and markViewed:
                self.eventsCache.questsProgress.markQuestProgressAsViewed(quest.getID())
            modelMissionsCompletedVisitedArray.addBool(not questCompletionChanged)

        modelMissionsCompletedVisitedArray.invalidate()

    def __addListeners(self):
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.viewModel.onMissionClick += self.__onMissionClick
        g_eventBus.addListener(LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__onHelpLayoutHide, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.SHOW_HELPLAYOUT, self.__onHelpLayoutShow, scope=EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.viewModel.onMissionClick -= self.__onMissionClick
        g_eventBus.removeListener(LobbySimpleEvent.CLOSE_HELPLAYOUT, self.__onHelpLayoutHide, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.SHOW_HELPLAYOUT, self.__onHelpLayoutShow, scope=EVENT_BUS_SCOPE.LOBBY)
