# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleReplay.py
# Compiled at: 2018-12-13 03:28:58
import BigWorld
import ResMgr
import os
import datetime
import Account
import Avatar
import Settings
import CommandMapping
import SoundGroups
import constants
from gui.Scaleform.utils import functions
import gui.SystemMessages
import gui.Scaleform.CursorDelegator
import Keys
from debug_utils import *
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from gui import VERSION_FILE_PATH
from helpers import i18n
from gui.WindowsManager import g_windowsManager
AUTO_RECORD_TEMP_FILENAME = 'temp.wotreplay'
g_replayCtrl = None

class BattleReplay:
    isPlaying = property(lambda self: self.__replayCtrl.isPlaying)
    isRecording = property(lambda self: self.__replayCtrl.isRecording)
    isClientReady = property(lambda self: self.__replayCtrl.isClientReady)
    isControllingCamera = property(lambda self: self.__replayCtrl.isControllingCamera)
    isOffline = property(lambda self: self.__replayCtrl.isOfflinePlaybackMode)
    fps = property(lambda self: self.__replayCtrl.fps)
    ping = property(lambda self: self.__replayCtrl.ping)
    isLaggingNow = property(lambda self: self.__replayCtrl.isLaggingNow)
    playbackSpeed = property(lambda self: self.__replayCtrl.playbackSpeed)

    def __init__(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_REPLAY_PREFERENCES):
            userPrefs.write(Settings.KEY_REPLAY_PREFERENCES, '')
            userPrefs[Settings.KEY_REPLAY_PREFERENCES].writeBool('enabled', False)
        self.__settings = userPrefs[Settings.KEY_REPLAY_PREFERENCES]
        self.__fileName = None
        self.__replayCtrl = BigWorld.WGReplayController()
        self.__replayCtrl.replayFinishedCallback = self.onReplayFinished
        self.__replayCtrl.controlModeChangedCallback = self.onControlModeChanged
        self.__replayCtrl.ammoButtonPressedCallback = self.onAmmoButtonPressed
        self.__replayCtrl.clientVersionDiffersCallback = self.onClientVersionDiffers
        self.__isAutoRecordingEnabled = False
        self.__quitAfterStop = False
        self.__playbackSpeedModifiers = (0.0, 0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
        self.__playbackSpeedModifiersStr = ('0', '1/16', '1/8', '1/4', '1/2', '1', '2', '4', '8', '16')
        self.__playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
        self.__gunWasLockedBeforePause = False
        self.__replayDir = './replays'
        sec = ResMgr.openSection(VERSION_FILE_PATH)
        version = i18n.makeString(sec.readString('appname')) + ' ' + sec.readString('version')
        self.__replayCtrl.clientVersion = version
        if self.__settings.readBool('enabled'):
            self.enableAutoRecordingBattles(True)
        self.__isPlayingPlayList = False
        self.__playList = []
        self.__cbPlayingList = None
        return

    def destroy(self):
        self.stop()
        self.enableAutoRecordingBattles(False)
        self.__replayCtrl.replayFinishedCallback = None
        self.__replayCtrl.controlModeChangedCallback = None
        self.__replayCtrl.clientVersionDiffersCallback = None
        self.__replayCtrl = None
        if self.__cbPlayingList is not None:
            BigWorld.cancelCallback(self.__cbPlayingList)
            self.__cbPlayingList = None
        return

    def record(self, fileName=None):
        if self.isPlaying:
            return False
        elif self.isRecording:
            return self.__fileName == fileName
        else:
            if fileName is None:
                try:
                    fileName = os.path.join(self.__replayDir, AUTO_RECORD_TEMP_FILENAME)
                    if not os.path.isdir(self.__replayDir):
                        os.makedirs(self.__replayDir)
                except:
                    LOG_CURRENT_EXCEPTION()
                    return

            if self.__replayCtrl.startRecording(fileName):
                self.__fileName = fileName
                return True
            return False
            return

    def play(self, fileName=None):
        if self.__cbPlayingList is not None:
            self.__cbPlayingList = None
        if self.isRecording:
            self.stop()
        elif self.isPlaying:
            return self.__fileName == fileName
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
                fileName = None

        if fileName is None:
            if not self.__playList:
                return False
            fileName = self.__playList[0]
            self.__playList.pop(0)
            self.__quitAfterStop = len(self.__playList) == 0
        if self.__replayCtrl.startPlayback(fileName):
            self.__fileName = fileName
            self.__playbackSpeedIdx = self.__playbackSpeedModifiers.index(1.0)
            self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
            return True
        else:
            return False
            return

    def stop(self):
        if not self.isPlaying and not self.isRecording:
            return False
        else:
            wasPlaying = self.isPlaying
            isOffline = self.__replayCtrl.isOfflinePlaybackMode
            self.__replayCtrl.stop()
            self.__fileName = None
            if wasPlaying:
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
            return self.play(fileName)
        return False

    def handleKeyEvent(self, isDown, key, mods, isRepeat, event):
        if self.isPlaying:
            if not self.isClientReady:
                return False
            cmdMap = CommandMapping.g_instance
            player = BigWorld.player()
            if not isinstance(player, Avatar.PlayerAvatar):
                return
            isCursorVisible = gui.Scaleform.CursorDelegator.g_cursorDelegator._CursorDelegator__activated
            if (key == Keys.KEY_LEFTMOUSE or cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key)) and isDown and not isCursorVisible:
                if self.isControllingCamera:
                    player.inputHandler.onControlModeChanged('arcade', saveDist=False, saveZoom=False)
                    self.__replayCtrl.isControllingCamera = False
                    self.__showInfoMessage('replayFreeCameraActivated')
                else:
                    self.__replayCtrl.isControllingCamera = True
                    self.onControlModeChanged()
                    self.__showInfoMessage('replaySavedCameraActivated')
                return True
            if cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
                if self.isControllingCamera:
                    return True
            if key == Keys.KEY_SPACE and isDown:
                if self.__playbackSpeedIdx > 0:
                    self.setPlaybackSpeedIdx(0)
                else:
                    self.setPlaybackSpeedIdx(self.__savedPlaybackSpeedIdx)
                return True
            if key == Keys.KEY_LEFTARROW and isDown:
                if self.__playbackSpeedIdx > 0:
                    self.setPlaybackSpeedIdx(self.__playbackSpeedIdx - 1)
                return True
            if key == Keys.KEY_RIGHTARROW and isDown:
                if self.__playbackSpeedIdx < len(self.__playbackSpeedModifiers) - 1:
                    self.setPlaybackSpeedIdx(self.__playbackSpeedIdx + 1)
                return True
            if key == Keys.KEY_DOWNARROW and isDown:
                self.setPlaybackSpeedIdx(self.__playbackSpeedModifiers.index(1.0))
                return True
            if cmdMap.isFiredList(xrange(CommandMapping.CMD_AMMO_CHOICE_1, CommandMapping.CMD_AMMO_CHOICE_0 + 1), key) and isDown:
                return True
            if cmdMap.isFiredList((CommandMapping.CMD_CM_LOCK_TARGET,
             CommandMapping.CMD_CM_LOCK_TARGET_OFF,
             CommandMapping.CMD_USE_HORN,
             CommandMapping.CMD_STOP_UNTIL_FIRE,
             CommandMapping.CMD_INCREMENT_CRUISE_MODE,
             CommandMapping.CMD_DECREMENT_CRUISE_MODE,
             CommandMapping.CMD_MOVE_FORWARD,
             CommandMapping.CMD_MOVE_FORWARD_SPEC,
             CommandMapping.CMD_MOVE_BACKWARD), key) and isDown:
                return True
            return (key == Keys.KEY_RETURN or key == Keys.KEY_NUMPADENTER) and isDown and True
        return False

    def handleMouseEvent(self, dx, dy, dz):
        if self.isPlaying:
            if not self.isClientReady:
                return False
            player = BigWorld.player()
            if not isinstance(player, Avatar.PlayerAvatar):
                return False
            if self.isControllingCamera:
                return dz != 0 and True
        return False

    def setGunRotatorTargetPoint(self, value):
        self.__replayCtrl.gunRotatorTargetPoint = value

    def getGunRotatorTargetPoint(self):
        return self.__replayCtrl.gunRotatorTargetPoint

    def setGunMarkerDiameter(self, value):
        self.__replayCtrl.gunMarkerDiameter = value

    def getGunMarkerDiameter(self):
        return self.__replayCtrl.gunMarkerDiameter

    def setTurretYaw(self, value):
        self.__replayCtrl.turretYaw = value

    def getTurretYaw(self):
        return self.__replayCtrl.turretYaw

    def setGunPitch(self, value):
        self.__replayCtrl.gunPitch = value

    def getGunPitch(self):
        return self.__replayCtrl.gunPitch

    def setArenaPeriod(self, value):
        self.__replayCtrl.arenaPeriod = value

    def getArenaPeriod(self):
        return self.__replayCtrl.arenaPeriod

    def setArenaLength(self, value):
        self.__replayCtrl.arenaLength = value

    def getArenaLength(self):
        return self.__replayCtrl.arenaLength

    def setPlaybackSpeedIdx(self, value):
        self.__savedPlaybackSpeedIdx = self.__playbackSpeedIdx
        self.__playbackSpeedIdx = value
        oldSpeed = self.__playbackSpeedModifiers[self.__savedPlaybackSpeedIdx]
        if not oldSpeed == 0:
            oldQuiet = oldSpeed > 4.0
            newSpeed = self.__playbackSpeedModifiers[self.__playbackSpeedIdx]
            if not newSpeed == 0:
                newQuiet = newSpeed > 4.0
                if oldQuiet != newQuiet:
                    SoundGroups.g_instance.enableArenaSounds(not newQuiet)
                player = BigWorld.player()
                self.__gunWasLockedBeforePause = newSpeed == 0.0 and player.gunRotator._VehicleGunRotator__isLocked
                player.gunRotator.lock(True)
                self.__showInfoMessage('replayPaused')
            else:
                player.gunRotator.lock(self.__gunWasLockedBeforePause)
                newSpeedStr = self.__playbackSpeedModifiersStr[self.__playbackSpeedIdx]
                self.__showInfoMessage('replaySpeedChange', {'speed': newSpeedStr})
            self.__replayCtrl.playbackSpeed = newSpeed
            newSpeed == 0 and BigWorld.callback(0, self.__updateAim)

    def getPlaybackSpeedIdx(self):
        ret = self.__playbackSpeedModifiers.index(self.__replayCtrl.playbackSpeed)
        if ret == -1:
            return self.__playbackSpeedModifiers.index(1.0)
        return ret

    def setControlMode(self, value):
        self.__replayCtrl.controlMode = value

    def getControlMode(self):
        return self.__replayCtrl.controlMode

    def onClientReady(self):
        if self.isPlaying or self.isRecording:
            self.__replayCtrl.playerVehicleID = BigWorld.player().playerVehicleID
            self.__replayCtrl.onClientReady()
            if self.isRecording:
                arenaName = BigWorld.player().arena.typeDescriptor.geometry
                i = arenaName.find('/')
                if i != -1:
                    arenaName = arenaName[i + 1:]
                i = arenaName.find('_')
                if i != -1:
                    arenaName = arenaName[i + 1:]
                self.__replayCtrl.recMapName = arenaName
                vehName = BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name
                vehName = vehName.replace(':', '-')
                self.__replayCtrl.recPlayerVehicleName = vehName
        if self.isPlaying:
            self.__showInfoMessage('replayControlsHelp1')
            self.__showInfoMessage('replayControlsHelp2')
            self.__showInfoMessage('replayControlsHelp3')

    def onReplayFinished(self):
        if self.__isPlayingPlayList:
            self.stop()
            if self.__cbPlayingList is not None:
                BigWorld.cancelCallback(self.__cbPlayingList)
            self.__cbPlayingList = BigWorld.callback(1.0, self.play)
            return
        else:
            period = self.__replayCtrl.arenaPeriod
            player = BigWorld.player()
            if isinstance(player, Avatar.PlayerAvatar):
                if player.arena.period == constants.ARENA_PERIOD.AFTERBATTLE:
                    period = constants.ARENA_PERIOD.AFTERBATTLE
            if period != constants.ARENA_PERIOD.AFTERBATTLE:
                functions.showInformationDialog('replayStopped', self.stop, ns='battle')
            return

    def onControlModeChanged(self):
        if self.isPlaying and not self.isControllingCamera:
            return
        player = BigWorld.player()
        if isinstance(player, Avatar.PlayerAvatar):
            player.inputHandler.onControlModeChanged(self.getControlMode(), camMatrix=BigWorld.camera().matrix, preferredPos=self.getGunRotatorTargetPoint(), saveZoom=False, saveDist=False)

    def onAmmoButtonPressed(self, idx):
        player = BigWorld.player()
        if not isinstance(player, Avatar.PlayerAvatar):
            return
        if self.isPlaying:
            player.onAmmoButtonPressed(idx)
        elif self.isRecording:
            self.__replayCtrl.onAmmoButtonPressed(idx)

    def setFpsPingLag(self, fps, ping, isLaggingNow):
        if self.isPlaying:
            return
        self.__replayCtrl.fps = fps
        self.__replayCtrl.ping = ping
        self.__replayCtrl.isLaggingNow = isLaggingNow

    def onClientVersionDiffers(self):
        g_windowsManager.showLogin()
        functions.showConfirmDialog('replayNotification', self.__onClientVersionConfirmDlgClosed)

    def __onClientVersionConfirmDlgClosed(self, result):
        if result:
            self.__replayCtrl.isWaitingForVersionConfirm = False
        else:
            self.stop()

    def registerWotReplayFileExtension(self):
        self.__replayCtrl.registerWotReplayFileExtension()

    def enableAutoRecordingBattles(self, enable):
        if self.__isAutoRecordingEnabled == enable:
            return
        self.__isAutoRecordingEnabled = enable
        if enable:
            g_playerEvents.onAccountBecomePlayer += self.__startAutoRecord
            if isinstance(BigWorld.player(), Account.PlayerAccount):
                self.__startAutoRecord()
        else:
            g_playerEvents.onAccountBecomePlayer -= self.__startAutoRecord
            if self.isRecording:
                self.stop()

    def cancelSaveCurrMessage(self):
        self.__replayCtrl.cancelSaveCurrMessage()

    def __showInfoMessage(self, msg, args=None):
        g_windowsManager.battleWindow.vMsgsPanel.showMessage(msg, args)

    def __startAutoRecord(self):
        if self.isPlaying:
            return
        if self.isRecording:
            BigWorld.callback(0.1, self.__startAutoRecord)
            return
        self.record()

    def __showLoginPage(self):
        from gui.Scaleform.Disconnect import Disconnect
        Disconnect.hide()
        g_windowsManager.showLogin()
        connectionManager.onDisconnected -= self.__showLoginPage

    def __updateAim(self):
        if self.getPlaybackSpeedIdx() == 0:
            player = BigWorld.player()
            if isinstance(player, Avatar.PlayerAvatar):
                player.inputHandler.aim._update()
                BigWorld.callback(0, self.__updateAim)
