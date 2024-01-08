# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/game_control/story_mode_controller.py
from logging import getLogger
import typing
import BigWorld
import Event
import SoundGroups
import WWISE
from PlayerEvents import g_playerEvents
from StoryModeAccountComponent import StoryModeAccountComponent
from account_helpers import AccountSyncData
from adisp import adisp_process
from chat_shared import SYS_MESSAGE_TYPE
from frameworks.wulf import WindowLayer
from gui import app_loader
from gui.Scaleform.framework.managers.loaders import g_viewOverrider
from gui.Scaleform.framework.view_overrider import OverrideData
from gui.battle_results import RequestResultsContext
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty, prbDispatcherProperty
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
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
from skeletons.ui_logging import IUILoggingCore
from story_mode.gui.battle_control.arena_info.player_format import StoryModeNameFormatter
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.impl.lobby.base_prb_view import BasePrbView
from story_mode.gui.shared.event_dispatcher import showMissionSelectionView
from story_mode.gui.story_mode_gui_constants import STOP_ONBOARDING_MUSIC, SOUND_REMAPPING, START_ONBOARDING_MUSIC, GAMEMODE_GROUP, GAMEMODE_STATE
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.configs.story_mode_missions import missionsSchema, MissionsModel, MissionModel
from story_mode_common.configs.story_mode_settings import settingsSchema, SettingsModel
from story_mode_common.story_mode_constants import LOGGER_NAME, QUEUE_TYPE, SM_CONGRATULATIONS_MESSAGE, STORY_MODE_GAME_PARAMS_KEY
from story_mode_common.story_mode_constants import UNDEFINED_MISSION_ID, FIRST_MISSION_ID, ARENA_BONUS_TYPE, STORY_MODE_PDATA_KEY, PROGRESS_PDATA_KEY
if typing.TYPE_CHECKING:
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from gui.Scaleform.battle_entry import BattleEntry
_logger = getLogger(LOGGER_NAME)

