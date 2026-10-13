# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/mechanic_controls/simple_activation_control.py
from __future__ import absolute_import
import typing
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from items.vehicle_mechanics_types import VehicleMechanicKeys
from vehicles.mechanics.mechanic_helpers import getPlayerVehicleMechanicComponent
if typing.TYPE_CHECKING:
    from items.vehicle_mechanics_types import VehicleMechanicKey

class SimpleActivationControl(InputHandlerCommand):
    _VEHICLE_MECHANIC_KEYS = {VehicleMechanicKeys.AUTORELOADER_SURGE: CommandMapping.CMD_CM_SPECIAL_ABILITY,
     VehicleMechanicKeys.CONCENTRATION_MODE: CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION,
     VehicleMechanicKeys.PROPELLANT_GUN: CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION,
     VehicleMechanicKeys.ROCKET_ACCELERATION: CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION,
     VehicleMechanicKeys.STATIONARY_RELOAD: CommandMapping.CMD_RELOAD_PARTIAL_CLIP}

    def __init__(self, mechanic):
        self.__mechanic = mechanic
        self.__key = self._VEHICLE_MECHANIC_KEYS.get(mechanic, CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if not isDown or not CommandMapping.g_instance.isFired(self.__key, key):
            return False
        else:
            mechanicComponent = getPlayerVehicleMechanicComponent(self.__mechanic)
            mechanicResult = mechanicComponent.tryActivate() if mechanicComponent is not None else None
            return mechanicResult is None or mechanicResult


def createSimpleActivationControl(mechanic, *_, **__):
    return SimpleActivationControl(mechanic)
