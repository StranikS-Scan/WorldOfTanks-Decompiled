# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/plugins.py
import logging
import BigWorld
import typing
from battle_royale.gui.battle_control.controllers.radar_ctrl import IRadarListener
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import TRAJECTORY_VIEW_HINT_SECTION, PRE_BATTLE_HINT_SECTION, QUEST_PROGRESS_HINT_SECTION, HELP_SCREEN_HINT_SECTION, SIEGE_HINT_SECTION, WHEELED_MODE_HINT_SECTION, HINTS_LEFT, NUM_BATTLES, LAST_DISPLAY_DAY, IBC_HINT_SECTION, DEV_MAPS_HINT_SECTION, RADAR_HINT_SECTION, TURBO_SHAFT_ENGINE_MODE_HINT_SECTION, PRE_BATTLE_ROLE_HINT_SECTION, COMMANDER_CAM_HINT_SECTION, ROCKET_ACCELERATION_MODE_HINT_SECTION, RESERVES_HINT_SECTION, MAPBOX_HINT_SECTION, ASSAULT_CAMERA_HINT_SECTION
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from aih_constants import CTRL_MODE_NAME
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE, ARENA_PERIOD, ARENA_GUI_TYPE, ROLE_TYPE, ROCKET_ACCELERATION_STATE
from debug_utils import LOG_DEBUG
from dyn_squad_hint_plugin import DynSquadHintPlugin
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.hint_panel.hint_panel_plugin import HelpHintContext
from gui.Scaleform.daapi.view.battle.shared.hint_panel.crosshair_hint_plugin import AbstractCrosshairHintPlugin
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent, ViewEventType, LoadViewEvent
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from hint_panel_plugin import HintPanelPlugin, HintData, HintPriority, HINT_TIMEOUT
from items import makeIntCompactDescrByID
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.goodies import IBoostersStateProvider
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.goodies.booster_state_provider import BoosterStateProvider
    from items.vehicles import VehicleDescriptor
_logger = logging.getLogger(__name__)
_HINT_MIN_VEHICLE_LEVEL = 4
_HINT_COOLDOWN = 4
_TRAJECTORY_VIEW_HINT_POSITION = (0, 120)
BEFORE_START_BATTLE_PERIODS = (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.WAITING)

def createPlugins():
    result = {}
    if TrajectoryViewHintPlugin.isSuitable():
        result['trajectoryViewHint'] = TrajectoryViewHintPlugin
    if AssaultCameraHintPlugin.isSuitable():
        result['assaultCameraHint'] = AssaultCameraHintPlugin
    if SiegeIndicatorHintPlugin.isSuitable():
        result['siegeIndicatorHint'] = SiegeIndicatorHintPlugin
    if PreBattleHintPlugin.isSuitable():
        result['prebattleHints'] = PreBattleHintPlugin
    if RadarHintPlugin.isSuitable():
        result['radarHint'] = RadarHintPlugin
    if DynSquadHintPlugin.isSuitable():
        result['dynSquadHints'] = DynSquadHintPlugin
    if RoleHelpPlugin.isSuitable():
        result['prebattleRoleHint'] = RoleHelpPlugin
    if CommanderCameraHintPlugin.isSuitable():
        result['commanderCameraHints'] = CommanderCameraHintPlugin
    if MapsTrainingHelpHintPlugin.isSuitable():
        result['mapsTrainingHelpHint'] = MapsTrainingHelpHintPlugin
    if MapboxHelpPlugin.isSuitable():
        result['mapboxHelpHint'] = MapboxHelpPlugin
    if DevMapsHintPlugin.isSuitable():
        result['devMapsHelpHint'] = DevMapsHintPlugin
    return result


class PRBSettings(object):
    HELP_IDX = 0
    QUEST_IDX = 1
    HINT_DAY_COOLDOWN = 30
    HINT_BATTLES_COOLDOWN = 100


class TrajectoryViewHintPlugin(AbstractCrosshairHintPlugin):
    __slots__ = ()
    _HINT_DAY_COOLDOWN = 30
    _HINT_BATTLES_COOLDOWN = 10
    _SETTINGS_NAME = TRAJECTORY_VIEW_HINT_SECTION
    _CMD_NAME = CommandMapping.CMD_CM_TRAJECTORY_VIEW

    def start(self):
        super(TrajectoryViewHintPlugin, self).start()
        self._updateCounterOnStart(self._settings, self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)

    def _setup(self, crosshairCtrl, vehicleCtrl):
        self.__onStrategicCameraChanged(crosshairCtrl.getStrategicCameraID())

    def _addListeners(self):
        super(TrajectoryViewHintPlugin, self)._addListeners()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onStrategicCameraChanged += self.__onStrategicCameraChanged
        return

    def _removeListeners(self):
        super(TrajectoryViewHintPlugin, self)._removeListeners()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onStrategicCameraChanged -= self.__onStrategicCameraChanged
        return

    def _getHint(self):
        hintTextLeft = ''
        keyName = getReadableKey(self._CMD_NAME)
        key = getVirtualKey(self._CMD_NAME)
        if keyName:
            hintTextLeft = backport.text(R.strings.ingame_gui.trajectoryView.hint.alternateModeLeft())
            hintTextRight = backport.text(R.strings.ingame_gui.trajectoryView.hint.alternateModeRight())
        else:
            hintTextRight = backport.text(R.strings.ingame_gui.trajectoryView.hint.noBindingKey())
        return HintData(key, keyName, hintTextLeft, hintTextRight, offsetX=_TRAJECTORY_VIEW_HINT_POSITION[0], offsetY=_TRAJECTORY_VIEW_HINT_POSITION[1], priority=HintPriority.TRAJECTORY, reducedPanning=False, hintCtx=None, centeredMessage=False)

    def _removeHint(self):
        super(TrajectoryViewHintPlugin, self)._removeHint()
        self.stop()

    def _canShowHint(self, viewID):
        return super(TrajectoryViewHintPlugin, self)._canShowHint(viewID) and GUI_SETTINGS.spgAlternativeAimingCameraEnabled and viewID == CROSSHAIR_VIEW_ID.STRATEGIC and self.sessionProvider.shared.crosshair.getCtrlMode() != CTRL_MODE_NAME.SPG_ONLY_ARTY_MODE

    def __onStrategicCameraChanged(self, _):
        cmdMap = CommandMapping.g_instance
        isUserRequested = cmdMap is not None and cmdMap.isActive(self._CMD_NAME)
        if isUserRequested:
            self._updateCounterOnUsed(self._settings)
        if isUserRequested and self._isHintShown:
            self._removeHint()
        return


