# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleReplay.py
import base64
import os
import datetime
import json
import copy
import cPickle as pickle
import logging
import httplib
from collections import defaultdict
from functools import partial
import Math
import BigWorld
import ArenaType
import Settings
import CommandMapping
import constants
import Keys
import Event
import AreaDestructibles
import BWReplay
import TriggersManager
from aih_constants import CTRL_MODE_NAME
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui import GUI_CTRL_MODE_FLAG
from gui.SystemMessages import pushI18nMessage, SM_TYPE
from helpers import EffectsList, isPlayerAvatar, isPlayerAccount, getFullClientVersion
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from constants import ARENA_PERIOD
from helpers import dependency
from gui.app_loader import settings
from post_progression_common import SERVER_SETTINGS_KEY
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gameplay import IGameplayLogic, ReplayEventID
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
from constants import ARENA_BONUS_TYPE
_logger = logging.getLogger(__name__)
g_replayCtrl = None
REPLAY_FILE_EXTENSION = '.wotreplay'
AUTO_RECORD_TEMP_FILENAME = 'temp'
FIXED_REPLAY_FILENAME = 'replay_last_battle'
REPLAY_TIME_MARK_CLIENT_READY = 2147483648L
REPLAY_TIME_MARK_REPLAY_FINISHED = 2147483649L
REPLAY_TIME_MARK_CURRENT_TIME = 2147483650L
REPLAY_DOWNLOAD_TIMEOUT = 2.0
FAST_FORWARD_STEP = 20.0
_BATTLE_SIMULATION_KEY_PATH = 'development/replayBattleSimulation'
_POSTMORTEM_CTRL_MODES = (CTRL_MODE_NAME.POSTMORTEM, CTRL_MODE_NAME.DEATH_FREE_CAM, CTRL_MODE_NAME.RESPAWN_DEATH)
_FORWARD_INPUT_CTRL_MODES = (CTRL_MODE_NAME.POSTMORTEM,
 CTRL_MODE_NAME.VIDEO,
 CTRL_MODE_NAME.CAT,
 CTRL_MODE_NAME.DEATH_FREE_CAM)
_IGNORED_SWITCHING_CTRL_MODES = (CTRL_MODE_NAME.SNIPER,
 CTRL_MODE_NAME.ARCADE,
 CTRL_MODE_NAME.ARTY,
 CTRL_MODE_NAME.STRATEGIC,
 CTRL_MODE_NAME.DUAL_GUN,
 CTRL_MODE_NAME.MAP_CASE,
 CTRL_MODE_NAME.MAP_CASE_ARCADE,
 CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD)

class CallbackDataNames(object):
    APPLY_ZOOM = 'applyZoom'
    BC_MARKERS_ONTRIGGERACTIVATED = 'bootcampMarkers_onTriggerActivated'
    BC_MARKERS_ONTRIGGERDEACTIVATED = 'bootcampMarkers_onTriggerDeactivated'
    BC_MARKERS_SHOWMARKER = 'bootcampMarkers_showMarker'
    BC_MARKERS_HIDEMARKER = 'bootcampMarkers_hideMarker'
    BC_HINT_SHOW = 'bootcampHint_show'
    BC_HINT_HIDE = 'bootcampHint_hide'
    BC_HINT_COMPLETE = 'bootcampHint_complete'
    BC_HINT_CLOSE = 'bootcampHint_close'
    BC_HINT_ONHIDED = 'bootcampHint_onHided'
    BW_CHAT2_REPLAY_ACTION_RECEIVED_CALLBACK = 'bw_chat2.onActionReceived'
    CLIENT_VEHICLE_STATE_GROUP = 'client_vehicle_state_{}'
    DYN_SQUAD_SEND_ACTION_NAME = 'DynSquad.SendInvitationToSquad'
    DYN_SQUAD_ACCEPT_ACTION_NAME = 'DynSquad.AcceptInvitationToSquad'
    DYN_SQUAD_REJECT_ACTION_NAME = 'DynSquad.RejectInvitationToSquad'
    GUN_DAMAGE_SOUND = 'gunDamagedSound'
    SHOW_AUTO_AIM_MARKER = 'showAutoAimMarker'
    HIDE_AUTO_AIM_MARKER = 'hideAutoAimMarker'
    MT_CONFIG_CALLBACK = 'mapsTrainingConfigurationCallback'


class SimulatedAoI(object):

    def __init__(self):
        self.__aoiMapping = defaultdict(dict)
        self.__withheld = dict()
        self.__pending = dict()
        self.currentVehicleID = None
        self.currentAvatarID = None
        self.__controlMode = CTRL_MODE_NAME.POSTMORTEM
        return

    def changeVehicle(self, vehicleID):
        if self.currentVehicleID == vehicleID:
            return
        else:
            self.flush(self.__controlMode)
            self.currentVehicleID = vehicleID
            priorAvatarID = self.currentAvatarID
            self.currentAvatarID = None
            if vehicleID:
                vehicleEntity = BigWorld.entities.get(vehicleID)
                if vehicleEntity:
                    self.currentAvatarID = vehicleEntity.avatarID
            if priorAvatarID and priorAvatarID in self.__aoiMapping:
                for entityID, shown in self.__aoiMapping[priorAvatarID].items():
                    if not shown:
                        BWReplay.wg_withholdEntity(entityID, False)
                        self.__withheld[entityID] = False

            currentAoI = None
            if self.currentAvatarID and self.currentAvatarID in self.__aoiMapping:
                currentAoI = self.__aoiMapping[self.currentAvatarID]
            for entityID, isWithheld in self.__withheld.items():
                shouldSee = currentAoI.get(entityID, False) if currentAoI else True
                shouldWithhold = not shouldSee
                if isWithheld != shouldWithhold:
                    BWReplay.wg_withholdEntity(entityID, shouldWithhold)
                    self.__withheld[entityID] = shouldWithhold

            return

    def handleAoIEvent(self, witnessID, entityID, hasEnteredAoI):
        self.__aoiMapping[witnessID][entityID] = hasEnteredAoI
        isWithheld = self.__withheld.setdefault(entityID, False)
        isCurrentAvatar = self.currentAvatarID == witnessID
        if isCurrentAvatar:
            isWithheld = self.__pending.get(entityID, isWithheld)
            shouldWithhold = not hasEnteredAoI
            if isWithheld != shouldWithhold:
                self.__pending[entityID] = shouldWithhold

    def flush(self, controlMode=CTRL_MODE_NAME.POSTMORTEM):
        if controlMode == CTRL_MODE_NAME.VIDEO:
            if self.__controlMode == CTRL_MODE_NAME.VIDEO:
                return
            self.__controlMode = CTRL_MODE_NAME.VIDEO
            for entityID in self.__withheld:
                BWReplay.wg_withholdEntity(entityID, False)

        else:
            for entityID, shouldWithhold in self.__pending.items():
                BWReplay.wg_withholdEntity(entityID, shouldWithhold)
                self.__withheld[entityID] = shouldWithhold

            if self.__controlMode == CTRL_MODE_NAME.VIDEO:
                for entityID, shouldWithhold in self.__withheld.items():
                    if entityID not in self.__pending:
                        BWReplay.wg_withholdEntity(entityID, shouldWithhold)

            self.__pending.clear()
            if self.__controlMode != controlMode:
                self.__controlMode = controlMode

    def reset(self):
        self.__aoiMapping.clear()
        self.__withheld.clear()
        self.__pending.clear()
        self.currentVehicleID = None
        self.currentAvatarID = None
        return


