# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/kill_cam_modes.py
import logging
import weakref
import typing
import BigWorld
import constants
import Keys
import Math
import BattleReplay
import math_utils
import GUI
import CommandMapping as CM
from PlayerEvents import g_playerEvents
from battleground.simulated_scene import SimulatedScene, ANIMATION_DURATION_BEFORE_SHOT
from constants import ATTACK_REASON, ATTACK_REASONS, ARENA_PERIOD, POSTMORTEM_MODIFIERS
from gui.battle_control.arena_info.interfaces import IBattleFieldController
from gui.shared.events import DeathCamEvent
from wotdecorators import noexcept
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera
from AvatarInputHandler.DynamicCameras.kill_cam_camera import KillCamera, StartCamDirection, LOOK_AT_KILLER_DURATION
from control_modes import IControlMode, _readCameraTransitionSettings
from aih_constants import CTRL_MODE_NAME
from helpers import dependency, uniprof
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from PostmortemDelay import PostmortemDelay
from account_helpers.AccountSettings import AccountSettings, WHEELED_DEATH_DELAY_COUNT
if typing.TYPE_CHECKING:
    from typing import Dict, Any
_PARTICLES_DURATION_AFTER_SHOT = 0.0
_PREPARE_KILLER_VISION_FADE_TIME = 0.8
_SHOW_KILLER_VISION_FADE_TIME = 1.0
_LEAVE_KILLER_VISION_FADE_TIME = 0.8
_SHOW_DEAD_TANK_FADE_TIME = 1.0
_START_VISION_DELAY = 1.0
_KILL_CAM_WAIT_TIME = 2.0
_TIME_BEFORE_FOLLOW_TANK = 2.0
_WHEELED_VEHICLE_POSTMORTEM_DELAY = 3.0
_LOOK_AT_KILLER_DURATION_LEGACY = 2.0
_LOOK_AT_KILLER_SUBSTITUTE_WAIT_TIME = 5
_NO_SKIP_DEATH_CAM_DURATION = 2.0
_PAUSE_BUTTON_COOLDOWN = 0.5
_SKIP_KILL_CAM_BEFORE_AUTORESPAWN_TIME = 15
_RADIUS = 10
_RADIUS_ALPHA = 2
_BLOCKED_KEYS = {Keys.KEY_LCONTROL,
 Keys.KEY_RCONTROL,
 Keys.KEY_T,
 Keys.KEY_M,
 Keys.KEY_B,
 Keys.KEY_N,
 Keys.KEY_TAB}
_BLOCKED_ACTIONS = (CM.CMD_SHOW_HELP,)
_BLACK_BG_IMG = 'gui/maps/login/blackBg.png'
_logger = logging.getLogger(__name__)

class SimulationAvailability(object):
    AVAILABLE = 0
    NOT_AVAILABLE_MISSING_DATA = 1
    NOT_AVAILABLE_END_OF_BATTLE = 2
    VEHICLES_TOO_CLOSE = 3
    NOT_KILLED_BY_SHOT = 4
    NOT_SUPPORTED_MODE = 5
    NOT_ENOUGH_TIME = 6
    NOT_AVAILABLE = (NOT_AVAILABLE_MISSING_DATA,
     NOT_AVAILABLE_END_OF_BATTLE,
     VEHICLES_TOO_CLOSE,
     NOT_KILLED_BY_SHOT,
     NOT_SUPPORTED_MODE,
     NOT_ENOUGH_TIME)