class AssaultCameraHintPlugin(AbstractCrosshairHintPlugin):
    _SETTINGS_NAME = ASSAULT_CAMERA_HINT_SECTION
    _CMD_NAME = CommandMapping.CMD_CAMERA_ZOOM

    def _canShowHint(self, viewId):
        return viewId == CROSSHAIR_VIEW_ID.ASSAULT

    def _getHint(self):
        hintTextLeft = backport.text(R.strings.ingame_gui.camera.hint.press())
        hintTextRight = backport.text(R.strings.ingame_gui.camera.hint.wheeled())
        return HintData(getVirtualKey(self._CMD_NAME), getReadableKey(self._CMD_NAME), hintTextLeft, hintTextRight, offsetX=0, offsetY=0, priority=HintPriority.TRAJECTORY, reducedPanning=False, hintCtx=None, centeredMessage=False)

    def _addListeners(self):
        super(AssaultCameraHintPlugin, self)._addListeners()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onAssaultCameraStateChanged += self.__onAssaultCameraStateChanged
        return

    def _removeListeners(self):
        super(AssaultCameraHintPlugin, self)._removeListeners()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onAssaultCameraStateChanged -= self.__onAssaultCameraStateChanged
        return

    def __onAssaultCameraStateChanged(self, cameraState):
        if self._isHintShown:
            self._removeHint()
            self._updateBattleCounterOnUsed(self._settings)


