# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Avatar.py
import cPickle
import math
import zlib
from functools import partial
import BigWorld
import Keys
import Math
import ResMgr
import WWISE
import WoT
import Account
import AccountCommands
import AreaDestructibles
import AuxiliaryFx
import AvatarInputHandler
import AvatarPositionControl
import BattleReplay
import ClientArena
import CommandMapping
import Event
import FlockManager
import MusicControllerWWISE
import ProjectileMover
import SoundGroups
import TriggersManager
import Vehicle
import Weather
import constants
from AimSound import AimSound
from AvatarInputHandler import cameras
from AvatarInputHandler.control_modes import ArcadeControlMode, VideoCameraControlMode, PostMortemControlMode
from BattleReplay import CallbackDataNames
from ChatManager import chatManager
from ClientChat import ClientChat
from Flock import DebugLine
from LightFx import LightManager
from OfflineMapCreator import g_offlineMapCreator
from PlayerEvents import g_playerEvents
from TriggersManager import TRIGGER_TYPE
from Vibroeffects.Controllers.ReloadController import ReloadController as VibroReloadController
from account_helpers import BattleResultsCache
from account_helpers import ClientInvitations
from account_helpers.settings_core.settings_constants import SOUND
from avatar_helpers import AvatarSyncData
from battle_results_shared import AVATAR_PRIVATE_STATS, listToDict
from bootcamp.Bootcamp import g_bootcamp
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from constants import ARENA_PERIOD, AIMING_MODE, VEHICLE_SETTING, DEVELOPMENT_INFO, ARENA_GUI_TYPE
from constants import DROWN_WARNING_LEVEL
from constants import TARGET_LOST_FLAGS
from constants import VEHICLE_MISC_STATUS, VEHICLE_HIT_FLAGS
from constants import VEHICLE_SIEGE_STATE
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG_DEV, LOG_CODEPOINT_WARNING, LOG_NOTE
from gui import GUI_CTRL_MODE_FLAG, IngameSoundNotifications, SystemMessages
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.READABLE_KEY_NAMES import READABLE_KEY_NAMES
from gui.app_loader import g_appLoader, settings as app_settings
from gui.battle_control import BattleSessionSetup
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CANT_SHOOT_ERROR, DestroyTimerViewState, DeathZoneTimerViewState
from gui.prb_control.formatters import messages
from gui.wgnc import g_wgncProvider
from gun_rotation_shared import decodeGunAngles, isShootPositionInsideOtherVehicle
from helpers import DecalMap
from helpers import bound_effects
from helpers import dependency, uniprof
from helpers.i18n import makeString
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles
from items.vehicles import VEHICLE_ATTRIBUTE_FACTORS
from material_kinds import EFFECT_MATERIALS
from messenger import MessengerEntry, g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from physics_shared import computeBarrelLocalPoint
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.helpers.statistics import IStatisticsCollector
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN, STREAM_ID_AVATAR_BATTLE_RESULS
from avatar_components.CombatEquipmentManager import CombatEquipmentManager
from avatar_components.AvatarObserver import AvatarObserver
from avatar_components.avatar_epic_data import AvatarEpicData
from avatar_components.avatar_recovery_mechanic import AvatarRecoveryMechanic
from avatar_components.avatar_respawn_mechanic import AvatarRespawnMechanic
from avatar_components.team_healthbar_mechanic import TeamHealthbarMechanic
from vehicle_systems import appearance_cache
from vehicle_systems.stipple_manager import StippleManager
from AvatarInputHandler.epic_battle_death_mode import DeathFreeCamMode
from AvatarInputHandler.RespawnDeathMode import RespawnDeathMode
from gui.sounds.epic_sound_constants import EPIC_SOUND

class _CRUISE_CONTROL_MODE(object):
    NONE = 0
    FWD25 = 1
    FWD50 = 2
    FWD100 = 3
    BCKW50 = -1
    BCKW100 = -2


_SHOT_WAITING_MAX_TIMEOUT = 0.2
_SHOT_WAITING_MIN_TIMEOUT = 0.12

class _MOVEMENT_FLAGS(object):
    FORWARD = 1
    BACKWARD = 2
    ROTATE_LEFT = 4
    ROTATE_RIGHT = 8
    CRUISE_CONTROL50 = 16
    CRUISE_CONTROL25 = 32
    BLOCK_TRACKS = 64


class ClientVisibilityFlags(object):
    CLIENT_MASK = 4293918720L
    SERVER_MASK = 1048575

    @staticmethod
    def updateSpaceVisibility(spaceID, clientVisibilityFlags):
        existingVisibilityFlags = BigWorld.wg_getSpaceItemsVisibilityMask(spaceID)
        existingVisibilityFlags &= ClientVisibilityFlags.SERVER_MASK
        BigWorld.wg_setSpaceItemsVisibilityMask(spaceID, clientVisibilityFlags | existingVisibilityFlags)

    OBSERVER_OBJECTS = 2147483648L


class _INIT_STEPS(object):
    SPACE_LOADED = 1
    ENTERED_WORLD = 2
    SET_PLAYER_ID = 4
    VEHICLE_ENTERED = 8
    ALL_STEPS_PASSED = SPACE_LOADED | ENTERED_WORLD | SET_PLAYER_ID | VEHICLE_ENTERED
    INIT_COMPLETED = 16
    PLAYER_READY = 32


AVATAR_COMPONENTS = {CombatEquipmentManager,
 AvatarObserver,
 TeamHealthbarMechanic,
 AvatarEpicData,
 AvatarRecoveryMechanic,
 AvatarRespawnMechanic}

