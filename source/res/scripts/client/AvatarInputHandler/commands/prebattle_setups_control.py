# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/prebattle_setups_control.py
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from gui.battle_control import event_dispatcher
_SETUP_CMDS = (CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_1, CommandMapping.CMD_AMMUNITION_SHORTCUT_SWITCH_SETUP_2)

class PrebattleSetupsControl(InputHandlerCommand):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if CommandMapping.g_instance.isFiredList(_SETUP_CMDS, key) and isDown:
            event_dispatcher.changeAmmunitionSetup(key)
            return True
        return False