class SiegeIndicatorHintPlugin(HintPanelPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    _HINT_DAY_COOLDOWN = 30
    _HINT_BATTLES_COOLDOWN = 10

    def __init__(self, parentObj):
        super(SiegeIndicatorHintPlugin, self).__init__(parentObj)
        self.__isEnabled = False
        self.__siegeState = _SIEGE_STATE.DISABLED
        self.__settings = {}
        self.__isHintShown = False
        self.__isInPostmortem = False
        self.__isObserver = False
        self._isInRecovery = False
        self._isInProgressCircle = False
        self._isUnderFire = False
        self.__isWheeledTech = False
        self.__hasTurboshaftEngine = False
        self.__hasHydraulicChassis = False
        self.__hasRocketAcceleration = False
        self.__isSuitableVehicle = False
        self.__period = None
        self.__isInDisplayPeriod = False
        self.__callbackDelayer = CallbackDelayer()
        self.__startCounterUpdated = False
        self.__rocketCmp = None
        return

    @classmethod
    def isSuitable(cls):
        return True

    def start(self):
        self.__startCounterUpdated = False
        vStateCtrl = self.sessionProvider.shared.vehicleState
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is not None:
            self.__isObserver = arenaDP.getVehicleInfo().isObserver()
        else:
            self.__isObserver = False
        self.__settings = {setting:AccountSettings.getSettings(setting) for setting in (SIEGE_HINT_SECTION,
         WHEELED_MODE_HINT_SECTION,
         TURBO_SHAFT_ENGINE_MODE_HINT_SECTION,
         ROCKET_ACCELERATION_MODE_HINT_SECTION)}
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vStateCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        return

    def stop(self):
        if self.__rocketCmp:
            self.__rocketCmp.unsubscribe(tryActivateCallback=self.__onTryRocketAccelerationActivate)
            self.__rocketCmp = None
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vStateCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        for name, setting in self.__settings.iteritems():
            AccountSettings.setSettings(name, setting)

        self.__callbackDelayer.destroy()
        return

    def updateMapping(self):
        if not self.__isEnabled:
            return
        self.__updateHint()

    def setPeriod(self, period):
        if period is ARENA_PERIOD.BATTLE:
            self.__isInDisplayPeriod = self.__period is not None
            if self.__isSuitableVehicle:
                self._updateCounterOnBattle(self.__getSuitableSetting())
        self.__period = period
        if self.__isEnabled:
            self.__updateHint()
        return

    def __onHintUsed(self):
        self._updateCounterOnUsed(self.__getSuitableSetting())

    def __updateHint(self):
        LOG_DEBUG('Updating siege mode: hint')
        if self.__isInPostmortem or self.__isObserver or self.sessionProvider.isReplayPlaying:
            return

        def _showHint():
            self._parentObj.setBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, self._getHint())
            self.__isHintShown = True
            self.__isInDisplayPeriod = False
            self.__callbackDelayer.delayCallback(HINT_TIMEOUT, self.__onHintTimeOut)

        isInSteadyMode = self.__siegeState not in _SIEGE_STATE.SWITCHING
        haveHintsLeft = self._haveHintsLeft(self.__getSuitableSetting())
        if isInSteadyMode and self.__isInDisplayPeriod and haveHintsLeft and not self.__areOtherIndicatorsShown():
            _showHint()
        elif self.__isHintShown or self.__areOtherIndicatorsShown():
            self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
            self.__isHintShown = False
            self.__callbackDelayer.destroy()

    def __onVehicleControlling(self, vehicle):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        self.__isWheeledTech = vTypeDesc.isWheeledVehicle
        self.__hasTurboshaftEngine = vTypeDesc.hasTurboshaftEngine
        self.__hasHydraulicChassis = vTypeDesc.hasHydraulicChassis
        self.__hasRocketAcceleration = vTypeDesc.hasRocketAcceleration
        self.__isSuitableVehicle = (vTypeDesc.hasSiegeMode or self.__hasRocketAcceleration) and not (vTypeDesc.type.isDualgunVehicleType or vTypeDesc.hasAutoSiegeMode)
        if self.__hasRocketAcceleration:
            if self.__rocketCmp:
                self.__rocketCmp.unsubscribe(tryActivateCallback=self.__onTryRocketAccelerationActivate)
            self.__rocketCmp = vehicle.dynamicComponents.get('rocketAccelerationController', None)
            if self.__rocketCmp:
                self.__rocketCmp.subscribe(tryActivateCallback=self.__onTryRocketAccelerationActivate)
        if vehicle.isAlive() and self.__isSuitableVehicle:
            self.__isEnabled = True
            state = VEHICLE_VIEW_STATE.SIEGE_MODE
            value = vStateCtrl.getStateValue(state)
            if self.__hasTurboshaftEngine:
                value = (_SIEGE_STATE.ENABLED, None)
            if value is not None:
                self.__onVehicleStateUpdated(state, value)
        else:
            self.__siegeState = _SIEGE_STATE.DISABLED
            if self.__isEnabled:
                self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
            self.__isEnabled = False
        if not self.__startCounterUpdated and self.__isSuitableVehicle:
            self._updateCounterOnStart(self.__getSuitableSetting(), self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)
        self.__startCounterUpdated = True
        return

    def __onTryRocketAccelerationActivate(self):
        if not self.__isObserver and not self.__isInPostmortem:
            if self.__rocketCmp and self.__rocketCmp.stateStatus.status == ROCKET_ACCELERATION_STATE.READY:
                self.__onHintUsed()

    def __onVehicleStateUpdated(self, state, value):
        if not self.__isEnabled:
            return
        if state == VEHICLE_VIEW_STATE.SIEGE_MODE:
            siegeState, _ = value
            if siegeState in _SIEGE_STATE.SWITCHING:
                if not self.__isObserver and not self.__isInPostmortem:
                    self.__onHintUsed()
            if self.__siegeState != siegeState:
                self.__siegeState = siegeState
                self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.RECOVERY:
            self._isInRecovery = value[0]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.PROGRESS_CIRCLE:
            self._isInProgressCircle = value[1]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            self._isUnderFire = value
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isInDisplayPeriod = False
            self.__updateHint()

    def __onPostMortemSwitched(self, *_):
        self.__isInPostmortem = True
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        self.__isHintShown = False

    def __onRespawnBaseMoving(self):
        self.__isInPostmortem = False

    def __updateDestroyed(self, _):
        self.__isEnabled = False
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)

    def __onHintTimeOut(self):
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        self.__isHintShown = False

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        key = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        pressText = ''
        if keyName:
            pressText = backport.text(R.strings.ingame_gui.siegeMode.hint.press())
            if self.__isWheeledTech:
                hintText = backport.text(R.strings.ingame_gui.siegeMode.hint.wheeled())
            elif self.__hasTurboshaftEngine:
                hintText = backport.text(R.strings.ingame_gui.siegeMode.hint.turboshaftEngine())
            elif self.__hasRocketAcceleration:
                hintText = backport.text(R.strings.ingame_gui.siegeMode.hint.rocketAcceleration())
            else:
                hintTextID = R.strings.ingame_gui.siegeMode.hint.forMode.dyn(attr='c_{}'.format(self.__siegeState))
                hintText = backport.text(hintTextID()) if hintTextID.exists() else None
        else:
            hintText = backport.text(R.strings.ingame_gui.siegeMode.hint.noBinding())
        return HintData(key, keyName, pressText, hintText, 0, 0, HintPriority.SIEGE, False, None, False)

    def __areOtherIndicatorsShown(self):
        return self._isUnderFire or self._isInRecovery or self._isInProgressCircle

    def __getSuitableSetting(self):
        if self.__isWheeledTech:
            return self.__settings[WHEELED_MODE_HINT_SECTION]
        if self.__hasHydraulicChassis:
            return self.__settings[SIEGE_HINT_SECTION]
        if self.__hasTurboshaftEngine:
            return self.__settings[TURBO_SHAFT_ENGINE_MODE_HINT_SECTION]
        return self.__settings[ROCKET_ACCELERATION_MODE_HINT_SECTION] if self.__hasRocketAcceleration else {}


