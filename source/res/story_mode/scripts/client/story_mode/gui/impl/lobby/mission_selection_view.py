# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mission_selection_view.py
import json
import logging
from datetime import datetime
import typing
import BigWorld
import ResMgr
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewStatus, WindowLayer
from gui import GUI_SETTINGS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import i18n, dependency
from ids_generators import SequenceIDGenerator
from items import vehicles
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from story_mode.account_settings import setUnlockedTaskShown, isUnlockedTaskShown, isWelcomeScreenSeen
from story_mode.gui.impl.gen.view_models.views.lobby.mission_model import MissionModel
from story_mode.gui.impl.gen.view_models.views.lobby.mission_selection_view_model import MissionSelectionViewModel, TabsEnum
from story_mode.gui.impl.gen.view_models.views.lobby.task_model import TaskModel, TaskStateEnum
from story_mode.gui.impl.lobby.base_prb_view import BasePrbView
from story_mode.gui.impl.lobby.difficulty_tooltip import DifficultyTooltip
from story_mode.gui.impl.lobby.event_entry_point_view import EventEntryPointView
from story_mode.gui.impl.lobby.mission_tooltip import MissionTooltip
from story_mode.gui.shared.event_dispatcher import sendViewLoadedEvent, showEventWelcomeWindow
from story_mode.gui.shared.utils import formatAndFillRewards
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS, INFO_PAGE_STORY_MODE
from story_mode.gui.sound_constants import STORY_MODE_SOUND_SPACE
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import SelectMissionWindow
from story_mode_common.helpers import isTaskCompleted
from story_mode_common.story_mode_constants import UNDEFINED_MISSION_ID, LOGGER_NAME
if typing.TYPE_CHECKING:
    from story_mode_common.configs.story_mode_missions import MissionModel as ConfigMissionModel
    from gui.shared.gui_items import Vehicle
    from story_mode.gui.impl.gen.view_models.views.lobby.parallax_model import ParallaxModel
_logger = logging.getLogger(LOGGER_NAME)
PATH_TO_CONFIGS = 'story_mode/gui/parallax/configs.json'
PARALLAX_DEFAULT_SCALE = 1

