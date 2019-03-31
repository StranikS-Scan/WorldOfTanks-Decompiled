# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Avatar.py
# Compiled at: 2018-12-11 23:56:21
import BigWorld, Keys, Math, cPickle
from functools import partial
import math
import random
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
from gui.BattleContext import g_battleContext
from constants import ARENA_PERIOD, AIMING_MODE, VEHICLE_SETTING, DEVELOPMENT_INFO, SHOT_RESULT
from constants import SERVER_TICK_LENGTH, AUTO_AIM_LOSS_REASON, VEHICLE_MISC_STATUS
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN
from messenger.wrappers import ChatActionWrapper
from messenger.gui import MessengerDispatcher
from PlayerEvents import g_playerEvents
from ClientChat import ClientChat
from ChatManager import chatManager
from VehicleAppearance import StippleManager
from helpers import bound_effects
from helpers import DecalMap
from helpers import i18n
from gui import GameInfoPanel
from gui import PlayerBonusesPanel
from gui import IngameSoundNotifications
from gui.WindowsManager import g_windowsManager
from chat_shared import CHAT_ACTIONS, CHAT_COMMANDS
from debug_utils import *
from material_kinds import EFFECT_MATERIALS
from post_processing import g_postProcessing
from Vibroeffects.Controllers.ReloadController import ReloadController as VibroReloadController
from LightFx import LightManager
from account_helpers.AccountSettings import AccountSettings
import physics_shared
import BattleReplay
import HornCooldown
import Vivox
import material_kinds

class _CRUISE_CONTROL_MODE():
    NONE = 0
    FWD25 = 1
    FWD50 = 2
    FWD100 = 3
    BCKW50 = -1
    BCKW100 = -2


_SHOT_WAITING_MAX_TIMEOUT = 0.2
_SHOT_WAITING_MIN_TIMEOUT = 0.12

