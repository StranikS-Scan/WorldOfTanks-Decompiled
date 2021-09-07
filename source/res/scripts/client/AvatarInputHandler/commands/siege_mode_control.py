# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/siege_mode_control.py
import BigWorld
import CommandMapping
from Event import Event
from constants import VEHICLE_SIEGE_STATE, VEHICLE_SETTING
from debug_utils import LOG_DEBUG
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand

class SiegeModeControl(InputHandlerCommand):

    def __init__(self):
        self.onSiegeStateChanged = Event()
        self.onRequestFail = Event()
        self.__currentState = VEHICLE_SIEGE_STATE.DISABLED

    def destroy(self):
        self.onSiegeStateChanged.clear()
        self.onRequestFail.clear()

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        keyCaptured = cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown
        if not keyCaptured:
            return False
        else:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is not None and vehicle.typeDescriptor.type.isDualgunVehicleType:
                return False
            if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive():
                self.__switchSiegeMode()
            return True

    def notifySiegeModeChanged(self, vehicle, newState, timeToNextMode):
        avatar = BigWorld.player()
        if not (vehicle.isPlayerVehicle or vehicle.id == avatar.observedVehicleID):
            return
        LOG_DEBUG('SiegeMode: new state received: {}'.format((newState, timeToNextMode)))
        self.onSiegeStateChanged(newState, timeToNextMode)
        self.__currentState = newState
        self.__timeToNextMode = timeToNextMode

    def __switchSiegeMode(self):
        if BigWorld.player().deviceStates.get('engine') == 'destroyed':
            if self.__currentState not in VEHICLE_SIEGE_STATE.SWITCHING:
                self.onRequestFail()
            return
        if self.__currentState in (VEHICLE_SIEGE_STATE.SWITCHING_ON, VEHICLE_SIEGE_STATE.ENABLED):
            enableSiegeMode = False
        else:
            enableSiegeMode = True
        BigWorld.player().cell.vehicle_changeSetting(VEHICLE_SETTING.SIEGE_MODE_ENABLED, enableSiegeMode)