class StoryModeController(IStoryModeController, IGlobalListener):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _appLoader = dependency.descriptor(IAppLoader)
    _battleResults = dependency.descriptor(IBattleResultsService)
    _webController = dependency.descriptor(IWebController)
    _uiLoggerCore = dependency.descriptor(IUILoggingCore)

    def __init__(self):
        self.__wasOnboardingSkipped = False
        self.__selectedMissionId = UNDEFINED_MISSION_ID
        self.__selectRandomBattle = False
        self.__isOnboarding = False
        self.__needToShowAward = False
        self.__lobbyViewOverrideData = None
        self.__syncData = {}
        self.__isQuittingBattle = False
        self.__isOnboardingMusicStarted = False
        self.__isNameFormatterSubstituted = False
        self.onSyncDataUpdated = Event.Event()
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
        return self.__needToShowAward

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
        g_playerEvents.onAccountShowGUISkipped += self.__onAccountShowGUISkipped
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        g_playerEvents.onConfigModelUpdated += self.__configModelUpdateHandler
        g_eventBus.addListener(events.PrebattleEvent.NOT_SWITCHED, self.__unsuccessfulSwitchHandler, scope=EVENT_BUS_SCOPE.LOBBY)

    def fini(self):
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handleChatMessage
        g_playerEvents.onAccountShowGUISkipped -= self.__onAccountShowGUISkipped
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        g_playerEvents.onConfigModelUpdated -= self.__configModelUpdateHandler
        g_eventBus.removeListener(events.PrebattleEvent.NOT_SWITCHED, self.__unsuccessfulSwitchHandler, scope=EVENT_BUS_SCOPE.LOBBY)

    def onDisconnected(self):
        self.stopGlobalListening()
        self.stopOnboardingMusic()
        self.__wasOnboardingSkipped = False
        self.__isQuittingBattle = False
        self.__selectedMissionId = UNDEFINED_MISSION_ID
        self.__selectRandomBattle = True
        self.__isOnboarding = False
        self.__needToShowAward = False
        self.__syncData = {}
        self.__onExitPrb()

    def onAccountBecomeNonPlayer(self):
        g_eventBus.removeListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__guiImplViewLoaded, EVENT_BUS_SCOPE.LOBBY)

    def isEnabled(self):
        return self.settings.enabled

    def isMissionCompleted(self, missionId):
        return missionId in self.__syncData.get(PROGRESS_PDATA_KEY, ())

    def getFirstMission(self):
        return self.missions.missions[0]

    def getNextMission(self, missionId):
        nextMissionId = missionId + 1
        for mission in self.missions.missions:
            if mission.missionId == nextMissionId:
                return mission

    def skipOnboarding(self):
        _logger.debug('skipOnboarding')
        self.__wasOnboardingSkipped = True
        self.__isQuittingBattle = True
        if isPlayerAvatar():
            self._sessionProvider.exit()

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
        StoryModeAccountComponent.instance().base.StoryModeAccountComponent.removeForceOnboarding()
        isAccount = isPlayerAccount()
        isInQueue = self.prbEntity and self.prbEntity.isInQueue()
        if not isAccount or isInQueue:
            _logger.error('goToHangar method cant be called: isAccount=%s, isInQueue=%s', isAccount, isInQueue)
            return
        else:
            self.__isQuittingBattle = True
            self.__isOnboarding = False
            self.__selectRandomBattle = True
            self.stopOnboardingMusic()
            WWISE.deactivateRemapping(SOUND_REMAPPING)
            BigWorld.player().battleQueueType = QUEUE_TYPE.UNKNOWN
            if guiCtx is None:
                guiCtx = self._lobbyContext.getGuiCtx()
            guiCtx.update({'inQueue': QUEUE_TYPE.UNKNOWN,
             'skipShowGUI': False})
            g_playerEvents.onAccountShowGUI(guiCtx)
            return

    def awardShown(self):
        self.__needToShowAward = False

    def startOnboardingMusic(self, event=None):
        if not self.__isOnboardingMusicStarted:
            self.__isOnboardingMusicStarted = True
            WWISE.WW_setState(GAMEMODE_GROUP, GAMEMODE_STATE)
            SoundGroups.g_instance.playSound2D(START_ONBOARDING_MUSIC if event is None else event)
        return

    def stopOnboardingMusic(self):
        if self.__isOnboardingMusicStarted:
            self.__isOnboardingMusicStarted = False
            SoundGroups.g_instance.playSound2D(STOP_ONBOARDING_MUSIC)

    @adisp_process
    def onLobbyInited(self, *_):
        if (self.__selectRandomBattle or not self.isEnabled()) and self.__isInPrb():
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        self.__selectRandomBattle = False
        self.__isOnboarding = False

    def onPrbEntitySwitching(self):
        if self.__isInPrb():
            self.__onExitPrb()

    def onPrbEntitySwitched(self):
        if not self.__selectRandomBattle and self.isEnabled() and self.__isInPrb():
            self.__onEnterPrb()
            if self.__selectedMissionId == UNDEFINED_MISSION_ID:
                self.__selectedMissionId = next((mission.missionId for mission in self.missions.missions if not self.isMissionCompleted(mission.missionId)), FIRST_MISSION_ID)
            showMissionSelectionView()
        else:
            self.__selectedMissionId = UNDEFINED_MISSION_ID

    def onAvatarBecomePlayer(self):
        self.__isQuittingBattle = False
        arenaBonusType = self._sessionProvider.arenaVisitor.getArenaBonusType()
        if arenaBonusType == ARENA_BONUS_TYPE.STORY_MODE:
            self._sessionProvider.getCtx().setPlayerFullNameFormatter(StoryModeNameFormatter())
            self.__isNameFormatterSubstituted = True
            BigWorld.player().waitForPlayerChoice()

    @adisp_process
    def onKickedFromQueue(self, queueType, *args):
        if queueType == QUEUE_TYPE.STORY_MODE and self.__isInPrb() and not self.isEnabled() and not self.__isOnboarding:
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    def __onAvatarBecomeNonPlayer(self):
        if self.__isNameFormatterSubstituted:
            self.__isNameFormatterSubstituted = False
            self._sessionProvider.getCtx().resetPlayerFullNameFormatter()

    def __configModelUpdateHandler(self, schemaName):
        if schemaName == STORY_MODE_GAME_PARAMS_KEY:
            if not self.isEnabled():
                self.__lobbyViewOverrideData = None
        return

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()

    def __onAccountShowGUISkipped(self, ctx):
        isStoryModeQueue = ctx.get('inQueue', QUEUE_TYPE.UNKNOWN) == QUEUE_TYPE.STORY_MODE
        skippedShowGUI = ctx.get('skipShowGUI', False)
        if not (isStoryModeQueue and skippedShowGUI):
            return
        else:
            battleCtx = self._sessionProvider.getCtx()
            lastArenaUniqueID = battleCtx.lastArenaUniqueID
            if self.__wasOnboardingSkipped:
                self.goToHangar(guiCtx=ctx)
            else:
                self._lobbyContext.onAccountShowGUI(ctx)
                self._uiLoggerCore.start(ensureSession=True)
                self._webController.start(force=False)
                self._uiLoggerCore.send()
                if lastArenaUniqueID:
                    self.__showBattleResults(lastArenaUniqueID)
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
        yield self._battleResults.requestResults(RequestResultsContext(arenaUniqueID=lastArenaUniqueId, arenaBonusType=ARENA_BONUS_TYPE.STORY_MODE))

    def __isInPrb(self):
        return self.prbEntity is not None and self.prbEntity.getEntityType() == QUEUE_TYPE.STORY_MODE and not self.prbEntity.isInQueue()

    def __onEnterPrb(self):
        self.stopOnboardingMusic()
        WWISE.activateRemapping(SOUND_REMAPPING)
        g_viewOverrider.addOverride(VIEW_ALIAS.LOBBY_HANGAR, self.__viewOverrideDelegate)
        g_eventBus.addListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__guiImplViewLoaded, EVENT_BUS_SCOPE.LOBBY)

    def __onExitPrb(self):
        WWISE.deactivateRemapping(SOUND_REMAPPING)
        g_viewOverrider.removeOverride(VIEW_ALIAS.LOBBY_HANGAR, self.__viewOverrideDelegate)
        self.__lobbyViewOverrideData = None
        g_eventBus.removeListener(events.ViewEventType.LOAD_GUI_IMPL_VIEW, self.__guiImplViewLoaded, EVENT_BUS_SCOPE.LOBBY)
        return

    def __viewOverrideDelegate(self, *_, **__):
        return self.__lobbyViewOverrideData

    def __guiImplViewLoaded(self, event):
        if issubclass(event.loadParams.viewClass, BasePrbView):
            self.__lobbyViewOverrideData = OverrideData(event.loadParams, *event.args, **event.kwargs)

    def __handleChatMessage(self, _, message):
        if message.type == SYS_MESSAGE_TYPE.lookup(SM_CONGRATULATIONS_MESSAGE).index():
            self.__needToShowAward = True

    def __onClientUpdated(self, diff, *_):
        isFullSync = AccountSyncData.isFullSyncDiff(diff)
        if isFullSync:
            self.__syncData = {}
        diff = diff.get(STORY_MODE_PDATA_KEY)
        if diff is not None:
            synchronizeDicts(diff, self.__syncData)
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
            containerManager.destroyViews(VIEW_ALIAS.STORY_MODE_SETTINGS_WINDOW)
            containerManager.destroyViews(VIEW_ALIAS.INGAME_HELP)
            return

    @UseStoryModeFading(layer=WindowLayer.TOP_SUB_VIEW, show=False)
    def __unsuccessfulSwitchHandler(self, *_):
        pass