class BattleReplay(object):
    isPlaying = property(lambda self: self.__replayCtrl.isPlaying())
    isServerSideReplay = property(lambda self: self.__replayCtrl.isServerSideReplay)
    isRecording = property(lambda self: self.__replayCtrl.isRecording)
    isClientReady = property(lambda self: self.__replayCtrl.isClientReady)
    isControllingCamera = property(lambda self: self.__replayCtrl.isControllingCamera)
    isOffline = property(lambda self: self.__replayCtrl.isOfflinePlaybackMode)
    isTimeWarpInProgress = property(lambda self: self.__replayCtrl.isTimeWarpInProgress)
    isServerAim = property(lambda self: self.__replayCtrl.isServerAim)
    playerVehicleID = property(lambda self: self.__replayCtrl.playerVehicleID)
    isLoading = property(lambda self: self.__replayCtrl.getAutoStartFileName() is not None and self.__replayCtrl.getAutoStartFileName() != '')
    isPaused = property(lambda self: self.__replayCtrl.playbackSpeed == 0)
    fps = property(lambda self: self.__replayCtrl.fps)
    ping = property(lambda self: self.__replayCtrl.ping)
    compressed = property(lambda self: self.__replayCtrl.isFileCompressed())
    isLaggingNow = property(lambda self: self.__replayCtrl.isLaggingNow)
    playbackSpeed = property(lambda self: self.__replayCtrl.playbackSpeed)
    scriptModalWindowsEnabled = property(lambda self: self.__replayCtrl.scriptModalWindowsEnabled)
    currentTime = property(lambda self: self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_CURRENT_TIME))
    warpTime = property(lambda self: self.__warpTime)
    rewind = property(lambda self: self.__rewind)
    isAutoRecordingEnabled = property(lambda self: self.__isAutoRecordingEnabled)
    arenaInfo = property(lambda self: json.loads(self.__replayCtrl.getArenaInfoStr()))

    def resetUpdateGunOnTimeWarp(self):
        self.__updateGunOnTimeWarp = False

    isUpdateGunOnTimeWarp = property(lambda self: self.__updateGunOnTimeWarp)
    isBattleSimulation = property(lambda self: self.__isBattleSimulation)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    gameplay = dependency.descriptor(IGameplayLogic)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_REPLAY_PREFERENCES):
            userPrefs.write(Settings.KEY_REPLAY_PREFERENCES, '')
        self.__settings = userPrefs[Settings.KEY_REPLAY_PREFERENCES]
        self.__fileName = None
        self.__replayCtrl = BigWorld.WGReplayController()
        self.__replayCtrl.replayFinishedCallback = self.onReplayFinished
        self.__replayCtrl.replayTerminatedCallback = self.onReplayTerminated
        self.__replayCtrl.controlModeChangedCallback = self.onControlModeChanged
        self.__replayCtrl.ammoButtonPressedCallback = self.__onAmmoButtonPressed
        self.__replayCtrl.playerVehicleIDChangedCallback = self.onPlayerVehicleIDChanged
        self.__replayCtrl.clientVersionDiffersCallback = self.onClientVersionDiffers
        self.__replayCtrl.battleChatMessageCallback = self.onBattleChatMessage
        self.__replayCtrl.lockTargetCallback = self.onLockTarget
        self.__replayCtrl.equipmentIdCallback = self.onSetEquipmentId
        self.__replayCtrl.warpFinishedCallback = self.__onTimeWarpFinished
        self.__replayCtrl.sniperModeCallback = self.onSniperModeChanged
        self.__replayCtrl.entityAoIChangedCallback = self.onEntityAoIChangedCallback
        self.__replayCtrl.postTickCallback = self.onPostTickCallback
        self.__isAutoRecordingEnabled = False
        self.__quitAfterStop = False
        self.__isPlayingPlayList = False
        self.__playList = []
        self.__isFinished = False
        self.__isMenuShowed = False
        self.__updateGunOnTimeWarp = False
        self.__isBattleSimulation = False
        self.__lastObservedVehicleID = None
        self.__aoi = SimulatedAoI()
        self.__isVehicleChanging = False
        battleSimulationSection = userPrefs[_BATTLE_SIMULATION_KEY_PATH]
        if battleSimulationSection is not None:
            self.__isBattleSimulation = battleSimulationSection.asBool
        self.__playerDatabaseID = 0
        self.__serverSettings = dict()
        if isPlayerAccount():
            self.__playerDatabaseID = BigWorld.player().databaseID
        self.__playbackSpeedModifiers = (0.0, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
        self.__playbackSpeedModifiersStr = ('0', '1/16', '1/8', '1/4', '1/2', '1', '2', '4', '8', '16')
        self.__playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
        self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
        self.__gunWasLockedBeforePause = False
        self.__wasVideoBeforeRewind = False
        self.__videoCameraMatrix = Math.Matrix()
        self.__replayDir = './replays'
        self.__replayCtrl.clientVersion = BigWorld.wg_getProductVersion()
        self.__enableTimeWarp = False
        self.__isChatPlaybackEnabled = True
        self.__warpTime = -1.0
        self.__equipmentId = None
        self.__rewind = False
        self.replayTimeout = 0
        self.__arenaPeriod = -1
        self.__previousPeriod = -1
        self.enableAutoRecordingBattles(True)
        self.onCommandReceived = Event.Event()
        self.onAmmoSettingChanged = Event.Event()
        self.onStopped = Event.Event()
        if hasattr(self.__replayCtrl, 'setupStreamExcludeFilter'):
            import streamIDs
            self.__replayCtrl.setupStreamExcludeFilter(streamIDs.STREAM_ID_CHAT_MIN, streamIDs.STREAM_ID_CHAT_MAX)
        if hasattr(self.__replayCtrl, 'setupAvatarMethodExcludeFilter'):
            self.__replayCtrl.setupAvatarMethodExcludeFilter('messenger_onActionByServer_chat2')
        if constants.IS_DEVELOPMENT:
            try:
                import development.replay_override
            except Exception:
                pass

        self.__originalPickleLoads = None
        self.__demandedToWatchFileName = None
        return

    def subscribe(self):
        g_playerEvents.onBattleResultsReceived += self.__onBattleResultsReceived
        g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_playerEvents.onBootcampAccountMigrationComplete += self.__onBootcampAccountMigrationComplete
        g_playerEvents.onAvatarObserverVehicleChanged += self.__onAvatarObserverVehicleChanged
        self.settingsCore.onSettingsChanged += self.__onSettingsChanging

    def unsubscribe(self):
        g_playerEvents.onBattleResultsReceived -= self.__onBattleResultsReceived
        g_playerEvents.onAccountBecomePlayer -= self.__onAccountBecomePlayer
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onBootcampAccountMigrationComplete -= self.__onBootcampAccountMigrationComplete
        g_playerEvents.onAvatarObserverVehicleChanged -= self.__onAvatarObserverVehicleChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanging

    def destroy(self):
        self.stop(isDestroyed=True)
        self.onCommandReceived.clear()
        self.onCommandReceived = None
        self.onAmmoSettingChanged.clear()
        self.onAmmoSettingChanged = None
        self.enableAutoRecordingBattles(False)
        self.__replayCtrl.replayTerminatedCallback = None
        self.__replayCtrl.replayFinishedCallback = None
        self.__replayCtrl.controlModeChangedCallback = None
        self.__replayCtrl.clientVersionDiffersCallback = None
        self.__replayCtrl.playerVehicleIDChangedCallback = None
        self.__replayCtrl.battleChatMessageCallback = None
        self.__replayCtrl.ammoButtonPressedCallback = None
        self.__replayCtrl.lockTargetCallback = None
        self.__replayCtrl.equipmentIdCallback = None
        self.__replayCtrl.warpFinishedCallback = None
        self.__replayCtrl = None
        self.__settings = None
        self.__videoCameraMatrix = None
        self.__warpTime = -1.0
        self.__arenaPeriod = -1
        return

    def testOrCreateReplayDir(self):
        try:
            if not os.path.isdir(self.__replayDir):
                os.makedirs(self.__replayDir)
            return True
        except Exception:
            LOG_ERROR('Failed to create directory for replay files')
            return False

    def record(self, fileName=None):
        if self.isPlaying:
            return False
        if self.isRecording:
            if not self.stop():
                LOG_ERROR('Failed to start recording new replay - cannot stop previous record')
                return False
        useAutoFilename = False
        if fileName is None:
            useAutoFilename = True
        if not self.testOrCreateReplayDir():
            return False
        success = False
        for i in xrange(100):
            try:
                if useAutoFilename:
                    fileName = os.path.join(self.__replayDir, AUTO_RECORD_TEMP_FILENAME + ('' if i == 0 else str(i)) + REPLAY_FILE_EXTENSION)
                f = open(fileName, 'wb')
                f.close()
                os.remove(fileName)
                success = True
                break
            except Exception:
                if useAutoFilename:
                    continue
                else:
                    break

        if not success:
            LOG_ERROR('Failed to create replay file, replays folder may be write-protected')
            return False
        g_replayEvents.onRecording()
        if self.__replayCtrl.startRecording(fileName):
            self.__fileName = fileName
            return True
        else:
            return False

    def play(self, fileName=None):
        if self.isRecording:
            self.stop()
        import SafeUnpickler
        unpickler = SafeUnpickler.SafeUnpickler()
        self.__originalPickleLoads = pickle.loads
        pickle.loads = unpickler.loads
        if fileName is not None and fileName.rfind('.wotreplaylist') != -1:
            self.__playList = []
            self.__isPlayingPlayList = True
            try:
                f = open(fileName)
                s = f.read()
                f.close()
                self.__playList = s.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                fileName = None
            except Exception:
                pass

        if fileName is None:
            if not self.__playList:
                return False
            fileName = self.__playList[0]
            self.__playList.pop(0)
            self.__quitAfterStop = not self.__playList
        self.__fileName = fileName
        if self.__replayCtrl.startPlayback(fileName):
            self.__playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
            self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
            g_replayEvents.onPlaying()
            return True
        else:
            self.__fileName = None
            return False

    def stop(self, rewindToTime=None, delete=False, isDestroyed=False):
        if not self.isPlaying and not self.isRecording:
            return False
        else:
            self.onStopped()
            wasPlaying = self.isPlaying
            wasServerReplay = self.isServerSideReplay
            isOffline = self.__replayCtrl.isOfflinePlaybackMode
            self.__aoi.reset()
            self.__lastObservedVehicleID = None
            self.__replayCtrl.stop(delete)
            self.__fileName = None
            self.__isVehicleChanging = False
            if wasPlaying:
                if isPlayerAvatar():
                    BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
                    BigWorld.player().onObserverVehicleChanged -= self.__onObserverVehicleChanged
                if not isOffline and not isDestroyed:
                    self.connectionMgr.onDisconnected += self.__goToNextReplay
                if wasServerReplay:
                    BigWorld.clearAllSpaces()
                else:
                    BigWorld.clearEntitiesAndSpaces()
                    BigWorld.disconnect()
                g_replayEvents.onReplayTerminated.clear()
                if self.__quitAfterStop:
                    BigWorld.quit()
                elif isOffline and not isDestroyed:
                    self.__goToNextReplay()
            return True

    def getDemandedToWatchFileName(self):
        return self.__demandedToWatchFileName

    def onReplayTerminated(self, reason):
        _logger.debug('BattleReplay.onReplayTerminated: reason=%r', reason)
        g_replayEvents.onReplayTerminated()
        self.__isFinished = False
        if self.__originalPickleLoads is not None:
            pickle.loads = self.__originalPickleLoads
            self.__originalPickleLoads = None
        return

    def onEntityAoIChangedCallback(self, witnessID, entityID, hasEnteredAoI):
        _logger.debug('BattleReplay: onEntityAoIChangedCallback: witnessID=%s, entityID=%s, hasEnteredAoI=%s', witnessID, entityID, hasEnteredAoI)
        self.__aoi.handleAoIEvent(witnessID, entityID, hasEnteredAoI)

    def downloadReplay(self, url, timeout=REPLAY_DOWNLOAD_TIMEOUT, callback=None):
        if not self.testOrCreateReplayDir():
            return
        else:
            LOG_DEBUG('Starting replay download %s into, timeout %ds' % (url, timeout))
            BigWorld.fetchURL(url, partial(self.onReplayDownloaded, url=url, callback=callback), None, timeout, 'GET')
            return

    def onReplayDownloaded(self, response, url='', callback=None):
        filename = os.path.join(self.__replayDir, url.split('/')[-1])
        isSuccess = False
        if response.responseCode != httplib.OK:
            LOG_ERROR('Replay download error : %d' % response.responseCode)
        else:
            try:
                open(filename, 'wb').write(response.body)
                LOG_DEBUG('Replay downloaded to file %s' % filename)
                isSuccess = True
            except EnvironmentError as error:
                LOG_ERROR('Replay write to file error : %s' % error)

        if not isSuccess:
            pushI18nMessage('#system_messages:ssr/unavailable', type=SM_TYPE.Error)
        if callback is not None:
            callback(isSuccess, filename)
        return

    def downloadAndPlayServerSideReplay(self, url):
        self.downloadReplay(url, REPLAY_DOWNLOAD_TIMEOUT, lambda isSuccess, filename: self.startWatchingServerSideReplay(filename) if isSuccess else None)

    def startWatchingServerSideReplay(self, filename, callback=None):
        if not filename or not os.path.isfile(filename):
            LOG_ERROR('Replay file %s is not accessible' % str(filename))
            return
        if isPlayerAccount():
            self.__demandedToWatchFileName = filename
            if self.isRecording:
                self.stop(delete=True)
            BigWorld.player().startWatchingReplay(callback)
        else:
            LOG_ERROR('Player is not Account, cannot start watching')

    def getAutoStartFileName(self):
        return self.__replayCtrl.getAutoStartFileName()

    def autoStartBattleReplay(self):
        fileName = self.getAutoStartFileName()
        if fileName:
            self.__quitAfterStop = True
            if not self.play(fileName):
                BigWorld.quit()
            else:
                return True
        return False

    def getSpaceID(self):
        return BigWorld.player().spaceID

    def handleKeyEvent(self, isDown, key, mods, isRepeat, event):
        if not self.isPlaying:
            return False
        if self.isBattleSimulation:
            return False
        if self.isTimeWarpInProgress:
            return True
        if key == Keys.KEY_F1:
            if not isRepeat and not isDown:
                self.__showInfoMessages()
            return True
        if not self.isClientReady:
            return False
        cmdMap = CommandMapping.g_instance
        player = BigWorld.player()
        if not isPlayerAvatar():
            return False
        isCursorVisible = player.isForcedGuiControlMode()
        if key == Keys.KEY_ESCAPE:
            if isDown and not isCursorVisible:
                self.__isMenuShowed = True
                return False
        if not player.isForcedGuiControlMode():
            self.__isMenuShowed = False
        if self.__isMenuShowed:
            return False
        currReplayTime = self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_CURRENT_TIME)
        finishReplayTime = self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_REPLAY_FINISHED)
        if currReplayTime > finishReplayTime:
            currReplayTime = finishReplayTime
        fastForwardStep = FAST_FORWARD_STEP * (2.0 if mods == 2 else 1.0)
        if key == Keys.KEY_F11 and isDown:
            if self.isPlaying:
                self.__replayCtrl.onPutScreenshotMark()
                return True
        if key == Keys.KEY_LEFTMOUSE or cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key):
            if isDown and not isCursorVisible:
                if self.isServerSideReplay:
                    return self.ssrSwitchViewPoint()
                if self.isControllingCamera:
                    self.appLoader.detachCursor(settings.APP_NAME_SPACE.SF_BATTLE)
                    controlMode = self.getControlMode()
                    if controlMode not in _POSTMORTEM_CTRL_MODES:
                        self.onControlModeChanged('arcade')
                    self.__replayCtrl.isControllingCamera = False
                    self.onControlModeChanged(controlMode)
                    self.__showInfoMessage('replayFreeCameraActivated')
                else:
                    if not self.__isAllowedSavedCamera():
                        return False
                    self.__replayCtrl.isControllingCamera = True
                    self.onControlModeChanged()
                    self.__showInfoMessage('replaySavedCameraActivated')
                return True
        if cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
            if self.isControllingCamera:
                return True
        if key == Keys.KEY_SPACE and isDown and not self.__isFinished:
            if self.__playbackSpeedIdx > 0:
                self.setPlaybackSpeedIdx(0)
            else:
                self.setPlaybackSpeedIdx(self.__savedPlaybackSpeedIdx if self.__savedPlaybackSpeedIdx != 0 else self.__playbackSpeedModifiers.index(1.0))
            return True
        if key == Keys.KEY_DOWNARROW and isDown and not self.__isFinished:
            if self.__playbackSpeedIdx > 0:
                self.setPlaybackSpeedIdx(self.__playbackSpeedIdx - 1)
            return True
        if key == Keys.KEY_UPARROW and isDown and not self.__isFinished:
            if self.__playbackSpeedIdx < len(self.__playbackSpeedModifiers) - 1:
                self.setPlaybackSpeedIdx(self.__playbackSpeedIdx + 1)
            return True
        if key == Keys.KEY_RIGHTARROW and isDown and not self.__isFinished:
            self.__timeWarp(currReplayTime + fastForwardStep)
            return True
        if key == Keys.KEY_LEFTARROW:
            self.__aoi.reset()
            self.__timeWarp(currReplayTime - fastForwardStep)
            return True
        if key == Keys.KEY_HOME and isDown:
            self.__aoi.reset()
            self.__timeWarp(0.0)
            return True
        if key == Keys.KEY_END and isDown and not self.__isFinished:
            self.__timeWarp(finishReplayTime)
            return True
        if key == Keys.KEY_C and isDown:
            self.__isChatPlaybackEnabled = not self.__isChatPlaybackEnabled
        suppressCommand = False
        if cmdMap.isFiredList(xrange(CommandMapping.CMD_AMMO_CHOICE_1, CommandMapping.CMD_AMMO_CHOICE_0 + 1), key) and isDown:
            suppressCommand = True
        elif cmdMap.isFiredList((CommandMapping.CMD_CM_LOCK_TARGET,
         CommandMapping.CMD_CM_LOCK_TARGET_OFF,
         CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE,
         CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE,
         CommandMapping.CMD_RADIAL_MENU_SHOW,
         CommandMapping.CMD_RELOAD_PARTIAL_CLIP), key) and isDown and not isCursorVisible:
            suppressCommand = True
        elif cmdMap.isFiredList((CommandMapping.CMD_STOP_UNTIL_FIRE,
         CommandMapping.CMD_INCREMENT_CRUISE_MODE,
         CommandMapping.CMD_DECREMENT_CRUISE_MODE,
         CommandMapping.CMD_MOVE_FORWARD,
         CommandMapping.CMD_MOVE_FORWARD_SPEC,
         CommandMapping.CMD_MOVE_BACKWARD,
         CommandMapping.CMD_ROTATE_LEFT,
         CommandMapping.CMD_ROTATE_RIGHT,
         CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION), key):
            suppressCommand = True
        if suppressCommand:
            playerControlModeName = player.inputHandler.ctrlModeName
            isForwardInputToCtrlMode = playerControlModeName in _FORWARD_INPUT_CTRL_MODES
            if isForwardInputToCtrlMode:
                player.inputHandler.ctrl.handleKeyEvent(isDown, key, mods, event)
            return True
        return False

    def handleMouseEvent(self, dx, dy, dz):
        if not (self.isPlaying and self.isClientReady):
            return False
        if self.isTimeWarpInProgress:
            return True
        if not isPlayerAvatar():
            return False
        if self.isControllingCamera:
            if dz != 0:
                return True
        return False

    def ssrSwitchViewPoint(self):
        if not self.isServerSideReplay:
            _logger.error('BattleReplay.ssrSwitchViewPoint called but isServerSideReplay==False')
            return False
        return self.ssrSwitchToVideoControlMode() if self.getControlMode() == CTRL_MODE_NAME.POSTMORTEM else self.ssrSwitchToPostmortemControlMode()

    def ssrSwitchToVideoControlMode(self):
        _logger.debug('BattleReplay.ssrSwitchToVideoControlMode')
        if self.getControlMode() == CTRL_MODE_NAME.VIDEO:
            return False
        self.setControlMode(CTRL_MODE_NAME.VIDEO)
        self.onControlModeChanged(CTRL_MODE_NAME.VIDEO)
        self.__showInfoMessage('replayFreeCameraActivated')
        return True

    def ssrSwitchToPostmortemControlMode(self):
        _logger.debug('BattleReplay.ssrSwitchToPostmortemControlMode')
        if self.getControlMode() == CTRL_MODE_NAME.POSTMORTEM:
            return False
        self.setControlMode(CTRL_MODE_NAME.POSTMORTEM)
        self.onControlModeChanged(CTRL_MODE_NAME.POSTMORTEM)
        self.__showInfoMessage('replaySavedCameraActivated')
        return True

    def setGunRotatorTargetPoint(self, value):
        self.__replayCtrl.gunRotatorTargetPoint = value

    def getGunRotatorTargetPoint(self):
        return self.__replayCtrl.gunRotatorTargetPoint

    def setConsumablesPosition(self, pos, direction=Math.Vector3(1, 1, 1)):
        self.__replayCtrl.gunMarkerPosition = pos
        self.__replayCtrl.gunMarkerDirection = direction

    def setGunMarkerParams(self, diameter, pos, direction):
        controlMode = self.getControlMode()
        if controlMode != 'mapcase':
            self.__replayCtrl.gunMarkerDiameter = diameter
            self.__replayCtrl.gunMarkerPosition = pos
            self.__replayCtrl.gunMarkerDirection = direction

    def getGunMarkerParams(self, defaultPos, defaultDir):
        diameter = self.__replayCtrl.gunMarkerDiameter
        direction = self.__replayCtrl.gunMarkerDirection
        pos = self.__replayCtrl.gunMarkerPosition
        if direction == Math.Vector3(0, 0, 0):
            pos = defaultPos
            direction = defaultDir
        return (diameter, pos, direction)

    def getGunMarkerPos(self):
        return self.__replayCtrl.gunMarkerPosition

    def getEquipmentId(self):
        return self.__equipmentId

    def setArcadeGunMarkerSize(self, size):
        self.__replayCtrl.setArcadeGunMarkerSize(size)

    def useSyncroniusResourceLoading(self, use):
        self.__replayCtrl.useSyncroniusResourceLoading = use

    def getArcadeGunMarkerSize(self):
        return self.__replayCtrl.getArcadeGunMarkerSize()

    def setSPGGunMarkerParams(self, dispersionAngle, size):
        self.__replayCtrl.setSPGGunMarkerParams((dispersionAngle, size))

    def getSPGGunMarkerParams(self):
        return self.__replayCtrl.getSPGGunMarkerParams()

    def setAimClipPosition(self, position):
        self.__replayCtrl.setAimClipPosition(position)

    def getAimClipPosition(self):
        return self.__replayCtrl.getAimClipPosition()

    def setTurretYaw(self, value):
        self.__replayCtrl.turretYaw = value

    def getTurretYaw(self):
        return self.__replayCtrl.getTurretYawByTime(self.currentTime)

    def setGunPitch(self, value):
        self.__replayCtrl.gunPitch = value

    def getGunPitch(self):
        return self.__replayCtrl.gunPitch

    def setGunReloadTime(self, startTime, duration):
        self.__replayCtrl.setGunReloadTime(startTime, duration)

    def resetArenaPeriod(self):
        if not self.isRecording:
            LOG_ERROR('Replay is not recorded on resetArenaPeriod')
        self.__replayCtrl.resetArenaPeriod()

    def setArenaPeriod(self, period, length):
        if not self.isRecording:
            LOG_ERROR('Replay is not recorded on setArenaPeriod')
        self.__replayCtrl.arenaPeriod = period
        self.__replayCtrl.arenaLength = length

    def getArenaPeriod(self):
        if not self.isPlaying:
            raise SoftException('Replay is not playing')
        return self.__replayCtrl.arenaPeriod

    def getArenaLength(self):
        if not self.isPlaying:
            raise SoftException('Replay is not playing')
        return self.__replayCtrl.arenaLength

    def setPlayerVehicleID(self, vehicleID):
        if vehicleID == 0 and isPlayerAvatar():
            vehicleID = BigWorld.player().playerVehicleID
        self.__replayCtrl.playerVehicleID = vehicleID

    def setPlaybackSpeedIdx(self, value):
        if self.isTimeWarpInProgress:
            return
        else:
            self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
            self.__playbackSpeedIdx = value
            newSpeed = self.__playbackSpeedModifiers[self.__playbackSpeedIdx]
            self.__enableInGameEffects(0.0 < newSpeed < 8.0)
            g_replayEvents.onMuteSound(newSpeed == 0.0)
            player = BigWorld.player()
            if newSpeed != self.__replayCtrl.playbackSpeed:
                if newSpeed == 0:
                    if player.gunRotator is not None:
                        self.__gunWasLockedBeforePause = player.gunRotator._VehicleGunRotator__isLocked
                        player.gunRotator.lock(True)
                    self.__showInfoMessage('replayPaused')
                    isPaused = True
                else:
                    if player.gunRotator is not None:
                        player.gunRotator.lock(self.__gunWasLockedBeforePause)
                    newSpeedStr = self.__playbackSpeedModifiersStr[self.__playbackSpeedIdx]
                    self.__showInfoMessage('replaySpeedChange', {'speed': newSpeedStr})
                    isPaused = False
                self.__replayCtrl.playbackSpeed = newSpeed
                g_replayEvents.onPause(isPaused)
            return

    def getPlaybackSpeedIdx(self):
        ret = self.__playbackSpeedModifiers.index(self.__replayCtrl.playbackSpeed)
        return self.__playbackSpeedModifiers.index(1.0) if ret == -1 else ret

    def setControlMode(self, value):
        self.__replayCtrl.controlMode = value

    def getControlMode(self):
        return self.__replayCtrl.controlMode

    def onClientReady(self):
        if not (self.isPlaying or self.isRecording):
            return
        elif self.isRecording and BigWorld.player().arena.guiType == constants.ARENA_GUI_TYPE.TUTORIAL:
            self.stop(None, True)
            return
        else:
            self.__replayCtrl.playerVehicleID = BigWorld.player().playerVehicleID
            self.__replayCtrl.onClientReady()
            if self.isPlaying:
                if not BigWorld.IS_CONSUMER_CLIENT_BUILD:
                    self.__logSVNInfo()
                AreaDestructibles.g_destructiblesManager.onAfterReplayTimeWarp()
                if isPlayerAvatar():
                    BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
                    BigWorld.player().onObserverVehicleChanged += self.__onObserverVehicleChanged
                    if isServerSideReplay():
                        BigWorld.player().startServerSideReplay()
                if not self.isServerSideReplay:
                    self.appLoader.attachCursor(settings.APP_NAME_SPACE.SF_BATTLE, flags=GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED)
            if self.isRecording:
                player = BigWorld.player()
                arena = player.arena
                arenaName = arena.arenaType.geometry
                i = arenaName.find('/')
                if i != -1:
                    arenaName = arenaName[i + 1:]
                now = datetime.datetime.now()
                now = '%02d.%02d.%04d %02d:%02d:%02d' % (now.day,
                 now.month,
                 now.year,
                 now.hour,
                 now.minute,
                 now.second)
                vehicleName = BigWorld.entities[player.playerVehicleID].typeDescriptor.name
                vehicleName = vehicleName.replace(':', '-')
                vehicles = self.__getArenaVehiclesInfo()
                gameplayID = player.arenaTypeID >> 16
                clientVersionFromXml = getFullClientVersion()
                clientVersionFromExe = BigWorld.wg_getProductVersion()
                arenaInfo = {'dateTime': now,
                 'playerName': player.name,
                 'playerID': self.__playerDatabaseID,
                 'playerVehicle': vehicleName,
                 'mapName': arenaName,
                 'mapDisplayName': arena.arenaType.name,
                 'gameplayID': ArenaType.getGameplayName(gameplayID) or gameplayID,
                 'vehicles': vehicles,
                 'battleType': arena.bonusType,
                 'clientVersionFromExe': clientVersionFromExe,
                 'clientVersionFromXml': clientVersionFromXml,
                 'serverName': self.connectionMgr.serverUserName,
                 'regionCode': constants.AUTH_REALM,
                 'serverSettings': self.__serverSettings,
                 'hasMods': self.__replayCtrl.hasMods}
                if not BigWorld.IS_CONSUMER_CLIENT_BUILD:
                    arenaInfo['branchURL'], arenaInfo['lastChangedRevision'] = self.__getBranchAndRevision()
                if BigWorld.player().arena.guiType == constants.ARENA_GUI_TYPE.BOOTCAMP:
                    from bootcamp.Bootcamp import g_bootcamp
                    arenaInfo['lessonId'] = g_bootcamp.getLessonNum()
                    arenaInfo['bootcampCtx'] = g_bootcamp.serializeContext()
                self.__replayCtrl.recMapName = arenaName
                self.__replayCtrl.recPlayerVehicleName = vehicleName
                self.__replayCtrl.setArenaInfoStr(json.dumps(_JSON_Encode(arenaInfo)))
            else:
                self.__showInfoMessages()
                if self.replayTimeout > 0:
                    LOG_DEBUG('replayTimeout set for %.2f' % float(self.replayTimeout))
                    BigWorld.callback(float(self.replayTimeout), BigWorld.quit)
            return

    @property
    def isNormalSpeed(self):
        return self.playbackSpeed == 1.0

    def __getBranchAndRevision(self):
        from wot_svn import svn
        svnInstance = svn()
        if not svnInstance.enabled():
            return ('undefined', 'undefined')
        else:
            info = svnInstance.getInfo()
            if info is None:
                return ('undefined', 'undefined')
            rootPath = info.workingCopyRootAbsPath
            info = svnInstance.getInfo(rootPath)
            return ('undefined', 'undefined') if info is None else (info.branchURL, info.lastChangedRevision)

    def __logSVNInfo(self):
        if self.isServerSideReplay:
            return
        else:
            currentBranch, currentRevision = self.__getBranchAndRevision()
            replayBranch = self.arenaInfo.get('branchURL')
            if replayBranch is None:
                replayBranch = 'undefined'
            replayRevision = self.arenaInfo.get('lastChangedRevision')
            if replayRevision is None:
                replayRevision = 'undefined'
            _logger.info('Current branch: ' + currentBranch)
            _logger.info('Current revision: ' + str(currentRevision))
            _logger.info('Replay branch: ' + replayBranch)
            _logger.info('Replay revision: ' + str(replayRevision))
            return

    def __showInfoMessages(self):
        self.__showInfoMessage('replayControlsHelp1')
        self.__showInfoMessage('replayControlsHelp2')
        self.__showInfoMessage('replayControlsHelp3')

    def __getArenaVehiclesInfo(self):
        vehicles = {}
        for k, v in BigWorld.player().arena.vehicles.iteritems():
            vehicle = copy.copy(v)
            vehicle['vehicleType'] = v['vehicleType'].name if v['vehicleType'] is not None else ''
            del vehicle['accountDBID']
            del vehicle['prebattleID']
            del vehicle['clanDBID']
            del vehicle['isPrebattleCreator']
            del vehicle['isAvatarReady']
            del vehicle['outfitCD']
            vehicles[k] = vehicle

        return vehicles

    def loadServerSettings(self):
        if self.isPlaying:
            if not self.isServerSideReplay:
                self.__serverSettings = dict()
                try:
                    self.__serverSettings = self.arenaInfo.get('serverSettings')
                except Exception:
                    LOG_WARNING('There is problem while unpacking server settings from replay')
                    if constants.IS_DEVELOPMENT:
                        LOG_CURRENT_EXCEPTION()

            self.lobbyContext.setServerSettings(self.__serverSettings)

    def disableTimeWarp(self):
        self.__enableTimeWarp = False

    def enableTimeWarp(self):
        if self.isPlaying:
            self.__enableTimeWarp = True

    def onBattleLoadingFinished(self):
        self.enableTimeWarp()
        if self.isPlaying:
            self.__replayCtrl.onBattleLoadingFinished()

    def onReplayFinished(self):
        if not self.scriptModalWindowsEnabled:
            self.stop()
            return
        if self.__isPlayingPlayList:
            self.stop()
            BigWorld.callback(1.0, self.play)
            return
        self.__isMenuShowed = False
        self.gameplay.postStateEvent(ReplayEventID.REPLAY_FINISHED)
        self.__isFinished = True
        self.setPlaybackSpeedIdx(0)

    def onControlModeChanged(self, forceControlMode=None):
        player = BigWorld.player()
        if not self.isPlaying or not isPlayerAvatar():
            return
        else:
            entity = BigWorld.entities.get(self.playerVehicleID)
            if (entity is None or not entity.isStarted) and forceControlMode is None:
                controlMode = self.getControlMode()
                if controlMode == CTRL_MODE_NAME.SNIPER:
                    return
            if not self.isControllingCamera and forceControlMode is None:
                return
            controlMode = self.getControlMode() if forceControlMode is None else forceControlMode
            if forceControlMode is None and not self.isControllingCamera and controlMode in _IGNORED_SWITCHING_CTRL_MODES:
                return
            if self.__equipmentId is None and controlMode == CTRL_MODE_NAME.MAP_CASE_ARCADE:
                return
            preferredPos = self.getGunRotatorTargetPoint()
            if controlMode == CTRL_MODE_NAME.MAP_CASE:
                _, preferredPos, _ = self.getGunMarkerParams(preferredPos, Math.Vector3(0.0, 0.0, 1.0))
            player.inputHandler.onControlModeChanged(controlMode, camMatrix=BigWorld.camera().matrix, preferredPos=preferredPos, saveZoom=False, saveDist=False, equipmentID=self.__equipmentId, curVehicleID=self.__replayCtrl.playerVehicleID)
            return

    def onPlayerVehicleIDChanged(self):
        player = BigWorld.player()
        if self.isPlaying and hasattr(player, 'positionControl'):
            player.inputHandler.ctrl.selectPlayer(self.__replayCtrl.playerVehicleID)

    def __onAvatarObserverVehicleChanged(self, vehID):
        if self.isServerSideReplay:
            self.__isVehicleChanging = True
            if vehID != BigWorld.player().playerVehicleID:
                self.__lastObservedVehicleID = vehID
            self.__aoi.changeVehicle(vehID)
        self.__isVehicleChanging = False

    def getLastObservedVehicleID(self):
        return self.__lastObservedVehicleID

    def isVehicleChanging(self):
        return self.__isVehicleChanging

    def isAllyToObservedVehicle(self, vehID):
        observedVehicleID = self.__aoi.currentVehicleID
        if not observedVehicleID:
            return False
        arenaVehicles = BigWorld.player().arena.vehicles
        currTeam = arenaVehicles[observedVehicleID]['team']
        vehTeam = arenaVehicles[vehID]['team']
        return currTeam == vehTeam

    def onPostTickCallback(self, currentTick, totalTicks):
        self.__aoi.flush(self.getControlMode())

    def setAmmoSetting(self, idx):
        if not isPlayerAvatar():
            return
        if self.isRecording:
            self.__replayCtrl.onAmmoButtonPressed(idx)

    def __onAmmoButtonPressed(self, idx):
        self.onAmmoSettingChanged(idx)

    def onSniperModeChanged(self, enable):
        if self.isPlaying:
            if enable:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.SNIPER_MODE)
            else:
                TriggersManager.g_manager.deactivateTrigger(TriggersManager.TRIGGER_TYPE.SNIPER_MODE)
        elif self.isRecording:
            self.__replayCtrl.onSniperMode(enable)

    def onLockTarget(self, lock, playVoiceNotifications):
        if not isPlayerAvatar():
            return
        if self.isPlaying:
            BigWorld.player().onLockTarget(lock, playVoiceNotifications)
        elif self.isRecording:
            self.__replayCtrl.onLockTarget(lock, playVoiceNotifications)

    def onBattleChatMessage(self, messageText, isCurrentPlayer):
        from messenger import MessengerEntry
        if self.isRecording:
            self.__replayCtrl.onBattleChatMessage(messageText, isCurrentPlayer)
        elif self.isPlaying and not self.isTimeWarpInProgress:
            if self.__isChatPlaybackEnabled:
                MessengerEntry.g_instance.gui.addClientMessage(messageText, isCurrentPlayer)

    def setFpsPingLag(self, fps, ping, isLaggingNow):
        if self.isPlaying:
            return
        self.__replayCtrl.fps = int(fps)
        self.__replayCtrl.ping = int(ping)
        self.__replayCtrl.isLaggingNow = isLaggingNow

    def onClientVersionDiffers(self):
        if not self.scriptModalWindowsEnabled:
            self.acceptVersionDiffering()
            return
        self.gameplay.postStateEvent(ReplayEventID.REPLAY_VERSION_CONFIRMATION)

    def acceptVersionDiffering(self):
        self.__replayCtrl.confirmDlgAccepted()

    def registerWotReplayFileExtension(self):
        self.__replayCtrl.registerWotReplayFileExtension()

    def enableAutoRecordingBattles(self, enable, delete=False):
        if self.__isAutoRecordingEnabled == enable:
            return
        else:
            self.__isAutoRecordingEnabled = enable
            if enable:
                if enable == 1:
                    self.setResultingFileName(FIXED_REPLAY_FILENAME, True)
                elif enable == 2:
                    self.setResultingFileName(None)
                g_playerEvents.onAccountBecomePlayer += self.__startAutoRecord
                self.__startAutoRecord()
            else:
                g_playerEvents.onAccountBecomePlayer -= self.__startAutoRecord
                if self.isRecording:
                    self.stop(delete=delete)
            return

    def setResultingFileName(self, fileName, overwriteExisting=False):
        self.__replayCtrl.setResultingFileName(fileName or '', overwriteExisting)

    def timeWarp(self, time):
        self.__timeWarp(time)

    def __showInfoMessage(self, msg, args=None):
        if not self.isTimeWarpInProgress:
            g_replayEvents.onWatcherNotify(msg, args)

    def __startAutoRecord(self):
        if not self.__isAutoRecordingEnabled:
            return
        if self.isPlaying:
            return
        if self.isRecording or not isPlayerAccount():
            return
        self.record()

    def __goToNextReplay(self):
        self.gameplay.postStateEvent(ReplayEventID.REPLAY_NEXT)
        self.connectionMgr.onDisconnected -= self.__goToNextReplay

    def setArenaStatisticsStr(self, arenaUniqueStr):
        self.__replayCtrl.setArenaStatisticsStr(arenaUniqueStr)

    def __onBattleResultsReceived(self, isPlayerVehicle, results):
        if isPlayerVehicle:
            modifiedResults = copy.deepcopy(results)
            allPlayersVehicles = modifiedResults.get('vehicles', None)
            if allPlayersVehicles is not None:
                for playerVehicles in allPlayersVehicles.itervalues():
                    for vehicle in playerVehicles:
                        if vehicle is not None:
                            vehicle['damageEventList'] = None

            personals = modifiedResults.get('personal', None)
            if personals is not None:
                for personal in personals.itervalues():
                    for field in ('damageEventList', 'xpReplay', 'creditsReplay', 'tmenXPReplay', 'flXPReplay', 'goldReplay', 'crystalReplay', 'eventCoinReplay', 'bpcoinReplay', 'freeXPReplay', 'avatarDamageEventList'):
                        personal[field] = None

                    for currency in personal.get('currencies', {}).itervalues():
                        currency['replay'] = None

            common = modifiedResults.get('common', None)
            if common is not None:
                common['accountCompDescr'] = None
            modifiedResults = (modifiedResults, self.__getArenaVehiclesInfo(), BigWorld.player().arena.statistics)
            try:
                self.__replayCtrl.setArenaStatisticsStr(json.dumps(_JSON_Encode(modifiedResults)))
            except Exception:
                LOG_ERROR('__onBattleResultsReceived::setArenaStatisticsStr _JSON_Encode error!')

        return

    def __onAccountBecomePlayer(self):
        self.enableAutoRecordingBattles(True)
        if not isPlayerAccount():
            return
        else:
            player = BigWorld.player()
            serverSettings = player.serverSettings
            self.__serverSettings['roaming'] = serverSettings['roaming']
            self.__serverSettings['isPotapovQuestEnabled'] = serverSettings.get('isPotapovQuestEnabled', False)
            if 'spgRedesignFeatures' in serverSettings:
                self.__serverSettings['spgRedesignFeatures'] = serverSettings['spgRedesignFeatures']
            self.__serverSettings['ranked_config'] = serverSettings['ranked_config']
            self.__serverSettings['battle_royale_config'] = serverSettings['battle_royale_config']
            self.__serverSettings['epic_config'] = serverSettings['epic_config']
            self.__serverSettings[SERVER_SETTINGS_KEY] = serverSettings[SERVER_SETTINGS_KEY]
            if player.databaseID is None:
                BigWorld.callback(0.1, self.__onAccountBecomePlayer)
            else:
                self.__playerDatabaseID = player.databaseID
            return

    def __onSettingsChanging(self, *_):
        newSpeed = self.__playbackSpeedModifiers[self.__playbackSpeedIdx]
        newQuiet = newSpeed == 0 or newSpeed > 4.0
        g_replayEvents.onMuteSound(newQuiet)

    def __timeWarp(self, time):
        if not self.isPlaying or not self.__enableTimeWarp:
            return
        g_replayEvents.onTimeWarpStart()
        if self.__isFinished:
            self.setPlaybackSpeedIdx(self.__savedPlaybackSpeedIdx)
        self.__isFinished = False
        self.__warpTime = time
        self.__rewind = time < self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_CURRENT_TIME)
        AreaDestructibles.g_destructiblesManager.onBeforeReplayTimeWarp(self.__rewind)
        self.__updateGunOnTimeWarp = True
        EffectsList.EffectsListPlayer.clear()
        if self.__rewind:
            playerControlModeName = BigWorld.player().inputHandler.ctrlModeName
            self.__wasVideoBeforeRewind = playerControlModeName == CTRL_MODE_NAME.VIDEO
            self.__videoCameraMatrix.set(BigWorld.camera().matrix)
            BigWorld.PyGroundEffectManager().stopAll()
            BigWorld.wg_clearDecals()
        g_replayEvents.onMuteSound(True)
        self.__enableInGameEffects(False)
        if self.__rewind:
            self.gameplay.postStateEvent(ReplayEventID.REPLAY_REWIND)
        if not self.__replayCtrl.beginTimeWarp(time):
            self.__cleanupAfterTimeWarp()
            return
        self.__rewind = False

    def __enableInGameEffects(self, enable):
        AreaDestructibles.g_destructiblesManager.forceNoAnimation = not enable

    def getSetting(self, key, default=None):
        return pickle.loads(base64.b64decode(self.__settings.readString(key))) if self.__settings.has_key(key) else default

    def setSetting(self, key, value):
        self.__settings.write(key, base64.b64encode(pickle.dumps(value)))
        diff = {key: value}
        self.settingsCore.onSettingsChanged(diff)

    def isFinished(self):
        return self.__isFinished if self.isPlaying or g_replayCtrl.isTimeWarpInProgress else False

    def isFinishedNoPlayCheck(self):
        return self.__isFinished

    def isNeedToPlay(self, entity_id):
        return self.__replayCtrl.isEffectNeedToPlay(entity_id)

    def setUseServerAim(self, server_aim):
        return self.__replayCtrl.onServerAim(server_aim)

    def printAIMType(self):
        if self.isServerAim:
            print 'SERVER_AIM_ACTIVE'
        else:
            print 'CLIENT_AIM_ACTIVE'

    def setEquipmentID(self, value):
        self.__replayCtrl.onSetEquipmentID(value)

    def onSetEquipmentId(self, equipmentId):
        if equipmentId != -1:
            self.__equipmentId = equipmentId
            BigWorld.player().inputHandler.showGunMarker(False)
        else:
            BigWorld.player().inputHandler.showGunMarker(True)
            self.__equipmentId = None
        return

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == self.playerVehicleID:
            if self.__replayCtrl.isControllingCamera:
                self.onControlModeChanged(self.getControlMode())

    def __onObserverVehicleChanged(self):
        if self.__replayCtrl.isControllingCamera and not self.__isAllowedSavedCamera():
            self.__replayCtrl.isControllingCamera = False

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if self.isRecording:
            if self.__arenaPeriod == period and period == ARENA_PERIOD.BATTLE and self.__previousPeriod != period:
                self.__perviousPeriod = period
                self.resetArenaPeriod()
        self.__arenaPeriod = period
        self.__replayCtrl.arenaPeriod = period
        self.__replayCtrl.arenaLength = periodLength

    def __onBootcampAccountMigrationComplete(self):
        if self.isRecording:
            self.stop(delete=True)

    def setDataCallback(self, name, callback):
        eventHandler = self.__replayCtrl.getCallbackHandler(name)
        if eventHandler is None:
            eventHandler = Event.Event()
            self.__replayCtrl.setDataCallback(name, eventHandler)
        eventHandler += callback
        return

    def serializeCallbackData(self, cbkName, data):
        self.__replayCtrl.serializeCallbackData(cbkName, data)

    def delDataCallback(self, name, callback):
        eventHandler = self.__replayCtrl.getCallbackHandler(name)
        if eventHandler is not None:
            eventHandler -= callback
        return

    def __onTimeWarpFinished(self):
        self.__cleanupAfterTimeWarp()

    def __cleanupAfterTimeWarp(self):
        self.__warpTime = -1.0
        self.__enableInGameEffects(0.0 < self.__playbackSpeedModifiers[self.__playbackSpeedIdx] < 8.0)
        mute = not 0.0 < self.__playbackSpeedModifiers[self.__playbackSpeedIdx] < 8.0
        g_replayEvents.onMuteSound(mute)
        if self.__wasVideoBeforeRewind:
            BigWorld.player().inputHandler.onControlModeChanged('video', prevModeName='arcade', camMatrix=self.__videoCameraMatrix)
            self.__wasVideoBeforeRewind = False
        g_replayEvents.onTimeWarpFinish()

    def onRespawnMode(self, enabled):
        self.__replayCtrl.onRespawnMode(enabled)

    def __isAllowedSavedCamera(self):
        return BigWorld.player().arenaBonusType not in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE if BigWorld.player().isObserver() else True


