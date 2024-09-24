# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/siege_mode_player_notifications.py
import BigWorld
import Math
from cgf_obsolete_script.py_component import Component
import SoundGroups
from constants import VEHICLE_SIEGE_STATE
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DEVICE_STATE_DESTROYED
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.tankStructure import TankNodeNames

class SiegeStates(object):
    STARTED = 0
    PAUSED = 1
    STOPPED = 2


def playTriggerSound(soundStateChange):
    if soundStateChange and soundStateChange.trigger:
        SoundGroups.g_instance.playSound2D(soundStateChange.trigger)


def playUnavailableSound(soundStateChange):
    if soundStateChange and soundStateChange.unavailable:
        SoundGroups.g_instance.playSound2D(soundStateChange.unavailable)


class SoundNotifications(object):
    START_TO_SIEGE_MODE = 'start_to_siege_mode_PC'
    START_TO_BASE_MODE = 'start_to_base_mode_PC'
    MOVEMENT_LIMITED_ON = 'strv_siege_mode_movement_limited_on'
    MOVEMENT_LIMITED_OFF = 'strv_siege_mode_movement_limited_off'
    TRANSITION_TIMER = 'siege_mode_transition_timer'
    UI_TURBINE_MODE_ON_STOP = 'ui_turbine_polish_siege_mode_on_stop'
    UI_TURBINE_MODE_OFF_STOP = 'ui_turbine_polish_siege_mode_off_stop'
    UI_TURBINE_MODE_ON = 'ui_turbine_polish_siege_mode_on'
    UI_TURBINE_MODE_OFF = 'ui_turbine_polish_siege_mode_off'
    TWIN_GUN_SWITCH_START = 'gun_rld_dgp_switch_start'
    TWIN_GUN_SWITCH_STOP = 'gun_rld_dgp_switch_stop'


class SiegeModeNotificationsBase(Component):
    _MODE_TYPE = ''

    def __init__(self, vehicleID):
        self.__vehicleID = vehicleID

    @property
    def vehicleID(self):
        return self.__vehicleID

    def start(self):
        pass

    def stop(self):
        pass

    @classmethod
    def getModeType(cls):
        return cls._MODE_TYPE


class TurboshaftModeSoundNotifications(SiegeModeNotificationsBase):
    _MODE_TYPE = 'turboshaft'

    def __init__(self, vehicleID):
        super(TurboshaftModeSoundNotifications, self).__init__(vehicleID)
        self.__sounds = {VEHICLE_SIEGE_STATE.SWITCHING_ON: SoundGroups.g_instance.getSound2D(SoundNotifications.UI_TURBINE_MODE_ON),
         VEHICLE_SIEGE_STATE.SWITCHING_OFF: SoundGroups.g_instance.getSound2D(SoundNotifications.UI_TURBINE_MODE_OFF),
         VEHICLE_SIEGE_STATE.ENABLED: SoundGroups.g_instance.getSound2D(SoundNotifications.UI_TURBINE_MODE_ON_STOP),
         VEHICLE_SIEGE_STATE.DISABLED: SoundGroups.g_instance.getSound2D(SoundNotifications.UI_TURBINE_MODE_OFF_STOP)}
        self.__lastState = None
        self.__engineWasDestroyed = False
        return

    def onSiegeStateChanged(self, vehicleID, newState, _):
        if newState not in self.__sounds or vehicleID != self.vehicleID:
            return
        else:
            vehicle = avatar_getter.getPlayerVehicle()
            if vehicle is None or not vehicle.isAlive():
                return
            isEngineDestroyed = BigWorld.player().deviceStates.get('engine') == 'destroyed'
            if isEngineDestroyed != self.__engineWasDestroyed:
                if isEngineDestroyed:
                    SoundGroups.g_instance.playSound2D(SoundNotifications.MOVEMENT_LIMITED_ON)
                else:
                    SoundGroups.g_instance.playSound2D(SoundNotifications.MOVEMENT_LIMITED_OFF)
                self.__engineWasDestroyed = isEngineDestroyed
            if self.__lastState == newState:
                return
            isValidTransition = self.__lastState is not None and (self.__lastState + 1) % (VEHICLE_SIEGE_STATE.SWITCHING_OFF + 1) == newState
            if self.__lastState:
                self.__sounds[self.__lastState].stop()
            if isValidTransition:
                self.__sounds[newState].play()
            self.__lastState = newState
            return

    def destroy(self):
        if self.__lastState:
            self.__sounds[self.__lastState].stop()
        if self.__engineWasDestroyed:
            SoundGroups.g_instance.playSound2D(SoundNotifications.MOVEMENT_LIMITED_OFF)


