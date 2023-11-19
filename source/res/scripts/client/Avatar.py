# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Avatar.py
import cPickle
import logging
import math
import weakref
import zlib
from functools import partial
import BigWorld
import Keys
import Math
import ResMgr
import WWISE
import WoT
import CGF
import Account
import AccountCommands
import AreaDestructibles
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
import VehicleGunRotator
import VehicleObserverGunRotator
import Weather
import constants
from AimSound import AimSound
from AvatarInputHandler import cameras, keys_handlers
from AvatarInputHandler.RespawnDeathMode import RespawnDeathMode
from AvatarInputHandler.control_modes import ArcadeControlMode, VideoCameraControlMode, PostMortemControlMode
from AvatarInputHandler.epic_battle_death_mode import DeathFreeCamMode
from BattleReplay import CallbackDataNames
from ChatManager import chatManager
from ClientChat import ClientChat
from Flock import DebugLine
from OfflineMapCreator import g_offlineMapCreator
from PlayerEvents import g_playerEvents
from TriggersManager import TRIGGER_TYPE
from account_helpers import BattleResultsCache, ClientInvitations
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from avatar_components.AvatarObserver import AvatarObserver
from avatar_components.CombatEquipmentManager import CombatEquipmentManager
from avatar_components.VehiclesSpawnListStorage import VehiclesSpawnListStorage
from avatar_components.avatar_chat_key_handling import AvatarChatKeyHandling
from avatar_components.avatar_epic_data import AvatarEpicData
from avatar_components.avatar_recovery_mechanic import AvatarRecoveryMechanic
from avatar_components.avatar_respawn_mechanic import AvatarRespawnMechanic
from avatar_components.team_healthbar_mechanic import TeamHealthbarMechanic
from avatar_components.triggers_controller import TriggersController
from avatar_components.vehicle_health_broadcast_listener_component import VehicleHealthBroadcastListenerComponent
from avatar_components.vehicle_removal_controller import VehicleRemovalController
from avatar_components.visual_script_controller import VisualScriptController
from avatar_helpers import AvatarSyncData, getBestShotResultSound
from battle_results_shared import AVATAR_PRIVATE_STATS, listToDict
from bootcamp.Bootcamp import g_bootcamp
from constants import ARENA_PERIOD, AIMING_MODE, VEHICLE_SETTING, DEVELOPMENT_INFO, ARENA_GUI_TYPE
from constants import DEFAULT_VECTOR_3
from constants import DROWN_WARNING_LEVEL
from constants import DUAL_GUN, DUALGUN_CHARGER_STATUS, DUALGUN_CHARGER_ACTION_TYPE
from constants import TARGET_LOST_FLAGS
from constants import VEHICLE_MISC_STATUS, VEHICLE_HIT_FLAGS, VEHICLE_SIEGE_STATE
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG_DEV, LOG_CODEPOINT_WARNING, LOG_NOTE
from DualAccuracy import getPlayerVehicleDualAccuracy
from gui import GUI_CTRL_MODE_FLAG, IngameSoundNotifications, SystemMessages
from gui.app_loader import settings as app_settings
from gui.battle_control import BattleSessionSetup
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CANT_SHOOT_ERROR, DestroyTimerViewState, DeathZoneTimerViewState, TIMER_VIEW_STATE, ENTITY_IN_FOCUS_TYPE
from gui.game_loading.resources.consts import Milestones
from gui.prb_control.formatters import messages
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.sounds.epic_sound_constants import EPIC_SOUND
from gui.wgnc import g_wgncProvider
from gun_rotation_shared import decodeGunAngles
from helpers import bound_effects, dependency, uniprof
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles
from material_kinds import EFFECT_MATERIALS
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from physics_shared import computeBarrelLocalPoint
from shared_utils.avatar_helpers import DualGun
from math_utils import almostZero
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.helpers.statistics import IStatisticsCollector
from soft_exception import SoftException
from streamIDs import RangeStreamIDCallbacks, STREAM_ID_CHAT_MAX, STREAM_ID_CHAT_MIN, STREAM_ID_AVATAR_BATTLE_RESULS
from vehicle_systems.stricted_loading import makeCallbackWeak
from messenger import MessengerEntry
from battle_modifiers_common import BattleModifiers, BattleParams
import VOIP
_logger = logging.getLogger(__name__)

class _CRUISE_CONTROL_MODE(object):
    NONE = 0
    FWD25 = 1
    FWD50 = 2
    FWD100 = 3
    BCKW50 = -1
    BCKW100 = -2


_SHOT_WAITING_MAX_TIMEOUT = 0.2
_SHOT_WAITING_MIN_TIMEOUT = 0.12
_MAX_SPEED_MULTIPLIER = 1.5
_MAX_ROTATION_SPEED_MULTIPLIER = 1.5
_SPEEDOMETER_CORRECTION_DELTA = 0.25

class MOVEMENT_FLAGS(object):
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
    WAIT_PLAYER_CHOICE = 64


AVATAR_COMPONENTS = {CombatEquipmentManager,
 AvatarObserver,
 TeamHealthbarMechanic,
 AvatarEpicData,
 AvatarRecoveryMechanic,
 AvatarRespawnMechanic,
 VehiclesSpawnListStorage,
 VehicleRemovalController,
 VehicleHealthBroadcastListenerComponent,
 AvatarChatKeyHandling,
 TriggersController,
 VisualScriptController}

class VehicleDeinitFailureException(SoftException):

    def __init__(self):
        super(VehicleDeinitFailureException, self).__init__('Exception during vehicle deinit has been detected, thus leading to unstable state of it. Please, check the first exception happened in this function call instead of analyzing c++ crash.')