def _JSON_Encode(obj):
    if isinstance(obj, dict):
        newDict = {}
        for key, value in obj.iteritems():
            if isinstance(key, tuple):
                newDict[str(key)] = _JSON_Encode(value)
            newDict[key] = _JSON_Encode(value)

        return newDict
    if isinstance(obj, (list,
     tuple,
     set,
     frozenset)):
        newList = []
        for value in obj:
            newList.append(_JSON_Encode(value))

        return newList
    return obj


def isPlaying():
    return g_replayCtrl.isPlaying or g_replayCtrl.isTimeWarpInProgress if g_replayCtrl is not None else False


def isServerSideReplay():
    return g_replayCtrl.isServerSideReplay if g_replayCtrl is not None else False


def isLoading():
    return g_replayCtrl is not None and g_replayCtrl.isLoading


def isFinished():
    return g_replayCtrl is not None and g_replayCtrl.isFinishedNoPlayCheck()


def getSpaceID():
    return g_replayCtrl.getSpaceID() if g_replayCtrl is not None else BigWorld.player().spaceID


def getDemandedToWatchFileName():
    return g_replayCtrl.getDemandedToWatchFileName() if g_replayCtrl is not None else None


def customCallback(result, filename):
    LOG_DEBUG('Replay Downloaded Custom Callback : result = %d, filename = %s' % (result, filename))
