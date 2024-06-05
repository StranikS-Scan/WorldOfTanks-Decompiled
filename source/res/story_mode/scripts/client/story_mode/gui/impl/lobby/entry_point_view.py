# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/entry_point_view.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getTimestampFromUTC
from story_mode.account_settings import setEntryPointShownState, getEntryPointShownState
from story_mode.gui.impl.gen.view_models.views.lobby.entry_point_view_model import EntryPointViewModel
from story_mode.gui.impl.lobby.consts import EntryPointStates
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.loggers import EntryPointLogger
from story_mode_common.configs.story_mode_missions import missionsSchema
from story_mode_common.configs.story_mode_settings import settingsSchema

class EntryPointView(ViewImpl):
    __controller = dependency.descriptor(IStoryModeController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.story_mode.lobby.EntryPointView())
        settings.flags = flags
        settings.model = EntryPointViewModel()
        super(EntryPointView, self).__init__(settings)
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
            state = EntryPointView.__getState()
            if getEntryPointShownState() < state:
                setEntryPointShownState(state)

    def _getEvents(self):
        return [(self.getViewModel().onClick, self.__onClick),
         (self.getViewModel().onHoverForSetTime, self.__onHover),
         (self.getViewModel().onLeaveAfterSetTime, self.__onUnhover),
         (g_playerEvents.onConfigModelUpdated, self.__configChangeHandler)]

    def _onLoading(self, *args, **kwargs):
        super(EntryPointView, self)._onLoading(*args, **kwargs)
        self.__fillViewModel()

    def __configChangeHandler(self, _):
        self.__fillViewModel()

    def __fillViewModel(self):
        self.__newRemoved = False
        self.__state = self.__getState()
        settings = settingsSchema.getModel()
        if settings:
            with self.getViewModel().transaction() as model:
                model.setStartDate(getTimestampFromUTC(settings.entryPoint.eventStartAt.timetuple()))
                model.setEndDate(getTimestampFromUTC(settings.entryPoint.eventEndAt.timetuple()))
                model.setIsNewTasksUnlocked(self.__state == EntryPointStates.TASKS_UNLOCKED)
                model.setIsNew(getEntryPointShownState() < self.__state)

    def __onClick(self):
        self.__uiLogger.logClick(self.__state)
        self.__newRemoved = False
        self.__controller.switchPrb()

    def __onHover(self):
        view = self.getViewModel()
        if view.getIsNew():
            self.__newRemoved = True
            view.setIsNew(False)
            setEntryPointShownState(self.__state)

    @staticmethod
    def __getState():
        missionsModel = missionsSchema.getModel()
        missions = missionsModel.missions if missionsModel else []
        return EntryPointStates.TASKS_UNLOCKED if any((EntryPointView.__isAdditionalTasksUnlocked(mission) for mission in missions if mission.isEvent)) else EntryPointStates.NEW_EVENT

    @staticmethod
    def __isAdditionalTasksUnlocked(mission):
        return False if len(mission.tasks) <= 1 else any((not task.isLocked() for task in mission.tasks[1:]))

    def __onUnhover(self):
        if self.__newRemoved:
            self.__uiLogger.logUnhover(self.__state)
            self.__newRemoved = False
