# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/siege_mode_control.py
import BigWorld
from constants import ARENA_PERIOD, VEHICLE_SIEGE_STATE, VEHICLE_SETTING
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from AvatarInputHandler.siege_mode_player_notifications import playTriggerSound, playUnavailableSound
from debug_utils import LOG_DEBUG
from Event import Event
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class SiegeModeControl(InputHandlerCommand):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __CANT_SWITCH_ERRORS = {'gun': 'cantSwitchGunDestroyed',
     'engine': 'cantSwitchEngineDestroyed'}

    def __init__(self):
        self.onSiegeStateChanged = Event()
        self.__currentState = VEHICLE_SIEGE_STATE.DISABLED

    def destroy(self):
        self.onSiegeStateChanged.clear()

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        keyCaptured = cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown
        if not keyCaptured:
            return False
        else:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is None:
                return False
            vehicleDescr = vehicle.typeDescriptor
            if vehicleDescr.type.isDualgunVehicleType:
                return False
            onlyInBattleSwitch = vehicleDescr.isTwinGunVehicle
            if onlyInBattleSwitch and self.__sessionProvider.arenaVisitor.getArenaPeriod() != ARENA_PERIOD.BATTLE:
                return False
            if vehicle.isPlayerVehicle and vehicle.isAlive():
                self.__switchSiegeMode(vehicle)
            return True

    def notifySiegeModeChanged(self, vehicle, newState, timeToNextMode):
        avatar = BigWorld.player()
        if not (vehicle.isPlayerVehicle or vehicle.id == avatar.observedVehicleID):
            return
        LOG_DEBUG('SiegeMode: new state received: {}'.format((newState, timeToNextMode)))
        self.onSiegeStateChanged(vehicle.id, newState, timeToNextMode)
        self.__currentState = newState

    def __switchSiegeMode(self, vehicle):
        player = BigWorld.player()
        if player is None:
            return
        else:
            siegeModeParams = vehicle.typeDescriptor.type.siegeModeParams
            soundStateChange = siegeModeParams['soundStateChange'] if siegeModeParams else None
            playTriggerSound(soundStateChange)
            isSwitching = self.__currentState in VEHICLE_SIEGE_STATE.SWITCHING
            if isSwitching and siegeModeParams and not siegeModeParams['switchCancelEnabled']:
                return
            deviceName = vehicle.typeDescriptor.type.siegeDeviceName
            if player.deviceStates.get(deviceName) == 'destroyed' and not isSwitching:
                player.showVehicleError(self.__CANT_SWITCH_ERRORS[deviceName])
                playUnavailableSound(soundStateChange)
                return
            ammo = self.__sessionProvider.shared.ammo
            enableSiegeMode = self.__currentState not in (VEHICLE_SIEGE_STATE.SWITCHING_ON, VEHICLE_SIEGE_STATE.ENABLED)
            if vehicle.typeDescriptor.isTwinGunVehicle and enableSiegeMode and ammo and ammo.getShellsQuantityLeft() == 1:
                player.showVehicleError('cantSwitchOneShellLeft')
                playUnavailableSound(soundStateChange)
                return
            player.cell.vehicle_changeSetting(VEHICLE_SETTING.SIEGE_MODE_ENABLED, enableSiegeMode)
            return
