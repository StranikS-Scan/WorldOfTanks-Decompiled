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
from AvatarInputHandler.kill_cam_mode_helpers.kill_cam_helpers import calculateSPGTrajectory
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
_NO_SKIP_DEATH_CAM_DURATION = 2.0
_UNSPOTTED_PIVOT_DISTANCE_FACTOR = 12
_UNSPOTTED_MARKER_DISTANCE_FACTOR = 4
_PAUSE_BUTTON_COOLDOWN = 0.5
_SKIP_KILL_CAM_BEFORE_AUTORESPAWN_TIME = 15
_RADIUS = 10
_RADIUS_ALPHA = 2
_BLOCKED_KEYS = {Keys.KEY_LCONTROL,
 Keys.KEY_RCONTROL,
 Keys.KEY_T,
 Keys.KEY_M,
 Keys.KEY_B,
 Keys.KEY_N}
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
    NOT_AVAILABLE = (NOT_AVAILABLE_MISSING_DATA,
     NOT_AVAILABLE_END_OF_BATTLE,
     VEHICLES_TOO_CLOSE,
     NOT_KILLED_BY_SHOT,
     NOT_SUPPORTED_MODE)


class KillCamMode(IControlMode, CallbackDelayer):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, dataSection, avatarInputHandler):
        super(KillCamMode, self).__init__()
        CallbackDelayer.__init__(self)
        self._isForcedExitActive = False
        self.__modeEnteredTime = -1
        self.__postmortemKwargs = None
        self.__isLeaveKillCamWhenPrepared = False
        self.__bFadeScreenActive = False
        self.__isRespawnActive = False
        self.__lastTimePauseToggled = 0.0
        self.__victimVehicleID = None
        self.__killerVehicleID = None
        self.__simulatedVictimID = None
        self.__simulatedKillerID = None
        self.__killCamState = DeathCamEvent.State.NONE
        self.__trajectoryPoints = []
        self.__unspottedOrigin = None
        self.__rawSimulationData = None
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__cam = KillCamera(dataSection['camera'], dataSection.readVector2('defaultOffset'))
        self._cameraTransitionDurations = _readCameraTransitionSettings(dataSection['camera'])
        self.__simulatedScene = SimulatedScene(dataSection['deathCamPostProcessEffects'])
        self.__skipKillCamDistance = dataSection.readFloat('skipKillCamVehiclesDistance')
        self.__skipBattleTimeLeft = dataSection.readFloat('skipBattleTimeLeft')
        return

    @property
    def __killerIsSpotted(self):
        return self.__rawSimulationData['attacker'] and self.__rawSimulationData['attacker']['spotted']

    @property
    def __isRicochet(self):
        return self.__rawSimulationData['projectile']['ricochetCount'] > 0

    @property
    def camera(self):
        return self.__cam

    @property
    def curVehicleID(self):
        return self.__victimVehicleID

    @property
    def killCamState(self):
        return self.__killCamState

    def create(self):
        self.__cam.create(onChangeControlMode=None, postmortemMode=True, smartPointCalculator=True)
        self.__simulatedScene.create()
        return

    def destroy(self):
        self.disable(smoothFade=False)
        self.__cam.destroy()
        self.__cam = None
        self.__aih = None
        self.__simulatedScene.destroy()
        self.__simulatedScene = None
        self.clearCallbacks()
        return

    def enable(self, **kwargs):
        uniprof.enterToRegion('avatar.control_mode.kill_cam')
        _logger.info('[KillCamCtrlMode] Kill Cam is Enabled')
        avatar = BigWorld.player()
        if avatar is None:
            _logger.error('Avatar is None, cannot enter Kill Camera mode.')
            return
        else:
            self.__simulatedScene.saveKillSnapshot()
            self.__victimVehicleID = avatar.playerVehicleID
            respawnCtrl = self.guiSessionProvider.dynamic.respawn
            self.__isRespawnActive = respawnCtrl is not None
            if self.__isRespawnActive:
                self._isForcedExitActive = False
                respawnCtrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdate
            BigWorld.wg_setTreeHidingRadius(_RADIUS, _RADIUS_ALPHA)
            self.__modeEnteredTime = BigWorld.time()
            self.__postmortemKwargs = kwargs
            self.__postmortemKwargs['newVehicleID'] = BigWorld.player().playerVehicleID
            vehicleMProv = avatar.consistentMatrices.attachedVehicleMatrix
            camAngles = None
            pivotSettings = None
            previousCam = None
            isInArcadeZoomState = False
            if 'previousCam' in kwargs:
                camAngles = getattr(kwargs['previousCam'], 'angles', None)
                previousCam = kwargs['previousCam']
                if isinstance(previousCam, ArcadeCamera):
                    pivotSettings = previousCam.aimingSystem.getPivotSettings()
                    isInArcadeZoomState = previousCam.isInArcadeZoomState()
            if previousCam is None or not isInArcadeZoomState or pivotSettings is None:
                pivotSettings = PostmortemDelay.KILLER_VEHICLE_CAMERA_PIVOT_SETTINGS
            self.__cam.enable(vehicleMProv=vehicleMProv, preferredPos=camAngles, initialPivotSettings=pivotSettings)
            g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChanged
            self.__simulatedScene.onAllVehiclesLoaded += self.__onAllVehiclesLoaded
            self.__simulatedScene.onSimulatedSceneHasEnded += self.__simulatedSceneEnded
            killerVehicleID = self.__aih.getKillerVehicleID()
            deathReason = self.__aih.getDeathReason()
            if killerVehicleID is None and deathReason is None:
                self.__aih.onReceivedKillerID += self.__onReceiveKillerID
            else:
                self.__onReceiveKillerID(killerVehicleID)
            self.__changeKillCamModeState(DeathCamEvent.State.INACTIVE)
            return

    def disable(self, smoothFade=True):
        _logger.info('[KillCamCtrlMode] disable()')
        self.__isLeaveKillCamWhenPrepared = False
        self.__postmortemKwargs = None
        self.__rawSimulationData = None
        self.__cam.disable()
        self.__modeEnteredTime = -1
        self.__simulatedScene.onAnimationsCompleted -= self.__onVehicleAnimationFinished
        self.__simulatedScene.disableScene()
        self.clearCallbacks()
        BigWorld.wg_setHideEdges(False)
        if self.__isRespawnActive:
            respawnCtrl = self.guiSessionProvider.dynamic.respawn
            if respawnCtrl is not None:
                respawnCtrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdate
        if self.__bFadeScreenActive:
            self.__fadeScreen(smoothFade, _LEAVE_KILLER_VISION_FADE_TIME if smoothFade else 0.0)
        self.__aih.onReceivedKillerID -= self.__onReceiveKillerID
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChanged
        self.__simulatedScene.onAllVehiclesLoaded -= self.__onAllVehiclesLoaded
        self.__simulatedScene.onSimulatedSceneHasEnded -= self.__simulatedSceneEnded
        if self.__killCamState not in (DeathCamEvent.State.NONE, DeathCamEvent.State.FINISHED):
            self.__changeKillCamModeState(DeathCamEvent.State.FINISHED)
        uniprof.exitFromRegion('avatar.control_mode.kill_cam')
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if key in _BLOCKED_KEYS or CM.g_instance.isFiredList(_BLOCKED_ACTIONS, key):
            return True
        if key == Keys.KEY_ESCAPE and isDown:
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPaused:
                replayCtrl.resetPlaybackSpeedIdx()
            if self.__killCamState in DeathCamEvent.SIMULATION_INCL_FADES:
                self.__fadeAndLeaveKillCam()
                if self.guiSessionProvider.shared.killCamCtrl:
                    self.guiSessionProvider.shared.killCamCtrl.killCamInterrupted()
                return True
            self.__isLeaveKillCamWhenPrepared = True
        if BattleReplay.g_replayCtrl.isPlaying:
            return self.handleReplayKeyEvent(isDown, key)
        if key == Keys.KEY_SPACE and isDown:
            if self.__killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
                self.togglePauseKillCam()
                return True
        if CM.g_instance.isFired(CM.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown and self.__canSkipKillCamera():
            self._switchToCtrlMode(CTRL_MODE_NAME.DEATH_FREE_CAM)
            return True
        if self.__killCamState == DeathCamEvent.State.INACTIVE and key in (Keys.KEY_LEFTMOUSE, Keys.KEY_RIGHTMOUSE) and not isDown and BigWorld.time() - self.__modeEnteredTime > _NO_SKIP_DEATH_CAM_DURATION:
            avatar = BigWorld.player()
            targetMode = avatar.getNextControlMode()
            self._switchToCtrlMode(targetMode, immediateSwitchToAllyVehicle=avatar.canSwitchToAllyVehicle())
            return True
        return False

    def handleReplayKeyEvent(self, isDown, key):
        replayCtrl = BattleReplay.g_replayCtrl
        isReplayPaused = replayCtrl.isPlaying and replayCtrl.isPaused
        if key == Keys.KEY_SPACE and isDown:
            if self.__killCamState not in DeathCamEvent.SIMULATION_EXCL_FADES:
                if isReplayPaused:
                    replayCtrl.resetPlaybackSpeedIdx()
                else:
                    replayCtrl.setPlaybackSpeedIdx(0)
            elif self.__killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
                self.togglePauseKillCam()
            return True
        if key == Keys.KEY_RIGHTARROW and not isDown:
            if self.__killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
                self.__fadeAndLeaveKillCam()
                if self.guiSessionProvider.shared.killCamCtrl:
                    self.guiSessionProvider.shared.killCamCtrl.killCamInterrupted()
                    if isReplayPaused:
                        replayCtrl.resetPlaybackSpeedIdx()
                    return True
        return False

    def handleMouseEvent(self, dx, dy, dz):
        self.__cam.update(dx, dy, math_utils.clamp(-1, 1, dz))
        GUI.mcursor().position = Math.Vector2(0, 0)
        return True

    def isSelfVehicle(self):
        return False

    def togglePauseKillCam(self):
        if self.__killCamState == DeathCamEvent.State.ENDING:
            return
        replayCtrl = BattleReplay.g_replayCtrl
        isPauseCooldownActive = BigWorld.time() - self.__lastTimePauseToggled < _PAUSE_BUTTON_COOLDOWN
        isReplayPaused = replayCtrl.isPlaying and replayCtrl.isPaused
        if not isReplayPaused and isPauseCooldownActive:
            return
        self.__lastTimePauseToggled = BigWorld.time()
        if self.__killCamState == DeathCamEvent.State.RESUME or self.__killCamState == DeathCamEvent.State.ACTIVE:
            self.__changeKillCamModeState(DeathCamEvent.State.PAUSE)
            if replayCtrl.isPlaying:
                replayCtrl.setPlaybackSpeedIdx(0)
            self.__pauseResumeChanged(True)
        elif self.__killCamState == DeathCamEvent.State.PAUSE:
            self.__changeKillCamModeState(DeathCamEvent.State.RESUME)
            if replayCtrl.isPlaying:
                replayCtrl.resetPlaybackSpeedIdx(allowResetToZero=True)
            self.__pauseResumeChanged(False)
        else:
            _logger.error("KillCamMode: Pausing kill cam during phase when it's not allowed")

    def _switchToCtrlMode(self, targetMode, **kwargs):
        if self.__killCamState == DeathCamEvent.State.PREPARING:
            return
        else:
            if targetMode != CTRL_MODE_NAME.DEATH_FREE_CAM:
                self.selectPlayer(None)
            newVehicleID = BigWorld.player().playerVehicleID if targetMode in (CTRL_MODE_NAME.POSTMORTEM, CTRL_MODE_NAME.DEATH_FREE_CAM) else None
            BigWorld.player().inputHandler.onControlModeChanged(targetMode, prevModeName=CTRL_MODE_NAME.KILL_CAM, camMatrix=Math.Matrix(BigWorld.camera().matrix), curVehicleID=self.__victimVehicleID, newVehicleID=newVehicleID, transitionDuration=self._cameraTransitionDurations[targetMode], **kwargs)
            return

    def __onReceiveKillerID(self, vehicleID):
        self.__killerVehicleID = vehicleID
        playerVehicle = BigWorld.entities.get(self.__victimVehicleID)
        isDefinedPostmortemView = playerVehicle and playerVehicle.isPostmortemViewPointDefined
        if isDefinedPostmortemView:
            self.__leaveKillCam()
        else:
            self.delayCallback(_KILL_CAM_WAIT_TIME, self.__initializeSimulationData)

    def __isKillByShot(self):
        deathReasonID = BigWorld.player().inputHandler.getDeathReason()
        return deathReasonID is not None and ATTACK_REASONS[deathReasonID] in (ATTACK_REASON.SHOT, ATTACK_REASON.FIRE)

    def __initializeSimulationData(self):
        simulationAvailability, self.__rawSimulationData = self.__checkSimulationAvailability()
        if simulationAvailability != SimulationAvailability.AVAILABLE:
            self.__skipKillCam(simulationAvailability)
            return
        if BattleReplay.g_replayCtrl.isPlaying and BattleReplay.g_replayCtrl.isControllingCamera:
            BattleReplay.g_replayCtrl.stopCameraControl()
        self.__trajectoryPoints = self.__setupTrajectory()
        projectile = self.__rawSimulationData['projectile']
        shotID = projectile['shotID'] if 'shotID' in projectile else 0
        self.__simulatedScene.setPendingShotID(shotID, stopTracking=not self.__isRespawnActive)
        self.__startInitialCameraRotation()

    def __startInitialCameraRotation(self):
        uniprof.enterToRegion('avatar.control_mode.kill_cam.initialCamera')
        enemySpottedInsideAOI = BigWorld.entity(self.__killerVehicleID) is not None
        killerIsSpotted = self.__killerIsSpotted
        self.__handleCameraRotation(enemySpottedInsideAOI, killerIsSpotted)
        self.__postmortemKwargs['bPostmortemDelay'] = False
        self.__tryDecrementWheeledDeathCounter(self.__victimVehicleID)
        self.delayCallback(LOOK_AT_KILLER_DURATION - _PREPARE_KILLER_VISION_FADE_TIME, self.__fadeAndPrepareKillCamData)
        return

    def __handleCameraRotation(self, enemySpottedInsideAOI=False, killerIsSpotted=False):
        if enemySpottedInsideAOI:
            self.__cam.setCameraToLookTowards(sourceVehicleID=self.__victimVehicleID, targetVehicleID=self.__killerVehicleID, mode=StartCamDirection.TOWARDS_TARGET, isInstant=False)
        elif killerIsSpotted:
            self.__cam.setCameraToLookTowards(sourceVehicleID=self.__victimVehicleID, targetVehicleID=None, firstPoint=self.__trajectoryPoints[0], lastPoint=self.__trajectoryPoints[-1], isInstant=False)
        else:
            self.__cam.setCameraToLookTowards(sourceVehicleID=self.__victimVehicleID, targetVehicleID=None, firstPoint=self.__trajectoryPoints[0], lastPoint=self.__trajectoryPoints[-1], isInstant=False, originatesFromVehicle=False)
        return

    def __skipKillCam(self, simulationAvailability):
        suicide = self.__killerVehicleID == self.__victimVehicleID
        isKillerSpotted = BigWorld.entity(self.__killerVehicleID) is not None
        timeToWait = _TIME_BEFORE_FOLLOW_TANK
        isTenDeathWheeledTank = self.__isFirstTenDeathsWheeledTank(self.__victimVehicleID)
        if isTenDeathWheeledTank:
            self.__tryDecrementWheeledDeathCounter(self.__victimVehicleID)
            timeToWait = _WHEELED_VEHICLE_POSTMORTEM_DELAY
        if not suicide and isKillerSpotted:
            self.__handleCameraRotation(enemySpottedInsideAOI=True)
            if simulationAvailability == SimulationAvailability.NOT_KILLED_BY_SHOT or simulationAvailability == SimulationAvailability.NOT_AVAILABLE_MISSING_DATA:
                timeToWait = _WHEELED_VEHICLE_POSTMORTEM_DELAY if isTenDeathWheeledTank else _LOOK_AT_KILLER_DURATION_LEGACY
            self.__postmortemKwargs['keepCameraSettings'] = True
        if suicide or simulationAvailability == SimulationAvailability.NOT_AVAILABLE_END_OF_BATTLE:
            self.__postmortemKwargs['bPostmortemDelay'] = False
        self.delayCallback(timeToWait, self.__leaveKillCam)
        return

    def __fadeAndPrepareKillCamData(self):
        uniprof.exitFromRegion('avatar.control_mode.kill_cam.initialCamera')
        if self.__isLeaveKillCamWhenPrepared or not self.__canShowKillerVisionInPeriod() or not self.__areBothTeamsAlive():
            self.__leaveKillCam()
            return
        self.__changeKillCamModeState(DeathCamEvent.State.PREPARING)
        BigWorld.wg_setHideEdges(True)
        self.__fadeScreen(True, _PREPARE_KILLER_VISION_FADE_TIME)
        self.delayCallback(_PREPARE_KILLER_VISION_FADE_TIME, self.__prepareAnimationsAndCam)

    def __prepareAnimationsAndCam(self):
        self.__simulatedScene.onAnimationsCompleted += self.__onVehicleAnimationFinished
        self.__simulatedScene.enableScene(self.__rawSimulationData, self.__trajectoryPoints, self.__killerIsSpotted)
        self.__simulatedKillerID = self.__simulatedScene.simulatedKillerID
        self.__simulatedVictimID = self.__simulatedScene.simulatedVictimID
        self.__cam.trajectoryPoints = self.__trajectoryPoints
        self.__cam.playerHuskID = self.__simulatedVictimID
        self.__changeKillCamModeState(DeathCamEvent.State.STARTING)

    def __canShowKillerVisionInPeriod(self):
        periodCtrl = self.guiSessionProvider.shared.arenaPeriod
        if not periodCtrl:
            return False
        if BattleReplay.g_replayCtrl.isPlaying:
            return True
        isBattlePeriod = ARENA_PERIOD.BATTLE == periodCtrl.getPeriod()
        isTimeLeft = periodCtrl.getEndTime() - BigWorld.serverTime() > self.__skipBattleTimeLeft
        return isBattlePeriod and isTimeLeft

    def __areBothTeamsAlive(self):
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

    def __checkSimulationAvailability(self):
        avatar = BigWorld.player()
        vehicle = avatar.vehicle
        if vehicle is None:
            vehicle = BigWorld.entity(avatar.playerVehicleID)
        if not self.__canShowKillerVisionInPeriod() or not self.__areBothTeamsAlive():
            _logger.debug('Skip KillerVision because the battle ends in the next seconds or no-one is alive anymore')
            return (SimulationAvailability.NOT_AVAILABLE_END_OF_BATTLE, None)
        elif avatar.arenaExtraData.get('isRandomEventsAllowed', False):
            _logger.debug('Skip DeathCam scene because Random Events are not supported')
            return (SimulationAvailability.NOT_SUPPORTED_MODE, None)
        elif not self.__isKillByShot():
            _logger.debug("Player wasn't killed by shot")
            return (SimulationAvailability.NOT_KILLED_BY_SHOT, None)
        elif 'killCamData' not in vehicle.dynamicComponents:
            _logger.debug("Player doesn't have killCamData available")
            return (SimulationAvailability.NOT_AVAILABLE_MISSING_DATA, None)
        battleFieldCtrl = self.guiSessionProvider.dynamic.battleField
        if not battleFieldCtrl:
            _logger.error('Error, battle field controller not available')
            return (SimulationAvailability.NOT_AVAILABLE_MISSING_DATA, None)
        simulationData = self.__getRawSimulationData(vehicle)
        if not simulationData:
            _logger.debug('Skip KillerVision because no simulation data are available')
            return (SimulationAvailability.NOT_AVAILABLE_MISSING_DATA, None)
        elif not self.__isDistanceFarEnough(simulationData):
            _logger.debug('Skip KillerVision because vehicles are too close to each other')
            return (SimulationAvailability.VEHICLES_TOO_CLOSE, None)
        else:
            return (SimulationAvailability.AVAILABLE, simulationData)

    def __getRawSimulationData(self, vehicle):
        if not vehicle:
            _logger.error("__getRawSimulationData: Unable to get player's vehicle")
            return None
        else:
            rawSimulationData = vehicle.killCamData.getSimulationData()
            return rawSimulationData if self.__validateRawSimulationData(rawSimulationData) else None

    def __onAllVehiclesLoaded(self):
        self.delayCallback(_START_VISION_DELAY, self.__startKillCamSimulation)

    def __startKillCamSimulation(self):
        if self.__isLeaveKillCamWhenPrepared:
            self.__leaveKillCam()
            return
        killCamCtrl = self.guiSessionProvider.shared.killCamCtrl
        killCamCtrl.simulationSceneActive(True)
        self.__fadeScreen(False, _SHOW_KILLER_VISION_FADE_TIME)
        projectileData = self.__rawSimulationData['projectile']
        self.__cam.projectileTriNorm = self.__rawSimulationData['projectile']['triNormal']
        self.__cam.hasProjectilePierced = self.__rawSimulationData['projectile']['hasProjectilePierced']
        self.__cam.isSPG = self.__rawSimulationData['attacker']['vehicleType'] == 'SPG'
        impactType = self.__rawSimulationData['projectile']['impactType']
        if impactType == constants.IMPACT_TYPES.LEGACY_HE:
            self.delayCallback(_SHOW_KILLER_VISION_FADE_TIME, self.__enableEdgeDrawing)
        if self.__killerIsSpotted:
            self.__simulatedScene.startAnimations(projectileData['shotID'])
        self.__notifyKillCamCtrl()
        uniprof.enterToRegion('avatar.control_mode.kill_cam.vision')
        if self.__killerIsSpotted:
            self.__cam.startKillerVision(self.__simulatedKillerID, self.__simulatedVictimID, self.__isRicochet, projectileData, self.__fadeAndLeaveKillCam)
        else:
            self.__cam.startPlayerVision(projectileData, self.__fadeAndLeaveKillCam)
            self.__displayKillCamAnimationEffects()
        self.__changeKillCamModeState(DeathCamEvent.State.ACTIVE)

    def __notifyKillCamCtrl(self):
        phase1Duration, phase2Duration, phase3Duration, totalSceneDuration = self.__cam.calculatePhaseDurations(self.__killerIsSpotted)
        phaseDurations = (phase1Duration, phase2Duration, phase3Duration)
        projectileData = self.__rawSimulationData['projectile']
        playerRelativeArmor = self.__rawSimulationData['player']['relativeArmor']
        hasSpottedData = self.__rawSimulationData['attacker']['hasSpottedData']
        playerIsSpotted = self.__rawSimulationData['player']['victimIsNotSpotted']
        causeOfDeath = self.__rawSimulationData['player']['causeOfDeath']
        simulatedKiller = BigWorld.entity(self.__simulatedKillerID) if self.__simulatedKillerID else None
        if simulatedKiller:
            simulatedKillerGunInfo = (simulatedKiller.gunJointMatrix, simulatedKiller.gunFireMatrix)
        else:
            simulatedKillerGunInfo = None
        self.guiSessionProvider.shared.killCamCtrl.killCamModeActive(self.__unspottedOrigin, simulatedKillerGunInfo, projectileData, phaseDurations, hasSpottedData, simulatedKiller is not None, playerRelativeArmor, playerIsSpotted, totalSceneDuration - _START_VISION_DELAY, causeOfDeath)
        return

    @staticmethod
    def __validateRawSimulationData(rawSimulationData):
        if rawSimulationData is None:
            return False
        attackerData = rawSimulationData.get('attacker', None)
        playerData = rawSimulationData.get('player', None)
        projectileData = rawSimulationData.get('projectile', None)
        if not attackerData or not playerData or not projectileData:
            _logger.error('__validateRawSimulationData():Missing attackerData: %s, playerData %s or projectileData %s', attackerData, playerData, projectileData)
            return False
        else:
            return True

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
        if self.__killCamState == DeathCamEvent.State.PREPARING:
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

    def __fadeAndLeaveKillCam(self):
        uniprof.exitFromRegion('avatar.control_mode.kill_cam.vision')
        if self.__killCamState == DeathCamEvent.State.ENDING or self.__killCamState == DeathCamEvent.State.FINISHED:
            return
        self.__simulatedScene.hideEdgeEffects()
        self.__fadeScreen(True, _LEAVE_KILLER_VISION_FADE_TIME)
        self.delayCallback(_LEAVE_KILLER_VISION_FADE_TIME, self.__leaveKillCam)
        self.__changeKillCamModeState(DeathCamEvent.State.ENDING)

    @noexcept
    def __leaveKillCam(self):
        _logger.info('[KillCamCtrlMode] __leaveKillCam()')
        self.guiSessionProvider.shared.killCamCtrl.simulationSceneActive(False)
        self.stopCallback(self.__leaveKillCam)
        self.__simulatedScene.onAnimationsCompleted -= self.__onVehicleAnimationFinished
        self.__simulatedScene.disableScene()

    def __simulatedSceneEnded(self):
        if self.__postmortemKwargs is None:
            return
        else:
            self.__enableEdgeDrawing()
            self.__rawSimulationData = None
            if self.__killCamState not in DeathCamEvent.BEFORE_SIMULATION:
                self.__fadeScreen(False, _SHOW_DEAD_TANK_FADE_TIME)
            self.__changeKillCamModeState(DeathCamEvent.State.FINISHED)
            targetMode = BigWorld.player().getNextControlMode()
            if self.__postmortemKwargs.get('keepCameraSettings', False):
                self.__postmortemKwargs['pivotSettings'] = self.camera.getPivotSettings()
                self.__postmortemKwargs['distanceFromFocus'] = self.camera.aimingSystem.distanceFromFocus
            self.__aih.onControlModeChanged(targetMode, **self.__postmortemKwargs)
            self.__cam.resetCamera()
            return

    def __displayKillCamAnimationEffects(self):
        isSpotted = self.__killerIsSpotted
        self.__simulatedScene.displayEffects(self.__simulatedVictimID)
        self.guiSessionProvider.shared.killCamCtrl.killCamModeEffectsPlaced(isSpotted)
        if _PARTICLES_DURATION_AFTER_SHOT <= 0.0:
            return
        BigWorld.wg_setWorldTimeScale(1.0 / ANIMATION_DURATION_BEFORE_SHOT)
        self.delayCallback(_PARTICLES_DURATION_AFTER_SHOT, self.__stopParticlesAfterShot)

    def __stopParticlesAfterShot(self):
        self.__simulatedScene.updateParticlesTimeScale()

    def __pauseResumeChanged(self, pause):
        self.__simulatedScene.pauseOrResumeAnimations(pause)
        self.__cam.userInterruption(pause)

    def __onVehicleAnimationFinished(self):
        self.__simulatedScene.onAnimationsCompleted -= self.__onVehicleAnimationFinished
        self.__simulatedScene.updateParticlesTimeScale()
        self.__displayKillCamAnimationEffects()

    def __setupTrajectory(self):
        projectileData = self.__rawSimulationData['projectile']
        origin = Math.Vector3(projectileData['origin'])
        impactPoint = Math.Vector3(projectileData['impactPoint'])
        gravity = Math.Vector3(0.0, -projectileData['gravity'], 0.0)
        self.__unspottedOrigin = None
        if not self.__killerIsSpotted:
            directionVector = origin - impactPoint
            directionVector *= 1 / directionVector.length
            self.__unspottedOrigin = impactPoint + directionVector * _UNSPOTTED_MARKER_DISTANCE_FACTOR
            origin = impactPoint + directionVector * _UNSPOTTED_PIVOT_DISTANCE_FACTOR
        elif self.__rawSimulationData['attacker']['vehicleType'] == 'SPG':
            velocity = Math.Vector3(projectileData['velocity'])
            trajectoryPoints = calculateSPGTrajectory(origin, impactPoint, velocity, gravity)
            if self.__killerIsSpotted:
                return trajectoryPoints
            trajectoryEndVector = Math.Vector3(trajectoryPoints[-1] - trajectoryPoints[-2])
            halfLength = trajectoryEndVector.length / 2.0
            trajectoryEndVector.normalise()
            trajectoryPoints = [trajectoryPoints[-2] + trajectoryEndVector * halfLength, trajectoryPoints[-1]]
            self.__unspottedOrigin = trajectoryPoints[-2]
            return trajectoryPoints
        if self.__isRicochet:
            ricochetPoint = projectileData['ricochetPoint']
            return [origin, ricochetPoint, impactPoint]
        else:
            return [origin, impactPoint]

    def __onArenaPeriodChanged(self, period, *args):
        if period != ARENA_PERIOD.AFTERBATTLE or BattleReplay.g_replayCtrl.isPlaying:
            return
        if self.__killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
            self.__fadeAndLeaveKillCam()
        elif self.__killCamState == DeathCamEvent.State.PREPARING:
            self.__isLeaveKillCamWhenPrepared = True
        else:
            self.__leaveKillCam()

    def __onRespawnInfoUpdate(self, respawnInfo):
        if respawnInfo is not None and not self._isForcedExitActive:
            self._isForcedExitActive = True
            killCamSceneUntilNow = int(BigWorld.time() - self.__modeEnteredTime)
            autoRespawnTimeLeft = int(respawnInfo.autoRespawnTime - BigWorld.serverTime())
            forcedExitTime = autoRespawnTimeLeft - _SKIP_KILL_CAM_BEFORE_AUTORESPAWN_TIME - killCamSceneUntilNow
            self.delayCallback(forcedExitTime, self.__forceExitKillCamScene)
        return

    def __forceExitKillCamScene(self):
        if self.__killCamState in DeathCamEvent.SIMULATION_EXCL_FADES:
            _logger.debug('Forcing killcam scene end due to auto respawn')
            self.__fadeAndLeaveKillCam()

    def __changeKillCamModeState(self, newState):
        self.__killCamState = newState
        _logger.info('KillCamMode: Kill Cam State changed to: %s', self.__killCamState)
        self.guiSessionProvider.shared.killCamCtrl.changeKillCamModeState(self.__killCamState)

    def __isDistanceFarEnough(self, simulationData):
        if not simulationData['attacker']['spotted']:
            return True
        attackerPosition = simulationData['attacker']['position']
        victimPosition = simulationData['player']['position']
        return (victimPosition - attackerPosition).length > self.__skipKillCamDistance

    def __canSkipKillCamera(self):
        if self.__killCamState in DeathCamEvent.SIMULATION_EXCL_FADES or self.__killCamState == DeathCamEvent.State.ENDING or BigWorld.time() - self.__modeEnteredTime < _NO_SKIP_DEATH_CAM_DURATION:
            return False
        needToRespawn = self.__isRespawnActive and self.guiSessionProvider.dynamic.respawn.playerLives > 0
        return False if needToRespawn or self.__bFadeScreenActive or not BigWorld.player().isPostmortemFeatureEnabled(CTRL_MODE_NAME.DEATH_FREE_CAM) else True

    def __isFirstTenDeathsWheeledTank(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isWheeledTech:
            return False
        else:
            wheeledDeathCountLeft = AccountSettings.getSettings(WHEELED_DEATH_DELAY_COUNT)
            return False if wheeledDeathCountLeft == 0 else True

    def __tryDecrementWheeledDeathCounter(self, vehicleID):
        if self.__isFirstTenDeathsWheeledTank(vehicleID):
            wheeledDeathCountLeft = AccountSettings.getSettings(WHEELED_DEATH_DELAY_COUNT)
            AccountSettings.setSettings(WHEELED_DEATH_DELAY_COUNT, max(wheeledDeathCountLeft - 1, 0))
