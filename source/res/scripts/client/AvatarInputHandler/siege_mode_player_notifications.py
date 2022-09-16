# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/siege_mode_player_notifications.py
import BigWorld
import Math
from cgf_obsolete_script.py_component import Component
import SoundGroups
from constants import VEHICLE_SIEGE_STATE
from gui.battle_control import avatar_getter
from vehicle_systems.tankStructure import TankNodeNames

class SOUND_NOTIFICATIONS(object):
    START_TO_SIEGE_MODE = 'start_to_siege_mode_PC'
    START_TO_BASE_MODE = 'start_to_base_mode_PC'
    MOVEMENT_LIMITED_ON = 'strv_siege_mode_movement_limited_on'
    MOVEMENT_LIMITED_OFF = 'strv_siege_mode_movement_limited_off'
    TRANSITION_TIMER = 'siege_mode_transition_timer'
    UI_TURBINE_MODE_ON_STOP = 'ui_turbine_polish_siege_mode_on_stop'
    UI_TURBINE_MODE_OFF_STOP = 'ui_turbine_polish_siege_mode_off_stop'
    UI_TURBINE_MODE_ON = 'ui_turbine_polish_siege_mode_on'
    UI_TURBINE_MODE_OFF = 'ui_turbine_polish_siege_mode_off'


class SiegeModeNotificationsBase(Component):
    _MODE_TYPE = ''

    def getModeType(self):
        return self._MODE_TYPE


class TurboshaftModeSoundNotifications(SiegeModeNotificationsBase):
    _MODE_TYPE = 'turboshaft'

    def __init__(self):
        self.__sounds = {VEHICLE_SIEGE_STATE.SWITCHING_ON: SoundGroups.g_instance.getSound2D(SOUND_NOTIFICATIONS.UI_TURBINE_MODE_ON),
         VEHICLE_SIEGE_STATE.SWITCHING_OFF: SoundGroups.g_instance.getSound2D(SOUND_NOTIFICATIONS.UI_TURBINE_MODE_OFF),
         VEHICLE_SIEGE_STATE.ENABLED: SoundGroups.g_instance.getSound2D(SOUND_NOTIFICATIONS.UI_TURBINE_MODE_ON_STOP),
         VEHICLE_SIEGE_STATE.DISABLED: SoundGroups.g_instance.getSound2D(SOUND_NOTIFICATIONS.UI_TURBINE_MODE_OFF_STOP)}
        self.__lastState = None
        self.__engineWasDestroyed = False
        return

    def onSiegeStateChanged(self, newState, _):
        self.__updateNotifications(newState)

    def __updateNotifications(self, newState):
        if newState not in self.__sounds:
            return
        else:
            vehicle = avatar_getter.getPlayerVehicle()
            if vehicle is None or not vehicle.isAlive():
                return
            isEngineDestroyed = BigWorld.player().deviceStates.get('engine') == 'destroyed'
            if isEngineDestroyed != self.__engineWasDestroyed:
                if isEngineDestroyed:
                    SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.MOVEMENT_LIMITED_ON)
                else:
                    SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.MOVEMENT_LIMITED_OFF)
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
            SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.MOVEMENT_LIMITED_OFF)


class SiegeModeSoundNotifications(SiegeModeNotificationsBase):
    _MODE_TYPE = 'siege'

    def __init__(self):
        self.__sounds = {SOUND_NOTIFICATIONS.START_TO_SIEGE_MODE: SoundGroups.g_instance.getSound2D(SOUND_NOTIFICATIONS.START_TO_SIEGE_MODE),
         SOUND_NOTIFICATIONS.START_TO_BASE_MODE: SoundGroups.g_instance.getSound2D(SOUND_NOTIFICATIONS.START_TO_BASE_MODE)}
        self.__engineWasDestroyed = False
        self.__siegeCallback = None
        return

    def destroy(self):
        if self.__sounds is not None:
            for sound in self.__sounds.itervalues():
                if sound is not None:
                    sound.stop()

        if self.__engineWasDestroyed:
            SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.MOVEMENT_LIMITED_OFF)
        self.__sounds = None
        if self.__siegeCallback is not None:
            BigWorld.cancelCallback(self.__siegeCallback)
        return

    def onSiegeStateChanged(self, newState, timeToNextMode):
        self.__updateNotifications(newState, timeToNextMode)

    def __updateNotifications(self, newState, timeToNextMode):
        if self.__sounds is None:
            return
        else:
            goToSiegeMode = newState == VEHICLE_SIEGE_STATE.SWITCHING_ON
            goToBaseMode = newState == VEHICLE_SIEGE_STATE.SWITCHING_OFF
            siegeModeEnabled = newState == VEHICLE_SIEGE_STATE.ENABLED
            siegeModeDisabled = newState == VEHICLE_SIEGE_STATE.DISABLED
            isValidState = goToSiegeMode or goToBaseMode or siegeModeEnabled or siegeModeDisabled
            if not isValidState:
                return
            eventId = SOUND_NOTIFICATIONS.START_TO_SIEGE_MODE
            if goToBaseMode or siegeModeDisabled:
                eventId = SOUND_NOTIFICATIONS.START_TO_BASE_MODE
            isEngineDestroyed = BigWorld.player().deviceStates.get('engine') == 'destroyed'
            if isEngineDestroyed != self.__engineWasDestroyed:
                if isEngineDestroyed:
                    SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.MOVEMENT_LIMITED_ON)
                else:
                    SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.MOVEMENT_LIMITED_OFF)
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
        SoundGroups.g_instance.playSound2D(SOUND_NOTIFICATIONS.TRANSITION_TIMER)
        self.__siegeCallback = None
        return


class SiegeModeCameraShaker(object):
    SIEGE_CAMERA_IMPULSE = 0.05

    @staticmethod
    def shake(newState, timeToNextMode):
        if newState not in VEHICLE_SIEGE_STATE.SWITCHING:
            return
        else:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is None:
                return
            if vehicle.typeDescriptor.hasAutoSiegeMode:
                return
            inputHandler = BigWorld.player().inputHandler
            matrix = Math.Matrix(vehicle.model.matrix)
            impulseDir = -matrix.applyToAxis(2)
            impulsePosition = Math.Matrix(vehicle.model.node(TankNodeNames.GUN_JOINT)).translation
            inputHandler.onSpecificImpulse(impulsePosition, impulseDir * SiegeModeCameraShaker.SIEGE_CAMERA_IMPULSE, 'sniper')
            return
