# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mission_selection_view.py
import logging
from datetime import datetime
import typing
from frameworks.wulf import ViewStatus, WindowLayer
from gui import GUI_SETTINGS
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import i18n, dependency
from items import vehicles
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from PlayerEvents import g_playerEvents
from story_mode.account_settings import setUnlockedTaskShown, isUnlockedTaskShown, isWelcomeScreenSeen
from story_mode.gui.impl.gen.view_models.views.lobby.mission_model import MissionModel
from story_mode.gui.impl.gen.view_models.views.lobby.mission_selection_view_model import MissionSelectionViewModel, TabsEnum
from story_mode.gui.impl.gen.view_models.views.lobby.mission_task_tooltip_model import TaskStateEnum as TooltipTaskStateEnum
from story_mode.gui.impl.gen.view_models.views.lobby.task_model import TaskModel, TaskStateEnum
from story_mode.gui.impl.lobby.base_prb_view import BasePrbView
from story_mode.gui.impl.lobby.difficulty_tooltip import DifficultyTooltip
from story_mode.gui.impl.lobby.event_entry_point_view import EventEntryPointView
from story_mode.gui.impl.lobby.mission_tooltip import MissionTooltip
from story_mode.gui.impl.lobby.task_tooltip import TaskTooltip
from story_mode.gui.shared.event_dispatcher import sendViewLoadedEvent, showEventWelcomeWindow
from story_mode.gui.story_mode_gui_constants import STORY_MODE_SOUND_SPACE
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import SelectMissionWindow
from story_mode_common.helpers import isTaskCompleted
from story_mode_common.story_mode_constants import UNDEFINED_MISSION_ID, LOGGER_NAME
if typing.TYPE_CHECKING:
    from story_mode_common.configs.story_mode_missions import MissionModel as ConfigMissionModel
    from gui.shared.gui_items import Vehicle
_logger = logging.getLogger(LOGGER_NAME)
_TASK_STATE_ENUM_TO_TOOLTIP_MAP = {TaskStateEnum.UNCOMPLETED: TooltipTaskStateEnum.UNCOMPLETED,
 TaskStateEnum.COMPLETED: TooltipTaskStateEnum.COMPLETED,
 TaskStateEnum.LOCKED: TooltipTaskStateEnum.LOCKED}
_INFO_PAGE_STORY_MODE = 'infoPageStory_mode'

