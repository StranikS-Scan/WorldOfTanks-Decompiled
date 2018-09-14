# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleReplay.py
import base64
import os
import datetime
import json
import copy
import cPickle as pickle
import Math
import BigWorld
import ArenaType
import Settings
import CommandMapping
import constants
import Keys
import Event
import AreaDestructibles
import gui.SystemMessages
import gui.Scaleform.CursorDelegator
from gui import GUI_SETTINGS
from gui.app_loader import g_appLoader
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID
from helpers import EffectsList, isPlayerAvatar, isPlayerAccount, getFullClientVersion
from debug_utils import *
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from constants import ARENA_PERIOD

def _isVideoCameraCtrl(mode):
    from AvatarInputHandler.control_modes import VideoCameraControlMode
    return isinstance(mode, VideoCameraControlMode)


def _isCatCtrl(mode):
    from AvatarInputHandler.control_modes import CatControlMode
    return isinstance(mode, CatControlMode)


g_replayCtrl = None
REPLAY_FILE_EXTENSION = '.wotreplay'
AUTO_RECORD_TEMP_FILENAME = 'temp'
FIXED_REPLAY_FILENAME = 'replay_last_battle'
REPLAY_TIME_MARK_CLIENT_READY = 2147483648L
REPLAY_TIME_MARK_REPLAY_FINISHED = 2147483649L
REPLAY_TIME_MARK_CURRENT_TIME = 2147483650L
FAST_FORWARD_STEP = 20.0

