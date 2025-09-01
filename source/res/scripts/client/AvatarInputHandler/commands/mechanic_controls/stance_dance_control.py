# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/mechanic_controls/stance_dance_control.py
import typing
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from vehicles.mechanics.mechanic_helpers import getPlayerVehicleMechanic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

class StanceDanceControl(InputHandlerCommand):

    def __init__(self, mechanic):
        self.__mechanic = mechanic

    def handleKeyEvent(self, isDown, key, mods, event=None):
        mechanicComponent = getPlayerVehicleMechanic(self.__mechanic)
        if mechanicComponent is not None and isDown:
            if CommandMapping.g_instance.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key):
                return mechanicComponent.trySwitchStance()
            if CommandMapping.g_instance.isFired(CommandMapping.CMD_CM_SPECIAL_ABILITY, key):
                return mechanicComponent.tryUseActiveAbility()
        return False


def createStanceDanceControl(mechanic, *_, **__):
    return StanceDanceControl(mechanic)