class PlayerAvatar(BigWorld.Entity, ClientChat, CombatEquipmentManager, AvatarObserver, TeamHealthbarMechanic, AvatarEpicData, AvatarRecoveryMechanic, AvatarRespawnMechanic, VehiclesSpawnListStorage, VehicleRemovalController, VehicleHealthBroadcastListenerComponent, AvatarChatKeyHandling, TriggersController, VisualScriptController):
    __onStreamCompletePredef = {STREAM_ID_AVATAR_BATTLE_RESULS: 'receiveBattleResults'}
    isOnArena = property(lambda self: self.__isOnArena)
    isVehicleAlive = property(lambda self: self.__isVehicleAlive)
    isWaitingForShot = property(lambda self: self.__isWaitingForShot)
    autoAimVehicle = property(lambda self: BigWorld.entities.get(self.__autoAimVehID, None))
    deviceStates = property(lambda self: self.__deviceStates)
    vehicles = property(lambda self: self.__vehicles)
    consistentMatrices = property(lambda self: self.__consistentMatrices)
    isVehicleOverturned = property(lambda self: self.__isVehicleOverturned)
    isVehicleDrowning = property(lambda self: self.__isVehicleDrowning)
    isOwnBarrelUnderWater = property(lambda self: self.__isOwnBarrelUnderWater())
    inCharge = property(lambda self: self.__chargeWaitingTimerID is not None)
    isDisableRespawnMode = property(lambda self: self.__disableRespawnMode)
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    appLoader = dependency.descriptor(IAppLoader)
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    canMakeDualShot = property(lambda self: self.__canMakeDualShot)
    magneticAutoAimTags = property(lambda self: self.__magneticAutoAimTags)
    followTeamID = property(lambda self: self.observableTeamID if self.observableTeamID else self.team)

    def __init__(self):
        _logger.info('client Avatar.init')
        g_playerEvents.onLoadingMilestoneReached(Milestones.LOAD_CONTENT)
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
                self.spaFlags = repository.spaFlags
                self.dogTags = repository.dogTags
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
        self.__tryChargeCallbackID = None
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
        self.__chargeWaitingTimerID = None
        self.__dualGunHelper = None
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
        self.__ownVehicleTurretMProv = self.__consistentMatrices.ownVehicleTurretMProv
        self.__isVehicleOverturned = False
        self.__isVehicleDrowning = False
        self.__battleResults = None
        self.__gunDamagedShootSound = None
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.GUN_DAMAGE_SOUND, self.__gunDamagedSound)
        self.__aimingBooster = None
        self.__canMakeDualShot = False
        self.__magneticAutoAimTags = self.lobbyContext.getServerSettings().getMagneticAutoAimConfig().get('enableForTags', set())
        self.__vehiclesWaitedInfo = {}
        self.__isVehicleMoving = False
        self.__deadOnLoading = False
        self.arena = None
        return

    @property
    def fireInVehicle(self):
        playerVehicle = BigWorld.entities[self.playerVehicleID]
        return playerVehicle.isOnFire() if playerVehicle else False

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def onBecomePlayer(self):
        uniprof.enterToRegion('avatar.entering')
        _logger.info('[INIT_STEPS] Avatar.onBecomePlayer')
        self.__dynamicObjectsCache.load(self.arenaGuiType)
        BigWorld.cameraSpaceID(0)
        BigWorld.camera(BigWorld.CursorCamera())
        chatManager.switchPlayerProxy(self)
        g_playerEvents.isPlayerEntityChanging = False
        if BattleReplay.isServerSideReplay():
            originalPlayerVehicleID = self.playerVehicleID
        self.playerVehicleID = 0
        self.__isSpaceInitialized = False
        self.__isOnArena = False
        uniprof.enterToRegion('avatar.arena.loading')
        BigWorld.enableLoadingTimer(True)
        self.arena = ClientArena.ClientArena(self.arenaUniqueID, self.arenaTypeID, self.arenaBonusType, self.arenaGuiType, self.arenaExtraData, self.spaceID)
        AreaDestructibles.g_destructiblesManager.startSpace(self.spaceID)
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
            self.onObserverVehicleChanged = Event.Event()
            self.invRotationOnBackMovement = False
            self.onSwitchingViewPoint = Event.Event()
            self.onGoodiesSnapshotUpdated = Event.Event()
            self.__isVehicleAlive = True
            self.__firstHealthUpdate = True
            self.__deadOnLoading = False
            self.__isRespawnAvailable = False
            self.__ownVehicleStabMProv = Math.WGAdaptiveMatrixProvider()
            self.__ownVehicleStabMProv.setStaticTransform(Math.Matrix())
            self.__aimingInfo = [0.0,
             0.0,
             0.0,
             0.0]
            self.__dispersionInfo = [1.0,
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
            self.__forcedGuiCtrlModeFlags = GUI_CTRL_MODE_FLAG.CURSOR_DETACHED
            self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
            self.__stopUntilFire = False
            self.__stopUntilFireStartTime = -1
            self.__lastTimeOfKeyDown = -1
            self.__lastKeyDown = Keys.KEY_NONE
            self.__numSimilarKeyDowns = 0
            self.target = None
            self.__autoAimVehID = 0
            self.__shotWaitingTimerID = None
            self.__isWaitingForShot = False
            self.__gunReloadCommandWaitEndTime = 0.0
            self.__prevGunReloadTimeLeft = -1.0
            self.__vehicleToVehicleCollisions = {}
            self.__deviceStates = {}
            self.__maySeeOtherVehicleDamagedDevices = False
            if self.intUserSettings is not None:
                self.intUserSettings.onProxyBecomePlayer()
                self.syncData.onAvatarBecomePlayer()
            if self.prebattleInvitations is not None:
                self.prebattleInvitations.onProxyBecomePlayer()
            for comp in AVATAR_COMPONENTS:
                comp.onBecomePlayer(self)

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
            MusicControllerWWISE.onBecomePlayer()
            self.__flockMangager.start(self)
            self.__gunDamagedShootSound = SoundGroups.g_instance.getSound2D('gun_damaged')
            if not g_offlineMapCreator.Active():
                self.cell.switchObserverFPV(False)
            BigWorld.worldDrawEnabled(False)
            uniprof.exitFromRegion('avatar.entering')
            from battleground.location_point_manager import g_locationPointManager
            g_locationPointManager.activate()
            if BattleReplay.isServerSideReplay():
                self.playerVehicleID = originalPlayerVehicleID
            return

    def loadPrerequisites(self, prereqs):
        from battleground.location_point_manager import g_locationPointManager
        g_locationPointManager.loadPrerequisites()
        BigWorld.loadResourceListBG(prereqs, makeCallbackWeak(self.onPrereqsLoaded, prereqs))

    def onPrereqsLoaded(self, resNames, resourceRefs):
        failedRefs = resourceRefs.failedIDs
        for resName in resNames:
            if resName not in failedRefs:
                self.__prereqs[resName] = resourceRefs[resName]
            LOG_WARNING('Resource is not found', resName)

    def onBecomeNonPlayer(self):
        uniprof.exitFromRegion('avatar.arena.battle')
        uniprof.enterToRegion('avatar.exiting')
        _logger.info('[INIT_STEPS] Avatar.onBecomeNonPlayer')
        try:
            if self.gunRotator is not None:
                self.gunRotator.destroy()
                self.gunRotator = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.__destroyGUI()
        self.__dynamicObjectsCache.unload(self.arenaGuiType)
        self.__flockMangager.stop(self)
        self.statsCollector.stop()
        from battleground.location_point_manager import g_locationPointManager
        g_locationPointManager.deactivate()
        BigWorld.worldDrawEnabled(False)
        BigWorld.target.clear()
        MusicControllerWWISE.onLeaveArena()
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.enable(False)
        for v in BigWorld.entities.values():
            if isinstance(v, Vehicle.Vehicle):
                if v.isStarted:
                    try:
                        self.onVehicleLeaveWorld(v)
                        if self.playerVehicleID == v.id:
                            g_playerEvents.onAvatarVehicleLeaveWorld()
                        v.stopVisual()
                    except:
                        LOG_CURRENT_EXCEPTION()
                        raise VehicleDeinitFailureException()

                elif v.isHidden:
                    v.stopGUIVisual()

        if self.__initProgress & _INIT_STEPS.INIT_COMPLETED:
            try:
                SoundGroups.g_instance.enableArenaSounds(False)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.guiSessionProvider.stop()
        self.__dualGunHelper = None
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
        if self.__tryChargeCallbackID is not None:
            BigWorld.cancelCallback(self.__tryChargeCallbackID)
        self.__cancelWaitingForCharge()
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

        try:
            self.arena.destroy()
            self.arena = None
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            vehicles.g_cache.clearPrereqs()
            BattleModifiers.clearVehicleModifications()
            BattleModifiers.clearConstantsModifications()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        Vehicle.Vehicle.onArenaDestroyed()
        AreaDestructibles.clear()
        self.__ownVehicleMProv.target = None
        self.__ownVehicleTurretMProv.target = None
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

        from helpers import EffectsList
        EffectsList.EffectsListPlayer.clear()
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
        if self.__vehiclesWaitedInfo:
            self.__vehiclesWaitedInfo.clear()
        self.__vehiclesWaitedInfo = None
        uniprof.exitFromRegion('avatar.exiting')
        return

    def onEnterWorld(self, prereqs):
        _logger.info('[INIT_STEPS] Avatar.onEnterWorld')
        if self.__initProgress & _INIT_STEPS.ENTERED_WORLD > 0:
            return
        else:
            self.__initProgress |= _INIT_STEPS.ENTERED_WORLD
            self.__onInitStepCompleted()
            if g_offlineMapCreator.Active():
                self.playerVehicleID = 0
                self.planeTrajectory = None
                self.XPUpdated = None
                self.combatEquipmentShot = None
                self.questProgress = None
                self.developmentInfo = None
                self.showHittingArea = None
            if self.playerVehicleID != 0:
                if not BattleReplay.isPlaying():
                    self.set_playerVehicleID(0)
                else:
                    BigWorld.callback(0, partial(self.set_playerVehicleID, 0))
            self.__consistentMatrices.notifyEnterWorld(self)
            AvatarObserver.onEnterWorld(self)
            return

    def onLeaveWorld(self):
        _logger.info('[INIT_STEPS] Avatar.onLeaveWorld')
        self.__consistentMatrices.notifyLeaveWorld(self)
        self.__cancelWaitingForCharge()

    def onVehicleChanged(self):
        _logger.info('Avatar vehicle has changed to %s', self.vehicle)
        AvatarObserver.onVehicleChanged(self)
        if self.vehicle is not None:
            self.__consistentMatrices.notifyVehicleChanged(self)
            ctrl = self.guiSessionProvider.shared.vehicleState
            if self.vehicle.stunInfo.stunFinishTime > 0.0 and (self.isObserver() or ctrl.isInPostmortem):
                self.vehicle.updateStunInfo()
            if self.__dualGunHelper is not None:
                self.__dualGunHelper.reset()
            if self.vehicle.typeDescriptor.hasSiegeMode:
                siegeState = self.vehicle.siegeState
                siegeModeParams = self.vehicle.typeDescriptor.type.siegeModeParams
                if siegeState == VEHICLE_SIEGE_STATE.ENABLED:
                    switchingTime = siegeModeParams.get('switchOffTime', 0.0)
                elif siegeState == VEHICLE_SIEGE_STATE.DISABLED:
                    switchingTime = siegeModeParams.get('switchOnTime', 0.0)
                else:
                    switchingTime = self.vehicle.getSiegeSwitchTimeLeft()
                self.updateSiegeStateStatus(self.vehicle.id, siegeState, switchingTime)
            self.guiSessionProvider.shared.viewPoints.updateAttachedVehicle(self.vehicle.id)
            ctrl = self.guiSessionProvider.dynamic.vehicleCount
            if ctrl is not None:
                ctrl.updateAttachedVehicle(self.vehicle.id)
            self.__aimingBooster = None
        return

    def onSpaceLoaded(self):
        _logger.info('[INIT_STEPS] Avatar.onSpaceLoaded')
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
        ext = cPickle.loads(ext)
        callback = self.__onCmdResponse.pop(requestID, None)
        if callback is not None:
            callback(requestID, resultID, errorStr, ext)
        elif constants.IS_DEVELOPMENT and isinstance(ext, dict):
            exceptionInCallback = ext.get('exception_message', None)
            if exceptionInCallback:
                raise SoftException(exceptionInCallback)
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
                if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and constants.HAS_DEV_RESOURCES:
                    if key == Keys.KEY_ESCAPE:
                        gui_event_dispatcher.toggleGUIVisibility()
                        return True
                    if key == Keys.KEY_1:
                        self.base.setDevelopmentFeature(0, 'heal', 0, '')
                        return True
                    if key == Keys.KEY_2:
                        self.base.setDevelopmentFeature(0, 'reload_gun', 0, '')
                        return True
                    if key == Keys.KEY_3:
                        self.base.setDevelopmentFeature(0, 'start_fire', 0, '')
                        return True
                    if key == Keys.KEY_4:
                        self.base.setDevelopmentFeature(0, 'explode', 0, '')
                        return True
                    if key == Keys.KEY_5:
                        self.base.setDevelopmentFeature(0, 'break_left_track', 0, '')
                        return True
                    if key == Keys.KEY_6:
                        self.base.setDevelopmentFeature(0, 'break_right_track', 0, '')
                        return True
                    if key == Keys.KEY_7:
                        self.base.setDevelopmentFeature(0, 'destroy_self', 0, '')
                        return True
                    if key == Keys.KEY_8:
                        self.base.setDevelopmentFeature(0, 'kill_engine', 0, '')
                        return True
                    if key == Keys.KEY_9:
                        self.base.setDevelopmentFeature(0, 'damage_device', 500, 'ammoBayHealth')
                        return True
                    if key == Keys.KEY_0:
                        self.base.setDevelopmentFeature(0, 'damage_device', 500, 'fuelTankHealth')
                        return True
                    if key == Keys.KEY_MINUS:
                        self.base.setDevelopmentFeature(0, 'damage_device', 500, 'engineHealth')
                        return True
                    if key == Keys.KEY_F12:
                        gui_event_dispatcher.togglePiercingDebugPanel()
                        return True
                    if key == Keys.KEY_F9:
                        self.__makeScreenShot()
                        return True
                    if key == Keys.KEY_F:
                        vehicle = BigWorld.entity(self.playerVehicleID)
                        vehicle.filter.enableClientFilters = not vehicle.filter.enableClientFilters
                        return True
                    if key == Keys.KEY_G:
                        self.moveVehicle(1, True)
                        return True
                    if key == Keys.KEY_R:
                        if mods == 0:
                            self.base.setDevelopmentFeature(0, 'pickup', 0, 'straight')
                        elif mods == 1:
                            if CGF.hotReload(self.spaceID, None):
                                self.base.setDevelopmentFeature(0, 'hot_reload', 0, '')
                        return True
                    if key == Keys.KEY_T:
                        self.base.setDevelopmentFeature(0, 'log_tkill_ratings', 0, '')
                        return True
                    if key == Keys.KEY_N:
                        self.isTeleport = not self.isTeleport
                        return True
                    if key == Keys.KEY_K:
                        self.base.setDevelopmentFeature(0, 'respawn_vehicle', 0, '')
                        return True
                    if key == Keys.KEY_O:
                        self.base.setDevelopmentFeature(0, 'pickup', 0, 'roll')
                        return True
                    if key == Keys.KEY_P:
                        self.base.setDevelopmentFeature(0, 'captureClosestBase', 0, '')
                        return True
                    if key == Keys.KEY_Q:
                        self.base.setDevelopmentFeature(0, 'teleportToShotPoint', 0, '')
                        return True
                    if key == Keys.KEY_V:
                        self.base.setDevelopmentFeature(0, 'setSignal', 3, '')
                        return True
                    if key == Keys.KEY_C:
                        self.base.setDevelopmentFeature(0, 'navigateTo', 0, cPickle.dumps((tuple(self.inputHandler.getDesiredShotPoint()), None, None), -1))
                        return True
                    if key == Keys.KEY_PAUSE:
                        self.base.setDevelopmentFeature(0, 'togglePauseAI', 0, '')
                        return True
                    if key == Keys.KEY_Y:
                        ctrl = self.guiSessionProvider.shared.areaMarker
                        if ctrl:
                            matrix = Math.Matrix(self.vehicle.matrix)
                            ctrl.addMarker(ctrl.createMarker(matrix, 0))
                        return True
                    if key == Keys.KEY_U:
                        ctrl = self.guiSessionProvider.shared.areaMarker
                        if ctrl:
                            ctrl.removeAllMarkers()
                        return True
                    if key == Keys.KEY_H:
                        ctrl = self.guiSessionProvider.shared.areaMarker
                        if ctrl:
                            vehicle = BigWorld.entity(self.playerVehicleID)
                            ctrl.addMarker(ctrl.createMarker(vehicle.matrix, 0))
                        return True
                    if key == Keys.KEY_BACKSLASH:
                        self.base.setDevelopmentFeature(0, 'killEnemyTeam', 0, '')
                        return True
                    if key == Keys.KEY_J:
                        self.base.setDevelopmentFeature(0, 'stun', 0, '')
                        return True
                if constants.HAS_DEV_RESOURCES and cmdMap.isFired(CommandMapping.CMD_SWITCH_SERVER_MARKER, key) and isDown:
                    self.gunRotator.showServerMarker = not self.gunRotator.showServerMarker
                    return True
                isGuiEnabled = self.isForcedGuiControlMode()
                if cmdMap.isFired(CommandMapping.CMD_TOGGLE_GUI, key) and isDown and self.__couldToggleGUIVisibility():
                    gui_event_dispatcher.toggleGUIVisibility()
                if constants.HAS_DEV_RESOURCES and isDown:
                    if key == Keys.KEY_I and mods == 0:
                        import Cat
                        if Cat.Tasks.ScreenInfo.ScreenInfoObject.getVisible():
                            Cat.Tasks.ScreenInfo.ScreenInfoObject.setVisible(False)
                        else:
                            Cat.Tasks.ScreenInfo.ScreenInfoObject.setVisible(True)
                        return True
                if cmdMap.isFired(CommandMapping.CMD_INCREMENT_CRUISE_MODE, key) and isDown and self.__isVehicleAlive:
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
                if cmdMap.isFired(CommandMapping.CMD_DECREMENT_CRUISE_MODE, key) and isDown and self.__isVehicleAlive:
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
                if cmdMap.isFiredList((CommandMapping.CMD_MOVE_FORWARD, CommandMapping.CMD_MOVE_FORWARD_SPEC, CommandMapping.CMD_MOVE_BACKWARD), key) and isDown:
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
                    movementCommands = self.makeVehicleMovementCommandByKeys()
                    self.moveVehicle(movementCommands, isDown, cmdMap.isActive(CommandMapping.CMD_BLOCK_TRACKS))
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_MOVE, moveCommands=movementCommands)
                    return True
                isEpicBattle = self.arenaBonusType in [constants.ARENA_BONUS_TYPE.EPIC_BATTLE, constants.ARENA_BONUS_TYPE.EPIC_BATTLE_TRAINING]
                isBR = ARENA_BONUS_TYPE_CAPS.checkAny(self.arenaBonusType, ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
                if cmdMap.isFired(CommandMapping.CMD_QUEST_PROGRESS_SHOW, key) and not isBR and not isEpicBattle and (mods != 2 or not isDown) and self.lobbyContext.getServerSettings().isPersonalMissionsEnabled():
                    gui_event_dispatcher.toggleFullStatsQuestProgress(isDown)
                    return True
                supportsBoosters = ARENA_BONUS_TYPE_CAPS.checkAny(self.arenaBonusType, ARENA_BONUS_TYPE_CAPS.BOOSTERS)
                if cmdMap.isFired(CommandMapping.CMD_SHOW_PERSONAL_RESERVES, key) and not isEpicBattle and not BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and supportsBoosters and self.lobbyContext.getServerSettings().personalReservesConfig.isReservesInBattleActivationEnabled:
                    gui_event_dispatcher.toggleFullStatsPersonalReserves(isDown)
                    return True
                if not isGuiEnabled and isDown and mods == 0:
                    if keys_handlers.processAmmoSelection(key):
                        return True
                    if cmdMap.isFiredList(xrange(CommandMapping.CMD_AMMO_CHOICE_4, CommandMapping.CMD_AMMO_CHOICE_0 + 1), key):
                        gui_event_dispatcher.choiceConsumable(key)
                        return True
                isComp7 = ARENA_BONUS_TYPE_CAPS.checkAny(self.arenaBonusType, ARENA_BONUS_TYPE_CAPS.COMP7)
                if not isComp7 and cmdMap.isFired(CommandMapping.CMD_VOICECHAT_ENABLE, key) and not isDown:
                    if self.__isPlayerInSquad() and not BattleReplay.isPlaying():
                        if VOIP.getVOIPManager().isVoiceSupported():
                            gui_event_dispatcher.toggleVoipChannelEnabled(self.arenaBonusType)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_VEHICLE_MARKERS_SHOW_INFO, key):
                    gui_event_dispatcher.showExtendedInfo(isDown)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_SHOW_HELP, key) and isDown and mods == 0:
                    if g_bootcamp.isRunning() or not self.sessionProvider.shared.ingameHelp.canShow():
                        return True
                    return self.sessionProvider.shared.ingameHelp.showIngameHelp(self.getVehicleAttached())
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
                if not isGuiEnabled and self.guiSessionProvider.shared.drrScale is not None and self.guiSessionProvider.shared.drrScale.handleKey(key, isDown):
                    return True
                if cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP, CommandMapping.CMD_MINIMAP_VISIBLE), key) and isDown:
                    gui_event_dispatcher.setMinimapCmd(key)
                    return True
                if cmdMap.isFired(CommandMapping.CMD_RELOAD_PARTIAL_CLIP, key) and isDown:
                    self.guiSessionProvider.shared.ammo.reloadPartialClip(self)
                    return True
                if key == Keys.KEY_ESCAPE and isDown and mods == 0 and self.guiSessionProvider.shared.equipments.cancel():
                    return True
                if self.appLoader.handleKey(app_settings.APP_NAME_SPACE.SF_BATTLE, isDown, key, mods):
                    return True
                for comp in AVATAR_COMPONENTS:
                    hasHandledKey = comp.handleKey(self, isDown, key, mods)
                    if hasHandledKey:
                        return True

            except Exception:
                LOG_CURRENT_EXCEPTION()
                return True

            return False

    def __couldToggleGUIVisibility(self):
        app = self.appLoader.getApp()
        if app is None:
            return False
        else:
            return not app.hasGuiControlModeConsumers(BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL_FILTER_POPOVER) if self.arenaGuiType == constants.ARENA_GUI_TYPE.COMP7 and self.arena.period <= ARENA_PERIOD.PREBATTLE else not self.isForcedGuiControlMode()

    def set_playerVehicleID(self, *args):
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

    def set_isGunLocked(self, *args):
        if not self.userSeesWorld():
            return
        else:
            if not self.isObserver() and self.gunRotator is not None:
                if self.isGunLocked:
                    self.gunRotator.lock(True)
                    if not isinstance(self.inputHandler.ctrl, (VideoCameraControlMode,
                     ArcadeControlMode,
                     PostMortemControlMode,
                     DeathFreeCamMode,
                     RespawnDeathMode)):
                        self.inputHandler.setAimingMode(False, AIMING_MODE.USER_DISABLED)
                        self.inputHandler.onControlModeChanged('arcade', preferredPos=self.inputHandler.getDesiredShotPoint())
                        self.guiSessionProvider.shared.equipments.cancel()
                else:
                    self.gunRotator.lock(False)
            return

    def set_ownVehicleGear(self, *args):
        pass

    def set_observableTeamID(self, prev):
        self.__isObserver = self.observableTeamID > 0

    def set_ownVehicleAuxPhysicsData(self, prev=None):
        self.__onSetOwnVehicleAuxPhysicsData(prev)

    def targetBlur(self, prevEntity):
        if not prevEntity:
            return
        else:
            isVehicle = prevEntity.__class__.__name__ == 'Vehicle'
            entityInFocusType = ENTITY_IN_FOCUS_TYPE.VEHICLE if isVehicle else ENTITY_IN_FOCUS_TYPE.DESTRUCTIBLE_ENTITY
            self.guiSessionProvider.shared.feedback.setTargetInFocus(0, False, entityInFocusType)
            prevEntity.removeEdge()
            self.target = None
            TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AIM_AT_VEHICLE)
            if isVehicle and self.__maySeeOtherVehicleDamagedDevices:
                self.cell.monitorVehicleDamagedDevices(0)
                self.guiSessionProvider.shared.feedback.hideVehicleDamagedDevices()
            return

    def targetFocus(self, entity):
        if not entity:
            return
        self.target = entity
        isVehicle = entity.__class__.__name__ == 'Vehicle'
        if self.inputHandler.isGuiVisible and entity.isAlive():
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.AIM_AT_VEHICLE, vehicleId=entity.id)
            entity.drawEdge()
            if isVehicle and self.__maySeeOtherVehicleDamagedDevices:
                self.cell.monitorVehicleDamagedDevices(entity.id)
        entityInFocusType = ENTITY_IN_FOCUS_TYPE.VEHICLE if isVehicle else ENTITY_IN_FOCUS_TYPE.DESTRUCTIBLE_ENTITY
        self.guiSessionProvider.shared.feedback.setTargetInFocus(entity.id, True, entityInFocusType)

    def reload(self):
        self.__reloadGUI()

    def vehicle_onAppearanceReady(self, vehicle):
        LOG_DEBUG('Avatar.vehicle_onAppearanceReady')
        self.__vehicles.add(vehicle)
        AvatarObserver.vehicle_onAppearanceReady(self, vehicle)
        if vehicle.id != self.playerVehicleID:
            vehicle.targetCaps = [1]
        else:
            LOG_DEBUG('[INIT_STEPS] Avatar.vehicle_onAppearanceReady', vehicle.id)
            vehicle.isPlayerVehicle = True
            if not self.__initProgress & _INIT_STEPS.VEHICLE_ENTERED:
                self.vehicleTypeDescriptor = vehicle.typeDescriptor
                if vehicle.typeDescriptor.turret.ceilless is not None:
                    WWISE.WW_setRTCPGlobal('ceilless', 1 if vehicle.typeDescriptor.turret.ceilless else 0)
                else:
                    WWISE.WW_setRTCPGlobal('ceilless', 0)
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    m = vehicle.filter.bodyMatrix
                    tm = vehicle.filter.turretMatrix
                    self.__ownVehicleTurretMProv.setStaticTransform(Math.Matrix(tm))
                else:
                    m = vehicle.matrix
                    if vehicle.appearance:
                        tm = vehicle.appearance.turretMatrix
                        self.__ownVehicleTurretMProv.setStaticTransform(Math.Matrix(tm))
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

    def __makeScreenShot(self, fileType='jpg', fileMask='./../screenshots/'):
        BigWorld.screenShot(fileType, fileMask)

    def enemySPGHit(self, hitPoint):
        self.guiSessionProvider.shared.feedback.setEnemySPGHit(hitPoint)

    def enemySPGShotSound(self, shooterPosition, targetPosition):
        self.complexSoundNotifications.notifyEnemySPGShotSound((self.getOwnVehiclePosition() - targetPosition).length, shooterPosition)

    def __waitVehilceInfoForStartVisual(self, vehicle, resetControllers):
        if vehicle.id in self.arena.vehicles:
            if vehicle.id in self.__vehiclesWaitedInfo:
                del self.__vehiclesWaitedInfo[vehicle.id]
            return False
        self.__vehiclesWaitedInfo[vehicle.id] = (weakref.proxy(vehicle), resetControllers)
        return True

    def __onVehicleInfoAddedForStartVisual(self, vehID):
        if vehID in self.__vehiclesWaitedInfo:
            params = self.__vehiclesWaitedInfo.pop(vehID)
            self.__startVehicleVisual(*params)

    def __startVehicleVisual(self, vehicle, resetControllers=False):
        if self.__waitVehilceInfoForStartVisual(vehicle, resetControllers):
            return
        else:
            vehicle.startVisual()
            if vehicle.isHidden:
                vehicle.startGUIVisual()
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
                    self.clearObservedVehicleID()
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
            if vehicle.isHidden:
                vehicle.stopGUIVisual()
            return
        else:
            try:
                self.onVehicleLeaveWorld(vehicle)
                if self.playerVehicleID == vehicle.id:
                    g_playerEvents.onAvatarVehicleLeaveWorld()
                self.__vehicles.remove(vehicle)
                vehicle.stopVisual()
            except:
                LOG_CURRENT_EXCEPTION()
                raise VehicleDeinitFailureException()

            vehicle.model = None
            return

    def __onSetOwnVehicleAuxPhysicsData(self, prev):
        vehicle = BigWorld.entity(self.playerVehicleID)
        if vehicle and vehicle.id and vehicle.isStarted:
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

    def onKickedFromServer(self, reason, kickReasonType, expiryTime):
        LOG_DEBUG('onKickedFromServer', reason, kickReasonType, expiryTime)
        self.statsCollector.reset()
        if not BattleReplay.isPlaying():
            self.connectionMgr.setKickedFromServer(reason, kickReasonType, expiryTime)

    def setUpdatedGoodiesSnapshot(self, updatedSnapshot):
        self.goodiesSnapshot = updatedSnapshot
        self.onGoodiesSnapshotUpdated()

    def onSwitchViewpoint(self, vehicleID, position):
        LOG_DEBUG('onSwitchViewpoint', vehicleID, position)
        self.onSwitchingViewPoint()
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
        if autoAimVehID:
            self.onLockTarget(AimSound.TARGET_LOST, not lossReasonFlags & TARGET_LOST_FLAGS.KILLED_BY_ME)
        TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE)

    def updateVehicleHealth(self, vehicleID, health, deathReasonID, isCrewActive, isRespawn):
        if vehicleID != self.playerVehicleID or not self.userSeesWorld():
            return
        else:
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
                self.guiSessionProvider.movingToRespawnBase(BigWorld.entities.get(self.playerVehicleID))
                self.inputHandler.movingToRespawnBase()
                if self.vehicle:
                    self.vehicle.ownVehicle.initialUpdate(force=True)
            if not isAlive and wasAlive:
                if self.gunRotator:
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
                    ctrl = self.guiSessionProvider.dynamic.vehicleCount
                    if ctrl is not None:
                        ctrl.updateAttachedVehicle(self.vehicle.id)
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
                vehicle = BigWorld.entities.get(self.playerVehicleID)
                noRespawnPossible = not (self.respawnEnabled or bool(vehicle.enableExternalRespawn))
                self.guiSessionProvider.switchToPostmortem(noRespawnPossible, isRespawn)
            return

    def updateVehicleGunReloadTime(self, vehicleID, timeLeft, baseTime):
        if vehicleID != self.playerVehicleID and vehicleID != self.observedVehicleID:
            if not self.__isVehicleAlive and vehicleID == self.inputHandler.ctrl.curVehicleID:
                self.guiSessionProvider.shared.feedback.setVehicleHasAmmo(vehicleID, timeLeft != -2)
            return
        if timeLeft == baseTime:
            self.__gunReloadCommandWaitEndTime = 0.0
        self.__prevGunReloadTimeLeft = timeLeft
        ammoCtrl = self.guiSessionProvider.shared.ammo
        gunSettings = ammoCtrl.getGunSettings()
        shellsLeft = ammoCtrl.getShellsQuantityLeft()
        burstSize = gunSettings.burst.size if gunSettings.isBurstAndClip() else 0
        if (shellsLeft <= 1 or burstSize > 0 and shellsLeft == burstSize) and timeLeft <= 0.0:
            shellsLayout = ammoCtrl.getOrderedShellsLayout()
            allShells = 0
            for layout in shellsLayout:
                allShells += layout[2]

            if allShells == 1 or burstSize > 0 and allShells == burstSize:
                baseTime = -1
        if timeLeft < 0.0:
            timeLeft = -1
        self.guiSessionProvider.shared.ammo.setGunReloadTime(timeLeft, baseTime)

    def updateVehicleClipReloadTime(self, vehicleID, timeLeft, baseTime, firstTime, stunned, isBoostApplicable):
        self.guiSessionProvider.shared.ammo.setGunAutoReloadTime(timeLeft, baseTime, firstTime, stunned, isBoostApplicable)

    def updateDualGunState(self, vehicleID, activeGun, gunStates, cooldownTimes):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is not None and vehicle.typeDescriptor is not None and vehicle.typeDescriptor.isDualgunVehicle and vehicle.isStarted:
            vehicle.onActiveGunChanged(activeGun, cooldownTimes[DUAL_GUN.COOLDOWNS.SWITCH])
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DUAL_GUN_STATE_UPDATED, (activeGun, cooldownTimes, gunStates))
        elif self.isObserver():
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DUAL_GUN_STATE_UPDATED, (activeGun, cooldownTimes, gunStates))
        if self.__dualGunHelper is not None:
            self.__dualGunHelper.updateGunReloadTime(self, vehicleID, activeGun, gunStates, cooldownTimes, self.guiSessionProvider.shared.ammo)
        self.__canMakeDualShot = all((state == DUAL_GUN.GUN_STATE.READY for state in gunStates))
        self.guiSessionProvider.shared.ammo.setDualGunQuickChangeReady(self.__canMakeDualShot)
        LOG_DEBUG_DEV('updateDualGunState', vehicleID, activeGun, gunStates, cooldownTimes)
        return

    def stopSetupSelection(self):
        self.guiSessionProvider.shared.prebattleSetups.stopSelection()

    def beforeSetupUpdate(self, vehicleID):
        vehicleDescriptor = self.__getDetailedVehicleDescriptor()
        self.guiSessionProvider.shared.prebattleSetups.stopSelection()
        self.guiSessionProvider.shared.ammo.clear(leave=False)
        self.guiSessionProvider.shared.equipments.clear(leave=False)
        self.guiSessionProvider.shared.optionalDevices.reset()
        self.guiSessionProvider.shared.ammo.setGunSettings(vehicleDescriptor.gun)
        self.guiSessionProvider.shared.equipments.notifyPlayerVehicleSet(vehicleID)
        self.__aimingBooster = None
        return

    def updateVehicleAmmo(self, vehicleID, compactDescr, quantity, quantityInClipOrNextStage, previousStage, timeRemaining, totalTime, index=None):
        LOG_DEBUG_DEV('updateVehicleAmmo vehicleID={}, compactDescr={}'.format(vehicleID, compactDescr))
        if not compactDescr:
            itemTypeIdx = ITEM_TYPE_INDICES['equipment']
        else:
            itemTypeIdx = getTypeOfCompactDescr(compactDescr)
        processor = self.__updateConsumablesProcessors.get(itemTypeIdx)
        if processor:
            if itemTypeIdx == ITEM_TYPE_INDICES['equipment'] and self.arena.period == ARENA_PERIOD.BATTLE:
                self.guiSessionProvider.shared.equipments.setServerPrevStage(previousStage, compactDescr)
            getattr(self, processor)(vehicleID, compactDescr, quantity, quantityInClipOrNextStage, timeRemaining, totalTime)
        else:
            LOG_WARNING('Not supported item type index', itemTypeIdx)

    __updateConsumablesProcessors = {ITEM_TYPE_INDICES['shell']: '_PlayerAvatar__processVehicleAmmo',
     ITEM_TYPE_INDICES['equipment']: '_PlayerAvatar__processVehicleEquipments'}

    def resetVehicleAmmo(self, oldCompactDescr, newCompactDescr, quantity, stage, timeRemaining, totalTime):
        LOG_DEBUG_DEV('resetVehicleAmmo oldCompactDescr={}, newCompactDescr={}'.format(oldCompactDescr, newCompactDescr))
        self.guiSessionProvider.shared.equipments.resetEquipment(oldCompactDescr, newCompactDescr, quantity, stage, timeRemaining, totalTime)
        CommandMapping.g_instance.onMappingChanged()

    def updateVehicleOptionalDeviceStatus(self, vehicleID, deviceID, isOn):
        currentVehicle = self.getVehicleAttached()
        if currentVehicle is not None and vehicleID == currentVehicle.id:
            self.guiSessionProvider.shared.optionalDevices.setOptionalDevice(deviceID, isOn)
        return

    def __updateVehicleStatus(self, vehicleID):
        observedVehID = self.guiSessionProvider.shared.vehicleState.getControllingVehicleID()
        if vehicleID != self.playerVehicleID and vehicleID != observedVehID and (self.__isVehicleAlive or vehicleID != self.inputHandler.ctrl.curVehicleID):
            return False
        else:
            typeDescr = None
            if self.isObserver() or observedVehID == vehicleID:
                observedVehicleData = self.arena.vehicles.get(observedVehID)
                if observedVehicleData:
                    typeDescr = observedVehicleData['vehicleType']
                else:
                    LOG_DEBUG_DEV('[updateVehicleStatus] Vehicle #{} is not in arena vehicles'.format(observedVehID))
                    return False
            return typeDescr

    def updateIsOtherVehicleDamagedDevicesVisible(self, vehicleID, status):
        if not self.__updateVehicleStatus(vehicleID):
            return
        else:
            prevVal = self.__maySeeOtherVehicleDamagedDevices
            newVal = status
            self.__maySeeOtherVehicleDamagedDevices = status
            if not prevVal and newVal:
                target = BigWorld.target()
                if target is not None and isinstance(target, Vehicle.Vehicle):
                    self.cell.monitorVehicleDamagedDevices(target.id)
            return

    def __getLeftTime(self, endTime):
        return max(endTime - BigWorld.serverTime(), 0) if endTime > 0 else endTime

    def updateSiegeStateStatus(self, vehicleID, status, timeLeft):
        typeDescr = self.__updateVehicleStatus(vehicleID)
        if not typeDescr:
            return
        if status in (constants.VEHICLE_SIEGE_STATE.SWITCHING_ON, constants.VEHICLE_SIEGE_STATE.SWITCHING_OFF):
            if 'autoSiege' not in typeDescr.type.tags:
                self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
            self.__updateCruiseControlPanel()
            self.moveVehicleByCurrentKeys(False)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.SIEGE_MODE, (status, timeLeft))
        self.__onSiegeStateUpdated(vehicleID, status, timeLeft)

    def updateDestroyedDevicesIsRepairing(self, vehicleID, extraIndex, progress, timeLeft, repairMode):
        typeDescr = self.__updateVehicleStatus(vehicleID)
        if not typeDescr:
            return
        extraIndex = extraIndex
        progress = progress
        LOG_DEBUG_DEV('DESTROYED_DEVICE_IS_REPAIRING (%s): %s%%, %s sec' % (typeDescr.extras[extraIndex].name, progress, timeLeft))
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.REPAIRING, (typeDescr.extras[extraIndex].name[:-len('Health')],
         progress,
         timeLeft,
         repairMode))

    def updateDualGunStatus(self, vehicleID, status, times):
        if not self.__updateVehicleStatus(vehicleID):
            return
        else:
            LOG_DEBUG_DEV('Charger updated ( {}, {} )'.format(status, times))
            dualGunControl = self.inputHandler.dualGunControl
            if dualGunControl is not None:
                dualGunControl.updateChargeState(status, times)
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DUAL_GUN_CHARGER, (status, times))
            if status == DUALGUN_CHARGER_STATUS.PREPARING:
                _, timeLeft = times
                self.__startWaitingForCharge(timeLeft)
            elif status in (DUALGUN_CHARGER_STATUS.CANCELED, DUALGUN_CHARGER_STATUS.UNAVAILABLE):
                self.__cancelWaitingForCharge()
            elif status == DUALGUN_CHARGER_STATUS.APPLIED:
                self.__dropStopUntilFireMode()
            return

    def updateBurnoutUnavailable(self, vehicleID, status):
        if not self.__updateVehicleStatus(vehicleID):
            return
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BURNOUT_UNAVAILABLE_DUE_TO_BROKEN_ENGINE, status)

    def updateBurnoutWarning(self, vehicleID, status):
        if not self.__updateVehicleStatus(vehicleID):
            return
        else:
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BURNOUT_WARNING, status)
            if status > 0:
                SoundGroups.g_instance.playSound2D('eng_damage_risk')
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is not None:
                vehicle.appearance.onEngineDamageRisk(status > 0)
            return

    def updateDrownLevel(self, vehicleID, level, times):
        if not self.__updateVehicleStatus(vehicleID):
            return
        else:
            self.__isVehicleDrowning = constants.DROWN_WARNING_LEVEL.isDrowning(level)
            self.updateVehicleDestroyTimer(VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING, times, level)
            ctrl = self.guiSessionProvider.dynamic.progression
            if ctrl is not None:
                ctrl.onVehicleStatusChanged()
            return

    def updateOverturnLevel(self, vehicleID, level, times):
        if not self.__updateVehicleStatus(vehicleID):
            return
        else:
            self.__isVehicleOverturned = constants.OVERTURN_WARNING_LEVEL.isOverturned(level)
            self.updateVehicleDestroyTimer(VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED, times, level)
            ctrl = self.guiSessionProvider.dynamic.progression
            if ctrl is not None:
                ctrl.onVehicleStatusChanged()
            return

    def updateVehicleSettings(self, vehicleSettings):
        for vehicleSetting in vehicleSettings:
            self.updateVehicleSetting(vehicleSetting.vehicleID, vehicleSetting.code, vehicleSetting.value)

    def updateVehicleSetting(self, vehicleID, code, value):
        self.__updateVehicleSetting(vehicleID, code, value)

    def predictVehicleSetting(self, vehicleID, code, value):
        self.__updateVehicleSetting(vehicleID, code, value, fromServer=False)

    def updateTargetingInfo(self, entityId, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed, shotDispMultiplierFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime):
        LOG_DEBUG_DEV('updateTargetingInfo', entityId, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed, shotDispMultiplierFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime)
        if entityId != self.playerVehicleID and entityId != self.observedVehicleID:
            return
        dispersionInfo = self.__dispersionInfo
        dispersionInfo[0] = shotDispMultiplierFactor
        dispersionInfo[1] = gunShotDispersionFactorsTurretRotation
        dispersionInfo[2] = chassisShotDispersionFactorsMovement
        dispersionInfo[3] = chassisShotDispersionFactorsRotation
        dispersionInfo[4] = aimingTime
        if self.gunRotator:
            self.gunRotator.update(turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed)
            self.getOwnVehicleShotDispersionAngle(self.gunRotator.turretRotationSpeed)

    def redrawVehicleOnRespawn(self, vehicleID, newVehCompactDescr, newVehOutfitCompactDescr):
        ownVehicle = vehicleID == self.playerVehicleID
        if ownVehicle and self.__firstHealthUpdate:
            self.__deadOnLoading = True
        Vehicle.Vehicle.respawnVehicle(vehicleID, newVehCompactDescr, newVehOutfitCompactDescr)
        if ownVehicle:
            self.__consistentMatrices.notifyVehicleChanged(self, updateStopped=True)

    def updateGunMarker(self, vehicleID, shotPos, shotVec, dispersionAngle):
        if self.gunRotator:
            self.gunRotator.setShotPosition(vehicleID, shotPos, shotVec, dispersionAngle)

    def updateTargetVehicleID(self, targetID):
        gui_event_dispatcher.changeTargetVehicle(targetID)

    def updateVehicleDestroyTimer(self, code, period, warnLvl=None):
        state = VEHICLE_VIEW_STATE.DESTROY_TIMER
        value = DestroyTimerViewState.makeCloseTimerState(code)
        if warnLvl is None:
            if period[1] > 0:
                value = DestroyTimerViewState(code, period[0], TIMER_VIEW_STATE.CRITICAL, period[0])
        elif warnLvl == DROWN_WARNING_LEVEL.DANGER:
            value = DestroyTimerViewState(code, period[1], TIMER_VIEW_STATE.CRITICAL, period[0])
        elif warnLvl == DROWN_WARNING_LEVEL.CAUTION:
            value = DestroyTimerViewState(code, period[1], TIMER_VIEW_STATE.WARNING, period[0])
        self.guiSessionProvider.invalidateVehicleState(state, value)
        return

    def updateVehicleDeathZoneTimer(self, time, zoneID, entered=True, finishTime=None, isCausingDamage=False, state=TIMER_VIEW_STATE.CRITICAL):
        timer = VEHICLE_VIEW_STATE.DEATHZONE_TIMER
        value = DeathZoneTimerViewState.makeCloseTimerState(zoneID, isCausingDamage)
        if time > 0 or state == TIMER_VIEW_STATE.WARNING:
            value = DeathZoneTimerViewState(zoneID, isCausingDamage, time, state, finishTime, entered)
        self.guiSessionProvider.invalidateVehicleState(timer, value)

    def updatePersonalDeathZoneWarningNotification(self, enable, time):
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.PERSONAL_DEATHZONE, (enable, time))

    def updateDeathZoneWarningNotification(self, enable, playerEntering, strikeTime, waveDuration):
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEATHZONE, (enable,
         playerEntering,
         strikeTime,
         waveDuration))

    def showOwnVehicleHitDirection(self, hitDirYaw, attackerID, damage, crits, isBlocked, isShellHE, damagedID, attackReasonID):
        if not self.__isVehicleAlive and not self.isObserver():
            return
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        if self.isObserver() and BigWorld.player().getVehicleAttached().id == attackerID:
            return
        LOG_DEBUG_DEV('showOwnVehicleHitDirection: hitDirYaw={}, attackerID={}, damage={}, crits={}isBlocked={}, isHighExplosive={}, damagedID={}, attackReasonID={}'.format(hitDirYaw, attackerID, damage, crits, isBlocked, isShellHE, damagedID, attackReasonID))
        self.guiSessionProvider.addHitDirection(hitDirYaw, attackerID, damage, isBlocked, crits, isShellHE, damagedID, attackReasonID)

    def showVehicleDamageInfo(self, vehicleID, damageIndex, extraIndex, entityID, equipmentID, ignoreMessages=False):
        if not self.userSeesWorld():
            return
        else:
            damageCode = constants.DAMAGE_INFO_CODES[damageIndex]
            LOG_DEBUG_DEV('[showVehicleDamageInfo] Vehicle', vehicleID, damageCode, damageIndex, extraIndex, entityID, equipmentID)
            typeDescr = self.vehicleTypeDescriptor
            observedVehID = self.guiSessionProvider.shared.vehicleState.getControllingVehicleID()
            if self.isObserver() or observedVehID == vehicleID:
                observedVehicleData = self.arena.vehicles.get(observedVehID)
                if observedVehicleData:
                    typeDescr = observedVehicleData['vehicleType']
                else:
                    LOG_DEBUG_DEV('[showVehicleDamageInfo] Vehicle #{} is not in arena vehicles'.format(observedVehID))
                    return
            extra = typeDescr.extras[extraIndex] if extraIndex != 0 else None
            if vehicleID == self.playerVehicleID or vehicleID == observedVehID or not self.__isVehicleAlive and vehicleID == self.inputHandler.ctrl.curVehicleID:
                self.__showDamageIconAndPlaySound(damageCode, extra, vehicleID, ignoreMessages)
            if damageCode not in self.__damageInfoNoNotification:
                self.guiSessionProvider.shared.messages.showVehicleDamageInfo(self, damageCode, vehicleID, entityID, extra, equipmentID, ignoreMessages)
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
                    if flags & (VHF.ARMOR_WITH_ZERO_DF_NOT_PIERCED_BY_PROJECTILE | VHF.DEVICE_NOT_PIERCED_BY_PROJECTILE) or not flags & VHF.IS_ANY_PIERCING_MASK:
                        sound = 'enemy_no_piercing_by_player'
                    else:
                        sound = 'enemy_no_hp_damage_at_no_attempt_by_player'
                    if len(enemies) == 1:
                        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED, targetId=enemyVehID)
                if sound is not None:
                    bestSound = getBestShotResultSound(bestSound, sound, enemyVehID)

            if bestSound is not None:

                def checkFn(vehID):
                    if self.arena:
                        vehicleInfo = self.arena.vehicles.get(vehID)
                        return vehicleInfo and vehicleInfo['isAlive']
                    return False

                self.soundNotifications.play(bestSound[0], checkFn=partial(checkFn, bestSound[1]), boundVehicleID=bestSound[1])
                for burnEnemyVehID in burningEnemies:
                    self.soundNotifications.play('enemy_fire_started_by_player', checkFn=partial(checkFn, burnEnemyVehID), boundVehicleID=burnEnemyVehID)

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
        if code == 100:
            return self.arena.loadVsePlans()
        else:
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
                        allKeys = set(params['finalAttrs'].keys())
                        allKeys |= set(params['factors'].keys())
                        boardConfig = [ (key, key) for key in allKeys ]
                        board.refreshConfig(boardConfig)
                        board.setUpdater(lambda x: ' / '.join([str(params['finalAttrs'].get(x)), str(params['factors'].get(x)), str(params['miscAttrs'].get(x))]))
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

    def syncVehicleAttrs(self, _, attrs):
        LOG_DEBUG('syncVehicleAttrs', attrs)
        if self.guiSessionProvider.shared.prebattleSetups.isSelectionStarted():
            self.guiSessionProvider.shared.prebattleSetups.setVehicleAttrs(self.playerVehicleID, attrs)
        else:
            self.guiSessionProvider.shared.feedback.setVehicleAttrs(self.playerVehicleID, attrs)

    def showTracer(self, shooterID, shotID, isRicochet, effectsIndex, refStartPoint, velocity, gravity, maxShotDist, gunIndex):
        if not self.userSeesWorld() or self.__projectileMover is None:
            return
        else:
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            startPoint = refStartPoint
            shooter = BigWorld.entity(shooterID)
            if not isRicochet and shooter is not None and shooter.isStarted and effectsDescr.get('artilleryID') is None:
                multiGun = shooter.typeDescriptor.turret.multiGun
                nodeName = multiGun[gunIndex].gunFire if shooter.typeDescriptor.isDualgunVehicle and multiGun is not None else 'HP_gunFire'
                node = shooter.appearance.compoundModel.node(nodeName)
                if not node:
                    return
                gunMatrix = Math.Matrix(node)
                gunFirePos = gunMatrix.translation
                if cameras.isPointOnScreen(gunFirePos):
                    startPoint = gunFirePos
                    replayCtrl = BattleReplay.g_replayCtrl
                    if (gunFirePos - refStartPoint).length > 50.0 > (gunFirePos - BigWorld.camera().position).length and replayCtrl.isPlaying:
                        velocity = velocity.length * gunMatrix.applyVector((0, 0, 1))
            self.__projectileMover.add(shotID, effectsDescr, gravity, refStartPoint, velocity, startPoint, maxShotDist, shooterID, BigWorld.camera().position)
            if isRicochet:
                self.__projectileMover.hold(shotID)
            return

    def stopTracer(self, shotID, endPoint):
        if self.userSeesWorld() and self.__projectileMover is not None:
            self.__projectileMover.hide(shotID, endPoint)
        return

    def projectileMover(self):
        return self.__projectileMover

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

    def onRoundFinished(self, winnerTeam, reason, extraData):
        LOG_DEBUG('onRoundFinished', winnerTeam, reason, extraData)
        g_playerEvents.onRoundFinished(winnerTeam, reason, extraData)

    def onKickedFromArena(self, reasonCode):
        LOG_DEBUG('onKickedFromArena', reasonCode)
        g_playerEvents.onKickedFromArena(reasonCode)
        SystemMessages.pushMessage(messages.getKickReasonMessage(reasonCode), type=SystemMessages.SM_TYPE.Error)

    def onBattleEvents(self, events):
        LOG_DEBUG('Battle events has been received: ', events)
        observedVehID = self.guiSessionProvider.shared.vehicleState.getControllingVehicleID()
        if self.isObserver() or observedVehID == self.playerVehicleID:
            self.guiSessionProvider.shared.feedback.handleBattleEvents(events, self.__getBattleEventsAdditionalData())

    def onObservedByEnemy(self, vehicleID):
        if not self.__updateVehicleStatus(vehicleID):
            return
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY, True)

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

    def updateQuestProgress(self, questID, progressesInfo):
        LOG_DEBUG('[QUEST] Progress:', questID, progressesInfo)
        self.guiSessionProvider.shared.questProgress.updateQuestProgress(questID, progressesInfo)

    def updateVehicleQuickShellChanger(self, vehicleID, isActive):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle and not almostZero(vehicle.quickShellChangerFactor - 1.0) and vehicle.isAlive():
            if isActive and not vehicle.quickShellChangerIsActive and self.soundNotifications:
                self.soundNotifications.play('gun_intuition')
            vehicle.quickShellChangerIsActive = isActive
            self.guiSessionProvider.updateVehicleQuickShellChanger(isActive)

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

    def makeDenunciation(self, violatorID, topicID, violatorKind, _):
        if self.denunciationsLeft <= 0:
            return
        self.denunciationsLeft -= 1
        self.base.makeDenunciation(violatorID, topicID, violatorKind)

    def modifyPlayerRelations(self, targetVehicleID, actionID):
        self._doCmdInt2(AccountCommands.CMD_UPDATE_USER_RELATIONS, targetVehicleID, actionID, None)
        return

    def onRankUpdated(self, newRank):
        self._doCmdInt(AccountCommands.CMD_RANK_UPDATED, newRank, None)
        return

    def banUnbanUser(self, accountDBID, restrType, banPeriod, reason, isBan):
        reason = reason.encode('utf8')
        self.base.banUnbanUser(accountDBID, restrType, banPeriod, reason, isBan)

    def isObserver(self):
        if self.__isObserver is None:
            self.__isObserver = self.guiSessionProvider.getCtx().isObserver(self.playerVehicleID)
        return self.__isObserver

    def setIsObserver(self):
        self.__isObserver = True

    def isVehiclesColorized(self):
        return self.observerSeesAll()

    def isVehicleMoving(self):
        return self.__isVehicleMoving

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
                flags = MOVEMENT_FLAGS.FORWARD
        elif cmdMap.isActive(CommandMapping.CMD_MOVE_BACKWARD):
            flags = MOVEMENT_FLAGS.BACKWARD
        else:
            if self.__cruiseControlMode >= _CRUISE_CONTROL_MODE.FWD25:
                flags = MOVEMENT_FLAGS.FORWARD
            elif self.__cruiseControlMode <= _CRUISE_CONTROL_MODE.BCKW50:
                flags = MOVEMENT_FLAGS.BACKWARD
            isOn = self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD50 or self.__cruiseControlMode == _CRUISE_CONTROL_MODE.BCKW50
            if isOn:
                flags |= MOVEMENT_FLAGS.CRUISE_CONTROL50
            elif self.__cruiseControlMode == _CRUISE_CONTROL_MODE.FWD25:
                flags |= MOVEMENT_FLAGS.CRUISE_CONTROL25
        rotateLeftFlag = MOVEMENT_FLAGS.ROTATE_LEFT
        rotateRightFlag = MOVEMENT_FLAGS.ROTATE_RIGHT
        if self.invRotationOnBackMovement and flags & MOVEMENT_FLAGS.BACKWARD != 0:
            rotateLeftFlag, rotateRightFlag = rotateRightFlag, rotateLeftFlag
        if cmdMap.isActive(CommandMapping.CMD_ROTATE_LEFT):
            if not cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
                flags |= rotateLeftFlag
        elif cmdMap.isActive(CommandMapping.CMD_ROTATE_RIGHT):
            flags |= rotateRightFlag
        if cmdMap.isActive(CommandMapping.CMD_BLOCK_TRACKS):
            flags |= MOVEMENT_FLAGS.BLOCK_TRACKS
        flags |= forceMask & forceFlags
        flags &= ~forceMask | forceFlags
        return flags

    def moveVehicle(self, flags, isKeyDown, handbrakeFired=False):
        if not self.__isOnArena:
            return
        else:
            self.__isVehicleMoving = flags != 0
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
                    if flags & MOVEMENT_FLAGS.ROTATE_RIGHT:
                        rotationDir = 1
                    elif flags & MOVEMENT_FLAGS.ROTATE_LEFT:
                        rotationDir = -1
                    if flags & MOVEMENT_FLAGS.FORWARD:
                        movementDir = 1
                    elif flags & MOVEMENT_FLAGS.BACKWARD:
                        movementDir = -1
                    vehicle.notifyInputKeysDown(movementDir, rotationDir, handbrakeFired)
                    if isKeyDown and not flags & MOVEMENT_FLAGS.BLOCK_TRACKS:
                        self.inputHandler.setAutorotation(True)
            elif vehicle is not None and vehicle.isStarted:
                vehicle.turnoffThrottle()
            self.cell.vehicle_moveWith(flags)
            return

    def enableOwnVehicleAutorotation(self, enable, triggeredByKey=False):
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.AUTO_ROTATION, enable)
        self.cell.vehicle_changeSetting(VEHICLE_SETTING.AUTOROTATION_ENABLED, enable)
        if triggeredByKey is True:
            self.__playOwnVehicleAutorotationSound(enable)

    def enableServerAim(self, enable):
        self.cell.setServerMarker(enable)

    def autoAim(self, target=None, magnetic=False):
        if ARENA_BONUS_TYPE_CAPS.checkAny(self.arenaBonusType, ARENA_BONUS_TYPE_CAPS.DISABLE_AUTO_AIM):
            return
        else:
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
                    self.onLockTarget(AimSound.TARGET_UNLOCKED, True)
                    TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE)
            return

    def __gunDamagedSound(self):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.GUN_DAMAGE_SOUND, ())
        if self.__gunDamagedShootSound is not None:
            self.__gunDamagedShootSound.play()
        return

    def __playOwnVehicleAutorotationSound(self, enabled):
        typeDesc = self.getVehicleAttached().typeDescriptor
        if typeDesc is None or not typeDesc.gun.turretYawLimits:
            return
        else:
            soundNotification = 'hulllock_on'
            if enabled:
                soundNotification = 'hulllock_off'
            self.soundNotifications.play(soundNotification)
            return

    def __getBattleEventsAdditionalData(self):
        observedVeh = self.guiSessionProvider.shared.vehicleState.getControllingVehicle()
        return {'role': observedVeh.typeDescriptor.role}

    def __dropStopUntilFireMode(self):
        if self.__stopUntilFire:
            self.__stopUntilFire = False
            if BigWorld.time() - self.__stopUntilFireStartTime > 60.0:
                self.__cruiseControlMode = _CRUISE_CONTROL_MODE.NONE
            self.__updateCruiseControlPanel()
            self.moveVehicle(self.makeVehicleMovementCommandByKeys(), True)

    def shoot(self, isRepeat=False):
        if self.__tryShootCallbackId is None:
            self.__tryShootCallbackId = BigWorld.callback(0.0, self.__tryShootCallback)
        if not self.__isOnArena:
            return
        else:
            dualGunControl = self.inputHandler.dualGunControl
            if dualGunControl is not None and dualGunControl.isShotLocked:
                return
            if self.__tryChargeCallbackID is not None:
                return
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
                    self.showVehicleError(self.__cantShootCriticals[error], args={'typeDescriptor': self.getVehicleDescriptor()})
                return
            if self.__gunReloadCommandWaitEndTime > BigWorld.time():
                return
            if self.__shotWaitingTimerID is not None or self.__isWaitingForShot:
                return
            if self.__chargeWaitingTimerID is not None:
                return
            if self.isGunLocked or self.__isOwnBarrelUnderWater():
                if not isRepeat:
                    self.showVehicleError(self.__cantShootCriticals['gun_locked'])
                return
            if self.__isOwnVehicleSwitchingSiegeMode():
                return
            self.cell.vehicle_shoot()
            shotArgs = None
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is not None and vehicle.isStarted:
                if vehicle.activeGunIndex is not None:
                    shotArgs = (vehicle.activeGunIndex, False)
            self.__startWaitingForShot(error != CANT_SHOOT_ERROR.EMPTY_CLIP, shotArgs)
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_SHOOT, aimingInfo=self.__aimingInfo)
            self.__dropStopUntilFireMode()
            return

    def shootDualGun(self, chargeActionType, isPrepared=False, isRepeat=False):
        keyDown = chargeActionType != DUALGUN_CHARGER_ACTION_TYPE.CANCEL
        if self.isForcedGuiControlMode():
            return
        else:
            if self.__tryChargeCallbackID is None and keyDown:
                self.__tryChargeCallbackID = BigWorld.callback(0.0, partial(self.__tryChargeCallback, chargeActionType))
            elif self.__tryChargeCallbackID is not None and not keyDown:
                BigWorld.cancelCallback(self.__tryChargeCallbackID)
                self.__tryChargeCallbackID = None
            if isRepeat and self.__chargeWaitingTimerID is not None:
                return
            if isPrepared and self.isWaitingForShot:
                return
            if not self.__isOnArena:
                return
            if keyDown and not self.__canMakeDualShot:
                return
            if not keyDown:
                self.__cancelWaitingForCharge()
            if self.isGunLocked or self.__isOwnBarrelUnderWater():
                if not isRepeat:
                    self.showVehicleError(self.__cantShootCriticals['gun_locked'])
                return
            for deviceName, stateName in self.__deviceStates.iteritems():
                msgName = self.__cantShootCriticals.get(deviceName + '_' + stateName)
                if msgName is not None:
                    if not isRepeat:
                        self.__gunDamagedSound()
                    self.showVehicleError(msgName)
                    return

            canShoot, error = self.guiSessionProvider.shared.ammo.canShoot(False)
            if not canShoot:
                if error in self.__cantShootCriticals:
                    self.showVehicleError(self.__cantShootCriticals[error], args={'typeDescriptor': self.getVehicleDescriptor()})
                return
            self.cell.setDualGunCharger(chargeActionType)
            return

    def __tryShootCallback(self):
        self.__tryShootCallbackId = None
        if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
            self.shoot(isRepeat=True)
        return

    def __tryChargeCallback(self, chargeActionType):
        self.__tryChargeCallbackID = None
        cmdMap = CommandMapping.g_instance
        if cmdMap.isActive(CommandMapping.CMD_CM_CHARGE_SHOT):
            self.shootDualGun(chargeActionType, isRepeat=True)
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
        _logger.info('Avatar.leaveArena')
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
        self.__cancelWaitingForCharge()
        self.__setIsOnArena(False)
        self.base.leaveArena(None)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            BigWorld.callback(0.0, replayCtrl.stop)
        if replayCtrl.isRecording:
            replayCtrl.stop()
        self.__reportClientStats()
        return

    def __reportClientStats(self):
        sessionData = self.statsCollector.getSessionData()
        if sessionData and self.lobbyContext.collectUiStats:
            report = {key:sessionData[key] for key in sessionData if key in ('ping_lt_50', 'ping_51_100', 'ping_101_150', 'ping_151_400', 'ping_gt_400', 'lag')}
            self.cell.reportClientStats(report)

    def addBotToArena(self, vehicleTypeName, team, pos=DEFAULT_VECTOR_3, group=0):
        compactDescr = vehicles.VehicleDescr(typeName=vehicleTypeName).makeCompactDescr()
        self.base.addBotToArena(compactDescr, team, self.name, pos, group)

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

    def getOwnVehicleMatrix(self, default=None):
        observedMatrix = self.getObservedVehicleMatrix()
        if observedMatrix is not None:
            return observedMatrix
        else:
            if Math.Matrix(self.__ownVehicleMProv).translation == Math.Matrix().translation:
                LOG_WARNING('Invalid vehicle matrix')
                if default is not None:
                    self.__ownVehicleMProv.target = default
            return self.__ownVehicleMProv
            return

    def getOwnVehicleTurretMatrix(self):
        turretMatrix = self.getObservedVehicleTurretMatrix()
        return turretMatrix if turretMatrix is not None else self.__ownVehicleTurretMProv

    def getOwnVehicleStabilisedMatrix(self):
        observedMatrix = self.getObservedVehicleStabilisedMatrix()
        return observedMatrix if observedMatrix is not None else self.__ownVehicleStabMProv

    def getOwnVehicleSpeeds(self, getInstantaneous=False):
        vehicle = BigWorld.entity(self.playerVehicleID)
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
        if vehicle is None or not vehicle.isStarted:
            return (0.0, 0.0)
        else:
            speedInfo = vehicle.speedInfo.value
            if getInstantaneous:
                speed = speedInfo[2]
                rspeed = speedInfo[3]
            else:
                speed = speedInfo[0]
                rspeed = speedInfo[1]
            physics = vehicle.typeDescriptor.physics
            if self.__fwdSpeedometerLimit is None or self.__bckwdSpeedometerLimit is None:
                self.__fwdSpeedometerLimit, self.__bckwdSpeedometerLimit = physics['speedLimits']
                self.__fwdSpeedometerLimit *= _MAX_SPEED_MULTIPLIER
                self.__bckwdSpeedometerLimit *= _MAX_SPEED_MULTIPLIER
            if speed > self.__fwdSpeedometerLimit:
                speed = self.__fwdSpeedometerLimit
                self.__fwdSpeedometerLimit += _SPEEDOMETER_CORRECTION_DELTA
            elif speed < self.__fwdSpeedometerLimit:
                lim = _MAX_SPEED_MULTIPLIER * physics['speedLimits'][0]
                if self.__fwdSpeedometerLimit > lim:
                    self.__fwdSpeedometerLimit -= _SPEEDOMETER_CORRECTION_DELTA
            if speed < -self.__bckwdSpeedometerLimit:
                speed = -self.__bckwdSpeedometerLimit
                self.__bckwdSpeedometerLimit += _SPEEDOMETER_CORRECTION_DELTA
            elif speed > -self.__bckwdSpeedometerLimit:
                lim = _MAX_SPEED_MULTIPLIER * physics['speedLimits'][1]
                if self.__bckwdSpeedometerLimit > lim:
                    self.__bckwdSpeedometerLimit -= _SPEEDOMETER_CORRECTION_DELTA
            rspeedLimit = physics['rotationSpeedLimit'] * _MAX_ROTATION_SPEED_MULTIPLIER
            if rspeed > rspeedLimit:
                rspeed = rspeedLimit
            elif rspeed < -rspeedLimit:
                rspeed = -rspeedLimit
            return (speed, rspeed)

    def getOwnVehicleShotDispersionAngle(self, turretRotationSpeed, withShot=0):
        descr = self.__getDetailedVehicleDescriptor()
        aimingStartTime, aimingStartFactor, dualAccStartTime, dualAccStartFactor = self.__aimingInfo
        multFactor, gunShotDispersionFactorsTurretRotation, chassisShotDispersionFactorsMovement, chassisShotDispersionFactorsRotation, aimingTime = self.__dispersionInfo
        dualAccMultFactor = multFactor
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
            shotFactor = descr.miscAttrs['gun/shotDispersionFactors/afterShot']
        else:
            shotFactor = descr.gun.shotDispersionFactors['afterShotInBurst']
        shotFactor *= shotFactor
        additiveSqrFactor = vehicleMovementFactor + vehicleRotationFactor + turretRotationFactor + shotFactor
        additiveSqrFactor *= self.__getAdditiveShotDispersionFactor(descr) ** 2
        idealFactor = multFactor * math.sqrt(1.0 + additiveSqrFactor)
        idealDualAccFactor = idealFactor
        dualAccuracy = getPlayerVehicleDualAccuracy()
        if dualAccuracy is not None:
            idealFactor *= dualAccuracy.getCurrentDualAccuracyFactor()
            idealDualAccFactor *= dualAccuracy.getDualAccuracyFactor()
            dualAccMultFactor *= dualAccuracy.getDualAccuracyFactor()
        currTime = BigWorld.time()
        aimingFactor = aimingStartFactor * math.exp((aimingStartTime - currTime) / aimingTime)
        dualAccFactor = dualAccStartFactor * math.exp((dualAccStartTime - currTime) / aimingTime)
        self.guiSessionProvider.shared.aimingSounds.updateDispersion(multFactor, aimingFactor, idealFactor, dualAccMultFactor, dualAccFactor, idealDualAccFactor, dualAccuracy is not None)
        if aimingFactor < idealFactor:
            aimingFactor = idealFactor
            self.__aimingInfo[0] = currTime
            self.__aimingInfo[1] = aimingFactor
        if dualAccFactor < idealDualAccFactor:
            dualAccFactor = idealDualAccFactor
            self.__aimingInfo[2] = currTime
            self.__aimingInfo[3] = dualAccFactor
        shotDispersionAngle = descr.gun.shotDispersionAngle
        return [shotDispersionAngle * aimingFactor,
         shotDispersionAngle * idealFactor,
         shotDispersionAngle * dualAccFactor,
         shotDispersionAngle * idealDualAccFactor]

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
        self.base.setDevelopmentFeature(0, 'tuneup_physics', 0, zlib.compress(jsonStr, 9))

    def tuneupVehicle(self, jsonStr):
        self.base.setDevelopmentFeature(0, 'tuneup_vehicle', 0, zlib.compress(jsonStr, 9))

    def receiveNotification(self, notification):
        LOG_DEBUG('receiveNotification', notification)
        g_wgncProvider.fromXmlString(notification)

    def messenger_onActionByServer_chat2(self, actionID, reqID, args):
        from messenger_common_chat2 import MESSENGER_ACTION_IDS as actions
        LOG_DEBUG('messenger_onActionByServer', actions.getActionName(actionID), reqID, args)
        MessengerEntry.g_instance.protos.BW_CHAT2.onActionReceived(actionID, reqID, args)

    def processInvitations(self, invitations):
        self.prebattleInvitations.processInvitations(invitations, ClientInvitations.InvitationScope.AVATAR)

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
            if vehicle.typeDescriptor is not None and vehicle.typeDescriptor.hasSiegeMode and vehicle.isStarted:
                vehicle.onSiegeStateUpdated(newState, timeToNextState)
            elif vehicle.isPlayerVehicle and self.__disableRespawnMode:
                self.__pendingSiegeSettings = (vehicleID, newState, timeToNextState)
        return

    def logXMPPEvents(self, intArr, strArr):
        self._doCmdIntArrStrArr(AccountCommands.CMD_LOG_CLIENT_XMPP_EVENTS, intArr, strArr, None)
        return

    def logMemoryCriticalEvent(self, memCritEvent):
        self.base.logMemoryCriticalEvent(memCritEvent)

    def activateGoodie(self, goodieID, callback=None):
        if callback is None:

            def __defaultLogger(resultID, errorCode):
                LOG_DEBUG('Action performed: "activateGoodie" resultID=%s, errorCode=%s' % (resultID, errorCode))

            callback = __defaultLogger
        self._doCmdInt(AccountCommands.CMD_ACTIVATE_GOODIE, goodieID, lambda requestID, resultID, errorCode: callback(resultID, errorCode))
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
        LOG_DEBUG_DEV('Avatar.setClientReady')
        if self.__initProgress < _INIT_STEPS.ALL_STEPS_PASSED or self.__initProgress & _INIT_STEPS.PLAYER_READY:
            return
        else:
            self.__initProgress |= _INIT_STEPS.PLAYER_READY
            self.inputHandler.setForcedGuiControlMode(self.__forcedGuiCtrlModeFlags)
            for v in BigWorld.entities.values():
                if v.inWorld and isinstance(v, Vehicle.Vehicle) and not v.isStarted:
                    self.__startVehicleVisual(v)

            BattleReplay.g_replayCtrl.onClientReady()
            self.base.setClientReady()
            if self.arena.period == ARENA_PERIOD.BATTLE:
                self.__setIsOnArena(True)
                battleTime = BigWorld.serverTime() - (self.arena.periodEndTime - self.arena.periodLength)
                BigWorld.notifyBattleTime(self.spaceID, battleTime)
            self.arena.onPeriodChange += self.__onArenaPeriodChange
            self.cell.autoAim(0, False)
            g_playerEvents.onAvatarReady()
            vehicle = BigWorld.entity(self.playerVehicleID)
            if vehicle is None:
                return
            vehicle.resetProperties()
            return

    def waitForPlayerChoice(self):
        _logger.info('[INIT_STEPS] Avatar.waitForPlayerChoice')
        if not self.__initProgress & _INIT_STEPS.WAIT_PLAYER_CHOICE:
            self.__initProgress |= _INIT_STEPS.WAIT_PLAYER_CHOICE

    def setPlayerReadyToBattle(self):
        _logger.info('[INIT_STEPS] Avatar.setPlayerReadyToBattle')
        if self.__initProgress & _INIT_STEPS.WAIT_PLAYER_CHOICE:
            self.__initProgress ^= _INIT_STEPS.WAIT_PLAYER_CHOICE
        self.__onInitStepCompleted()

    def __onInitStepCompleted(self):
        LOG_DEBUG('Avatar.__onInitStepCompleted()', self.__initProgress)
        if constants.IS_CAT_LOADED:
            if self.__initProgress & _INIT_STEPS.INIT_COMPLETED:
                return
        if self.__initProgress < _INIT_STEPS.ALL_STEPS_PASSED or self.__initProgress & _INIT_STEPS.INIT_COMPLETED or self.__initProgress & _INIT_STEPS.WAIT_PLAYER_CHOICE:
            return
        self.__initProgress |= _INIT_STEPS.INIT_COMPLETED
        self.__createFakeCameraMatrix()
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
        self.__projectileMover.setSpaceID(self.spaceID)
        self.__initGunRotator()
        self.positionControl = AvatarPositionControl.AvatarPositionControl(self)
        self.__dualGunHelper = DualGun.DualGunHelper()
        self.__startGUI()

    def __initGUI(self):
        prereqs = []
        if not g_offlineMapCreator.Active():
            self.inputHandler = AvatarInputHandler.AvatarInputHandler(self.spaceID)
            prereqs += self.inputHandler.prerequisites()
        self.soundNotifications = IngameSoundNotifications.IngameSoundNotifications()
        self.complexSoundNotifications = IngameSoundNotifications.ComplexSoundNotifications()
        arena = BigWorld.player().arena
        notificationsRemapping = arena.arenaType.notificationsRemapping or {}
        notificationsRemapping = arena.battleModifiers(BattleParams.SOUND_NOTIFICATIONS, notificationsRemapping)
        self.soundNotifications.setRemapping(notificationsRemapping)
        return prereqs

    def __startGUI(self):
        self.inputHandler.start()
        self.arena.onVehicleKilled += self.__onArenaVehicleKilled
        self.arena.onVehicleAdded += self.__onVehicleInfoAddedForStartVisual
        MessengerEntry.g_instance.onAvatarInitGUI()
        self.soundNotifications.start()

    def __destroyGUI(self):
        self.arena.onVehicleKilled -= self.__onArenaVehicleKilled
        self.arena.onVehicleAdded -= self.__onVehicleInfoAddedForStartVisual
        self.soundNotifications.destroy()
        self.soundNotifications = None
        self.complexSoundNotifications.destroy()
        self.complexSoundNotifications = None
        self.inputHandler.stop()
        self.inputHandler = None
        return

    def __reloadGUI(self):
        self.__destroyGUI()
        self.__initGUI()
        self.__startGUI()
        self.setForcedGuiControlMode(GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED | GUI_CTRL_MODE_FLAG.MOVING_DISABLED | GUI_CTRL_MODE_FLAG.AIMING_ENABLED)
        self.setForcedGuiControlMode(GUI_CTRL_MODE_FLAG.CURSOR_DETACHED)

    def __initGunRotator(self):
        if self.isObserver():
            self.gunRotator = VehicleObserverGunRotator.VehicleObserverGunRotator(self)
        else:
            self.gunRotator = VehicleGunRotator.VehicleGunRotator(self)

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
     'leftTrack0_destroyed': 'cantMoveChassisDamaged',
     'rightTrack0_destroyed': 'cantMoveChassisDamaged',
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
            return

    def showVehicleError(self, msgName, args=None):
        self.guiSessionProvider.shared.messages.showVehicleError(msgName, args)

    def __showDamageIconAndPlaySound(self, damageCode, extra, vehicleID, ignoreMessages=False):
        deviceName = None
        deviceState = None
        soundType = None
        soundNotificationCheckFn = None
        if extra is not None:
            if damageCode in self.__damageInfoCriticals:
                deviceName = extra.name[:-len('Health')]
                if damageCode == 'DEVICE_REPAIRED_TO_CRITICAL':
                    deviceState = 'repaired'
                    soundType = self.__getSoundTypeForTracks(deviceName, extra)
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DEVICE_CRITICAL, deviceName=deviceName, isRepaired=True, isCriticalNow=True)
                else:
                    deviceState = 'critical'
                    soundType = 'critical'
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DEVICE_CRITICAL, deviceName=deviceName, isRepaired=False, isCriticalNow=True)
                self.__deviceStates[deviceName] = 'critical'
            elif damageCode in self.__damageInfoDestructions:
                deviceName = extra.name[:-len('Health')]
                deviceState = 'destroyed'
                soundType = 'destroyed'
                self.__deviceStates[deviceName] = 'destroyed'
                if damageCode.find('TANKMAN_HIT') != -1 and not ignoreMessages:
                    self.playSoundIfNotMuted('crew_member_contusion')
                if damageCode.find('TANKMAN_HIT') != -1:
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_TANKMAN_SHOOTED, tankmanName=deviceName, isHealed=False)
                else:
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DEVICE_CRITICAL, deviceName=deviceName, isRepaired=False, isCriticalNow=False)
                if self.__cruiseControlMode is not _CRUISE_CONTROL_MODE.NONE:
                    msgName = self.__cantMoveCriticals.get(deviceName + '_' + deviceState)
                    if msgName is not None:
                        self.showVehicleError(msgName)
            elif damageCode in self.__damageInfoHealings:
                deviceName = extra.name[:-len('Health')]
                deviceState = 'normal'
                if deviceName in ('leftTrack0', 'rightTrack0'):
                    soundType = self.__getSoundTypeForTracks(deviceName, extra)
                else:
                    soundType = 'fixed'
                self.__deviceStates.pop(deviceName, None)
                if damageCode == 'TANKMAN_RESTORED':
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_TANKMAN_SHOOTED, tankmanName=deviceName, isHealed=True)
                elif damageCode == 'DEVICE_REPAIRED':
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.PLAYER_DEVICE_CRITICAL, deviceName=deviceName, isRepaired=True, isCriticalNow=False)
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
            if sound is not None and not ignoreMessages:
                self.playSoundIfNotMuted(sound, soundNotificationCheckFn)
        return

    def __getSoundTypeForTracks(self, deviceName, extra):
        if 'functionalCanMove' in extra.sounds:
            tracksToCheck = ['leftTrack0', 'rightTrack0']
            if deviceName in tracksToCheck:
                tracksToCheck.remove(deviceName)
            canMove = True
            for trackName in tracksToCheck:
                if trackName in self.__deviceStates and self.__deviceStates[trackName] == 'destroyed':
                    canMove = False
                    break

            if canMove and deviceName in self.__deviceStates and self.__deviceStates[deviceName] == 'destroyed':
                return 'functionalCanMove'

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
    __damageInfoNoNotification = ('DEVICE_CRITICAL',
     'DEVICE_DESTROYED',
     'TANKMAN_HIT',
     'FIRE',
     'DEVICE_CRITICAL_AT_DROWNING',
     'DEVICE_DESTROYED_AT_DROWNING',
     'TANKMAN_HIT_AT_DROWNING')

    def __onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
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
            self.__cancelWaitingForCharge()
            try:
                if self.gunRotator is not None:
                    self.gunRotator.stop()
            except Exception:
                LOG_CURRENT_EXCEPTION()

        if targetID == self.playerVehicleID:
            self.inputHandler.setKillerVehicleID(attackerID)
            return
        else:
            self.guiSessionProvider.shared.messages.showVehicleKilledMessage(self, targetID, attackerID, equipmentID, reason)
            return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        self.__setIsOnArena(period == ARENA_PERIOD.BATTLE)
        if period == ARENA_PERIOD.BATTLE and period > self.__prevArenaPeriod:
            if self.arenaBonusType == constants.ARENA_BONUS_TYPE.EPIC_BATTLE:
                if self.__prevArenaPeriod >= 0:
                    self.soundNotifications.play(EPIC_SOUND.BF_EB_START_BATTLE[self.team])
            else:
                self.soundNotifications.play('start_battle')
            BigWorld.notifyBattleTime(self.spaceID, 0)
        self.__prevArenaPeriod = period

    def __startWaitingForShot(self, makePrediction, shotArgs=None):
        if makePrediction:
            if self.__shotWaitingTimerID is not None:
                BigWorld.cancelCallback(self.__shotWaitingTimerID)
                self.__shotWaitingTimerID = None
            timeout = BigWorld.LatencyInfo().value[3] * 0.5
            timeout = min(_SHOT_WAITING_MAX_TIMEOUT, timeout)
            timeout = max(_SHOT_WAITING_MIN_TIMEOUT, timeout)
            self.__shotWaitingTimerID = BigWorld.callback(timeout, partial(self.__showTimedOutShooting, shotArgs))
            self.__isWaitingForShot = True
            self.inputHandler.setAimingMode(True, AIMING_MODE.SHOOTING)
            if not self.inputHandler.getAimingMode(AIMING_MODE.USER_DISABLED):
                self.gunRotator.targetLastShotPoint = True
            self.__gunReloadCommandWaitEndTime = BigWorld.time() + 2.0
        return

    def __startWaitingForCharge(self, timeLeft):
        chargeTime = timeLeft - constants.SERVER_TICK_LENGTH
        self.__chargeWaitingTimerID = BigWorld.callback(chargeTime, self.__onTimedOutCharge)

    def __onTimedOutCharge(self):
        self.__chargeWaitingTimerID = None
        self.__startWaitingForShot(self.__canMakeDualShot, (0, True))
        return

    def __cancelWaitingForCharge(self):
        if self.__chargeWaitingTimerID is not None:
            BigWorld.cancelCallback(self.__chargeWaitingTimerID)
            self.__chargeWaitingTimerID = None
        return

    def __showTimedOutShooting(self, shotArgs):
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
                if shotArgs is not None:
                    gunIndexDelayed, isDual = shotArgs
                    vehicle.showShooting(2 if isDual else burstCount, gunIndexDelayed, True)
                    return
                vehicle.showShooting(burstCount, None, True)
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
            self.cell.setServerMarker(True)
            self.base.setDevelopmentFeature(0, 'heal', 0, '')
            self.base.setDevelopmentFeature(0, 'stop_bot', 0, '')
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
        self.base.logLag()

    def __updateCruiseControlPanel(self):
        if self.__stopUntilFire or not self.__isVehicleAlive:
            mode = _CRUISE_CONTROL_MODE.NONE
        else:
            mode = self.__cruiseControlMode
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CRUISE_MODE, mode)

    def __updateVehicleSetting(self, _, code, value, fromServer=True):
        if code == VEHICLE_SETTING.CURRENT_SHELLS:
            ammoCtrl = self.guiSessionProvider.shared.ammo
            if not ammoCtrl.shellInAmmo(value):
                return
            ammoCtrl.setCurrentShellCD(value, not fromServer)
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
        isObserver = BigWorld.player().isObserver()
        if not isObserver:
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle is None or not vehicle.isAlive():
                return
        currentVehicle = self.getVehicleAttached()
        prebattleVehicleID = self.guiSessionProvider.shared.prebattleSetups.getPrebattleVehicleID()
        if prebattleVehicleID == vehicleID:
            return
        else:
            if currentVehicle is not None and vehicleID == currentVehicle.id:
                self.guiSessionProvider.shared.ammo.setShells(compactDescr, quantity, quantityInClip)
            return

    def __processVehicleEquipments(self, vehicleID, compactDescr, quantity, stage, timeRemaining, totalTime):
        if compactDescr:
            descriptor = vehicles.getItemByCompactDescr(compactDescr)
            if descriptor.name == 'aimingStabilizerBattleBooster':
                self.__aimingBooster = descriptor
        currentVehicle = self.getVehicleAttached()
        if currentVehicle is not None and vehicleID == currentVehicle.id:
            self.guiSessionProvider.shared.equipments.setEquipment(compactDescr, quantity, stage, timeRemaining, totalTime)
        return

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

    def _doCmdInt(self, cmd, int1, callback):
        self.__doCmd('doCmdInt', cmd, callback, int1)

    def _doCmdInt2(self, cmd, int1, int2, callback):
        self.__doCmd('doCmdInt2', cmd, callback, int1, int2)

    def _doCmdInt3(self, cmd, int1, int2, int3, callback):
        self.__doCmd('doCmdInt3', cmd, callback, int1, int2, int3)

    def _doCmdInt3Str(self, cmd, int1, int2, int3, s, callback):
        self.__doCmd('doCmdInt3Str', cmd, callback, int1, int2, int3, s)

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

    def _doCmdIntStr(self, cmd, int1, s, callback):
        self.__doCmd('doCmdIntStr', cmd, callback, int1, s)

    def update(self, pickledDiff):
        self._update(cPickle.loads(pickledDiff))

    def _update(self, diff):
        if self.intUserSettings is not None:
            self.intUserSettings.synchronize(False, diff)
            g_playerEvents.onClientUpdated(diff, False)
        return

    def isSynchronized(self):
        return True if self.intUserSettings is None else self.intUserSettings.isSynchronized()

    def reloadPlans(self, *args):
        self.base.setDevelopmentFeature(0, 'reloadPlans', 0, zlib.compress(cPickle.dumps(*args)))

    def killEngine(self):
        self.base.setDevelopmentFeature(0, 'kill_engine', 0, '')

    def change_rank_xp(self, value):
        self.base.setDevelopmentFeature(0, 'change_rank_xp', value, '')

    def receivePhysicsDebugInfo(self, info):
        modifD = dict()
        self.telemetry.receivePhysicsDebugInfo(info, modifD)

    def physicModeChanged(self, newMode):
        self.__physicsMode = newMode

    def __isPlayerInSquad(self):
        return self.arena is not None and self.guiSessionProvider.getArenaDP().isSquadMan(vID=self.playerVehicleID)

    def __getAdditiveShotDispersionFactor(self, descriptor):
        if self.__aimingBooster is not None:
            factors = descriptor.miscAttrs.copy()
            self.__aimingBooster.updateVehicleAttrFactorsForAspect(descriptor, factors, None)
        else:
            factors = descriptor.miscAttrs
        return factors['additiveShotDispersionFactor']

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

    def muteSounds(self, newMuteSounds):
        self._muteSounds = newMuteSounds

    def playSoundIfNotMuted(self, sound, checkFn=None):
        if sound not in self._muteSounds:
            self.soundNotifications.play(sound, checkFn=checkFn)

    def onLockTarget(self, state, playVoiceNotifications):
        if playVoiceNotifications:
            AimSound.play(state, self.soundNotifications)
        else:
            AimSound.play(state)
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onLockTarget(state, playVoiceNotifications)

    def onDynamicComponentCreated(self, component):
        LOG_DEBUG_DEV('Component created', component)

    def addOrRemoveMarkerTo(self, key):
        if constants.HAS_DEV_RESOURCES:
            ctrl = self.guiSessionProvider.shared.areaMarker
            if not ctrl:
                return False
            if key == 0:
                matrix = Math.Matrix(self.vehicle.matrix)
                ctrl.addMarker(ctrl.createMarker(matrix, 0))
                return True
            if key == 1:
                ctrl.removeAllMarkers()
                return True
            if key == 2:
                vehicle = BigWorld.entity(self.playerVehicleID)
                ctrl.addMarker(ctrl.createMarker(vehicle.matrix, 0))
                return True
        return False

    @property
    def initCompleted(self):
        return self.__initProgress & _INIT_STEPS.INIT_COMPLETED != 0

    def hotReloadCGF(self):
        self.base.setDevelopmentFeature(0, 'hot_reload', 0, '')


def preload(alist):
    ds = ResMgr.openSection('precache.xml')
    if ds is not None:
        for sec in ds.values():
            alist.append(sec.asString)

    return


def _boundingBoxAsVector4(bb):
    return Math.Vector4(bb[0][0], bb[0][1], bb[1][0], bb[1][1])


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
    gunOffs = vd.activeGunShotPosition
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