class BattleReplay():
    isPlaying = property(lambda self: self.__replayCtrl.isPlaying())
    isRecording = property(lambda self: self.__replayCtrl.isRecording)
    isClientReady = property(lambda self: self.__replayCtrl.isClientReady)
    isControllingCamera = property(lambda self: self.__replayCtrl.isControllingCamera)
    isOffline = property(lambda self: self.__replayCtrl.isOfflinePlaybackMode)
    isTimeWarpInProgress = property(lambda self: self.__replayCtrl.isTimeWarpInProgress or self.__timeWarpCleanupCb is not None)
    isServerAim = property(lambda self: self.__replayCtrl.isServerAim)
    playerVehicleID = property(lambda self: self.__replayCtrl.playerVehicleID)
    fps = property(lambda self: self.__replayCtrl.fps)
    ping = property(lambda self: self.__replayCtrl.ping)
    compressed = property(lambda self: self.__replayCtrl.isFileCompressed())
    isLaggingNow = property(lambda self: self.__replayCtrl.isLaggingNow)
    playbackSpeed = property(lambda self: self.__replayCtrl.playbackSpeed)
    scriptModalWindowsEnabled = property(lambda self: self.__replayCtrl.scriptModalWindowsEnabled)
    currentTime = property(lambda self: self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_CURRENT_TIME))
    warpTime = property(lambda self: self.__warpTime)

    def resetUpdateGunOnTimeWarp(self):
        self.__updateGunOnTimeWarp = False

    isUpdateGunOnTimeWarp = property(lambda self: self.__updateGunOnTimeWarp)

    def __init__(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_REPLAY_PREFERENCES):
            userPrefs.write(Settings.KEY_REPLAY_PREFERENCES, '')
        self.__settings = userPrefs[Settings.KEY_REPLAY_PREFERENCES]
        self.__fileName = None
        self.__replayCtrl = BigWorld.WGReplayController()
        self.__replayCtrl.replayFinishedCallback = self.onReplayFinished
        self.__replayCtrl.controlModeChangedCallback = self.onControlModeChanged
        self.__replayCtrl.ammoButtonPressedCallback = self.__onAmmoButtonPressed
        self.__replayCtrl.playerVehicleIDChangedCallback = self.onPlayerVehicleIDChanged
        self.__replayCtrl.clientVersionDiffersCallback = self.onClientVersionDiffers
        self.__replayCtrl.battleChatMessageCallback = self.onBattleChatMessage
        self.__replayCtrl.lockTargetCallback = self.onLockTarget
        self.__replayCtrl.cruiseModeCallback = self.onSetCruiseMode
        self.__replayCtrl.equipmentIdCallback = self.onSetEquipmentId
        self.__isAutoRecordingEnabled = False
        self.__quitAfterStop = False
        self.__isPlayingPlayList = False
        self.__playList = []
        self.__isFinished = False
        self.__isMenuShowed = False
        self.__updateGunOnTimeWarp = False
        g_playerEvents.onBattleResultsReceived += self.__onBattleResultsReceived
        g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.__onSettingsChanging
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
        self.__timeWarpCleanupCb = None
        self.__enableTimeWarp = False
        self.__isChatPlaybackEnabled = True
        self.__warpTime = -1.0
        self.__skipMessage = False
        self.__equipmentId = None
        self.__rewind = False
        self.replayTimeout = 0
        self.__arenaPeriod = -1
        self.enableAutoRecordingBattles(True)
        gui.Scaleform.CursorDelegator.g_cursorDelegator.detachCursor()
        self.onCommandReceived = Event.Event()
        self.onAmmoSettingChanged = Event.Event()
        self.onStopped = Event.Event()
        return

    def destroy(self):
        self.stop()
        self.onCommandReceived.clear()
        self.onCommandReceived = None
        self.onAmmoSettingChanged.clear()
        self.onAmmoSettingChanged = None
        g_playerEvents.onBattleResultsReceived -= self.__onBattleResultsReceived
        g_playerEvents.onAccountBecomePlayer -= self.__onAccountBecomePlayer
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanging
        self.enableAutoRecordingBattles(False)
        self.__replayCtrl.replayFinishedCallback = None
        self.__replayCtrl.controlModeChangedCallback = None
        self.__replayCtrl.clientVersionDiffersCallback = None
        self.__replayCtrl.playerVehicleIDChangedCallback = None
        self.__replayCtrl.battleChatMessageCallback = None
        self.__replayCtrl.ammoButtonPressedCallback = None
        self.__replayCtrl.lockTargetCallback = None
        self.__replayCtrl.cruiseModeCallback = None
        self.__replayCtrl.equipmentIdCallback = None
        self.__replayCtrl = None
        self.__settings = None
        self.__videoCameraMatrix = None
        self.__warpTime = -1.0
        self.__arenaPeriod = -1
        if self.__timeWarpCleanupCb is not None:
            BigWorld.cancelCallback(self.__timeWarpCleanupCb)
            self.__timeWarpCleanupCb = None
        return

    def record(self, fileName=None):
        if self.isPlaying:
            return False
        else:
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
            except:
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
                except:
                    if useAutoFilename:
                        continue
                    else:
                        break

            if not success:
                LOG_ERROR('Failed to create replay file, replays folder may be write-protected')
                return False
            if self.__replayCtrl.startRecording(fileName):
                self.__fileName = fileName
                return True
            return False
            return

    def play(self, fileName=None):
        if self.isRecording:
            self.stop()
        import SafeUnpickler
        import cPickle
        unpickler = SafeUnpickler.SafeUnpickler()
        cPickle.loads = unpickler.loads
        if fileName is not None and fileName.rfind('.wotreplaylist') != -1:
            self.__playList = []
            self.__isPlayingPlayList = True
            try:
                f = open(fileName)
                s = f.read()
                f.close()
                self.__playList = s.replace('\r\n', '\n').replace('\r', '\n').split('\n')
                fileName = None
            except:
                pass

        if fileName is None:
            if len(self.__playList) == 0:
                return False
            fileName = self.__playList[0]
            self.__playList.pop(0)
            self.__quitAfterStop = len(self.__playList) == 0
        self.__fileName = fileName
        if self.__replayCtrl.startPlayback(fileName):
            self.__playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
            self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
            return True
        else:
            self.__fileName = None
            return False
            return

    def stop(self, rewindToTime=None, delete=False):
        if not self.isPlaying and not self.isRecording:
            return False
        else:
            self.onStopped()
            wasPlaying = self.isPlaying
            isOffline = self.__replayCtrl.isOfflinePlaybackMode
            self.__replayCtrl.stop(delete)
            self.__fileName = None
            if wasPlaying:
                if isPlayerAvatar():
                    BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
                if not isOffline:
                    connectionManager.onDisconnected += self.__showLoginPage
                BigWorld.clearEntitiesAndSpaces()
                BigWorld.disconnect()
                if self.__quitAfterStop:
                    BigWorld.quit()
                elif isOffline:
                    self.__showLoginPage()
            return

    def autoStartBattleReplay(self):
        fileName = self.__replayCtrl.getAutoStartFileName()
        if fileName != '':
            self.__quitAfterStop = True
            if not self.play(fileName):
                BigWorld.quit()
            else:
                return True
        return False

    def handleKeyEvent(self, isDown, key, mods, isRepeat, event):
        if not self.isPlaying:
            return False
        if self.isTimeWarpInProgress:
            return True
        if key == Keys.KEY_F1:
            return True
        if not self.isClientReady:
            return False
        cmdMap = CommandMapping.g_instance
        player = BigWorld.player()
        if not isPlayerAvatar():
            return False
        if key == Keys.KEY_ESCAPE:
            if isDown and not player.isForcedGuiControlMode():
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
        isCursorVisible = gui.Scaleform.CursorDelegator.g_cursorDelegator._CursorDelegator__activated
        fastForwardStep = FAST_FORWARD_STEP * (2.0 if mods == 2 else 1.0)
        if (key == Keys.KEY_LEFTMOUSE or cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key)) and isDown and not isCursorVisible:
            if self.isControllingCamera:
                controlMode = self.getControlMode()
                self.onControlModeChanged('arcade')
                self.__replayCtrl.isControllingCamera = False
                self.onControlModeChanged(controlMode)
                self.__showInfoMessage('replayFreeCameraActivated')
            else:
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
            self.__timeWarp(currReplayTime - fastForwardStep)
            return True
        if key == Keys.KEY_HOME and isDown:
            self.__timeWarp(0.0)
            return True
        if key == Keys.KEY_END and isDown and not self.__isFinished:
            self.__timeWarp(finishReplayTime)
            return True
        if key == Keys.KEY_C and isDown:
            self.__isChatPlaybackEnabled = not self.__isChatPlaybackEnabled
        playerControlMode = player.inputHandler.ctrl
        isVideoCamera = _isVideoCameraCtrl(playerControlMode) or _isCatCtrl(playerControlMode)
        suppressCommand = False
        if cmdMap.isFiredList(xrange(CommandMapping.CMD_AMMO_CHOICE_1, CommandMapping.CMD_AMMO_CHOICE_0 + 1), key) and isDown:
            suppressCommand = True
        elif (key == Keys.KEY_RETURN or key == Keys.KEY_NUMPADENTER) and isDown and mods != 4:
            suppressCommand = not GUI_SETTINGS.useAS3Battle
        elif cmdMap.isFiredList((CommandMapping.CMD_CM_LOCK_TARGET,
         CommandMapping.CMD_CM_LOCK_TARGET_OFF,
         CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE,
         CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE,
         CommandMapping.CMD_RADIAL_MENU_SHOW,
         CommandMapping.CMD_RELOAD_PARTIAL_CLIP), key) and isDown and not isCursorVisible:
            suppressCommand = True
        elif cmdMap.isFiredList((CommandMapping.CMD_USE_HORN,
         CommandMapping.CMD_STOP_UNTIL_FIRE,
         CommandMapping.CMD_INCREMENT_CRUISE_MODE,
         CommandMapping.CMD_DECREMENT_CRUISE_MODE,
         CommandMapping.CMD_MOVE_FORWARD,
         CommandMapping.CMD_MOVE_FORWARD_SPEC,
         CommandMapping.CMD_MOVE_BACKWARD,
         CommandMapping.CMD_ROTATE_LEFT,
         CommandMapping.CMD_ROTATE_RIGHT), key):
            suppressCommand = True
        if suppressCommand:
            if isVideoCamera:
                playerControlMode.handleKeyEvent(isDown, key, mods, event)
            return True
        return False

    def handleMouseEvent(self, dx, dy, dz):
        if not (self.isPlaying and self.isClientReady):
            return False
        if self.isTimeWarpInProgress:
            return True
        player = BigWorld.player()
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

    def setConsumablesPosition(self, pos, dir=Math.Vector3(1, 1, 1)):
        self.__replayCtrl.gunMarkerPosition = pos
        self.__replayCtrl.gunMarkerDirection = dir

    def setGunMarkerParams(self, diameter, pos, dir):
        controlMode = self.getControlMode()
        if controlMode != 'mapcase':
            self.__replayCtrl.gunMarkerDiameter = diameter
            self.__replayCtrl.gunMarkerPosition = pos
            self.__replayCtrl.gunMarkerDirection = dir

    def getGunMarkerParams(self, defaultPos, defaultDir):
        diameter = self.__replayCtrl.gunMarkerDiameter
        dir = self.__replayCtrl.gunMarkerDirection
        pos = self.__replayCtrl.gunMarkerPosition
        if dir == Math.Vector3(0, 0, 0):
            pos = defaultPos
            dir = defaultDir
        return (diameter, pos, dir)

    def getGunMarkerPos(self):
        return self.__replayCtrl.gunMarkerPosition

    def getEquipmentId(self):
        return self.__equipmentId

    def setArcadeGunMarkerSize(self, size):
        self.__replayCtrl.setArcadeGunMarkerSize(size)

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
        return self.__replayCtrl.turretYaw

    def setGunPitch(self, value):
        self.__replayCtrl.gunPitch = value

    def getGunPitch(self):
        return self.__replayCtrl.gunPitch

    def getGunReloadAmountLeft(self):
        return self.__replayCtrl.getGunReloadAmountLeft()

    def setGunReloadTime(self, startTime, duration):
        self.__replayCtrl.setGunReloadTime(startTime, duration)

    def resetArenaPeriod(self):
        if not self.isRecording:
            LOG_ERROR('Replay is not recorded on resetArenaPeriod')
        self.__replayCtrl.resetArenaPeriod()

    def setArenaPeriod(self, period, length):
        if not self.isRecording:
            LOG_ERROR('Replay is not recorded on setArenaPeriod')
        if period == constants.ARENA_PERIOD.AFTERBATTLE:
            period = constants.ARENA_PERIOD.BATTLE
        self.__replayCtrl.arenaPeriod = period
        self.__replayCtrl.arenaLength = length

    def getArenaPeriod(self):
        assert self.isPlaying
        ret = self.__replayCtrl.arenaPeriod
        if ret not in (constants.ARENA_PERIOD.IDLE,
         constants.ARENA_PERIOD.WAITING,
         constants.ARENA_PERIOD.PREBATTLE,
         constants.ARENA_PERIOD.BATTLE):
            ret = constants.ARENA_PERIOD.WAITING
        return ret

    def getArenaLength(self):
        assert self.isPlaying
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
                AreaDestructibles.g_destructiblesManager.onAfterReplayTimeWarp()
                if isPlayerAvatar():
                    BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
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
                 'serverName': connectionManager.serverUserName,
                 'regionCode': constants.AUTH_REALM,
                 'serverSettings': self.__serverSettings}
                self.__replayCtrl.recMapName = arenaName
                self.__replayCtrl.recPlayerVehicleName = vehicleName
                self.__replayCtrl.setArenaInfoStr(json.dumps(arenaInfo))
            else:
                self.__showInfoMessage('replayControlsHelp1')
                self.__showInfoMessage('replayControlsHelp2')
                self.__showInfoMessage('replayControlsHelp3')
                if self.replayTimeout > 0:
                    LOG_DEBUG('replayTimeout set for %.2f' % float(self.replayTimeout))
                    BigWorld.callback(float(self.replayTimeout), BigWorld.quit)
            return

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
            vehicles[k] = vehicle

        return vehicles

    def onBattleSwfLoaded(self):
        if self.isPlaying:
            self.__serverSettings = dict()
            try:
                self.__serverSettings = json.loads(self.__replayCtrl.getArenaInfoStr()).get('serverSettings')
            except:
                LOG_WARNING('There is problem while unpacking server settings from replay')
                if IS_DEVELOPMENT:
                    LOG_CURRENT_EXCEPTION()

            from gui.LobbyContext import g_lobbyContext
            g_lobbyContext.setServerSettings(self.__serverSettings)

    def onCommonSwfLoaded(self):
        self.__enableTimeWarp = False

    def onCommonSwfUnloaded(self):
        if self.isPlaying:
            self.__enableTimeWarp = True
            self.__replayCtrl.onCommonSfwUnloaded()

    def onReplayFinished(self):
        if not self.scriptModalWindowsEnabled:
            self.stop()
            return
        if self.__isPlayingPlayList:
            self.stop()
            BigWorld.callback(1.0, self.play)
            return
        self.__isMenuShowed = False
        from gui import DialogsInterface
        DialogsInterface.showI18nInfoDialog('replayStopped', self.__setStopDelay)
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
                if controlMode == 'sniper' or forceControlMode == 'strategic':
                    return
            if not self.isControllingCamera and forceControlMode is None:
                return
            controlMode = self.getControlMode() if forceControlMode is None else forceControlMode
            preferredPos = self.getGunRotatorTargetPoint()
            if controlMode == 'mapcase':
                _, preferredPos, _ = self.getGunMarkerParams(preferredPos, Math.Vector3(0.0, 0.0, 1.0))
            player.inputHandler.onControlModeChanged(controlMode, camMatrix=BigWorld.camera().matrix, preferredPos=preferredPos, saveZoom=False, saveDist=False, equipmentID=self.__equipmentId)
            return

    def onPlayerVehicleIDChanged(self):
        player = BigWorld.player()
        if self.isPlaying and hasattr(player, 'positionControl'):
            player.inputHandler.ctrl.selectPlayer(self.__replayCtrl.playerVehicleID)

    def setAmmoSetting(self, idx):
        if not isPlayerAvatar():
            return
        if self.isRecording:
            self.__replayCtrl.onAmmoButtonPressed(idx)

    def __onAmmoButtonPressed(self, idx):
        self.onAmmoSettingChanged(idx)

    def onLockTarget(self, lock):
        player = BigWorld.player()
        if not isPlayerAvatar():
            return
        if self.isPlaying:
            if lock == 1:
                player.soundNotifications.play('target_captured')
            elif lock == 0:
                player.soundNotifications.play('target_unlocked')
            else:
                player.soundNotifications.play('target_lost')
        elif self.isRecording:
            self.__replayCtrl.onLockTarget(lock)

    def onBattleChatMessage(self, messageText, isCurrentPlayer):
        from messenger import MessengerEntry
        if self.isRecording:
            if not self.__skipMessage:
                self.__replayCtrl.onBattleChatMessage(messageText, isCurrentPlayer)
            self.__skipMessage = False
        elif self.isPlaying and not self.isTimeWarpInProgress:
            if self.__isChatPlaybackEnabled:
                MessengerEntry.g_instance.gui.addClientMessage(messageText, isCurrentPlayer)

    def skipMessage(self):
        self.__skipMessage = True

    def onChatAction(self, chatAction):
        if self.isPlaying:
            pass

    def setFpsPingLag(self, fps, ping, isLaggingNow):
        if self.isPlaying:
            return
        self.__replayCtrl.fps = fps
        self.__replayCtrl.ping = ping
        self.__replayCtrl.isLaggingNow = isLaggingNow

    def onClientVersionDiffers(self):
        if BigWorld.wg_isFpsInfoStoreEnabled():
            BigWorld.wg_markFpsStoreFileAsFailed(self.__fileName)
            self.__onClientVersionConfirmDlgClosed(False)
            return
        if not self.scriptModalWindowsEnabled:
            self.__onClientVersionConfirmDlgClosed(True)
            return
        g_appLoader.onGUISpaceEntered += self.__onGUISpaceEntered
        g_appLoader.showLogin()

    def __onGUISpaceEntered(self, spaceID):
        if spaceID != GUI_GLOBAL_SPACE_ID.LOGIN:
            return
        g_appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered
        from gui import DialogsInterface
        DialogsInterface.showI18nConfirmDialog('replayNotification', self.__onClientVersionConfirmDlgClosed)

    def __onClientVersionConfirmDlgClosed(self, result):
        if result:
            self.__replayCtrl.confirmDlgAccepted()
        else:
            self.stop()

    def registerWotReplayFileExtension(self):
        self.__replayCtrl.registerWotReplayFileExtension()

    def enableAutoRecordingBattles(self, enable):
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
                    self.stop()
            return

    def setResultingFileName(self, fileName, overwriteExisting=False):
        self.__replayCtrl.setResultingFileName(fileName or '', overwriteExisting)

    def cancelSaveCurrMessage(self):
        self.__replayCtrl.saveCurrMessage(False)

    def saveCurrMessage(self):
        self.__replayCtrl.saveCurrMessage(True)

    def __showInfoMessage(self, msg, args=None):
        if not self.isTimeWarpInProgress:
            g_replayEvents.onWatcherNotify(msg, args)

    def __startAutoRecord(self):
        if not self.__isAutoRecordingEnabled:
            return
        if self.isPlaying:
            return
        if self.isRecording or not isPlayerAccount():
            BigWorld.callback(0.1, self.__startAutoRecord)
            return
        self.record()

    def __showLoginPage(self):
        g_appLoader.showLogin()
        connectionManager.onDisconnected -= self.__showLoginPage

    def setArenaStatisticsStr(self, arenaUniqueStr):
        self.__replayCtrl.setArenaStatisticsStr(arenaUniqueStr)

    def __onBattleResultsReceived(self, isPlayerVehicle, results):
        if isPlayerVehicle:
            modifiedResults = copy.deepcopy(results)
            allPlayersVehicles = modifiedResults.get('vehicles', None)
            if allPlayersVehicles is not None:
                for playerVehicles in allPlayersVehicles.itervalues():
                    for vehicle in playerVehicles:
                        vehicle['damageEventList'] = None

            personals = modifiedResults.get('personal', None)
            if personals is not None:
                for personal in personals.itervalues():
                    for field in ('damageEventList', 'xpReplay', 'creditsReplay', 'tmenXPReplay', 'fortResourceReplay', 'goldReplay', 'freeXPReplay', 'avatarDamageEventList'):
                        personal[field] = None

            modifiedResults = (modifiedResults, self.__getArenaVehiclesInfo(), BigWorld.player().arena.statistics)
            self.__replayCtrl.setArenaStatisticsStr(json.dumps(_JSON_Encode(modifiedResults)))
        return

    def __onAccountBecomePlayer(self):
        if not isPlayerAccount():
            return
        else:
            player = BigWorld.player()
            self.__serverSettings['roaming'] = player.serverSettings['roaming']
            self.__serverSettings['isPotapovQuestEnabled'] = player.serverSettings.get('isPotapovQuestEnabled', False)
            if player.databaseID is None:
                BigWorld.callback(0.1, self.__onAccountBecomePlayer)
            else:
                self.__playerDatabaseID = player.databaseID
            return

    def __onSettingsChanging(self, diff):
        newSpeed = self.__playbackSpeedModifiers[self.__playbackSpeedIdx]
        newQuiet = newSpeed == 0 or newSpeed > 4.0
        g_replayEvents.onMuteSound(newQuiet)

    def __timeWarp(self, time):
        if not self.isPlaying or not self.__enableTimeWarp:
            return
        else:
            BigWorld.wg_enableGUIBackground(True, False)
            if self.__isFinished:
                self.setPlaybackSpeedIdx(self.__savedPlaybackSpeedIdx)
            self.__isFinished = False
            self.__warpTime = time
            self.__rewind = time < self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_CURRENT_TIME)
            AreaDestructibles.g_destructiblesManager.onBeforeReplayTimeWarp(self.__rewind)
            self.__updateGunOnTimeWarp = True
            EffectsList.EffectsListPlayer.clear()
            if self.__rewind:
                playerControlMode = BigWorld.player().inputHandler.ctrl
                self.__wasVideoBeforeRewind = _isVideoCameraCtrl(playerControlMode)
                self.__videoCameraMatrix.set(BigWorld.camera().matrix)
                g_replayEvents.onMuteSound(True)
                BigWorld.PyGroundEffectManager().stopAll()
            self.__enableInGameEffects(False)
            if not self.__replayCtrl.beginTimeWarp(time):
                self.__cleanupAfterTimeWarp()
                return
            if self.__timeWarpCleanupCb is None:
                self.__timeWarpCleanupCb = BigWorld.callback(0.0, self.__cleanupAfterTimeWarp)
            g_replayEvents.onTimeWarpStart()
            g_replayEvents.onMuteSound(True)
            return

    def __cleanupAfterTimeWarp(self):
        BigWorld.wg_clearDecals()
        if self.__replayCtrl.isTimeWarpInProgress:
            self.__enableInGameEffects(False)
            self.__timeWarpCleanupCb = BigWorld.callback(0.0, self.__cleanupAfterTimeWarp)
        else:
            if self.__timeWarpCleanupCb is not None:
                BigWorld.cancelCallback(self.__timeWarpCleanupCb)
                self.__timeWarpCleanupCb = None
            self.__warpTime = -1.0
            BigWorld.wg_enableGUIBackground(False, False)
            self.__enableInGameEffects(0.0 < self.__playbackSpeedModifiers[self.__playbackSpeedIdx] < 8.0)
            g_replayEvents.onMuteSound(not 0.0 < self.__playbackSpeedModifiers[self.__playbackSpeedIdx] < 8.0)
            if self.__wasVideoBeforeRewind:
                BigWorld.player().inputHandler.onControlModeChanged('video', prevModeName='arcade', camMatrix=self.__videoCameraMatrix)
                self.__wasVideoBeforeRewind = False
            g_replayEvents.onTimeWarpFinish()
        return

    def __enableInGameEffects(self, enable):
        AreaDestructibles.g_destructiblesManager.forceNoAnimation = not enable

    def getSetting(self, key, default=None):
        return pickle.loads(base64.b64decode(self.__settings.readString(key))) if self.__settings.has_key(key) else default

    def setSetting(self, key, value):
        self.__settings.write(key, base64.b64encode(pickle.dumps(value)))

    def isFinished(self):
        if self.isPlaying or g_replayCtrl.isTimeWarpInProgress:
            return self.__isFinished
        else:
            return False

    def onSetCruiseMode(self, mode):
        from gui.battle_control import g_sessionProvider
        from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
        if self.isRecording:
            self.__replayCtrl.onSetCruiseMode(mode)
        elif self.isPlaying:
            g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CRUISE_MODE, mode)

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
        arcadeMode = BigWorld.player().inputHandler.ctrls.get('arcade', None)
        if equipmentId != -1:
            self.__equipmentId = equipmentId
            arcadeMode.showGunMarker(False)
            mapCaseMode = BigWorld.player().inputHandler.ctrls.get('mapcase', None)
            if mapCaseMode is not None:
                mapCaseMode.activateEquipment(equipmentId)
        else:
            arcadeMode.showGunMarker(True)
        return

    def __setStopDelay(self, *args):
        BigWorld.callback(0.0, self.stop)

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == self.playerVehicleID:
            if self.__replayCtrl.isControllingCamera:
                self.onControlModeChanged(self.getControlMode())

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if self.isRecording:
            if self.__arenaPeriod == period and period == ARENA_PERIOD.BATTLE:
                self.resetArenaPeriod()
        self.__arenaPeriod = period

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


def _JSON_Encode(obj):
    if isinstance(obj, dict):
        newDict = {}
        for key, value in obj.iteritems():
            if isinstance(key, tuple):
                newDict[str(key)] = _JSON_Encode(value)
            newDict[key] = _JSON_Encode(value)

        return newDict
    if isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
        newList = []
        for value in obj:
            newList.append(_JSON_Encode(value))

        return newList
    return obj


def isPlaying():
    return g_replayCtrl.isPlaying or g_replayCtrl.isTimeWarpInProgress
