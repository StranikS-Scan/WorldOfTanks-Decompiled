# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleReplay.py
import base64
import os
import datetime
import json
import copy
import cPickle as pickle
import logging
import zlib
from collections import defaultdict
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
from AvatarInfo import AvatarInfo
from aih_constants import CTRL_MODE_NAME
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui import GUI_CTRL_MODE_FLAG
from gui.shared.system_factory import registerReplayModeTag, collectReplayModeTag
from helpers import EffectsList, isPlayerAvatar, isPlayerAccount, getFullClientVersion
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from constants import ARENA_PERIOD, ARENA_BONUS_TYPE, ARENA_GUI_TYPE, INBATTLE_CONFIGS, NULL_ENTITY_ID
from helpers import dependency
from gui.app_loader import settings
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gameplay import IGameplayLogic, ReplayEventID
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
from helpers.styles_perf_toolset import g_reportGenerator
_logger = logging.getLogger(__name__)
g_replayCtrl = None
REPLAY_FILE_EXTENSION = '.wotreplay'
AUTO_RECORD_TEMP_FILENAME = 'temp'
FIXED_REPLAY_FILENAME = 'replay_last_battle'
REPLAY_TIME_MARK_CLIENT_READY = 2147483648L
REPLAY_TIME_MARK_REPLAY_FINISHED = 2147483649L
REPLAY_TIME_MARK_CURRENT_TIME = 2147483650L
FAST_FORWARD_STEP = 20.0
MIN_REPLAY_TIME = 1
_FORWARD_INPUT_CTRL_MODES = (CTRL_MODE_NAME.VIDEO,
 CTRL_MODE_NAME.DEBUG,
 CTRL_MODE_NAME.DEATH_FREE_CAM,
 CTRL_MODE_NAME.KILL_CAM)
_IGNORED_SWITCHING_CTRL_MODES = (CTRL_MODE_NAME.SNIPER,
 CTRL_MODE_NAME.ARCADE,
 CTRL_MODE_NAME.ARTY,
 CTRL_MODE_NAME.STRATEGIC,
 CTRL_MODE_NAME.DUAL_GUN,
 CTRL_MODE_NAME.MAP_CASE,
 CTRL_MODE_NAME.MAP_CASE_ARCADE,
 CTRL_MODE_NAME.MAP_CASE_EPIC,
 CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD,
 CTRL_MODE_NAME.TWIN_GUN)
registerReplayModeTag(ARENA_GUI_TYPE.COMP7, 'Onslaught')

