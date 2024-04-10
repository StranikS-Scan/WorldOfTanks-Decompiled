# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicles/dualgun_component.py
from weakref import proxy
import BattleReplay
import BigWorld
from ReplayEvents import g_replayEvents
from Vehicle import StunInfo
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from constants import DUALGUN_CHARGER_STATUS
from constants import DUAL_GUN
from constants import VEHICLE_MISC_STATUS
from debug_utils import LOG_WARNING
from dualgun_sounds import DualGunSounds
from items.utils import getFirstReloadTime
from gui.Scaleform.daapi.view.meta.DualGunPanelMeta import DualGunPanelMeta
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID, DestroyTimerViewState
from gui.battle_control.controllers.prebattle_setups_ctrl import IPrebattleSetupsListener
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from helpers.time_utils import MS_IN_SECOND
from skeletons.gui.battle_session import IBattleSessionProvider
from wotdecorators import noexceptReturn

class GunStatesUI(object):
    EMPTY = 1
    RELOADING = 2
    READY = 3


class DualGunConstants(object):
    LEFT_TIME = 'leftTime'
    BASE_TIME = 'baseTime'
    TIME_MULTIPLIER = 1000
    CHARGE_TIME_MULTIPLIER = 1000
    CHANGE_GUN_TRANSITION_TIME = 0.4


class ReloadFactorsState(object):
    __slots__ = ('__flags', '__weakref__')

    def __init__(self):
        self.__flags = 0

    def __ior__(self, other):
        self.__flags |= other
        return self

    def __iand__(self, other):
        self.__flags &= other
        return self

    def cleanup(self):
        self.__flags = 0

    def hasNegativeEffect(self):
        return bool(self.__flags)


class ReloadingAffectPolicy(object):
    __slots__ = ('__stateID', '__reloadingFactors')

    def __init__(self, reloadingFactors, stateID):
        self.__stateID = stateID
        self.__reloadingFactors = proxy(reloadingFactors)

    def __call__(self, value):
        if not isinstance(value, bool):
            return
        self._updateFactors(value)

    def _updateFactors(self, value):
        if value:
            self.__reloadingFactors |= self.__stateID
        else:
            self.__reloadingFactors &= ~self.__stateID


class DeviceAffectPolicy(ReloadingAffectPolicy):
    __AFFECT_DEVICES = ('ammoBay', 'loader')
    __AFFECT_STATES = ('critical', 'destroyed')

    def __call__(self, value):
        if not isinstance(value, tuple):
            return
        deviceState = value
        for device in self.__AFFECT_DEVICES:
            if device in deviceState[0]:
                self._updateFactors(deviceState[1] in self.__AFFECT_STATES)


class DestroyStateAffectPolicy(ReloadingAffectPolicy):
    __AFFECT_STATES = (VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED,)
    __AFFECT_LEVEL = ('critical',)

    def __call__(self, value):
        if not isinstance(value, DestroyTimerViewState):
            return
        timerViewState = value
        if timerViewState.code in self.__AFFECT_STATES:
            self._updateFactors(timerViewState.level in self.__AFFECT_LEVEL)


class StunAffectPolicy(ReloadingAffectPolicy):

    def __call__(self, value):
        if not isinstance(value, StunInfo):
            return
        stunInfo = value
        self._updateFactors(stunInfo.duration > 0)