class TwinGunModeSoundNotifications(SiegeModeNotificationsBase):
    _MODE_TYPE = 'twinGun'
    __DEVICE = 'gun'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicleID):
        super(TwinGunModeSoundNotifications, self).__init__(vehicleID)
        self.__vehicleStateUpdatedHandlers = {VEHICLE_VIEW_STATE.DEVICES: self.__updateDeviceState,
         VEHICLE_VIEW_STATE.REPAIRING: self.__updateRepairingDevice}
        self.__siegeTransitionState = SiegeStates.STOPPED
        self.__startSound = SoundGroups.g_instance.getSound2D(SoundNotifications.TWIN_GUN_SWITCH_START)

    def destroy(self):
        self.__clear()
        self.__startSound = None
        return

    def start(self):
        vehicleCtrl = self.__sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def stop(self):
        vehicleCtrl = self.__sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.__clear()
        return

    def onSiegeStateChanged(self, vehicleID, newState, _):
        if vehicleID != self.vehicleID:
            return
        if BigWorld.player().deviceStates.get(self.__DEVICE) == DEVICE_STATE_DESTROYED:
            return
        isSwitching = newState in VEHICLE_SIEGE_STATE.SWITCHING
        isSwitchingStarted = self.__isSwitchingStarted()
        if isSwitchingStarted == isSwitching:
            return
        if not isSwitchingStarted and isSwitching:
            self.__startSound.play()
            self.__siegeTransitionState = SiegeStates.STARTED
        else:
            self.__stopSound()
            SoundGroups.g_instance.playSound2D(SoundNotifications.TWIN_GUN_SWITCH_STOP)
            self.__siegeTransitionState = SiegeStates.STOPPED

    def __clear(self):
        if self.__isSwitchingStarted():
            self.__stopSound()
        self.__siegeTransitionState = SiegeStates.STOPPED
        self.__vehicleStateUpdatedHandlers = {}

    def __isSwitchingStarted(self):
        return self.__siegeTransitionState == SiegeStates.STARTED

    def __isValidDevice(self, device):
        return device == self.__DEVICE

    def __onVehicleStateUpdated(self, state, value):
        if state in self.__vehicleStateUpdatedHandlers and self.__isValidDevice(value[0]):
            handler = self.__vehicleStateUpdatedHandlers[state]
            handler(value)

    def __playGunDestroyedSound(self):
        vehicle = avatar_getter.getPlayerVehicle()
        if vehicle is not None:
            siegeModeParams = vehicle.typeDescriptor.type.siegeModeParams
            soundStateChange = siegeModeParams['soundStateChange'] if siegeModeParams else None
            playUnavailableSound(soundStateChange)
        return

    def __stopSound(self):
        if self.__startSound.isPlaying:
            self.__startSound.stop()

    def __updateDeviceState(self, value):
        _, deviceState, __ = value
        if deviceState == DEVICE_STATE_DESTROYED and self.__isSwitchingStarted():
            self.__playGunDestroyedSound()
            self.__stopSound()
            SoundGroups.g_instance.playSound2D(SoundNotifications.TWIN_GUN_SWITCH_STOP)
            self.__siegeTransitionState = SiegeStates.PAUSED

    def __updateRepairingDevice(self, value):
        if self.__siegeTransitionState == SiegeStates.PAUSED:
            _, progress, _, __ = value
            if progress == 0:
                self.__playGunDestroyedSound()


