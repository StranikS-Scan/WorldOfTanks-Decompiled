# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/game_control/story_mode_controller.py
from logging import getLogger
import typing
import AccountCommands
import BigWorld
import Event
import WWISE
from PlayerEvents import g_playerEvents
from account_helpers import AccountSyncData
from adisp import adisp_process
from chat_shared import SYS_MESSAGE_TYPE
from constants import ARENA_BONUS_TYPE, QUEUE_TYPE
from frameworks.wulf import WindowLayer
from gui import app_loader
from gui.Scaleform.framework.managers.loaders import g_viewOverrider
from gui.Scaleform.framework.view_overrider import OverrideData
from gui.battle_results import RequestResultsContext
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty, prbDispatcherProperty
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency, isPlayerAvatar, isPlayerAccount
from helpers.server_settings import ServerSettings
from messenger.proto.events import g_messengerEvents
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
from skeletons.helpers.statistics import IStatisticsCollector
from skeletons.ui_logging import IUILoggingCore
from skeletons.gui.shared import IItemsCache
from story_mode.account_settings import isNewbieAdvertisingScreenSeen, getMissionNewSeenId, setMissionNewSeenId
from story_mode.gui.battle_control.arena_info.player_format import StoryModeNameFormatter
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.impl.lobby.base_prb_view import BasePrbView
from story_mode.gui.shared.event_dispatcher import showMissionSelectionView, showNewbieAdvertisingWindow
from story_mode.gui.story_mode_gui_constants import SOUND_REMAPPING, GAMEMODE_GROUP, GAMEMODE_DEFAULT, PREBATTLE_ACTION_NAME, VIEW_ALIAS
from story_mode.gui.game_control.sounds_controller import SoundsController
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.configs.story_mode_missions import missionsSchema, MissionsModel, MissionModel
from story_mode_common.configs.story_mode_settings import settingsSchema, SettingsModel
from story_mode_common.helpers import isMissionCompleted, isTaskCompleted, isMissionDisabledByABGroup
from story_mode_common.story_mode_constants import LOGGER_NAME, SM_CONGRATULATIONS_MESSAGE, STORY_MODE_BONUS_TYPES, UNDEFINED_MISSION_ID, STORY_MODE_PDATA_KEY, PROGRESS_PDATA_KEY, MissionsDifficulty, MissionType, STORY_MODE_AB_FEATURE
from uilogging.performance.battle.loggers import BattleMetricsLogger
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from gui.Scaleform.battle_entry import BattleEntry
_logger = getLogger(LOGGER_NAME)

class StoryModeOverrideData(OverrideData):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def checkCondition(self, *args, **kwargs):
        return self._storyModeCtrl.isInPrb()