class DualGunComponent(DualGunPanelMeta, IPrebattleSetupsListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(DualGunComponent, self).__init__()
        self.__reloadingState = ReloadFactorsState()
        self.__deviceStateHandlers = {VEHICLE_VIEW_STATE.FIRE: ReloadingAffectPolicy(self.__reloadingState, VEHICLE_VIEW_STATE.FIRE),
         VEHICLE_VIEW_STATE.DEVICES: DeviceAffectPolicy(self.__reloadingState, VEHICLE_VIEW_STATE.DEVICES),
         VEHICLE_VIEW_STATE.CREW_DEACTIVATED: DeviceAffectPolicy(self.__reloadingState, VEHICLE_VIEW_STATE.CREW_DEACTIVATED),
         VEHICLE_VIEW_STATE.STUN: StunAffectPolicy(self.__reloadingState, VEHICLE_VIEW_STATE.STUN),
         VEHICLE_VIEW_STATE.DESTROY_TIMER: DestroyStateAffectPolicy(self.__reloadingState, VEHICLE_VIEW_STATE.DESTROY_TIMER)}
        self.__isEnabled = False
        self.__isObservingVehicle = False
        self.__isAllowedByContext = True
        self.__chargeState = DUALGUN_CHARGER_STATUS.BEFORE_PREPARING
        self.__prevChargeState = DUALGUN_CHARGER_STATUS.BEFORE_PREPARING
        self.__deferredGunState = None
        self.__bulletCollapsed = False
        self.__debuffInProgress = False
        self.__debuffBaseTime = 0
        self.__inBattle = False
        self.__reloadEventReceived = False
        self.__isObserver = False
        self.__currentTotalTimeTimer = 0
        self.__soundManager = DualGunSounds()
        return

    def updateVehicleParams(self, vehicle, factors):
        leftTime = getFirstReloadTime(vehicle.descriptor, factors)
        rightTime = getFirstReloadTime(vehicle.descriptor, factors, ignoreRespawn=True)
        self.__currentTotalTimeTimer = (leftTime + rightTime) * DualGunConstants.CHARGE_TIME_MULTIPLIER
        self.__updateTimeUntilNextDoubleShot(increaseByDebuff=False)

    def _populate(self):
        super(DualGunComponent, self)._populate()
        ctrl = self.__sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
            g_replayEvents.onPause += self.__onReplayPause
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        specCtrl = self.__sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded += self.__updateChargeTimerState
            ammoCtrl.onShellsUpdated += self.__updateChargeTimerState
            ammoCtrl.onCurrentShellChanged += self.__updateChargeTimerState
        feedBackCtrl = self.__sessionProvider.shared.feedback
        if feedBackCtrl is not None:
            feedBackCtrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        prbCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prbCtrl is not None:
            prbCtrl.onBattleStarted += self.__onBattleStarted
            self.__updateContextAvailability()
        add = g_eventBus.addListener
        add(GameEvent.CHARGE_RELEASED, self.__chargeReleased, scope=EVENT_BUS_SCOPE.BATTLE)
        add(GameEvent.PRE_CHARGE, self.__onPreCharge, scope=EVENT_BUS_SCOPE.BATTLE)
        add(GameEvent.CONTROL_MODE_CHANGE, self.__onControlModeChange, scope=EVENT_BUS_SCOPE.BATTLE)
        add(GameEvent.SNIPER_CAMERA_TRANSITION, self.__onSniperCameraTransition, scope=EVENT_BUS_SCOPE.BATTLE)
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
            self.__onArenaPeriodChange(arena.period, arena.periodEndTime, arena.periodLength, arena.periodAdditionalInfo)
            player = BigWorld.player()
            if player is not None and player.inputHandler is not None:
                player.inputHandler.onCameraChanged += self.__onCameraChanged
        self.as_setChangeGunTweenPropsS(MS_IN_SECOND / 2, MS_IN_SECOND)
        arenaDP = self.__sessionProvider.getArenaDP()
        if arenaDP is not None:
            vInfo = arenaDP.getVehicleInfo()
            self.__isObserver = vInfo.isObserver()
        return

    def _dispose(self):
        super(DualGunComponent, self)._dispose()
        self.as_setVisibleS(False)
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
            g_replayEvents.onPause -= self.__onReplayPause
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        vStateCtrl = self.__sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        specCtrl = self.__sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onShellsAdded -= self.__updateChargeTimerState
            ammoCtrl.onShellsUpdated -= self.__updateChargeTimerState
            ammoCtrl.onCurrentShellChanged -= self.__updateChargeTimerState
        feedBackCtrl = self.__sessionProvider.shared.feedback
        if feedBackCtrl is not None:
            feedBackCtrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        prbCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prbCtrl is not None:
            prbCtrl.onBattleStarted -= self.__onBattleStarted
        self.__soundManager.onComponentDisposed()
        remove = g_eventBus.removeListener
        remove(GameEvent.CHARGE_RELEASED, self.__chargeReleased, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(GameEvent.PRE_CHARGE, self.__onPreCharge, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(GameEvent.CONTROL_MODE_CHANGE, self.__onControlModeChange, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(GameEvent.SNIPER_CAMERA_TRANSITION, self.__onSniperCameraTransition, scope=EVENT_BUS_SCOPE.BATTLE)
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
            player = BigWorld.player()
            if player is not None and player.inputHandler is not None:
                player.inputHandler.onCameraChanged -= self.__onCameraChanged
        return

    def __onVehicleStateUpdated(self, stateID, value):
        if not self.__isEnabled:
            return
        if stateID == VEHICLE_VIEW_STATE.DUAL_GUN_STATE_UPDATED:
            self.__onDualGunStateUpdated(value)
        elif stateID == VEHICLE_VIEW_STATE.DUAL_GUN_CHARGER:
            self.__onDualGunChargeStateUpdated(value)
        elif stateID == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isEnabled = False
            self.as_setVisibleS(False)
        elif stateID in self.__deviceStateHandlers:
            self.__deviceStateHandlers[stateID](value)
            self.as_setReloadingTimeIncreasedS(self.__reloadingState.hasNegativeEffect())

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__isEnabled = False
        self.as_setVisibleS(False)

    def __onSpectatorModeChanged(self, mode):
        self.__isEnabled = False
        self.as_setVisibleS(False)

    def __onCrosshairViewChanged(self, viewID):
        self.as_setViewS(viewID)

    def __onArenaPeriodChange(self, arenaPeriod, endTime, *_):
        self.__inBattle = arenaPeriod == ARENA_PERIOD.BATTLE

    def __onVehicleControlling(self, vehicle):
        vTypeDesc = vehicle.typeDescriptor
        self.__isObservingVehicle = avatar_getter.getIsObserverFPV()
        self.__isEnabled = False
        if vehicle.isAlive() and vTypeDesc.isDualgunVehicle and (vehicle.isPlayerVehicle or self.__isObservingVehicle):
            self.__isEnabled = True
        self.as_setVisibleS(self.__isVisible())
        if self.__isObserver:
            self.__soundManager.onObserverSwitched()
        self.__reloadingState.cleanup()
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is None:
            return
        else:
            for stateID in self.__deviceStateHandlers.iterkeys():
                value = ctrl.getStateValue(stateID)
                if value is not None:
                    if stateID == VEHICLE_VIEW_STATE.DEVICES:
                        for v in value:
                            self.__deviceStateHandlers[stateID](v)

                    else:
                        self.__deviceStateHandlers[stateID](value)

            self.as_setReloadingTimeIncreasedS(self.__reloadingState.hasNegativeEffect())
            return

    @staticmethod
    def _convertServerStateToUI(state):
        if state == DUAL_GUN.GUN_STATE.EMPTY:
            return GunStatesUI.EMPTY
        elif state == DUAL_GUN.GUN_STATE.RELOADING:
            return GunStatesUI.RELOADING
        else:
            return GunStatesUI.READY if state == DUAL_GUN.GUN_STATE.READY else None

    def __onBattleStarted(self):
        self.__updateContextAvailability()
        self.as_setVisibleS(self.__isVisible())

    def __updateContextAvailability(self):
        prebattleCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleCtrl is not None:
            self.__isAllowedByContext = prebattleCtrl.isVehicleStateIndicatorAllowed()
        else:
            self.__isAllowedByContext = True
        return

    def __updateGunState(self, gunID, state, serverCooldownData):
        leftTime = int(serverCooldownData[gunID].leftTime * DualGunConstants.TIME_MULTIPLIER)
        baseTime = int(serverCooldownData[gunID].baseTime * DualGunConstants.TIME_MULTIPLIER)
        self.as_setGunStateS(gunID, state, leftTime, baseTime)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_ACTIVE_GUN_CHANGED:
            _, switchDelay = value
            self.as_setChangeGunTweenPropsS(DualGunConstants.CHANGE_GUN_TRANSITION_TIME * MS_IN_SECOND, switchDelay * MS_IN_SECOND)
            self.__reloadEventReceived = True
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD and self.__isObserver:
            self.as_setVisibleS(False)

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if currentVehicleId is None:
            return
        else:
            if cameraName != 'video':
                vehicle = BigWorld.entities.get(currentVehicleId)
                if vehicle and self.__isEnabled and vehicle.isAlive() and vehicle.typeDescriptor.isDualgunVehicle:
                    self.as_setVisibleS(self.__isVisible())
            else:
                self.as_setVisibleS(False)
            return

    def __onDualGunStateUpdated(self, value):
        if self.__chargeState == DUALGUN_CHARGER_STATUS.PREPARING:
            self.__deferredGunState = value
            return
        activeGun, cooldownTimes, states = value
        self.__debuffBaseTime = cooldownTimes[DUAL_GUN.COOLDOWNS.DEBUFF].baseTime
        if len(states) < 2:
            LOG_WARNING('Got incorrect dualgun states length, aborting')
            return
        leftGunState = self._convertServerStateToUI(states[DUAL_GUN.ACTIVE_GUN.LEFT])
        rightGunState = self._convertServerStateToUI(states[DUAL_GUN.ACTIVE_GUN.RIGHT])
        self.__updateGunState(DUAL_GUN.COOLDOWNS.LEFT, leftGunState, cooldownTimes)
        self.__updateGunState(DUAL_GUN.COOLDOWNS.RIGHT, rightGunState, cooldownTimes)
        leftTime = cooldownTimes[DUAL_GUN.COOLDOWNS.SWITCH].leftTime
        baseTime = cooldownTimes[DUAL_GUN.COOLDOWNS.SWITCH].baseTime
        activeGunReloadingTimeLeft = max(leftTime, cooldownTimes[activeGun].leftTime)
        switchLeftTime = int(activeGunReloadingTimeLeft * DualGunConstants.TIME_MULTIPLIER)
        switchBaseTime = int(baseTime * DualGunConstants.TIME_MULTIPLIER)
        if self.__reloadEventReceived:
            if cooldownTimes[activeGun].leftTime != activeGunReloadingTimeLeft:
                self.__soundManager.onWeaponChanged(switchLeftTime / MS_IN_SECOND)
            self.__reloadEventReceived = False
        self.as_updateActiveGunS(activeGun, switchLeftTime, switchBaseTime)
        self.__updateDualGunState(states, cooldownTimes)
        self.__updateChargeTimerState()
        if not self.__debuffInProgress:
            timeUntilDoubleShot = self.__getTimeUntilNextDoubleShot(cooldownTimes)
            self.__currentTotalTimeTimer = timeUntilDoubleShot * DualGunConstants.TIME_MULTIPLIER
            self.__updateTimeUntilNextDoubleShot(increaseByDebuff=False)

    @staticmethod
    def __getTimeUntilNextDoubleShot(cooldownTimes):
        totalTime = 0
        for gunID in (DUAL_GUN.ACTIVE_GUN.LEFT, DUAL_GUN.ACTIVE_GUN.RIGHT):
            totalTime += cooldownTimes[gunID].baseTime

        return totalTime

    def __updateDualGunState(self, states, cooldownTimes):
        debuff = cooldownTimes[DUAL_GUN.COOLDOWNS.DEBUFF]
        if debuff.leftTime > 0:
            self.__debuffInProgress = True
            self.__bulletCollapsed = False
            self.__soundManager.onCooldownEnd(debuff.leftTime)
            totalDebuffTime = debuff.leftTime + cooldownTimes[DUAL_GUN.ACTIVE_GUN.LEFT].baseTime + cooldownTimes[DUAL_GUN.ACTIVE_GUN.RIGHT].baseTime
            self.as_setCooldownS(totalDebuffTime * DualGunConstants.TIME_MULTIPLIER)
            self.__updateTimeUntilNextDoubleShot(increaseByDebuff=True)
            return
        self.__debuffInProgress = False
        if states[DUAL_GUN.ACTIVE_GUN.LEFT] == DUAL_GUN.GUN_STATE.READY and states[DUAL_GUN.ACTIVE_GUN.RIGHT] == DUAL_GUN.GUN_STATE.READY:
            self.as_readyForChargeS()
        elif BigWorld.player().isObserver() and self.__inBattle and self.__chargeState == DUALGUN_CHARGER_STATUS.APPLIED:
            if self.__prevChargeState == DUALGUN_CHARGER_STATUS.PREPARING:
                self.__prevChargeState = DUALGUN_CHARGER_STATUS.BEFORE_PREPARING
                self.as_expandPanelS()

    def __onPreCharge(self, _):
        if self.__inBattle:
            self.__soundManager.onPreChargeStarted()

    def __onSniperCameraTransition(self, _):
        self.__soundManager.onSniperCameraTransition()

    def __onControlModeChange(self, event):
        mode = event.ctx.get('mode')
        if self.__isEnabled and mode is not None and mode in (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.DUAL_GUN):
            self.as_setVisibleS(self.__isVisible())
        else:
            self.as_setVisibleS(False)
        return

    def __chargeReleased(self, event):
        canShot, error = self.__sessionProvider.shared.ammo.canShoot()
        canMakeDualShoot = BigWorld.player().canMakeDualShot
        keyDown = event.ctx.get('keyDown')
        if keyDown and self.__inBattle:
            self.__soundManager.onChargeReleased(canShot, error, canMakeDualShoot)
        if keyDown is not None and not self.__debuffInProgress and self.__inBattle:
            if keyDown:
                self.__bulletCollapsed = True
                self.as_collapsePanelS()
            if not keyDown and self.__bulletCollapsed:
                self.__bulletCollapsed = False
                self.as_expandPanelS()
        return

    def __onDualGunChargeStateUpdated(self, value):
        self.__prevChargeState = self.__chargeState
        self.__chargeState, time = value
        if self.__chargeState == DUALGUN_CHARGER_STATUS.PREPARING:
            baseTime, timeLeft = time
            self.__soundManager.onChargeStarted(timeLeft)
            self.as_startChargingS(timeLeft * MS_IN_SECOND, baseTime * MS_IN_SECOND)
            self.__updateTimeUntilNextDoubleShot(increaseByDebuff=True)
            return
        else:
            if self.__chargeState in (DUALGUN_CHARGER_STATUS.CANCELED, DUALGUN_CHARGER_STATUS.UNAVAILABLE):
                self.__soundManager.onChargeCanceled()
                self.__updateTimeUntilNextDoubleShot(increaseByDebuff=False)
                if self.__chargeState == DUALGUN_CHARGER_STATUS.CANCELED:
                    self.as_cancelChargeS()
                else:
                    self.as_disableChargeS()
            if self.__deferredGunState:
                self.__onDualGunStateUpdated(self.__deferredGunState)
                self.__deferredGunState = None
            return

    def __updateChargeTimerState(self, *args):
        shellsQuantity = self.__sessionProvider.shared.ammo.getShellsQuantityLeft()
        if shellsQuantity > 1 or shellsQuantity < 0 or not self.__isPlayerVehicle():
            self.as_setTimerVisibleS(True)
        else:
            self.as_setTimerVisibleS(False)

    def __onReplayTimeWarpStart(self):
        self.as_resetS()

    def __onReplayPause(self, _):
        self.as_setPlaybackSpeedS(BattleReplay.g_replayCtrl.playbackSpeed)

    def __updateTimeUntilNextDoubleShot(self, increaseByDebuff=False):
        timeValue = self.__currentTotalTimeTimer
        if increaseByDebuff:
            timeValue += self.__debuffBaseTime * DualGunConstants.TIME_MULTIPLIER
        self.as_updateTotalTimeS(timeValue)

    def __isPlayerVehicle(self):
        player = BigWorld.player()
        return player.vehicle.isPlayerVehicle if player is not None and player.vehicle is not None else False

    @noexceptReturn(False)
    def __isVisible(self):
        isVisible = self.__isEnabled and self.__isAllowedByContext
        if isVisible:
            ctrl = self.__sessionProvider.shared.vehicleState
            if ctrl.isInPostmortem and avatar_getter.getInputHandler().ctrlModeName == CTRL_MODE_NAME.POSTMORTEM and not self.__isObservingVehicle:
                isVisible = False
        return isVisible
