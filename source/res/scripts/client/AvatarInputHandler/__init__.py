# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/__init__.py
import functools
import logging
import math
from functools import partial
import BigWorld
import Keys
import Math
import ResMgr
from AvatarInputHandler.AimingSystems import disableShotPointCache
from AvatarInputHandler.vehicles_selection_mode import VehiclesSelectionControlMode
from AvatarInputHandler.commands.fl_random_reserves import FLRandomReserves
from aih_constants import MAP_CASE_MODES
from helpers.CallbackDelayer import CallbackDelayer
import BattleReplay
import CommandMapping
import DynamicCameras.ArcadeCamera
import DynamicCameras.ArtyCamera
import DynamicCameras.DualGunCamera
import DynamicCameras.SniperCamera
import DynamicCameras.StrategicCamera
import DynamicCameras.kill_cam_camera
import GenericComponents
import MapCaseMode
import RespawnDeathMode
import TriggersManager
import aih_constants
import cameras
import constants
import control_modes
import kill_cam_modes
import DynamicCameras.twin_gun_camera
from AvatarInputHandler import AimingSystems, keys_handlers
from AvatarInputHandler import aih_global_binding, gun_marker_ctrl
from AvatarInputHandler import steel_hunter_control_modes
from BigWorld import SniperAimingSystem
from AvatarInputHandler.commands.auto_shoot_gun_control import createAutoShootGunControl
from AvatarInputHandler.commands.dualgun_control import DualGunController
from AvatarInputHandler.commands.prebattle_setups_control import PrebattleSetupsControl
from AvatarInputHandler.commands.radar_control import RadarControl
from AvatarInputHandler.commands.siege_mode_control import SiegeModeControl
from AvatarInputHandler.commands.rocket_acceleration_control import RocketAccelerationControl
from AvatarInputHandler.commands.vehicle_upgrade_control import VehicleUpdateControl
from AvatarInputHandler.commands.vehicle_upgrade_control import VehicleUpgradePanelControl
from AvatarInputHandler.remote_camera_sender import RemoteCameraSender
from AvatarInputHandler.siege_mode_player_notifications import SiegeModeSoundNotifications, TurboshaftModeSoundNotifications, TwinGunModeSoundNotifications, SiegeModeCameraShaker
from Event import Event
from TriggersManager import TRIGGER_TYPE
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import ARENA_PERIOD, AIMING_MODE
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import g_guiResetters, GUI_CTRL_MODE_FLAG, GUI_SETTINGS
from gui.app_loader import settings
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from cgf_obsolete_script.script_game_object import ScriptGameObject, ComponentDescriptor
INPUT_HANDLER_CFG = 'gui/avatar_input_handler.xml'
_logger = logging.getLogger(__name__)
_CTRL_TYPE = aih_constants.CTRL_TYPE
_ARTY_CTRL_TYPE = _CTRL_TYPE.USUAL if GUI_SETTINGS.spgAlternativeAimingCameraEnabled else _CTRL_TYPE.DEVELOPMENT
_ShakeReason = aih_constants.ShakeReason
_CTRL_MODE = aih_constants.CTRL_MODE_NAME
_GUN_MARKER_TYPE = aih_constants.GUN_MARKER_TYPE
_GUN_MARKER_FLAG = aih_constants.GUN_MARKER_FLAG
_BINDING_ID = aih_global_binding.BINDING_ID
_CTRL_MODES = aih_constants.CTRL_MODES
_CTRLS_FIRST = _CTRL_MODE.DEFAULT
_INITIAL_MODE_BY_BONUS_TYPE = {constants.ARENA_BONUS_TYPE.COMP7: _CTRL_MODE.VEHICLES_SELECTION,
 constants.ARENA_BONUS_TYPE.TOURNAMENT_COMP7: _CTRL_MODE.VEHICLES_SELECTION,
 constants.ARENA_BONUS_TYPE.TRAINING_COMP7: _CTRL_MODE.VEHICLES_SELECTION}