class RadarHintPlugin(HintPanelPlugin, CallbackDelayer, IRadarListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _HINT_DAY_COOLDOWN = 30
    _HINT_BATTLES_COOLDOWN = 10
    _TIME_AFTER_RADAR_COOLDOWN = 1

    def __init__(self, parentObj):
        super(RadarHintPlugin, self).__init__(parentObj)
        CallbackDelayer.__init__(self)
        self.__isEnabled = False
        self.__settings = {}
        self.__isHintShown = False
        self.__isInPostmortem = False
        self.__isObserver = False
        self.__period = None
        self.__isInDisplayPeriod = False
        self._isInRecovery = False
        self._isInProgressCircle = False
        self._isUnderFire = False
        self.__cbOnRadarCooldown = None
        self.__radarInProgress = False
        return

    def start(self):
        self.__settings = AccountSettings.getSettings(RADAR_HINT_SECTION)
        self._updateCounterOnStart(self.__settings, self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)
        arenaDP = self._sessionProvider.getArenaDP()
        self.__isObserver = arenaDP.getVehicleInfo().isObserver() if arenaDP is not None else False
        arena = BigWorld.player().arena
        if arena is not None:
            self.__isEnabled = ARENA_BONUS_TYPE_CAPS.checkAny(arena.bonusType, ARENA_BONUS_TYPE_CAPS.RADAR)
        if self._sessionProvider.dynamic.radar:
            self._sessionProvider.dynamic.radar.addRuntimeView(self)
        vStateCtrl = self._sessionProvider.shared.vehicleState
        if vStateCtrl:
            vStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    @classmethod
    def isSuitable(cls):
        return cls._sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.BATTLE_ROYALE

    def stop(self):
        if self._sessionProvider.dynamic.radar:
            self._sessionProvider.dynamic.radar.removeRuntimeView(self)
        vStateCtrl = self._sessionProvider.shared.vehicleState
        if self.__cbOnRadarCooldown is not None:
            BigWorld.cancelCallback(self.__cbOnRadarCooldown)
            self.__cbOnRadarCooldown = None
        if vStateCtrl:
            vStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        AccountSettings.setSettings(RADAR_HINT_SECTION, self.__settings)
        self.destroy()
        return

    def updateMapping(self):
        if not self.__isEnabled:
            return
        self.__updateHint()

    def setPeriod(self, period):
        if period is ARENA_PERIOD.BATTLE:
            self.__isInDisplayPeriod = self.__period is not None
            self._updateCounterOnBattle(self.__settings)
        self.__period = period
        return

    def radarActivated(self, _):
        _logger.debug('Radar activated')
        self.__radarInProgress = True
        self.__hideHint()

    def reset(self):
        self.__clearRadarCooldown()

    def timeOutDone(self):
        self.__radarInProgress = False

    def radarActivationFailed(self, code):
        _logger.debug('Radar activation failed')
        self.__hideHint()

    def startTimeOut(self, timeLeft, duration):
        if self.__isEnabled and self.__isInDisplayPeriod and self.__cbOnRadarCooldown is None:
            self.__cbOnRadarCooldown = BigWorld.callback(timeLeft + self._TIME_AFTER_RADAR_COOLDOWN, self.__updateHint)
        return

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_ACTIVATE_RADAR)
        key = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_ACTIVATE_RADAR)
        pressText = ''
        if keyName:
            pressText = backport.text(R.strings.battle_royale.radar.hint.press())
            hintText = backport.text(R.strings.battle_royale.radar.hint.text())
        else:
            hintText = backport.text(R.strings.battle_royale.radar.hint.noBinding())
        return HintData(key, keyName, pressText, hintText, 0, 0, HintPriority.RADAR, False, None, False)

    def __showHint(self):
        _logger.debug('Showing radar hint')
        if self.__radarInProgress:
            return
        self._parentObj.setBtnHint(CommandMapping.CMD_CM_VEHICLE_ACTIVATE_RADAR, self._getHint())
        self.__isHintShown = True
        self.__isInDisplayPeriod = False
        self.delayCallback(HINT_TIMEOUT, self.__onHintTimeOut)
        self._updateCounterOnUsed(self.__settings)

    def __hideHint(self):
        _logger.debug('Hiding radar hint isHintShown=%r', self.__isHintShown)
        if self.__isHintShown:
            self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_ACTIVATE_RADAR)
            self.__isHintShown = False
            self.stopCallback(self.__onHintTimeOut)

    def __updateHint(self):
        _logger.debug('Updating radar hint. isInPostmortem=%r, isObserver=%r, isEnabled=%r', self.__isInPostmortem, self.__isObserver, self.__isEnabled)
        self.__cbOnRadarCooldown = None
        if self.__isInPostmortem or self.__isObserver or not self.__isEnabled:
            return
        else:
            if self.__isInDisplayPeriod and self._haveHintsLeft(self.__settings) and not self.__areOtherIndicatorsShown():
                self.__showHint()
            else:
                self.__hideHint()
            return

    def __onVehicleStateUpdated(self, state, value):
        if not self.__isEnabled:
            return
        if state == VEHICLE_VIEW_STATE.RECOVERY:
            self._isInRecovery = value[0]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.PROGRESS_CIRCLE:
            self._isInProgressCircle = value[1]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            self._isUnderFire = value
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isInDisplayPeriod = False
            self.__updateHint()

    def __onPostMortemSwitched(self, *_):
        _logger.debug('Is in postmortem')
        self.__isInPostmortem = True
        self.__isHintShown = False

    def __onHintTimeOut(self):
        _logger.debug('Radar hint timed out')
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_ACTIVATE_RADAR)
        self.__isHintShown = False

    def __areOtherIndicatorsShown(self):
        return self._isUnderFire or self._isInRecovery or self._isInProgressCircle

    def __clearRadarCooldown(self):
        _logger.debug('Clearing radar cooldown')
        if self.__cbOnRadarCooldown is not None:
            BigWorld.cancelCallback(self.__cbOnRadarCooldown)
            self.__cbOnRadarCooldown = None
        return