class PlayerAvatar(BigWorld.Entity, ClientChat, CombatEquipmentManager, AvatarObserver, TeamHealthbarMechanic, AvatarEpicData, AvatarRecoveryMechanic, AvatarRespawnMechanic):
    __onStreamCompletePredef = {STREAM_ID_AVATAR_BATTLE_RESULS: 'receiveBattleResults'}
    isOnArena = property(lambda self: self.__isOnArena)
    isVehicleAlive = property(lambda self: self.__isVehicleAlive)
    isWaitingForShot = property(lambda self: self.__isWaitingForShot)
    isInTutorial = property(lambda self: self.arena is not None and self.arena.guiType == constants.ARENA_GUI_TYPE.TUTORIAL)
    autoAimVehicle = property(lambda self: BigWorld.entities.get(self.__autoAimVehID, None))
    fireInVehicle = property(lambda self: self.__fireInVehicle)
    deviceStates = property(lambda self: self.__deviceStates)
    vehicles = property(lambda self: self.__vehicles)
    consistentMatrices = property(lambda self: self.__consistentMatrices)
    isVehicleOverturned = property(lambda self: self.__isVehicleOverturned)
    isOwnBarrelUnderWater = property(lambda self: self.__isOwnBarrelUnderWater())
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        LOG_DEBUG('client Avatar.init')
        ClientChat.__init__(self)
        for comp in AVATAR_COMPONENTS:
            comp.__init__(self)

        self._muteSounds = ()
        if not BattleReplay.isPlaying():
            self.syncData = AvatarSyncData.AvatarSyncData()
            self.syncData.setAvatar(self)
            repository = Account.g_accountRepository
            if repository is not None:
                self.intUserSettings = repository.intUserSettings
                if self.intUserSettings is not None:
                    self.intUserSettings.setProxy(self, self.syncData)
                self.prebattleInvitations = repository.prebattleInvitations
            else:
                self.intUserSettings = None
                self.prebattleInvitations = None
        else:
            self.intUserSettings = None
            self.prebattleInvitations = ClientInvitations.ReplayClientInvitations(g_playerEvents)
        if self.prebattleInvitations is not None:
            self.prebattleInvitations.setProxy(self)
        self.__rangeStreamIDCallbacks = RangeStreamIDCallbacks()
        self.__rangeStreamIDCallbacks.addRangeCallback((STREAM_ID_CHAT_MIN, STREAM_ID_CHAT_MAX), '_ClientChat__receiveStreamedData')
        self.__onCmdResponse = {}
        self.__requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN
        self.__prevArenaPeriod = -1
        self.__tryShootCallbackId = None
        self.__fwdSpeedometerLimit = None
        self.__bckwdSpeedometerLimit = None
        self.isTeleport = False
        self.__isObserver = None
        self.__fireNonFatalDamageTriggerID = None
        if constants.HAS_DEV_RESOURCES:
            from avatar_helpers import VehicleTelemetry
            self.telemetry = VehicleTelemetry.VehicleTelemetry(self)
        else:
            self.telemetry = None
        self.__initProgress = 0
        self.__shotWaitingTimerID = None
        self.__isWaitingForShot = False
        self.__projectileMover = None
        self.positionControl = None
        self.__disableRespawnMode = False
        self.__pendingSiegeSettings = None
        self.__flockMangager = FlockManager.getManager()
        self.gunRotator = None
        self.inputHandler = None
        self.__vehicles = set()
        self.__consistentMatrices = AvatarPositionControl.ConsistentMatrices()
        self.__ownVehicleMProv = self.__consistentMatrices.ownVehicleMatrix
        self.__isVehicleOverturned = False
        self.__battleResults = None
        DecalMap.g_instance.initGroups(1.0)
        self.__gunDamagedShootSound = None
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.GUN_DAMAGE_SOUND, self.__gunDamagedSound)
        self.__aimingBooster = None
        self.__hackSpaceKeeper = None
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def onBecomePlayer(self):
        uniprof.enterToRegion('avatar.entering')
        LOG_DEBUG('[INIT_STEPS] Avatar.onBecomePlayer')
        for comp in AVATAR_COMPONENTS:
            comp.onBecomePlayer(self)

        BigWorld.cameraSpaceID(0)
        BigWorld.camera(BigWorld.CursorCamera())
        chatManager.switchPlayerProxy(self)
        g_playerEvents.isPlayerEntityChanging = False
        self.__isSpaceInitialized = False
        self.__isOnArena = False
        uniprof.enterToRegion('avatar.arena.loading')
        BigWorld.enableLoadingTimer(True)
        self.arena = ClientArena.ClientArena(self.arenaUniqueID, self.arenaTypeID, self.arenaBonusType, self.arenaGuiType, self.arenaExtraData, self.weatherPresetID)
        if self.arena.arenaType is None:
            import game
            game.abort()
            return
        else:
            self.vehicleTypeDescriptor = None
            self.terrainEffects = bound_effects.StaticSceneBoundEffects()
            self.filter = BigWorld.AvatarFilter()
            self.filter.enableLagDetection(True)
            self.onVehicleEnterWorld = Event.Event()
            self.onVehicleLeaveWorld = Event.Event()
            self.onGunShotChanged = Event.Event()
            self.invRotationOnBackMovement = False
            self.__isVehicleAlive = True
            self.__firstHealthUpdate = True
            self.__deadOnLoading = False
            self.__isRespawnAvailable = False
            self.__ownVehicleStabMProv = Math.WGAdaptiveMatrixProvider()
            self.__ownVehicleStabMProv.setStaticTransform(Math.Matrix())
            self.__lastVehicleSpeeds = (0.0, 0.0)
            self.__aimingInfo = [0.0,
             0.0,
             1.0,
             0.0,
             0.0,
             0.0,
             1.0]
            if not g_offlineMapCreator.Active():
                self.guiSessionProvider.start(BattleSessionSetup(avatar=self, replayCtrl=BattleReplay.g_replayCtrl))
            if BattleReplay.isPlaying() and self.arenaGuiType == ARENA_GUI_TYPE.BOOTCAMP:
                arenaInfo = BattleReplay.g_replayCtrl.arenaInfo
                lessonId = arenaInfo.get('lessonId', None)
                bootcampCtx = arenaInfo.get('bootcampCtx', None)
                if bootcampCtx is not None:
                    g_bootcamp.setContext(g_bootcamp.deserializeContext(bootcampCtx))
                if lessonId is not None:
                    g_bootcamp.start(lessonId, True)
            self.__fireInVehicle = False
            self.__forcedGuiCtrlModeFlags = GUI_CTRL_MODE_FLAG.CURSOR_DETACHED
            self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
            self.__stopUntilFire = False
            self.__stopUntilFireStartTime = -1
            self.__lastTimeOfKeyDown = -1
            self.__lastKeyDown = Keys.KEY_NONE
            self.__numSimilarKeyDowns = 0
            self.__stippleMgr = StippleManager()
            self.target = None
            self.__autoAimVehID = 0
            self.__shotWaitingTimerID = None
            self.__isWaitingForShot = False
            self.__gunReloadCommandWaitEndTime = 0.0
            self.__prevGunReloadTimeLeft = -1.0
            self.__frags = set()
            self.__vehicleToVehicleCollisions = {}
            self.__deviceStates = {}
            self.__maySeeOtherVehicleDamagedDevices = False
            if self.intUserSettings is not None:
                self.intUserSettings.onProxyBecomePlayer()
                self.syncData.onAvatarBecomePlayer()
            if self.prebattleInvitations is not None:
                self.prebattleInvitations.onProxyBecomePlayer()
            g_playerEvents.onAvatarBecomePlayer()
            self.__staticCollisionEffectID = None
            self.__drownWarningLevel = DROWN_WARNING_LEVEL.SAFE
            BigWorld.wg_clearDecals()
            BigWorld.target.caps(1)
            self.bwProto.voipController.invalidateMicrophoneMute()
            from helpers import EdgeDetectColorController
            EdgeDetectColorController.g_instance.updateColors()
            self.statsCollector.start()
            self.__prereqs = dict()
            self.loadPrerequisites(self.__initGUI())
            self.__projectileMover = ProjectileMover.ProjectileMover()
            SoundGroups.g_instance.enableArenaSounds(False)
            self.__flockMangager.start(self)
            appearance_cache.init(self.arena)
            self.__gunDamagedShootSound = SoundGroups.g_instance.getSound2D('gun_damaged')
            if not g_offlineMapCreator.Active():
                self.cell.switchObserverFPV(False)
            BigWorld.worldDrawEnabled(False)
            uniprof.exitFromRegion('avatar.entering')
            return

    def loadPrerequisites(self, prereqs):
        from battleground.StunAreaManager import g_stunAreaManager
        g_stunAreaManager.loadPrerequisites()
        BigWorld.loadResourceListBG(prereqs, partial(self.onPrereqsLoaded, prereqs))

    def onPrereqsLoaded(self, resNames, resourceRefs):
        failedRefs = resourceRefs.failedIDs
        for resName in resNames:
            if resName not in failedRefs:
                self.__prereqs[resName] = resourceRefs[resName]
            LOG_WARNING('Resource is not found', resName)

    def onBecomeNonPlayer(self):
        uniprof.exitFromRegion('avatar.arena.battle')
        uniprof.enterToRegion('avatar.exiting')
        LOG_DEBUG('[INIT_STEPS] Avatar.onBecomeNonPlayer')
        try:
            if self.gunRotator is not None:
                self.gunRotator.destroy()
                self.gunRotator = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.__destroyGUI()
        self.__flockMangager.stop(self)
        self.statsCollector.stop()
        from battleground.StunAreaManager import g_stunAreaManager
        g_stunAreaManager.clear()
        BigWorld.worldDrawEnabled(False)
        BigWorld.target.clear()
        MusicControllerWWISE.onLeaveArena()
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.enable(False)
        for v in BigWorld.entities.values():
            if isinstance(v, Vehicle.Vehicle) and v.isStarted:
                self.onVehicleLeaveWorld(v)
                v.stopVisual(False)

        try:
            self.__stippleMgr.destroy()
            self.__stippleMgr = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        if self.__initProgress & _INIT_STEPS.INIT_COMPLETED:
            try:
                SoundGroups.g_instance.enableArenaSounds(False)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.guiSessionProvider.stop()
        try:
            if self.positionControl is not None:
                self.positionControl.destroy()
                self.positionControl = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        for comp in AVATAR_COMPONENTS:
            comp.onBecomeNonPlayer(self)

        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.stop()
        if self.__tryShootCallbackId:
            BigWorld.cancelCallback(self.__tryShootCallbackId)
            self.__tryShootCallbackId = None
        if self.__shotWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__shotWaitingTimerID)
            self.__shotWaitingTimerID = None
        self.__isWaitingForShot = False
        if self.__fireNonFatalDamageTriggerID is not None:
            BigWorld.cancelCallback(self.__fireNonFatalDamageTriggerID)
            self.__fireNonFatalDamageTriggerID = None
        try:
            if self.__projectileMover is not None:
                self.__projectileMover.destroy()
                self.__projectileMover = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        BigWorld.wg_clearDecals()
        try:
            self.terrainEffects.destroy()
            self.terrainEffects = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        appearance_cache.destroy()
        try:
            self.arena.destroy()
            self.arena = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            vehicles.g_cache.clearPrereqs()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        AreaDestructibles.clear()
        self.__ownVehicleMProv.target = None
        if self.__ownVehicleStabMProv is not None:
            self.__ownVehicleStabMProv.target = None
        self.bwProto.voipController.invalidateMicrophoneMute()
        SoundGroups.g_instance.soundModes.setMode(SoundGroups.SoundModes.DEFAULT_MODE_NAME)
        chatManager.switchPlayerProxy(None)
        g_playerEvents.onAvatarBecomeNonPlayer()
        try:
            self.onVehicleEnterWorld.clear()
            self.onVehicleEnterWorld = None
            self.onVehicleLeaveWorld.clear()
            self.onVehicleLeaveWorld = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.__vehicleToVehicleCollisions = None
        if self.intUserSettings is not None:
            self.intUserSettings.onProxyBecomeNonPlayer()
            self.syncData.onAvatarBecomeNonPlayer()
            self.intUserSettings.setProxy(None, None)
        if self.prebattleInvitations is not None:
            self.prebattleInvitations.onProxyBecomeNonPlayer()
            self.prebattleInvitations.setProxy(None)
        self.__initProgress = 0
        self.__vehicles = set()
        self.__gunDamagedShootSound = None
        if self.__hackSpaceKeeper is not None:
            BigWorld.delModel(self.__hackSpaceKeeper)
            self.__hackSpaceKeeper = None
        uniprof.exitFromRegion('avatar.exiting')
        return

    def onEnterWorld(self, prereqs):
        LOG_DEBUG('[INIT_STEPS] Avatar.onEnterWorld')
        if self.__initProgress & _INIT_STEPS.ENTERED_WORLD > 0:
            return
        self.__initProgress |= _INIT_STEPS.ENTERED_WORLD
        self.__onInitStepCompleted()
        if g_offlineMapCreator.Active():
            self.playerVehicleID = 0
        if self.playerVehicleID != 0:
            if not BattleReplay.isPlaying():
                self.set_playerVehicleID(0)
            else:
                BigWorld.callback(0, partial(self.set_playerVehicleID, 0))
        self.__consistentMatrices.notifyEnterWorld(self)
        AvatarObserver.onEnterWorld(self)

    def onLeaveWorld(self):
        LOG_DEBUG('[INIT_STEPS] Avatar.onLeaveWorld')
        self.__consistentMatrices.notifyLeaveWorld(self)

    def onVehicleChanged(self):
        LOG_DEBUG('Avatar vehicle has changed to %s' % self.vehicle)
        AvatarObserver.onVehicleChanged(self)
        if self.vehicle is not None:
            self.__consistentMatrices.notifyVehicleChanged(self)
            ctrl = self.guiSessionProvider.shared.vehicleState
            if self.vehicle.stunInfo > 0.0 and (self.isObserver() or ctrl.isInPostmortem):
                self.vehicle.updateStunInfo()
            self.guiSessionProvider.shared.viewPoints.updateAttachedVehicle(self.vehicle.id)
        return

    def onSpaceLoaded(self):
        LOG_DEBUG('[INIT_STEPS] Avatar.onSpaceLoaded')
        self.__applyTimeAndWeatherSettings()
        self.__initProgress |= _INIT_STEPS.SPACE_LOADED
        self.__onInitStepCompleted()
        self.__flockMangager.onSpaceLoaded()

    def onStreamComplete(self, streamID, desc, data):
        isCorrupted, origPacketLen, packetLen, origCrc32, crc32 = desc
        if isCorrupted:
            self.base.logStreamCorruption(streamID, origPacketLen, packetLen, origCrc32, crc32)
        callback = self.__rangeStreamIDCallbacks.getCallbackForStreamID(streamID)
        if callback is not None:
            getattr(self, callback)(streamID, data)
            return
        else:
            callback = self.__onStreamCompletePredef.get(streamID, None)
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

    def onCmdResponseExt(self, requestID, resultID, errorStr, ext):
        raise NotImplementedError

    def onIGRTypeChanged(self, data):
        try:
            data = cPickle.loads(data)
            g_playerEvents.onIGRTypeChanged(data.get('roomType'), data.get('igrXPFactor'))
        except Exception:
            LOG_ERROR('Error while unpickling igr data information', data)

    def handleKeyEvent(self, event):
        return False

    def handleKey(self, isDown, key, mods):
        if not self.userSeesWorld() or not self.__initProgress & _INIT_STEPS.VEHICLE_ENTERED:
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
                for comp in AVATAR_COMPONENTS:
                    comp.handleKey(self, isDown, key, mods)

                if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and constants.HAS_DEV_RESOURCES:
                    if key == Keys.KEY_ESCAPE:
                        gui_event_dispatcher.toggleGUIVisibility()
                        return True
                    if key == Keys.KEY_1:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'heal', 0, '')
                        return True
                    if key == Keys.KEY_2:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'reload_gun', 0, '')
                        return True
                    if key == Keys.KEY_3:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'start_fire', 0, '')
                        return True
                    if key == Keys.KEY_4:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'explode', 0, '')
                        return True
                    if key == Keys.KEY_5:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'break_left_track', 0, '')
                        return True
                    if key == Keys.KEY_6:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'break_right_track', 0, '')
                        return True
                    if key == Keys.KEY_7:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'destroy_self', 0, '')
                    if key == Keys.KEY_8:
                        self.base.setVehicleDevelopmentFeature(self.playerVehicleID, 'kill_engine', 0, '')
                    if key == Keys.KEY_F:
                        vehicle = BigWorld.entity(self.playerVehicleID)
                        vehicle.filter.enableClientFilters = not vehicle.filter.enableClientFilters
                        return True
                    if key == Keys.KEY_G:
                        self.moveVehicle(1, True)
                        return True
                    if key == Keys.KEY_R:
                        self.base.setDevelopmentFeature('pickup', 0, 'straight')
                        return True
                    if key == Keys.KEY_T:
                        self.base.setDevelopmentFeature('log_tkill_ratings', 0, '')
                        return True
                    if key == Keys.KEY_N:
                        self.isTeleport = not self.isTeleport
                        return True
                    if key == Keys.KEY_K:
                        self.base.setDevelopmentFeature('respawn_vehicle', 0, '')
                        return True
                    if key == Keys.KEY_O:
                        self.base.setDevelopmentFeature('pickup', 0, 'roll')
                        return True
                    if key == Keys.KEY_P:
                        self.base.setDevelopmentFeature('captureClosestBase', 0, '')
                        return True
                    if key == Keys.KEY_Q:
                        self.base.setDevelopmentFeature('teleportToShotPoint', 0, '')
                        return True
                    if key == Keys.KEY_V:
                        self.base.setDevelopmentFeature('setSignal', 3, '')
                        return True
                    if key == Keys.KEY_C:
                        self.base.setDevelopmentFeature('navigateTo', 0, cPickle.dumps((tuple(self.inputHandler.getDesiredShotPoint()), None, None), -1))
                        return True
                if constants.HAS_DEV_RESOURCES and cmdMap.isFired(CommandMapping.CMD_SWITCH_SERVER_MARKER, key) and isDown:
                    self.gunRotator.showServerMarker = not self.gunRotator.showServerMarker
                    return True
                isGuiEnabled = self.isForcedGuiControlMode()
                if not isGuiEnabled and cmdMap.isFired(CommandMapping.CMD_TOGGLE_GUI, key) and isDown:
                    gui_event_dispatcher.toggleGUIVisibility()
                if constants.HAS_DEV_RESOURCES and isDown:
                    if key == Keys.KEY_I and mods == 0:
                        import Cat
                        if Cat.Tasks.ScreenInfo.ScreenInfoObject.getVisible():
                            Cat.Tasks.ScreenInfo.ScreenInfoObject.setVisible(False)
                        else:
                            Cat.Tasks.ScreenInfo.ScreenInfoObject.setVisible(True)
                        return True
                if cmdMap.isFired(CommandMapping.CMD_INCREMENT_CRUISE_MODE, key) and isDown and not isGuiEnabled:
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
                if cmdMap.isFired(CommandMapping.CMD_DECREMENT_CRUISE_MODE, key) and isDown and not isGuiEnabled:
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
                if cmdMap.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD), key) and isDown and not isGuiEnabled:
                    self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                    self.__updateCruiseControlPanel()
                if cmdMap.isFired(CommandMapping.CMD_STOP_UNTIL_FIRE, key) and isDown and not isGuiEnabled:
                    if not self.__stopUntilFire:
                        self.__stopUntilFire = True
                        self.__stopUntilFireStartTime = time
                    else:
                        self.__stopUntilFire = False
                    self.moveVehicle(self.makeVehicleMovementCommandByKeys(), isDown)
                    self.__updateCruiseControlPanel()
                handbrakeFired = cmdMap.isFired(CommandMapping.CMD_BLOCK_TRACKS, key)
                if cmdMap.isFiredList((CommandMapping.CMD_MOVE_FORWARD,
                 CommandMapping.CMD_MOVE_FORWARD_SPEC,
                 CommandMapping.CMD_MOVE_BACKWARD,
                 CommandMapping.CMD_ROTATE_LEFT,
                 CommandMapping.CMD_ROTATE_RIGHT), key) or handbrakeFired:
                    if self.__stopUntilFire and isDown and not isGuiEnabled:
                        self.__stopUntilFire = False
                        self.__updateCruiseControlPanel()
                    self.moveVehicle(self.makeVehicleMovementCommandByKeys(), isDown, cmdMap.isActive(CommandMapping.CMD_BLOCK_TRACKS))
                    return True
                if cmdMap.isFired(CommandMapping.CMD_QUEST_PROGRESS_SHOW, key) and (mods != 2 or not isDown):
                    gui_event_dispatcher.toggleFullStatsQuestProgress(isDown)
                    return True
                if not isGuiEnabled and cmdMap.isFiredList(xrange(CommandMapping.CMD_AMMO_CHOICE_1, CommandMapping.CMD_AMMO_CHOICE_0 + 1), key) and isDown and mods == 0:
                    gui_event_dispatcher.choiceConsumable(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_RADIAL_MENU_SHOW, key):
                    if self.__isVehicleAlive or not isDown:
                        gui_event_dispatcher.setRadialMenuCmd(key, isDown)
                    return True
                if cmdMap.isFiredList((CommandMapping.CMD_CHAT_SHORTCUT_ATTACK,
                 CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE,
                 CommandMapping.CMD_CHAT_SHORTCUT_POSITIVE,
                 CommandMapping.CMD_CHAT_SHORTCUT_NEGATIVE,
                 CommandMapping.CMD_CHAT_SHORTCUT_HELPME,
                 CommandMapping.CMD_CHAT_SHORTCUT_RELOAD), key) and self.__isVehicleAlive:
                    self.guiSessionProvider.handleShortcutChatCommand(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_ATTACK_MY_TARGET, key) and self.__isVehicleAlive:
                    if BigWorld.target() is None and self.lobbyContext.getServerSettings().spgRedesignFeatures.markTargetAreaEnabled and not BattleReplay.isPlaying() and 'SPG' in self.getVehicleAttached().typeDescriptor.type.tags and self.arena.period == ARENA_PERIOD.BATTLE:
                        self.guiSessionProvider.shared.chatCommands.handleSPGAimAreaCommand(self)
                    else:
                        self.guiSessionProvider.handleShortcutChatCommand(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VOICECHAT_ENABLE, key) and not isDown:
                    if self.__isPlayerInSquad(self.playerVehicleID) and not BattleReplay.isPlaying():
                        newVoIPState = not self.settingsCore.getSetting(SOUND.VOIP_ENABLE)
                        self.settingsCore.applySetting(SOUND.VOIP_ENABLE, newVoIPState)
                        if newVoIPState:
                            message = makeString(MESSENGER.CLIENT_DYNSQUAD_ENABLEVOIP)
                        else:
                            keyName = makeString(READABLE_KEY_NAMES.key(BigWorld.keyToString(key)))
                            message = makeString(MESSENGER.CLIENT_DYNSQUAD_DISABLEVOIP, keyName=keyName)
                        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': message}))
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VEHICLE_MARKERS_SHOW_INFO, key):
                    gui_event_dispatcher.showExtendedInfo(isDown)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_SHOW_HELP, key) and isDown and mods == 0:
                    vehicle = self.getVehicleAttached()
                    if vehicle is not None and vehicle.isWheeledTech:
                        ctx = {'isWheeled': True,
                         'hasBurnout': vehicle.typeDescriptor.hasBurnout,
                         'name': vehicle.typeDescriptor.type.userString,
                         'hasSiegeMode': vehicle.typeDescriptor.hasSiegeMode}
                        gui_event_dispatcher.toggleHelpDetailed(ctx)
                    else:
                        gui_event_dispatcher.toggleHelp()
                    return True
                if key == Keys.KEY_F12 and isDown and mods == 0 and constants.HAS_DEV_RESOURCES:
                    self.__dumpVehicleState()
                    return True
                if key == Keys.KEY_F12 and isDown and mods == 2 and constants.HAS_DEV_RESOURCES:
                    self.__reportLag()
                    return True
                if key == Keys.KEY_O and isDown and mods == 2 and constants.HAS_DEV_RESOURCES:
                    occlussionWatcher = 'Occlusion Culling/Enabled'
                    BigWorld.setWatcher(occlussionWatcher, BigWorld.getWatcher(occlussionWatcher) == 'false')
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VOICECHAT_MUTE, key):
                    self.bwProto.voipController.setMicrophoneMute(not isDown)
                    return True
                if not isGuiEnabled and self.guiSessionProvider.shared.drrScale.handleKey(key, isDown):
                    return True
                if cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP, CommandMapping.CMD_MINIMAP_VISIBLE), key) and isDown:
                    gui_event_dispatcher.setMinimapCmd(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_RELOAD_PARTIAL_CLIP, key) and isDown:
                    self.guiSessionProvider.shared.ammo.reloadPartialClip(self)
                    return True
                if key == Keys.KEY_ESCAPE and isDown and mods == 0 and self.guiSessionProvider.shared.equipments.cancel():
                    return True
                if g_appLoader.handleKey(app_settings.APP_NAME_SPACE.SF_BATTLE, isDown, key, mods):
                    return True
            except Exception:
                LOG_CURRENT_EXCEPTION()
                return True

            return False

    def set_playerVehicleID(self, prev):
        LOG_DEBUG('[INIT_STEPS] Avatar.set_playerVehicleID')
        self.__initProgress |= _INIT_STEPS.SET_PLAYER_ID
        self.__onInitStepCompleted()
        self.__isObserver = None
        ownVehicle = BigWorld.entity(self.playerVehicleID)
        if ownVehicle is not None and ownVehicle.inWorld and not ownVehicle.isPlayerVehicle:
            ownVehicle.isPlayerVehicle = True
            self.vehicleTypeDescriptor = ownVehicle.typeDescriptor
            self.__isVehicleAlive = ownVehicle.isAlive()
            self.guiSessionProvider.setPlayerVehicle(self.playerVehicleID, self.vehicleTypeDescriptor)
            self.__initProgress |= _INIT_STEPS.VEHICLE_ENTERED
            self.__onInitStepCompleted()
        return

    def set_isGunLocked(self, prev):
        if not self.isObserver():
            if self.isGunLocked:
                self.gunRotator.lock(True)
                if not isinstance(self.inputHandler.ctrl, (VideoCameraControlMode,
                 ArcadeControlMode,
                 PostMortemControlMode,
                 DeathFreeCamMode,
                 RespawnDeathMode)):
                    self.inputHandler.setAimingMode(False, AIMING_MODE.USER_DISABLED)
                    self.inputHandler.onControlModeChanged('arcade', preferredPos=self.inputHandler.getDesiredShotPoint())
            else:
                self.gunRotator.lock(False)

    def set_ownVehicleGear(self, prev):
        pass

    def set_ownVehicleAuxPhysicsData(self, prev):
        self.__onSetOwnVehicleAuxPhysicsData(prev)

    def targetBlur(self, prevEntity):
        if not prevEntity:
            return
        else:
            self.guiSessionProvider.shared.feedback.setTargetInFocus(0, False)
            prevEntity.removeEdge()
            self.target = None
            TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AIM_AT_VEHICLE)
            isVehicle = prevEntity.__class__.__name__ == 'Vehicle'
            if isVehicle and self.__maySeeOtherVehicleDamagedDevices:
                self.cell.monitorVehicleDamagedDevices(0)
                self.guiSessionProvider.shared.feedback.hideVehicleDamagedDevices()
            return

    def targetFocus(self, entity):
        if not entity:
            return
        self.target = entity
        self.guiSessionProvider.shared.feedback.setTargetInFocus(entity.id, True)
        if (self.inputHandler.isGuiVisible or self.isInTutorial) and entity.isAlive():
            isVehicle = entity.__class__.__name__ == 'Vehicle'
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.AIM_AT_VEHICLE, vehicleId=entity.id)
            entity.drawEdge()
            if isVehicle and self.__maySeeOtherVehicleDamagedDevices:
                self.cell.monitorVehicleDamagedDevices(entity.id)

    def reload(self):
        self.__reloadGUI()

    def vehicle_onEnterWorld(self, vehicle):
        self.__stippleMgr.hideIfExistFor(vehicle)
        self.__vehicles.add(vehicle)
        AvatarObserver.vehicle_onEnterWorld(self, vehicle)
        if vehicle.id != self.playerVehicleID:
            vehicle.targetCaps = [1]
        else:
            LOG_DEBUG('[INIT_STEPS] Avatar.vehicle_onEnterWorld', vehicle.id)
            vehicle.isPlayerVehicle = True
            if not self.__initProgress & _INIT_STEPS.VEHICLE_ENTERED:
                self.vehicleTypeDescriptor = vehicle.typeDescriptor
                if vehicle.typeDescriptor.turret.ceilless is not None:
                    WWISE.WW_setRTCPGlobal('ceilless', 1 if vehicle.typeDescriptor.turret.ceilless else 0)
                else:
                    WWISE.WW_setRTCPGlobal('ceilless', 0)
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    m = vehicle.filter.bodyMatrix
                else:
                    m = vehicle.matrix
                self.__ownVehicleMProv.setStaticTransform(Math.Matrix(m))
                stabMat = WoT.computeStabilisedVehicleMatrixU64(m, self.ownVehicleAuxPhysicsData)
                self.__ownVehicleStabMProv.setStaticTransform(Math.Matrix(stabMat))
                self.__initProgress |= _INIT_STEPS.VEHICLE_ENTERED
                self.__onInitStepCompleted()
            else:
                vehicle.typeDescriptor.activeGunShotIndex = self.vehicleTypeDescriptor.activeGunShotIndex
            self.__isVehicleAlive = vehicle.isAlive()
        if self.__initProgress & _INIT_STEPS.INIT_COMPLETED and not vehicle.isStarted:
            self.__startVehicleVisual(vehicle, resetControllers=True)
        else:
            self.consistentMatrices.notifyVehicleLoaded(self, vehicle)
        return

    def __startVehicleVisual(self, vehicle, resetControllers=False):
        vehicle.startVisual()
        self.onVehicleEnterWorld(vehicle)
        self.consistentMatrices.notifyVehicleLoaded(self, vehicle)
        if vehicle.id == self.playerVehicleID:
            if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                self.__onSetOwnVehicleAuxPhysicsData(self.ownVehicleAuxPhysicsData)
                self.__ownVehicleStabMProv.target = vehicle.filter.stabilisedMatrix
            else:
                self.__ownVehicleStabMProv.target = vehicle.matrix
            if self.__disableRespawnMode:
                self.__disableRespawnMode = False
                self.inputHandler.deactivatePostmortem()
                self.__deviceStates = {}
                self.gunRotator.stop()
                self.gunRotator.start()
                self.gunRotator.reset()
                self.enableServerAim(self.gunRotator.showServerMarker)
            if self.__pendingSiegeSettings:
                vehicleID, newState, timeToNextState = self.__pendingSiegeSettings
                if vehicle.id == vehicleID:
                    vehicle.onSiegeStateUpdated(newState, timeToNextState)
                    self.__pendingSiegeSettings = None
            if resetControllers:
                repo = self.guiSessionProvider.shared
                for ctrl in (repo.ammo, repo.equipments, repo.optionalDevices):
                    if ctrl is not None:
                        ctrl.clear(False)

            self.guiSessionProvider.setPlayerVehicle(self.playerVehicleID, self.vehicleTypeDescriptor)
        return

    def vehicle_onLeaveWorld(self, vehicle):
        if vehicle.id == self.playerVehicleID:
            LOG_DEBUG('[INIT_STEPS] Avatar.vehicle_onLeaveWorld', vehicle.id)
            self.__initProgress &= ~_INIT_STEPS.VEHICLE_ENTERED
        if not vehicle.isStarted:
            return
        else:
            self.onVehicleLeaveWorld(vehicle)
            self.__vehicles.remove(vehicle)
            model = vehicle.stopVisual(True)
            vehicle.model = None
            if model is not None:
                self.__stippleMgr.showFor(vehicle, model)
            return

    def __onSetOwnVehicleAuxPhysicsData(self, prev):
        vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            y, p, r, leftScroll, rightScroll, _ = WoT.unpackAuxVehiclePhysicsData(self.ownVehicleAuxPhysicsData)
            appearance = vehicle.appearance
            appearance.updateTracksScroll(leftScroll, rightScroll)
            syncStabilisedYPR = getattr(vehicle.filter, 'syncStabilisedYPR', None)
            if syncStabilisedYPR:
                syncStabilisedYPR(y, p, r)
        return

    def prerequisites(self):
        pass

    def initSpace(self):
        if not self.__isSpaceInitialized:
            self.__isSpaceInitialized = True

    def userSeesWorld(self):
        return self.__initProgress & _INIT_STEPS.PLAYER_READY

    def requestToken(self, requestID, tokenType):
        self.base.requestToken(requestID, tokenType)

    def onTokenReceived(self, requestID, tokenType, data):
        if Account.g_accountRepository is not None:
            Account.g_accountRepository.onTokenReceived(requestID, tokenType, data)
        return

    def onKickedFromServer(self, reason, isBan, expiryTime):
        LOG_DEBUG('onKickedFromServer', reason, isBan, expiryTime)
        self.statsCollector.reset()
        if not BattleReplay.isPlaying():
            self.connectionMgr.setKickedFromServer(reason, isBan, expiryTime)

    def onSwitchViewpoint(self, vehicleID, position):
        LOG_DEBUG('onSwitchViewpoint', vehicleID, position)
        self.inputHandler.ctrl.onSwitchViewpoint(vehicleID, position)
        staticPosition = position
        if vehicleID != -1:
            staticPosition = None
        self.consistentMatrices.notifyViewPointChanged(self, staticPosition)
        return

    def onAutoAimVehicleLost(self, lossReasonFlags):
        autoAimVehID = self.__autoAimVehID
        self.__autoAimVehID = 0
        self.inputHandler.setAimingMode(False, AIMING_MODE.TARGET_LOCK)
        self.gunRotator.clientMode = True
        if autoAimVehID and autoAimVehID not in self.__frags:
            self.onLockTarget(AimSound.TARGET_LOST, not lossReasonFlags & TARGET_LOST_FLAGS.KILLED_BY_ME)
        TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE)
        if BigWorld.player().vehicle.isWheeledTech:
            gui_event_dispatcher.hideAutoAimMarker()

    def updateVehicleHealth(self, vehicleID, health, deathReasonID, isCrewActive, isRespawn):
        rawHealth = health
        health = max(0, health)
        isAlive = health > 0 and isCrewActive
        wasAlive = self.__isVehicleAlive or self.__firstHealthUpdate
        wasRespawnAvailable = self.__isRespawnAvailable
        if self.__deadOnLoading:
            wasAlive = False
            self.__deadOnLoading = False
        self.__firstHealthUpdate = False
        self.__isVehicleAlive = isAlive
        self.__isRespawnAvailable = isRespawn
        LOG_DEBUG_DEV('[RESPAWN] client.Avatar.updateVehicleHealth', vehicleID, health, deathReasonID, isCrewActive, isRespawn, wasAlive)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HEALTH, health, vehicleID)
        if not wasAlive and isAlive:
            self.__disableRespawnMode = True
            self.guiSessionProvider.movingToRespawnBase()
        if not isAlive and wasAlive:
            self.gunRotator.stop()
            if health > 0 and not isCrewActive:
                self.soundNotifications.play('crew_deactivated')
                self.__deviceStates = {'crew': 'destroyed'}
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CREW_DEACTIVATED, deathReasonID)
            elif not self.guiSessionProvider.getCtx().isObserver(self.playerVehicleID):
                self.soundNotifications.play('vehicle_destroyed')
                self.__deviceStates = {'vehicle': 'destroyed'}
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DESTROYED, deathReasonID)
            if self.vehicle is not None:
                self.guiSessionProvider.shared.viewPoints.updateAttachedVehicle(self.vehicle.id)
            self.inputHandler.activatePostmortem(isRespawn)
            self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
            self.__updateCruiseControlPanel()
            self.__stopUntilFire = False
            if rawHealth <= 0:
                vehicle = BigWorld.entities.get(self.playerVehicleID)
                if vehicle is not None:
                    prevHealth = vehicle.health
                    vehicle.health = rawHealth
                    vehicle.set_health(prevHealth)
        if not isAlive and wasAlive or not isAlive and wasRespawnAvailable and not isRespawn:
            self.guiSessionProvider.switchToPostmortem(not self.respawnEnabled, isRespawn)
        return

    def updateVehicleGunReloadTime(self, vehicleID, timeLeft, baseTime):
        AvatarObserver.updateVehicleGunReloadTime(self, vehicleID, timeLeft, baseTime)
        if vehicleID != self.playerVehicleID and vehicleID != self.observedVehicleID:
            if not self.__isVehicleAlive and vehicleID == self.inputHandler.ctrl.curVehicleID:
                self.guiSessionProvider.shared.feedback.setVehicleHasAmmo(vehicleID, timeLeft != -2)
            return
        self.__gunReloadCommandWaitEndTime = 0.0
        if self.__prevGunReloadTimeLeft != timeLeft and timeLeft == 0.0:
            VibroReloadController()
        self.__prevGunReloadTimeLeft = timeLeft
        if timeLeft < 0.0:
            timeLeft = -1
        self.guiSessionProvider.shared.ammo.setGunReloadTime(timeLeft, baseTime)

    def updateVehicleClipReloadTime(self, vehicleID, timeLeft, baseTime, stunned):
        self.guiSessionProvider.shared.ammo.setGunAutoReloadTime(timeLeft, baseTime, stunned)

    def updateVehicleAmmo(self, vehicleID, compactDescr, quantity, quantityInClip, timeRemaining, totalTime):
        if not compactDescr:
            itemTypeIdx = ITEM_TYPE_INDICES['equipment']
        else:
            itemTypeIdx = getTypeOfCompactDescr(compactDescr)
        processor = self.__updateConsumablesProcessors.get(itemTypeIdx)
        if processor:
            getattr(self, processor)(vehicleID, compactDescr, quantity, quantityInClip, timeRemaining, totalTime)
        else:
            LOG_WARNING('Not supported item type index', itemTypeIdx)

    __updateConsumablesProcessors = {ITEM_TYPE_INDICES['shell']: '_PlayerAvatar__processVehicleAmmo',
     ITEM_TYPE_INDICES['equipment']: '_PlayerAvatar__processVehicleEquipments'}

    def updateVehicleOptionalDeviceStatus(self, vehicleID, deviceID, isOn):
        AvatarObserver.updateVehicleOptionalDeviceStatus(self, vehicleID, deviceID, isOn)
        self.guiSessionProvider.shared.optionalDevices.setOptionalDevice(deviceID, isOn)

    def updateVehicleMiscStatus(self, vehicleID, code, intArg, floatArgs):
        if vehicleID != self.playerVehicleID and vehicleID != self.observedVehicleID and (self.__isVehicleAlive or vehicleID != self.inputHandler.ctrl.curVehicleID):
            return
        else:
            STATUS = VEHICLE_MISC_STATUS
            floatArg = floatArgs[0]
            typeDescr = self.vehicleTypeDescriptor
            if self.observedVehicleID is not None:
                observedVehicle = BigWorld.entity(self.observedVehicleID)
                if observedVehicle is not None:
                    typeDescr = observedVehicle.typeDescriptor
            if code == STATUS.DESTROYED_DEVICE_IS_REPAIRING:
                extraIndex = intArg & 255
                progress = (intArg & 65280) >> 8
                LOG_DEBUG_DEV('DESTROYED_DEVICE_IS_REPAIRING (%s): %s%%, %s sec' % (typeDescr.extras[extraIndex].name, progress, floatArg))
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.REPAIRING, (typeDescr.extras[extraIndex].name[:-len('Health')], progress, floatArg))
            elif code == STATUS.OTHER_VEHICLE_DAMAGED_DEVICES_VISIBLE:
                prevVal = self.__maySeeOtherVehicleDamagedDevices
                newVal = bool(intArg)
                self.__maySeeOtherVehicleDamagedDevices = newVal
                if not prevVal and newVal:
                    target = BigWorld.target()
                    if target is not None and isinstance(target, Vehicle.Vehicle):
                        self.cell.monitorVehicleDamagedDevices(target.id)
            elif code == STATUS.VEHICLE_IS_OVERTURNED:
                self.__isVehicleOverturned = constants.OVERTURN_WARNING_LEVEL.isOverturned(intArg)
                self.updateVehicleDestroyTimer(code, floatArgs, intArg)
            elif code == STATUS.IN_DEATH_ZONE:
                finishTime = BigWorld.serverTime() + floatArg
                self.updateVehicleDeathZoneTimer(floatArg, intArg, finishTime=finishTime)
            elif code == STATUS.VEHICLE_DROWN_WARNING:
                self.updateVehicleDestroyTimer(code, floatArgs, intArg)
            elif code == STATUS.IS_OBSERVED_BY_ENEMY:
                if intArg == 0:
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY, True)
            elif code == STATUS.LOADER_INTUITION_WAS_USED:
                self.soundNotifications.play('gun_intuition')
                self.guiSessionProvider.useLoaderIntuition()
            elif code == STATUS.SIEGE_MODE_STATE_CHANGED:
                if intArg in (constants.VEHICLE_SIEGE_STATE.SWITCHING_ON, constants.VEHICLE_SIEGE_STATE.SWITCHING_OFF):
                    self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
                    self.__updateCruiseControlPanel()
                    self.moveVehicleByCurrentKeys(False)
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.SIEGE_MODE, (intArg, floatArg))
                self.__onSiegeStateUpdated(vehicleID, intArg, floatArg)
            elif code == STATUS.BURNOUT_WARNING:
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BURNOUT_WARNING, intArg)
                if intArg > 0:
                    SoundGroups.g_instance.playSound2D('eng_damage_risk')
                vehicle = BigWorld.entity(self.playerVehicleID)
                if vehicle is not None:
                    vehicle.appearance.onEngineDamageRisk(intArg > 0)
            elif code == STATUS.BURNOUT_UNAVAILABLE_DUE_TO_BROKEN_ENGINE:
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BURNOUT_UNAVAILABLE_DUE_TO_BROKEN_ENGINE, intArg)
            return

    def updateVehicleSetting(self, vehicleID, code, value):
        AvatarObserver.updateVehicleSetting(self, vehicleID, code, value)
        if code == VEHICLE_SETTING.CURRENT_SHELLS:
            ammoCtrl = self.guiSessionProvider.shared.ammo
            if not ammoCtrl.setCurrentShellCD(value):
                return
            shotIdx = ammoCtrl.getGunSettings().getShotIndex(value)
            if shotIdx > -1:
                self.getVehicleDescriptor().activeGunShotIndex = shotIdx
                vehicle = BigWorld.entity(self.playerVehicleID)
                if vehicle is not None:
                    vehicle.typeDescriptor.activeGunShotIndex = shotIdx
                self.onGunShotChanged()
            return
        elif code == VEHICLE_SETTING.NEXT_SHELLS:
            self.guiSessionProvider.shared.ammo.setNextShellCD(value)
            return
        elif code == VEHICLE_SETTING.AUTOROTATION_ENABLED:
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.AUTO_ROTATION, value)
            return
        else:
            LOG_CODEPOINT_WARNING(code, value)
            return

    def updateTargetingInfo(self, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed, shotDispMultiplierFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime):
        LOG_DEBUG_DEV('updateTargetingInfo', turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed, shotDispMultiplierFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime)
        aimingInfo = self.__aimingInfo
        aimingInfo[2] = shotDispMultiplierFactor
        aimingInfo[3] = gunShotDispersionFactorsTurretRotation
        aimingInfo[4] = chassisShotDispersionFactorsMovement
        aimingInfo[5] = chassisShotDispersionFactorsRotation
        aimingInfo[6] = aimingTime
        if self.gunRotator is not None:
            self.gunRotator.update(turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed)
        self.getOwnVehicleShotDispersionAngle(self.gunRotator.turretRotationSpeed)
        return

    def redrawVehicleOnRespawn(self, vehicleID, newVehCompactDescr, newVehOutfitCompactDescr):
        if vehicleID == self.playerVehicleID and self.__firstHealthUpdate:
            self.__deadOnLoading = True
        Vehicle.Vehicle.respawnVehicle(vehicleID, newVehCompactDescr, newVehOutfitCompactDescr)

    def updateGunMarker(self, vehicleID, shotPos, shotVec, dispersionAngle):
        self.gunRotator.setShotPosition(vehicleID, shotPos, shotVec, dispersionAngle)

    def updateOwnVehiclePosition(self, position, direction, speed, rspeed):
        self.__lastVehicleSpeeds = (speed, rspeed)

    def updateVehicleDestroyTimer(self, code, period, warnLvl=None):
        state = VEHICLE_VIEW_STATE.DESTROY_TIMER
        value = DestroyTimerViewState.makeCloseTimerState(code)
        if warnLvl is None:
            if period[1] > 0:
                value = DestroyTimerViewState(code, period[0], 'critical', period[0])
        elif warnLvl == DROWN_WARNING_LEVEL.DANGER:
            value = DestroyTimerViewState(code, period[1], 'critical', period[0])
        elif warnLvl == DROWN_WARNING_LEVEL.CAUTION:
            value = DestroyTimerViewState(code, 0, 'warning', 0)
        self.guiSessionProvider.invalidateVehicleState(state, value)
        return

    def updateVehicleDeathZoneTimer(self, time, zoneID, entered=True, finishTime=None, state='critical'):
        timer = VEHICLE_VIEW_STATE.DEATHZONE_TIMER
        value = DeathZoneTimerViewState.makeCloseTimerState(zoneID)
        if time > 0 or state == 'warning':
            value = DeathZoneTimerViewState(zoneID, time, state, finishTime, entered)
        self.guiSessionProvider.invalidateVehicleState(timer, value)

    def showOwnVehicleHitDirection(self, hitDirYaw, attackerID, damage, crits, isBlocked, isShellHE, damagedID, attackReasonID):
        if not self.__isVehicleAlive and not self.isObserver():
            return
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        LOG_DEBUG_DEV('showOwnVehicleHitDirection: hitDirYaw={}, attackerID={}, damage={}, crits={}isBlocked={}, isHighExplosive={}, damagedID={}, attackReasonID={}'.format(hitDirYaw, attackerID, damage, crits, isBlocked, isShellHE, damagedID, attackReasonID))
        self.guiSessionProvider.addHitDirection(hitDirYaw, attackerID, damage, isBlocked, crits, isShellHE, damagedID, attackReasonID)

    def showVehicleDamageInfo(self, vehicleID, damageIndex, extraIndex, entityID, equipmentID):
        damageCode = constants.DAMAGE_INFO_CODES[damageIndex]
        typeDescr = self.vehicleTypeDescriptor
        if self.observedVehicleID is not None:
            observedVehicle = BigWorld.entity(self.observedVehicleID)
            if observedVehicle is not None:
                typeDescr = observedVehicle.typeDescriptor
        extra = typeDescr.extras[extraIndex] if extraIndex != 0 else None
        if vehicleID == self.playerVehicleID or vehicleID == self.observedVehicleID or not self.__isVehicleAlive and vehicleID == self.inputHandler.ctrl.curVehicleID:
            self.__showDamageIconAndPlaySound(damageCode, extra, vehicleID)
        if damageCode not in self.__damageInfoNoNotification:
            self.guiSessionProvider.shared.messages.showVehicleDamageInfo(self, damageCode, vehicleID, entityID, extra, equipmentID)
        TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_RECEIVE_DAMAGE, attackerId=entityID)
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
            if g_bootcamp.isRunning():
                g_bootcamp.onBattleAction(BOOTCAMP_BATTLE_ACTION.PLAYER_HIT_VEHICLE, [vehicleID, flags])
            if flags & VHF.VEHICLE_KILLED:
                hasKill = True
                continue
            if self.team == arenaVehicles[vehicleID]['team'] and self.playerVehicleID != vehicleID:
                if flags & (VHF.IS_ANY_DAMAGE_MASK | VHF.ATTACK_IS_DIRECT_PROJECTILE):
                    damagedAllies.append(vehicleID)
            enemies[vehicleID] = enemies.get(vehicleID, 0) | flags
            if flags & VHF.FIRE_STARTED:
                burningEnemies.append(vehicleID)

        showMessage = self.guiSessionProvider.shared.messages.showAllyHitMessage
        for allyVehID in damagedAllies:
            showMessage(allyVehID)

        if hasKill:
            return
        else:
            bestSound = None
            for enemyVehID, flags in enemies.iteritems():
                if enemyVehID == self.playerVehicleID:
                    continue
                if flags & VHF.IS_ANY_PIERCING_MASK:
                    self.__fireNonFatalDamageTriggerID = BigWorld.callback(0.5, partial(self.__fireNonFatalDamageTrigger, enemyVehID))
                sound = None
                if flags & VHF.ATTACK_IS_EXTERNAL_EXPLOSION:
                    if flags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_EXPLOSION:
                        sound = 'enemy_hp_damaged_by_near_explosion_by_player'
                    elif flags & VHF.IS_ANY_PIERCING_MASK:
                        sound = 'enemy_no_hp_damage_by_near_explosion_by_player'
                elif flags & VHF.MATERIAL_WITH_POSITIVE_DF_PIERCED_BY_PROJECTILE:
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
                        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_RICOCHET, targetId=enemyVehID)
                elif flags & VHF.MATERIAL_WITH_POSITIVE_DF_NOT_PIERCED_BY_PROJECTILE:
                    if flags & (VHF.GUN_DAMAGED_BY_PROJECTILE | VHF.GUN_DAMAGED_BY_EXPLOSION):
                        sound = 'enemy_no_hp_damage_at_attempt_and_gun_damaged_by_player'
                    elif flags & (VHF.CHASSIS_DAMAGED_BY_PROJECTILE | VHF.CHASSIS_DAMAGED_BY_EXPLOSION):
                        sound = 'enemy_no_hp_damage_at_attempt_and_chassis_damaged_by_player'
                    else:
                        sound = 'enemy_no_hp_damage_at_attempt_by_player'
                        if len(enemies) == 1:
                            TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
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
                        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
                if sound is not None:
                    bestSound = _getBestShotResultSound(bestSound, sound, enemyVehID)

            if bestSound is not None:
                self.soundNotifications.play(bestSound[0], bestSound[1])
            for burnEnemyVehID in burningEnemies:
                self.soundNotifications.play('enemy_fire_started_by_player', burnEnemyVehID)

            return

    def showOtherVehicleDamagedDevices(self, vehicleID, damagedExtras, destroyedExtras):
        target = BigWorld.target()
        if target is None or not isinstance(target, Vehicle.Vehicle):
            if self.__maySeeOtherVehicleDamagedDevices and vehicleID != 0:
                self.cell.monitorVehicleDamagedDevices(0)
            return
        else:
            feedback = self.guiSessionProvider.shared.feedback
            if target.id == vehicleID:
                feedback.showVehicleDamagedDevices(vehicleID, damagedExtras, destroyedExtras)
                return
            if self.__maySeeOtherVehicleDamagedDevices:
                self.cell.monitorVehicleDamagedDevices(target.id)
            feedback.hideVehicleDamagedDevices(vehicleID)
            return

    def showDevelopmentInfo(self, code, arg):
        if constants.HAS_DEV_RESOURCES:
            params = cPickle.loads(arg)
            g_playerEvents.onShowDevelopmentInfo(code, params)
            if code == DEVELOPMENT_INFO.BONUSES:
                self.guiSessionProvider.shared.feedback.setDevelopmentInfo(code, params)
            elif code == DEVELOPMENT_INFO.VISIBILITY:
                import Cat
                Cat.Tasks.VisibilityTest.VisibilityTestObject.setContent(params)
            elif code == DEVELOPMENT_INFO.VEHICLE_ATTRS:
                LOG_DEBUG('showDevelopmentInfo', code, params)
                import Cat
                board = Cat.Tasks.ScreenInfo.ScreenInfoObject.getBoard('vehicleAttrs')
                if board is not None:
                    board.setUpdater(lambda key: params.get(key, VEHICLE_ATTRIBUTE_FACTORS.get(key)))
                    board.update()
            elif code == DEVELOPMENT_INFO.EXPLOSION_RAY:
                start, direction, _, collDist = params
                debugLines = getattr(self, '_debugLines', None)
                if debugLines is None:
                    debugLines = self._debugLines = []
                debugLines.append(DebugLine(start, start + direction * collDist))
            elif code == DEVELOPMENT_INFO.FRONTLINE:
                if constants.IS_DEVELOPMENT:
                    self.frontLineInformationUpdate(params)
            else:
                LOG_DEBUG('showDevelopmentInfo', code, params)
        return

    def syncVehicleAttrs(self, attrs):
        LOG_DEBUG('syncVehicleAttrs', attrs)
        self.guiSessionProvider.shared.feedback.setVehicleAttrs(self.playerVehicleID, attrs)

    def showTracer(self, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist):
        if not self.userSeesWorld() or self.__projectileMover is None:
            return
        else:
            startPoint = refStartPoint
            shooter = BigWorld.entity(shooterID)
            if not isRicochet and shooter is not None and shooter.isStarted:
                gunMatrix = Math.Matrix(shooter.appearance.compoundModel.node('HP_gunFire'))
                gunFirePos = gunMatrix.translation
                if cameras.isPointOnScreen(gunFirePos):
                    startPoint = gunFirePos
                    replayCtrl = BattleReplay.g_replayCtrl
                    if (gunFirePos - refStartPoint).length > 50.0 and (gunFirePos - BigWorld.camera().position).length < 50.0 and replayCtrl.isPlaying:
                        velocity = velocity.length * gunMatrix.applyVector((0, 0, 1))
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            self.__projectileMover.add(shotID, effectsDescr, gravity, refStartPoint, velocity, startPoint, maxShotDist, shooterID, BigWorld.camera().position)
            if isRicochet:
                self.__projectileMover.hold(shotID)
            return

    def stopTracer(self, shotID, endPoint):
        if self.userSeesWorld() and self.__projectileMover is not None:
            self.__projectileMover.hide(shotID, endPoint)
        return

    def explodeProjectile(self, shotID, effectsIndex, effectMaterialIndex, endPoint, velocityDir, damagedDestructibles):
        if self.userSeesWorld() and self.__projectileMover is not None:
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
        return

    def onRoundFinished(self, winnerTeam, reason):
        LOG_DEBUG('onRoundFinished', winnerTeam, reason)
        g_playerEvents.onRoundFinished(winnerTeam, reason)

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        g_playerEvents.onKickedFromArena(reasonCode)
        SystemMessages.pushMessage(messages.getKickReasonMessage(reasonCode), type=SystemMessages.SM_TYPE.Error)

    def onBattleEvents(self, events):
        LOG_DEBUG('Battle events has been received: ', events)
        observedVehID = self.guiSessionProvider.shared.vehicleState.getControllingVehicleID()
        if self.isObserver() or observedVehID == self.playerVehicleID:
            self.guiSessionProvider.shared.feedback.handleBattleEvents(events)

    def battleEventsSummary(self, summary):
        LOG_DEBUG_DEV('Summary of battle events has been received:  data={}'.format(summary))
        observedVehID = self.guiSessionProvider.shared.vehicleState.getControllingVehicleID()
        if self.isObserver() or observedVehID == self.playerVehicleID:
            self.guiSessionProvider.shared.feedback.handleBattleEventsSummary(summary)

    def onBootcampEvent(self, details):
        g_bootcamp.onBattleAction(details[0], details[1:])

    def updateArena(self, updateType, argStr):
        self.arena.update(updateType, argStr)

    def updatePositions(self, indices, positions):
        try:
            self.arena.updatePositions(indices, positions)
        except Exception:
            pass

    def updateCarriedFlagPositions(self, flagIDs, positions):
        pass

    def onRepairPointAction(self, repairPointIndex, action, nextActionTime):
        pass

    def updateGasAttackState(self, state, activationTime, currentTime):
        pass

    def updateQuestProgress(self, questID, progressesInfo):
        LOG_DEBUG('[QUEST] Progress:', questID, progressesInfo)
        self.guiSessionProvider.shared.questProgress.updateQuestProgress(questID, progressesInfo)

    def updateAvatarPrivateStats(self, stats):
        stats = cPickle.loads(zlib.decompress(stats))
        stats = listToDict(AVATAR_PRIVATE_STATS, stats)
        self.guiSessionProvider.updateAvatarPrivateStats(stats)

    def updateResourceAmount(self, resourcePointID, newAmount):
        pass

    def onFrictionWithVehicle(self, otherID, frictionPoint, state):
        vehicle = self.getVehicleAttached()
        if vehicle is not None:
            vehicle.appearance.onFriction(otherID, frictionPoint, state)
        return

    def onCollisionWithVehicle(self, point, energy):
        vehicle = self.getVehicleAttached()
        if vehicle is not None:
            vehicle.showVehicleCollisionEffect(point, 10, energy / 1000.0)
        return

    def makeDenunciation(self, violatorID, topicID, violatorKind):
        if self.denunciationsLeft <= 0:
            return
        self.denunciationsLeft -= 1
        self.base.makeDenunciation(violatorID, topicID, violatorKind)

    def banUnbanUser(self, accountDBID, restrType, banPeriod, reason, isBan):
        reason = reason.encode('utf8')
        self.base.banUnbanUser(accountDBID, restrType, banPeriod, reason, isBan)

    def isObserver(self):
        if self.__isObserver is None:
            self.__isObserver = self.guiSessionProvider.getCtx().isObserver(self.playerVehicleID)
        return self.__isObserver

    def receiveAccountStats(self, requestID, stats):
        callback = self.__onCmdResponse.pop(requestID, None)
        if callback is None:
            return
        else:
            try:
                stats = cPickle.loads(stats)
            except Exception:
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

    def moveVehicleByCurrentKeys(self, isKeyDown, forceFlags=204, forceMask=0):
        moveFlags = self.makeVehicleMovementCommandByKeys(forceFlags, forceMask)
        self.moveVehicle(moveFlags, isKeyDown)

    def makeVehicleMovementCommandByKeys(self, forceFlags=204, forceMask=0):
        cmdMap = CommandMapping.g_instance
        flags = 0
        if self.__stopUntilFire:
            return flags
        if cmdMap.isActiveList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC)):
            if not cmdMap.isActive(CommandMapping.CMD_MOVE_BACKWARD):
                flags = _MOVEMENT_FLAGS.FORWARD
        elif cmdMap.isActive(CommandMapping.CMD_MOVE_BACKWARD):
            flags = _MOVEMENT_FLAGS.BACKWARD
        else:
            if self.__cruiseControlMode >= _CRUISE_CONTROL_MODE.FWD25:
                flags = _MOVEMENT_FLAGS.FORWARD
            elif self.__cruiseControlMode <= _CRUISE_CONTROL_MODE.BCKW50:
                flags = _MOVEMENT_FLAGS.BACKWARD
            isOn = self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD50 or self.__cruiseControlMode == _CRUISE_CONTROL_MODE.BCKW50
            if isOn:
                flags |= _MOVEMENT_FLAGS.CRUISE_CONTROL50
            elif self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD25:
                flags |= _MOVEMENT_FLAGS.CRUISE_CONTROL25
        rotateLeftFlag = _MOVEMENT_FLAGS.ROTATE_LEFT
        rotateRightFlag = _MOVEMENT_FLAGS.ROTATE_RIGHT
        if self.invRotationOnBackMovement and flags & _MOVEMENT_FLAGS.BACKWARD != 0:
            rotateLeftFlag, rotateRightFlag = rotateRightFlag, rotateLeftFlag
        if cmdMap.isActive(CommandMapping.CMD_ROTATE_LEFT):
            if not cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
                flags |= rotateLeftFlag
        elif cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
            flags |= rotateRightFlag
        if cmdMap.isActive(CommandMapping.CMD_BLOCK_TRACKS):
            flags |= _MOVEMENT_FLAGS.BLOCK_TRACKS
        flags |= forceMask & forceFlags
        flags &= ~forceMask | forceFlags
        return flags

    def moveVehicle(self, flags, isKeyDown, handbrakeFired=False):
        if not self.__isOnArena:
            return
        else:
            cantMove = False
            vehicle = BigWorld.entity(self.playerVehicleID)
            if self.inputHandler.ctrl.isSelfVehicle():
                for deviceName, stateName in self.__deviceStates.iteritems():
                    msgName = self.__cantMoveCriticals.get(deviceName + '_' + stateName)
                    if msgName is not None:
                        cantMove = True
                        if isKeyDown:
                            if vehicle is not None and vehicle.isAlive():
                                self.showVehicleError(msgName)
                        break

            if not cantMove:
                if vehicle is not None and vehicle.isStarted:
                    rotationDir, movementDir = (0, 0)
                    if flags & _MOVEMENT_FLAGS.ROTATE_RIGHT:
                        rotationDir = 1
                    elif flags & _MOVEMENT_FLAGS.ROTATE_LEFT:
                        rotationDir = -1
                    if flags & _MOVEMENT_FLAGS.FORWARD:
                        movementDir = 1
                    elif flags & _MOVEMENT_FLAGS.BACKWARD:
                        movementDir = -1
                    vehicle.notifyInputKeysDown(movementDir, rotationDir, handbrakeFired)
                    if isKeyDown and not flags & _MOVEMENT_FLAGS.BLOCK_TRACKS:
                        self.inputHandler.setAutorotation(True)
            elif vehicle is not None and vehicle.isStarted:
                vehicle.turnoffThrottle()
            self.base.vehicle_moveWith(flags)
            if g_bootcamp.isRunning() and not cantMove:
                g_bootcamp.onBattleAction(BOOTCAMP_BATTLE_ACTION.PLAYER_MOVE, [flags])
            return

    def enableOwnVehicleAutorotation(self, enable):
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.AUTO_ROTATION, enable)
        self.base.vehicle_changeSetting(VEHICLE_SETTING.AUTOROTATION_ENABLED, enable)

    def enableServerAim(self, enable):
        self.base.setDevelopmentFeature('server_marker', enable, '')

    def autoAim(self, target=None, magnetic=False):
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
            self.cell.autoAim(vehID, magnetic)
            if vehID != 0:
                self.inputHandler.setAimingMode(True, AIMING_MODE.TARGET_LOCK)
                self.gunRotator.clientMode = False
                self.onLockTarget(AimSound.TARGET_LOCKED, True)
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE, vehicleId=vehID)
            else:
                self.inputHandler.setAimingMode(False, AIMING_MODE.TARGET_LOCK)
                self.gunRotator.clientMode = True
                self.__aimingInfo[0] = BigWorld.time()
                minShotDisp = self.vehicleTypeDescriptor.gun.shotDispersionAngle
                self.__aimingInfo[1] = self.gunRotator.dispersionAngle / minShotDisp
                self.onLockTarget(AimSound.TARGET_UNLOCKED, True)
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE)
                if BigWorld.player().vehicle.isWheeledTech:
                    gui_event_dispatcher.hideAutoAimMarker()
        return

    def __gunDamagedSound(self):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.GUN_DAMAGE_SOUND, ())
        if self.__gunDamagedShootSound is not None:
            self.__gunDamagedShootSound.play()
        return

    def shoot(self, isRepeat=False):
        if self.__tryShootCallbackId is None:
            self.__tryShootCallbackId = BigWorld.callback(0.0, self.__tryShootCallback)
        if not self.__isOnArena:
            return
        else:
            for deviceName, stateName in self.__deviceStates.iteritems():
                msgName = self.__cantShootCriticals.get(deviceName + '_' + stateName)
                if msgName is not None:
                    if not isRepeat:
                        self.__gunDamagedSound()
                    self.showVehicleError(msgName)
                    return

            canShoot, error = self.guiSessionProvider.shared.ammo.canShoot(isRepeat)
            if not canShoot:
                if not isRepeat and error in self.__cantShootCriticals:
                    self.showVehicleError(self.__cantShootCriticals[error])
                return
            if self.__gunReloadCommandWaitEndTime > BigWorld.time():
                return
            if self.__shotWaitingTimerID is not None or self.__isWaitingForShot:
                return
            if self.isGunLocked or self.__isOwnBarrelUnderWater():
                if not isRepeat:
                    self.showVehicleError(self.__cantShootCriticals['gun_locked'])
                return
            if self.__isOwnVehicleSwitchingSiegeMode():
                return
            self.base.vehicle_shoot()
            self.__startWaitingForShot(error != CANT_SHOOT_ERROR.EMPTY_CLIP)
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_SHOOT, aimingInfo=self.__aimingInfo)
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
        if self.__isWaitingForShot:
            self.inputHandler.setAimingMode(False, AIMING_MODE.SHOOTING)
            self.gunRotator.targetLastShotPoint = False
            self.__isWaitingForShot = False
        return

    def selectPlayer(self, vehicleID):
        if self.isForcedGuiControlMode() and not BattleReplay.isPlaying():
            vehicleDesc = self.arena.vehicles.get(vehicleID)
            if vehicleDesc['isAlive'] and (vehicleDesc['team'] == self.team or self.isObserver()):
                self.inputHandler.selectPlayer(vehicleID)

    def leaveArena(self):
        LOG_DEBUG('Avatar.leaveArena')
        from helpers import statistics
        self.statsCollector.noteLastArenaData(self.arenaTypeID, self.arenaUniqueID, self.team)
        self.statsCollector.needCollectSessionData(True)
        self.statsCollector.noteHangarLoadingState(statistics.HANGAR_LOADING_STATE.CONNECTED, True)
        try:
            if self.__projectileMover is not None:
                self.__projectileMover.destroy()
                self.__projectileMover = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        BigWorld.PyGroundEffectManager().stopAll()
        g_playerEvents.isPlayerEntityChanging = True
        g_playerEvents.onPlayerEntityChanging()
        self.__setIsOnArena(False)
        self.base.leaveArena(None)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            BigWorld.callback(0.0, replayCtrl.stop)
        if replayCtrl.isRecording:
            replayCtrl.stop()
        return

    def addBotToArena(self, vehicleTypeName, team):
        compactDescr = vehicles.VehicleDescr(typeName=vehicleTypeName).makeCompactDescr()
        self.base.addBotToArena(compactDescr, team, self.name)

    def addBotToArenaEx(self, vehicleTypeName, team, *moduleIDs):
        ids = [0,
         0,
         0,
         0,
         0,
         0]
        for i, id_ in enumerate(moduleIDs[:6]):
            ids[i] = id_

        nationID, vehicleTypeID = vehicles.g_list.getIDsByName(vehicleTypeName)
        type_ = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
        c_desc = type_.chassis[ids[0]]
        e_desc = type_.engines[ids[1]]
        f_desc = type_.fuelTanks[ids[2]]
        r_desc = type_.radios[ids[3]]
        t_desc = type_.turrets[ids[4]][0]
        g_desc = t_desc.guns[ids[5]]
        stock = vehicles.VehicleDescr(typeName=vehicleTypeName)
        custom = stock
        custom.installComponent(c_desc.compactDescr)
        custom.installComponent(e_desc.compactDescr)
        custom.installComponent(f_desc.compactDescr)
        custom.installComponent(r_desc.compactDescr)
        custom.installTurret(t_desc.compactDescr, g_desc.compactDescr)
        compactDescr = custom.makeCompactDescr()
        self.base.addBotToArena(compactDescr, team, self.name)

    def controlAnotherVehicle(self, vehicleID, callback=None):
        BigWorld.entity(self.playerVehicleID).isPlayerVehicle = False
        self.base.controlAnotherVehicle(vehicleID, 1)
        if vehicleID not in BigWorld.entities.keys():
            BigWorld.callback(0.1, partial(self.__controlAnotherVehicleWait, vehicleID, callback, 50))
            return
        BigWorld.callback(1.0, partial(self.__controlAnotherVehicleAfteraction, vehicleID, callback))

    def setForcedGuiControlMode(self, flags):
        result = False
        if self.__forcedGuiCtrlModeFlags != flags:
            result = self.inputHandler.setForcedGuiControlMode(flags)
            if result and self.inputHandler.isDetached and self.inputHandler.ctrl.isSelfVehicle():
                self.moveVehicle(self.makeVehicleMovementCommandByKeys(), False)
        if flags & GUI_CTRL_MODE_FLAG.MOVING_DISABLED > 0:
            self.moveVehicle(0, False)
        self.__forcedGuiCtrlModeFlags = flags
        return result

    def isForcedGuiControlMode(self):
        return self.__forcedGuiCtrlModeFlags & GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED > 0

    def getForcedGuiControlModeFlags(self):
        return self.__forcedGuiCtrlModeFlags

    def getOwnVehiclePosition(self):
        return Math.Matrix(self.getOwnVehicleMatrix()).translation

    def getOwnVehicleMatrix(self):
        observedMatrix = self.getObservedVehicleMatrix()
        return observedMatrix if observedMatrix is not None else self.__ownVehicleMProv

    def getOwnVehicleStabilisedMatrix(self):
        observedMatrix = self.getObservedVehicleStabilisedMatrix()
        return observedMatrix if observedMatrix is not None else self.__ownVehicleStabMProv

    def getOwnVehicleSpeeds(self, getInstantaneous=False):
        vehicle = BigWorld.entity(self.playerVehicleID)
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
        if vehicle is None or not vehicle.isStarted:
            return self.__lastVehicleSpeeds
        else:
            speedInfo = vehicle.speedInfo.value
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

    def getOwnVehicleShotDispersionAngle(self, turretRotationSpeed, withShot=0):
        descr = self.__getDetailedVehicleDescriptor()
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
            shotFactor = descr.gun.shotDispersionFactors['afterShot']
        else:
            shotFactor = descr.gun.shotDispersionFactors['afterShotInBurst']
        shotFactor *= shotFactor
        idealFactor = vehicleMovementFactor + vehicleRotationFactor + turretRotationFactor + shotFactor
        additiveFactor = self.__getAdditiveShotDispersionFactor(descr)
        idealFactor *= additiveFactor ** 2
        idealFactor = multFactor * math.sqrt(1.0 + idealFactor)
        currTime = BigWorld.time()
        aimingFactor = aimingStartFactor * math.exp((aimingStartTime - currTime) / aimingTime)
        isGunReload = self.guiSessionProvider.shared.ammo.isGunReloading()
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
        return [descr.gun.shotDispersionAngle * aimingFactor, descr.gun.shotDispersionAngle * idealFactor]

    def handleVehicleCollidedVehicle(self, vehA, vehB, hitPt, time):
        if self.__vehicleToVehicleCollisions is None:
            return
        else:
            lastCollisionTime = 0
            key = (vehA.id, vehB.id)
            if not self.__vehicleToVehicleCollisions.has_key(key):
                key = (vehB.id, vehA.id)
            if self.__vehicleToVehicleCollisions.has_key(key):
                lastCollisionTime = self.__vehicleToVehicleCollisions[key]
            if time - lastCollisionTime < 0.2:
                return
            vehSpeedSum = (vehA.filter.velocity - vehB.filter.velocity).length
            if vehA is not self.vehicle:
                self.__vehicleToVehicleCollisions[key] = time
                vehA.showVehicleCollisionEffect(hitPt, vehSpeedSum)
            self.inputHandler.onVehicleCollision(vehA, vehSpeedSum)
            self.inputHandler.onVehicleCollision(vehB, vehSpeedSum)
            return

    def getVehicleDescriptor(self):
        descr = self.vehicleTypeDescriptor
        if self.isObserver() and self.getVehicleAttached() is not None:
            descr = self.getVehicleAttached().typeDescriptor
        return descr

    def receiveBattleResults(self, isSuccess, data):
        LOG_DEBUG('receiveBattleResults', isSuccess)
        if not isSuccess:
            return
        try:
            self.__battleResults = cPickle.loads(zlib.decompress(data))
            BattleResultsCache.save(self.name, self.__battleResults)
            LOG_DEBUG('Show battle results.')
            g_playerEvents.onBattleResultsReceived(True, BattleResultsCache.convertToFullForm(self.__battleResults))
            self.base.confirmBattleResultsReceiving()
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def tuneupVehiclePhysics(self, jsonStr):
        self.base.setDevelopmentFeature('tuneup_physics', 0, zlib.compress(jsonStr, 9))

    def tuneupVehicle(self, jsonStr):
        self.base.setDevelopmentFeature('tuneup_vehicle', 0, zlib.compress(jsonStr, 9))

    def receiveNotification(self, notification):
        LOG_DEBUG('receiveNotification', notification)
        g_wgncProvider.fromXmlString(notification)

    def messenger_onActionByServer_chat2(self, actionID, reqID, args):
        from messenger_common_chat2 import MESSENGER_ACTION_IDS as actions
        LOG_DEBUG('messenger_onActionByServer', actions.getActionName(actionID), reqID, args)
        MessengerEntry.g_instance.protos.BW_CHAT2.onActionReceived(actionID, reqID, args)

    def processInvitations(self, invitations):
        self.prebattleInvitations.processInvitations(invitations)

    def onUnitError(self, requestID, curUnitMgrID, errorCode, errorString):
        LOG_DEBUG('PlayerAvatar.onUnitError: requestID=%s, unitMgrID=%s, errorCode=%s, errorString=%s' % (requestID,
         curUnitMgrID,
         errorCode,
         errorString))

    def onUnitCallOk(self, requestID):
        LOG_DEBUG('PlayerAvatar.onUnitOk: requestID=%s' % requestID)

    def __onSiegeStateUpdated(self, vehicleID, newState, timeToNextState):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is not None:
            if vehicle.typeDescriptor is not None and vehicle.typeDescriptor.hasSiegeMode:
                vehicle.onSiegeStateUpdated(newState, timeToNextState)
            elif vehicle.isPlayerVehicle and self.__disableRespawnMode:
                self.__pendingSiegeSettings = (vehicleID, newState, timeToNextState)
        return

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

    def __createFakeCameraMatrix(self):
        BigWorld.camera(BigWorld.FreeCamera())
        vehicleMatrix = self.vehicle.matrix if self.vehicle is not None else self.matrix
        vehicleMatrix = Math.Matrix(vehicleMatrix)
        shiftMat = Math.Matrix()
        shiftMat.translation = Math.Vector3(0, 0, -5)
        vehicleMatrix.preMultiply(shiftMat)
        vehicleMatrix.invert()
        camMat = vehicleMatrix
        BigWorld.camera().set(camMat)
        return

    def setClientReady(self):
        if self.__initProgress < _INIT_STEPS.ALL_STEPS_PASSED or self.__initProgress & _INIT_STEPS.PLAYER_READY:
            return
        self.__initProgress |= _INIT_STEPS.PLAYER_READY
        self.inputHandler.setForcedGuiControlMode(self.__forcedGuiCtrlModeFlags)
        for v in BigWorld.entities.values():
            if v.inWorld and isinstance(v, Vehicle.Vehicle) and not v.isStarted:
                self.__startVehicleVisual(v)

        BattleReplay.g_replayCtrl.onClientReady()
        self.base.setClientReady()
        if self.arena.period == ARENA_PERIOD.BATTLE:
            self.__setIsOnArena(True)
        self.arena.onPeriodChange += self.__onArenaPeriodChange
        self.cell.autoAim(0, False)
        g_playerEvents.onAvatarReady()

    def __onInitStepCompleted(self):
        self.__createFakeCameraMatrix()
        LOG_DEBUG('Avatar.__onInitStepCompleted()', self.__initProgress)
        if constants.IS_CAT_LOADED:
            if self.__initProgress & _INIT_STEPS.INIT_COMPLETED:
                return
        if self.__initProgress < _INIT_STEPS.ALL_STEPS_PASSED or self.__initProgress & _INIT_STEPS.INIT_COMPLETED:
            return
        self.__initProgress |= _INIT_STEPS.INIT_COMPLETED
        self.initSpace()
        SoundGroups.g_instance.enableArenaSounds(True)
        SoundGroups.g_instance.applyPreferences()
        MusicControllerWWISE.onEnterArena()
        TriggersManager.g_manager.enable(True)
        BigWorld.wg_enableTreeHiding(False)
        BigWorld.worldDrawEnabled(True)
        BigWorld.uniprofSceneStart()
        BigWorld.wg_setWaterTexScale(self.arena.arenaType.waterTexScale)
        BigWorld.wg_setWaterFreqX(self.arena.arenaType.waterFreqX)
        BigWorld.wg_setWaterFreqZ(self.arena.arenaType.waterFreqZ)
        clientVisibilityFlags = 0
        if self.isObserver():
            clientVisibilityFlags |= ClientVisibilityFlags.OBSERVER_OBJECTS
        ClientVisibilityFlags.updateSpaceVisibility(self.spaceID, clientVisibilityFlags)
        BigWorld.callback(10.0, partial(BigWorld.pauseDRRAutoscaling, False))
        appearance_cache.onSpaceLoaded()
        self.__projectileMover.setSpaceID(self.spaceID)
        if self.isObserver():
            import VehicleObserverGunRotator
            self.gunRotator = VehicleObserverGunRotator.VehicleObserverGunRotator(self)
        else:
            import VehicleGunRotator
            self.gunRotator = VehicleGunRotator.VehicleGunRotator(self)
        self.positionControl = AvatarPositionControl.AvatarPositionControl(self)
        self.__startGUI()
        self.__hackSpaceKeeper = BigWorld.Model('')
        BigWorld.addModel(self.__hackSpaceKeeper, self.spaceID)

    def __initGUI(self):
        prereqs = []
        if not g_offlineMapCreator.Active():
            self.inputHandler = AvatarInputHandler.AvatarInputHandler()
            prereqs += self.inputHandler.prerequisites()
        BigWorld.player().arena
        self.soundNotifications = IngameSoundNotifications.IngameSoundNotifications()
        self.complexSoundNotifications = IngameSoundNotifications.ComplexSoundNotifications(self.soundNotifications)
        return prereqs

    def __startGUI(self):
        self.inputHandler.start()
        self.arena.onVehicleKilled += self.__onArenaVehicleKilled
        MessengerEntry.g_instance.onAvatarInitGUI()
        self.soundNotifications.start()

    def __destroyGUI(self):
        self.arena.onVehicleKilled -= self.__onArenaVehicleKilled
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
        self.setForcedGuiControlMode(GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED | GUI_CTRL_MODE_FLAG.MOVING_DISABLED | GUI_CTRL_MODE_FLAG.AIMING_ENABLED)
        self.setForcedGuiControlMode(GUI_CTRL_MODE_FLAG.CURSOR_DETACHED)

    def setComponentsVisibility(self, flag):
        vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle is None:
            return
        else:
            if flag and vehicle.isAlive():
                vehicle.drawEdge()
            else:
                vehicle.removeEdge()
            CombatEquipmentManager.setGUIVisible(self, flag)
            self.inputHandler.setGUIVisible(flag)
            return

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
                if self.gunRotator is not None:
                    self.gunRotator.stop()
            else:
                if self.gunRotator is not None:
                    self.gunRotator.start()
                self.moveVehicle(self.makeVehicleMovementCommandByKeys(), False)
                self.guiSessionProvider.shared.ammo.applySettings(self)
            return

    def showVehicleError(self, msgName, args=None):
        self.guiSessionProvider.shared.messages.showVehicleError(msgName, args)

    def __getDetailedVehicleDescriptor(self):
        vehicleAttached = self.getVehicleAttached()
        if vehicleAttached is None:
            return self.getVehicleDescriptor()
        else:
            vehInfo = self.arena.vehicles.get(vehicleAttached.id)
            if vehInfo is not None:
                desc = vehInfo['vehicleType']
                if desc.hasSiegeMode:
                    desc.onSiegeStateChanged(vehicleAttached.siegeState)
                return desc
            return vehicleAttached.typeDescriptor
            return

    def __showDamageIconAndPlaySound(self, damageCode, extra, vehicleID):
        deviceName = None
        deviceState = None
        soundType = None
        soundNotificationCheckFn = None
        if damageCode in self.__damageInfoFire:
            extra = self.vehicleTypeDescriptor.extrasDict['fire']
            self.__fireInVehicle = damageCode != 'FIRE_STOPPED'
            soundType = 'critical' if self.__fireInVehicle else 'fixed'
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE, self.__fireInVehicle)
            curFireState = self.__fireInVehicle
            soundNotificationCheckFn = lambda : curFireState == self.__fireInVehicle
            if self.__fireInVehicle:
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_IN_FIRE)
            else:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_VEHICLE_IN_FIRE)
        elif extra is not None:
            if damageCode in self.__damageInfoCriticals:
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
                if damageCode.find('TANKMAN_HIT') != -1:
                    if 'crew_member_contusion' not in self._muteSounds:
                        self.soundNotifications.play('crew_member_contusion')
                vehicle = BigWorld.entity(vehicleID)
                if vehicle is not None and damageCode not in self.__damageInfoNoNotification:
                    vehicle.appearance.executeCriticalHitVibrations(vehicle, extra.name)
                if damageCode == 'TANKMAN_HIT' or damageCode == 'TANKMAN_HIT_AT_SHOT':
                    TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_TANKMAN_SHOOTED)
            elif damageCode in self.__damageInfoHealings:
                deviceName = extra.name[:-len('Health')]
                deviceState = 'normal'
                soundType = 'fixed'
                self.__deviceStates.pop(deviceName, None)
                if damageCode == 'TANKMAN_RESTORED':
                    TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.PLAYER_TANKMAN_SHOOTED)
        if deviceState is not None:
            if deviceName in self.__deviceStates:
                actualState = self.__deviceStates[deviceName]
            else:
                actualState = 'normal'
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEVICES, (deviceName, deviceState, actualState))
            vehicle = self.getVehicleAttached()
            if vehicle is not None and vehicle.id == vehicleID:
                vehicle.appearance.deviceStateChanged(deviceName, deviceState)
            if deviceState == 'repaired':
                deviceState = 'critical'
            if damageCode.find('DEVICE_REPAIRED') != -1 and deviceName == 'gun':
                if self.__gunDamagedShootSound is not None and self.__gunDamagedShootSound.isPlaying:
                    self.__gunDamagedShootSound.stop()
            soundNotificationCheckFn = lambda : self.__deviceStates.get(deviceName, 'normal') == deviceState
        if soundType is not None and damageCode not in self.__damageInfoNoNotification:
            sound = extra.sounds.get(soundType)
            if sound in self._muteSounds:
                sound = None
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
     'ENGINE_CRITICAL_AT_UNLIMITED_RPM',
     'ENGINE_CRITICAL_AT_BURNOUT')
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
     'ENGINE_DESTROYED_AT_UNLIMITED_RPM',
     'ENGINE_DESTROYED_AT_BURNOUT')
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

    def __onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason):
        if self.__autoAimVehID != 0 and self.__autoAimVehID == targetID and self.__isVehicleAlive:
            self.onLockTarget(AimSound.TARGET_LOST, False)
        isMyVehicle = targetID == self.playerVehicleID
        isObservedVehicle = not self.__isVehicleAlive and targetID == getattr(self.inputHandler.ctrl, 'curVehicleID', None)
        if isMyVehicle or isObservedVehicle:
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DESTROY_TIMER, DestroyTimerViewState.makeCloseAllState())
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEATHZONE_TIMER, DeathZoneTimerViewState.makeCloseAllState())
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.UNDER_FIRE, False)
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.RECOVERY, (False, 0, None))
            deathInfo = {'killerID': attackerID,
             'reason': reason}
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEATH_INFO, deathInfo)
            try:
                if self.gunRotator is not None:
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
            self.guiSessionProvider.shared.messages.showVehicleKilledMessage(self, targetID, attackerID, equipmentID, reason)
            return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        self.__setIsOnArena(period == ARENA_PERIOD.BATTLE)
        if period == ARENA_PERIOD.PREBATTLE and period > self.__prevArenaPeriod:
            LightManager.GameLights.startTicks()
            if AuxiliaryFx.g_instance is not None:
                AuxiliaryFx.g_instance.execEffect('startTicksEffect')
        if period == ARENA_PERIOD.BATTLE and period > self.__prevArenaPeriod:
            if self.arenaBonusType == constants.ARENA_BONUS_TYPE.EPIC_BATTLE:
                if self.__prevArenaPeriod >= 0:
                    self.soundNotifications.play(EPIC_SOUND.BF_EB_START_BATTLE[self.team])
            else:
                self.soundNotifications.play('start_battle')
            LightManager.GameLights.roundStarted()
            if AuxiliaryFx.g_instance is not None:
                AuxiliaryFx.g_instance.execEffect('roundStartedEffect')
        self.__prevArenaPeriod = period
        return

    def __startWaitingForShot(self, makePrediction):
        if makePrediction:
            if self.__shotWaitingTimerID is not None:
                BigWorld.cancelCallback(self.__shotWaitingTimerID)
                self.__shotWaitingTimerID = None
            timeout = BigWorld.LatencyInfo().value[3] * 0.5
            timeout = min(_SHOT_WAITING_MAX_TIMEOUT, timeout)
            timeout = max(_SHOT_WAITING_MIN_TIMEOUT, timeout)
            self.__shotWaitingTimerID = BigWorld.callback(timeout, self.__showTimedOutShooting)
            self.__isWaitingForShot = True
            self.inputHandler.setAimingMode(True, AIMING_MODE.SHOOTING)
            if not self.inputHandler.getAimingMode(AIMING_MODE.USER_DISABLED):
                self.gunRotator.targetLastShotPoint = True
            self.__gunReloadCommandWaitEndTime = BigWorld.time() + 2.0
        return

    def __showTimedOutShooting(self):
        self.__shotWaitingTimerID = None
        self.__isWaitingForShot = False
        self.inputHandler.setAimingMode(False, AIMING_MODE.SHOOTING)
        self.gunRotator.targetLastShotPoint = False
        try:
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is not None and vehicle.isStarted:
                return self.__isOwnBarrelUnderWater() and None
            gunDescr = vehicle.typeDescriptor.gun
            burstCount = gunDescr.burst[0]
            ammo = self.guiSessionProvider.shared.ammo
            if ammo.getCurrentShellCD() is not None:
                totalShots, shotsInClip = ammo.getCurrentShells()
                if burstCount > totalShots > 0:
                    burstCount = totalShots
                if gunDescr.clip[0] > 1:
                    if burstCount > shotsInClip > 0:
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
            vehicle.isPlayerVehicle = True
            self.__isVehicleAlive = True
            self.playerVehicleID = vehicleID
            self.vehicleTypeDescriptor = vehicle.typeDescriptor
            self.base.controlAnotherVehicle(vehicleID, 2)
            self.gunRotator.clientMode = False
            self.gunRotator.start()
            self.base.setDevelopmentFeature('server_marker', True, '')
            self.base.setDevelopmentFeature('heal', 0, '')
            self.base.setDevelopmentFeature('stop_bot', 0, '')
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
            LOG_NOTE('Vehicle turret: ', self.vehicleTypeDescriptor.turret.name)
            LOG_NOTE('Vehicle gun: ', self.vehicleTypeDescriptor.gun.name)
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
            if type(e) == AreaDestructibles.AreaDestructibles:
                numAreaDestrs += 1

        msg += '\tnum Vehicle: %d\n\tnum AreaDestructibles: %d\n' % (numVehs, numAreaDestrs)
        msg += '\tarena: %s\n' % self.arena.arenaType.geometryName
        msg += '\tposition: ' + str(self.position)
        LOG_NOTE(msg)
        self.base.setDevelopmentFeature('log_lag', True, '')

    def __updateCruiseControlPanel(self):
        if self.__stopUntilFire or not self.__isVehicleAlive:
            mode = _CRUISE_CONTROL_MODE.NONE
        else:
            mode = self.__cruiseControlMode
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CRUISE_MODE, mode)

    def __applyTimeAndWeatherSettings(self, overridePresetID=None):
        presets = self.arena.arenaType.weatherPresets
        weather = Weather.weather()
        if not presets or presets[0].get('name') is None:
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

    def __processVehicleAmmo(self, vehicleID, compactDescr, quantity, quantityInClip, _, __):
        self.processObservedVehicleAmmo(vehicleID, compactDescr, quantity, quantityInClip)
        self.guiSessionProvider.shared.ammo.setShells(compactDescr, quantity, quantityInClip)

    def __processVehicleEquipments(self, vehicleID, compactDescr, quantity, stage, timeRemaining, totalTime):
        self.processObservedVehicleEquipments(vehicleID, compactDescr, quantity, stage, timeRemaining, totalTime)
        if compactDescr:
            descriptor = vehicles.getItemByCompactDescr(compactDescr)
            if descriptor.name == 'aimingStabilizerBattleBooster':
                self.__aimingBooster = descriptor
        self.guiSessionProvider.shared.equipments.setEquipment(compactDescr, quantity, stage, timeRemaining, totalTime)

    def __isOwnBarrelUnderWater(self):
        ownVehicle = BigWorld.entity(self.playerVehicleID)
        if ownVehicle is None or not ownVehicle.isStarted:
            return
        else:
            turretYaw = Math.Matrix(self.gunRotator.turretMatrix).yaw
            gunPitch = Math.Matrix(self.gunRotator.gunMatrix).pitch
            lp = computeBarrelLocalPoint(ownVehicle.typeDescriptor, turretYaw, gunPitch)
            wp = Math.Matrix(ownVehicle.matrix).applyPoint(lp)
            up = Math.Vector3((0.0, 0.1, 0.0))
            return BigWorld.wg_collideWater(wp, wp + up, False) != -1.0

    def __isOwnVehicleSwitchingSiegeMode(self):
        ownVehicle = BigWorld.entity(self.playerVehicleID)
        return None if ownVehicle is None or not ownVehicle.isStarted else ownVehicle.siegeState in VEHICLE_SIEGE_STATE.SWITCHING

    def __fireNonFatalDamageTrigger(self, targetId):
        self.__fireNonFatalDamageTriggerID = None
        vehicle = BigWorld.entities.get(targetId)
        if vehicle is not None:
            if not vehicle.isPlayerVehicle and vehicle.isAlive():
                TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_MADE_NONFATAL_DAMAGE, targetId=targetId)
        return

    def __getRequestID(self):
        self.__requestID += 1
        if self.__requestID >= AccountCommands.REQUEST_ID_UNRESERVED_MAX:
            self.__requestID = AccountCommands.REQUEST_ID_UNRESERVED_MIN
        return self.__requestID

    def __doCmd(self, doCmdMethod, cmd, callback, *args):
        if Account.g_accountRepository is None and not BattleReplay.isPlaying():
            return
        else:
            requestID = self.__getRequestID()
            if requestID is None:
                return
            if callback is not None:
                self.__onCmdResponse[requestID] = callback
            getattr(self.base, doCmdMethod)(requestID, cmd, *args)
            return

    def _doCmdStr(self, cmd, s, callback):
        self.__doCmd('doCmdStr', cmd, callback, s)

    def _doCmdInt2(self, cmd, int1, int2, callback):
        self.__doCmd('doCmdInt2', cmd, callback, int1, int2)

    def _doCmdInt3(self, cmd, int1, int2, int3, callback):
        self.__doCmd('doCmdInt3', cmd, callback, int1, int2, int3)

    def _doCmdInt4(self, cmd, int1, int2, int3, int4, callback):
        self.__doCmd('doCmdInt4', cmd, callback, int1, int2, int3, int4)

    def _doCmdInt2Str(self, cmd, int1, int2, s, callback):
        self.__doCmd('doCmdInt2Str', cmd, callback, int1, int2, s)

    def _doCmdIntArr(self, cmd, arr, callback):
        self.__doCmd('doCmdIntArr', cmd, callback, arr)

    def _doCmdIntArrStrArr(self, cmd, intArr, strArr, callback):
        self.__doCmd('doCmdIntArrStrArr', cmd, callback, intArr, strArr)

    def _doCmdStrArr(self, cmd, strArr, callback):
        self.__doCmd('doCmdStrArr', cmd, callback, strArr)

    def update(self, pickledDiff):
        self._update(cPickle.loads(pickledDiff))

    def _update(self, diff):
        if self.intUserSettings is not None:
            self.intUserSettings.synchronize(False, diff)
            g_playerEvents.onClientUpdated(diff, False)
        return

    def isSynchronized(self):
        return True if self.intUserSettings is None else self.intUserSettings.isSynchronized()

    def __isShootPositionInsideOtherVehicle(self):
        vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle is not None and vehicle.isStarted:
            turretPosition, shootPosition = getVehicleShootingPositions(vehicle)
            return isShootPositionInsideOtherVehicle(vehicle, turretPosition, shootPosition)
        else:
            return False

    def killEngine(self):
        self.base.setDevelopmentFeature('kill_engine', 0, '')

    def receivePhysicsDebugInfo(self, info):
        modifD = dict()
        self.telemetry.receivePhysicsDebugInfo(info, modifD)

    def physicModeChanged(self, newMode):
        self.__physicsMode = newMode

    def __isPlayerInSquad(self, vehicleId):
        return self.arena is not None and self.arena.guiType in (constants.ARENA_GUI_TYPE.RANDOM, constants.ARENA_GUI_TYPE.EPIC_RANDOM, constants.ARENA_GUI_TYPE.EPIC_BATTLE) and self.guiSessionProvider.getArenaDP().isSquadMan(vID=vehicleId)

    def __getAdditiveShotDispersionFactor(self, descriptor):
        if self.__aimingBooster is not None:
            factors = descriptor.miscAttrs.copy()
            self.__aimingBooster.updateVehicleAttrFactors(descriptor, factors, None)
        else:
            factors = descriptor.miscAttrs
        return factors['additiveShotDispersionFactor']

    def muteSounds(self, newMuteSounds):
        self._muteSounds = newMuteSounds

    def onLockTarget(self, state, playVoiceNotifications):
        if playVoiceNotifications:
            AimSound.play(state, self.soundNotifications)
        else:
            AimSound.play(state)
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onLockTarget(state, playVoiceNotifications)


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
    else:
        return (newSoundName, otherData, newSoundPriority) if newSoundPriority > currBest[2] else currBest


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

    def __init__(self, entityFilter=None, period=5):
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
    gunOffs = vd.turret.gunPosition
    turretOffs = vd.hull.turretPositions[0] + vd.chassis.hullPosition
    turretYaw, gunPitch = decodeGunAngles(vehicle.gunAnglesPacked, vd.gun.pitchLimits['absolute'])
    turretWorldMatrix = Math.Matrix()
    turretWorldMatrix.setRotateY(turretYaw)
    turretWorldMatrix.translation = turretOffs
    turretWorldMatrix.postMultiply(vehicle.model.matrix)
    gunWorldMatrix = Math.Matrix()
    gunWorldMatrix.setRotateX(gunPitch)
    gunWorldMatrix.postMultiply(turretWorldMatrix)
    return (turretWorldMatrix.applyPoint(gunOffs), turretWorldMatrix.translation)