_CONTROL_MODE_SWITCH_COOLDOWN = 1.0
_CTRLS_DESC_MAP = {_CTRL_MODE.ARCADE: (control_modes.ArcadeControlMode, 'arcadeMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.STRATEGIC: (control_modes.StrategicControlMode, 'strategicMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.ARTY: (control_modes.ArtyControlMode, 'artyMode', _ARTY_CTRL_TYPE),
 _CTRL_MODE.SNIPER: (control_modes.SniperControlMode, 'sniperMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.DUAL_GUN: (control_modes.DualGunControlMode, 'sniperMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.TWIN_GUN: (control_modes.TwinGunControlMode, 'sniperMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.POSTMORTEM: (control_modes.PostMortemControlMode, 'postMortemMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.DEBUG: (control_modes.DebugControlMode, None, _CTRL_TYPE.DEVELOPMENT),
 _CTRL_MODE.VIDEO: (control_modes.VideoCameraControlMode, 'videoMode', _CTRL_TYPE.OPTIONAL),
 _CTRL_MODE.MAP_CASE: (MapCaseMode.MapCaseControlMode, 'strategicMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.MAP_CASE_ARCADE: (MapCaseMode.ArcadeMapCaseControlMode, 'arcadeMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.MAP_CASE_EPIC: (MapCaseMode.EpicMapCaseControlMode, 'strategicMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.MAP_CASE_ARCADE_EPIC_MINEFIELD: (MapCaseMode.AracdeMinefieldControleMode, 'arcadeEpicMinefieldMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.RESPAWN_DEATH: (RespawnDeathMode.RespawnDeathMode, 'postMortemMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.DEATH_FREE_CAM: (control_modes.DeathFreeCamMode, 'freeVideoMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.KILL_CAM: (kill_cam_modes.KillCamMode, 'killCamMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.LOOK_AT_KILLER: (kill_cam_modes.LookAtKillerMode, 'killCamMode', _CTRL_TYPE.USUAL),
 _CTRL_MODE.VEHICLES_SELECTION: (VehiclesSelectionControlMode, 'vehiclesSelection', _CTRL_TYPE.USUAL)}
OVERWRITE_CTRLS_DESC_MAP = {}
for royaleBonusCap in constants.ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
    OVERWRITE_CTRLS_DESC_MAP[royaleBonusCap] = {_CTRL_MODE.POSTMORTEM: (steel_hunter_control_modes.SHPostMortemControlMode, 'postMortemMode', _CTRL_TYPE.USUAL)}

_DYNAMIC_CAMERAS = (DynamicCameras.ArcadeCamera.ArcadeCamera,
 DynamicCameras.SniperCamera.SniperCamera,
 DynamicCameras.StrategicCamera.StrategicCamera,
 DynamicCameras.ArtyCamera.ArtyCamera,
 DynamicCameras.DualGunCamera.DualGunCamera,
 DynamicCameras.twin_gun_camera.TwinGunCamera,
 DynamicCameras.kill_cam_camera.KillCamera)
_FREE_AND_CHAT_SHORTCUT_CMD = (CommandMapping.CMD_CM_FREE_CAMERA, CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND)

class DynamicCameraSettings(object):
    settings = property(lambda self: self.__dynamic)

    def __init__(self, dataSec):
        self.__dynamic = {'caliberImpulses': [],
         'massSensitivity': []}
        caliberSettings = dataSec['caliberImpulses']
        if caliberSettings is not None:
            self.__dynamic['caliberImpulses'] = self.__readRange(caliberSettings)
        else:
            _logger.error('<caliberImpulses> dataSection is not found!')
        sensitivitySettings = dataSec['massSensitivity']
        if sensitivitySettings is not None:
            self.__dynamic['massSensitivity'] = self.__readRange(sensitivitySettings)
        else:
            _logger.error('<massSensitivity> dataSection is not found!')
        self.__dynamic['collisionSpeedToImpulseRatio'] = cameras.readFloat(dataSec, 'collisionSpeedToImpulseRatio', 0, 1000, 1.0)
        self.__dynamic['minCollisionSpeed'] = cameras.readFloat(dataSec, 'minCollisionSpeed', 0, 1000, 1.0)
        self.__dynamic['zeroDamageHitSensitivity'] = cameras.readFloat(dataSec, 'zeroDamageHitSensitivity', 0, 1000, 1.0)
        self.__dynamic['ownShotImpulseDelay'] = cameras.readFloat(dataSec, 'ownShotImpulseDelay', 0.0, 1000, 0.0)
        return

    def getGunImpulse(self, caliber):
        impulseMagnitude = 0.0
        for minCaliber, magnitude in self.__dynamic['caliberImpulses']:
            if caliber < minCaliber:
                break
            impulseMagnitude = magnitude

        return impulseMagnitude

    def getSensitivityToImpulse(self, vehicleMass):
        sensitivity = 0.0
        for mass, sense in self.__dynamic['massSensitivity']:
            if vehicleMass < mass:
                break
            sensitivity = sense

        return sensitivity

    def __readRange(self, dataSec):
        ranges = []
        for rangeSec in dataSec.values():
            val = rangeSec.asVector2
            ranges.append((val.x, val.y))

        ranges.sort(key=lambda val: val[0])
        return ranges


class AvatarInputHandler(CallbackDelayer, ScriptGameObject):
    ctrl = property(lambda self: self.__curCtrl)
    ctrls = property(lambda self: self.__ctrls)
    isSPG = property(lambda self: self.__isSPG)
    isATSPG = property(lambda self: self.__isATSPG)
    isDualGun = property(lambda self: self.__isDualGun)
    isTwinGun = property(lambda self: self.__isTwinGun)
    isMagneticAimEnabled = property(lambda self: self.__isMagnetAimEnabled)
    isFlashBangAllowed = property(lambda self: self.__curCtrl not in (self.__ctrls['video'], self.__ctrls['killcam']))
    isDetached = property(lambda self: self.__isDetached)
    isGuiVisible = property(lambda self: self.__isGUIVisible)
    isStarted = property(lambda self: self.__isStarted)
    isObserverFPV = property(lambda self: BigWorld.player().isObserver() and BigWorld.player().isObserverFPV)
    remoteCameraSender = property(lambda self: self.__remoteCameraSender)
    __ctrlModeName = aih_global_binding.bindRW(_BINDING_ID.CTRL_MODE_NAME)
    __aimOffset = aih_global_binding.bindRW(_BINDING_ID.AIM_OFFSET)
    _DYNAMIC_CAMERAS_ENABLED_KEY = 'global/dynamicCameraEnabled'
    settingsCore = dependency.descriptor(ISettingsCore)
    appLoader = dependency.descriptor(IAppLoader)

    @staticmethod
    def enableDynamicCamera(enable, useHorizontalStabilizer=True):
        for dynamicCameraClass in _DYNAMIC_CAMERAS:
            dynamicCameraClass.enableDynamicCamera(enable)

        if isinstance(useHorizontalStabilizer, tuple):
            SniperAimingSystem.setStabilizerSettings(*useHorizontalStabilizer)
        else:
            SniperAimingSystem.setStabilizerSettings(useHorizontalStabilizer, True)

    @staticmethod
    def enableHullLock(enable):
        SniperAimingSystem.hullLockSetting = enable

    @staticmethod
    def isCameraDynamic():
        for dynamicCameraClass in _DYNAMIC_CAMERAS:
            if not dynamicCameraClass.isCameraDynamic():
                return False

        return True

    @staticmethod
    def isSniperStabilized():
        return SniperAimingSystem.getStabilizerSettings()

    @staticmethod
    def isHullLockEnabled():
        return SniperAimingSystem.hullLockSetting

    @property
    def ctrlModeName(self):
        return self.__ctrlModeName

    siegeModeControl = ComponentDescriptor()
    dualGunControl = ComponentDescriptor()
    siegeModeSoundNotifications = ComponentDescriptor()
    rocketAccelerationControl = ComponentDescriptor()
    DEFAULT_AIH_WORLD_ID = -1

    def __init__(self, spaceID):
        CallbackDelayer.__init__(self)
        if spaceID == 0:
            spaceID = self.DEFAULT_AIH_WORLD_ID
        ScriptGameObject.__init__(self, spaceID, 'AvatarInputHandler')
        self.__alwaysShowAimKey = None
        self.__showMarkersKey = None
        sec = self._readCfg()
        self.onCameraChanged = Event()
        self.onPostmortemKillerVisionEnter = Event()
        self.onPostmortemKillerVisionExit = Event()
        self.onReceivedKillerID = Event()
        self.__isArenaStarted = False
        self.__isStarted = False
        self.__targeting = _Targeting()
        self.__vertScreenshotCamera = _VertScreenshotCamera()
        self.__ctrls = dict()
        self.__killerVehicleID = None
        self.__deathReasonID = None
        self.__isAutorotation = True
        self.__prevModeAutorotation = None
        self.__isSPG = False
        self.__isATSPG = False
        self.__isDualGun = False
        self.__isTwinGun = False
        self.__isMagnetAimEnabled = False
        self.__setupCtrls(sec)
        self.__curCtrl = self.__ctrls[_CTRLS_FIRST]
        self.__ctrlModeName = _CTRLS_FIRST
        self.__isDetached = False
        self.__pendingModeSwitch = None
        self.__observerVehicle = None
        self.__commands = []
        self.__detachedCommands = []
        self.__persistentCommands = [PrebattleSetupsControl()]
        self.__remoteCameraSender = None
        self.__isGUIVisible = False
        self.__lastSwitchTime = 0
        return

    def __constructComponents(self):
        self.__commands = []
        self.__detachedCommands = []
        self.__persistentCommands = []
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if not vehicle:
            _logger.debug('Attempt to construct components when vehicle is none')
            return
        else:
            typeDescr = vehicle.typeDescriptor
            notificationsCls = None
            if typeDescr.hasSiegeMode:
                if not self.siegeModeControl:
                    self.siegeModeControl = SiegeModeControl()
                self.__commands.append(self.siegeModeControl)
                if typeDescr.hasHydraulicChassis or typeDescr.isWheeledVehicle:
                    notificationsCls = SiegeModeSoundNotifications
                elif typeDescr.hasTurboshaftEngine:
                    notificationsCls = TurboshaftModeSoundNotifications
                elif typeDescr.isTwinGunVehicle:
                    notificationsCls = TwinGunModeSoundNotifications
                self.siegeModeControl.onSiegeStateChanged += SiegeModeCameraShaker.shake
            if typeDescr.hasRocketAcceleration:
                if not self.rocketAccelerationControl:
                    self.rocketAccelerationControl = RocketAccelerationControl()
                self.__commands.append(self.rocketAccelerationControl)
            if notificationsCls is None or not self.siegeModeSoundNotifications or notificationsCls.getModeType() != self.siegeModeSoundNotifications.getModeType() or self.siegeModeSoundNotifications.vehicleID != vehicle.id:
                if self.siegeModeSoundNotifications:
                    self.siegeModeControl.onSiegeStateChanged -= self.siegeModeSoundNotifications.onSiegeStateChanged
                    self.siegeModeSoundNotifications.stop()
                    self.siegeModeSoundNotifications = None
                if notificationsCls is not None:
                    notifications = notificationsCls(vehicle.id)
                    self.siegeModeControl.onSiegeStateChanged += notifications.onSiegeStateChanged
                    notifications.start()
                    self.siegeModeSoundNotifications = notifications
            if typeDescr.isDualgunVehicle and not self.dualGunControl:
                self.dualGunControl = DualGunController(typeDescr)
            elif not typeDescr.isDualgunVehicle:
                self.dualGunControl = None
            if typeDescr.isAutoShootGunVehicle:
                self.__commands.append(createAutoShootGunControl())
            if player.hasBonusCap(ARENA_BONUS_TYPE_CAPS.RADAR):
                self.__commands.append(RadarControl())
            if player.hasBonusCap(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE):
                self.__commands.append(VehicleUpdateControl())
                self.__commands.append(VehicleUpgradePanelControl())
                self.__detachedCommands.append(VehicleUpgradePanelControl())
            if player.hasBonusCap(ARENA_BONUS_TYPE_CAPS.EPIC):
                self.__detachedCommands.append(FLRandomReserves())
            if player.hasBonusCap(ARENA_BONUS_TYPE_CAPS.SWITCH_SETUPS):
                self.__persistentCommands.append(PrebattleSetupsControl())
            if vehicle.appearance:
                vehicle.appearance.removeComponentByType(GenericComponents.ControlModeStatus)
                vehicle.appearance.createComponent(GenericComponents.ControlModeStatus, _CTRL_MODES.index(self.__ctrlModeName))
            if player.inWorld:
                player.entityGameObject.removeComponentByType(GenericComponents.ControlModeStatus)
                player.entityGameObject.createComponent(GenericComponents.ControlModeStatus, _CTRL_MODES.index(self.__ctrlModeName))
            return

    def prerequisites(self):
        out = []
        for ctrl in self.__ctrls.itervalues():
            out += ctrl.prerequisites()

        return out

    def handleKeyEvent(self, event):
        import game
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isRepeat:
            return False
        else:
            player = BigWorld.player()
            for command in self.__persistentCommands:
                if command.handleKeyEvent(isDown, key, mods, event):
                    return True

            if self.__isStarted and self.__isDetached:
                alwaysReceive = self.__curCtrl.alwaysReceiveKeyEvents(isDown=isDown) and not self.isObserverFPV
                cmdLockTarget = CommandMapping.g_instance.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key)
                cmdFreeAndChat = CommandMapping.g_instance.isFiredList(_FREE_AND_CHAT_SHORTCUT_CMD, key, True)
                if alwaysReceive or cmdLockTarget or cmdFreeAndChat:
                    self.__curCtrl.handleKeyEvent(isDown, key, mods, event)
                for command in self.__detachedCommands:
                    if command.handleKeyEvent(isDown, key, mods, event):
                        return True

                return player.handleKey(isDown, key, mods)
            if not self.__isStarted and isDown and mods == 0:
                if keys_handlers.processAmmoSelection(key):
                    return True
            if not self.__isStarted or self.__isDetached:
                return False
            for command in self.__commands:
                if command.handleKeyEvent(isDown, key, mods, event):
                    return True

            if isDown and BigWorld.isKeyDown(Keys.KEY_CAPSLOCK):
                if self.__alwaysShowAimKey is not None and key == self.__alwaysShowAimKey:
                    gui_event_dispatcher.toggleCrosshairVisibility()
                    return True
                if self.__showMarkersKey is not None and key == self.__showMarkersKey and not self.__isGUIVisible:
                    gui_event_dispatcher.toggleMarkers2DVisibility()
                    return True
                if key == Keys.KEY_F5 and constants.HAS_DEV_RESOURCES:
                    self.__vertScreenshotCamera.enable(not self.__vertScreenshotCamera.isEnabled)
                    return True
            if key == Keys.KEY_SPACE and isDown and player.isObserver() and self.__ctrlModeName != _CTRL_MODE.KILL_CAM:
                if self.isControlModeChangeAllowed():
                    player.switchObserverFPV()
                    return True
            return True if not self.isObserverFPV and self.__curCtrl.handleKeyEvent(isDown, key, mods, event) else player.handleKey(isDown, key, mods)

    def handleMouseEvent(self, dx, dy, dz):
        return False if not self.__isStarted or self.__isDetached else self.__curCtrl.handleMouseEvent(dx, dy, dz)

    def setForcedGuiControlMode(self, flags):
        result = False
        detached = flags & GUI_CTRL_MODE_FLAG.CURSOR_ATTACHED > 0
        if detached ^ self.__isDetached:
            self.__isDetached = detached
            self.__targeting.detach(self.__isDetached)
            if detached:
                self.appLoader.attachCursor(settings.APP_NAME_SPACE.SF_BATTLE, flags=flags)
                result = True
                if flags & GUI_CTRL_MODE_FLAG.AIMING_ENABLED > 0:
                    self.setAimingMode(False, AIMING_MODE.USER_DISABLED)
            else:
                self.appLoader.detachCursor(settings.APP_NAME_SPACE.SF_BATTLE)
                result = True
            self.__curCtrl.setForcedGuiControlMode(detached)
        elif detached:
            self.appLoader.syncCursor(settings.APP_NAME_SPACE.SF_BATTLE, flags=flags)
        return result

    def updateShootingStatus(self, canShoot):
        return None if self.__isDetached else self.__curCtrl.updateShootingStatus(canShoot)

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        return None if self.__isDetached else self.__curCtrl.getDesiredShotPoint(ignoreAimingMode)

    def getMarkerPoint(self):
        point = None
        if self.__ctrlModeName in (_CTRL_MODE.ARCADE, _CTRL_MODE.STRATEGIC, _CTRL_MODE.ARTY):
            AimingSystems.shootInSkyPoint.has_been_called = False
            point = self.getDesiredShotPoint(ignoreAimingMode=True)
            if AimingSystems.shootInSkyPoint.has_been_called:
                point = None
        return point

    def showClientGunMarkers(self, isShown):
        self.__curCtrl.setGunMarkerFlag(isShown, _GUN_MARKER_FLAG.CLIENT_MODE_ENABLED)

    def showServerGunMarker(self, isShown):
        if not BattleReplay.isPlaying():
            BattleReplay.g_replayCtrl.setUseServerAim(isShown)
            self.__curCtrl.setGunMarkerFlag(isShown, _GUN_MARKER_FLAG.SERVER_MODE_ENABLED)
            if gun_marker_ctrl.useDefaultGunMarkers():
                self.__curCtrl.setGunMarkerFlag(not isShown, _GUN_MARKER_FLAG.CLIENT_MODE_ENABLED)

    def updateClientGunMarker(self, pos, direction, size, sizeOffset, relaxTime, collData):
        self.__curCtrl.updateGunMarker(_GUN_MARKER_TYPE.CLIENT, pos, direction, size, sizeOffset, relaxTime, collData)

    def updateServerGunMarker(self, pos, direction, size, sizeOffset, relaxTime, collData):
        self.__curCtrl.updateGunMarker(_GUN_MARKER_TYPE.SERVER, pos, direction, size, sizeOffset, relaxTime, collData)

    def updateDualAccGunMarker(self, pos, direction, size, sizeOffset, relaxTime, collData):
        self.__curCtrl.updateGunMarker(_GUN_MARKER_TYPE.DUAL_ACC, pos, direction, size, sizeOffset, relaxTime, collData)

    def setAimingMode(self, enable, mode):
        self.__curCtrl.setAimingMode(enable, mode)

    def getAimingMode(self, mode):
        return self.__curCtrl.getAimingMode(mode)

    def setAutorotation(self, bValue, triggeredByKey=False):
        if not self.__curCtrl.enableSwitchAutorotationMode(triggeredByKey):
            return
        elif not BigWorld.player().isOnArena:
            return
        else:
            if self.__isAutorotation != bValue:
                self.__isAutorotation = bValue
                BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation, triggeredByKey)
                self.__curCtrl.onAutorotationChanged(bValue)
            self.__prevModeAutorotation = None
            return

    def getAutorotation(self):
        return self.__isAutorotation

    def switchAutorotation(self, triggeredByKey=False):
        self.setAutorotation(not self.__isAutorotation, triggeredByKey)

    def activatePostmortem(self):
        if self.siegeModeSoundNotifications is not None:
            self.siegeModeSoundNotifications.stop()
            self.siegeModeControl.onSiegeStateChanged -= self.siegeModeSoundNotifications.onSiegeStateChanged
            self.siegeModeSoundNotifications = None
        avatar = BigWorld.player()
        avatar.autoAim(None)
        for ctlMode in self.__ctrls.itervalues():
            ctlMode.resetAimingMode()

        params = self.__curCtrl.postmortemCamParams if hasattr(self.__curCtrl, 'postmortemCamParams') else None
        battleReplayInProgress = BattleReplay.g_replayCtrl.isTimeWarpInProgress
        nextCtrlMode = avatar.getNextControlMode()
        if battleReplayInProgress or avatar.isObserver() or nextCtrlMode == _CTRL_MODE.POSTMORTEM:
            self.onControlModeChanged(_CTRL_MODE.POSTMORTEM, postmortemParams=params, bPostmortemDelay=True, newVehicleID=BigWorld.player().playerVehicleID)
        elif nextCtrlMode in _CTRL_MODE.KILL_CAM_MODES:
            self.onControlModeChanged(nextCtrlMode, postmortemParams=params, bPostmortemDelay=True)
        else:
            _logger.error('Attempt to go to an unsupported CTRL Mode %s', nextCtrlMode)
        return

    def movingToRespawnBase(self):
        if self.ctrlModeName in _CTRL_MODE.POSTMORTEM_CONTROL_MODES:
            self.onControlModeChanged(_CTRL_MODE.RESPAWN_DEATH)
            respMode = self.__ctrls[_CTRL_MODE.RESPAWN_DEATH]
            respMode.camera.setToVehicleDirection()

    def deactivatePostmortem(self):
        if self.ctrlModeName not in _CTRL_MODE.POSTMORTEM_CONTROL_MODES:
            _logger.warning('Trying to deactivate postmortem when it is not active. Current mode: %s', self.ctrlModeName)
            return
        self.onControlModeChanged('arcade')
        arcadeMode = self.__ctrls['arcade']
        arcadeMode.camera.setToVehicleDirection()
        self.__identifyVehicleType()
        self.__constructComponents()

    def setKillerVehicleID(self, killerVehicleID, deathReasonID=None):
        self.__killerVehicleID = killerVehicleID
        self.__deathReasonID = deathReasonID
        self.onReceivedKillerID(self.__killerVehicleID)

    def getKillerVehicleID(self):
        return self.__killerVehicleID

    def getDeathReason(self):
        return self.__deathReasonID

    def start(self):
        self.__setInitialControlMode()
        g_guiResetters.add(self.__onRecreateDevice)
        self.__identifyVehicleType()
        self.__constructComponents()
        for control in self.__ctrls.itervalues():
            control.create()

        avatar = BigWorld.player()
        if not self.__curCtrl.isManualBind():
            avatar.positionControl.bindToVehicle(True)
        self.__curCtrl.enable()
        tmp = self.__curCtrl.getPreferredAutorotationMode()
        if tmp is not None:
            self.__isAutorotation = tmp
            self.__prevModeAutorotation = True
        else:
            self.__isAutorotation = True
            self.__prevModeAutorotation = None
        avatar.enableOwnVehicleAutorotation(self.__isAutorotation)
        self.__targeting.enable(True)
        self.__isStarted = True
        self.__isGUIVisible = True
        self.__killerVehicleID = None
        self.__deathReasonID = None
        arena = avatar.arena
        arena.onPeriodChange += self.__onArenaStarted
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        avatar.consistentMatrices.onVehicleMatrixBindingChanged += self.__onVehicleMatrixBindingChanged
        self.__onArenaStarted(arena.period)
        if not avatar.isObserver() and arena.hasObservers:
            self.__remoteCameraSender = RemoteCameraSender(self)
        self.onCameraChanged('arcade')
        return

    def stop(self):
        self.__isStarted = False
        import SoundGroups
        SoundGroups.g_instance.changePlayMode(0)
        aih_global_binding.clear()
        for control in self.__ctrls.itervalues():
            control.destroy()

        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setPlayerVehicleID(0)
        if self.__remoteCameraSender is not None:
            self.__remoteCameraSender.destroy()
            self.__remoteCameraSender = None
        self.onCameraChanged.clear()
        self.onCameraChanged = None
        self.onPostmortemKillerVisionEnter.clear()
        self.onPostmortemKillerVisionEnter = None
        self.onPostmortemKillerVisionExit.clear()
        self.onPostmortemKillerVisionExit = None
        self.__targeting.enable(False)
        self.__killerVehicleID = None
        self.__deathReasonID = None
        if self.siegeModeSoundNotifications is not None:
            self.siegeModeSoundNotifications.stop()
            self.siegeModeSoundNotifications = None
        if self.__onRecreateDevice in g_guiResetters:
            g_guiResetters.remove(self.__onRecreateDevice)
        BigWorld.player().arena.onPeriodChange -= self.__onArenaStarted
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged -= self.__onVehicleMatrixBindingChanged
        ScriptGameObject.destroy(self)
        CallbackDelayer.destroy(self)
        return

    def __onVehicleMatrixBindingChanged(self, isStatic):
        self.__identifyVehicleType()
        self.__constructComponents()
        if self.__pendingModeSwitch:
            player = BigWorld.player()
            ownVehicle = BigWorld.entity(player.playerVehicleID)
            vehicle = player.getVehicleAttached()
            if vehicle != ownVehicle:
                pendingMode, args = self.__pendingModeSwitch
                self.onControlModeChanged(pendingMode, *args)

    def setObservedVehicle(self, vehicleID):
        for control in self.__ctrls.itervalues():
            control.setObservedVehicle(vehicleID)

    @disableShotPointCache
    def onControlModeChanged(self, eMode, **kwargs):
        _logger.debug('onControlModeChanged %s', eMode)
        if not self.__isArenaStarted and not self.__isModeSwitchInPrebattlePossible(eMode):
            return
        else:
            player = BigWorld.player()
            isObserverMode = 'observer' in player.vehicleTypeDescriptor.type.tags if player is not None else True
            self.__pendingModeSwitch = None
            if not isObserverMode and self.__isDualGun:
                gui_event_dispatcher.controlModeChange(eMode)
            if not player.observerSeesAll():
                if isObserverMode and eMode == _CTRL_MODE.POSTMORTEM:
                    if self.__observerVehicle is not None:
                        player.positionControl.followCamera(False)
                        player.positionControl.bindToVehicle(True, self.__observerVehicle)
                        if player.playerVehicleID == player.getVehicleAttached().id:
                            self.__pendingModeSwitch = (eMode, kwargs)
                            return
            if isObserverMode and self.__ctrlModeName == _CTRL_MODE.POSTMORTEM:
                if player.observedVehicleID and player.observedVehicleID != player.playerVehicleID:
                    self.__observerVehicle = player.observedVehicleID
                else:
                    self.__observerVehicle = None
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setControlMode(eMode)
            self.__curCtrl.disable()
            prevCtrl = self.__curCtrl
            prevCtrlModeName = self.__ctrlModeName
            self.__curCtrl = self.__ctrls[eMode]
            self.__ctrlModeName = eMode
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.CTRL_MODE_CHANGE, currentMode=self.__ctrlModeName, previousMode=prevCtrlModeName)
            if player is not None:
                if player.observerSeesAll():
                    if prevCtrlModeName == _CTRL_MODE.VIDEO:
                        player.positionControl.followCamera(False)
                        player.positionControl.bindToVehicle(True, self.__observerVehicle)
                    if eMode == _CTRL_MODE.VIDEO:
                        self.__observerVehicle = player.observedVehicleID
                        player.positionControl.bindToVehicle(True)
                elif not prevCtrl.isManualBind() and self.__curCtrl.isManualBind():
                    if replayCtrl.isServerSideReplay:
                        pass
                    elif isObserverMode:
                        player.positionControl.bindToVehicle(False, -1)
                    else:
                        player.positionControl.bindToVehicle(False)
                elif prevCtrl.isManualBind() and not self.__curCtrl.isManualBind():
                    if replayCtrl.isServerSideReplay:
                        pass
                    elif isObserverMode:
                        player.positionControl.followCamera(False)
                        player.positionControl.bindToVehicle(True, self.__observerVehicle)
                    else:
                        player.positionControl.bindToVehicle(True)
                newAutoRotationMode = self.__curCtrl.getPreferredAutorotationMode()
                if newAutoRotationMode is not None:
                    if prevCtrl.getPreferredAutorotationMode() is None:
                        self.__prevModeAutorotation = self.__isAutorotation
                    if self.__isAutorotation != newAutoRotationMode:
                        self.__isAutorotation = newAutoRotationMode
                        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
                elif prevCtrl.getPreferredAutorotationMode() is not None:
                    if self.__prevModeAutorotation is None:
                        self.__prevModeAutorotation = True
                    if self.__isAutorotation != self.__prevModeAutorotation:
                        self.__isAutorotation = self.__prevModeAutorotation
                        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
                    self.__prevModeAutorotation = None
                if not isObserverMode and self.__ctrlModeName in (_CTRL_MODE.ARCADE, _CTRL_MODE.SNIPER):
                    lockEnabled = prevCtrl.getAimingMode(AIMING_MODE.TARGET_LOCK)
                    self.__curCtrl.setAimingMode(lockEnabled, AIMING_MODE.TARGET_LOCK)
            self.__targeting.onRecreateDevice()
            self.__curCtrl.setGUIVisible(self.__isGUIVisible)
            if isObserverMode:
                kwargs.update(vehicleID=self.__observerVehicle)
            if eMode in _CTRL_MODE.KILL_CAM_MODES and hasattr(prevCtrl, 'camera'):
                kwargs.update(previousCam=prevCtrl.camera)
            self.__curCtrl.enable(**kwargs)
            isReplayPlaying = replayCtrl.isPlaying
            self.notifyCameraChanged()
            vehicle = player.getVehicleAttached()
            if not isReplayPlaying and vehicle is not None and not vehicle.isUpgrading:
                self.__curCtrl.handleMouseEvent(0.0, 0.0, 0.0)
            if vehicle is not None and vehicle.appearance is not None:
                vehicle.appearance.removeComponentByType(GenericComponents.ControlModeStatus)
                vehicle.appearance.createComponent(GenericComponents.ControlModeStatus, _CTRL_MODES.index(eMode))
            player.entityGameObject.removeComponentByType(GenericComponents.ControlModeStatus)
            player.entityGameObject.createComponent(GenericComponents.ControlModeStatus, _CTRL_MODES.index(self.__ctrlModeName))
            BigWorld.setEdgeDrawerRenderMode(1 if eMode in aih_constants.MAP_CASE_MODES else 0)
            return

    def onObserverControlModeChanged(self, eMode):
        _logger.debug('onObserverControlModeChanged: %s %s ', eMode, self.isObserverFPV)
        if not self.isObserverFPV:
            self.onControlModeChanged(_CTRL_MODE.POSTMORTEM)
            return
        elif eMode in MAP_CASE_MODES:
            return
        else:
            targetPos = self.getDesiredShotPoint() or Math.Vector3(0, 0, 0)
            _logger.debug('onObserverControlModeChanged: %s %s', eMode, targetPos)
            vehicle = BigWorld.player().getVehicleAttached()
            self.onControlModeChanged(eMode, preferredPos=targetPos, aimingMode=0, saveZoom=False, saveDist=True, equipmentID=None, curVehicleID=vehicle.id if vehicle is not None else BigWorld.player().playerVehicleID)
            return

    def getTargeting(self):
        return self.__targeting

    def setGUIVisible(self, isVisible):
        self.__isGUIVisible = isVisible
        self.__curCtrl.setGUIVisible(isVisible)

    def selectPlayer(self, vehId):
        self.__curCtrl.selectPlayer(vehId)

    def onMinimapClicked(self, worldPos):
        return self.__curCtrl.onMinimapClicked(worldPos)

    def onVehicleShaken(self, vehicle, shakeReason, impulsePosition, impulseDir, caliber, sensitivity=1.0):
        if shakeReason == _ShakeReason.OWN_SHOT_DELAYED:
            shakeFuncBound = functools.partial(self.onVehicleShaken, vehicle, _ShakeReason.OWN_SHOT, impulsePosition, impulseDir, caliber, sensitivity)
            delayTime = self.__dynamicCameraSettings.settings['ownShotImpulseDelay']
            self.delayCallback(delayTime, shakeFuncBound)
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            impulseValue = self.__dynamicCameraSettings.getGunImpulse(caliber) * sensitivity
            vehicleSensitivity = 0.0
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None or not avatarVehicle.isAlive():
                return
            avatarVehicleTypeDesc = getattr(avatarVehicle, 'typeDescriptor', None)
            if avatarVehicleTypeDesc is not None:
                avatarVehWeightTons = avatarVehicleTypeDesc.physics['weight'] / 1000.0
                vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehWeightTons)
                vehicleSensitivity *= avatarVehicleTypeDesc.hull.swinging.sensitivityToImpulse
            impulseReason = None
            isDistant = False
            if shakeReason == _ShakeReason.OWN_SHOT:
                if vehicle is avatarVehicle:
                    impulseReason = cameras.ImpulseReason.MY_SHOT
                    isDistant = False
                else:
                    impulseReason = cameras.ImpulseReason.OTHER_SHOT
                    isDistant = True
            elif vehicle is avatarVehicle:
                if shakeReason == _ShakeReason.HIT or shakeReason == _ShakeReason.HIT_NO_DAMAGE:
                    impulseValue *= 1.0 if shakeReason == _ShakeReason.HIT else self.__dynamicCameraSettings.settings['zeroDamageHitSensitivity']
                    impulseReason = cameras.ImpulseReason.ME_HIT
                    isDistant = False
                else:
                    impulseReason = cameras.ImpulseReason.SPLASH
                    isDistant = True
            impulseDir, impulseValue = self.__adjustImpulse(impulseDir, impulseValue, camera, impulsePosition, vehicleSensitivity, impulseReason)
            if isDistant:
                camera.applyDistantImpulse(impulsePosition, impulseValue, impulseReason)
            else:
                camera.applyImpulse(impulsePosition, impulseDir * impulseValue, impulseReason)
            return

    def onVehicleCollision(self, vehicle, impactVelocity):
        if impactVelocity < self.__dynamicCameraSettings.settings['minCollisionSpeed']:
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None or not avatarVehicle.isAlive():
                return
            if vehicle is avatarVehicle:
                impulse = Math.Vector3(0, impactVelocity * self.__dynamicCameraSettings.settings['collisionSpeedToImpulseRatio'], 0)
                camera.applyImpulse(vehicle.position, impulse, cameras.ImpulseReason.COLLISION)
            return

    def onVehicleDeath(self, vehicle, exploded):
        if not exploded:
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None or avatarVehicle is vehicle:
                return
            caliber = vehicle.typeDescriptor.shot.shell.caliber
            impulseValue = self.__dynamicCameraSettings.getGunImpulse(caliber)
            avatarVehicleWeightInTons = avatarVehicle.typeDescriptor.physics['weight'] / 1000.0
            vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehicleWeightInTons)
            vehicleSensitivity *= avatarVehicle.typeDescriptor.hull.swinging.sensitivityToImpulse
            _, impulseValue = self.__adjustImpulse(Math.Vector3(0, 0, 0), impulseValue, camera, vehicle.position, vehicleSensitivity, cameras.ImpulseReason.VEHICLE_EXPLOSION)
            camera.applyDistantImpulse(vehicle.position, impulseValue, cameras.ImpulseReason.VEHICLE_EXPLOSION)
            return

    def onExplosionImpulse(self, position, impulseValue):
        camera = getattr(self.ctrl, 'camera', None)
        if camera is None:
            return
        else:
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None:
                return
            avatarVehicleWeightInTons = avatarVehicle.typeDescriptor.physics['weight'] / 1000.0
            vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehicleWeightInTons)
            vehicleSensitivity *= avatarVehicle.typeDescriptor.hull.swinging.sensitivityToImpulse
            _, impulseValue = self.__adjustImpulse(Math.Vector3(0, 0, 0), impulseValue, camera, position, vehicleSensitivity, cameras.ImpulseReason.HE_EXPLOSION)
            camera.applyDistantImpulse(position, impulseValue, cameras.ImpulseReason.HE_EXPLOSION)
            return

    def onProjectileHit(self, position, caliber, sensitivity, isOwnShot):
        if not isOwnShot:
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            impulseValue = self.__dynamicCameraSettings.getGunImpulse(caliber) * sensitivity
            vehicleSensitivity = 1.0
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is not None:
                avatarVehicleWeightInTons = avatarVehicle.typeDescriptor.physics['weight'] / 1000.0
                vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehicleWeightInTons)
                vehicleSensitivity *= avatarVehicle.typeDescriptor.hull.swinging.sensitivityToImpulse
            _, impulseValue = self.__adjustImpulse(Math.Vector3(0, 0, 0), impulseValue, camera, position, vehicleSensitivity, cameras.ImpulseReason.VEHICLE_EXPLOSION)
            camera.applyDistantImpulse(position, impulseValue, cameras.ImpulseReason.PROJECTILE_HIT)
            return

    def onSpecificImpulse(self, position, impulse, specificCtrl=None):
        if specificCtrl is None:
            camera = getattr(self.ctrl, 'camera', None)
        else:
            camera = self.ctrls[specificCtrl].camera
        if camera is None:
            return
        else:
            camera.applyImpulse(position, impulse, cameras.ImpulseReason.MY_SHOT)
            return

    def notifyCameraChanged(self):
        player = BigWorld.player()
        isObserverMode = 'observer' in player.vehicleTypeDescriptor.type.tags if player is not None else True
        vehicleID = None
        if isObserverMode:
            if self.__observerVehicle is not None:
                vehicleID = self.__observerVehicle
            elif player.observedVehicleID and player.observedVehicleID != player.playerVehicleID:
                vehicleID = player.observedVehicleID
        else:
            vehicle = player.getVehicleAttached()
            if vehicle is not None and BattleReplay.g_replayCtrl.isPlaying:
                vehicleID = vehicle.id
        self.onCameraChanged(self.__ctrlModeName, vehicleID)
        return

    def __adjustImpulse(self, impulseDir, impulseValue, camera, impulsePosition, vehicleSensitivity, impulseReason):
        if impulseReason in camera.getReasonsAffectCameraDirectly():
            dirToCamera = camera.camera.position - impulsePosition
            dirToCamera.normalise()
            impulseDir = dirToCamera
        else:
            impulseValue *= vehicleSensitivity
        return (impulseDir, impulseValue)

    def __identifyVehicleType(self):
        avatar = BigWorld.player()
        magnetAimTags = avatar.magneticAutoAimTags
        veh = BigWorld.entity(avatar.playerVehicleID)
        if veh is None:
            return
        else:
            vehTypeDesc = veh.typeDescriptor.type
            self.__isSPG = 'SPG' in vehTypeDesc.tags
            self.__isATSPG = 'AT-SPG' in vehTypeDesc.tags
            self.__isDualGun = veh.typeDescriptor.isDualgunVehicle
            self.__isTwinGun = veh.typeDescriptor.isTwinGunVehicle
            self.__isMagnetAimEnabled = bool(magnetAimTags & vehTypeDesc.tags)
            return

    def reloadDynamicSettings(self):
        if not constants.HAS_DEV_RESOURCES:
            return
        ResMgr.purge(INPUT_HANDLER_CFG)
        sec = ResMgr.openSection(INPUT_HANDLER_CFG)
        self.__dynamicCameraSettings = DynamicCameraSettings(sec['dynamicCameraCommon'])
        try:
            self.__ctrls['sniper'].camera.aimingSystem.reloadConfig(sec['sniperMode']['camera'])
        except Exception:
            pass

    def _readCfg(self):
        sec = ResMgr.openSection(INPUT_HANDLER_CFG)
        if sec is None:
            _logger.error('can not open <%s>.', INPUT_HANDLER_CFG)
            return
        else:
            self.__checkSections(sec)
            keySec = sec['keys']
            if keySec is not None:
                self.__showMarkersKey = getattr(Keys, keySec.readString('showMarkersKey', ''), None)
                self.__alwaysShowAimKey = getattr(Keys, keySec.readString('alwaysShowAimKey', ''), None)
            self.__dynamicCameraSettings = DynamicCameraSettings(sec['dynamicCameraCommon'])
            return sec

    def __setupCtrls(self, section):
        bonusType = BigWorld.player().arenaBonusType
        bonusTypeCtrlsMap = OVERWRITE_CTRLS_DESC_MAP.get(bonusType, {})
        for name, desc in _CTRLS_DESC_MAP.items():
            if name in bonusTypeCtrlsMap:
                desc = bonusTypeCtrlsMap[name]
            try:
                classType, modeName, ctrlType = desc
                if ctrlType != _CTRL_TYPE.DEVELOPMENT or ctrlType == _CTRL_TYPE.DEVELOPMENT and constants.HAS_DEV_RESOURCES:
                    if name not in self.__ctrls:
                        self.__ctrls[name] = classType(section[modeName] if modeName else None, self)
                    else:
                        _logger.warning('Control "%s" is already added to the list! Please check OVERWRITE_CTRLS_DESC_MAP. %s is skipped!', name, classType)
            except Exception:
                _logger.error('Error while setting ctrls %s %s %s', name, desc, constants.HAS_DEV_RESOURCES)
                LOG_CURRENT_EXCEPTION()

        return

    def __checkSections(self, section):
        for _, desc in _CTRLS_DESC_MAP.items():
            if desc[1] is None or desc[2] == _CTRL_TYPE.OPTIONAL or desc[2] == _CTRL_TYPE.DEVELOPMENT and not constants.HAS_DEV_RESOURCES:
                continue
            if not section.has_key(desc[1]):
                _logger.error('Invalid section <%s> in <%s>.', desc[1], INPUT_HANDLER_CFG)

        return

    def __onArenaStarted(self, period, *args):
        self.__isArenaStarted = period == ARENA_PERIOD.BATTLE
        self.__curCtrl.setGunMarkerFlag(self.__isArenaStarted, _GUN_MARKER_FLAG.CONTROL_ENABLED)
        self.showServerGunMarker(gun_marker_ctrl.useServerGunMarker())
        self.showClientGunMarkers(gun_marker_ctrl.useClientGunMarker())

    def __onRecreateDevice(self):
        self.__curCtrl.onRecreateDevice()
        self.__targeting.onRecreateDevice()

    def __onSettingsChanged(self, diff):
        if 'dynamicCamera' in diff or 'horStabilizationSnp' in diff:
            dynamicCamera = self.settingsCore.getSetting('dynamicCamera')
            horStabilizationSnp = self.settingsCore.getSetting('horStabilizationSnp')
            self.enableDynamicCamera(dynamicCamera, horStabilizationSnp)
        if 'hullLockEnabled' in diff:
            hullLock = self.settingsCore.getSetting('hullLockEnabled')
            self.enableHullLock(hullLock)

    def isControlModeChangeAllowed(self):
        player = BigWorld.player()
        if not self.isAllowToSwitchPositionOrFPV():
            return False
        if not player.observerSeesAll():
            return True
        if BigWorld.time() - self.__lastSwitchTime < _CONTROL_MODE_SWITCH_COOLDOWN:
            _logger.warning('Control mode switch is on cooldown')
            return False
        self.__lastSwitchTime = BigWorld.time()
        return True

    @classmethod
    def isAllowToSwitchPositionOrFPV(cls):
        player = BigWorld.player()
        return not player.positionControl.isSwitching and not player.isFPVModeSwitching

    def __setInitialControlMode(self):
        if BigWorld.player().arena.period < ARENA_PERIOD.BATTLE:
            arenaBonusType = BigWorld.player().arenaBonusType
            initialControlMode = _INITIAL_MODE_BY_BONUS_TYPE.get(arenaBonusType, _CTRLS_FIRST)
        else:
            initialControlMode = _CTRLS_FIRST
        self.__curCtrl = self.__ctrls[initialControlMode]
        self.__ctrlModeName = initialControlMode

    def __isModeSwitchInPrebattlePossible(self, eMode):
        if eMode in (_CTRL_MODE.POSTMORTEM, _CTRL_MODE.KILL_CAM, _CTRL_MODE.LOOK_AT_KILLER):
            return True
        return True if self.__ctrlModeName == _CTRL_MODE.VEHICLES_SELECTION and eMode == _CTRL_MODE.ARCADE else False