class MissionSelectionView(BasePrbView):
    LAYOUT_ID = R.views.story_mode.lobby.MissionSelectionView()
    MODEL_CLASS = MissionSelectionViewModel
    _COMMON_SOUND_SPACE = STORY_MODE_SOUND_SPACE
    _gui = dependency.descriptor(IGuiLoader)
    _itemsCache = dependency.descriptor(IItemsCache)
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, *args, **kwargs):
        super(MissionSelectionView, self).__init__(*args, **kwargs)
        self._animationCounter = 0
        self._isBackgroundLoaded = False
        self._uiLogger = SelectMissionWindow()
        self.__isAnimationPlayedAfterWindowMap = {R.views.story_mode.lobby.BattleResultView(): False,
         R.views.story_mode.lobby.EventWelcomeView(): False,
         R.views.story_mode.common.CongratulationsWindow(): False}

    def createToolTipContent(self, event, contentID):
        selectedMissionId = self._storyModeCtrl.selectedMissionId
        if contentID == R.views.story_mode.lobby.MissionTooltip():
            mission = self._storyModeCtrl.missions.getMission(selectedMissionId)
            if mission is None:
                _logger.error('Mission ID=%s not exists', selectedMissionId)
                return
            vehTypeCD = vehicles.makeVehicleTypeCompDescrByName(mission.vehicle.name)
            vehicle = self._itemsCache.items.getItemByCD(vehTypeCD)
            return MissionTooltip(vehicle)
        elif contentID == R.views.story_mode.lobby.DifficultyTooltip():
            return DifficultyTooltip(event.getArgument('difficulty'), event.getArgument('isSelected'))
        elif contentID == R.views.story_mode.lobby.TaskTooltip():
            taskId = int(event.getArgument('taskId'))
            mission = self._storyModeCtrl.missions.getMission(selectedMissionId)
            if mission is None:
                _logger.error('Mission ID=%s not exists', selectedMissionId)
                return
            task = mission.getTask(taskId)
            if task is None:
                _logger.error('Task ID=%s not exists', taskId)
                return
            taskState = self.__getTaskState(selectedMissionId, task)
            return TaskTooltip(R.strings.sm_lobby.missionSelection.taskDescription.num(selectedMissionId).num(taskId), _TASK_STATE_ENUM_TO_TOOLTIP_MAP[taskState], task.reward, task.unlockDate)
        elif contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        else:
            return super(MissionSelectionView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(MissionSelectionView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__updateSelectedMission(model)

    def _onLoaded(self, *args, **kwargs):
        super(MissionSelectionView, self)._onLoaded(*args, **kwargs)
        viewModel = self.getViewModel()
        self._uiLogger.logOpen(viewModel.selectedMission.getMissionId() if viewModel else UNDEFINED_MISSION_ID)

    def _initialize(self):
        super(MissionSelectionView, self)._initialize()
        self._storyModeCtrl.startMusic()
        if self._storyModeCtrl.missions.isEventEnabled:
            if not isWelcomeScreenSeen():
                showEventWelcomeWindow()

    def _finalize(self):
        self._uiLogger.logClose()
        super(MissionSelectionView, self)._finalize()

    def _getEvents(self):
        viewModel = self.getViewModel()
        return ((viewModel.onLoaded, self._onBackgroundLoaded),
         (viewModel.onQuit, self._quit),
         (viewModel.onMissionSelect, self.__onMissionSelect),
         (viewModel.onChangeTab, self.__onChangeTab),
         (viewModel.onSelectedMissionTaskUnlocked, self.__onTaskUnlocked),
         (viewModel.onAboutClick, self.__openAbout),
         (self._gui.windowsManager.onViewStatusChanged, self.__onViewStatusChanged),
         (self._storyModeCtrl.onSyncDataUpdated, self.__onMissionsDataUpdated),
         (self._storyModeCtrl.onMissionsConfigUpdated, self.__onMissionsDataUpdated),
         (g_playerEvents.onDossiersResync, self.__onDossiersResync))

    def _onBackgroundLoaded(self):
        sendViewLoadedEvent(self.LAYOUT_ID)
        self._isBackgroundLoaded = True

    def _quit(self):
        if self._isBackgroundLoaded:
            self._uiLogger.logClick(LogButtons.CLOSE)
            super(MissionSelectionView, self)._quit()

    def __onViewStatusChanged(self, uniqueID, newState):
        if newState == ViewStatus.DESTROYING:
            view = self._gui.windowsManager.getView(uniqueID)
            if view and view.layoutID in self.__isAnimationPlayedAfterWindowMap and not self.__isAnimationPlayedAfterWindowMap[view.layoutID]:
                with self.getViewModel().transaction() as model:
                    for taskModel in model.getTasks():
                        if taskModel.getIsCompletedFirstTime() or taskModel.getIsUnlockedFirstTime():
                            self._animationCounter += 1
                            taskModel.setAnimationCounter(self._animationCounter)
                            self.__isAnimationPlayedAfterWindowMap[view.layoutID] = True

    def __selectMission(self, missionId, updateMissions):
        self._storyModeCtrl.selectedMissionId = missionId
        with self.getViewModel().transaction() as model:
            isMissionChanged = self.__updateSelectedMission(model, updateMissions)
        model = self.getViewModel()
        if isMissionChanged and model:
            g_eventDispatcher.updateUI()
            self._uiLogger.logMissionSelectClick(model.selectedMission.getMissionId())
            self._storyModeCtrl.startMusic()

    def __onMissionSelect(self, args):
        self.__selectMission(int(args.get('id')), False)

    def __onChangeTab(self, args):
        newTab = int(args['id'])
        isEvent = newTab == TabsEnum.EVENT
        missionId = self._storyModeCtrl.chooseSelectedMissionId(isEvent=isEvent)
        if missionId == UNDEFINED_MISSION_ID:
            _logger.error('[Missions view] Tab(event=%s) can not be selected. No suitable missions in tab.', isEvent)
            return
        self.__selectMission(missionId, True)

    def __onMissionsDataUpdated(self):
        with self.getViewModel().transaction() as model:
            isMissionChanged = self.__updateSelectedMission(model)
        model = self.getViewModel()
        if isMissionChanged and model:
            self._uiLogger.logAutoSelect(model.selectedMission.getMissionId())

    def __updateSelectedMission(self, model, updateMissions=True):
        missionId = self._storyModeCtrl.selectedMissionId
        if missionId == UNDEFINED_MISSION_ID:
            return False
        prevMissionId = model.selectedMission.getMissionId()
        missionConfig = self._storyModeCtrl.missions.getMission(missionId)
        currentTab = TabsEnum.EVENT if missionConfig.isEvent else TabsEnum.NEWBIES
        model.setSelectedTab(currentTab)
        self.__updateSelectedMissionModel(model, missionConfig)
        if updateMissions:
            self.__updateMissionsModels(model, currentTab)
        EventEntryPointView.onMissionSelected(missionId)
        return prevMissionId != missionId

    def __onTaskUnlocked(self, args):
        setUnlockedTaskShown(self.getViewModel().selectedMission.getMissionId(), int(args['taskId']))

    def __updateSelectedMissionModel(self, model, missionConfig):
        selectedMissionModel = model.selectedMission
        selectedMissionModel.setMissionId(missionConfig.missionId)
        selectedMissionModel.setIsCompleted(self._storyModeCtrl.isMissionCompleted(missionConfig.missionId))
        selectedMissionModel.setLocked(False)
        selectedMissionModel.setIsCountdownVisible(False)
        if missionConfig.disabledTimer:
            utcnow = datetime.utcnow()
            if missionConfig.disabledTimer.showAt <= utcnow:
                selectedMissionModel.setIsCountdownVisible(True)
                selectedMissionModel.setSecondsCountdown(_totalSeconds(missionConfig.disabledTimer.endAt))
        battlesCount = self._itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
        if missionConfig.isMissionLocked(battlesCount):
            selectedMissionModel.setLocked(True)
            selectedMissionModel.setBattlesToUnlock(missionConfig.unlockBattlesCount - battlesCount)
        self.__updateTasks(model, missionConfig)

    def __updateMissionsModels(self, model, currentTab):
        missionsModel = model.getMissions()
        missionsModel.clear()
        isEventTab = currentTab == TabsEnum.EVENT
        tabsWithMissions = set()
        for mission in self._storyModeCtrl.filterMissions():
            tabsWithMissions.add(TabsEnum.EVENT if mission.isEvent else TabsEnum.NEWBIES)
            if isEventTab != mission.isEvent:
                continue
            missionModel = MissionModel()
            if mission.displayName:
                missionModel.setDisplayName(i18n.makeString(mission.displayName))
            else:
                missionModel.setDisplayName(str(mission.missionId))
            missionModel.setIsCompleted(self._storyModeCtrl.isMissionCompleted(mission.missionId))
            missionModel.setMissionId(mission.missionId)
            missionModel.setDifficulty(mission.difficulty)
            battlesCount = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
            if mission.isMissionLocked(battlesCount):
                missionModel.setLocked(True)
            missionsModel.addViewModel(missionModel)

        missionsModel.invalidate()
        model.setIsTabsVisible(len(tabsWithMissions) > 1)

    def __updateTasks(self, model, missionConfig):
        progressDiff = {missionConfig.missionId: self._storyModeCtrl.popMissionProgressDiff(missionConfig.missionId)}
        tasksModel = model.getTasks()
        tasksModel.clear()
        for task in missionConfig.tasks:
            taskModel = TaskModel()
            taskModel.setTaskId(task.id)
            taskState = self.__getTaskState(missionConfig.missionId, task)
            taskModel.setTaskState(taskState)
            if task.unlockDate:
                if taskState == TaskStateEnum.LOCKED:
                    taskModel.setSecondsBeforeUnlock(_totalSeconds(task.unlockDate))
                elif taskState == TaskStateEnum.UNCOMPLETED:
                    if not isUnlockedTaskShown(missionConfig.missionId, task.id):
                        taskModel.setIsUnlockedFirstTime(True)
                        setUnlockedTaskShown(missionConfig.missionId, task.id)
            taskModel.setIsCompletedFirstTime(isTaskCompleted(progressDiff, missionConfig.missionId, task.id))
            self._animationCounter += 1
            taskModel.setAnimationCounter(self._animationCounter)
            tasksModel.addViewModel(taskModel)

        tasksModel.invalidate()

    def __openAbout(self):
        url = GUI_SETTINGS.lookup(_INFO_PAGE_STORY_MODE)
        showBrowserOverlayView(url, VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def __getTaskState(self, missionId, task):
        if self._storyModeCtrl.isMissionTaskCompleted(missionId, task.id):
            return TaskStateEnum.COMPLETED
        return TaskStateEnum.LOCKED if task.isLocked() else TaskStateEnum.UNCOMPLETED

    def __onDossiersResync(self, *args):
        model = self.getViewModel()
        if model is not None:
            self.__updateSelectedMission(model, True)
        return


def _totalSeconds(endDate):
    return max(int((endDate - datetime.utcnow()).total_seconds()), 0)
