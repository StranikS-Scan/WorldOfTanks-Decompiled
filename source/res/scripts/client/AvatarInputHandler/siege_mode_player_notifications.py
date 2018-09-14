# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/siege_mode_player_notifications.py
import BigWorld
import Math
import SoundGroups
from constants import VEHICLE_SIEGE_STATE
from svarog_script.py_component import Component
from vehicle_systems.tankStructure import TankNodeNames

class SOUND_NOTIFICATIONS:
    START_TO_SIEGE_MODE = 'start_to_siege_mode_PC'
    START_TO_BASE_MODE = 'start_to_base_mode_PC'
    MOVEMENT_LIMITED_ON = 'strv_siege_mode_movement_limited_on'
    MOVEMENT_LIMITED_OFF = 'strv_siege_mode_movement_limited_off'
    TRANSITION_TIMER = 'siege_mode_transition_timer'


class SiegeModeSoundNotifications(Component):

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
            inputHandler = BigWorld.player().inputHandler
            matrix = Math.Matrix(vehicle.model.matrix)
            impulseDir = -matrix.applyToAxis(2)
            impulsePosition = Math.Matrix(vehicle.model.node(TankNodeNames.GUN_JOINT)).translation
            inputHandler.onSpecificImpulse(impulsePosition, impulseDir * SiegeModeCameraShaker.SIEGE_CAMERA_IMPULSE, 'sniper')
            return
