# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/thermal_vision_control.py
import BigWorld
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand

class ThermalVisionControl(InputHandlerCommand):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        keyCaptured = cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown
        if not keyCaptured:
            return False
        else:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive():
                self.__activateThermalVision(vehicle)
            return True

    def __activateThermalVision(self, vehicle):
        component = vehicle.dynamicComponents.get('thermalVisionController')
        if component is not None:
            component.tryActivate()
        return