class PreBattleHintPlugin(HintPanelPlugin):
    __slots__ = ('__isActive', '__hintInQueue', '__callbackDelayer', '__questHintSettings', '__helpHintSettings', '__battleComHintSettings', '__reservesHintSettings', '__isInDisplayPeriod', '__haveReqLevel', '__vehicleId')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, parentObj):
        super(PreBattleHintPlugin, self).__init__(parentObj)
        self.__isActive = False
        self.__hintInQueue = None
        self.__callbackDelayer = CallbackDelayer()
        self.__questHintSettings = {}
        self.__helpHintSettings = {}
        self.__battleComHintSettings = {}
        self.__reservesHintSettings = {}
        self.__isInDisplayPeriod = False
        self.__haveReqLevel = False
        self.__vehicleId = None
        return

    @classmethod
    def isSuitable(cls):
        guiType = cls.sessionProvider.arenaVisitor.getArenaGuiType()
        return not cls.sessionProvider.isReplayPlaying and guiType != ARENA_GUI_TYPE.RANKED and guiType != ARENA_GUI_TYPE.BATTLE_ROYALE and guiType != ARENA_GUI_TYPE.MAPS_TRAINING

    def start(self):
        prbSettings = dict(AccountSettings.getSettings(PRE_BATTLE_HINT_SECTION))
        self.__questHintSettings = prbSettings[QUEST_PROGRESS_HINT_SECTION]
        self.__helpHintSettings = prbSettings[HELP_SCREEN_HINT_SECTION]
        self.__battleComHintSettings = prbSettings[IBC_HINT_SECTION]
        self.__reservesHintSettings = prbSettings[RESERVES_HINT_SECTION]
        HintPanelPlugin._updateCounterOnStart(self.__questHintSettings, PRBSettings.HINT_DAY_COOLDOWN, PRBSettings.HINT_BATTLES_COOLDOWN)
        self.__isActive = True
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__handlePressQuestBtn, scope=EVENT_BUS_SCOPE.BATTLE)
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
        return

    def stop(self):
        if not self.isActive():
            return
        else:
            g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__handlePressQuestBtn, scope=EVENT_BUS_SCOPE.BATTLE)
            vStateCtrl = self.sessionProvider.shared.vehicleState
            if vStateCtrl is not None:
                vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            self.__callbackDelayer.destroy()
            self.__isActive = False
            prbHintSettings = dict()
            prbHintSettings[QUEST_PROGRESS_HINT_SECTION] = self.__questHintSettings
            prbHintSettings[HELP_SCREEN_HINT_SECTION] = self.__helpHintSettings
            prbHintSettings[IBC_HINT_SECTION] = self.__battleComHintSettings
            prbHintSettings[RESERVES_HINT_SECTION] = self.__reservesHintSettings
            AccountSettings.setSettings(PRE_BATTLE_HINT_SECTION, prbHintSettings)
            return

    def isActive(self):
        return self.__isActive

    def setPeriod(self, period):
        self.__isInDisplayPeriod = period in BEFORE_START_BATTLE_PERIODS
        if period is ARENA_PERIOD.BATTLE and self.__haveReqLevel:
            self._updateCounterOnBattle(self.__questHintSettings)

    def updateMapping(self):
        if self.__hintInQueue is not None:
            self._parentObj.setBtnHint(self.__hintInQueue, self._getHint())
        return

    def _getHint(self):
        serverSettings = self.lobbyContext.getServerSettings()
        if self.__hintInQueue is CommandMapping.CMD_SHOW_HELP:
            return self._makeHintData(R.strings.ingame_gui.helpScreen, HintPriority.HELP, HelpHintContext.MECHANICS)
        if self.__hintInQueue is CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND:
            return self._makeHintData(R.strings.ingame_gui.battleCommunication, HintPriority.BATTLE_COMMUNICATION)
        if self.__hintInQueue is CommandMapping.CMD_QUEST_PROGRESS_SHOW:
            if serverSettings.isPersonalMissionsEnabled():
                return self._makeHintData(R.strings.ingame_gui.battleProgress, HintPriority.QUESTS)
        elif self.__hintInQueue is CommandMapping.CMD_SHOW_PERSONAL_RESERVES and serverSettings.personalReservesConfig.isReservesInBattleActivationEnabled:
            return self._makeHintData(R.strings.ingame_gui.personal_reserves, HintPriority.RESERVES)

    def _makeHintData(self, resourceRoot, priority, hintCtx=None):
        cmd = self.__hintInQueue
        keyName = getReadableKey(cmd)
        key = getVirtualKey(cmd)
        pressText = ''
        hintText = backport.text(R.strings.ingame_gui.hint.noBindingKey())
        if keyName:
            pressText = backport.text(resourceRoot.hint.press())
            hintText = backport.text(resourceRoot.hint.description())
        return HintData(key, keyName, pressText, hintText, 0, 0, priority, False, hintCtx=hintCtx, centeredMessage=False)

    def _canDisplayCustomHelpHint(self):
        return False

    def __checkHintConditions(self, typeDescriptor):
        return typeDescriptor.isWheeledVehicle and not typeDescriptor.isWheeledVehicleWithoutFeatures or typeDescriptor.type.isDualgunVehicleType or typeDescriptor.hasTurboshaftEngine or typeDescriptor.isTrackWithinTrack or typeDescriptor.hasRocketAcceleration or typeDescriptor.hasDualAccuracy or typeDescriptor.isAssaultSPG or typeDescriptor.isMultiTrack or self.__checkFlameThrowerConditions(typeDescriptor)

    def __onVehicleControlling(self, vehicle):
        if not self.isActive():
            return
        else:
            vTypeDesc = vehicle.typeDescriptor
            vehicleType = vTypeDesc.type.id
            self.__vehicleId = makeIntCompactDescrByID('vehicle', vehicleType[0], vehicleType[1])
            self.__haveReqLevel = vTypeDesc.level >= _HINT_MIN_VEHICLE_LEVEL
            if self.__checkHintConditions(vTypeDesc):
                self.__updateHintCounterOnStart(self.__vehicleId, vehicle, self.__helpHintSettings)
            if self.__canDisplayVehicleHelpHint(vTypeDesc) or self._canDisplayCustomHelpHint():
                self.__displayHint(CommandMapping.CMD_SHOW_HELP)
                return
            if self.__canDisplayBattleCommunicationHint():
                isDisplayed = self.__displayHint(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND)
                if isDisplayed:
                    self.__battleComHintSettings = self._updateBattleCounterOnUsed(self.__battleComHintSettings)
                return
            if self.__canDisplayQuestHint():
                self.__displayHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
                return
            if self.__canDisplayPersonalReservesActivationHint():
                isDisplayed = self.__displayHint(CommandMapping.CMD_SHOW_PERSONAL_RESERVES)
                if isDisplayed:
                    self._updateBattleCounterOnUsed(self.__reservesHintSettings)
            elif self.__hintInQueue is not None:
                self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
                self._parentObj.removeBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
                self._parentObj.removeBtnHint(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND)
                self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_PERSONAL_RESERVES)
                self.__callbackDelayer.destroy()
            return

    def __updateHintCounterOnStart(self, section, vehicle, setting):
        if section not in setting:
            setting[section] = {HINTS_LEFT: 3,
             LAST_DISPLAY_DAY: 0,
             NUM_BATTLES: 0}
        if vehicle.isAlive() and vehicle.isPlayerVehicle:
            self._updateCounterOnBattle(setting[section])
            HintPanelPlugin._updateCounterOnStart(setting[section], PRBSettings.HINT_DAY_COOLDOWN, PRBSettings.HINT_BATTLES_COOLDOWN)

    def __onHintTimeOut(self):
        self._parentObj.removeBtnHint(self.__hintInQueue)
        if self.__hintInQueue in (CommandMapping.CMD_SHOW_HELP,
         CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND,
         CommandMapping.CMD_SHOW_PERSONAL_RESERVES,
         CommandMapping.CMD_QUEST_PROGRESS_SHOW):
            self.__callbackDelayer.delayCallback(_HINT_COOLDOWN, self.__onHintTimeCooldown, self.__hintInQueue)
        self.__hintInQueue = None
        return

    def __canDisplayVehicleHelpHint(self, typeDescriptor):
        return self.__checkHintConditions(typeDescriptor) and self.__isInDisplayPeriod and self._haveHintsLeft(self.__helpHintSettings[self.__vehicleId])

    def __checkFlameThrowerConditions(self, typeDescriptor):
        guiType = self.sessionProvider.arenaVisitor.getArenaGuiType()
        return typeDescriptor.isFlamethrower and guiType in ARENA_GUI_TYPE.RANDOM_RANGE

    def __canDisplayBattleCommunicationHint(self):
        settingsCore = dependency.instance(ISettingsCore)
        battleCommunicationIsEnabled = bool(settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
        return self.__isInDisplayPeriod and self._haveHintsLeft(self.__battleComHintSettings) and self.sessionProvider.arenaVisitor.getArenaGuiType() != ARENA_GUI_TYPE.BOOTCAMP and battleCommunicationIsEnabled

    def __canDisplayPersonalReservesActivationHint(self):
        battleBoostersCache = dependency.instance(IBoostersStateProvider)
        supported = ARENA_BONUS_TYPE_CAPS.checkAny(self.sessionProvider.arenaVisitor.getArenaBonusType(), ARENA_BONUS_TYPE_CAPS.BOOSTERS)
        return self.__isInDisplayPeriod and self._haveHintsLeft(self.__reservesHintSettings) and not battleBoostersCache.getActiveResources() and battleBoostersCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.IN_ACCOUNT) and supported and self.lobbyContext.getServerSettings().personalReservesConfig.isReservesInBattleActivationEnabled

    def __canDisplayQuestHint(self):
        return self.__isInDisplayPeriod and self._haveHintsLeft(self.__questHintSettings) and self.__haveReqLevel and self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.RANDOM_RANGE and self.lobbyContext.getServerSettings().isPersonalMissionsEnabled()

    def __onHintTimeCooldown(self, lastHint):
        if lastHint == CommandMapping.CMD_SHOW_HELP and self.__canDisplayBattleCommunicationHint():
            isDisplayed = self.__displayHint(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND)
            if isDisplayed:
                self.__battleComHintSettings = self._updateBattleCounterOnUsed(self.__battleComHintSettings)
        elif lastHint in (CommandMapping.CMD_SHOW_HELP, CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND) and self.__canDisplayQuestHint():
            self.__displayHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
        elif lastHint in (CommandMapping.CMD_SHOW_HELP, CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND, CommandMapping.CMD_QUEST_PROGRESS_SHOW) and self.__canDisplayPersonalReservesActivationHint():
            isDisplayed = self.__displayHint(CommandMapping.CMD_SHOW_PERSONAL_RESERVES)
            if isDisplayed:
                self._updateBattleCounterOnUsed(self.__reservesHintSettings)

    def __displayHint(self, hintType):
        if self.__isInDisplayPeriod:
            self.__hintInQueue = hintType
            self._parentObj.setBtnHint(hintType, self._getHint())
            return True
        return False

    def __handleShowBtnHint(self, event):
        if event.ctx.get('btnID') in (CommandMapping.CMD_SHOW_HELP,
         CommandMapping.CMD_QUEST_PROGRESS_SHOW,
         CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND,
         CommandMapping.CMD_SHOW_PERSONAL_RESERVES):
            self.__callbackDelayer.delayCallback(HINT_TIMEOUT, self.__onHintTimeOut)
        elif self.__callbackDelayer.hasDelayedCallback(self.__onHintTimeOut):
            self.__callbackDelayer.stopCallback(self.__onHintTimeOut)

    def __handleLoadView(self, event):
        if event.alias == VIEW_ALIAS.INGAME_DETAILS_HELP:
            if self.__hintInQueue == CommandMapping.CMD_SHOW_HELP:
                self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
                self.__callbackDelayer.delayCallback(_HINT_COOLDOWN, self.__onHintTimeCooldown, self.__hintInQueue)
                self.__hintInQueue = None
            viewCtx = event.kwargs.get('ctx', {})
            if viewCtx.get('hasUniqueVehicleHelpScreen', False):
                vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
                if self.__checkHintConditions(vehicle.typeDescriptor):
                    hintStats = self.__helpHintSettings[self.__vehicleId]
                    self.__helpHintSettings[self.__vehicleId] = self._updateCounterOnUsed(hintStats)
        return

    def __handlePressQuestBtn(self, _):
        if self.__hintInQueue == CommandMapping.CMD_QUEST_PROGRESS_SHOW:
            self._parentObj.removeBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
            self.__hintInQueue = None
        self.__questHintSettings = self._updateCounterOnUsed(self.__questHintSettings)
        return


