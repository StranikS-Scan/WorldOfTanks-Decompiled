# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/mechanic_controls/nitro_control.py
import typing
import logging
import BigWorld
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_helpers import getPlayerVehicleMechanic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
_logger = logging.getLogger(__name__)
CLICK_THRESHOLD = 0.75

class NitroActivationControl(InputHandlerCommand):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, mechanic):
        self.__mechanic = mechanic
        self.__startTime = BigWorld.time()
        self.__stopTime = BigWorld.time()

    def __alternateNitro(self):
        mechanicComponent = getPlayerVehicleMechanic(self.__mechanic)
        if mechanicComponent:
            mechanicComponent.alternateOnState()

    def __cancelNitro(self):
        mechanicComponent = getPlayerVehicleMechanic(self.__mechanic)
        if mechanicComponent:
            mechanicComponent.tryDeactivate()

    def handleKeyEvent(self, isDown, key, mods, event=None):
        mechanicCmd = CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION
        if not CommandMapping.g_instance.isFired(mechanicCmd, key):
            return False
        if isDown:
            self.__startTime = BigWorld.time()
        else:
            self.__stopTime = BigWorld.time()
        if not isDown and abs(self.__stopTime - self.__startTime) < CLICK_THRESHOLD:
            return False
        if isDown:
            self.__alternateNitro()
        else:
            self.__cancelNitro()
        return True


def createNitroActivationControl(mechanic, *_, **__):
    return NitroActivationControl(mechanic)
