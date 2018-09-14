# Embedded file name: scripts/client/Avatar.py
import cPickle
import zlib
from functools import partial
import math
import Account
import BigWorld, FMOD
import Keys
import Math
import Vehicle
import ClientArena
import AvatarInputHandler
import ProjectileMover
import Settings
import VehicleGunRotator
import constants
import Event
import AreaDestructibles
import CommandMapping
import Weather
import MusicController
import SoundGroups
import AvatarPositionControl
import ResMgr
import TriggersManager
import AccountCommands
from TriggersManager import TRIGGER_TYPE
from OfflineMapCreator import g_offlineMapCreator
from constants import ARENA_PERIOD, AIMING_MODE, VEHICLE_SETTING, DEVELOPMENT_INFO
from constants import SERVER_TICK_LENGTH, VEHICLE_MISC_STATUS, VEHICLE_HIT_FLAGS
from constants import SCOUT_EVENT_TYPE, DROWN_WARNING_LEVEL
from gui.battle_control import g_sessionProvider
from gui.battle_control.battle_constants import SHELL_SET_RESULT, VEHICLE_VIEW_STATE
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles
from messenger import MessengerEntry
from messenger.storage import storage_getter
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN, STREAM_ID_AVATAR_BATTLE_RESULS
from PlayerEvents import g_playerEvents
from ClientChat import ClientChat
from ChatManager import chatManager
from VehicleAppearance import StippleManager
from helpers import bound_effects
from helpers import DecalMap
from gui import PlayerBonusesPanel
from gui import IngameSoundNotifications
from gui import game_control
from gui.Scaleform.BattleDamageMessages import BattleDamageMessages
from gui.WindowsManager import g_windowsManager
from debug_utils import *
from material_kinds import EFFECT_MATERIALS
from post_processing import g_postProcessing
from Vibroeffects.Controllers.ReloadController import ReloadController as VibroReloadController
from LightFx import LightManager
import AuxiliaryFx
from account_helpers import BattleResultsCache
from avatar_helpers import AvatarSyncData
import BattleReplay
import HornCooldown
from physics_shared import computeBarrelLocalPoint
from AvatarInputHandler.control_modes import ArcadeControlMode, VideoCameraControlMode
from AvatarInputHandler import cameras
from gun_rotation_shared import decodeGunAngles, isShootPositionInsideOtherVehicle
import VOIP

class _CRUISE_CONTROL_MODE():
    NONE = 0
    FWD25 = 1
    FWD50 = 2
    FWD100 = 3
    BCKW50 = -1
    BCKW100 = -2


_SHOT_WAITING_MAX_TIMEOUT = 0.2
_SHOT_WAITING_MIN_TIMEOUT = 0.12

class ClientVisibilityFlags():
    CLIENT_MASK = 4293918720L
    SERVER_MASK = 1048575

    @staticmethod
    def updateSpaceVisibility(spaceID, clientVisibilityFlags):
        existingVisibilityFlags = BigWorld.wg_getSpaceItemsVisibilityMask(spaceID)
        existingVisibilityFlags &= ClientVisibilityFlags.SERVER_MASK
        BigWorld.wg_setSpaceItemsVisibilityMask(spaceID, clientVisibilityFlags | existingVisibilityFlags)

    OBSERVER_OBJECTS = 2147483648L