class RoleHelpPlugin(HintPanelPlugin):
    __slots__ = ('__isActive', '__settings', '__vehicleCD', '__isShown', '__isInDisplayPeriod', '__callbackDelayer', '__isVisible')
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HINTS_COUNT = 1
    _BATTLES_COUNT = 3

    def __init__(self, parentObj):
        super(RoleHelpPlugin, self).__init__(parentObj)
        self.__isActive = False
        self.__settings = None
        self.__vehicleCD = None
        self.__isShown = False
        self.__isVisible = False
        self.__isInDisplayPeriod = False
        self.__callbackDelayer = None
        return

    @classmethod
    def isSuitable(cls):
        return cls._sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.RANKED

    @classmethod
    def isAvailableToShow(cls):
        result = False
        vehicle = cls._sessionProvider.shared.vehicleState.getControllingVehicle()
        hasRole = vehicle and vehicle.typeDescriptor.role != ROLE_TYPE.NOT_DEFINED
        if not cls.__getIsObserver() and hasRole and not cls._sessionProvider.isReplayPlaying:
            periodCtrl = cls._sessionProvider.shared.arenaPeriod
            if cls.isSuitable() and periodCtrl.getPeriod() in BEFORE_START_BATTLE_PERIODS:
                result = cls.isAvailableInSettings(vehicle.typeDescriptor.type.compactDescr)
        return result

    def start(self):
        if self.__getIsObserver():
            return
        self.__isActive = True
        self.__settings = dict(AccountSettings.getSettings(PRE_BATTLE_ROLE_HINT_SECTION))
        self.__callbackDelayer = CallbackDelayer()
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        if self.__isActive:
            self.__hide()
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
            if self.__isShown:
                AccountSettings.setSettings(PRE_BATTLE_ROLE_HINT_SECTION, self.__settings)
        self.__isActive = False
        return

    def isActive(self):
        return self.__isActive

    def setPeriod(self, period):
        if not self.isActive():
            return
        self.__isInDisplayPeriod = period in BEFORE_START_BATTLE_PERIODS
        if self.__isVisible and not self.__isInDisplayPeriod:
            self.__hide()
        elif self.__isInDisplayPeriod and not self.__isShown:
            self.__vehicleCD = self._sessionProvider.getArenaDP().getVehicleInfo().vehicleType.compactDescr
            if self.__vehicleCD not in self.__settings:
                self.__initSettings(self.__vehicleCD)

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_SHOW_HELP)
        key = getVirtualKey(CommandMapping.CMD_SHOW_HELP)
        pressText = backport.text(R.strings.ingame_gui.helpScreen.hint.press())
        hintText = backport.text(R.strings.ingame_gui.helpScreen.hint.description())
        return HintData(key, keyName, pressText, hintText, 0, 0, HintPriority.HELP, False, HelpHintContext.ROLE_HELP, False)

    @classmethod
    def isAvailableInSettings(cls, vehCD):
        settings = AccountSettings.getSettings(PRE_BATTLE_ROLE_HINT_SECTION)
        result = True
        if vehCD in settings:
            result = settings[vehCD][NUM_BATTLES] > 0 and settings[vehCD][HINTS_LEFT] > 0
        return result

    @classmethod
    def __getIsObserver(cls):
        isObserver = False
        arenaDP = cls._sessionProvider.getArenaDP()
        if arenaDP is not None:
            vInfo = arenaDP.getVehicleInfo()
            isObserver = vInfo.isObserver()
        return isObserver

    def __initSettings(self, vehicleId):
        self.__settings[vehicleId] = {HINTS_LEFT: self._HINTS_COUNT,
         NUM_BATTLES: self._BATTLES_COUNT}

    def __showHint(self):
        self._parentObj.setBtnHint(CommandMapping.CMD_SHOW_HELP, self._getHint())
        self.__settings[self.__vehicleCD][NUM_BATTLES] -= 1
        self.__callbackDelayer.delayCallback(HINT_TIMEOUT, self.__hide)
        self.__isVisible = True
        self.__isShown = True
        self.__handleRoleToggleEvent(True)

    @staticmethod
    def __handleRoleToggleEvent(isVisible):
        g_eventBus.handleEvent(GameEvent(GameEvent.ROLE_HINT_TOGGLE, ctx={'isShown': isVisible}), scope=EVENT_BUS_SCOPE.BATTLE)

    def __handleLoadView(self, event):
        if event.alias == VIEW_ALIAS.INGAME_DETAILS_HELP:
            self.__hide()
            self._updateCounterOnUsed(self.__settings[self.__vehicleCD])

    def __handleBattleLoading(self, event):
        battleLoadingShown = event.ctx.get('isShown')
        if not battleLoadingShown and self.__isInDisplayPeriod and self.isAvailableInSettings(self.__vehicleCD):
            self.__showHint()

    def __hide(self):
        if self.__isVisible:
            self.__callbackDelayer.stopCallback(self.__hide)
            self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
            self.__handleRoleToggleEvent(False)
            self.__isVisible = False


