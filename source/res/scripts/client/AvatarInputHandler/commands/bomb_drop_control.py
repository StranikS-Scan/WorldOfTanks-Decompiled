# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/bomb_drop_control.py
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from gui.battle_control import avatar_getter
from items.vehicles import getEquipmentByName

class BombDropControl(InputHandlerCommand):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if isDown and CommandMapping.g_instance.isFired(CommandMapping.CMD_BOMB_DROP, key):
            avatar_getter.activateVehicleEquipment(getEquipmentByName('builtinDrop_wt').id[1], param='')
            return True
        return False