class PlayerAvatar(BigWorld.Entity, ClientChat):
    __onStreamCompletePredef = {STREAM_ID_AVATAR_BATTLE_RESULS: 'receiveBattleResults'}
    isOnArena = property(lambda self: self.__isOnArena)
    isVehicleAlive = property(lambda self: self.__isVehicleAlive)
    isWaitingForShot = property(lambda self: self.__shotWaitingTimerID is not None)
    autoAimVehicle = property(lambda self: BigWorld.entities.get(self.__autoAimVehID, None))
    fireInVehicle = property(lambda self: self.__fireInVehicle)
    deviceStates = property(lambda self: self.__deviceStates)

    def __init__(self):
        LOG_DEBUG('client Avatar.init')
        ClientChat.__init__(self)
        if not BattleReplay.isPlaying():
            self.intUserSettings = Account.g_accountRepository.intUserSettings
            self.syncData = AvatarSyncData.AvatarSyncData()
            self.syncData.setAvatar(self)
            self.intUserSettings.setProxy(self, self.syncData)
        self.__rangeStreamIDCallbacks = RangeStreamIDCallbacks()
        self.__rangeStreamIDCallbacks.addRangeCallback((STREAM_ID_CHAT_MIN, STREAM_ID_CHAT_MAX), '_ClientChat__receiveStreamedData')
        self.__onCmdResponse = {}
        self.__requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN
        self.__prevArenaPeriod = -1
        self.__tryShootCallbackId = None
        self.__fwdSpeedometerLimit = None
        self.__bckwdSpeedometerLimit = None
        self.isTeleport = False
        self.__fireNonFatalDamageTriggerID = None
        return

    def onBecomePlayer(self):
        LOG_DEBUG('Avatar.onBecomePlayer()')
        BigWorld.camera(BigWorld.CursorCamera())
        from gui.shared.utils.HangarSpace import g_hangarSpace
        if g_hangarSpace is not None:
            g_hangarSpace.destroy()
        chatManager.switchPlayerProxy(self)
        g_playerEvents.isPlayerEntityChanging = False
        self.arena = ClientArena.ClientArena(self.arenaUniqueID, self.arenaTypeID, self.arenaBonusType, self.arenaGuiType, self.arenaExtraData, self.weatherPresetID)
        self.vehicleTypeDescriptor = None
        self.terrainEffects = None
        self.hitTesters = set()
        self.filter = BigWorld.AvatarFilter()
        self.onVehicleEnterWorld = Event.Event()
        self.onVehicleLeaveWorld = Event.Event()
        self.onGunShotChanged = Event.Event()
        self.invRotationOnBackMovement = False
        self.__stepsTillInit = 4
        self.__isSpaceInitialized = False
        self.__isOnArena = False
        self.__isVehicleAlive = True
        self.__ownVehicleMProv = Math.WGAdaptiveMatrixProvider()
        m = Math.Matrix()
        m.setIdentity()
        self.__ownVehicleMProv.setStaticTransform(m)
        self.__lastVehicleSpeeds = (0.0, 0.0)
        self.__setOwnVehicleMatrixTimerID = None
        self.__aimingInfo = [0.0,
         0.0,
         1.0,
         0.0,
         0.0,
         0.0,
         1.0]
        g_sessionProvider.start()
        self.__fireInVehicle = False
        self.__isForcedGuiControlMode = False
        self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
        self.__stopUntilFire = False
        self.__stopUntilFireStartTime = -1
        self.__lastTimeOfKeyDown = -1
        self.__lastKeyDown = Keys.KEY_NONE
        self.__numSimilarKeyDowns = 0
        self.__stippleMgr = StippleManager()
        self.__autoAimVehID = 0
        self.__shotWaitingTimerID = None
        self.__gunReloadCommandWaitEndTime = 0.0
        self.__prevGunReloadTimeLeft = -1.0
        self.__frags = set()
        self.__vehicleToVehicleCollisions = {}
        self.__deviceStates = {}
        self.__maySeeOtherVehicleDamagedDevices = False
        cdWnd = vehicles.HORN_COOLDOWN.WINDOW + vehicles.HORN_COOLDOWN.CLIENT_WINDOW_EXPANSION
        self.__hornCooldown = HornCooldown.HornCooldown(cdWnd, vehicles.HORN_COOLDOWN.MAX_SIGNALS)
        BigWorld.wg_setBatchingEnabled(self.arena.arenaType.batchingEnabled)
        if not BattleReplay.isPlaying():
            self.intUserSettings.onProxyBecomePlayer()
            self.syncData.onAvatarBecomePlayer()
        g_playerEvents.onAvatarBecomePlayer()
        SoundGroups.g_instance.loadRemapping(self.arena.arenaType)
        MusicController.g_musicController.stopAmbient()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_COMBAT_LOADING)
        self.__staticCollisionEffectID = None
        self.__drownWarningLevel = DROWN_WARNING_LEVEL.SAFE
        BigWorld.wg_clearDecals()
        return

    def onBecomeNonPlayer(self):
        LOG_DEBUG('Avatar.onBecomeNonPlayer()')
        chatManager.switchPlayerProxy(None)
        g_playerEvents.onAvatarBecomeNonPlayer()
        self.onVehicleEnterWorld.clear()
        self.onVehicleEnterWorld = None
        self.onVehicleLeaveWorld.clear()
        self.onVehicleLeaveWorld = None
        self.__vehicleToVehicleCollisions = None
        BigWorld.wg_clearDecals()
        if not BattleReplay.isPlaying():
            self.intUserSettings.onProxyBecomeNonPlayer()
            self.syncData.onAvatarBecomeNonPlayer()
            self.intUserSettings.setProxy(None, None)
        return

    def onEnterWorld(self, prereqs):
        LOG_DEBUG('Avatar.onEnterWorld()')
        list = []
        for p in set(self.__prereqs):
            try:
                list.append(prereqs[p])
            except Exception as e:
                LOG_WARNING('Resource is not found', p)

        self.__prereqs = list
        self.gunRotator = VehicleGunRotator.VehicleGunRotator(self)
        self.positionControl = AvatarPositionControl.AvatarPositionControl(self)
        BigWorld.target.caps(1)
        self.__onInitStepCompleted()
        if self.playerVehicleID != 0:
            self.set_playerVehicleID(0)
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            VOIP.getVOIPManager().setMicMute(True)
        from helpers import EdgeDetectColorController
        EdgeDetectColorController.g_instance.updateColors()
        from helpers import statistics
        statistics.g_statistics.start()

    def onLeaveWorld(self):
        LOG_DEBUG('Avatar.onLeaveWorld()')
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.stop()
        if self.__tryShootCallbackId:
            BigWorld.cancelCallback(self.__tryShootCallbackId)
            self.__tryShootCallbackId = None
        MusicController.g_musicController.onLeaveArena()
        TriggersManager.g_manager.enable(False)
        BigWorld.wg_setEntityUnloadable(self.playerVehicleID, False)
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_setAmbientReverb('')
        BigWorld.target.clear()
        from helpers import statistics
        statistics.g_statistics.stop()
        for v in BigWorld.entities.values():
            if isinstance(v, Vehicle.Vehicle) and v.isStarted:
                self.onVehicleLeaveWorld(v)
                v.stopVisual()

        if self.__setOwnVehicleMatrixTimerID is not None:
            BigWorld.cancelCallback(self.__setOwnVehicleMatrixTimerID)
            self.__setOwnVehicleMatrixTimerID = None
        if self.__shotWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__shotWaitingTimerID)
            self.__shotWaitingTimerID = None
        if self.__fireNonFatalDamageTriggerID is not None:
            BigWorld.cancelCallback(self.__fireNonFatalDamageTriggerID)
            self.__fireNonFatalDamageTriggerID = None
        try:
            self.__stippleMgr.destroy()
            self.__stippleMgr = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            if hasattr(self, 'gunRotator') and self.gunRotator is not None:
                self.gunRotator.destroy()
                self.gunRotator = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        if self.__stepsTillInit == 0:
            try:
                self.__destroyGUI()
                SoundGroups.g_instance.enableArenaSounds(False)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.__stepsTillInit = None
        try:
            self.__projectileMover.destroy()
            self.__projectileMover = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            self.terrainEffects.destroy()
            self.terrainEffects = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            self.arena.destroy()
            self.arena = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            self.positionControl.destroy()
            self.positionControl = None
        except:
            LOG_CURRENT_EXCEPTION()

        try:
            for hitTester in self.hitTesters:
                hitTester.releaseBspModel()

        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            vehicles.g_cache.clearPrereqs()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        AreaDestructibles.clear()
        self.__ownVehicleMProv.target = None
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            VOIP.getVOIPManager().setMicMute(True)
        SoundGroups.g_instance.soundModes.setMode(SoundGroups.SoundModes.DEFAULT_MODE_NAME)
        return

    def onSpaceLoaded(self):
        LOG_DEBUG('onSpaceLoaded()')
        self.__applyTimeAndWeatherSettings()
        self.__onInitStepCompleted()

    def onStreamComplete(self, id, desc, data):
        isCorrupted, origPacketLen, packetLen, origCrc32, crc32 = desc
        if isCorrupted:
            self.base.logStreamCorruption(id, origPacketLen, packetLen, origCrc32, crc32)
        if BattleReplay.g_replayCtrl.isRecording:
            if id >= STREAM_ID_CHAT_MIN and id <= STREAM_ID_CHAT_MAX:
                BattleReplay.g_replayCtrl.cancelSaveCurrMessage()
        callback = self.__rangeStreamIDCallbacks.getCallbackForStreamID(id)
        if callback is not None:
            getattr(self, callback)(id, data)
            return
        else:
            callback = self.__onStreamCompletePredef.get(id, None)
            if callback is not None:
                getattr(self, callback)(True, data)
                return
            return

    def onCmdResponse(self, requestID, resultID, errorStr):
        LOG_DEBUG('onCmdResponse requestID=%s, resultID=%s, errorStr=%s' % (requestID, resultID, errorStr))
        callback = self.__onCmdResponse.pop(requestID, None)
        if callback is not None:
            callback(requestID, resultID, errorStr)
        return

    def onIGRTypeChanged(self, data):
        try:
            data = cPickle.loads(data)
            g_playerEvents.onIGRTypeChanged(data.get('roomType'), data.get('igrXPFactor'))
        except Exception:
            LOG_ERROR('Error while unpickling igr data information', data)

    def handleKeyEvent(self, event):
        return False

    def handleKey(self, isDown, key, mods):
        if not self.userSeesWorld():
            return False
        else:
            time = BigWorld.time()
            cmdMap = CommandMapping.g_instance
            try:
                isDoublePress = False
                if isDown:
                    if self.__lastTimeOfKeyDown == -1:
                        self.__lastTimeOfKeyDown = 0
                    if key == self.__lastKeyDown and time - self.__lastTimeOfKeyDown < 0.35:
                        self.__numSimilarKeyDowns = self.__numSimilarKeyDowns + 1
                        isDoublePress = True if self.__numSimilarKeyDowns == 2 else False
                    else:
                        self.__numSimilarKeyDowns = 1
                    self.__lastKeyDown = key
                    self.__lastTimeOfKeyDown = time
                if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and constants.IS_DEVELOPMENT:
                    if key == Keys.KEY_ESCAPE:
                        self.__setVisibleGUI(not self.__isGuiVisible)
                        return True
                    if key == Keys.KEY_1:
                        self.base.setDevelopmentFeature('heal', 0)
                        return True
                    if key == Keys.KEY_2:
                        self.base.setDevelopmentFeature('reload_gun', 0)
                        return True
                    if key == Keys.KEY_3:
                        self.base.setDevelopmentFeature('start_fire', 0)
                        return True
                    if key == Keys.KEY_4:
                        self.base.setDevelopmentFeature('explode', 0)
                        return True
                    if key == Keys.KEY_5:
                        self.base.setDevelopmentFeature('break_left_track', 0)
                        return True
                    if key == Keys.KEY_6:
                        self.base.setDevelopmentFeature('break_right_track', 0)
                        return True
                    if key == Keys.KEY_7:
                        self.base.setDevelopmentFeature('destroy_self', True)
                    if key == Keys.KEY_9:
                        BigWorld.setWatcher('Render/Spots/draw', BigWorld.getWatcher('Render/Spots/draw') == 'false')
                        return True
                    if key == Keys.KEY_F:
                        vehicle = BigWorld.entity(self.playerVehicleID)
                        vehicle.filter.enableClientFilters = not vehicle.filter.enableClientFilters
                        return True
                    if key == Keys.KEY_G:
                        self.moveVehicle(1, True)
                        return True
                    if key == Keys.KEY_R:
                        self.base.setDevelopmentFeature('pickup', 0)
                        return True
                    if key == Keys.KEY_T:
                        self.base.setDevelopmentFeature('log_tkill_ratings', 0)
                        return True
                    if key == Keys.KEY_N:
                        self.isTeleport = not self.isTeleport
                        return True
                if constants.IS_DEVELOPMENT and cmdMap.isFired(CommandMapping.CMD_SWITCH_SERVER_MARKER, key) and isDown:
                    self.gunRotator.showServerMarker = not self.gunRotator.showServerMarker
                    return True
                if not self.__isForcedGuiControlMode and cmdMap.isFired(CommandMapping.CMD_TOGGLE_GUI, key) and isDown:
                    self.__setVisibleGUI(not self.__isGuiVisible)
                if constants.IS_DEVELOPMENT and isDown:
                    if key == Keys.KEY_B and mods == 0:
                        g_windowsManager.showBotsMenu()
                        return True
                    if key == Keys.KEY_H and mods != 0:
                        import Cat
                        Cat.Tasks.VehicleModels.VehicleModelsObject.switchVisualState()
                        return True
                    if key == Keys.KEY_I and mods == 0:
                        import Cat
                        if Cat.Tasks.ScreenInfo.ScreenInfoObject.getVisible():
                            Cat.Tasks.ScreenInfo.ScreenInfoObject.setVisible(False)
                        else:
                            Cat.Tasks.ScreenInfo.ScreenInfoObject.setVisible(True)
                        return True
                if cmdMap.isFired(CommandMapping.CMD_INCREMENT_CRUISE_MODE, key) and isDown and not self.__isForcedGuiControlMode:
                    if self.__stopUntilFire:
                        self.__stopUntilFire = False
                        self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                    if isDoublePress:
                        newMode = _CRUISE_CONTROL_MODE.FWD100
                    else:
                        newMode = self.__cruiseControlMode + 1
                        newMode = min(newMode, _CRUISE_CONTROL_MODE.FWD100)
                    if newMode != self.__cruiseControlMode:
                        self.__cruiseControlMode = newMode
                        if not cmdMap.isActiveList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD)):
                            self.moveVehicle(self.makeVehicleMovementCommandByKeys(), isDown)
                    self.__updateCruiseControlPanel()
                    return True
                if cmdMap.isFired(CommandMapping.CMD_DECREMENT_CRUISE_MODE, key) and isDown and not self.__isForcedGuiControlMode:
                    if self.__stopUntilFire:
                        self.__stopUntilFire = False
                        self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                    if isDoublePress:
                        newMode = _CRUISE_CONTROL_MODE.BCKW100
                    else:
                        newMode = self.__cruiseControlMode - 1
                        newMode = max(newMode, _CRUISE_CONTROL_MODE.BCKW100)
                    if newMode != self.__cruiseControlMode:
                        self.__cruiseControlMode = newMode
                        if not cmdMap.isActiveList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD)):
                            self.moveVehicle(self.makeVehicleMovementCommandByKeys(), isDown)
                    self.__updateCruiseControlPanel()
                    return True
                if cmdMap.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD), key) and isDown and not self.__isForcedGuiControlMode:
                    self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                    self.__updateCruiseControlPanel()
                if cmdMap.isFired(CommandMapping.CMD_STOP_UNTIL_FIRE, key) and isDown and not self.__isForcedGuiControlMode:
                    if not self.__stopUntilFire:
                        self.__stopUntilFire = True
                        self.__stopUntilFireStartTime = time
                    else:
                        self.__stopUntilFire = False
                    self.moveVehicle(self.makeVehicleMovementCommandByKeys(), isDown)
                    self.__updateCruiseControlPanel()
                if cmdMap.isFiredList((CommandMapping.CMD_MOVE_FORWARD,
                 CommandMapping.CMD_MOVE_FORWARD_SPEC,
                 CommandMapping.CMD_MOVE_BACKWARD,
                 CommandMapping.CMD_ROTATE_LEFT,
                 CommandMapping.CMD_ROTATE_RIGHT), key):
                    if self.__stopUntilFire and isDown and not self.__isForcedGuiControlMode:
                        self.__stopUntilFire = False
                        self.__updateCruiseControlPanel()
                    if not self.__isForcedGuiControlMode:
                        self.moveVehicle(self.makeVehicleMovementCommandByKeys(), isDown)
                    return True
                if not self.__isForcedGuiControlMode and cmdMap.isFiredList(xrange(CommandMapping.CMD_AMMO_CHOICE_1, CommandMapping.CMD_AMMO_CHOICE_0 + 1), key) and isDown and mods == 0:
                    g_windowsManager.battleWindow.consumablesPanel.handleKey(key)
                    return True
                if cmdMap.isFiredList((CommandMapping.CMD_CHAT_SHORTCUT_ATTACK,
                 CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE,
                 CommandMapping.CMD_CHAT_SHORTCUT_FOLLOWME,
                 CommandMapping.CMD_CHAT_SHORTCUT_POSITIVE,
                 CommandMapping.CMD_CHAT_SHORTCUT_NEGATIVE,
                 CommandMapping.CMD_CHAT_SHORTCUT_HELPME,
                 CommandMapping.CMD_CHAT_SHORTCUT_RELOAD,
                 CommandMapping.CMD_RADIAL_MENU_SHOW), key) and self.__isVehicleAlive:
                    if self.inputHandler.aim is not None:
                        g_windowsManager.battleWindow.radialMenu.handleKey(key, isDown, self.inputHandler.aim.offset())
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VEHICLE_MARKERS_SHOW_INFO, key):
                    g_windowsManager.battleWindow.vMarkersManager.showExtendedInfo(isDown)
                    g_windowsManager.battleWindow.minimap.onAltPress(isDown)
                    return True
                if key == Keys.KEY_F1 and isDown and mods == 0:
                    g_windowsManager.battleWindow.toggleHelpWindow()
                    return True
                if key == Keys.KEY_F12 and isDown and mods == 0:
                    self.__dumpVehicleState()
                    return True
                if key == Keys.KEY_F12 and isDown and mods == 2:
                    self.__reportLag()
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VOICECHAT_MUTE, key):
                    LOG_DEBUG('onVoiceChatPTT', isDown)
                    if VOIP.getVOIPManager().getCurrentChannel():
                        VOIP.getVOIPManager().setMicMute(not isDown)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_USE_HORN, key) and isDown:
                    self.useHorn(True)
                    return True
                if self.isHornActive() and self.hornMode() != 'oneshot' and not cmdMap.isActive(CommandMapping.CMD_USE_HORN):
                    self.useHorn(False)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_LOGITECH_SWITCH_VIEW, key) and isDown:
                    LOG_DEBUG('LOGITECH SWICH VIEW', isDown)
                    from gui.Scaleform.LogitechMonitor import LogitechMonitor
                    LogitechMonitor.onChangeView()
                if not self.__isForcedGuiControlMode and g_sessionProvider.getDrrScaleCtrl().handleKey(key, isDown):
                    return True
                if not self.__isForcedGuiControlMode and cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP, CommandMapping.CMD_MINIMAP_VISIBLE), key) and isDown:
                    g_windowsManager.battleWindow.minimap.handleKey(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_RELOAD_PARTIAL_CLIP, key) and isDown:
                    g_sessionProvider.getAmmoCtrl().reloadPartialClip(self)
                    return True
            except Exception:
                LOG_CURRENT_EXCEPTION()
                return True

            return False

    def set_playerVehicleID(self, prev):
        LOG_DEBUG('Avatar.set_playerVehicleID()', self.playerVehicleID)
        BigWorld.wg_setEntityUnloadable(self.playerVehicleID, True)
        self.__onInitStepCompleted()
        ownVehicle = BigWorld.entity(self.playerVehicleID)
        if ownVehicle is not None and ownVehicle.inWorld and not ownVehicle.isPlayer:
            ownVehicle.isPlayer = True
            self.vehicleTypeDescriptor = ownVehicle.typeDescriptor
            g_sessionProvider.setPlayerVehicle(self.vehicleTypeDescriptor)
            self.__onInitStepCompleted()
        return

    def set_isGunLocked(self, prev):
        if self.isGunLocked:
            self.gunRotator.lock(True)
            if not isinstance(self.inputHandler.ctrl, ArcadeControlMode) and not isinstance(self.inputHandler.ctrl, VideoCameraControlMode):
                self.inputHandler.setAimingMode(False, AIMING_MODE.USER_DISABLED)
                self.inputHandler.onControlModeChanged('arcade', preferredPos=self.inputHandler.getDesiredShotPoint())
        else:
            self.gunRotator.lock(False)

    def set_isOwnVehicleContactingWorld(self, prev):
        pass

    def targetBlur(self, prevEntity):
        if not isinstance(prevEntity, Vehicle.Vehicle):
            return
        if self.inputHandler.aim:
            self.inputHandler.aim.clearTarget()
        TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AIM_AT_VEHICLE)
        BigWorld.wgDelEdgeDetectEntity(prevEntity)
        if self.__maySeeOtherVehicleDamagedDevices:
            self.cell.monitorVehicleDamagedDevices(0)
            g_windowsManager.battleWindow.damageInfoPanel.hide()

    def targetFocus(self, entity):
        if not isinstance(entity, Vehicle.Vehicle):
            return
        else:
            if self.inputHandler.aim:
                self.inputHandler.aim.setTarget(entity)
            isInTutorial = self.arena is not None and self.arena.guiType == constants.ARENA_GUI_TYPE.TUTORIAL
            if (self.__isGuiVisible or isInTutorial) and entity.isAlive():
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.AIM_AT_VEHICLE, vehicleId=entity.id)
                if self.team == entity.publicInfo['team']:
                    BigWorld.wgAddEdgeDetectEntity(entity, 2)
                else:
                    BigWorld.wgAddEdgeDetectEntity(entity, 1)
                if self.__maySeeOtherVehicleDamagedDevices:
                    self.cell.monitorVehicleDamagedDevices(entity.id)
            return

    def reload(self):
        self.__reloadGUI()
        self.inputHandler.setReloading(0.0)

    def vehicle_onEnterWorld(self, vehicle):
        self.__stippleMgr.hideIfExistFor(vehicle)
        if vehicle.id != self.playerVehicleID:
            vehicle.targetCaps = [1]
        else:
            LOG_DEBUG('Avatar.vehicle_onEnterWorld(): own vehicle', vehicle.id)
            vehicle.isPlayer = True
            if self.__stepsTillInit != 0:
                self.vehicleTypeDescriptor = vehicle.typeDescriptor
                g_sessionProvider.setPlayerVehicle(self.vehicleTypeDescriptor)
                if vehicle.typeDescriptor.turret['ceilless'] is not None:
                    FMOD.setEventsParam('ceilless', 1 if vehicle.typeDescriptor.turret['ceilless'] else 0)
                else:
                    FMOD.setEventsParam('ceilless', 0)
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    m = vehicle.filter.bodyMatrix
                else:
                    m = vehicle.matrix
                self.__ownVehicleMProv.setStaticTransform(Math.Matrix(m))
                self.__onInitStepCompleted()
            else:
                vehicle.typeDescriptor.activeGunShotIndex = self.vehicleTypeDescriptor.activeGunShotIndex
                if self.inputHandler.aim:
                    self.inputHandler.aim.resetVehicleMatrix()
        if self.__stepsTillInit == 0 and not vehicle.isStarted:
            vehicle.startVisual()
            self.onVehicleEnterWorld(vehicle)
        return

    def vehicle_onLeaveWorld(self, vehicle):
        if not vehicle.isStarted:
            return
        else:
            self.onVehicleLeaveWorld(vehicle)
            vehicle.stopVisual()
            model = vehicle.model
            vehicle.model = None
            self.__stippleMgr.showFor(vehicle, model)
            return

    def prerequisites(self):
        if hasattr(self, '_PlayerAvatar__prereqs'):
            return ()
        SoundGroups.g_instance.enableArenaSounds(False)
        self.__prereqs = []
        self.__fakeModelName = Settings.g_instance.scriptConfig.readString(Settings.KEY_FAKE_MODEL)
        if self.__fakeModelName:
            self.__prereqs.append(self.__fakeModelName)
        else:
            LOG_ERROR("The '%s' is missing or empty in '%s'" % (Settings.KEY_FAKE_MODEL, Settings.g_instance.scriptConfig.name))
        self.terrainEffects = bound_effects.StaticSceneBoundEffects()
        self.__projectileMover = ProjectileMover.ProjectileMover()
        self.__prereqs += self.__initGUI()
        self.__prereqs += g_postProcessing.prerequisites()
        return self.__prereqs

    def initSpace(self):
        if not self.__isSpaceInitialized:
            self.__isSpaceInitialized = True

    def userSeesWorld(self):
        return self.__stepsTillInit == 0

    def newFakeModel(self):
        return BigWorld.Model(self.__fakeModelName)

    def requestToken(self, requestID, tokenType):
        self.base.requestToken(requestID, tokenType)

    def onTokenReceived(self, requestID, tokenType, data):
        if Account.g_accountRepository is not None:
            Account.g_accountRepository.onTokenReceived(requestID, tokenType, data)
        return

    def onKickedFromServer(self, reason, isBan, expiryTime):
        LOG_MX('onKickedFromServer', reason, isBan, expiryTime)
        from helpers import statistics
        statistics.g_statistics.reset()
        import BattleReplay
        if not BattleReplay.isPlaying():
            from gui import DialogsInterface
            DialogsInterface.showDisconnect(reason, isBan, expiryTime)

    def onAutoAimVehicleLost(self):
        autoAimVehID = self.__autoAimVehID
        self.__autoAimVehID = 0
        self.inputHandler.setAimingMode(False, AIMING_MODE.TARGET_LOCK)
        self.gunRotator.clientMode = True
        if autoAimVehID and autoAimVehID not in self.__frags:
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.onLockTarget(2)
            self.soundNotifications.play('target_lost')

    def updateVehicleHealth(self, health, isCrewActive):
        rawHealth = health
        health = max(0, health)
        isAlive = health > 0 and isCrewActive
        wasAlive = self.__isVehicleAlive
        self.__isVehicleAlive = isAlive
        aim = self.inputHandler.aim
        if aim:
            aim.setHealth(health)
        g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HEALTH, health)
        if not isAlive and wasAlive:
            self.gunRotator.stop()
            if health > 0 and not isCrewActive:
                self.soundNotifications.play('crew_deactivated')
                self.__deviceStates = {'crew': 'destroyed'}
                g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CREW_DEACTIVATED, None)
            elif not g_sessionProvider.getCtx().isObserver(self.playerVehicleID):
                self.soundNotifications.play('vehicle_destroyed')
                self.__deviceStates = {'vehicle': 'destroyed'}
                g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DESTROYED, None)
            self.inputHandler.activatePostmortem()
            g_sessionProvider.switchToPostmortem()
            self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
            self.__updateCruiseControlPanel()
            self.__stopUntilFire = False
            if rawHealth <= 0:
                vehicle = BigWorld.entities.get(self.playerVehicleID)
                if vehicle is not None:
                    prevHealth = vehicle.health
                    vehicle.health = rawHealth
                    vehicle.set_health(prevHealth)
        return

    def updateVehicleGunReloadTime(self, vehicleID, timeLeft, baseTime):
        if vehicleID != self.playerVehicleID:
            if not self.__isVehicleAlive and vehicleID == self.inputHandler.ctrl.curVehicleID:
                aim = self.inputHandler.aim
                if aim is not None:
                    aim.updateAmmoState(timeLeft != -2)
            return
        else:
            self.__gunReloadCommandWaitEndTime = 0.0
            if self.__prevGunReloadTimeLeft != timeLeft and timeLeft == 0.0:
                self.soundNotifications.play('gun_reloaded')
                VibroReloadController()
            self.__prevGunReloadTimeLeft = timeLeft
            if timeLeft < 0.0:
                timeLeft = -1
            g_sessionProvider.getAmmoCtrl().setGunReloadTime(timeLeft, baseTime)
            return

    def updateVehicleAmmo(self, compactDescr, quantity, quantityInClip, timeRemaining):
        if not compactDescr:
            itemTypeIdx = ITEM_TYPE_INDICES['equipment']
        else:
            itemTypeIdx = getTypeOfCompactDescr(compactDescr)
        processor = self.__updateConsumablesProcessors.get(itemTypeIdx)
        if processor:
            getattr(self, processor)(compactDescr, quantity, quantityInClip, timeRemaining)
        else:
            LOG_WARNING('Not supported item type index', itemTypeIdx)

    __updateConsumablesProcessors = {ITEM_TYPE_INDICES['shell']: '_PlayerAvatar__processVehicleAmmo',
     ITEM_TYPE_INDICES['equipment']: '_PlayerAvatar__processVehicleEquipments'}

    def updateVehicleOptionalDeviceStatus(self, deviceID, isOn):
        g_sessionProvider.getOptDevicesCtrl().setOptionalDevice(deviceID, isOn)

    def updateVehicleMiscStatus(self, vehicleID, code, intArg, floatArg):
        if vehicleID != self.playerVehicleID and (self.__isVehicleAlive or vehicleID != self.inputHandler.ctrl.curVehicleID):
            return
        else:
            STATUS = VEHICLE_MISC_STATUS
            if code == STATUS.DESTROYED_DEVICE_IS_REPAIRING:
                extraIndex = intArg & 255
                progress = (intArg & 65280) >> 8
                LOG_DEBUG_DEV('DESTROYED_DEVICE_IS_REPAIRING (%s): %s%%, %s sec' % (self.vehicleTypeDescriptor.extras[extraIndex].name, progress, floatArg))
                if g_windowsManager.battleWindow is not None:
                    damagePanel = g_windowsManager.battleWindow.damagePanel
                    damagePanel.updateModuleRepair(self.vehicleTypeDescriptor.extras[extraIndex].name[:-len('Health')], progress, floatArg)
            elif code == STATUS.OTHER_VEHICLE_DAMAGED_DEVICES_VISIBLE:
                prevVal = self.__maySeeOtherVehicleDamagedDevices
                newVal = bool(intArg)
                self.__maySeeOtherVehicleDamagedDevices = newVal
                if not prevVal and newVal:
                    target = BigWorld.target()
                    if target is not None and isinstance(target, Vehicle.Vehicle):
                        self.cell.monitorVehicleDamagedDevices(target.id)
            elif code == STATUS.VEHICLE_IS_OVERTURNED:
                self.updateVehicleDestroyTimer(code, floatArg)
            elif code == STATUS.IN_DEATH_ZONE:
                self.updateVehicleDestroyTimer(code, floatArg)
            elif code == STATUS.VEHICLE_DROWN_WARNING:
                self.updateVehicleDestroyTimer(code, floatArg, intArg)
            elif code == STATUS.IS_OBSERVED_BY_ENEMY:
                if g_windowsManager.battleWindow is not None:
                    g_windowsManager.battleWindow.showSixthSenseIndicator(True)
            elif code == STATUS.LOADER_INTUITION_WAS_USED:
                self.soundNotifications.play('gun_intuition')
                if g_windowsManager.battleWindow is not None:
                    g_windowsManager.battleWindow.vMsgsPanel.showMessage('LOADER_INTUITION_WAS_USED')
                g_sessionProvider.getAmmoCtrl().useLoaderIntuition()
            elif code == STATUS.HORN_BANNED:
                self.__hornCooldown.ban(floatArg)
            return

    def updateVehicleSetting(self, code, value):
        if code == VEHICLE_SETTING.CURRENT_SHELLS:
            ammoCtrl = g_sessionProvider.getAmmoCtrl()
            if not ammoCtrl.setCurrentShellCD(value):
                return
            shotIdx = ammoCtrl.getGunSettings().getShotIndex(value)
            if shotIdx > -1:
                self.vehicleTypeDescriptor.activeGunShotIndex = shotIdx
                vehicle = BigWorld.entity(self.playerVehicleID)
                if vehicle is not None:
                    vehicle.typeDescriptor.activeGunShotIndex = shotIdx
                self.onGunShotChanged()
            return
        elif code == VEHICLE_SETTING.NEXT_SHELLS:
            g_sessionProvider.getAmmoCtrl().setNextShellCD(value)
            return
        else:
            LOG_CODEPOINT_WARNING(code, value)
            return

    def updateTargetingInfo(self, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed, shotDispMultiplierFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime):
        aimingInfo = self.__aimingInfo
        aimingInfo[2] = shotDispMultiplierFactor
        aimingInfo[3] = gunShotDispersionFactorsTurretRotation
        aimingInfo[4] = chassisShotDispersionFactorsMovement
        aimingInfo[5] = chassisShotDispersionFactorsRotation
        aimingInfo[6] = aimingTime
        if hasattr(self, 'gunRotator') and self.gunRotator is not None:
            self.gunRotator.update(turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed)
        self.getOwnVehicleShotDispersionAngle(self.gunRotator.turretRotationSpeed)
        return

    def updateGunMarker(self, shotPos, shotVec, dispersionAngle):
        self.gunRotator.setShotPosition(shotPos, shotVec, dispersionAngle)

    def updateOwnVehiclePosition(self, position, direction, speed, rspeed):
        if self.__setOwnVehicleMatrixTimerID is not None:
            BigWorld.cancelCallback(self.__setOwnVehicleMatrixTimerID)
            self.__setOwnVehicleMatrixTimerID = None
        m = Math.Matrix()
        m.setRotateYPR(direction)
        m.translation = position
        self.__ownVehicleMProv.setStaticTransform(m)
        self.__lastVehicleSpeeds = (speed, rspeed)
        BigWorld.wg_setOutAoIEntityParams(self.playerVehicleID, position, direction)
        self.__ownVehicleMProv.target = None
        self.__setOwnVehicleMatrixTimerID = BigWorld.callback(SERVER_TICK_LENGTH / 10, self.__setOwnVehicleMatrixCallback)
        return

    def updateVehicleDestroyTimer(self, code, time, warnLvl = None):
        if g_windowsManager.battleWindow is not None:
            if warnLvl is None:
                if time > 0:
                    g_windowsManager.battleWindow.showVehicleTimer(code, time)
                else:
                    g_windowsManager.battleWindow.hideVehicleTimer(code)
            elif warnLvl == DROWN_WARNING_LEVEL.DANGER:
                g_windowsManager.battleWindow.showVehicleTimer(code, time, 'critical')
            elif warnLvl == DROWN_WARNING_LEVEL.CAUTION:
                g_windowsManager.battleWindow.showVehicleTimer(code, 0, 'warning')
            else:
                g_windowsManager.battleWindow.hideVehicleTimer(code)
        return

    def showOwnVehicleHitDirection(self, hitDirYaw, isDamage):
        if self.inputHandler.aim is not None:
            self.inputHandler.aim.showHit(hitDirYaw, isDamage)
        return

    def showVehicleDamageInfo(self, vehicleID, damageIndex, extraIndex, entityID):
        damageCode = constants.DAMAGE_INFO_CODES[damageIndex]
        extra = self.vehicleTypeDescriptor.extras[extraIndex] if extraIndex != 0 else None
        if vehicleID == self.playerVehicleID or not self.__isVehicleAlive and vehicleID == self.inputHandler.ctrl.curVehicleID:
            self.__showDamageIconAndPlaySound(damageCode, extra)
        if damageCode not in self.__damageInfoNoNotification:
            self.battleMessages.showVehicleDamageInfo(damageCode, entityID, extra)
        return

    def showShotResults(self, results):
        arenaVehicles = self.arena.vehicles
        VHF = VEHICLE_HIT_FLAGS
        enemies = {}
        burningEnemies = []
        damagedAllies = []
        hasKill = False
        for r in results:
            vehicleID = r & 4294967295L
            flags = r >> 32 & 4294967295L
            if flags & VHF.VEHICLE_WAS_DEAD_BEFORE_ATTACK:
                continue
            if flags & VHF.VEHICLE_KILLED:
                hasKill = True
                continue
            if self.team == arenaVehicles[vehicleID]['team'] and self.playerVehicleID != vehicleID:
                if flags & (VHF.IS_ANY_DAMAGE_MASK | VHF.ATTACK_IS_DIRECT_PROJECTILE):
                    damagedAllies.append(vehicleID)
            else:
                enemies[vehicleID] = enemies.get(vehicleID, 0) | flags
                if flags & VHF.FIRE_STARTED:
                    burningEnemies.append(vehicleID)

        for vehicleID in damagedAllies:
            g_windowsManager.battleWindow.pMsgsPanel.showMessage('ALLY_HIT', {'entity': g_sessionProvider.getCtx().getFullPlayerName(vID=vehicleID)}, extra=(('entity', vehicleID),))

        if hasKill:
            return
        else:
            bestSound = None
            for vehicleID, flags in enemies.iteritems():
                if flags & VHF.IS_ANY_PIERCING_MASK:
                    self.__fireNonFatalDamageTriggerID = BigWorld.callback(0.5, lambda : self.__fireNonFatalDamageTrigger(vehicleID))
                sound = None
                if flags & VHF.ATTACK_IS_EXTERNAL_EXPLOSION:
                    if flags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                        sound = 'enemy_hp_damaged_by_near_explosion_by_player'
                    elif flags & VHF.IS_ANY_PIERCING_MASK:
                        sound = 'enemy_no_hp_damage_by_near_explosion_by_player'
                else:
                    raise flags & VHF.ATTACK_IS_DIRECT_PROJECTILE or AssertionError
                    if flags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE:
                        if flags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                            sound = 'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player'
                        elif flags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                            sound = 'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player'
                        else:
                            sound = 'enemy_hp_damaged_by_projectile_by_player'
                    elif flags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                        sound = 'enemy_hp_damaged_by_explosion_at_direct_hit_by_player'
                    elif flags & VHF.RICOCHET and not flags & VHF.DEVICE_PIERCED_BY_PROJECTILE:
                        sound = 'enemy_ricochet_by_player'
                        if len(enemies) == 1:
                            TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_RICOCHET, targetId=vehicleID)
                    elif flags & VHF.MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_BY_PROJECTILE:
                        if flags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                            sound = 'enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player'
                        elif flags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                            sound = 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player'
                        else:
                            sound = 'enemy_no_hp_damage_at_attempt_by_player'
                            if len(enemies) == 1:
                                TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=vehicleID)
                    elif flags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                        sound = 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player'
                    elif flags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                        sound = 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player'
                    else:
                        if flags & VHF.IS_ANY_PIERCING_MASK:
                            sound = 'enemy_no_hp_damage_at_no_attempt_by_player'
                        else:
                            sound = 'enemy_no_piercing_by_player'
                        if len(enemies) == 1:
                            TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=vehicleID)
                if sound is not None:
                    bestSound = _getBestShotResultSound(bestSound, sound, vehicleID)

            if bestSound is not None:
                self.soundNotifications.play(bestSound[0], bestSound[1])
            for vehicleID in burningEnemies:
                self.soundNotifications.play('enemy_fire_started_by_player', vehicleID)

            return

    def showOtherVehicleDamagedDevices(self, vehicleID, damagedExtras, destroyedExtras):
        target = BigWorld.target()
        if target is None or not isinstance(target, Vehicle.Vehicle):
            if self.__maySeeOtherVehicleDamagedDevices and vehicleID != 0:
                self.cell.monitorVehicleDamagedDevices(0)
            return
        elif target.id == vehicleID:
            g_windowsManager.battleWindow.damageInfoPanel.show(vehicleID, damagedExtras, destroyedExtras)
            return
        else:
            if self.__maySeeOtherVehicleDamagedDevices:
                self.cell.monitorVehicleDamagedDevices(target.id)
            g_windowsManager.battleWindow.damageInfoPanel.hide()
            return

    def showDevelopmentInfo(self, code, arg):
        params = cPickle.loads(arg)
        if code == DEVELOPMENT_INFO.BONUSES:
            if constants.IS_DEVELOPMENT:
                if self.playerBonusesPanel is not None:
                    self.playerBonusesPanel.setVisible(True)
                    self.playerBonusesPanel.setContent(params)
        elif code == DEVELOPMENT_INFO.VISIBILITY:
            if constants.IS_DEVELOPMENT:
                import Cat
                Cat.Tasks.VisibilityTest.VisibilityTestObject.setContent(params)
        elif code == DEVELOPMENT_INFO.VEHICLE_ATTRS:
            if constants.IS_DEVELOPMENT:
                attrs = cPickle.loads(arg)
                LOG_DEBUG('circularVisionRadius: %s' % attrs['circularVisionRadius'])
        else:
            LOG_MX('showDevelopmentInfo', code, params)
        return

    def showTracer(self, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist):
        if not self.userSeesWorld():
            return
        else:
            startPoint = refStartPoint
            shooter = BigWorld.entity(shooterID)
            if not isRicochet and shooter is not None and shooter.isStarted:
                gunMatrix = Math.Matrix(shooter.appearance.modelsDesc['gun']['model'].node('HP_gunFire'))
                gunFirePos = gunMatrix.translation
                if cameras.isPointOnScreen(gunFirePos):
                    startPoint = gunFirePos
                    replayCtrl = BattleReplay.g_replayCtrl
                    if (gunFirePos - refStartPoint).length > 50.0 and (gunFirePos - BigWorld.camera().position).length < 50.0 and replayCtrl.isPlaying:
                        velocity = velocity.length * gunMatrix.applyVector((0, 0, 1))
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            isOwnShoot = self.playerVehicleID == shooterID
            self.__projectileMover.add(shotID, effectsDescr, gravity, refStartPoint, velocity, startPoint, maxShotDist, isOwnShoot, BigWorld.camera().position)
            if isRicochet:
                self.__projectileMover.hold(shotID)
            return

    def stopTracer(self, shotID, endPoint):
        if self.userSeesWorld():
            self.__projectileMover.hide(shotID, endPoint)

    def explodeProjectile(self, shotID, effectsIndex, effectMaterialIndex, endPoint, velocityDir, damagedDestructibles):
        if self.userSeesWorld():
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            effectMaterial = EFFECT_MATERIALS[effectMaterialIndex]
            self.__projectileMover.explode(shotID, effectsDescr, effectMaterial, endPoint, velocityDir)
            physParams = effectsDescr['physicsParams']
            if damagedDestructibles:
                damagedDestructibles = [ (int(code >> 16), int(code >> 8 & 255), int(code & 255)) for code in damagedDestructibles ]
                velocityDir.normalise()
                explInfo = (endPoint,
                 velocityDir,
                 physParams['shellVelocity'],
                 physParams['shellMass'],
                 physParams['splashRadius'],
                 physParams['splashStrength'])
                AreaDestructibles.g_destructiblesManager.onProjectileExploded(explInfo, damagedDestructibles)
            else:
                BigWorld.wg_havokExplosion(endPoint, physParams['splashStrength'], physParams['splashRadius'])

    def onRoundFinished(self, winnerTeam, reason):
        LOG_MX('onRoundFinished', winnerTeam, reason)

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        g_playerEvents.onKickedFromArena(reasonCode)

    def onScoutEvent(self, eventType, reportedID):
        LOG_DEBUG('onScoutEvent, eventType = %s, reportedID = %s' % (eventType, reportedID))
        msgType = ''
        if eventType == SCOUT_EVENT_TYPE.SPOTTED:
            self.complexSoundNotifications.notifyEnemySpotted(reportedID == 0)
            msgType = 'ENEMY_SPOTTED'
        elif eventType == SCOUT_EVENT_TYPE.HIT_ASSIST:
            msgType = 'ENEMY_SPOTTED_HIT'
        elif eventType == SCOUT_EVENT_TYPE.KILL_ASSIST:
            self.soundNotifications.play('enemy_killed')
            msgType = 'ENEMY_SPOTTED_KILLED'
        additionalInfo = None
        extra = None
        if reportedID > 0:
            additionalInfo = {'entity': g_sessionProvider.getCtx().getFullPlayerName(vID=reportedID)}
            extra = (('entity', reportedID),)
        else:
            msgType += '_PLURAL'
        g_windowsManager.battleWindow.pMsgsPanel.showMessage(msgType, additionalInfo, extra)
        return

    def updateArena(self, updateType, argStr):
        self.arena.update(updateType, argStr)

    def updatePositions(self, indices, positions):
        self.arena.updatePositions(indices, positions)

    def receiveHorn(self, vehicleID, hornID, start):
        vInfo = self.arena.vehicles.get(vehicleID, {})
        user = storage_getter('users')().getUser(vInfo.get('accountDBID', 0))
        if user and user.isIgnored() and start:
            return
        else:
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle is not None:
                if start:
                    vehicle.playHornSound(hornID)
                else:
                    vehicle.stopHornSound()
            return

    def useHorn(self, start):
        if not self.__isVehicleAlive or not self.__isOnArena:
            return
        elif self.vehicleTypeDescriptor is None or self.vehicleTypeDescriptor.hornID is None:
            return
        elif start and not self.__hornCooldown.ask():
            g_windowsManager.battleWindow.vMsgsPanel.showMessage('HORN_IS_BLOCKED', max(1.0, self.__hornCooldown.banTime()))
            return
        else:
            playerVehicle = BigWorld.entities.get(self.playerVehicleID)
            if playerVehicle is not None:
                if start:
                    playerVehicle.playHornSound(playerVehicle.typeDescriptor.hornID)
                else:
                    playerVehicle.stopHornSound()
            self.base.vehicle_useHorn(start)
            return

    def isHornActive(self):
        playerVehicle = BigWorld.entities.get(self.playerVehicleID)
        if playerVehicle is not None:
            return playerVehicle.isHornActive()
        else:
            return False
            return

    def hornMode(self):
        playerVehicle = BigWorld.entities.get(self.playerVehicleID)
        if playerVehicle is not None:
            return playerVehicle.hornMode
        else:
            return ''
            return

    def makeDenunciation(self, violatorID, topicID, violatorKind):
        if self.denunciationsLeft <= 0:
            return
        self.denunciationsLeft -= 1
        self.base.makeDenunciation(violatorID, topicID, violatorKind)

    def banUnbanUser(self, accountDBID, restrType, banPeriod, reason, isBan):
        reason = reason.encode('utf8')
        self.base.banUnbanUser(accountDBID, restrType, banPeriod, reason, isBan)

    def receiveAccountStats(self, requestID, stats):
        callback = self.__onCmdResponse.pop(requestID, None)
        if callback is None:
            return
        else:
            try:
                stats = cPickle.loads(stats)
            except:
                LOG_CURRENT_EXCEPTION()

            callback(stats)
            return

    def requestAccountStats(self, names, callback):
        requestID = self.__getRequestID()
        self.__onCmdResponse[requestID] = callback
        self.base.sendAccountStats(requestID, names)

    def storeClientCtx(self, clientCtx):
        self.clientCtx = clientCtx
        self.base.setClientCtx(clientCtx)

    def teleportVehicle(self, position, yaw):
        self.base.vehicle_teleport(position, yaw)

    def replenishAmmo(self):
        self.base.vehicle_replenishAmmo()

    def moveVehicleByCurrentKeys(self, isKeyDown, forceFlags = 204, forceMask = 0):
        moveFlags = self.makeVehicleMovementCommandByKeys(forceFlags, forceMask)
        self.moveVehicle(moveFlags, isKeyDown)

    def makeVehicleMovementCommandByKeys(self, forceFlags = 204, forceMask = 0):
        cmdMap = CommandMapping.g_instance
        flags = 0
        if self.__stopUntilFire:
            return flags
        if cmdMap.isActiveList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC)):
            if not cmdMap.isActive(CommandMapping.CMD_MOVE_BACKWARD):
                flags = 1
        elif cmdMap.isActive(CommandMapping.CMD_MOVE_BACKWARD):
            flags = 2
        else:
            if self.__cruiseControlMode >= _CRUISE_CONTROL_MODE.FWD25:
                flags = 1
            elif self.__cruiseControlMode <= _CRUISE_CONTROL_MODE.BCKW50:
                flags = 2
            isOn = self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD50 or self.__cruiseControlMode == _CRUISE_CONTROL_MODE.BCKW50
            if isOn:
                flags |= 16
            elif self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD25:
                flags |= 32
        rotateLeftFlag = 4
        rotateRightFlag = 8
        if self.invRotationOnBackMovement and flags & 2 != 0:
            rotateLeftFlag, rotateRightFlag = rotateRightFlag, rotateLeftFlag
        if cmdMap.isActive(CommandMapping.CMD_ROTATE_LEFT):
            if not cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
                flags |= rotateLeftFlag
        elif cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
            flags |= rotateRightFlag
        flags |= forceMask & forceFlags
        flags &= ~forceMask | forceFlags
        return flags

    def moveVehicle(self, flags, isKeyDown):
        if not self.__isOnArena:
            return
        else:
            cantMove = False
            if self.inputHandler.ctrl.isSelfVehicle():
                for deviceName, stateName in self.__deviceStates.iteritems():
                    msgName = self.__cantMoveCriticals.get(deviceName + '_' + stateName)
                    if msgName is not None:
                        cantMove = True
                        if isKeyDown:
                            self.__showPlayerError(msgName)
                        break

            if not cantMove:
                vehicle = BigWorld.entity(self.playerVehicleID)
                if vehicle is not None and vehicle.isStarted:
                    vehicle.showPlayerMovementCommand(flags)
                    rotationDir = -1 if flags & 4 else (1 if flags & 8 else 0)
                    movementDir = -1 if flags & 2 else (1 if flags & 1 else 0)
                    vehicle.filter.notifyInputKeysDown(movementDir, rotationDir)
                    if isKeyDown:
                        self.inputHandler.setAutorotation(True)
            self.base.vehicle_moveWith(flags)
            return

    def enableOwnVehicleAutorotation(self, enable):
        g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.AUTO_ROTATION, enable)
        self.base.vehicle_changeSetting(VEHICLE_SETTING.AUTOROTATION_ENABLED, enable)

    def enableServerAim(self, enable):
        self.base.setDevelopmentFeature('server_marker', enable)

    def autoAim(self, target):
        if target is None:
            vehID = 0
        elif not isinstance(target, Vehicle.Vehicle):
            vehID = 0
        elif target.id == self.__autoAimVehID:
            vehID = 0
        elif target.publicInfo['team'] == self.team:
            vehID = 0
        elif not target.isAlive():
            vehID = 0
        else:
            vehID = target.id
        if self.__autoAimVehID != vehID:
            self.__autoAimVehID = vehID
            self.cell.autoAim(vehID)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.onLockTarget(vehID != 0)
            if vehID != 0:
                self.inputHandler.setAimingMode(True, AIMING_MODE.TARGET_LOCK)
                self.gunRotator.clientMode = False
                self.soundNotifications.play('target_captured')
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE, vehicleId=vehID)
            else:
                self.inputHandler.setAimingMode(False, AIMING_MODE.TARGET_LOCK)
                self.gunRotator.clientMode = True
                self.__aimingInfo[0] = BigWorld.time()
                minShotDisp = self.vehicleTypeDescriptor.gun['shotDispersionAngle']
                self.__aimingInfo[1] = self.gunRotator.dispersionAngle / minShotDisp
                self.soundNotifications.play('target_unlocked')
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE)
        return

    def shoot(self, isRepeat = False):
        if self.__tryShootCallbackId is None:
            self.__tryShootCallbackId = BigWorld.callback(0.0, self.__tryShootCallback)
        if not self.__isOnArena:
            return
        else:
            for deviceName, stateName in self.__deviceStates.iteritems():
                msgName = self.__cantShootCriticals.get(deviceName + '_' + stateName)
                if msgName is not None:
                    self.__showPlayerError(msgName)
                    return

            canShoot, error = g_sessionProvider.getAmmoCtrl().canShoot()
            if not canShoot:
                if not isRepeat and error in self.__cantShootCriticals:
                    self.__showPlayerError(self.__cantShootCriticals[error])
                return
            if self.__gunReloadCommandWaitEndTime > BigWorld.time():
                return
            if self.__shotWaitingTimerID is not None:
                return
            if self.isGunLocked or self.__isOwnBarrelUnderWater() or self.__isShootPositionInsideOtherVehicle():
                if not isRepeat:
                    self.__showPlayerError(self.__cantShootCriticals['gun_locked'])
                return
            self.base.vehicle_shoot()
            self.__startWaitingForShot()
            if self.__stopUntilFire:
                self.__stopUntilFire = False
                if BigWorld.time() - self.__stopUntilFireStartTime > 60.0:
                    self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                self.__updateCruiseControlPanel()
                self.moveVehicle(self.makeVehicleMovementCommandByKeys(), True)
            return

    def __tryShootCallback(self):
        self.__tryShootCallbackId = None
        if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
            self.shoot(isRepeat=True)
        return

    def cancelWaitingForShot(self):
        if self.__shotWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__shotWaitingTimerID)
            self.__shotWaitingTimerID = None
            self.inputHandler.setAimingMode(False, AIMING_MODE.SHOOTING)
            self.gunRotator.targetLastShotPoint = False
        return

    def selectPlayer(self, vehId):
        if self.__isForcedGuiControlMode:
            vehicleDesc = self.arena.vehicles.get(vehId)
            if vehicleDesc['isAlive'] and vehicleDesc['team'] == self.team:
                self.inputHandler.selectPlayer(vehId)

    def leaveArena(self):
        LOG_DEBUG('Avatar.leaveArena')
        from helpers import statistics
        stats = statistics.g_statistics.getStatistics()
        LOG_DEBUG(stats)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording or replayCtrl.isPlaying:
            replayCtrl.stop()
        g_playerEvents.isPlayerEntityChanging = True
        g_playerEvents.onPlayerEntityChanging()
        self.__setIsOnArena(False)
        self.base.leaveArena(stats if game_control.g_instance.collectUiStats and len(stats) > 0 else None)
        return

    def addBotToArena(self, vehicleTypeName, team):
        compactDescr = vehicles.VehicleDescr(typeName=vehicleTypeName).makeCompactDescr()
        self.base.addBotToArena(compactDescr, team, self.name)

    def controlAnotherVehicle(self, vehicleID, callback = None):
        BigWorld.entity(self.playerVehicleID).isPlayer = False
        self.base.controlAnotherVehicle(vehicleID, 1)
        if vehicleID not in BigWorld.entities.keys():
            BigWorld.callback(0.1, partial(self.__controlAnotherVehicleWait, vehicleID, callback, 50))
            return
        BigWorld.callback(1.0, partial(self.__controlAnotherVehicleAfteraction, vehicleID, callback))

    def setForcedGuiControlMode(self, value, stopVehicle = True, enableAiming = True):
        if self.__stepsTillInit == 0:
            if self.__isForcedGuiControlMode ^ value:
                self.__doSetForcedGuiControlMode(value, enableAiming)
                if not value:
                    flags = self.makeVehicleMovementCommandByKeys()
                    self.moveVehicle(flags, False)
            if value and stopVehicle:
                self.moveVehicle(0, False)
        self.__isForcedGuiControlMode = value

    def isForcedGuiControlMode(self):
        return self.__isForcedGuiControlMode

    def getOwnVehiclePosition(self):
        return Math.Matrix(self.__ownVehicleMProv).translation

    def getOwnVehicleMatrix(self):
        return self.__ownVehicleMProv

    def getOwnVehicleSpeeds(self, getInstantaneous = False):
        if self.__ownVehicleMProv.target is None:
            return self.__lastVehicleSpeeds
        else:
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is None or not vehicle.isStarted:
                return self.__lastVehicleSpeeds
            speedInfo = vehicle.filter.speedInfo.value
            if getInstantaneous:
                speed = speedInfo[2]
                rspeed = speedInfo[3]
            else:
                speed = speedInfo[0]
                rspeed = speedInfo[1]
            MAX_SPEED_MULTIPLIER = 1.5
            physics = vehicle.typeDescriptor.physics
            if self.__fwdSpeedometerLimit is None or self.__bckwdSpeedometerLimit is None:
                self.__fwdSpeedometerLimit, self.__bckwdSpeedometerLimit = physics['speedLimits']
                self.__fwdSpeedometerLimit *= MAX_SPEED_MULTIPLIER
                self.__bckwdSpeedometerLimit *= MAX_SPEED_MULTIPLIER
            if speed > self.__fwdSpeedometerLimit:
                speed = self.__fwdSpeedometerLimit
                self.__fwdSpeedometerLimit += 1
            elif speed < self.__fwdSpeedometerLimit:
                lim = MAX_SPEED_MULTIPLIER * physics['speedLimits'][0]
                if self.__fwdSpeedometerLimit > lim:
                    self.__fwdSpeedometerLimit -= 1
            if speed < -self.__bckwdSpeedometerLimit:
                speed = -self.__bckwdSpeedometerLimit
                self.__bckwdSpeedometerLimit += 1
            elif speed > -self.__bckwdSpeedometerLimit:
                lim = MAX_SPEED_MULTIPLIER * physics['speedLimits'][1]
                if self.__bckwdSpeedometerLimit > lim:
                    self.__bckwdSpeedometerLimit -= 1
            rspeedLimit = physics['rotationSpeedLimit']
            if rspeed > rspeedLimit:
                rspeed = rspeedLimit
            elif rspeed < -rspeedLimit:
                rspeed = -rspeedLimit
            return (speed, rspeed)

    def getOwnVehicleShotDispersionAngle(self, turretRotationSpeed, withShot = 0):
        descr = self.vehicleTypeDescriptor
        aimingStartTime, aimingStartFactor, multFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime = self.__aimingInfo
        vehicleSpeed, vehicleRSpeed = self.getOwnVehicleSpeeds(True)
        vehicleMovementFactor = vehicleSpeed * chassisShotDispersionFactorsMovement
        vehicleMovementFactor *= vehicleMovementFactor
        vehicleRotationFactor = vehicleRSpeed * chassisShotDispersionFactorsRotation
        vehicleRotationFactor *= vehicleRotationFactor
        turretRotationFactor = turretRotationSpeed * gunShotDispersionFactorsTurretRotation
        turretRotationFactor *= turretRotationFactor
        if withShot == 0:
            shotFactor = 0.0
        elif withShot == 1:
            shotFactor = descr.gun['shotDispersionFactors']['afterShot']
        else:
            shotFactor = descr.gun['shotDispersionFactors']['afterShotInBurst']
        shotFactor *= shotFactor
        idealFactor = vehicleMovementFactor + vehicleRotationFactor + turretRotationFactor + shotFactor
        idealFactor *= descr.miscAttrs['additiveShotDispersionFactor'] ** 2
        idealFactor = multFactor * math.sqrt(1.0 + idealFactor)
        currTime = BigWorld.time()
        aimingFactor = aimingStartFactor * math.exp((aimingStartTime - currTime) / aimingTime)
        aim = self.inputHandler.aim
        isGunReload = False
        if aim is not None:
            isGunReload = aim.isGunReload()
        if aimingFactor < idealFactor:
            aimingFactor = idealFactor
            self.__aimingInfo[0] = currTime
            self.__aimingInfo[1] = aimingFactor
            if abs(idealFactor - multFactor) < 0.001:
                self.complexSoundNotifications.setAimingEnded(True, isGunReload)
            elif idealFactor / multFactor > 1.1:
                self.complexSoundNotifications.setAimingEnded(False, isGunReload)
        elif aimingFactor / multFactor > 1.1:
            self.complexSoundNotifications.setAimingEnded(False, isGunReload)
        return descr.gun['shotDispersionAngle'] * aimingFactor

    def handleVehicleCollidedVehicle(self, vehA, vehB, hitPt, time):
        if self.__vehicleToVehicleCollisions is None:
            return
        else:
            lastCollisionTime = 0
            key = (vehA, vehB)
            if not self.__vehicleToVehicleCollisions.has_key(key):
                key = (vehB, vehA)
            if self.__vehicleToVehicleCollisions.has_key(key):
                lastCollisionTime = self.__vehicleToVehicleCollisions[key]
            if time - lastCollisionTime < 0.2:
                return
            self.__vehicleToVehicleCollisions[key] = time
            vehSpeedSum = (vehA.filter.velocity - vehB.filter.velocity).length
            vehA.showVehicleCollisionEffect(hitPt, vehSpeedSum)
            self.inputHandler.onVehicleCollision(vehA, vehSpeedSum)
            self.inputHandler.onVehicleCollision(vehB, vehSpeedSum)
            return

    def getVehicleAttached(self):
        vehicle = self.vehicle
        if vehicle is None:
            vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle is None or not vehicle.inWorld or not vehicle.isStarted or vehicle.isDestroyed:
            return
        else:
            return vehicle

    def receiveBattleResults(self, isSuccess, data):
        LOG_MX('receiveBattleResults', isSuccess)
        if not isSuccess:
            return
        try:
            results = cPickle.loads(zlib.decompress(data))
            BattleResultsCache.save(self.name, results)
            g_playerEvents.onBattleResultsReceived(True, BattleResultsCache.convertToFullForm(results))
            self.base.confirmBattleResultsReceiving()
        except:
            LOG_CURRENT_EXCEPTION()

    def messenger_onActionByServer_chat2(self, actionID, reqID, args):
        from messenger_common_chat2 import MESSENGER_ACTION_IDS as actions
        LOG_DEBUG('messenger_onActionByServer', actions.getActionName(actionID), reqID, args)
        MessengerEntry.g_instance.protos.BW_CHAT2.onActionReceived(actionID, reqID, args)

    def logXMPPEvents(self, intArr, strArr):
        self._doCmdIntArrStrArr(AccountCommands.CMD_LOG_CLIENT_XMPP_EVENTS, intArr, strArr, None)
        return

    def __onAction(self, action):
        self.onChatShortcut(action)

    __cantShootCriticals = {'gun_destroyed': 'cantShootGunDamaged',
     'vehicle_destroyed': 'cantShootVehicleDestroyed',
     'crew_destroyed': 'cantShootCrewInactive',
     'no_ammo': 'cantShootNoAmmo',
     'gun_reload': 'cantShootGunReloading',
     'gun_locked': 'cantShootGunLocked'}

    def __onInitStepCompleted(self):
        LOG_DEBUG('Avatar.__onInitStepCompleted()', self.__stepsTillInit)
        if constants.IS_CAT_LOADED:
            if self.__stepsTillInit == 0:
                return
        if not self.__stepsTillInit > 0:
            raise AssertionError
            self.__stepsTillInit -= 1
            return self.__stepsTillInit != 0 and None
        else:
            self.initSpace()
            self.gunRotator.init_sound()
            self.__startGUI()
            DecalMap.g_instance.initGroups(1.0)
            if self.__isForcedGuiControlMode:
                self.__doSetForcedGuiControlMode(True, True)
            self.__setOwnVehicleMatrixCallback()
            for v in BigWorld.entities.values():
                if v.inWorld and isinstance(v, Vehicle.Vehicle) and not v.isStarted:
                    v.startVisual()
                    self.onVehicleEnterWorld(v)

            SoundGroups.g_instance.enableArenaSounds(True)
            SoundGroups.g_instance.applyPreferences()
            MusicController.g_musicController.onEnterArena()
            TriggersManager.g_manager.enable(True)
            BigWorld.wg_setUmbraEnabled(self.arena.arenaType.umbraEnabled)
            BigWorld.wg_enableTreeHiding(False)
            BigWorld.worldDrawEnabled(True)
            BigWorld.wg_setAmbientReverb(self.arena.arenaType.defaultReverbPreset)
            BigWorld.wg_setWaterTexScale(self.arena.arenaType.waterTexScale)
            BigWorld.wg_setWaterFreqX(self.arena.arenaType.waterFreqX)
            BigWorld.wg_setWaterFreqZ(self.arena.arenaType.waterFreqZ)
            BattleReplay.g_replayCtrl.onClientReady()
            self.base.setClientReady()
            if self.arena.period == ARENA_PERIOD.BATTLE:
                self.__setIsOnArena(True)
            self.arena.onPeriodChange += self.__onArenaPeriodChange
            ownVehicle = BigWorld.entity(self.playerVehicleID)
            if ownVehicle is not None:
                self.updateVehicleHealth(ownVehicle.health, ownVehicle.isCrewActive)
            self.cell.autoAim(0)
            clientVisibilityFlags = 0
            if g_sessionProvider.getCtx().isObserver(self.playerVehicleID):
                clientVisibilityFlags |= ClientVisibilityFlags.OBSERVER_OBJECTS
            ClientVisibilityFlags.updateSpaceVisibility(self.spaceID, clientVisibilityFlags)
            g_playerEvents.onAvatarReady()
            return

    def __initGUIConfig(self):
        up = Settings.g_instance.userPrefs
        out = dict()
        out['showFPS'] = True
        out['showPlayerBonuses'] = True
        if up.has_key('showFPS'):
            out['showFPS'] = up.readBool('showFPS')
        else:
            up.writeBool('showFPS', True)
        return out

    def __initGUI(self):
        prereqs = []
        self.guiConfig = self.__initGUIConfig()
        if not g_offlineMapCreator.Active():
            self.inputHandler = AvatarInputHandler.AvatarInputHandler()
            prereqs += self.inputHandler.prerequisites()
        BigWorld.player().arena
        self.playerBonusesPanel = None
        if self.guiConfig['showPlayerBonuses']:
            self.playerBonusesPanel = PlayerBonusesPanel.PlayerBonusesPanel()
            prereqs += self.playerBonusesPanel.prerequisites()
        self.soundNotifications = IngameSoundNotifications.IngameSoundNotifications()
        self.complexSoundNotifications = IngameSoundNotifications.ComplexSoundNotifications(self.soundNotifications)
        self.battleMessages = BattleDamageMessages()
        return prereqs

    def __startGUI(self):
        self.inputHandler.start()
        self.inputHandler.setReloading(-1)
        if self.playerBonusesPanel is not None:
            self.playerBonusesPanel.start()
            self.playerBonusesPanel.setVisible(False)
        self.__isGuiVisible = True
        self.arena.onVehicleKilled += self.__onArenaVehicleKilled
        MessengerEntry.g_instance.onAvatarInitGUI()
        g_windowsManager.startBattle()
        self.soundNotifications.start()
        return

    def __destroyGUI(self):
        g_windowsManager.destroyBattle()
        if self.playerBonusesPanel is not None:
            self.playerBonusesPanel.destroy()
            self.playerBonusesPanel = None
        self.arena.onVehicleKilled -= self.__onArenaVehicleKilled
        self.complexSoundNotifications.destroy()
        self.complexSoundNotifications = None
        self.soundNotifications.destroy()
        self.soundNotifications = None
        self.battleMessages.destroy()
        self.battleMessages = None
        self.inputHandler.stop()
        self.inputHandler = None
        g_sessionProvider.stop()
        return

    def __reloadGUI(self):
        self.__destroyGUI()
        self.__initGUI()
        self.__startGUI()
        self.setForcedGuiControlMode(True)
        self.setForcedGuiControlMode(False)

    def __setVisibleGUI(self, bool):
        self.__isGuiVisible = bool
        if g_windowsManager.battleWindow is not None:
            g_windowsManager.battleWindow.showAll(bool)
        BigWorld.wg_enableTreeTransparency(bool)
        vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle is None:
            return
        else:
            if bool and vehicle.isAlive():
                BigWorld.wgAddEdgeDetectEntity(vehicle, 0, True)
            else:
                BigWorld.wgDelEdgeDetectEntity(vehicle)
            self.inputHandler.setGUIVisible(bool)
            return

    @property
    def isGuiVisible(self):
        return self.__isGuiVisible

    def __doSetForcedGuiControlMode(self, value, enableAiming):
        self.inputHandler.detachCursor(value, enableAiming)

    __cantMoveCriticals = {'engine_destroyed': 'cantMoveEngineDamaged',
     'leftTrack_destroyed': 'cantMoveChassisDamaged',
     'rightTrack_destroyed': 'cantMoveChassisDamaged',
     'vehicle_destroyed': 'cantMoveVehicleDestroyed',
     'crew_destroyed': 'cantMoveCrewInactive'}

    def __setIsOnArena(self, onArena):
        if self.__isOnArena == onArena:
            return
        else:
            self.__isOnArena = onArena
            if not onArena:
                if hasattr(self, 'gunRotator') and self.gunRotator is not None:
                    self.gunRotator.stop()
            else:
                if hasattr(self, 'gunRotator') and self.gunRotator is not None:
                    self.gunRotator.start()
                self.moveVehicle(self.makeVehicleMovementCommandByKeys(), False)
                g_sessionProvider.getAmmoCtrl().applySettings(self)
            return

    def __showPlayerError(self, msgName, args = None):
        g_windowsManager.battleWindow.vErrorsPanel.showMessage(msgName, args)

    def __showDamageIconAndPlaySound(self, damageCode, extra):
        deviceName = None
        deviceState = None
        soundType = None
        soundNotificationCheckFn = None
        if damageCode in self.__damageInfoFire:
            extra = self.vehicleTypeDescriptor.extrasDict['fire']
            self.__fireInVehicle = damageCode != 'FIRE_STOPPED'
            soundType = 'critical' if self.__fireInVehicle else 'fixed'
            g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE, self.__fireInVehicle)
            curFireState = self.__fireInVehicle
            soundNotificationCheckFn = lambda : curFireState == self.__fireInVehicle
        elif damageCode in self.__damageInfoCriticals:
            deviceName = extra.name[:-len('Health')]
            if damageCode == 'DEVICE_REPAIRED_TO_CRITICAL':
                deviceState = 'repaired'
                if 'functionalCanMove' in extra.sounds:
                    tracksToCheck = ['leftTrack', 'rightTrack']
                    if deviceName in tracksToCheck:
                        tracksToCheck.remove(deviceName)
                    canMove = True
                    for trackName in tracksToCheck:
                        if trackName in self.__deviceStates and self.__deviceStates[trackName] == 'destroyed':
                            canMove = False
                            break

                    soundType = 'functionalCanMove' if canMove else 'functional'
                else:
                    soundType = 'functional'
            else:
                deviceState = 'critical'
                soundType = 'critical'
            self.__deviceStates[deviceName] = 'critical'
        elif damageCode in self.__damageInfoDestructions:
            deviceName = extra.name[:-len('Health')]
            deviceState = 'destroyed'
            soundType = 'destroyed'
            self.__deviceStates[deviceName] = 'destroyed'
            vehicle = self.vehicle
            if vehicle is not None and damageCode not in self.__damageInfoNoNotification:
                vehicle.appearance.executeCriticalHitVibrations(vehicle, extra.name)
        elif damageCode in self.__damageInfoHealings:
            deviceName = extra.name[:-len('Health')]
            deviceState = 'normal'
            soundType = 'fixed'
            self.__deviceStates.pop(deviceName, None)
        if deviceState is not None:
            if deviceName in self.__deviceStates:
                actualState = self.__deviceStates[deviceName]
            else:
                actualState = 'normal'
            g_sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEVICES, (deviceName, deviceState, actualState))
            if deviceState == 'repaired':
                deviceState = 'critical'
            soundNotificationCheckFn = lambda : self.__deviceStates.get(deviceName, 'normal') == deviceState
        if soundType is not None and damageCode not in self.__damageInfoNoNotification:
            sound = extra.sounds.get(soundType)
            if sound is not None:
                self.soundNotifications.play(sound, checkFn=soundNotificationCheckFn)
        return

    __damageInfoCriticals = ('DEVICE_CRITICAL',
     'DEVICE_REPAIRED_TO_CRITICAL',
     'DEVICE_CRITICAL_AT_SHOT',
     'DEVICE_CRITICAL_AT_RAMMING',
     'DEVICE_CRITICAL_AT_FIRE',
     'DEVICE_CRITICAL_AT_WORLD_COLLISION',
     'DEVICE_CRITICAL_AT_DROWNING',
     'ENGINE_CRITICAL_AT_UNLIMITED_RPM')
    __damageInfoDestructions = ('DEVICE_DESTROYED',
     'DEVICE_DESTROYED_AT_SHOT',
     'DEVICE_DESTROYED_AT_RAMMING',
     'DEVICE_DESTROYED_AT_FIRE',
     'DEVICE_DESTROYED_AT_WORLD_COLLISION',
     'DEVICE_DESTROYED_AT_DROWNING',
     'TANKMAN_HIT',
     'TANKMAN_HIT_AT_SHOT',
     'TANKMAN_HIT_AT_WORLD_COLLISION',
     'TANKMAN_HIT_AT_DROWNING',
     'ENGINE_DESTROYED_AT_UNLIMITED_RPM')
    __damageInfoHealings = ('DEVICE_REPAIRED', 'TANKMAN_RESTORED', 'FIRE_STOPPED')
    __damageInfoFire = ('FIRE',
     'DEVICE_STARTED_FIRE_AT_SHOT',
     'DEVICE_STARTED_FIRE_AT_RAMMING',
     'FIRE_STOPPED')
    __damageInfoNoNotification = ('DEVICE_CRITICAL',
     'DEVICE_DESTROYED',
     'TANKMAN_HIT',
     'FIRE',
     'DEVICE_CRITICAL_AT_DROWNING',
     'DEVICE_DESTROYED_AT_DROWNING',
     'TANKMAN_HIT_AT_DROWNING')

    def __setOwnVehicleMatrixCallback(self):
        self.__setOwnVehicleMatrixTimerID = None
        if not self.__ownVehicleMProv.target is None:
            raise AssertionError
            vehicle = self.vehicle
            if vehicle is not None and not vehicle.isDestroyed and vehicle.isStarted and vehicle.id == self.playerVehicleID:
                self.__ownVehicleMProv.target = isinstance(vehicle.filter, BigWorld.WGVehicleFilter) and vehicle.filter.bodyMatrix
            else:
                self.__ownVehicleMProv.target = vehicle.matrix
            return
        else:
            self.__setOwnVehicleMatrixTimerID = BigWorld.callback(SERVER_TICK_LENGTH, self.__setOwnVehicleMatrixCallback)
            return

    def __onArenaVehicleKilled(self, targetID, attackerID, reason):
        isMyVehicle = targetID == self.playerVehicleID
        isObservedVehicle = not self.__isVehicleAlive and targetID == self.inputHandler.ctrl.curVehicleID
        if isMyVehicle or isObservedVehicle:
            if g_windowsManager.battleWindow is not None:
                g_windowsManager.battleWindow.hideVehicleTimer('ALL')
            try:
                if hasattr(self, 'gunRotator') and self.gunRotator is not None:
                    self.gunRotator.stop()
            except Exception:
                LOG_CURRENT_EXCEPTION()

        if targetID == self.playerVehicleID:
            self.inputHandler.setKillerVehicleID(attackerID)
            return
        else:
            if attackerID == self.playerVehicleID:
                targetInfo = self.arena.vehicles.get(targetID)
                if targetInfo is None:
                    LOG_CODEPOINT_WARNING()
                    return
                self.__frags.add(targetID)
            self.battleMessages.onArenaVehicleKilled(targetID, attackerID, reason)
            return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        self.__setIsOnArena(period == ARENA_PERIOD.BATTLE)
        if period == ARENA_PERIOD.PREBATTLE and period > self.__prevArenaPeriod:
            LightManager.GameLights.startTicks()
            if AuxiliaryFx.g_instance is not None:
                AuxiliaryFx.g_instance.execEffect('startTicksEffect')
        if period == ARENA_PERIOD.BATTLE and period > self.__prevArenaPeriod:
            self.soundNotifications.play('start_battle')
            LightManager.GameLights.roundStarted()
            if AuxiliaryFx.g_instance is not None:
                AuxiliaryFx.g_instance.execEffect('roundStartedEffect')
        self.__prevArenaPeriod = period
        return

    def __startWaitingForShot(self):
        if self.__shotWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__shotWaitingTimerID)
            self.__shotWaitingTimerID = None
        timeout = BigWorld.LatencyInfo().value[3] * 0.5
        timeout = min(_SHOT_WAITING_MAX_TIMEOUT, timeout)
        timeout = max(_SHOT_WAITING_MIN_TIMEOUT, timeout)
        self.__shotWaitingTimerID = BigWorld.callback(timeout, self.__showTimedOutShooting)
        self.inputHandler.setAimingMode(True, AIMING_MODE.SHOOTING)
        if not self.inputHandler.getAimingMode(AIMING_MODE.USER_DISABLED):
            self.gunRotator.targetLastShotPoint = True
        self.__gunReloadCommandWaitEndTime = BigWorld.time() + 2.0
        return

    def __showTimedOutShooting(self):
        self.__shotWaitingTimerID = None
        self.inputHandler.setAimingMode(False, AIMING_MODE.SHOOTING)
        self.gunRotator.targetLastShotPoint = False
        try:
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is not None and vehicle.isStarted:
                gunDescr = vehicle.typeDescriptor.gun
                burstCount = gunDescr['burst'][0]
                ammo = g_sessionProvider.getAmmoCtrl()
                if ammo.getCurrentShellCD() is not None:
                    totalShots, shotsInClip = ammo.getCurrentShells()
                    if burstCount > totalShots > 0:
                        burstCount = totalShots
                    if gunDescr['clip'][0] > 1 and burstCount > shotsInClip > 0:
                        burstCount = shotsInClip
                vehicle.showShooting(burstCount, True)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    def __controlAnotherVehicleWait(self, vehicleID, callback, waitCallsLeft):
        if vehicleID in BigWorld.entities.keys():
            BigWorld.callback(1.0, partial(self.__controlAnotherVehicleAfteraction, vehicleID, callback))
        else:
            if waitCallsLeft <= 1:
                if callback is not None:
                    callback()
                return
            BigWorld.callback(0.1, partial(self.__controlAnotherVehicleWait, vehicleID, callback, waitCallsLeft - 1))
        return

    def __controlAnotherVehicleAfteraction(self, vehicleID, callback):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is None:
            return
        else:
            vehicle.isPlayer = True
            self.__isVehicleAlive = True
            self.playerVehicleID = vehicleID
            self.vehicleTypeDescriptor = vehicle.typeDescriptor
            self.base.controlAnotherVehicle(vehicleID, 2)
            self.gunRotator.clientMode = False
            self.gunRotator.start()
            self.base.setDevelopmentFeature('server_marker', True)
            self.base.setDevelopmentFeature('heal', 0)
            self.base.setDevelopmentFeature('stop_bot', 0)
            self.inputHandler.setKillerVehicleID(None)
            self.inputHandler.onControlModeChanged('arcade')
            if callback is not None:
                callback()
            return

    def __dumpVehicleState(self):
        matrix = Math.Matrix(self.getOwnVehicleMatrix())
        LOG_NOTE('Arena type: ', self.arena.arenaType.geometryName)
        LOG_NOTE('Vehicle position: ', matrix.translation)
        LOG_NOTE('Vehicle direction (y, p, r): ', (matrix.yaw, matrix.pitch, matrix.roll))
        LOG_NOTE('Vehicle speeds: ', self.getOwnVehicleSpeeds())
        if self.vehicleTypeDescriptor is not None:
            LOG_NOTE('Vehicle type: ', self.vehicleTypeDescriptor.type.name)
            LOG_NOTE('Vehicle turret: ', self.vehicleTypeDescriptor.turret['name'])
            LOG_NOTE('Vehicle gun: ', self.vehicleTypeDescriptor.gun['name'])
        LOG_NOTE('Shot point: ', self.gunRotator._VehicleGunRotator__lastShotPoint)
        return

    def __reportLag(self):
        msg = 'LAG REPORT\n'
        import time
        t = time.gmtime()
        msg += '\ttime: %d/%0d/%0d %0d:%0d:%0d UTC\n' % t[:6]
        msg += '\tAvatar.id: %d\n' % self.id
        ping = BigWorld.LatencyInfo().value[3] - 0.5 * constants.SERVER_TICK_LENGTH
        ping = max(1, ping * 1000)
        msg += '\tping: %d\n' % ping
        msg += '\tFPS: %d\n' % BigWorld.getFPS()[1]
        numVehs = 0
        numAreaDestrs = 0
        for e in BigWorld.entities.values():
            if type(e) is Vehicle.Vehicle:
                numVehs += 1
            elif type(e) == AreaDestructibles.AreaDestructibles:
                numAreaDestrs += 1

        msg += '\tnum Vehicle: %d\n\tnum AreaDestructibles: %d\n' % (numVehs, numAreaDestrs)
        msg += '\tarena: %s\n' % self.arena.arenaType.geometryName
        msg += '\tposition: ' + str(self.position)
        LOG_NOTE(msg)
        self.base.setDevelopmentFeature('log_lag', True)

    def __updateCruiseControlPanel(self):
        damagePanel = g_windowsManager.battleWindow.damagePanel
        if self.__stopUntilFire or not self.__isVehicleAlive:
            damagePanel.setCruiseMode(_CRUISE_CONTROL_MODE.NONE)
        else:
            damagePanel.setCruiseMode(self.__cruiseControlMode)

    def __applyTimeAndWeatherSettings(self, overridePresetID = None):
        presets = self.arena.arenaType.weatherPresets
        weather = Weather.weather()
        if len(presets) == 0 or presets[0].get('name') is None:
            return
        else:
            try:
                presetID = overridePresetID if overridePresetID is not None else self.weatherPresetID
                preset = presets[presetID]
                system = weather.newSystemByName(preset['name'])
                windSpeed = preset.get('windSpeed')
                if windSpeed is not None:
                    windSpeed = windSpeed.split()
                    weather.windSpeed(windSpeed)
                elif system is not None:
                    weather.windSpeed(system.windSpeed)
                windGustiness = preset.get('windGustiness')
                if windGustiness is not None:
                    weather.windGustiness(windGustiness)
                elif system is not None:
                    weather.windGustiness(float(system.windGustiness))
            except Exception:
                LOG_CURRENT_EXCEPTION()
                LOG_DEBUG("Weather system's ID was:", self.weatherPresetID)

            return

    def __processVehicleAmmo(self, compactDescr, quantity, quantityInClip, _):
        if g_sessionProvider.getCtx().isObserver(self.playerVehicleID):
            return
        result = g_sessionProvider.getAmmoCtrl().setShells(compactDescr, quantity, quantityInClip)
        if result & SHELL_SET_RESULT.CURRENT > 0:
            isCassetteReload = result & SHELL_SET_RESULT.CASSETTE_RELOAD > 0
            if not isCassetteReload:
                self.getOwnVehicleShotDispersionAngle(self.gunRotator.turretRotationSpeed, 1)

    def __processVehicleEquipments(self, compactDescr, quantity, _, timeRemaining):
        g_sessionProvider.getEquipmentsCtrl().setEquipment(compactDescr, quantity, timeRemaining)

    def __isOwnBarrelUnderWater(self):
        if self.vehicle is None:
            return
        else:
            turretYaw = Math.Matrix(self.gunRotator.turretMatrix).yaw
            gunPitch = Math.Matrix(self.gunRotator.gunMatrix).pitch
            lp = computeBarrelLocalPoint(self.vehicleTypeDescriptor, turretYaw, gunPitch)
            wp = Math.Matrix(self.vehicle.matrix).applyPoint(lp)
            up = Math.Vector3((0.0, 0.1, 0.0))
            return BigWorld.wg_collideWater(wp, wp + up, False) != -1.0

    def __fireNonFatalDamageTrigger(self, targetId):
        self.__fireNonFatalDamageTriggerID = None
        vehicle = BigWorld.entities.get(targetId)
        if vehicle is not None:
            if not vehicle.isPlayer and vehicle.isAlive():
                TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_MADE_NONFATAL_DAMAGE, targetId=targetId)
        return

    def __getRequestID(self):
        self.__requestID += 1
        if self.__requestID >= AccountCommands.REQUEST_ID_UNRESERVED_MAX:
            self.__requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN
        return self.__requestID

    def __doCmd(self, doCmdMethod, cmd, callback, *args):
        if Account.g_accountRepository is None:
            return
        else:
            requestID = self.__getRequestID()
            if requestID is None:
                return
            if callback is not None:
                self.__onCmdResponse[requestID] = callback
            getattr(self.base, doCmdMethod)(requestID, cmd, *args)
            return

    def _doCmdStr(self, cmd, str, callback):
        self.__doCmd('doCmdStr', cmd, callback, str)

    def _doCmdInt3(self, cmd, int1, int2, int3, callback):
        self.__doCmd('doCmdInt3', cmd, callback, int1, int2, int3)

    def _doCmdInt4(self, cmd, int1, int2, int3, int4, callback):
        self.__doCmd('doCmdInt4', cmd, callback, int1, int2, int3, int4)

    def _doCmdInt2Str(self, cmd, int1, int2, str, callback):
        self.__doCmd('doCmdInt2Str', cmd, callback, int1, int2, str)

    def _doCmdIntArr(self, cmd, arr, callback):
        self.__doCmd('doCmdIntArr', cmd, callback, arr)

    def _doCmdIntArrStrArr(self, cmd, intArr, strArr, callback):
        self.__doCmd('doCmdIntArrStrArr', cmd, callback, intArr, strArr)

    def update(self, pickledDiff):
        self._update(cPickle.loads(pickledDiff))

    def _update(self, diff):
        LOG_DEBUG('_update', diff)
        if not BattleReplay.isPlaying():
            self.intUserSettings.synchronize(False, diff)
            g_playerEvents.onClientUpdated(diff)

    def isSynchronized(self):
        if BattleReplay.isPlaying():
            return True
        else:
            return self.intUserSettings.isSynchronized()

    def __isShootPositionInsideOtherVehicle(self):
        vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            turretPosition, shootPosition = getVehicleShootingPositions(vehicle)
            return isShootPositionInsideOtherVehicle(vehicle, turretPosition, shootPosition)
        else:
            return False
            return