class CommanderCameraHintPlugin(HintPanelPlugin, CallbackDelayer):
    __slots__ = ('__currPeriod', '__canShow', '__hintData', '__settings')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, parentObj):
        super(CommanderCameraHintPlugin, self).__init__(parentObj)
        CallbackDelayer.__init__(self)
        strings = R.strings.ingame_gui
        self.__hintData = {'hintData': HintData(getVirtualKey(CommandMapping.CMD_COMMANDER_CAM), getReadableKey(CommandMapping.CMD_COMMANDER_CAM), '', backport.text(strings.commanderCam.hint.description()), 0, 0, HintPriority.HELP, True, HelpHintContext.COMMANDER_CAMERA, False),
         'btnID': CommandMapping.CMD_COMMANDER_CAM}
        self.__currPeriod = None
        self.__settings = {}
        self.__canShow = True
        return

    @classmethod
    def isSuitable(cls):
        return cls.sessionProvider.arenaVisitor.getArenaGuiType() != ARENA_GUI_TYPE.MAPS_TRAINING

    def start(self):
        settings = dict(AccountSettings.getSettings(COMMANDER_CAM_HINT_SECTION))
        self.__settings = settings
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(GameEvent.COMMANDER_HINT, self.__onHintShow, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(GameEvent.COMMANDER_HINT, self.__onHintShow, scope=EVENT_BUS_SCOPE.BATTLE)
        CallbackDelayer.destroy(self)
        AccountSettings.setSettings(COMMANDER_CAM_HINT_SECTION, self.__settings)

    def setPeriod(self, period):
        self.__currPeriod = period

    def updateMapping(self):
        self.__displayHint(self.__hintData)

    def _getHintDataByCMD(self, hint):
        return hint.get('hintData') if self.__currPeriod in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE) else None

    def __handleShowBtnHint(self, event):
        if event.ctx.get('btnID') == self.__hintData.get('btnID'):
            self._updateBattleCounterOnUsed(self.__settings)
            self.__canShow = False
            self.delayCallback(HINT_TIMEOUT, self.__hideHint)

    def __hideHint(self):
        self._parentObj.removeBtnHint(self.__hintData.get('btnID'))

    def __displayHint(self, hint):
        if self._haveHintsLeft(self.__settings) and self.__canShow:
            self._parentObj.setBtnHint(hint.get('btnID'), self._getHintDataByCMD(hint))

    def __onHintShow(self, event):
        if event.ctx.get('show'):
            self.__displayHint(self.__hintData)
        else:
            self.__hideHint()