class StoryModeController(IStoryModeController, IGlobalListener):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _appLoader = dependency.descriptor(IAppLoader)
    _battleResults = dependency.descriptor(IBattleResultsService)
    _itemsCache = dependency.descriptor(IItemsCache)
    _webController = dependency.descriptor(IWebController)
    _uiLoggerCore = dependency.descriptor(IUILoggingCore)
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        self.__selectedMissionId = UNDEFINED_MISSION_ID
        self.__selectRandomBattle = False
        self.__isOnboarding = False
        self.__needToShowAwardData = None
        self.__lobbyViewOverrideData = None
        self.__syncData = {}
        self.__isQuittingBattle = False
        self.__isNameFormatterSubstituted = False
        self.__missionsProgressDiff = {}
        self.__soundController = SoundsController()
        self.onSyncDataUpdated = Event.Event()
        self.onMissionsConfigUpdated = Event.Event()
        return

    @property
    def isOnboarding(self):
        return self.__isOnboarding

    @property
    def isQuittingBattle(self):
        return self.__isQuittingBattle

    @property
    def selectedMissionId(self):
        return self.__selectedMissionId

    @property
    def isSelectedMissionOnboarding(self):
        return self.missions.isOnboarding(self.__selectedMissionId)

    @selectedMissionId.setter
    def selectedMissionId(self, value):
        self.__selectedMissionId = value

    @property
    def settings(self):
        return self._serverSettings.getConfigModel(settingsSchema)

    @property
    def missions(self):
        return self._serverSettings.getConfigModel(missionsSchema)

    @property
    def needToShowAward(self):
        return bool(self.__needToShowAwardData)

    @property
    def _serverSettings(self):
        return self._lobbyContext.getServerSettings()

    @prbEntityProperty
    def prbEntity(self):
        pass

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def init(self):
        g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__handleChatMessage
        g_playerEvents.onAccountComponentsSynced += self.__onAccountComponentsSynced
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        g_playerEvents.onConfigModelUpdated += self.__configModelUpdateHandler
        g_eventBus.addListener(events.PrebattleEvent.NOT_SWITCHED, self.__unsuccessfulSwitchHandler, scope=EVENT_BUS_SCOPE.LOBBY)

    def fini(self):
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handleChatMessage
        g_playerEvents.onAccountComponentsSynced -= self.__onAccountComponentsSynced
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        g_playerEvents.onConfigModelUpdated -= self.__configModelUpdateHandler
        g_eventBus.removeListener(events.PrebattleEvent.NOT_SWITCHED, self.__unsuccessfulSwitchHandler, scope=EVENT_BUS_SCOPE.LOBBY)

    def onDisconnected(self):
        self.stopGlobalListening()
        self.__isQuittingBattle = False
        self.__selectedMissionId = UNDEFINED_MISSION_ID
        self.__selectRandomBattle = True
        self.__isOnboarding = False
        self.__needToShowAwardData = None
        self.__syncData = {}
        self.__missionsProgressDiff = {}
        self.__onExitPrb()
        return

    def isEventEntryPointVisible(self):
        return any((not isTaskCompleted(self.__progress, mission.missionId, task.id) for mission in self.filterMissions(missionType=MissionType.EVENT) for task in mission.tasks if not task.isLocked()))

    def isShowActiveModeState(self):
        return self.isEnabled() and any((not isMissionCompleted(self.__progress, mission) for mission in self.filterMissions(missionType=MissionType.EVENT)))

    def onAccountBecomeNonPlayer(self):
        g_eventBus.removeListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__guiImplViewLoaded, EVENT_BUS_SCOPE.LOBBY)

    def isEnabled(self):
        return self.settings.enabled

    def isInPrb(self):
        return self.prbEntity is not None and self.prbEntity.getEntityType() == QUEUE_TYPE.STORY_MODE and not self.prbEntity.isInQueue()

    @adisp_process
    def switchPrb(self):
        if self.isEnabled() and not self.isInPrb():
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.STORY_MODE))

    def popMissionProgressDiff(self, missionId):
        return self.__missionsProgressDiff.pop(missionId, 0)

    def isMissionCompleted(self, missionId):
        mission = self.missions.getMission(missionId)
        return False if not mission else isMissionCompleted(self.__progress, mission)

    def isEventMissionSuitable(self, mission):
        return not self.isMissionCompleted(mission.missionId) and any((not self.isMissionTaskCompleted(mission.missionId, task.id) for task in mission.getUnlockedTasks()))

    def isFirstTaskNotCompleted(self, mission):
        battlesCount = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        isMissionLocked = battlesCount < mission.unlockBattlesCount
        task = mission.getTask(1)
        return not isMissionLocked and not task.isLocked() and not self.isMissionTaskCompleted(mission.missionId, task.id)

    def isAnyTaskNotCompleted(self, mission):
        battlesCount = self._itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
        return not mission.isMissionLocked(battlesCount) and any((not self.isMissionTaskCompleted(mission.missionId, task.id) for task in mission.getUnlockedTasks()))

    def isSelectedMissionLocked(self):
        battlesCount = self._itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
        mission = self.missions.getMission(self.__selectedMissionId)
        return mission is not None and mission.isMissionLocked(battlesCount)

    def isMissionTaskCompleted(self, missionId, taskId):
        return isTaskCompleted(self.__progress, missionId, taskId)

    def filterMissions(self, missionType=None):
        for mission in self.missions.filter(enabled=True, missionType=missionType):
            if not self._isMissionDisabledByABGroup(mission):
                yield mission

    def isNewbieGuidanceNeeded(self):
        isNewbieGuidanceNeeded = False
        battlesCount = self._itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
        for mission in self.filterMissions(missionType=MissionType.REGULAR):
            isNewbieGuidanceNeeded |= mission.newbieBattlesMin <= battlesCount <= mission.newbieBattlesMax and self.isFirstTaskNotCompleted(mission) and mission.missionType == MissionType.REGULAR

        return isNewbieGuidanceNeeded and self.isEnabled()

    def isNewNeededForNewbies(self):
        showNewMissionId = UNDEFINED_MISSION_ID
        for mission in self.filterMissions(missionType=MissionType.REGULAR):
            if self.isFirstTaskNotCompleted(mission) and mission.missionType == MissionType.REGULAR:
                showNewMissionId = mission.missionId

        return self.isNewbieGuidanceNeeded() and getMissionNewSeenId() < showNewMissionId

    def setNewForNewbiesSeen(self):
        lastCachedMissionId = getMissionNewSeenId()
        for mission in self.filterMissions(missionType=MissionType.REGULAR):
            if self.isFirstTaskNotCompleted(mission) and mission.missionType == MissionType.REGULAR and mission.missionId > lastCachedMissionId:
                setMissionNewSeenId(mission.missionId)

    def getFirstMission(self):
        return self.missions.missions[0]

    def getNextMission(self, missionId):
        nextMissionId = missionId + 1
        for mission in self.missions.missions:
            if mission.missionId == nextMissionId:
                return mission

    def quitBattle(self):
        player = BigWorld.player()
        _logger.debug('quitBattle')
        self.__isQuittingBattle = True
        if not player:
            _logger.error('quitBattle: player is not available')
            return
        else:
            self.__selectRandomBattle = self.__isOnboarding
            self.__isOnboarding = False
            player._doCmdNoArgs(AccountCommands.CMD_REMOVE_FORCE_ONBOARDING, None)
            if isPlayerAvatar():
                self._sessionProvider.exit()
            return

    def goToQueue(self):
        g_prbLoader.createBattleDispatcher()
        g_prbLoader.setEnabled(enabled=True)
        self.prbEntity.doAction()

    def exitQueue(self):
        g_prbLoader.onAccountBecomeNonPlayer()
        self.goToHangar()

    @staticmethod
    def goToBattle():
        _logger.debug('goToBattle')
        if not isPlayerAvatar():
            _logger.error('goToBattle method can be called only for Avatar.')
            return None
        else:
            BigWorld.player().setPlayerReadyToBattle()
            return None

    def goToHangar(self, guiCtx=None):
        isAccount = isPlayerAccount()
        isInQueue = self.prbEntity and self.prbEntity.isInQueue()
        if not isAccount or isInQueue:
            _logger.error('goToHangar method cant be called: isAccount=%s, isInQueue=%s', isAccount, isInQueue)
            return
        else:
            BigWorld.player()._doCmdNoArgs(AccountCommands.CMD_REMOVE_FORCE_ONBOARDING, None)
            self.__isQuittingBattle = True
            self.__isOnboarding = False
            self.__selectRandomBattle = True
            self.stopMusic()
            WWISE.deactivateRemapping(SOUND_REMAPPING)
            WWISE.WW_setState(GAMEMODE_GROUP, GAMEMODE_DEFAULT)
            BigWorld.player().battleQueueType = QUEUE_TYPE.UNKNOWN
            if guiCtx is None:
                guiCtx = self._lobbyContext.getGuiCtx()
            guiCtx.update({'inQueue': QUEUE_TYPE.UNKNOWN,
             'skipHangar': False})
            g_playerEvents.onAccountShowGUI(guiCtx)
            return

    def popWaitingToBeShownAwardData(self):
        awardData = self.__needToShowAwardData
        self.__needToShowAwardData = None
        return awardData

    def startMusic(self):
        selectedMission = self.missions.getMission(self.selectedMissionId)
        self.__soundController.startMusicAndAmbience(selectedMission.sounds if selectedMission else None)
        return

    def stopMusic(self):
        self.__soundController.stopMusicAndAmbience()

    @adisp_process
    def onLobbyInited(self, *_):
        if (self.__selectRandomBattle or not self.isEnabled()) and self.isInPrb():
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        self.__selectRandomBattle = False
        self.__isOnboarding = False
        if self.isNewbieGuidanceNeeded() and not isNewbieAdvertisingScreenSeen():
            showNewbieAdvertisingWindow()

    def onPrbEntitySwitching(self):
        if self.isInPrb():
            self.__onExitPrb()

    def onPrbEntitySwitched(self):
        if not self.__selectRandomBattle and self.isEnabled() and self.isInPrb():
            self.__onEnterPrb()
            if self.__selectedMissionId == UNDEFINED_MISSION_ID:
                self.__assignSelectedMission()
            showMissionSelectionView()
        else:
            self.__selectedMissionId = UNDEFINED_MISSION_ID

    def onAvatarBecomePlayer(self):
        self.__isQuittingBattle = False
        arenaBonusType = self._sessionProvider.arenaVisitor.getArenaBonusType()
        if arenaBonusType in STORY_MODE_BONUS_TYPES:
            self._sessionProvider.getCtx().setPlayerFullNameFormatter(StoryModeNameFormatter())
            self.__isNameFormatterSubstituted = True
            BigWorld.player().waitForPlayerChoice()

    @adisp_process
    def onKickedFromQueue(self, queueType, *args):
        if queueType == QUEUE_TYPE.STORY_MODE and self.isInPrb() and not self.isEnabled() and not self.__isOnboarding:
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    def chooseSelectedMissionId(self, isEvent=False):
        chooser = self.__chooseEventSelectedMissionIds if isEvent else self.__chooseNewbieSelectedMissionIds
        missionId, defaultMissionId = chooser()
        return missionId if missionId != UNDEFINED_MISSION_ID else defaultMissionId

    def _isMissionDisabledByABGroup(self, mission):
        group = self._itemsCache.items.stats.getABGroup(feature=STORY_MODE_AB_FEATURE)
        abConfig = self._lobbyContext.getServerSettings().abFeatureTestConfig
        return isMissionDisabledByABGroup(mission, group, getattr(abConfig, STORY_MODE_AB_FEATURE, None))

    def __onAvatarBecomeNonPlayer(self):
        self.stopMusic()
        if self.__isNameFormatterSubstituted:
            self.__isNameFormatterSubstituted = False
            self._sessionProvider.getCtx().resetPlayerFullNameFormatter()

    def __configModelUpdateHandler(self, gpKey):
        if settingsSchema.gpKey == gpKey:
            if not self.isEnabled():
                self.__lobbyViewOverrideData = None
        elif missionsSchema.gpKey == gpKey:
            if self.__selectedMissionId != UNDEFINED_MISSION_ID:
                mission = self.missions.getMission(self.__selectedMissionId)
                if not mission or not mission.enabled:
                    self.__assignSelectedMission()
            self.onMissionsConfigUpdated()
        return

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()

    def __onAccountComponentsSynced(self, ctx, result):
        isStoryModeQueue = ctx.get('inQueue', QUEUE_TYPE.UNKNOWN) == QUEUE_TYPE.STORY_MODE
        skippedHangar = ctx.get('skipHangar', False)
        if not (isStoryModeQueue and skippedHangar and result):
            return
        else:
            battleCtx = self._sessionProvider.getCtx()
            lastArenaUniqueID = battleCtx.lastArenaUniqueID
            if lastArenaUniqueID:
                self.__showBattleResults(lastArenaUniqueID)
                resultVO = self._battleResults.getResultsVO(lastArenaUniqueID)
                if resultVO['isForceOnboarding'] and self.isEnabled():
                    missionId = resultVO['missionId']
                    lastMissionId = self.missions.onboardingLastMissionId
                    if missionId != lastMissionId or resultVO['finishResult'] != PLAYER_TEAM_RESULT.WIN:
                        self._statsCollector.needCollectSystemData(False)
                        statisticsLogger = BattleMetricsLogger()
                        statisticsLogger.initialize()
                        statisticsLogger.log()
            else:
                self.__isOnboarding = True
                self.goToQueue()
                WWISE.activateRemapping(SOUND_REMAPPING)
            battleCtx.lastArenaUniqueID = None
            battleCtx.lastArenaBonusType = None
            return

    def __showBattleResults(self, lastArenaUniqueId):
        app = self._appLoader.getApp()
        self._appLoader.getWaitingWorker().hide(R.strings.waiting.exit_battle())
        if app is not None and app.initialized:
            self.__requestBattleResults(lastArenaUniqueId)
            self.__closeExcessiveWindows()
        else:

            def _onAppInitialized(event):
                if event.ns == app_loader.settings.APP_NAME_SPACE.SF_LOBBY:
                    self.__requestBattleResults(lastArenaUniqueId)
                    g_eventBus.removeListener(events.AppLifeCycleEvent.INITIALIZED, _onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)

            g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, _onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)
        return

    @adisp_process
    def __requestBattleResults(self, lastArenaUniqueId):
        yield self._battleResults.requestResults(RequestResultsContext(arenaUniqueID=lastArenaUniqueId, arenaBonusType=ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING))

    def __onEnterPrb(self):
        WWISE.activateRemapping(SOUND_REMAPPING)
        g_viewOverrider.addOverride(VIEW_ALIAS.LOBBY_HANGAR, self.__viewOverrideDelegate)
        g_eventBus.addListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__guiImplViewLoaded, EVENT_BUS_SCOPE.LOBBY)

    def __onExitPrb(self):
        self.stopMusic()
        WWISE.deactivateRemapping(SOUND_REMAPPING)
        WWISE.WW_setState(GAMEMODE_GROUP, GAMEMODE_DEFAULT)
        g_viewOverrider.removeOverride(VIEW_ALIAS.LOBBY_HANGAR, self.__viewOverrideDelegate)
        self.__lobbyViewOverrideData = None
        g_eventBus.removeListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__guiImplViewLoaded, EVENT_BUS_SCOPE.LOBBY)
        return

    def __viewOverrideDelegate(self, *_, **__):
        return self.__lobbyViewOverrideData

    def __guiImplViewLoaded(self, event):
        if issubclass(event.loadParams.viewClass, BasePrbView):
            self.__lobbyViewOverrideData = StoryModeOverrideData(event.loadParams, *event.args, **event.kwargs)

    def __handleChatMessage(self, _, message):
        if message.type == SYS_MESSAGE_TYPE.lookup(SM_CONGRATULATIONS_MESSAGE).index():
            self.__needToShowAwardData = message.data

    def __onClientUpdated(self, diff, *_):
        isFullSync = AccountSyncData.isFullSyncDiff(diff)
        if isFullSync:
            self.__syncData = {}
            self.__missionsProgressDiff = {}
        diff = diff.get(STORY_MODE_PDATA_KEY)
        if diff is not None:
            oldProgress = self.__progress.copy()
            synchronizeDicts(diff, self.__syncData)
            if not isFullSync:
                self.__missionsProgressDiff = {missionId:missionProgress ^ oldProgress.get(missionId, 0) for missionId, missionProgress in self.__progress.iteritems()}
            self.onSyncDataUpdated()
        return

    def __closeExcessiveWindows(self):
        battleApp = self._appLoader.getDefBattleApp()
        if battleApp is None:
            return
        else:
            containerManager = battleApp.containerManager
            if containerManager is None:
                return
            containerManager.destroyViews(VIEW_ALIAS.INGAME_MENU)
            containerManager.destroyViews(VIEW_ALIAS.ONBOARDING_SETTINGS_WINDOW)
            containerManager.destroyViews(VIEW_ALIAS.INGAME_HELP)
            return

    @UseStoryModeFading(layer=WindowLayer.TOP_SUB_VIEW, show=False)
    def __unsuccessfulSwitchHandler(self, *_):
        pass

    @property
    def __progress(self):
        return self.__syncData.get(PROGRESS_PDATA_KEY, {})

    def __chooseSelectedMissionsIds(self, missionType=MissionType.REGULAR, precondition=lambda m: True, condition=lambda m: True):
        lastEnabled, firstSuitable = UNDEFINED_MISSION_ID, UNDEFINED_MISSION_ID
        for mission in self.filterMissions(missionType=missionType):
            if precondition(mission):
                if condition(mission):
                    return (mission.missionId, mission.missionId)
            if lastEnabled == UNDEFINED_MISSION_ID or lastEnabled < mission.missionId:
                lastEnabled = mission.missionId

        _logger.debug('[Controller] Missions <%s>, <%s> chosen.', firstSuitable, lastEnabled)
        return (firstSuitable, lastEnabled)

    def __chooseLastUnlockedMissionIds(self):
        lastEnabled, firstSuitable = UNDEFINED_MISSION_ID, UNDEFINED_MISSION_ID
        missionsList = list(self.filterMissions(missionType=MissionType.REGULAR))
        for mission in missionsList[::-1]:
            battlesCount = self._itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
            if not mission.isMissionLocked(battlesCount):
                return (mission.missionId, mission.missionId)
            if firstSuitable == UNDEFINED_MISSION_ID:
                firstSuitable = mission.missionId
            if lastEnabled == UNDEFINED_MISSION_ID or lastEnabled < mission.missionId:
                lastEnabled = mission.missionId

        _logger.debug('[Controller] Missions <%s>, <%s> chosen.', firstSuitable, lastEnabled)
        return (firstSuitable, lastEnabled)

    def __chooseNewbieSelectedMissionIds(self):
        for precondition, condition in ((self.isFirstTaskNotCompleted, lambda m: m.missionType == MissionType.REGULAR), (self.isAnyTaskNotCompleted, lambda m: m.missionType == MissionType.REGULAR), (self.isAnyTaskNotCompleted, lambda m: m.missionType == MissionType.ONBOARDING)):
            firstSuitable, lastEnabled = self.__chooseSelectedMissionsIds(precondition=precondition, condition=condition)
            if firstSuitable != UNDEFINED_MISSION_ID:
                return (firstSuitable, lastEnabled)

        return self.__chooseLastUnlockedMissionIds()

    def __chooseEventSelectedMissionIds(self):
        battlesCount = 0
        if self._itemsCache.isSynced():
            battlesCount = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        difficulties = MissionsDifficulty.getDifficultiesByBattles(battlesCount)
        return self.__chooseSelectedMissionsIds(missionType=MissionType.EVENT, condition=lambda m: m.difficulty in difficulties)

    def __assignSelectedMission(self):
        eMissionId, eDefaultMissionId = self.__chooseEventSelectedMissionIds()
        if eMissionId != UNDEFINED_MISSION_ID:
            self.__selectedMissionId = eMissionId
            _logger.debug('[Controller] Mission <%s> automatically selected.', self.__selectedMissionId)
            return
        if eDefaultMissionId != UNDEFINED_MISSION_ID:
            self.__selectedMissionId = eDefaultMissionId
            _logger.debug('[Controller] Mission <%s> automatically selected.', self.__selectedMissionId)
            return
        missionId, defaultMissionId = self.__chooseNewbieSelectedMissionIds()
        self.__selectedMissionId = missionId if missionId != UNDEFINED_MISSION_ID else defaultMissionId
        _logger.debug('[Controller] Mission <%s> automatically selected.', self.__selectedMissionId)


def eventEntryPointValidator():
    return dependency.instance(IStoryModeController).isEventEntryPointVisible()


def newbieEntryPointValidator():
    return dependency.instance(IStoryModeController).isNewbieGuidanceNeeded() and dependency.instance(IStoryModeController).settings.newbieBannerEnabled