class _Targeting(object):

    def __init__(self):
        target = BigWorld.target
        target.selectionFovDegrees = 1.0
        target.deselectionFovDegrees = 80.0
        target.maxDistance = 710.0
        target.skeletonCheckEnabled = True
        BigWorld.target.isEnabled = False
        self.__mouseMatProv = BigWorld.MouseTargetingMatrix()

    def isEnabled(self):
        return BigWorld.target.isEnabled

    def getTargetEntity(self):
        return BigWorld.target.entity

    def enable(self, flag):
        if flag and not BigWorld.target.isEnabled:
            player = BigWorld.player()
            player.targetBlur(player.target)
            BigWorld.target.isEnabled = True
            BigWorld.target.source = self.__mouseMatProv
        elif not flag:
            BigWorld.target.isEnabled = False
            BigWorld.target.clear()
            BigWorld.target.source = None
        return

    def onRecreateDevice(self):
        if BigWorld.target.isEnabled:
            BigWorld.target.clear()

    def detach(self, value):
        self.__mouseMatProv.detach(value)


class _VertScreenshotCamera(object):
    isEnabled = property(lambda self: self.__isEnabled)

    def __init__(self):
        super(_VertScreenshotCamera, self).__init__()
        self.__isEnabled = False
        self.__savedCamera = None
        self.__savedWatchers = {}
        self.__nearPlane = 0.0
        self.__farPlane = 0.0
        self.__watcherNames = ('Render/Fov', 'Render/Near Plane', 'Render/Far Plane', 'Render/Objects Far Plane/Enabled', 'Render/Shadows/qualityPreset', 'Visibility/Draw tanks', 'Visibility/Control Points', 'Visibility/GUI', 'Visibility/particles', 'Visibility/Sky', 'Client Settings/Script tick', 'Render/Terrain/AdaptiveMesh/cascades enabled', 'Render/Water/out land water')
        return

    def destroy(self):
        self.enable(False)

    def enable(self, doEnable):
        if self.__isEnabled == doEnable:
            return
        from cameras import FovExtended
        if not doEnable:
            self.__isEnabled = False
            BigWorld.camera(self.__savedCamera)
            BigWorld.wg_enableSuperShot(False, False)
            for k, v in self.__savedWatchers.iteritems():
                BigWorld.setWatcher(k, v)

            FovExtended.instance().enabled = True
            BigWorld.projection().nearPlane = self.__nearPlane
            BigWorld.projection().farPlane = self.__farPlane
            BigWorld.setWatcher('Render/Fog/enabled', True)
            BigWorld.setWatcher('Occlusion Culling/Enabled', True)
            BigWorld.setWatcher('Render/Terrain/AdaptiveMesh/cascades enabled', True)
            BigWorld.setWatcher('Render/Water/out land water', True)
            _logger.debug('Vertical screenshot camera is disabled')
            return
        self.__isEnabled = True
        self.__savedCamera = BigWorld.camera()
        FovExtended.instance().enabled = False
        arenaBB = BigWorld.player().arena.arenaType.spaceBoundingBox
        centerXZ = Math.Vector2(0.5 * (arenaBB[0][0] + arenaBB[1][0]), 0.5 * (arenaBB[0][1] + arenaBB[1][1]))
        halfSizesXZ = Math.Vector2(0.5 * (arenaBB[1][0] - arenaBB[0][0]), 0.5 * (arenaBB[1][1] - arenaBB[0][1]))
        camFov = math.radians(15.0)
        camPos = Math.Vector3(centerXZ.x, 0, centerXZ.y)
        aspectRatio = BigWorld.getAspectRatio()
        camPos.y = max(halfSizesXZ.x / math.sin(0.5 * camFov * aspectRatio), halfSizesXZ.y / math.sin(0.5 * camFov))
        camMatr = Math.Matrix()
        camMatr.setRotateYPR(Math.Vector3(0.0, math.pi * 0.5, 0.0))
        camMatr.translation = camPos
        camMatr.invert()
        self.__cam = BigWorld.FreeCamera()
        self.__cam.set(camMatr)
        BigWorld.camera(self.__cam)
        BigWorld.wg_enableSuperShot(True, False)
        self.__savedWatchers = {}
        for name in self.__watcherNames:
            try:
                self.__savedWatchers[name] = BigWorld.getWatcher(name)
                if name.startswith('Visibility'):
                    BigWorld.setWatcher(name, False)
            except TypeError:
                _logger.warning('Failed to get/set watcher %s', name)

        self.__nearPlane = BigWorld.projection().nearPlane
        self.__farPlane = BigWorld.projection().farPlane
        BigWorld.setWatcher('Render/Fog/enabled', False)
        BigWorld.projection().fov = camFov
        BigWorld.projection().nearPlane = max(0.1, camPos.y - 1000.0)
        BigWorld.projection().farPlane = camPos.y + 1000
        BigWorld.setWatcher('Render/Shadows/qualityPreset', 4)
        BigWorld.setWatcher('Client Settings/Script tick', False)
        BigWorld.setWatcher('Occlusion Culling/Enabled', False)
        BigWorld.setWatcher('Render/Terrain/AdaptiveMesh/cascades enabled', False)
        BigWorld.setWatcher('Render/Water/out land water', False)
        _logger.debug('Vertical screenshot camera is enabled')