class MapsTrainingHelpHintPlugin(PreBattleHintPlugin):

    @classmethod
    def isSuitable(cls):
        return cls.sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.MAPS_TRAINING

    def _getHint(self):
        return HintData(getVirtualKey(CommandMapping.CMD_SHOW_HELP), getReadableKey(CommandMapping.CMD_SHOW_HELP), backport.text(R.strings.maps_training.helpScreen.hint.press()), backport.text(R.strings.maps_training.helpScreen.hint.description()), 0, 0, HintPriority.HELP, False, HelpHintContext.MAPS_TRAINING, False)

    def _canDisplayCustomHelpHint(self):
        return True


class HelpPlugin(HintPanelPlugin):
    __slots__ = ('__isActive', '__settings', '__isShown', '__isInDisplayPeriod', '__callbackDelayer', '__isVisible', '__settingKey', '__settingSectionName', '_localeRes', '__hintPriority', '__hintContext')
    _HINT_TIMEOUT = 6

    def __init__(self, settingSectionName, settingKey, localeRes, hintPriority, hintContext, parentObj):
        self.__isActive = False
        self.__settings = None
        self.__isShown = False
        self.__isVisible = False
        self.__isInDisplayPeriod = False
        self.__callbackDelayer = None
        self.__settingKey = settingKey
        self.__settingSectionName = settingSectionName
        self._localeRes = localeRes
        self.__hintPriority = hintPriority
        self.__hintContext = hintContext
        super(HelpPlugin, self).__init__(parentObj)
        return

    def start(self):
        self.__isActive = True
        self.__callbackDelayer = CallbackDelayer()
        self.__settings = AccountSettings.getSettings(self.__settingSectionName)
        self.__settings[self.__settingKey] = self.__settings.get(self.__settingKey, {HINTS_LEFT: 3})
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.BATTLE_LOADING, self.__onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__onHintShown, scope=EVENT_BUS_SCOPE.GLOBAL)

    def stop(self):
        if self.__isActive:
            self.__hide()
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__handleLoadView, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.BATTLE_LOADING, self.__onBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__onHintShown, scope=EVENT_BUS_SCOPE.GLOBAL)
            if self.__isShown:
                AccountSettings.setSettings(self.__settingSectionName, self.__settings)
        self.__isActive = False
        self.__settingKey = None
        self.__settingSectionName = None
        self._localeRes = None
        self.__hintPriority = None
        self.__hintContext = None
        return

    def setPeriod(self, period):
        if not self.__isActive:
            return
        self.__isInDisplayPeriod = period in BEFORE_START_BATTLE_PERIODS
        if self.__isVisible and not self.__isInDisplayPeriod:
            self.__hide()

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_SHOW_HELP)
        key = getVirtualKey(CommandMapping.CMD_SHOW_HELP)
        return HintData(key, keyName, backport.text(self._localeRes.press()), backport.text(self._localeRes.description()), 0, 0, self.__hintPriority, False, self.__hintContext, False)

    def __showHint(self):
        self._parentObj.setBtnHint(CommandMapping.CMD_SHOW_HELP, self._getHint())

    def __onHintShown(self, event):
        if event.ctx.get('hintCtx') == self.__hintContext and not self.__isShown:
            self.__isVisible = True
            self.__isShown = True
            self.__callbackDelayer.delayCallback(self._HINT_TIMEOUT, self.__hide)

    def __handleLoadView(self, event):
        if event.alias == VIEW_ALIAS.INGAME_DETAILS_HELP:
            self.__hide()

    def __onBattleLoading(self, event):
        battleLoadingShown = event.ctx.get('isShown')
        if not battleLoadingShown and self.__isInDisplayPeriod and self.__settings[self.__settingKey][HINTS_LEFT] > 0:
            self.__showHint()

    def __hide(self):
        if self.__isVisible:
            self.__callbackDelayer.stopCallback(self.__hide)
            self.__isVisible = False
            hint = self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
            if hint and hint.hintCtx == self.__hintContext:
                self._updateBattleCounterOnUsed(self.__settings[self.__settingKey])


class MapboxHelpPlugin(HelpPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(MapboxHelpPlugin, self).__init__(MAPBOX_HINT_SECTION, 'mapbox', R.strings.ingame_gui.helpScreen.mapbox, HintPriority.MAPBOX, HelpHintContext.MAPBOX, parentObj)

    @classmethod
    def isSuitable(cls):
        return cls.__sessionProvider.arenaVisitor.getArenaGuiType() == ARENA_GUI_TYPE.MAPBOX


class DevMapsHintPlugin(HelpPlugin):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(DevMapsHintPlugin, self).__init__(DEV_MAPS_HINT_SECTION, 'devMaps', R.strings.ingame_gui.devMaps.hint, HintPriority.DEV_MAPS, HelpHintContext.DEV_MAPS, parentObj)

    @classmethod
    def isSuitable(cls):
        return cls.__sessionProvider.arenaVisitor.extra.isMapsInDevelopmentEnabled()