class KillModeBase(IControlMode, CallbackDelayer):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, dataSection, avatarInputHandler):
        super(KillModeBase, self).__init__()
        CallbackDelayer.__init__(self)
        self._modeEnteredTime = -1
        self._victimVehicleID = None
        self._killerVehicleID = None
        self._rawSimulationData = None
        self._trajectoryPoints = [None, None]
        self._postmortemKwargs = None
        self._skipBattleTimeLeft = dataSection.readFloat('skipBattleTimeLeft')
        self._cameraTransitionDurations = _readCameraTransitionSettings(dataSection['camera'])
        self._aih = weakref.proxy(avatarInputHandler)
        self._cam = KillCamera(dataSection['camera'], dataSection.readVector2('defaultOffset'))
        self.__killCamState = DeathCamEvent.State.NONE
        return

    @property
    def camera(self):
        return self._cam

    @property
    def curVehicleID(self):
        return self._victimVehicleID

    @property
    def killCamCtrl(self):
        return self.guiSessionProvider.shared.killCamCtrl

    @property
    def killCamState(self):
        return self.__killCamState

    @property
    def _killerIsSpotted(self):
        return self._rawSimulationData and self._rawSimulationData['attacker'] and self._rawSimulationData['attacker']['spotted']

    def create(self):
        self._cam.create(onChangeControlMode=None, postmortemMode=True, smartPointCalculator=True)
        return

    def destroy(self):
        self.disable(smoothFade=False)
        self._cam.destroy()
        self._cam = None
        self._aih = None
        self.clearCallbacks()
        return

    def enable(self, **kwargs):
        _logger.info('[%s] %s is Enabled', self.__class__.__name__, self.__class__.__name__)
        self._modeEnteredTime = BigWorld.time()
        avatar = BigWorld.player()
        if avatar is None:
            _logger.error('Avatar is None, cannot enter %s.', self.__class__.__name__)
            return
        else:
            self._aih.setForcedGuiControlMode(False)
            self._changeKillCamModeState(DeathCamEvent.State.NONE)
            self._victimVehicleID = avatar.playerVehicleID
            self._postmortemKwargs = kwargs
            self._postmortemKwargs['newVehicleID'] = BigWorld.player().playerVehicleID
            vehicleMProv = avatar.consistentMatrices.attachedVehicleMatrix
            camAngles = None
            pivotSettings = None
            previousCam = None
            isInArcadeZoomState = False
            if 'previousCam' in kwargs:
                previousCam = kwargs['previousCam']
                camAngles = getattr(previousCam, 'angles', None)
                if isinstance(previousCam, ArcadeCamera):
                    pivotSettings = previousCam.aimingSystem.getPivotSettings()
                    isInArcadeZoomState = previousCam.isInArcadeZoomState()
            if previousCam is None or not isInArcadeZoomState or pivotSettings is None:
                pivotSettings = PostmortemDelay.KILLER_VEHICLE_CAMERA_PIVOT_SETTINGS
            self._cam.enable(vehicleMProv=vehicleMProv, preferredPos=camAngles, initialPivotSettings=pivotSettings)
            killerVehicleID = self._aih.getKillerVehicleID()
            deathReason = self._aih.getDeathReason()
            if killerVehicleID is None and deathReason is None:
                self._aih.onReceivedKillerID += self.__onReceiveKillerID
            else:
                self.__onReceiveKillerID(killerVehicleID)
            return

    def disable(self, smoothFade=True):
        _logger.info('[%s] disable()', self.__class__.__name__)
        self._modeEnteredTime = -1
        self._postmortemKwargs = None
        self._cam.disable()
        self.clearCallbacks()
        self._aih.onReceivedKillerID -= self.__onReceiveKillerID
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if key in _BLOCKED_KEYS or CM.g_instance.isFiredList(_BLOCKED_ACTIONS, key):
            return True
        if BattleReplay.g_replayCtrl.isPlaying or not self._canSkipKillCamera():
            return False
        if CM.g_instance.isFired(CM.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown and self._canSwitchToFreecam():
            self._switchToCtrlMode(CTRL_MODE_NAME.DEATH_FREE_CAM)
            return True
        if key in (Keys.KEY_LEFTMOUSE, Keys.KEY_RIGHTMOUSE) and not isDown:
            avatar = BigWorld.player()
            self._switchToCtrlMode(CTRL_MODE_NAME.POSTMORTEM, immediateSwitchToAllyVehicle=avatar.canSwitchToAllyVehicle())
            return True
        return False

    def _leaveMode(self):
        raise NotImplementedError('Implement in inheriting classes!')

    def _handleModeExecution(self):
        raise NotImplementedError('Implement in inheriting classes!')

    def _changeKillCamModeState(self, newState):
        self.__killCamState = newState
        _logger.info('%s: Kill Cam State changed to: %s', self.__class__.__name__, self.__killCamState)
        if self.killCamCtrl:
            self.killCamCtrl.changeKillCamModeState(self.__killCamState)

    def _canShowKillerVisionInPeriod(self):
        periodCtrl = self.guiSessionProvider.shared.arenaPeriod
        if not periodCtrl:
            return False
        if BattleReplay.g_replayCtrl.isPlaying:
            return True
        isBattlePeriod = ARENA_PERIOD.BATTLE == periodCtrl.getPeriod()
        isTimeLeft = periodCtrl.getEndTime() - BigWorld.serverTime() > self._skipBattleTimeLeft
        return isBattlePeriod and isTimeLeft

    def _areBothTeamsAlive(self):
        avatar = BigWorld.player()
        battleFieldCtrl = self.guiSessionProvider.dynamic.battleField
        if not avatar or not battleFieldCtrl:
            return False
        if BattleReplay.g_replayCtrl.isPlaying:
            return True
        allies, enemies = battleFieldCtrl.getAliveVehicles()
        if not allies and not avatar.isPostmortemModificationActive(CTRL_MODE_NAME.KILL_CAM, POSTMORTEM_MODIFIERS.ENABLED_IF_NO_ALLY):
            _logger.debug('Skip KillerVision because no allies are left alive and battle will end')
            return False
        if not enemies:
            _logger.debug('Skip KillerVision because no enemies are left alive and battle will end')
            return False
        return True

    def _checkSimulationAvailability(self):
        avatar = BigWorld.player()
        vehicle = avatar.vehicle
        if vehicle is None:
            vehicle = BigWorld.entity(avatar.playerVehicleID)
        if not self._canShowKillerVisionInPeriod() or not self._areBothTeamsAlive():
            _logger.info('The battle ends soon - shorten Look At Killer rotation or skip Killer Vision')
            return (SimulationAvailability.NOT_AVAILABLE_END_OF_BATTLE, None)
        elif 'killCamData' not in vehicle.dynamicComponents:
            _logger.info("Player doesn't have killCamData available")
            return (SimulationAvailability.NOT_AVAILABLE_MISSING_DATA, None)
        elif not self._isKillByShot():
            _logger.info("Player wasn't killed by shot")
            return (SimulationAvailability.NOT_KILLED_BY_SHOT, None)
        simulationData = self.__getRawSimulationData(vehicle)
        if not self._validateRawSimulationData(simulationData):
            _logger.info('Skip KillerVision because no simulation data are available')
            return (SimulationAvailability.NOT_AVAILABLE_MISSING_DATA, None)
        else:
            return (SimulationAvailability.AVAILABLE, simulationData)

    def _validateRawSimulationData(self, rawSimulationData):
        if rawSimulationData is None:
            return False
        attackerData = rawSimulationData.get('attacker', None)
        trajectoryData = rawSimulationData.get('trajectoryData', None)
        if not attackerData or not trajectoryData:
            _logger.error('_validateRawSimulationData(): Missing attackerData %s, or trajectoryData %s', attackerData, trajectoryData)
            return False
        else:
            return True

    def _canSkipKillCamera(self):
        return False if BigWorld.time() - self._modeEnteredTime < _NO_SKIP_DEATH_CAM_DURATION else True

    def _canSwitchToFreecam(self):
        if not self._canSkipKillCamera():
            return False
        respawnCtrl = self.guiSessionProvider.dynamic.respawn
        needToRespawn = respawnCtrl and respawnCtrl.playerLives > 0
        return False if needToRespawn else BigWorld.player().isPostmortemFeatureEnabled(CTRL_MODE_NAME.DEATH_FREE_CAM)

    def _switchToCtrlMode(self, targetMode, **kwargs):
        if targetMode != CTRL_MODE_NAME.DEATH_FREE_CAM:
            self.selectPlayer(None)
        newVehicleID = BigWorld.player().playerVehicleID if targetMode in (CTRL_MODE_NAME.POSTMORTEM, CTRL_MODE_NAME.DEATH_FREE_CAM) else None
        BigWorld.player().inputHandler.onControlModeChanged(targetMode, prevModeName=CTRL_MODE_NAME.KILL_CAM, camMatrix=Math.Matrix(BigWorld.camera().matrix), curVehicleID=self._victimVehicleID, newVehicleID=newVehicleID, transitionDuration=self._cameraTransitionDurations[targetMode], **kwargs)
        return

    def _isKillByShot(self):
        deathReasonID = BigWorld.player().inputHandler.getDeathReason()
        return deathReasonID is not None and ATTACK_REASONS[deathReasonID] in (ATTACK_REASON.SHOT, ATTACK_REASON.FIRE)

    def _isFirstTenDeathsWheeledTank(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isWheeledTech:
            return False
        else:
            wheeledDeathCountLeft = AccountSettings.getSettings(WHEELED_DEATH_DELAY_COUNT)
            return False if wheeledDeathCountLeft == 0 else True

    def _tryDecrementWheeledDeathCounter(self, vehicleID):
        if self._isFirstTenDeathsWheeledTank(vehicleID):
            wheeledDeathCountLeft = AccountSettings.getSettings(WHEELED_DEATH_DELAY_COUNT)
            AccountSettings.setSettings(WHEELED_DEATH_DELAY_COUNT, max(wheeledDeathCountLeft - 1, 0))

    def __getRawSimulationData(self, vehicle):
        if not vehicle:
            _logger.error("__getRawSimulationData: Unable to get player's vehicle")
            return None
        else:
            rawSimulationData = vehicle.killCamData.getSimulationData()
            return rawSimulationData

    def __onReceiveKillerID(self, vehicleID):
        self._killerVehicleID = vehicleID
        playerVehicle = BigWorld.entities.get(self._victimVehicleID)
        isDefinedPostmortemView = playerVehicle and playerVehicle.isPostmortemViewPointDefined
        if isDefinedPostmortemView:
            _logger.info('[%s] Leave %s (in base class): we have a predefined postmortem view - leave mode', self.__class__.__name__, self.__class__.__name__)
            self._leaveMode()
        else:
            self._handleModeExecution()


class KillCamMode(KillModeBase):

    def __init__(self, dataSection, avatarInputHandler):
        super(KillCamMode, self).__init__(dataSection, avatarInputHandler)
        self.__isLeaveKillCamWhenPrepared = False
        self.__bFadeScreenActive = False
        self.__lastTimePauseToggled = 0.0
        self.__vehicleRespawnTriggered = False
        self.__isAutoRespawnScheduled = False
        self.__simulatedVictimID = None
        self.__simulatedKillerID = None
        self.__unspottedOrigin = None
        self.__simulatedScene = SimulatedScene(dataSection['deathCamPostProcessEffects'])
        self.__skipKillCamDistance = dataSection.readFloat('skipKillCamVehiclesDistance')
        self._skipBattleTimeLeft = dataSection.readFloat('skipBattleTimeLeft')
        self._skipNotEnoughTimeForDC = dataSection.readFloat('skipNotEnoughTimeForDC')
        return

    @property
    def __isRicochet(self):
        return self._rawSimulationData['projectile']['ricochetCount'] > 0

    def create(self):
        super(KillCamMode, self).create()
        ctrl = self.guiSessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onSwitchToPostmortem
        self.__simulatedScene.create()
        return

    def destroy(self):
        super(KillCamMode, self).destroy()
        ctrl = self.guiSessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onSwitchToPostmortem
        self.__simulatedScene.destroy()
        self.__simulatedScene = None
        return

    def enable(self, **kwargs):
        uniprof.enterToRegion('avatar.control_mode.kill_cam')
        respawnCtrl = self.guiSessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdate
        BigWorld.wg_setTreeHidingRadius(_RADIUS, _RADIUS_ALPHA)
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChanged
        if self.killCamCtrl:
            self.killCamCtrl.onRespawnRequested += self.__onVehicleRespawn
        self.__simulatedScene.onAllVehiclesLoaded += self.__onAllVehiclesLoaded
        self.__simulatedScene.onSimulatedSceneHasEnded += self.__simulatedSceneEnded
        self._changeKillCamModeState(DeathCamEvent.State.INACTIVE)
        super(KillCamMode, self).enable(**kwargs)
        return

    def disable(self, smoothFade=True):
        super(KillCamMode, self).disable(smoothFade)
        self.__isLeaveKillCamWhenPrepared = False
        self._rawSimulationData = None
        self.__vehicleRespawnTriggered = False
        self.__isAutoRespawnScheduled = False
        self.__simulatedScene.onAnimationsCompleted -= self.__onVehicleAnimationFinished
        self.__simulatedScene.disableScene()
        BigWorld.wg_setHideEdges(False)
        respawnCtrl = self.guiSessionProvider.dynamic.respawn
        if respawnCtrl is not None:
            respawnCtrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdate
        if self.__bFadeScreenActive:
            self.__fadeScreen(False, _LEAVE_KILLER_VISION_FADE_TIME if smoothFade else 0.0)
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChanged
        if self.killCamCtrl:
            self.killCamCtrl.onRespawnRequested -= self.__onVehicleRespawn
        self.__simulatedScene.onAllVehiclesLoaded -= self.__onAllVehiclesLoaded
        self.__simulatedScene.onSimulatedSceneHasEnded -= self.__simulatedSceneEnded
        if self.killCamState not in (DeathCamEvent.State.NONE, DeathCamEvent.State.FINISHED):
            self._changeKillCamModeState(DeathCamEvent.State.FINISHED)
        uniprof.exitFromRegion('avatar.control_mode.kill_cam')
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        handledInBase = super(KillCamMode, self).handleKeyEvent(isDown, key, mods, event)
        if handledInBase:
            return True
        if key == Keys.KEY_ESCAPE and isDown:
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPaused:
                replayCtrl.resetPlaybackSpeedIdx()
            if self.killCamState in DeathCamEvent.SIMULATION_INCL_FADES:
                self.__fadeAndLeaveKillCam(isInterrupted=True)
                return True
            self.__isLeaveKillCamWhenPrepared = True
        if BattleReplay.g_replayCtrl.isPlaying:
            return self.handleReplayKeyEvent(isDown, key)
        if key == Keys.KEY_SPACE and isDown:
            if self.killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
                self.togglePauseKillCam()
                return True
        return False

    def handleReplayKeyEvent(self, isDown, key):
        replayCtrl = BattleReplay.g_replayCtrl
        isReplayPaused = replayCtrl.isPlaying and replayCtrl.isPaused
        if key == Keys.KEY_SPACE and isDown:
            if self.killCamState not in DeathCamEvent.SIMULATION_EXCL_FADES:
                if isReplayPaused:
                    replayCtrl.resetPlaybackSpeedIdx()
                else:
                    replayCtrl.setPlaybackSpeedIdx(0)
            elif self.killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
                self.togglePauseKillCam()
            return True
        if key == Keys.KEY_RIGHTARROW and not isDown:
            if self.killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
                self.__fadeAndLeaveKillCam(isInterrupted=True)
                if isReplayPaused:
                    replayCtrl.resetPlaybackSpeedIdx()
                return True
        return False

    def handleMouseEvent(self, dx, dy, dz):
        self._cam.update(dx, dy, math_utils.clamp(-1, 1, dz))
        GUI.mcursor().position = Math.Vector2(0, 0)
        return True

    def isSelfVehicle(self):
        return False

    def togglePauseKillCam(self):
        if self.killCamState == DeathCamEvent.State.ENDING:
            return
        replayCtrl = BattleReplay.g_replayCtrl
        isPauseCooldownActive = BigWorld.time() - self.__lastTimePauseToggled < _PAUSE_BUTTON_COOLDOWN
        isReplayPaused = replayCtrl.isPlaying and replayCtrl.isPaused
        if not isReplayPaused and isPauseCooldownActive:
            return
        self.__lastTimePauseToggled = BigWorld.time()
        if self.killCamState == DeathCamEvent.State.RESUME or self.killCamState == DeathCamEvent.State.ACTIVE:
            self._changeKillCamModeState(DeathCamEvent.State.PAUSE)
            if replayCtrl.isPlaying:
                replayCtrl.setPlaybackSpeedIdx(0)
            self.__pauseResumeChanged(True)
        elif self.killCamState == DeathCamEvent.State.PAUSE:
            self._changeKillCamModeState(DeathCamEvent.State.RESUME)
            if replayCtrl.isPlaying:
                replayCtrl.resetPlaybackSpeedIdx(allowResetToZero=True)
            self.__pauseResumeChanged(False)
        else:
            _logger.error("KillCamMode: Pausing kill cam during phase when it's not allowed")

    def _handleModeExecution(self):
        _logger.info('[KillCamCtrlMode] _handleModeExecution()')
        waitTime = 0.0
        if not BigWorld.player().isPostmortemFeatureEnabled(CTRL_MODE_NAME.LOOK_AT_KILLER):
            self._tryDecrementWheeledDeathCounter(self._victimVehicleID)
            waitTime = _KILL_CAM_WAIT_TIME + _LOOK_AT_KILLER_SUBSTITUTE_WAIT_TIME - _PREPARE_KILLER_VISION_FADE_TIME
        self.delayCallback(waitTime, self.__initializeSimulationData)

    @noexcept
    def _leaveMode(self):
        _logger.info('[KillCamCtrlMode] _leaveMode()')
        if self.killCamCtrl:
            self.killCamCtrl.simulationSceneActive(False)
        self.clearCallbacks()
        self.__simulatedScene.onAnimationsCompleted -= self.__onVehicleAnimationFinished
        self.__simulatedScene.disableScene()
        self._cam.disable()

    def _canSkipKillCamera(self):
        if not BigWorld.player().isPostmortemFeatureEnabled(CTRL_MODE_NAME.LOOK_AT_KILLER):
            if not super(KillCamMode, self)._canSkipKillCamera():
                return False
        if self.killCamState in DeathCamEvent.SIMULATION_EXCL_FADES or self.killCamState == DeathCamEvent.State.ENDING:
            return False
        return False if self.__bFadeScreenActive else True

    def _switchToCtrlMode(self, targetMode, **kwargs):
        if self.killCamState == DeathCamEvent.State.PREPARING:
            return
        super(KillCamMode, self)._switchToCtrlMode(targetMode, **kwargs)

    def _checkSimulationAvailability(self):
        avatar = BigWorld.player()
        vehicle = avatar.vehicle
        if vehicle is None:
            vehicle = BigWorld.entity(avatar.playerVehicleID)
        availability, simulationData = super(KillCamMode, self)._checkSimulationAvailability()
        if availability is not SimulationAvailability.AVAILABLE:
            return (availability, None)
        elif avatar.arenaExtraData.get('isRandomEventsAllowed', False):
            _logger.info('Skip DeathCam scene because Random Events are not supported')
            return (SimulationAvailability.NOT_SUPPORTED_MODE, None)
        elif not self.killCamCtrl:
            _logger.warning("DeathCam is enabled but can't find killCamCtrl")
            return (SimulationAvailability.NOT_SUPPORTED_MODE, None)
        if 'VehicleRespawnComponent' in vehicle.dynamicComponents:
            delay = vehicle.dynamicComponents.get('VehicleRespawnComponent').delay
            if 0 < delay < self._skipNotEnoughTimeForDC:
                _logger.info('Not enough time to show DeathCam before respawn!')
                return (SimulationAvailability.NOT_ENOUGH_TIME, None)
        battleFieldCtrl = self.guiSessionProvider.dynamic.battleField
        if not battleFieldCtrl:
            _logger.error('Error, battle field controller not available')
            return (SimulationAvailability.NOT_AVAILABLE_MISSING_DATA, None)
        elif not self.__isDistanceFarEnough(simulationData):
            _logger.info('Skip KillerVision because vehicles are too close to each other')
            return (SimulationAvailability.VEHICLES_TOO_CLOSE, None)
        else:
            return (SimulationAvailability.AVAILABLE, simulationData)

    def _validateRawSimulationData(self, rawSimulationData):
        if not super(KillCamMode, self)._validateRawSimulationData(rawSimulationData):
            return False
        playerData = rawSimulationData.get('player', None)
        projectileData = rawSimulationData.get('projectile', None)
        unspottedOrigin = rawSimulationData.get('unspottedOrigin', None)
        if not playerData or not projectileData:
            _logger.error('_validateRawSimulationData():Missing playerData %s, projectileData %s, or unspottedOrigin %s', playerData, projectileData, unspottedOrigin)
            return False
        else:
            return True

    def __onSwitchToPostmortem(self, noRespawnPossible, respawnAvailable):
        _logger.info('[KillCamCtrlMode]: __onSwitchToPostmortem: saving kill snapshot')
        self.__simulatedScene.saveKillSnapshot()

    def __initializeSimulationData(self):
        simulationAvailability, self._rawSimulationData = self._checkSimulationAvailability()
        if simulationAvailability != SimulationAvailability.AVAILABLE:
            self.__skipKillCam(simulationAvailability)
            return
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isControllingCamera:
            BattleReplay.g_replayCtrl.stopCameraControl()
        self._trajectoryPoints = self._rawSimulationData['trajectoryData']
        self.__unspottedOrigin = self._rawSimulationData['unspottedOrigin']
        projectile = self._rawSimulationData['projectile']
        shotID = projectile['shotID'] if 'shotID' in projectile else 0
        self.__simulatedScene.setPendingShotID(shotID)
        self._postmortemKwargs['bPostmortemDelay'] = False
        self.__fadeAndPrepareKillCamData()

    def __skipKillCam(self, simulationAvailability):
        _logger.info('[KillCamCtrlMode] __skipKillCam()')
        suicide = self._killerVehicleID == self._victimVehicleID
        isKillerSpotted = BigWorld.entity(self._killerVehicleID) is not None
        if not suicide and isKillerSpotted:
            self._postmortemKwargs['keepCameraSettings'] = True
        if suicide or simulationAvailability == SimulationAvailability.NOT_AVAILABLE_END_OF_BATTLE:
            self._postmortemKwargs['bPostmortemDelay'] = False
        self._leaveMode()
        return

    def __fadeAndPrepareKillCamData(self):
        uniprof.exitFromRegion('avatar.control_mode.kill_cam.initialCamera')
        if self.__isLeaveKillCamWhenPrepared or not self._canShowKillerVisionInPeriod() or not self._areBothTeamsAlive():
            _logger.info('[KillCamCtrlMode] __fadeAndPrepareKillCamData: Battle ended while preparing')
            self._leaveMode()
            return
        self._changeKillCamModeState(DeathCamEvent.State.PREPARING)
        BigWorld.wg_setHideEdges(True)
        self.__fadeScreen(True, _PREPARE_KILLER_VISION_FADE_TIME)
        self.delayCallback(_PREPARE_KILLER_VISION_FADE_TIME, self.__prepareAnimationsAndCam)

    def __prepareAnimationsAndCam(self):
        self.__simulatedScene.onAnimationsCompleted += self.__onVehicleAnimationFinished
        self.__simulatedScene.enableScene(self._rawSimulationData, self._trajectoryPoints, self._killerIsSpotted)
        self.__simulatedKillerID = self.__simulatedScene.simulatedKillerID
        self.__simulatedVictimID = self.__simulatedScene.simulatedVictimID
        self._cam.trajectoryPoints = self._trajectoryPoints
        self._cam.playerHuskID = self.__simulatedVictimID
        self._changeKillCamModeState(DeathCamEvent.State.STARTING)

    def __onAllVehiclesLoaded(self):
        self.delayCallback(_START_VISION_DELAY, self.__startKillCamSimulation)

    def __startKillCamSimulation(self):
        if self.__isLeaveKillCamWhenPrepared:
            self._leaveMode()
            return
        self.killCamCtrl.simulationSceneActive(True)
        self.__fadeScreen(False, _SHOW_KILLER_VISION_FADE_TIME)
        projectileData = self._rawSimulationData['projectile']
        self._cam.projectileTriNorm = self._rawSimulationData['projectile']['triNormal']
        self._cam.hasProjectilePierced = self._rawSimulationData['projectile']['hasProjectilePierced']
        self._cam.hasNonPiercedDamage = self._rawSimulationData['projectile']['hasNonPiercedDamage']
        self._cam.isSPG = self._rawSimulationData['attacker']['vehicleType'] == 'SPG'
        impactType = self._rawSimulationData['projectile']['impactType']
        if impactType == constants.IMPACT_TYPES.LEGACY_HE:
            self.delayCallback(_SHOW_KILLER_VISION_FADE_TIME, self.__enableEdgeDrawing)
        if self._killerIsSpotted:
            self.__simulatedScene.startAnimations(projectileData['shotID'])
        self.__notifyKillCamCtrl()
        uniprof.enterToRegion('avatar.control_mode.kill_cam.vision')
        if self._killerIsSpotted:
            self._cam.startKillerVision(self.__simulatedKillerID, self.__simulatedVictimID, self.__isRicochet, projectileData, self.__fadeAndLeaveKillCam)
        else:
            self._cam.startPlayerVision(projectileData, self.__fadeAndLeaveKillCam)
            self.__displayKillCamAnimationEffects()
        self._changeKillCamModeState(DeathCamEvent.State.ACTIVE)

    def __notifyKillCamCtrl(self):
        phase1Duration, phase2Duration, phase3Duration, totalSceneDuration = self._cam.calculatePhaseDurations(self._killerIsSpotted)
        phaseDurations = (phase1Duration, phase2Duration, phase3Duration)
        projectileData = self._rawSimulationData['projectile']
        playerRelativeArmor = self._rawSimulationData['player']['relativeArmor']
        hasSpottedData = self._rawSimulationData['attacker']['hasSpottedData']
        playerIsSpotted = self._rawSimulationData['player']['victimIsNotSpotted']
        causeOfDeath = self._rawSimulationData['player']['causeOfDeath']
        simulatedKiller = BigWorld.entity(self.__simulatedKillerID) if self.__simulatedKillerID else None
        if simulatedKiller:
            simulatedKillerGunInfo = (simulatedKiller.gunJointMatrix, simulatedKiller.gunFireMatrix)
        else:
            simulatedKillerGunInfo = None
        self.killCamCtrl.killCamModeActive(self.__unspottedOrigin, simulatedKillerGunInfo, projectileData, phaseDurations, hasSpottedData, simulatedKiller is not None, playerRelativeArmor, playerIsSpotted, totalSceneDuration - _START_VISION_DELAY, causeOfDeath)
        return

    def __fadeScreen(self, bFade=True, duration=1.0):
        if self.__bFadeScreenActive == bFade:
            return
        self.__bFadeScreenActive = bFade
        if BigWorld.WGRenderSettings().getPosteffectsSettings() == 4:
            self.__startBlackScreen(bFade, duration)
        else:
            self.__startScreenFade(bFade, duration)

    def __startScreenFade(self, isFadeToBlack, duration):
        if isFadeToBlack:
            BigWorld.WGRenderSettings().setFadeParams(Math.Vector4(0, 0, 0, 1.0), duration)
        else:
            BigWorld.WGRenderSettings().setFadeParams(Math.Vector4(0, 0, 0, 0.0), duration)

    def __startBlackScreen(self, isFadeToBlack, duration):
        if self.killCamState == DeathCamEvent.State.PREPARING:
            self.delayCallback(duration, self.__setBlackScreen, isFadeToBlack)
            return
        self.__setBlackScreen(isFadeToBlack)

    def __setBlackScreen(self, isFadeToBlack):
        if isFadeToBlack:
            BigWorld.wg_enableGUIBackground(True, False)
            BigWorld.wg_setGUIBackground(_BLACK_BG_IMG)
        else:
            BigWorld.wg_enableGUIBackground(False, False)

    def __enableEdgeDrawing(self):
        BigWorld.wg_setHideEdges(False)

    def __fadeAndLeaveKillCam(self, isInterrupted=False):
        uniprof.exitFromRegion('avatar.control_mode.kill_cam.vision')
        if self.killCamState == DeathCamEvent.State.ENDING or self.killCamState == DeathCamEvent.State.FINISHED:
            return
        if isInterrupted and self.killCamCtrl:
            self.killCamCtrl.killCamInterrupted()
        self.__simulatedScene.hideEdgeEffects()
        self.__fadeScreen(True, _LEAVE_KILLER_VISION_FADE_TIME)
        self.delayCallback(_LEAVE_KILLER_VISION_FADE_TIME, self._leaveMode)
        self._changeKillCamModeState(DeathCamEvent.State.ENDING)

    def __simulatedSceneEnded(self):
        if self._postmortemKwargs is None:
            return
        else:
            self.__enableEdgeDrawing()
            self._rawSimulationData = None
            if self.killCamState not in DeathCamEvent.BEFORE_SIMULATION:
                self.__fadeScreen(False, _SHOW_DEAD_TANK_FADE_TIME)
            self._changeKillCamModeState(DeathCamEvent.State.FINISHED)
            if self.__vehicleRespawnTriggered:
                ownVehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID, None)
                vehRespComponent = ownVehicle and ownVehicle.dynamicComponents.get('VehicleRespawnComponent')
                if vehRespComponent:
                    vehRespComponent.waitForRespawnReadiness()
                else:
                    _logger.error('[KillCamMode] VehicleRespawnComponent not found!')
                return
            targetMode = BigWorld.player().getNextControlMode()
            if self._postmortemKwargs.get('keepCameraSettings', False):
                self._postmortemKwargs['pivotSettings'] = self.camera.getPivotSettings()
                self._postmortemKwargs['distanceFromFocus'] = self.camera.aimingSystem.distanceFromFocus
            self._aih.onControlModeChanged(targetMode, **self._postmortemKwargs)
            self._cam.resetCamera()
            return

    def __displayKillCamAnimationEffects(self):
        isSpotted = self._killerIsSpotted
        self.__simulatedScene.displayEffects(self.__simulatedVictimID)
        self.killCamCtrl.killCamModeEffectsPlaced(isSpotted)
        if _PARTICLES_DURATION_AFTER_SHOT <= 0.0:
            return
        BigWorld.wg_setWorldTimeScale(1.0 / ANIMATION_DURATION_BEFORE_SHOT)
        self.delayCallback(_PARTICLES_DURATION_AFTER_SHOT, self.__stopParticlesAfterShot)

    def __stopParticlesAfterShot(self):
        self.__simulatedScene.updateParticlesTimeScale()

    def __pauseResumeChanged(self, pause):
        self.__simulatedScene.pauseOrResumeAnimations(pause)
        self._cam.userInterruption(pause)

    def __onVehicleAnimationFinished(self):
        self.__simulatedScene.onAnimationsCompleted -= self.__onVehicleAnimationFinished
        self.__simulatedScene.updateParticlesTimeScale()
        self.__displayKillCamAnimationEffects()

    def __onArenaPeriodChanged(self, period, *args):
        if period != ARENA_PERIOD.AFTERBATTLE or BattleReplay.g_replayCtrl.isPlaying:
            return
        if self.killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
            self.__fadeAndLeaveKillCam()
        elif self.killCamState == DeathCamEvent.State.PREPARING:
            self.__isLeaveKillCamWhenPrepared = True
        else:
            self._leaveMode()

    def __onRespawnInfoUpdate(self, respawnInfo):
        if respawnInfo is not None and not self.__isAutoRespawnScheduled:
            self.__isAutoRespawnScheduled = True
            killCamSceneUntilNow = int(BigWorld.time() - self._modeEnteredTime)
            autoRespawnTimeLeft = int(respawnInfo.autoRespawnTime - BigWorld.serverTime())
            forcedExitTime = autoRespawnTimeLeft - _SKIP_KILL_CAM_BEFORE_AUTORESPAWN_TIME - killCamSceneUntilNow
            self.delayCallback(forcedExitTime, self.__forceExitKillCamScene)
        return

    def __onVehicleRespawn(self):
        self.__vehicleRespawnTriggered = True
        self.__forceExitKillCamScene()

    def __forceExitKillCamScene(self):
        self.__fadeAndLeaveKillCam()

    def __isDistanceFarEnough(self, simulationData):
        if not simulationData['attacker']['spotted']:
            return True
        attackerPosition = simulationData['attacker']['position']
        victimPosition = simulationData['player']['position']
        return (victimPosition - attackerPosition).length > self.__skipKillCamDistance


class LookAtKillerMode(KillModeBase):

    def _handleModeExecution(self):
        _logger.info('[LookAtKillerMode] _handleModeExecution()')
        self.delayCallback(_KILL_CAM_WAIT_TIME, self.__handleLookAtKillerFlow)

    def _leaveMode(self):
        _logger.info('[LookAtKillerMode] _leaveMode()')
        targetMode = BigWorld.player().getNextControlMode()
        self._postmortemKwargs['previousCam'] = self._cam
        self._aih.onControlModeChanged(targetMode, **self._postmortemKwargs)
        self._cam.resetCamera()

    def __handleLookAtKillerFlow(self):
        availability, self._rawSimulationData = self._checkSimulationAvailability()
        if availability == SimulationAvailability.AVAILABLE:
            self._trajectoryPoints = self._rawSimulationData.get('trajectoryData')
        self.__startCameraRotation(availability)

    def __startCameraRotation(self, simAvailability):
        suicide = self._killerVehicleID == self._victimVehicleID
        enemySpottedInsideAOI = BigWorld.entity(self._killerVehicleID) is not None
        waitTime = LOOK_AT_KILLER_DURATION - _PREPARE_KILLER_VISION_FADE_TIME if simAvailability == SimulationAvailability.AVAILABLE else _TIME_BEFORE_FOLLOW_TANK
        isFirstTenDeathWheeledTank = self._isFirstTenDeathsWheeledTank(self._victimVehicleID)
        if isFirstTenDeathWheeledTank and simAvailability != SimulationAvailability.AVAILABLE:
            self._tryDecrementWheeledDeathCounter(self._victimVehicleID)
            waitTime = _WHEELED_VEHICLE_POSTMORTEM_DELAY
        if not suicide:
            if (simAvailability == SimulationAvailability.NOT_KILLED_BY_SHOT or simAvailability == SimulationAvailability.NOT_AVAILABLE_MISSING_DATA) and not isFirstTenDeathWheeledTank:
                waitTime = _LOOK_AT_KILLER_DURATION_LEGACY
            self.__handleCameraRotation(enemySpottedInsideAOI=enemySpottedInsideAOI, killerIsSpotted=self._killerIsSpotted)
        if suicide or simAvailability == SimulationAvailability.NOT_AVAILABLE_END_OF_BATTLE:
            self._postmortemKwargs['bPostmortemDelay'] = False
        self.delayCallback(waitTime, self._leaveMode)
        return

    def __handleCameraRotation(self, enemySpottedInsideAOI=False, killerIsSpotted=False):
        _logger.info('[LookAtKillerMode] __handleCameraRotation()')
        if enemySpottedInsideAOI:
            self._cam.setCameraToLookTowards(sourceVehicleID=self._victimVehicleID, targetVehicleID=self._killerVehicleID, mode=StartCamDirection.TOWARDS_TARGET, isInstant=False)
        elif killerIsSpotted:
            self._cam.setCameraToLookTowards(sourceVehicleID=self._victimVehicleID, targetVehicleID=None, firstPoint=self._trajectoryPoints[0], lastPoint=self._trajectoryPoints[-1], isInstant=False)
        else:
            self._cam.setCameraToLookTowards(sourceVehicleID=self._victimVehicleID, targetVehicleID=None, firstPoint=self._trajectoryPoints[0], lastPoint=self._trajectoryPoints[-1], isInstant=False, originatesFromVehicle=False)
        return