class CallbackDataNames(object):
    APPLY_ZOOM = 'applyZoom'
    HINT_SHOW = 'hint_show'
    HINT_HIDE = 'hint_hide'
    HINT_COMPLETE = 'hint_complete'
    HINT_CLOSE = 'hint_close'
    HINT_ONHIDED = 'hint_onHided'
    BW_CHAT2_REPLAY_ACTION_RECEIVED_CALLBACK = 'bw_chat2.onActionReceived'
    CLIENT_VEHICLE_STATE_GROUP = 'client_vehicle_state_{}'
    DYN_SQUAD_SEND_ACTION_NAME = 'DynSquad.SendInvitationToSquad'
    DYN_SQUAD_ACCEPT_ACTION_NAME = 'DynSquad.AcceptInvitationToSquad'
    DYN_SQUAD_REJECT_ACTION_NAME = 'DynSquad.RejectInvitationToSquad'
    GUN_DAMAGE_SOUND = 'gunDamagedSound'
    SHOW_AUTO_AIM_MARKER = 'showAutoAimMarker'
    HIDE_AUTO_AIM_MARKER = 'hideAutoAimMarker'
    ON_TARGET_VEHICLE_CHANGED = 'onTargetVehicleChanged'
    MT_CONFIG_CALLBACK = 'mapsTrainingConfigurationCallback'
    SHOW_BATTLE_HINT = 'show_battle_hint'
    HIDE_BATTLE_HINT = 'hide_battle_hint'


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
        entity = BigWorld.entities.get(entityID)
        if entity:
            entityType = type(entity)
            if entityType is AvatarInfo:
                hasEnteredAoI = entity.avatarID == BigWorld.player().id
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
    __previousMode = CTRL_MODE_NAME.DEFAULT
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
    gameplay = dependency.descriptor(IGameplayLogic)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    appLoader = dependency.descriptor(IAppLoader)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_REPLAY_PREFERENCES):
            userPrefs.write(Settings.KEY_REPLAY_PREFERENCES, '')
        self.__settings = userPrefs[Settings.KEY_REPLAY_PREFERENCES]
        self.__fileName = None
        self.__replayCtrl = BigWorld.WGReplayController()
        self.__replayCtrl.replayFinishedCallback = self.onReplayFinished
        self.__replayCtrl.replayTerminatedCallback = self.onReplayTerminated
        self.__replayCtrl.replayMetaDataCallback = self.onReplayMetaData
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
        self.__replayCtrl.serverAimCallback = self.setUseServerAim
        self.__isAutoRecordingEnabled = False
        self.__quitAfterStop = False
        self.__isPlayingPlayList = False
        self.__playList = []
        self.__isFinished = False
        self.__isFinishAfterKillCamEnds = False
        self.__isMenuShowed = False
        self.__updateGunOnTimeWarp = False
        self.__lastObservedVehicleID = NULL_ENTITY_ID
        self.__aoi = SimulatedAoI()
        self.__isVehicleChanging = False
        self.__playerDatabaseID = 0
        self.__serverSettings = dict()
        if isPlayerAccount():
            self.__playerDatabaseID = BigWorld.player().databaseID
        self.__arenaStartTime = None
        self.__playbackSpeedModifiers = (0.0, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
        self.__playbackSpeedModifiersStr = ('0', '1/16', '1/8', '1/4', '1/2', '1', '2', '4', '8', '16')
        self.__playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
        self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
        self.__gunWasLockedBeforePause = False
        self.__ctrlModeBeforeRewind = None
        self.__cameraMatrixBeforeRewind = Math.Matrix()
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
        self.__wasKillCamActived = False
        self.enableAutoRecordingBattles(True)
        self.onCommandReceived = Event.Event()
        self.onAmmoSettingChanged = Event.Event()
        self.onServerAimChanged = Event.Event()
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
        return

    def subscribe(self):
        g_playerEvents.onBattleResultsReceived += self.__onBattleResultsReceived
        g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_playerEvents.onAvatarObserverVehicleChanged += self.__onAvatarObserverVehicleChanged
        self.settingsCore.onSettingsChanged += self.__onSettingsChanging

    def unsubscribe(self):
        g_playerEvents.onBattleResultsReceived -= self.__onBattleResultsReceived
        g_playerEvents.onAccountBecomePlayer -= self.__onAccountBecomePlayer
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onAvatarObserverVehicleChanged -= self.__onAvatarObserverVehicleChanged
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanging

    def destroy(self):
        self.stop(isDestroyed=True)
        self.onCommandReceived.clear()
        self.onCommandReceived = None
        self.onAmmoSettingChanged.clear()
        self.onAmmoSettingChanged = None
        self.onServerAimChanged.clear()
        self.onServerAimChanged = None
        self.enableAutoRecordingBattles(False)
        self.__replayCtrl.replayTerminatedCallback = None
        self.__replayCtrl.replayFinishedCallback = None
        self.__replayCtrl.replayMetaDataCallback = None
        self.__replayCtrl.controlModeChangedCallback = None
        self.__replayCtrl.clientVersionDiffersCallback = None
        self.__replayCtrl.playerVehicleIDChangedCallback = None
        self.__replayCtrl.battleChatMessageCallback = None
        self.__replayCtrl.ammoButtonPressedCallback = None
        self.__replayCtrl.lockTargetCallback = None
        self.__replayCtrl.equipmentIdCallback = None
        self.__replayCtrl.warpFinishedCallback = None
        self.__replayCtrl.serverAimCallback = None
        self.__replayCtrl = None
        self.__settings = None
        self.__cameraMatrixBeforeRewind = None
        self.__warpTime = -1.0
        self.__arenaPeriod = -1
        return

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
        try:
            if not os.path.isdir(self.__replayDir):
                os.makedirs(self.__replayDir)
        except Exception:
            LOG_ERROR('Failed to create directory for replay files')
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
        g_reportGenerator.startCollectingData()
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
            replayEndTime = self.__replayCtrl.getReplayEndTime()
            totalReplayTime = self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_REPLAY_FINISHED)
            replayStartTime = self.__replayCtrl.getReplayStartTime()
            replayStartTime = min(replayStartTime, replayEndTime - MIN_REPLAY_TIME, totalReplayTime - MIN_REPLAY_TIME)
            replayStartTime = max(replayStartTime, 0)
            self.__replayStartTime = replayStartTime
            self.__replayEndTime = replayEndTime
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
            g_reportGenerator.stopCollectingData()
            g_reportGenerator.generateReport()
            wasPlaying = self.isPlaying
            wasServerReplay = self.isServerSideReplay
            isOffline = self.__replayCtrl.isOfflinePlaybackMode
            self.__aoi.reset()
            self.__lastObservedVehicleID = NULL_ENTITY_ID
            self.__replayCtrl.stop(delete)
            self.__fileName = None
            self.__isVehicleChanging = False
            if wasPlaying:
                if isPlayerAvatar():
                    BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
                    BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
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

    def onReplayTerminated(self, reason):
        _logger.info('BattleReplay.onReplayTerminated: reason=%r', reason)
        g_replayEvents.onMuteSound(False)
        g_replayEvents.onReplayTerminated(reason)
        self.__isFinished = False
        if self.__originalPickleLoads is not None:
            pickle.loads = self.__originalPickleLoads
            self.__originalPickleLoads = None
        return

    def onReplayMetaData(self, metaData):
        if 'serverSettings' in metaData:
            self.__serverSettings = pickle.loads(zlib.decompress(base64.b64decode(metaData['serverSettings'])))

    def onEntityAoIChangedCallback(self, witnessID, entityID, hasEnteredAoI):
        _logger.debug('BattleReplay: onEntityAoIChangedCallback: witnessID=%s, entityID=%s, hasEnteredAoI=%s', witnessID, entityID, hasEnteredAoI)
        self.__aoi.handleAoIEvent(witnessID, entityID, hasEnteredAoI)

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
        controlMode = self.getControlMode()
        isKillCamActive = self.__isKillCamActive()
        if key == Keys.KEY_LEFTMOUSE or cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key):
            if isDown and not isCursorVisible:
                if self.isServerSideReplay:
                    if self.__arenaPeriod == ARENA_PERIOD.BATTLE:
                        player.switchObserverFPV()
                    return True
                if self.isControllingCamera:
                    self.appLoader.detachCursor(settings.APP_NAME_SPACE.SF_BATTLE)
                    if controlMode in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES:
                        self.onControlModeChanged(controlMode)
                    else:
                        self.onControlModeChanged('arcade')
                    self.__replayCtrl.isControllingCamera = False
                    self.__showInfoMessage('replayFreeCameraActivated')
                else:
                    if not self.__isAllowedSavedCamera():
                        return False
                    self.__gotoBoundMode()
                return True
        if cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
            if self.isControllingCamera:
                return True
        if key == Keys.KEY_SPACE and isDown and not self.__isFinished and not isKillCamActive:
            if self.__playbackSpeedIdx > 0:
                self.setPlaybackSpeedIdx(0)
            else:
                self.resetPlaybackSpeedIdx()
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
        if key == Keys.KEY_LEFTARROW and isDown:
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

    def setGunRotatorTargetPoint(self, value):
        self.__replayCtrl.gunRotatorTargetPoint = value

    def getGunRotatorTargetPoint(self):
        return self.__replayCtrl.gunRotatorTargetPoint

    def setConsumablesPosition(self, pos, direction=Math.Vector3(1, 1, 1)):
        self.__replayCtrl.gunMarkerPosition = pos
        self.__replayCtrl.gunMarkerDirection = direction

    def setGunMarkerParams(self, diameter, dualAccDiameter, pos, direction):
        controlMode = self.getControlMode()
        if controlMode != 'mapcase':
            self.__replayCtrl.gunMarkerDiameter = diameter
            self.__replayCtrl.dualAccDiameter = dualAccDiameter
            self.__replayCtrl.gunMarkerDirection = direction
            self.__replayCtrl.gunMarkerPosition = pos

    def getGunMarkerParams(self, defaultPos, defaultDir):
        diameter = self.__replayCtrl.gunMarkerDiameter
        dualAccDiameter = self.__replayCtrl.dualAccDiameter
        direction = self.__replayCtrl.gunMarkerDirection
        pos = self.__replayCtrl.gunMarkerPosition
        if direction == Math.Vector3(0, 0, 0):
            pos = defaultPos
            direction = defaultDir
        return (diameter,
         dualAccDiameter,
         pos,
         direction)

    def getGunMarkerPos(self):
        return self.__replayCtrl.gunMarkerPosition

    def getEquipmentId(self):
        return self.__equipmentId

    def useSyncroniusResourceLoading(self, use):
        self.__replayCtrl.useSyncroniusResourceLoading = use

    def setArcadeGunMarkerSize(self, size):
        self.__replayCtrl.setArcadeGunMarkerSize(size)

    def getArcadeGunMarkerSize(self):
        return self.__replayCtrl.getArcadeGunMarkerSize()

    def setDualAccMarkerSize(self, size):
        self.__replayCtrl.setDualAccMarkerSize(size)

    def getDualAccMarkerSize(self):
        return self.__replayCtrl.getDualAccMarkerSize()

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

    def setGunReloadTime(self, startTime, duration, clipTime=None):
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

    def resetPlaybackSpeedIdx(self, allowResetToZero=False):
        if self.__savedPlaybackSpeedIdx != 0 or allowResetToZero:
            playbackSpeedIdx = self.__savedPlaybackSpeedIdx
        else:
            playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
        self.setPlaybackSpeedIdx(playbackSpeedIdx)

    def getPlaybackSpeedIdx(self):
        ret = self.__playbackSpeedModifiers.index(self.__replayCtrl.playbackSpeed)
        return self.__playbackSpeedModifiers.index(1.0) if ret == -1 else ret

    def setControlMode(self, value):
        self.__replayCtrl.controlMode = value

    def getControlMode(self):
        if self.__wasKillCamActived:
            return CTRL_MODE_NAME.KILL_CAM
        recordedControlMode = self.__replayCtrl.controlMode
        return CTRL_MODE_NAME.POSTMORTEM if recordedControlMode == CTRL_MODE_NAME.KILL_CAM else recordedControlMode

    def getRecordedControlMode(self):
        return self.__replayCtrl.controlMode

    def onClientReady(self):
        player = BigWorld.player()
        if not (self.isPlaying or self.isRecording):
            return
        self.__replayCtrl.playerVehicleID = player.playerVehicleID
        self.__replayCtrl.onClientReady()
        if self.isPlaying:
            if not BigWorld.IS_CONSUMER_CLIENT_BUILD:
                self.__logSVNInfo()
            AreaDestructibles.g_destructiblesManager.onAfterReplayTimeWarp()
            if isPlayerAvatar():
                player.onVehicleEnterWorld += self.__onVehicleEnterWorld
                player.inputHandler.onCameraChanged += self.__onCameraChanged
                player.onObserverVehicleChanged += self.__onObserverVehicleChanged
                if isServerSideReplay():
                    otherVehicles = [ x for x in BigWorld.entities.valuesOfType('Vehicle') if x.id != player.playerVehicleID ]
                    self.bindToVehicleForServerSideReplay(player.playerVehicleID)
                    player.updateVehicleHealth(player.playerVehicleID, 0, 0, 1, 0)
                    if otherVehicles:
                        if self.__lastObservedVehicleID not in BigWorld.entities.keys():
                            self.bindToVehicleForServerSideReplay(otherVehicles[-1].id)
                        else:
                            self.bindToVehicleForServerSideReplay(self.__lastObservedVehicleID)
            if not self.isServerSideReplay:
                self.appLoader.attachCursor(settings.APP_NAME_SPACE.SF_BATTLE, flags=GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED)
        if self.isRecording:
            now = datetime.datetime.now()
            self.__arenaStartTime = '%02d.%02d.%04d %02d:%02d:%02d' % (now.day,
             now.month,
             now.year,
             now.hour,
             now.minute,
             now.second)
            self.updateArenaInfo()
        else:
            self.__showInfoMessages()
            if self.replayTimeout > 0:
                LOG_DEBUG('replayTimeout set for %.2f' % float(self.replayTimeout))
                BigWorld.callback(float(self.replayTimeout), BigWorld.quit)

    def updateArenaInfo(self, vehicleName=None):
        if not self.isRecording:
            return
        player = BigWorld.player()
        arena = player.arena
        vehicleName = vehicleName or BigWorld.entities[player.playerVehicleID].typeDescriptor.name
        vehicleName = vehicleName.replace(':', '-')
        arenaName = arena.arenaType.geometry
        i = arenaName.find('/')
        if i != -1:
            arenaName = arenaName[i + 1:]
        gameplayID = player.arenaTypeID >> 16
        arenaInfo = {'dateTime': self.__arenaStartTime,
         'playerName': player.name,
         'playerID': self.__playerDatabaseID,
         'playerVehicle': vehicleName,
         'mapName': arenaName,
         'mapDisplayName': arena.arenaType.name,
         'gameplayID': ArenaType.getGameplayName(gameplayID) or gameplayID,
         'vehicles': self.__getArenaVehiclesInfo(),
         'battleType': arena.bonusType,
         'clientVersionFromExe': BigWorld.wg_getProductVersion(),
         'clientVersionFromXml': getFullClientVersion(),
         'serverName': self.connectionMgr.serverUserName,
         'regionCode': constants.AUTH_REALM,
         'serverSettings': self.__serverSettings,
         'hasMods': self.__replayCtrl.hasMods}
        self.__replayCtrl.setArenaInfoStr(json.dumps(_JSON_Encode(arenaInfo)))
        self.__replayCtrl.recPlayerVehicleName = vehicleName
        self.__replayCtrl.recMapName = arenaName
        self.__replayCtrl.recBattleModeTag = collectReplayModeTag(arena.guiType)

    def bindToVehicleForServerSideReplay(self, vehicleID):
        LOG_DEBUG('Avatar.bindToVehicleForServerSideReplay: vehicleID=%s' % vehicleID)
        player = BigWorld.player()
        player.isObserverFPV, isObserverFPV = False, player.isObserverFPV
        if player.isObserverFPV != isObserverFPV:
            player.set_isObserverFPV(isObserverFPV)
        BWReplay.wg_withholdEntity(vehicleID, False)
        BWReplay.wg_injectNonVolatileUpdate(player.id, vehicleID, player.position, (player.yaw, player.pitch, player.roll))
        player.onSwitchViewpoint(vehicleID, Math.Vector3(0, 0, 0))

    @property
    def isNormalSpeed(self):
        return self.playbackSpeed == 1.0

    def loadServerSettings(self):
        if self.isPlaying:
            if not self.isServerSideReplay:
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
        if self.__isKillCamActive():
            self.__isFinishAfterKillCamEnds = True
            return
        replayTimes = self.__replayCtrl.getReplayTimes() - 1
        if replayTimes > 0:
            self.__replayCtrl.setReplayTimes(replayTimes)
            self.timeWarp(self.__replayStartTime - self.currentTime)
            return
        self.__replayCtrl.processFinish()
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
        controlMode = self.getControlMode()
        recordedControlMode = self.getRecordedControlMode() if forceControlMode is None else forceControlMode
        previousMode = self.__previousMode
        self.__previousMode = recordedControlMode
        if controlMode == CTRL_MODE_NAME.KILL_CAM:
            return
        elif recordedControlMode == CTRL_MODE_NAME.KILL_CAM:
            if self.isControllingCamera:
                self.__replayCtrl.isControllingCamera = False
            return
        else:
            if previousMode == CTRL_MODE_NAME.KILL_CAM:
                self.__replayCtrl.isControllingCamera = True
            if not self.isPlaying or not isPlayerAvatar():
                return
            entity = BigWorld.entities.get(self.playerVehicleID)
            if (entity is None or not entity.isStarted) and forceControlMode is None:
                if controlMode == CTRL_MODE_NAME.SNIPER:
                    return
            if not self.isControllingCamera and forceControlMode is None:
                if controlMode != CTRL_MODE_NAME.DEATH_FREE_CAM:
                    return
            if forceControlMode is None and not self.isControllingCamera and recordedControlMode in _IGNORED_SWITCHING_CTRL_MODES or recordedControlMode == CTRL_MODE_NAME.MAP_CASE_EPIC:
                return
            elif self.__equipmentId is None and recordedControlMode in (CTRL_MODE_NAME.MAP_CASE_ARCADE, CTRL_MODE_NAME.MAP_CASE_ARCADE_EPIC_MINEFIELD):
                return
            preferredPos = self.getGunRotatorTargetPoint()
            if recordedControlMode == CTRL_MODE_NAME.MAP_CASE:
                _, _, preferredPos, _ = self.getGunMarkerParams(preferredPos, Math.Vector3(0.0, 0.0, 1.0))
            player.inputHandler.onControlModeChanged(recordedControlMode, camMatrix=BigWorld.camera().matrix, preferredPos=preferredPos, saveZoom=False, saveDist=False, equipmentID=self.__equipmentId, curVehicleID=self.__replayCtrl.playerVehicleID)
            return

    def onPlayerVehicleIDChanged(self):
        player = BigWorld.player()
        if self.isPlaying and hasattr(player, 'positionControl') and player.inputHandler.ctrl is not None:
            player.inputHandler.ctrl.selectPlayer(self.__replayCtrl.playerVehicleID)
        return

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

    def onPostTickCallback(self):
        self.__aoi.flush(self.getRecordedControlMode())
        currentTime = self.currentTime
        if currentTime < self.__replayStartTime:
            self.timeWarp(self.__replayStartTime - currentTime)
        elif currentTime > self.__replayEndTime:
            self.onReplayFinished()

    def setAmmoSetting(self, idx):
        if not isPlayerAvatar():
            return
        if self.isRecording:
            self.__replayCtrl.onAmmoButtonPressed(idx)

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

    def setArenaStatisticsStr(self, arenaUniqueStr):
        self.__replayCtrl.setArenaStatisticsStr(arenaUniqueStr)

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

    def onRespawnMode(self, enabled):
        self.__replayCtrl.onRespawnMode(enabled)

    def stopCameraControl(self):
        self.__gotoUnboundMode()

    def __gotoUnboundMode(self):
        self.appLoader.detachCursor(settings.APP_NAME_SPACE.SF_BATTLE)
        controlMode = self.getRecordedControlMode()
        isDeathMode = controlMode in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES
        if not isDeathMode and not self.__isKillCamActive():
            self.onControlModeChanged('arcade')
        self.__replayCtrl.isControllingCamera = False
        self.onControlModeChanged(controlMode)
        self.__showInfoMessage('replayFreeCameraActivated')

    def __gotoBoundMode(self):
        self.__replayCtrl.isControllingCamera = True
        self.onControlModeChanged()
        self.__showInfoMessage('replaySavedCameraActivated')

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

    def __onAvatarObserverVehicleChanged(self, vehID):
        if self.isServerSideReplay:
            self.__isVehicleChanging = True
            if vehID != BigWorld.player().playerVehicleID:
                self.__lastObservedVehicleID = vehID
            self.__aoi.changeVehicle(vehID)
        self.__isVehicleChanging = False

    def __onAmmoButtonPressed(self, idx):
        self.onAmmoSettingChanged(idx)

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
                    for field in ('damageEventList', 'xpReplay', 'creditsReplay', 'tmenXPReplay', 'flXPReplay', 'goldReplay', 'crystalReplay', 'eventCoinReplay', 'bpcoinReplay', 'freeXPReplay', 'avatarDamageEventList', 'equipCoinReplay', 'battlePassPointsReplay'):
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
            for cfgName in INBATTLE_CONFIGS:
                self.__serverSettings[cfgName] = serverSettings[cfgName]

            if player.databaseID is None:
                BigWorld.callback(0.1, self.__onAccountBecomePlayer)
            else:
                self.__playerDatabaseID = player.databaseID
            return

    def __onAvatarBecomePlayer(self):
        if self.sessionProvider.arenaVisitor.getArenaBonusType() in constants.ARENA_BONUS_TYPE.REPLAY_DISABLE_RANGE:
            self.enableAutoRecordingBattles(False, True)

    def __onSettingsChanging(self, *_):
        if not self.isPlaying:
            return
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
            self.appLoader.detachCursor(settings.APP_NAME_SPACE.SF_BATTLE)
            playerControlModeName = BigWorld.player().inputHandler.ctrlModeName
            self.__ctrlModeBeforeRewind = playerControlModeName
            self.__cameraMatrixBeforeRewind.set(BigWorld.camera().matrix)
            BigWorld.PyGroundEffectManager().stopAll()
            BigWorld.wg_clearDecals()
            self.__wasKillCamActived = False
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
        if self.isPlaying:
            self.onServerAimChanged(server_aim)
        elif self.isRecording:
            self.__replayCtrl.onServerAim(server_aim)

    def printAIMType(self):
        if self.isServerAim:
            print 'SERVER_AIM_ACTIVE'
        else:
            print 'CLIENT_AIM_ACTIVE'

    def setEquipmentID(self, value):
        self.__replayCtrl.onSetEquipmentID(value)

    def onSetEquipmentId(self, equipmentId):
        inputHandler = BigWorld.player().inputHandler
        if equipmentId != -1:
            self.__equipmentId = equipmentId
            inputHandler.showClientGunMarkers(False)
            if self.getRecordedControlMode() == CTRL_MODE_NAME.MAP_CASE and inputHandler.ctrl.equipmentID != equipmentId:
                inputHandler.ctrl.activateEquipment(equipmentId)
        else:
            inputHandler.showClientGunMarkers(True)
            self.__equipmentId = None
        return

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == self.playerVehicleID:
            if self.__replayCtrl.isControllingCamera:
                self.onControlModeChanged(self.getRecordedControlMode())

    def __onObserverVehicleChanged(self):
        if self.__replayCtrl.isControllingCamera and not self.__isAllowedSavedCamera():
            self.__replayCtrl.isControllingCamera = False

    def __onCameraChanged(self, controlModeName, currentVehicleId=None):
        self.__wasKillCamActived = isKillCamActive = controlModeName == CTRL_MODE_NAME.KILL_CAM
        if self.__isFinishAfterKillCamEnds and not isKillCamActive:
            self.__isFinishAfterKillCamEnds = False
            self.onReplayFinished()
        if self.__previousMode == CTRL_MODE_NAME.KILL_CAM:
            self.onControlModeChanged()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if self.isRecording:
            if self.__arenaPeriod == period and period == ARENA_PERIOD.BATTLE and self.__previousPeriod != period:
                self.__perviousPeriod = period
                self.resetArenaPeriod()
        self.__arenaPeriod = period
        self.__replayCtrl.arenaPeriod = period
        self.__replayCtrl.arenaLength = periodLength

    def __onTimeWarpFinished(self):
        self.__cleanupAfterTimeWarp()

    def __cleanupAfterTimeWarp(self):
        self.__warpTime = -1.0
        self.__enableInGameEffects(0.0 < self.__playbackSpeedModifiers[self.__playbackSpeedIdx] < 8.0)
        mute = not 0.0 < self.__playbackSpeedModifiers[self.__playbackSpeedIdx] < 8.0
        g_replayEvents.onMuteSound(mute)
        if self.__ctrlModeBeforeRewind in (CTRL_MODE_NAME.VIDEO,):
            BigWorld.player().inputHandler.onControlModeChanged(self.__ctrlModeBeforeRewind, prevModeName=CTRL_MODE_NAME.ARCADE, camMatrix=self.__cameraMatrixBeforeRewind)
        self.__ctrlModeBeforeRewind = None
        g_replayEvents.onTimeWarpFinish()
        return

    def __isAllowedSavedCamera(self):
        if BigWorld.player().isObserver():
            return BigWorld.player().arenaBonusType not in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE
        return False if self.getRecordedControlMode() == CTRL_MODE_NAME.KILL_CAM else True

    def __isKillCamActive(self):
        return self.getControlMode() == CTRL_MODE_NAME.KILL_CAM


def isPlaying():
    return g_replayCtrl.isPlaying or g_replayCtrl.isTimeWarpInProgress if g_replayCtrl is not None else False


def isRecording():
    return g_replayCtrl is not None and g_replayCtrl.isRecording


def isServerSideReplay():
    return g_replayCtrl.isServerSideReplay if g_replayCtrl is not None else False


def isLoading():
    return g_replayCtrl is not None and g_replayCtrl.isLoading


def isFinished():
    return g_replayCtrl is not None and g_replayCtrl.isFinishedNoPlayCheck()


def getSpaceID():
    return g_replayCtrl.getSpaceID() if g_replayCtrl is not None else BigWorld.player().spaceID


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