class MissionSelectionView(BasePrbView):
    LAYOUT_ID = R.views.story_mode.lobby.MissionSelectionView()
    MODEL_CLASS = MissionSelectionViewModel
    _COMMON_SOUND_SPACE = STORY_MODE_SOUND_SPACE
    _MAX_BONUSES_IN_VIEW = 5
    _HIDDEN_REWARDS = ('slots',)
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
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        self._isParallaxEnabled = self._storyModeCtrl.settings.parallaxEnabled
        self._parallaxConfig = _toJson(_readSection(PATH_TO_CONFIGS))

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
            isLocked = False
            missionId = event.getArgument('missionId')
            mission = self._storyModeCtrl.missions.getMission(missionId)
            if mission is not None and mission.unlockMission:
                isLocked = not self._storyModeCtrl.isMissionCompleted(mission.unlockMission)
            isAutoCompleteCondition = False
            for task in mission.tasks:
                for completeTask in task.autoCompleteTasks:
                    completeMission = self._storyModeCtrl.missions.getMission(completeTask.missionId)
                    if completeMission is not None and completeMission.isEvent:
                        isAutoCompleteCondition = True

            return DifficultyTooltip(event.getArgument('difficulty'), event.getArgument('isSelected'), isLocked=isLocked, isAutoCompleteCondition=isAutoCompleteCondition)
        elif contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        else:
            return super(MissionSelectionView, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event)
                window.load()
                self._uiLogger.logTooltipShown(self._storyModeCtrl.selectedMissionId)
                return window
        return super(MissionSelectionView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(MissionSelectionView, self)._onLoading(*args, **kwargs)
        model = self.getViewModel()
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
        self._storyModeCtrl.stopMusic()
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
         (self._storyModeCtrl.onSettingsUpdated, self.__onSettingsUpdated),
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
        self._uiLogger.logTabChanged(self._storyModeCtrl.selectedMissionId)
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

    def __onSettingsUpdated(self):
        model = self.getViewModel()
        self._isParallaxEnabled = self._storyModeCtrl.settings.parallaxEnabled
        missionId = self._storyModeCtrl.selectedMissionId
        if missionId == UNDEFINED_MISSION_ID:
            return False
        missionConfig = self._storyModeCtrl.missions.getMission(missionId)
        self.__readParallaxConfig(missionConfig.missionId, model, self._isParallaxEnabled)

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
        self.__readParallaxConfig(missionConfig.missionId, model, self._isParallaxEnabled)

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
            if mission.unlockMission and not self._storyModeCtrl.isMissionCompleted(mission.unlockMission):
                missionModel.setLocked(True)
            missionsModel.addViewModel(missionModel)

        missionsModel.invalidate()
        model.setIsTabsVisible(len(tabsWithMissions) > 1)

    def __updateTasks(self, model, missionConfig):
        progressDiff = {missionConfig.missionId: self._storyModeCtrl.popMissionProgressDiff(missionConfig.missionId)}
        tasksModel = model.getTasks()
        tasksModel.clear()
        self.__bonusCache = {}
        for task in missionConfig.tasks:
            taskModel = TaskModel()
            taskModel.setTaskId(task.id)
            taskState = self.__getTaskState(missionConfig.missionId, task)
            taskModel.setTaskState(taskState)
            conditionLocals = {}
            localPath = R.strings.sm_lobby.missionSelection.taskDescription
            for condition in task.conditions:
                conditionLocals[condition.name] = backport.ntext(localPath.dyn(condition.name)(), int(condition.value), value=condition.value)

            description = backport.text(localPath.num(missionConfig.missionId).num(task.id)(), **conditionLocals)
            taskModel.setDescription(description)
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
            self.__updateTaskRewards(task, taskModel)
            tasksModel.addViewModel(taskModel)

        tasksModel.invalidate()

    def __openAbout(self):
        self._uiLogger.logClick(LogButtons.ABOUT, state=str(self._storyModeCtrl.selectedMissionId))
        infoPageKey = self._storyModeCtrl.storyModeInfoPageKey
        if self._storyModeCtrl.selectedMissionId is not UNDEFINED_MISSION_ID:
            selectedMission = self._storyModeCtrl.missions.getMission(self._storyModeCtrl.selectedMissionId)
            if not selectedMission.isEvent:
                infoPageKey = INFO_PAGE_STORY_MODE
        url = GUI_SETTINGS.lookup(infoPageKey)
        showBrowserOverlayView(url, VIEW_ALIAS.STORY_MODE_WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def __updateTaskRewards(self, task, taskModel):
        rewards = []
        for rewardName, rewardData in task.reward.iteritems():
            if rewardName in self._HIDDEN_REWARDS:
                continue
            rewards.extend(getNonQuestBonuses(rewardName, rewardData))

        formatAndFillRewards(rewards, taskModel.getRewards(), self.__idGen, self.__bonusCache, self._MAX_BONUSES_IN_VIEW)

    def __getTaskState(self, missionId, task):
        if self._storyModeCtrl.isMissionTaskCompleted(missionId, task.id):
            return TaskStateEnum.COMPLETED
        return TaskStateEnum.LOCKED if task.isLocked() else TaskStateEnum.UNCOMPLETED

    def __onDossiersResync(self, *args):
        model = self.getViewModel()
        if model is not None:
            self.__updateSelectedMission(model, True)
        return

    def __readParallaxConfig(self, missionId, model, isParallaxEnabled):
        if not isParallaxEnabled:
            model.setIsParallaxEnabled(False)
            _logger.info('story_mode_settings.xml parallaxEnabled is False')
            return
        else:
            isDeferredRendering = BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 0
            if not isDeferredRendering:
                model.setIsParallaxEnabled(False)
                _logger.info('Low graphics settings')
                return
            missionParallaxConfig = self._parallaxConfig.get(str(missionId))
            if missionParallaxConfig is None:
                model.setIsParallaxEnabled(False)
                _logger.info('cannot find config for %s', missionId)
                return
            parallaxStructure = _readSection(missionParallaxConfig.get('structurePath', ''))
            if parallaxStructure == '':
                model.setIsParallaxEnabled(False)
                _logger.info('cannot find parallax structure:%s', missionParallaxConfig.get('structurePath'))
                return
            model.setIsParallaxEnabled(True)
            chunks = _getChunks(missionParallaxConfig.get('chunksCount', 0), missionParallaxConfig.get('chunkName', ''), missionParallaxConfig.get('chunksDataDirPath', ''))
            modelParallax = model.parallax
            modelParallax.setMissionId(missionId)
            modelParallax.setPerspective(missionParallaxConfig.get('perspective', 0))
            modelParallax.setPerspectiveOriginX(missionParallaxConfig.get('perspectiveOriginX', 0))
            modelParallax.setPerspectiveOriginY(missionParallaxConfig.get('perspectiveOriginY', 0))
            modelParallax.setWrapperWidth(missionParallaxConfig.get('wrapperWidth', 0))
            modelParallax.setWrapperHeight(missionParallaxConfig.get('wrapperHeight', 0))
            modelParallax.setOverallScale(missionParallaxConfig.get('overallScale', PARALLAX_DEFAULT_SCALE))
            modelParallax.setXTilt(missionParallaxConfig.get('xTilt', 0.0))
            modelParallax.setXTiltRange(missionParallaxConfig.get('xTiltRange', 0.0))
            modelParallax.setYTilt(missionParallaxConfig.get('yTilt', 0.0))
            modelParallax.setYTiltRange(missionParallaxConfig.get('yTiltRange', 0.0))
            modelParallax.setXSlide(missionParallaxConfig.get('xSlide', 0.0))
            modelParallax.setYSlide(missionParallaxConfig.get('ySlide', 0.0))
            modelParallax.setParallaxStructure(parallaxStructure)
            modelParallax.setAtlas(chunks)
            modelParallax.setChunkFileExt(missionParallaxConfig.get('chunkFileExt', ''))
            modelParallax.setChunksAssetsPath(missionParallaxConfig.get('chunksAssetsPath', ''))
            return


def _totalSeconds(endDate):
    return max(int((endDate - datetime.utcnow()).total_seconds()), 0)


def _readSection(path):
    if path == '':
        return ''
    else:
        section = ResMgr.openSection(path)
        ResMgr.purge(path)
        return section.asString if section is not None else ''


def _toJson(inputData):
    try:
        jsonData = json.loads(inputData)
    except Exception as e:
        _logger.error('%s', e)
        return None

    if not jsonData:
        _logger.error('Empty jsonData received')
        return None
    else:
        return jsonData


def _getChunks(count, name, path):
    allChunks = dict()
    for i in xrange(count):
        chunkPath = '{0}{1}{2}.json'.format(path, name, str(i))
        chunk = _toJson(_readSection(chunkPath))
        if chunk is not None:
            allChunks.update(chunk)
        _logger.error('Chunk of parallax atlas is None')

    return json.dumps(allChunks)