class PlayerAvatar(BigWorld.Entity, ClientChat):
    __rangeStreamIDCallbacks = RangeStreamIDCallbacks()
    isOnArena = property(lambda self: self.__isOnArena)
    isVehicleAlive = property(lambda self: self.__isVehicleAlive)
    isWaitingForShot = property(lambda self: self.__shotWaitingTimerID is not None)

    def __init__(self):
        ClientChat.__init__(self)
        self.__rangeStreamIDCallbacks.addRangeCallback((STREAM_ID_CHAT_MIN, STREAM_ID_CHAT_MAX), '_ClientChat__receiveStreamedData')
        self.__prevArenaPeriod = -1

    def onBecomePlayer(self):
        LOG_DEBUG('Avatar.onBecomePlayer()')
        BigWorld.camera(BigWorld.CursorCamera())
        from gui.Scaleform.utils.HangarSpace import g_hangarSpace
        if g_hangarSpace is not None:
            g_hangarSpace.destroy()
        chatManager.switchPlayerProxy(self)
        g_playerEvents.isPlayerEntityChanging = False
        self.arena = ClientArena.ClientArena(self.arenaTypeID, self.arenaGuiType, self.arenaExtraData, self.weatherPresetID)
        self.vehicleTypeDescriptor = None
        self.terrainEffects = None
        self.hitTesters = set()
        self.onVehicleEnterWorld = Event.Event()
        self.onVehicleLeaveWorld = Event.Event()
        self.onGunShotChanged = Event.Event()
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
        self.__ammo = {}
        self.__currShellsIdx = None
        self.__nextShellsIdx = None
        self.__equipment = {}
        self.__equipmentFlags = {}
        self.__optionalDevices = {}
        self.__nextCSlotIdx = 0
        self.__fireInVehicle = False
        self.__burstShotResult = 0
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
        self.__frags = set()
        self.__vehicleToVehicleCollisions = {}
        self.__deviceStates = {}
        self.__maySeeOtherVehicleDamage = False
        cdWnd = vehicles.HORN_COOLDOWN.WINDOW + vehicles.HORN_COOLDOWN.CLIENT_WINDOW_EXPANSION
        self.__hornCooldown = HornCooldown.HornCooldown(cdWnd, vehicles.HORN_COOLDOWN.MAX_SIGNALS)
        BigWorld.wg_setBatchingEnabled(self.arena.typeDescriptor.batchingEnabled)
        g_playerEvents.onAvatarBecomePlayer()
        MusicController.g_musicController.stopAmbient()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_COMBAT_LOADING)
        BigWorld.wg_prefetchSpaceZip(self.arena.typeDescriptor.typeName)
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
        return

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
                if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and constants.HAS_DEV_RESOURCES:
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
                    if key == Keys.KEY_8:
                        if self.playerBonusesPanel is not None:
                            if not self.playerBonusesPanel.getVisible():
                                self.base.setDevelopmentFeature('send_player_bonuses', True)
                            else:
                                self.base.setDevelopmentFeature('send_player_bonuses', False)
                                self.playerBonusesPanel.setVisible(False)
                        return True
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
                if cmdMap.isFired(CommandMapping.CMD_SWITCH_SERVER_MARKER, key) and isDown:
                    showServerMarker = not self.gunRotator.showServerMarker
                    self.base.setDevelopmentFeature('server_marker', showServerMarker)
                    self.gunRotator.showServerMarker = showServerMarker
                    return True
                if cmdMap.isFired(CommandMapping.CMD_TOGGLE_GUI, key) and isDown:
                    self.__setVisibleGUI(not self.__isGuiVisible)
                if constants.HAS_DEV_RESOURCES and isDown:
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
                    if key == Keys.KEY_V and mods == 0:
                        import Cat
                        Cat.Help.SetVideoEngineerVisible(not Cat.Help.GetVideoEngineerVisible())
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
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET, key) and isDown and mods == 0:
                    self.__onChatShortcutAttackMyTarget()
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_ATTACK, key) and isDown and mods == 0:
                    self.__onChatShortcut('ATTACK')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE, key) and isDown and mods == 0:
                    self.__onChatShortcut('BACKTOBASE')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_FOLLOWME, key) and isDown and mods == 0:
                    self.__onChatShortcut('FOLLOWME')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_POSITIVE, key) and isDown and mods == 0:
                    self.__onChatShortcut('POSITIVE')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_NEGATIVE, key) and isDown and mods == 0:
                    self.__onChatShortcut('NEGATIVE')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_HELPME, key) and isDown and mods == 0:
                    self.__onChatShortcut('HELPME')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VEHICLE_MARKERS_SHOW_INFO, key):
                    g_windowsManager.battleWindow.vMarkersManager.showExtendedInfo(isDown)
                    return True
                if key == Keys.KEY_F12 and isDown and mods == 0:
                    self.__dumpVehicleState()
                    return True
                if key == Keys.KEY_F12 and isDown and mods == 2:
                    self.__reportLag()
                    return True
                if cmdMap.isFired(CommandMapping.CMD_USE_HORN, key) and isDown:
                    self.useHorn(True)
                    return True
                if self.isHornActive() and self.hornMode() != 'oneshot' and not cmdMap.isActive(CommandMapping.CMD_USE_HORN):
                    self.useHorn(False)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VOICECHAT_MUTE, key):
                    LOG_DEBUG('onVoiceChatPTT', isDown)
                    if Vivox.getResponseHandler().channelsMgr.currentChannel:
                        Vivox.getResponseHandler().setMicMute(not isDown)
                if cmdMap.isFired(CommandMapping.CMD_LOGITECH_SWITCH_VIEW, key) and isDown:
                    LOG_DEBUG('LOGITECH SWICH VIEW', isDown)
                    from gui.Scaleform.LogitechMonitor import LogitechMonitor
                    LogitechMonitor.onChangeView()
                if cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP, CommandMapping.CMD_MINIMAP_VISIBLE), key) and isDown:
                    g_windowsManager.battleWindow.minimap.handleKey(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_RELOAD_PARTIAL_CLIP, key) and isDown:
                    self.onReloadPartialClipKeyDown()
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
            self.__onInitStepCompleted()
        return

    def set_playerVehiclePitchRoll(self, prev):
        vehicle = BigWorld.entities.get(self.playerVehicleID)
        if vehicle is None or not vehicle.useAdvancedPhysics:
            return
        else:
            vehicle = BigWorld.entities.get(self.playerVehicleID)
            if isinstance(vehicle.filter, BigWorld.WGVehicleFilter2):
                if vehicle.filter.playerMode:
                    pitch = physics_shared.decodeAngleFromUint(self.playerVehiclePitchRoll[0], 16)
                    roll = physics_shared.decodeAngleFromUint(self.playerVehiclePitchRoll[1], 16)
                    delay = SERVER_TICK_LENGTH if constants.HAS_DEV_RESOURCES else 0.0
                    vehicle.filter.syncPitchRoll(pitch, roll, False, delay)
            return

    def set_aboardSyncMode(self, prev):
        vehicle = BigWorld.entities.get(self.playerVehicleID)
        if vehicle is None or not vehicle.useAdvancedPhysics:
            return
        else:
            if isinstance(vehicle.filter, BigWorld.WGVehicleFilter2):
                vehicle.filter.playerMode = self.aboardSyncMode
            return

    def set_isGunLocked(self, prev):
        if self.isGunLocked:
            self.gunRotator.lock(True)
            self.inputHandler.onControlModeChanged('arcade')
        else:
            self.gunRotator.lock(False)

    def onStaticCollision(self, matKind):
        vehicle = BigWorld.entities.get(self.playerVehicleID)
        if vehicle is not None:
            if matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES['stone']:
                vehicle.showCollisionEffect(Math.Vector3())
            vehicle.appearance.executeRammingVibrations(matKind)
        return

    def targetBlur(self, prevEntity):
        if not isinstance(prevEntity, Vehicle.Vehicle):
            return
        else:
            if self.inputHandler.aim:
                self.inputHandler.aim.clearTarget()
            BigWorld.wgDelEdgeDetectEntity(prevEntity)
            if self.__maySeeOtherVehicleDamage and self.vehicle is not None:
                self.cell.monitorVehicleDamage(0)
                LOG_DEBUG('TODO: WOTD-3248', prevEntity.id)
            return

    def targetFocus(self, entity):
        if not isinstance(entity, Vehicle.Vehicle):
            return
        else:
            if self.inputHandler.aim:
                self.inputHandler.aim.setTarget(entity)
            if self.__isGuiVisible and entity.isAlive():
                if self.team == entity.publicInfo['team']:
                    BigWorld.wgAddEdgeDetectEntity(entity, 2)
                else:
                    BigWorld.wgAddEdgeDetectEntity(entity, 1)
                if self.__maySeeOtherVehicleDamage and self.vehicle is not None:
                    self.cell.monitorVehicleDamage(entity.id)
            return

    def reload(self):
        self.__reloadGUI()
        self.inputHandler.setReloading(0.0)

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
        from helpers import EdgeDetectColorController
        EdgeDetectColorController.g_instance.updateColors()

    def onLeaveWorld(self):
        LOG_DEBUG('Avatar.onLeaveWorld()')
        MusicController.g_musicController.onLeaveArena()
        BigWorld.wg_setEntityUnloadable(self.playerVehicleID, False)
        BigWorld.worldDrawEnabled(False)
        BigWorld.wg_enableSpaceBoundFog(False)
        BigWorld.target.clear()
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
        try:
            self.__stippleMgr.destroy()
            self.__stippleMgr = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
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
        return

    def onKickedFromServer(self, reason, isBan, expiryTime):
        LOG_MX('onKickedFromServer', reason, isBan, expiryTime)
        from gui.Scaleform.Disconnect import Disconnect
        Disconnect.showKick(reason, isBan, expiryTime)

    def onAutoAimVehicleLost(self, lossReason):
        autoAimVehID = self.__autoAimVehID
        self.__autoAimVehID = 0
        self.inputHandler.setAimingMode(False, AIMING_MODE.TARGET_LOCK)
        self.gunRotator.clientMode = True
        if autoAimVehID and autoAimVehID not in self.__frags:
            self.soundNotifications.play('target_lost')

    def updateVehicleHealth(self, health, isCrewActive):
        rawHealth = health
        health = max(0, health)
        if health > 0:
            isAlive = isCrewActive
            wasAlive = self.__isVehicleAlive
            self.__isVehicleAlive = isAlive
            damagePanel = g_windowsManager.battleWindow.damagePanel
            damagePanel.updateHealth(health)
            if self.inputHandler.aim:
                self.inputHandler.aim.setHealth(health)
            if not isAlive and wasAlive:
                self.gunRotator.stop()
                if health > 0 and not isCrewActive:
                    damagePanel.onCrewDeactivated()
                    self.soundNotifications.play('crew_deactivated')
                    self.__deviceStates = {'crew': 'destroyed'}
                else:
                    damagePanel.onVehicleDestroyed()
                    self.soundNotifications.play('vehicle_destroyed')
                    self.__deviceStates = {'vehicle': 'destroyed'}
                battleWindow = g_windowsManager.battleWindow
                battleWindow.consumablesPanel.setDisabled(self.__currShellsIdx)
                g_windowsManager.showPostMortem()
                self.inputHandler.activatePostmortem()
                self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                self.__updateCruiseControlPanel()
                self.__stopUntilFire = False
                if rawHealth <= 0:
                    vehicle = BigWorld.entities.get(self.playerVehicleID)
                    prevHealth = vehicle is not None and vehicle.health
                    vehicle.health = rawHealth
                    vehicle.set_health(prevHealth)
        return

    def updateVehicleGunReloadTime(self, timeLeft):
        self.__gunReloadCommandWaitEndTime = 0.0
        if timeLeft == 0.0:
            self.soundNotifications.play('gun_reloaded')
            VibroReloadController()
        elif timeLeft < 0.0:
            timeLeft = -1
        self.inputHandler.setReloading(timeLeft)
        g_windowsManager.battleWindow.consumablesPanel.setCoolDownTime(self.__currShellsIdx, timeLeft)

    def updateVehicleAmmo(self, compactDescr, quantity, quantityInClip, timeRemaining):
        if not compactDescr:
            self.__processEmptyVehicleEquipment()
            return
        itemTypeIdx = getTypeOfCompactDescr(compactDescr)
        processor = self.__updateConsumablesProcessors.get(itemTypeIdx)
        if processor:
            getattr(self, processor)(compactDescr, quantity, quantityInClip, timeRemaining)
        else:
            LOG_WARNING('Not supported item type index', itemTypeIdx)

    __updateConsumablesProcessors = {ITEM_TYPE_INDICES['shell']: '_PlayerAvatar__processVehicleAmmo',
     ITEM_TYPE_INDICES['equipment']: '_PlayerAvatar__processVehicleEquipments'}

    def updateVehicleOptionalDeviceStatus(self, deviceID, isOn):
        self.__processVehicleOptionalDevices(deviceID, isOn)

    def updateVehicleMiscStatus(self, code, intArg, floatArg):
        if code == VEHICLE_MISC_STATUS.OTHER_VEHICLE_DAMAGE_VISIBLE:
            prevVal = self.__maySeeOtherVehicleDamage
            newVal = bool(intArg)
            self.__maySeeOtherVehicleDamage = newVal
            if not prevVal and newVal:
                target = BigWorld.target()
                if target is not None and isinstance(target, Vehicle.Vehicle):
                    if self.vehicle is not None:
                        self.cell.monitorVehicleDamage(target.id)
        elif code == VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED:
            if g_windowsManager.battleWindow is not None:
                g_windowsManager.battleWindow.setVehicleTimer(code, floatArg)
        elif code == VEHICLE_MISC_STATUS.VEHICLE_WILL_DROWN:
            if g_windowsManager.battleWindow is not None:
                g_windowsManager.battleWindow.setVehicleTimer(code, floatArg)
        elif code == VEHICLE_MISC_STATUS.IN_DEATH_ZONE:
            pass
        elif code == VEHICLE_MISC_STATUS.IS_OBSERVED_BY_ENEMY:
            LOG_DEBUG('IS_OBSERVED_BY_ENEMY', intArg)
        elif code == VEHICLE_MISC_STATUS.HORN_BANNED:
            self.__hornCooldown.ban(floatArg)
        return

    def updateVehicleSetting(self, code, value):
        consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
        if code == VEHICLE_SETTING.CURRENT_SHELLS:
            idx = self.__findIndexInAmmo(value)
            if idx is None:
                LOG_CODEPOINT_WARNING(code, value)
                return
            if idx == self.__currShellsIdx:
                return
            consumablesPanel.setCurrentShell(idx)
            self.__currShellsIdx = idx
            shellDescr = vehicles.getDictDescr(value)
            for shotIdx, descr in enumerate(self.vehicleTypeDescriptor.gun['shots']):
                if descr['shell']['id'] == shellDescr['id']:
                    self.vehicleTypeDescriptor.activeGunShotIndex = shotIdx
                    vehicle = BigWorld.entity(self.playerVehicleID)
                    if vehicle is not None:
                        vehicle.typeDescriptor.activeGunShotIndex = shotIdx
                    self.onGunShotChanged()
                    break

            aim = self.inputHandler.aim
            if aim is not None:
                aim.setAmmoStock(self.__ammo[idx][1])
            return
        elif code == VEHICLE_SETTING.NEXT_SHELLS:
            idx = self.__findIndexInAmmo(value)
            if idx is None:
                LOG_CODEPOINT_WARNING(code, value)
                return
            if idx == self.__nextShellsIdx:
                return
            consumablesPanel.setNextShell(idx)
            self.__nextShellsIdx = idx
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
        self.gunRotator.update(turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed)
        self.getOwnVehicleShotDispersionAngle(self.gunRotator.turretRotationSpeed)

    def updateGunMarker(self, shotPos, shotVec, dispersionAngle):
        self.gunRotator.setShotPosition(shotPos, shotVec, dispersionAngle)

    def showOwnVehicleDamageInfo(self, damageIndex, extraIndex, entityID):
        damageCode = constants.DAMAGE_INFO_CODES[damageIndex]
        extra = self.vehicleTypeDescriptor.extras[extraIndex] if extraIndex != 0 else None
        self.__showDamageIconAndPlaySound(damageCode, extra)
        self.__showVehicleDamageMessage(damageCode, extra, entityID)
        return

    def showOtherVehicleDamageInfo(self, vehicleID, damagedExtras, destroyedExtras):
        target = BigWorld.target()
        if target is None or not isinstance(target, Vehicle.Vehicle):
            if self.__maySeeOtherVehicleDamage and vehicleID != 0:
                self.cell.monitorVehicleDamage(0)
            return
        elif target.id == vehicleID:
            LOG_DEBUG('TODO: WOTD-3248', vehicleID, damagedExtras, destroyedExtras)
            return
        else:
            if self.__maySeeOtherVehicleDamage and self.vehicle is not None:
                self.cell.monitorVehicleDamage(target.id)
            LOG_DEBUG('TODO: WOTD-3248', target.id, vehicleID, damagedExtras, destroyedExtras)
            return

    def showDevelopmentInfo(self, code, arg):
        params = cPickle.loads(arg)
        if constants.HAS_DEV_RESOURCES:
            if code == DEVELOPMENT_INFO.BONUSES:
                if self.playerBonusesPanel is not None:
                    self.playerBonusesPanel.setVisible(True)
                    self.playerBonusesPanel.setContent(params)
            elif code == DEVELOPMENT_INFO.VISIBILITY:
                import Cat
                Cat.Tasks.VisibilityTest.VisibilityTestObject.setContent(params)
            else:
                LOG_MX('showDevelopmentInfo', code, params)
        return

    def showTracer(self, shooterID, shotID, effectsIndex, refStartPoint, velocity, gravity):
        if not self.userSeesWorld():
            return
        else:
            startPoint = refStartPoint
            shooter = BigWorld.entity(shooterID)
            if shooter is not None and shooter.isStarted:
                gunFirePos = Math.Matrix(shooter.appearance.modelsDesc['gun']['model'].node('HP_gunFire')).translation
                if gunFirePos.lengthSquared != 0.0:
                    startPoint = gunFirePos
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            isOwnShoot = self.playerVehicleID == shooterID
            self.__projectileMover.add(shotID, effectsDescr, gravity, refStartPoint, velocity, startPoint, isOwnShoot, BigWorld.camera().position)
            return

    def stopTracer(self, shotID, endPoint):
        if self.userSeesWorld():
            self.__projectileMover.hide(shotID, endPoint)

    def explodeProjectile(self, shotID, effectsIndex, effectMaterialIndex, endPoint, velocityDir):
        if self.userSeesWorld():
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            effectMaterial = EFFECT_MATERIALS[effectMaterialIndex]
            self.__projectileMover.explode(shotID, effectsDescr, effectMaterial, endPoint, velocityDir)

    def receiveHorn(self, vehicleID, hornID, start):
        vInfo = self.arena.vehicles.get(vehicleID, {})
        user = MessengerDispatcher.g_instance.users.getUser(vInfo.get('accountDBID', 0), vInfo.get('name'))
        if user.isIgnored() and start:
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

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        g_playerEvents.onKickedFromArena(reasonCode)

    def onVehicleLeftArena(self, isActiveVehicle, vehInvID, results):
        LOG_DEBUG('onVehicleLeftArena', isActiveVehicle, vehInvID, results.items())
        g_playerEvents.onBattleResultsReceived(isActiveVehicle, vehInvID, results)

    def updateArena(self, updateType, argStr):
        self.arena.update(updateType, argStr)

    def updatePositions(self, indices, positions):
        self.arena.updatePositions(indices, positions)

    def makeDenunciation(self, violatorID, topicID, violatorKind):
        if self.denunciationsLeft <= 0:
            return
        self.denunciationsLeft -= 1
        self.base.makeDenunciation(violatorID, topicID, violatorKind)

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
        self.__setOwnVehicleMatrixTimerID = BigWorld.callback(SERVER_TICK_LENGTH, self.__setOwnVehicleMatrixCallback)
        return

    def onStreamComplete(self, id, data):
        callback = self.__rangeStreamIDCallbacks.getCallbackForStreamID(id)
        if callback is not None:
            getattr(self, callback)(id, data)
            return
        else:
            return

    def onSpaceLoaded(self):
        LOG_DEBUG('onSpaceLoaded()')
        self.__onInitStepCompleted()

    def vehicle_onEnterWorld(self, vehicle):
        self.__stippleMgr.hideIfExistFor(vehicle)
        if vehicle.id != self.playerVehicleID:
            vehicle.targetCaps = [1]
        else:
            LOG_DEBUG('Avatar.vehicle_onEnterWorld(): own vehicle', vehicle.id)
            vehicle.isPlayer = True
            if self.__stepsTillInit != 0:
                self.vehicleTypeDescriptor = vehicle.typeDescriptor
                self.__ownVehicleMProv.setStaticTransform(Math.Matrix(vehicle.matrix))
                self.__onInitStepCompleted()
            else:
                vehicle.typeDescriptor.activeGunShotIndex = self.vehicleTypeDescriptor.activeGunShotIndex
                if self.inputHandler.aim:
                    self.inputHandler.aim.resetVehicleMatrix()
        if self.__stepsTillInit == 0 and not vehicle.isStarted:
            vehicle.startVisual()
            self.onVehicleEnterWorld(vehicle)

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

    def onMinimapCellClicked(self, cellIdx):
        if self.__isForcedGuiControlMode:
            channelID = chatManager.battleTeamChannelID
            if channelID != 0:
                ClientChat.sendChannelChatCommand(self, chatManager.battleTeamChannelID, CHAT_COMMANDS.ATTENTIONTOCELL, int16Arg=cellIdx)

    def onAmmoButtonPressed(self, idx):
        if not self.__isOnArena or not self.__isVehicleAlive:
            return
        if idx == self.__currShellsIdx and idx == self.__nextShellsIdx:
            return
        if idx not in self.__ammo.keys():
            return
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.onAmmoButtonPressed(idx)
        compactDescr, quantity, _ = self.__ammo[idx]
        if quantity <= 0:
            return
        if idx == self.__nextShellsIdx:
            code = VEHICLE_SETTING.CURRENT_SHELLS
        else:
            code = VEHICLE_SETTING.NEXT_SHELLS
        self.updateVehicleSetting(code, compactDescr)
        self.base.vehicle_changeSetting(code, compactDescr)

    def onEquipmentButtonPressed(self, idx, deviceName=None):
        if not self.__isOnArena or not self.__isVehicleAlive:
            return
        elif idx not in self.__equipment.keys():
            return
        else:
            compactDescr, quantity, time = self.__equipment[idx]
            if quantity <= 0 or compactDescr == 0 or time > 0:
                return
            artefact = vehicles.getDictDescr(compactDescr)
            if not artefact.tags or artefact.tags & frozenset(('fuel', 'stimulator')):
                return
            consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
            param = 0
            if artefact.tags & frozenset(('medkit', 'repairkit')):
                entitySuffix = 'Health'
                if deviceName is not None:
                    extra = self.vehicleTypeDescriptor.extrasDict[deviceName + entitySuffix]
                    param = (extra.index << 16) + artefact.id[1]
                elif artefact.repairAll:
                    if len(self.__deviceStates) > 0:
                        param = 65536 + artefact.id[1]
                    else:
                        self.__showPlayerError('medkitAllTankmenAreSafe' if 'medkit' in artefact.tags else 'repairkitAllDevicesAreNotDamaged')
                        return
                else:
                    vTypeDescr = self.vehicleTypeDescriptor.type
                    if 'medkit' in artefact.tags:
                        tagName = 'medkit'
                        enumRoles = {'gunner': 1,
                         'loader': 1,
                         'radioman': 1}
                        tankmen = []
                        for roles in vTypeDescr.crewRoles:
                            mainRole = roles[0]
                            if mainRole in enumRoles.keys():
                                tankmen.append(mainRole + str(enumRoles[mainRole]))
                                enumRoles[mainRole] += 1
                            else:
                                tankmen.append(mainRole)

                        entityStates = dict.fromkeys(tankmen)
                    else:
                        tagName = 'repairkit'
                        entityStates = dict.fromkeys(tuple((device.name[:-len(entitySuffix)] for device in vTypeDescr.devices)))
                    for eName in entityStates.keys():
                        state = self.__deviceStates.get(eName, None)
                        entityStates[eName] = state

                    consumablesPanel.expandEquipmentSlot(idx, tagName, entityStates)
                    return
            if artefact.tags & frozenset(('extinguisher',)):
                if not self.__fireInVehicle:
                    self.__showPlayerError('extinguisherDoesNotActivated', args={'name': artefact.userString})
                    return
                flag = self.__equipmentFlags.get(idx)
                if flag == 1:
                    self.__showPlayerError('equipmentAlreadyActivated', args={'name': artefact.userString})
                    return
                param = 65536 + artefact.id[1]
                self.__equipmentFlags[idx] = 1
            if artefact.tags & frozenset(('trigger',)):
                flag = self.__equipmentFlags.get(idx, 0)
                flag ^= 1
                param = (flag << 16) + artefact.id[1]
                self.__equipmentFlags[idx] = flag
            self.base.vehicle_changeSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, param)
            return

    def onDamageIconButtonPressed(self, tag, deviceName):
        for idx, (compactDescr, _, _) in self.__equipment.iteritems():
            if compactDescr == 0:
                continue
            eDescr = vehicles.getDictDescr(compactDescr)
            if eDescr.tags & frozenset((tag,)):
                self.onEquipmentButtonPressed(idx, deviceName=deviceName)
                return

    def onReloadPartialClipKeyDown(self):
        clipCapacity, _ = self.vehicleTypeDescriptor.gun['clip']
        if clipCapacity > 1 and self.__currShellsIdx < len(self.__ammo):
            _, quantity, quantityInClip = self.__ammo[self.__currShellsIdx]
            if quantity != 0 and quantityInClip < clipCapacity:
                self.base.vehicle_changeSetting(VEHICLE_SETTING.RELOAD_PARTIAL_CLIP, 0)

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
            self.__applyTimeAndWeatherSettings()
            self.__isSpaceInitialized = True

    def userSeesWorld(self):
        return self.__stepsTillInit == 0

    def newFakeModel(self):
        return BigWorld.Model(self.__fakeModelName)

    def leaveArena(self):
        LOG_DEBUG('Avatar.leaveArena')
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording or replayCtrl.isPlaying:
            replayCtrl.stop()
        g_playerEvents.isPlayerEntityChanging = True
        g_playerEvents.onPlayerEntityChanging()
        self.__setIsOnArena(False)
        self.base.leaveArena()

    def setForcedGuiControlMode(self, value, stopVehicle=True):
        if self.__stepsTillInit == 0:
            if self.__isForcedGuiControlMode ^ value:
                self.__doSetForcedGuiControlMode(value)
                if not value:
                    flags = self.makeVehicleMovementCommandByKeys()
                    self.moveVehicle(flags, False)
            if value and stopVehicle:
                self.moveVehicle(0, False)
        self.__isForcedGuiControlMode = value

    def enableOwnVehicleAutorotation(self, enable):
        battleWindow = g_windowsManager.battleWindow
        if battleWindow is not None:
            battleWindow.damagePanel.onVehicleAutorotationEnabled(enable)
        self.base.vehicle_changeSetting(VEHICLE_SETTING.AUTOROTATION_ENABLED, enable)
        return

    def getOwnVehiclePosition(self):
        return Math.Matrix(self.__ownVehicleMProv).translation

    def getOwnVehicleMatrix(self):
        return self.__ownVehicleMProv

    def getOwnVehicleSpeeds(self):
        if self.__ownVehicleMProv.target is None:
            return self.__lastVehicleSpeeds
        else:
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is None or not vehicle.isStarted:
                return self.__lastVehicleSpeeds
            speedInfo = vehicle.filter.speedInfo.value
            speed = speedInfo[0]
            rspeed = speedInfo[1]
            fwdSpeedLimit, bckwdSpeedLimit = vehicle.typeDescriptor.physics['speedLimits']
            if speed > fwdSpeedLimit:
                speed = fwdSpeedLimit
            elif speed < -bckwdSpeedLimit:
                speed = -bckwdSpeedLimit
            rspeedLimit = vehicle.typeDescriptor.chassis['rotationSpeed']
            if rspeed > rspeedLimit:
                rspeed = rspeedLimit
            elif rspeed < -rspeedLimit:
                rspeed = -rspeedLimit
            return (speed, rspeed)

    def getOwnVehicleShotDispersionAngle(self, turretRotationSpeed, withShot=0):
        descr = self.vehicleTypeDescriptor
        aimingStartTime, aimingStartFactor, multFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime = self.__aimingInfo
        vehicleSpeed, vehicleRSpeed = self.getOwnVehicleSpeeds()
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
        if aimingFactor < idealFactor:
            aimingFactor = idealFactor
            self.__aimingInfo[0] = currTime
            self.__aimingInfo[1] = aimingFactor
            if abs(idealFactor - multFactor) < 0.001:
                self.complexSoundNotifications.setAimingEnded(True)
            elif idealFactor / multFactor > 1.1:
                self.complexSoundNotifications.setAimingEnded(False)
        elif aimingFactor / multFactor > 1.1:
            self.complexSoundNotifications.setAimingEnded(False)
        return descr.gun['shotDispersionAngle'] * aimingFactor

    def shoot(self):
        if not self.__isOnArena:
            return
        else:
            for deviceName, stateName in self.__deviceStates.iteritems():
                msgName = self.__cantShootCriticals.get(deviceName + '_' + stateName)
                if msgName is not None:
                    self.__showPlayerError(msgName)
                    return

            if self.__currShellsIdx is None:
                return
            if self.__ammo[self.__currShellsIdx][1] == 0:
                self.__showPlayerError(self.__cantShootCriticals['no_ammo'])
                return
            if self.inputHandler.aim and self.inputHandler.aim.isGunReload():
                self.__showPlayerError(self.__cantShootCriticals['gun_reload'])
                return
            if self.__gunReloadCommandWaitEndTime > BigWorld.time():
                return
            if self.__shotWaitingTimerID is not None:
                return
            if self.isGunLocked:
                return
            self.base.vehicle_shoot()
            self.__startWaitingForShot()
            self.__burstShotResult = 0
            if self.__stopUntilFire:
                self.__stopUntilFire = False
                if BigWorld.time() - self.__stopUntilFireStartTime > 60.0:
                    self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                self.__updateCruiseControlPanel()
                self.moveVehicle(self.makeVehicleMovementCommandByKeys(), True)
            return

    __cantShootCriticals = {'gun_destroyed': 'cantShootGunDamaged',
     'vehicle_destroyed': 'cantShootVehicleDestroyed',
     'crew_destroyed': 'cantShootCrewInactive',
     'no_ammo': 'cantShootNoAmmo',
     'gun_reload': 'cantShootGunReloading'}

    def playShotResultNotification(self, result, target):
        if result is not None:
            if target.publicInfo.team != self.team:
                severity = self.__shotResultSeveritiesForEnemy[result]
            elif result < SHOT_RESULT.MIN_HIT:
                severity = 0
            else:
                severity = 3
                g_windowsManager.battleWindow.pMsgsPanel.showMessage('ALLY_HIT', {'entity': g_battleContext.getFullPlayerName(vID=target.id)}, extra=(('entity', target.id),))
            if severity > self.__burstShotResult:
                self.__burstShotResult = severity
        if result is None or self.vehicleTypeDescriptor.gun['burst'][0] == 1:
            severity = self.__burstShotResult
            self.__burstShotResult = 0
            play = self.soundNotifications.play
            if severity == 1:
                play('armor_ricochet_by_player', None if target is None else target.id)
            elif severity == 2:
                play('armor_not_pierced_by_player', None if target is None else target.id)
            elif severity == 5:
                play('armor_pierced_by_player', None if target is None else target.id)
            elif severity == 4:
                play('damage_by_near_explosion_by_player', None if target is None else target.id)
            elif severity == 6:
                play('armor_pierced_crit_by_player', None if target is None else target.id)
        return

    __shotResultSeveritiesForEnemy = (1,
     2,
     2,
     5,
     6,
     4)

    def playStartedFire(self, target):
        if self.team != target.publicInfo.team:
            self.soundNotifications.play('enemy_fire_started_by_player', target.id)

    def addBotToArena(self, vehicleTypeName, team):
        compactDescr = vehicles.VehicleDescr(typeName=vehicleTypeName).makeCompactDescr()
        self.base.addBotToArena(compactDescr, team, self.name)

    def controlAnotherVehicle(self, vehicleID, callback=None):
        BigWorld.entity(self.playerVehicleID).isPlayer = False
        self.base.controlAnotherVehicle(vehicleID, 1)
        if vehicleID not in BigWorld.entities.keys():
            BigWorld.callback(0.1, partial(self.__controlAnotherVehicleWait, vehicleID, callback, 50))
            return
        BigWorld.callback(1.0, partial(self.__controlAnotherVehicleAfteraction, vehicleID, callback))

    def autoAim(self, target):
        if target is None:
            vehID = 0
        elif not isinstance(target, Vehicle.Vehicle):
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
            if vehID != 0:
                self.inputHandler.setAimingMode(True, AIMING_MODE.TARGET_LOCK)
                self.gunRotator.clientMode = False
                self.soundNotifications.play('target_captured')
            else:
                self.inputHandler.setAimingMode(False, AIMING_MODE.TARGET_LOCK)
                self.gunRotator.clientMode = True
                self.soundNotifications.play('target_unlocked')
        return

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
            vehA.showVehicleCollisionEffect(hitPt)
            return

    def cancelWaitingForShot(self):
        if self.__shotWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__shotWaitingTimerID)
            self.__shotWaitingTimerID = None
            self.inputHandler.setAimingMode(False, AIMING_MODE.SHOOTING)
            self.gunRotator.targetLastShotPoint = False
        return

    def moveVehicleByCurrentKeys(self, isKeyDown, forceFlags=204, forceMask=0):
        moveFlags = self.makeVehicleMovementCommandByKeys(forceFlags, forceMask)
        self.moveVehicle(moveFlags, isKeyDown)

    def __onInitStepCompleted(self):
        LOG_DEBUG('Avatar.__onInitStepCompleted()', self.__stepsTillInit)
        if constants.IS_CAT_LOADED:
            if self.__stepsTillInit == 0:
                return
        assert self.__stepsTillInit > 0
        self.__stepsTillInit -= 1
        if self.__stepsTillInit != 0:
            return
        else:
            self.initSpace()
            self.__startGUI()
            DecalMap.g_instance.initGroups(1.0)
            if self.__isForcedGuiControlMode:
                self.__doSetForcedGuiControlMode(True)
            self.__setOwnVehicleMatrixCallback()
            for v in BigWorld.entities.values():
                if v.inWorld and isinstance(v, Vehicle.Vehicle) and not v.isStarted:
                    v.startVisual()
                    self.onVehicleEnterWorld(v)

            SoundGroups.g_instance.enableArenaSounds(True)
            SoundGroups.g_instance.applyPreferences()
            MusicController.g_musicController.onEnterArena()
            BigWorld.wg_setUmbraEnabled(self.arena.typeDescriptor.umbraEnabled)
            BigWorld.wg_enableTreeHiding(False)
            BigWorld.wg_enableSpaceBoundFog(True, _boundingBoxAsVector4(self.arena.typeDescriptor.boundingBox), 0.5)
            BigWorld.worldDrawEnabled(True)
            BigWorld.wg_setWaterTexScale(self.arena.typeDescriptor.waterTexScale)
            BigWorld.wg_setWaterFreqX(self.arena.typeDescriptor.waterFreqX)
            BigWorld.wg_setWaterFreqZ(self.arena.typeDescriptor.waterFreqZ)
            BattleReplay.g_replayCtrl.onClientReady()
            self.base.onClientReady()
            if self.arena.period == ARENA_PERIOD.BATTLE:
                self.__setIsOnArena(True)
            self.arena.onPeriodChange += self.__onArenaPeriodChange
            ownVehicle = BigWorld.entity(self.playerVehicleID)
            if ownVehicle is not None:
                self.updateVehicleHealth(ownVehicle.health, ownVehicle.isCrewActive)
            self.cell.autoAim(0)
            g_playerEvents.onAvatarReady()
            return

    def bbfog(self, enable, distance):
        BigWorld.wg_enableSpaceBoundFog(enable, _boundingBoxAsVector4(self.arena.typeDescriptor.boundingBox), distance)

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
        self.inputHandler = AvatarInputHandler.AvatarInputHandler()
        prereqs += self.inputHandler.prerequisites()
        BigWorld.player().arena
        self.gameInfoPanel = None
        if self.guiConfig['showFPS']:
            self.gameInfoPanel = GameInfoPanel.GameInfoPanel()
            prereqs += self.gameInfoPanel.prerequisites()
        self.playerBonusesPanel = None
        if self.guiConfig['showPlayerBonuses']:
            self.playerBonusesPanel = PlayerBonusesPanel.PlayerBonusesPanel()
            prereqs += self.playerBonusesPanel.prerequisites()
        self.soundNotifications = IngameSoundNotifications.IngameSoundNotifications()
        self.complexSoundNotifications = IngameSoundNotifications.ComplexSoundNotifications(self.soundNotifications)
        return prereqs

    def __startGUI(self):
        self.inputHandler.start()
        self.inputHandler.setReloading(-1)
        if self.gameInfoPanel is not None:
            self.gameInfoPanel.start()
        if self.playerBonusesPanel is not None:
            self.playerBonusesPanel.start()
            self.playerBonusesPanel.setVisible(False)
        self.__isGuiVisible = True
        self.arena.onVehicleKilled += self.__onArenaVehicleKilled
        MessengerDispatcher.g_instance.onBattleConnect()
        g_battleContext.init()
        battleWindow = g_windowsManager.startBattle()
        self.inputHandler.attachBattleWindow(battleWindow)
        self.soundNotifications.start()
        self.subscribeChatAction(self.__onUserChatCommand, CHAT_ACTIONS.userChatCommand)
        return

    def __destroyGUI(self):
        g_battleContext.fini()
        g_windowsManager.destroyBattle()
        if self.gameInfoPanel is not None:
            self.gameInfoPanel.destroy()
            self.gameInfoPanel = None
        if self.playerBonusesPanel is not None:
            self.playerBonusesPanel.destroy()
            self.playerBonusesPanel = None
        self.arena.onVehicleKilled -= self.__onArenaVehicleKilled
        self.unsubscribeChatAction(self.__onUserChatCommand, CHAT_ACTIONS.userChatCommand)
        self.complexSoundNotifications.destroy()
        self.complexSoundNotifications = None
        self.soundNotifications.destroy()
        self.soundNotifications = None
        self.inputHandler.stop()
        self.inputHandler = None
        return

    def __reloadGUI(self):
        self.__destroyGUI()
        self.__initGUI()
        self.__startGUI()
        self.setForcedGuiControlMode(True)
        self.setForcedGuiControlMode(False)
        print 'GUI reloaded'

    def __setVisibleGUI(self, bool):
        self.__isGuiVisible = bool
        from gui.Scaleform.Battle import Battle
        if isinstance(g_windowsManager.window, Battle):
            g_windowsManager.window.showAll(bool)
        self.inputHandler.setGUIVisible(bool)

    def __doSetForcedGuiControlMode(self, value):
        self.inputHandler.detachCursor(value)

    def makeVehicleMovementCommandByKeys(self, forceFlags=204, forceMask=0):
        cmdMap = CommandMapping.g_instance
        flags = 0
        if self.__stopUntilFire:
            return flags
        if cmdMap.isActiveList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC)):
            flags = 1
        elif cmdMap.isActive(CommandMapping.CMD_MOVE_BACKWARD):
            flags = 2
        else:
            if self.__cruiseControlMode >= _CRUISE_CONTROL_MODE.FWD25:
                flags = 1
            elif self.__cruiseControlMode <= _CRUISE_CONTROL_MODE.BCKW50:
                flags = 2
            if not self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD50:
                isOn = self.__cruiseControlMode == _CRUISE_CONTROL_MODE.BCKW50
                isOn and flags |= 16
            elif self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD25:
                flags |= 32
        if cmdMap.isActive(CommandMapping.CMD_ROTATE_LEFT):
            flags |= 4
        if cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
            flags |= 8
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

    __cantMoveCriticals = {'engine_destroyed': 'cantMoveEngineDamaged',
     'leftTrack_destroyed': 'cantMoveChassisDamaged',
     'rightTrack_destroyed': 'cantMoveChassisDamaged',
     'vehicle_destroyed': 'cantMoveVehicleDestroyed',
     'crew_destroyed': 'cantMoveCrewInactive'}

    def __setIsOnArena(self, onArena):
        if self.__isOnArena == onArena:
            return
        self.__isOnArena = onArena
        if not onArena:
            self.gunRotator.stop()
        else:
            self.gunRotator.start()
            if not self.__isForcedGuiControlMode:
                self.moveVehicle(self.makeVehicleMovementCommandByKeys(), False)

    def __showPlayerError(self, msgName, args=None):
        g_windowsManager.battleWindow.vErrorsPanel.showMessage(msgName, args)

    def __showDamageIconAndPlaySound(self, damageCode, extra):
        damagePanel = g_windowsManager.battleWindow.damagePanel
        consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
        deviceName = None
        deviceState = None
        soundType = None
        if damageCode in self.__damageInfoFire:
            extra = self.vehicleTypeDescriptor.extrasDict['fire']
            self.__fireInVehicle = damageCode != 'FIRE_STOPPED'
            soundType = 'critical' if self.__fireInVehicle else 'fixed'
            damagePanel.onFireInVehicle(self.__fireInVehicle)
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
            if vehicle is not None:
                vehicle.appearance.executeCriticalHitVibrations(vehicle, extra.name)
        elif damageCode in self.__damageInfoHealings:
            deviceName = extra.name[:-len('Health')]
            deviceState = 'normal'
            soundType = 'fixed'
            self.__deviceStates.pop(deviceName, None)
        if deviceState is not None:
            damagePanel.updateCriticalIcon(deviceName, deviceState)
            consumablesPanel.updateExpandedEquipmentSlot(deviceName, deviceState)
            aim = self.inputHandler.aim
            if aim is not None:
                aim.updateTankState(deviceName, deviceState)
        if soundType is not None:
            sound = extra.sounds.get(soundType)
            if sound is not None:
                self.soundNotifications.play(sound)
        return

    __damageInfoCriticals = ('DEVICE_CRITICAL',
     'DEVICE_REPAIRED_TO_CRITICAL',
     'DEVICE_CRITICAL_AT_SHOT',
     'DEVICE_CRITICAL_AT_RAMMING',
     'DEVICE_CRITICAL_AT_FIRE',
     'ENGINE_CRITICAL_AT_UNLIMITED_RPM')
    __damageInfoDestructions = ('DEVICE_DESTROYED',
     'DEVICE_DESTROYED_AT_SHOT',
     'DEVICE_DESTROYED_AT_RAMMING',
     'DEVICE_DESTROYED_AT_FIRE',
     'TANKMAN_HIT',
     'TANKMAN_HIT_AT_SHOT',
     'ENGINE_DESTROYED_AT_UNLIMITED_RPM')
    __damageInfoHealings = ('DEVICE_REPAIRED', 'TANKMAN_RESTORED', 'FIRE_STOPPED')
    __damageInfoFire = ('FIRE',
     'DEVICE_STARTED_FIRE_AT_SHOT',
     'DEVICE_STARTED_FIRE_AT_RAMMING',
     'FIRE_STOPPED')

    def __showVehicleDamageMessage(self, damageCode, extra, entityID):
        if damageCode in self.__damageInfoNoMessage:
            return
        else:
            names = {}
            if extra is not None:
                names['device'] = extra.deviceUserString
            if entityID != 0:
                vehicleInfo = self.arena.vehicles.get(entityID)
                if vehicleInfo is None:
                    LOG_CODEPOINT_WARNING()
                    return
                names['entity'] = g_battleContext.getFullPlayerName(vehicleInfo)
            g_windowsManager.battleWindow.vMsgsPanel.showMessage(damageCode, names)
            return

    __damageInfoNoMessage = ('DEVICE_CRITICAL',
     'DEVICE_DESTROYED',
     'TANKMAN_HIT',
     'FIRE')

    def __setOwnVehicleMatrixCallback(self):
        self.__setOwnVehicleMatrixTimerID = None
        assert self.__ownVehicleMProv.target is None
        vehicle = self.vehicle
        if vehicle is not None and not vehicle.isDestroyed and vehicle.isStarted and vehicle.id == self.playerVehicleID:
            self.__ownVehicleMProv.target = vehicle.matrix
            return
        else:
            self.__setOwnVehicleMatrixTimerID = BigWorld.callback(SERVER_TICK_LENGTH, self.__setOwnVehicleMatrixCallback)
            self.positionControl.onFollowCameraTick()
            return

    def __onArenaVehicleKilled(self, targetID, attackerID, reason):
        if targetID == self.playerVehicleID:
            self.inputHandler.setKillerVehicleID(attackerID)
            return
        else:
            playerMessagesPanel = g_windowsManager.battleWindow.pMsgsPanel
            if attackerID == self.playerVehicleID:
                targetInfo = self.arena.vehicles.get(targetID)
                if targetInfo is None:
                    LOG_CODEPOINT_WARNING()
                    return
                self.__frags.add(targetID)
                if targetInfo['team'] != self.team:
                    msg = 'player_frag'
                    self.soundNotifications.cancel('armor_pierced_by_player', False)
                    self.soundNotifications.play('enemy_killed_by_player')
                else:
                    msg = 'player_friendly_fire_frag'
                    self.soundNotifications.play('ally_killed_by_player')
                playerMessagesPanel.showMessage(msg, {'target': g_battleContext.getFullPlayerName(targetInfo)}, extra=(('target', targetID),))
                return
            targetInfo = self.arena.vehicles.get(targetID)
            attackerInfo = self.arena.vehicles.get(attackerID)
            if targetInfo is None or attackerInfo is None:
                LOG_CODEPOINT_WARNING()
                return
            targetTeam = targetInfo['team']
            attackerTeam = attackerInfo['team']
            if targetID == attackerID:
                msg = 'ally_suicide' if targetTeam == self.team else 'enemy_suicide'
                playerMessagesPanel.showMessage(msg, {'entity': g_battleContext.getFullPlayerName(targetInfo)}, extra=(('entity', targetID),))
                return
            if attackerTeam == self.team:
                if attackerTeam != targetTeam:
                    msg = 'ally_frag'
                else:
                    msg = 'ally_friendly_fire_frag'
            else:
                msg = 'enemy_frag' if attackerTeam != targetTeam else 'enemy_friendly_fire_frag'
            playerMessagesPanel.showMessage(msg, {'target': g_battleContext.getFullPlayerName(targetInfo),
             'attacker': g_battleContext.getFullPlayerName(attackerInfo)}, extra=(('target', targetID), ('attacker', attackerID)))
            return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        self.__setIsOnArena(period == ARENA_PERIOD.BATTLE)
        if period == ARENA_PERIOD.PREBATTLE and period > self.__prevArenaPeriod:
            LightManager.GameLights.startTicks()
        if period == ARENA_PERIOD.BATTLE and period > self.__prevArenaPeriod:
            self.soundNotifications.play('start_battle')
            LightManager.GameLights.roundStarted()
        self.__prevArenaPeriod = period

    def __onUserChatCommand(self, commandData):
        messenger = MessengerDispatcher.g_instance
        user = messenger.users.getUser(commandData['originator'], commandData['originatorNickName'])
        if not user.himself and user.isIgnored():
            LOG_DEBUG('chat command is ignored', dict(commandData))
            return
        else:
            vmManager = g_windowsManager.battleWindow.vMarkersManager
            cmd = CHAT_COMMANDS[commandData['data'][0]]
            if cmd != CHAT_COMMANDS.ATTENTIONTOCELL:
                self.soundNotifications.play('chat_shortcut_common_fx')
            if cmd == CHAT_COMMANDS.ATTENTIONTOCELL:
                cellIdx = commandData['data'][2]
                g_windowsManager.battleWindow.minimap.markCell(cellIdx, 3.0)
                cellName = g_windowsManager.battleWindow.minimap.getCellName(cellIdx)
                commandData['data'] = i18n.makeString(cmd.msgText, cellName)
                messenger.currentWindow.addChannelMessage(ChatActionWrapper(**dict(commandData)))
                return
            if cmd == CHAT_COMMANDS.ATTACKENEMY:
                vehID = commandData['data'][1]
                vehInfo = self.arena.vehicles.get(vehID)
                if vehInfo is None or vehInfo['team'] == self.team:
                    return
                g_windowsManager.battleWindow.minimap.showActionMarker(vehID, cmd.vehMarker)
                vehicle, vehicleId = self.__findNonPlayerVehicleByName(user.uid)
                if vehicleId:
                    g_windowsManager.battleWindow.minimap.showActionMarker(vehicleId, 'attackSender')
                vehicle = BigWorld.entity(vehID)
                if vehicle is not None and vehicle.isStarted:
                    vmManager.showActionMarker(vehicle.marker, cmd.vehMarker)
                commandData['data'] = i18n.makeString(cmd.msgText, vehInfo['name'])
                messenger.currentWindow.addChannelMessage(ChatActionWrapper(**dict(commandData)))
                return
            commandData['data'] = i18n.makeString(cmd.msgText)
            messenger.currentWindow.addChannelMessage(ChatActionWrapper(**dict(commandData)))
            markerName = cmd.get('vehMarker')
            if markerName is not None:
                vehicle, vehicleId = self.__findNonPlayerVehicleByName(user.uid)
                if vehicle is not None:
                    vmManager.showActionMarker(vehicle.marker, markerName)
                if vehicleId:
                    g_windowsManager.battleWindow.minimap.showActionMarker(vehicleId, markerName)
            return

    def __findNonPlayerVehicleByName(self, accDBID):
        result = (None, None)
        vehID = g_battleContext.getVehIDByAccDBID(accDBID)
        if vehID:
            vehicle = BigWorld.entities.get(vehID)
            if vehicle is not None and (not vehicle.isStarted or vehicle.isPlayer):
                vehicle = None
            result = (vehicle, vehID)
        return result

    def __onChatShortcutAttackMyTarget(self):
        if not self.__isVehicleAlive:
            return
        else:
            target = BigWorld.target()
            if target is None or not isinstance(target, Vehicle.Vehicle):
                return
            if target.publicInfo.team == self.team:
                return
            if not target.isAlive():
                return
            channelID = chatManager.battleTeamChannelID
            if channelID != 0:
                ClientChat.sendChannelChatCommand(self, chatManager.battleTeamChannelID, CHAT_COMMANDS.ATTACKENEMY, int64Arg=target.id)
            return

    def __onChatShortcut(self, cmdName):
        if not self.__isVehicleAlive:
            return
        channelID = chatManager.battleTeamChannelID
        if channelID != 0:
            ClientChat.sendChannelChatCommand(self, chatManager.battleTeamChannelID, getattr(CHAT_COMMANDS, cmdName))

    def __startWaitingForShot(self):
        if self.__shotWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__shotWaitingTimerID)
            self.__shotWaitingTimerID = None
        timeout = BigWorld.LatencyInfo().value[3] * 0.5
        timeout = min(_SHOT_WAITING_MAX_TIMEOUT, timeout)
        timeout = max(_SHOT_WAITING_MIN_TIMEOUT, timeout)
        self.__shotWaitingTimerID = BigWorld.callback(timeout, self.__showTimedOutShooting)
        self.inputHandler.setAimingMode(True, AIMING_MODE.SHOOTING)
        self.gunRotator.targetLastShotPoint = True
        self.__gunReloadCommandWaitEndTime = BigWorld.time() + 2.0
        return

    def __showTimedOutShooting(self):
        self.__shotWaitingTimerID = None
        self.inputHandler.setAimingMode(False, AIMING_MODE.SHOOTING)
        self.gunRotator.targetLastShotPoint = False
        try:
            vehicle = BigWorld.entity(self.playerVehicleID)
            gunDescr = vehicle is not None and vehicle.isStarted and vehicle.typeDescriptor.gun
            burstCount = gunDescr['burst'][0]
            if self.__currShellsIdx is not None:
                totalShots, shotsInClip = self.__ammo[self.__currShellsIdx][1:3]
                if burstCount > totalShots > 0:
                    burstCount = totalShots
                if gunDescr['clip'][0] > 1:
                    if burstCount > shotsInClip > 0:
                        burstCount = shotsInClip
                vehicle.showShooting(burstCount, True)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    def __findIndexInAmmo(self, compactDescr):
        for idx, (value, _, _) in self.__ammo.iteritems():
            if compactDescr == value:
                return idx

        return None

    def __findIndexInEquipment(self, compactDescr):
        for idx, (value, _, _) in self.__equipment.iteritems():
            if compactDescr == value:
                return idx

        return None

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
        LOG_NOTE('Arena type: ', self.arena.typeDescriptor.typeName)
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
        msg += '\tarena: %s\n' % self.arena.typeDescriptor.typeName
        msg += '\tposition: ' + str(self.position)
        LOG_NOTE(msg)
        self.base.setDevelopmentFeature('log_lag', True)

    def __updateCruiseControlPanel(self):
        aim = self.inputHandler.aim
        if aim is None:
            return
        else:
            if self.__stopUntilFire or not self.__isVehicleAlive:
                aim.setCruiseMode(_CRUISE_CONTROL_MODE.NONE)
            else:
                aim.setCruiseMode(self.__cruiseControlMode)
            return

    def __applyTimeAndWeatherSettings(self, overridePresetID=None):
        presets = self.arena.typeDescriptor.weatherPresets
        weather = Weather.weather()
        if len(presets) == 0 or presets[0].get('name') is None:
            weather.summon('Clear', immediate=True)
            return
        else:
            try:
                presetID = overridePresetID if overridePresetID is not None else self.weatherPresetID
                preset = presets[presetID]
                weather.summon(preset['name'], immediate=True)
                hour = preset.get('hour')
                if hour is not None:
                    BigWorld.wg_setHourOfDay(float(hour))
                fogDensity = preset.get('fogDensity')
                if fogDensity is None:
                    fogDensity = weather.getFog()[3]
                else:
                    fogDensity = float(fogDensity)
                fogColor = preset.get('fogColor')
                if fogColor is None:
                    fogColor = weather.getFog()
                else:
                    fogColor = fogColor.split()
                    fogColor = (float(fogColor[0]), float(fogColor[1]), float(fogColor[2]))
                weather.fog((fogColor[0],
                 fogColor[1],
                 fogColor[2],
                 fogDensity))
                rain = preset.get('rain')
                if rain is not None:
                    weather.rain(rain)
                ambientLight = preset.get('ambientLight')
                if ambientLight is not None:
                    ambientLight = ambientLight.split()
                    if len(ambientLight) == 1:
                        weather.ambient(Math.Vector4(float(ambientLight[0])))
                    elif len(ambientLight) >= 3:
                        weather.ambient(Math.Vector4(float(ambientLight[0]), float(ambientLight[1]), float(ambientLight[2]), 1.0))
                sunLight = preset.get('sunLight')
                if sunLight is not None:
                    sunLight = sunLight.split()
                    if len(sunLight) == 1:
                        weather.sun(Math.Vector4(float(sunLight[0])))
                    elif len(sunLight) >= 3:
                        weather.sun(Math.Vector4(float(sunLight[0]), float(sunLight[1]), float(sunLight[2]), 1.0))
            except Exception:
                LOG_CURRENT_EXCEPTION()
                LOG_DEBUG("Weather system's ID was:", self.weatherPresetID)

            return

    def __processVehicleAmmo(self, compactDescr, quantity, quantityInClip, _):
        consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
        idx = self.__findIndexInAmmo(compactDescr)
        if idx is not None:
            prevAmmo = self.__ammo.get(idx)
            self.__ammo[idx] = (compactDescr, quantity, quantityInClip)
            consumablesPanel.setShellQuantityInSlot(idx, quantity, quantityInClip)
            if idx == self.__currShellsIdx:
                isCassetteReload = (False if prevAmmo is None else quantityInClip > 0 and prevAmmo[2] == 0) and quantity == prevAmmo[1]
                if not isCassetteReload:
                    self.getOwnVehicleShotDispersionAngle(self.gunRotator.turretRotationSpeed, 1)
                aim = self.inputHandler.aim
                if aim is not None:
                    aim.setAmmoStock(quantity)
            return
        else:
            idx = self.__nextCSlotIdx
            self.__nextCSlotIdx += 1
            self.__ammo[idx] = (compactDescr, quantity, quantityInClip)
            shellDescr = vehicles.getDictDescr(compactDescr)
            for _, shotDescr in enumerate(self.vehicleTypeDescriptor.gun['shots']):
                if shotDescr['shell']['id'] == shellDescr['id']:
                    break

            clipCapacity, _ = self.vehicleTypeDescriptor.gun['clip']
            consumablesPanel.addShellSlot(idx, quantity, quantityInClip, clipCapacity, shellDescr, shotDescr['piercingPower'])
            return

    def __processVehicleEquipments(self, compactDescr, quantity, _, timeRemaining):
        consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
        idx = self.__findIndexInEquipment(compactDescr)
        if idx is not None:
            self.__equipment[idx] = (compactDescr, quantity, timeRemaining)
            if not timeRemaining and quantity > 0 and idx in self.__equipmentFlags:
                self.__equipmentFlags[idx] = 0
            consumablesPanel.setItemQuantityInSlot(idx, quantity)
            consumablesPanel.setCoolDownTime(idx, timeRemaining)
            return
        else:
            self.__nextCSlotIdx = consumablesPanel.checkEquipmentSlotIdx(self.__nextCSlotIdx)
            idx = self.__nextCSlotIdx
            self.__nextCSlotIdx += 1
            self.__equipment[idx] = (compactDescr, quantity, timeRemaining)
            eDescr = vehicles.getDictDescr(compactDescr)
            consumablesPanel.addEquipmentSlot(idx, quantity, eDescr)
            if timeRemaining:
                consumablesPanel.setCoolDownTime(idx, timeRemaining)
                if eDescr.tags & frozenset(('trigger', 'extinguisher')):
                    self.__equipmentFlags[idx] = 1
            return

    def __processEmptyVehicleEquipment(self):
        consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
        self.__nextCSlotIdx = consumablesPanel.checkEquipmentSlotIdx(self.__nextCSlotIdx)
        idx = self.__nextCSlotIdx
        self.__nextCSlotIdx += 1
        self.__equipment[idx] = (0, 0, 0)
        consumablesPanel.addEmptyEquipmentSlot(idx)

    def __processVehicleOptionalDevices(self, deviceID, isOn):
        consumablesPanel = g_windowsManager.battleWindow.consumablesPanel
        idx = self.__optionalDevices.get(deviceID)
        if idx is None:
            idx = self.__nextCSlotIdx
            self.__nextCSlotIdx += 1
            self.__optionalDevices[deviceID] = idx
            consumablesPanel.addOptionalDevice(idx, vehicles.g_cache.optionalDevices()[deviceID])
        consumablesPanel.setCoolDownTime(idx, -1 if isOn else 0)
        return


def preload(alist):
    ds = ResMgr.openSection('precache.xml')
    if ds is not None:
        for sec in ds.values():
            alist.append(sec.asString)

    return


def _boundingBoxAsVector4(bb):
    return Math.Vector4(bb[0][0], bb[0][1], bb[1][0], bb[1][1])


Avatar = PlayerAvatar