def preload(alist):
    ds = ResMgr.openSection('precache.xml')
    if ds is not None:
        for sec in ds.values():
            alist.append(sec.asString)

    return


def _boundingBoxAsVector4(bb):
    return Math.Vector4(bb[0][0], bb[0][1], bb[1][0], bb[1][1])


def _getBestShotResultSound(currBest, newSoundName, otherData):
    newSoundPriority = _shotResultSoundPriorities[newSoundName]
    if currBest is None:
        return (newSoundName, otherData, newSoundPriority)
    elif newSoundPriority > currBest[2]:
        return (newSoundName, otherData, newSoundPriority)
    else:
        return currBest


_shotResultSoundPriorities = {'enemy_hp_damaged_by_projectile_and_gun_damaged_by_player': 12,
 'enemy_hp_damaged_by_projectile_and_chassis_damaged_by_player': 11,
 'enemy_hp_damaged_by_projectile_by_player': 10,
 'enemy_hp_damaged_by_explosion_at_direct_hit_by_player': 9,
 'enemy_hp_damaged_by_near_explosion_by_player': 8,
 'enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player': 7,
 'enemy_no_hp_damage_at_no_attempt_and_gun_damaged_by_player': 6,
 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player': 5,
 'enemy_no_hp_damage_at_no_attempt_and_chassis_damaged_by_player': 4,
 'enemy_no_piercing_by_player': 3,
 'enemy_no_hp_damage_at_attempt_by_player': 3,
 'enemy_no_hp_damage_at_no_attempt_by_player': 2,
 'enemy_no_hp_damage_by_near_explosion_by_player': 1,
 'enemy_ricochet_by_player': 0}