class SiegeModeSoundNotifications(SiegeModeNotificationsBase):
    _MODE_TYPE = 'siege'

    def __init__(self, vehicleID):
        super(SiegeModeSoundNotifications, self).__init__(vehicleID)
        self.__sounds = {SoundNotifications.START_TO_SIEGE_MODE: SoundGroups.g_instance.getSound2D(SoundNotifications.START_TO_SIEGE_MODE),
         SoundNotifications.START_TO_BASE_MODE: SoundGroups.g_instance.getSound2D(SoundNotifications.START_TO_BASE_MODE)}
        self.__engineWasDestroyed = False
        self.__siegeCallback = None
        return

    def destroy(self):
        if self.__sounds is not None:
            for sound in self.__sounds.itervalues():
                if sound is not None:
                    sound.stop()

        if self.__engineWasDestroyed:
            SoundGroups.g_instance.playSound2D(SoundNotifications.MOVEMENT_LIMITED_OFF)
        self.__sounds = None
        if self.__siegeCallback is not None:
            BigWorld.cancelCallback(self.__siegeCallback)
        return

    def onSiegeStateChanged(self, vehicleID, newState, timeToNextMode):
        if self.__sounds is None or self.vehicleID != vehicleID:
            return
        else:
            goToSiegeMode = newState == VEHICLE_SIEGE_STATE.SWITCHING_ON
            goToBaseMode = newState == VEHICLE_SIEGE_STATE.SWITCHING_OFF
            siegeModeEnabled = newState == VEHICLE_SIEGE_STATE.ENABLED
            siegeModeDisabled = newState == VEHICLE_SIEGE_STATE.DISABLED
            isValidState = goToSiegeMode or goToBaseMode or siegeModeEnabled or siegeModeDisabled
            if not isValidState:
                return
            eventId = SoundNotifications.START_TO_SIEGE_MODE
            if goToBaseMode or siegeModeDisabled:
                eventId = SoundNotifications.START_TO_BASE_MODE
            isEngineDestroyed = BigWorld.player().deviceStates.get('engine') == 'destroyed'
            if isEngineDestroyed != self.__engineWasDestroyed:
                if isEngineDestroyed:
                    SoundGroups.g_instance.playSound2D(SoundNotifications.MOVEMENT_LIMITED_ON)
                else:
                    SoundGroups.g_instance.playSound2D(SoundNotifications.MOVEMENT_LIMITED_OFF)
                self.__engineWasDestroyed = isEngineDestroyed
            if goToSiegeMode:
                if self.__siegeCallback is not None:
                    BigWorld.cancelCallback(self.__siegeCallback)
                    self.__siegeCallback = None
                if not isEngineDestroyed:
                    deltaTime = timeToNextMode - 1.0 if timeToNextMode > 1.0 else 0.0
                    self.__siegeCallback = BigWorld.callback(deltaTime, self.__onSiegeTimer)
            shouldStopSound = siegeModeEnabled or siegeModeDisabled or isEngineDestroyed
            sound = self.__sounds[eventId]
            if sound is None:
                return
            if shouldStopSound:
                sound.stop()
            elif not sound.isPlaying:
                sound.play()
            return

    def __onSiegeTimer(self):
        SoundGroups.g_instance.playSound2D(SoundNotifications.TRANSITION_TIMER)
        self.__siegeCallback = None
        return


class SiegeModeCameraShaker(object):
    SIEGE_CAMERA_IMPULSE = 0.05

    @staticmethod
    def shake(_, newState, __):
        if newState not in VEHICLE_SIEGE_STATE.SWITCHING:
            return
        else:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is None:
                return
            typeDescriptor = vehicle.typeDescriptor
            if typeDescriptor.hasAutoSiegeMode or typeDescriptor.isTwinGunVehicle:
                return
            inputHandler = BigWorld.player().inputHandler
            matrix = Math.Matrix(vehicle.model.matrix)
            impulseDir = -matrix.applyToAxis(2)
            impulsePosition = Math.Matrix(vehicle.model.node(TankNodeNames.GUN_JOINT)).translation
            inputHandler.onSpecificImpulse(impulsePosition, impulseDir * SiegeModeCameraShaker.SIEGE_CAMERA_IMPULSE, 'sniper')
            return
