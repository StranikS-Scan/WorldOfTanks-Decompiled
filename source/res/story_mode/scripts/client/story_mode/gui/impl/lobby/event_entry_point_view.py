# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/event_entry_point_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getTimestampFromUTC
from story_mode.account_settings import setEventEntryPointShownState, getEventEntryPointShownState
from story_mode.gui.impl.gen.view_models.views.lobby.event_entry_point_view_model import EventEntryPointViewModel
from story_mode.gui.impl.lobby.consts import EntryPointStates
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.loggers import EntryPointLogger
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.configs.story_mode_settings import settingsSchema
_BG_FOLDER_NAME = 'eventEntryPoint'

class EventEntryPointView(ViewImpl):
    __controller = dependency.descriptor(IStoryModeController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.story_mode.lobby.EventEntryPointView())
        settings.flags = flags
        settings.model = EventEntryPointViewModel()
        super(EventEntryPointView, self).__init__(settings)
        self.__state = EntryPointStates.UNKNOWN
        self.__newRemoved = False
        self.__uiLogger = EntryPointLogger()

    @staticmethod
    def onMissionSelected(missionId):
        missionsModel = missionsSchema.getModel()
        if not missionsModel:
            return
        mission = missionsModel.getMission(missionId)
        if mission.isEvent:
            state = EventEntryPointView.__getState()
            if getEventEntryPointShownState() < state:
                setEventEntryPointShownState(state)

    def _getEvents(self):
        return [(self.getViewModel().onClick, self.__onClick),
         (self.getViewModel().onHoverForSetTime, self.__onHover),
         (self.getViewModel().onLeaveAfterSetTime, self.__onUnhover),
         (g_playerEvents.onConfigModelUpdated, self.__configChangeHandler)]

    def _onLoading(self, *args, **kwargs):
        super(EventEntryPointView, self)._onLoading(*args, **kwargs)
        viewModel = self.getViewModel()
        viewModel.setTitle(backport.text(R.strings.sm_lobby.entryPoint.title.newMode()))
        viewModel.setSubtitle(backport.text(R.strings.sm_lobby.entryPoint.subtitle.newMode()))
        viewModel.setBgFolderName(_BG_FOLDER_NAME)
        with viewModel.transaction() as vm:
            self.__fillViewModel(vm)

    def __configChangeHandler(self, _):
        with self.getViewModel().transaction() as vm:
            self.__fillViewModel(vm)

    def __fillViewModel(self, vm):
        self.__newRemoved = False
        self.__state = self.__getState()
        settings = settingsSchema.getModel()
        if settings:
            vm.setStartDate(getTimestampFromUTC(settings.entryPoint.eventStartAt.timetuple()))
            vm.setEndDate(getTimestampFromUTC(settings.entryPoint.eventEndAt.timetuple()))
            vm.setIsNew(getEventEntryPointShownState() < self.__state)
            if self.__state == EntryPointStates.TASKS_UNLOCKED:
                vm.setSubtitle(backport.text(R.strings.sm_lobby.entryPoint.subtitle.newMission()))

    def __onClick(self):
        self.__uiLogger.logClick(self.__state)
        self.__newRemoved = False
        self.__controller.switchPrb()

    def __onHover(self):
        view = self.getViewModel()
        if view.getIsNew():
            self.__newRemoved = True
            view.setIsNew(False)
            setEventEntryPointShownState(self.__state)

    @staticmethod
    def __getState():
        missionsModel = missionsSchema.getModel()
        missions = missionsModel.missions if missionsModel else []
        return EntryPointStates.TASKS_UNLOCKED if any((EventEntryPointView.__isAdditionalTasksUnlocked(mission) for mission in missions if mission.isEvent)) else EntryPointStates.NEW_EVENT

    @staticmethod
    def __isAdditionalTasksUnlocked(mission):
        return False if len(mission.tasks) <= 1 else any((not task.isLocked() for task in mission.tasks[1:]))

    def __onUnhover(self):
        if self.__newRemoved:
            self.__uiLogger.logUnhover(self.__state)
            self.__newRemoved = False