class FilterLagEmulator(object):

    def __init__(self, entityFilter = None, period = 5):
        self.__period = period
        self.__filter = BigWorld.player().getVehicleAttached().filter if entityFilter is None else entityFilter
        self.__callback = None
        return

    def start(self):
        if self.__callback is None:
            self.__onCallback()
        return

    def __onCallback(self):
        self.click()
        self.__callback = BigWorld.callback(self.__period, self.__onCallback)

    def click(self):
        self.__filter.ignoreInputs = not self.__filter.ignoreInputs

    def stop(self):
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
            self.__callback = None
        return


Avatar = PlayerAvatar

def getVehicleShootingPositions(vehicle):
    vd = vehicle.typeDescriptor
    gunOffs = vd.turret['gunPosition']
    turretOffs = vd.hull['turretPositions'][0] + vd.chassis['hullPosition']
    turretYaw, gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vd.gun['pitchLimits']['absolute'])
    turretWorldMatrix = Math.Matrix()
    turretWorldMatrix.setRotateY(turretYaw)
    turretWorldMatrix.translation = turretOffs
    turretWorldMatrix.postMultiply(vehicle.model.matrix)
    gunWorldMatrix = Math.Matrix()
    gunWorldMatrix.setRotateX(gunPitch)
    gunWorldMatrix.postMultiply(turretWorldMatrix)
    return (turretWorldMatrix.applyPoint(gunOffs), turretWorldMatrix.translation)
