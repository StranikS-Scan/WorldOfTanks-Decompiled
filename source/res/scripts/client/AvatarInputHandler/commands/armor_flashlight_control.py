# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/armor_flashlight_control.py
import CommandMapping
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class ArmorFlashlightControl(InputHandlerCommand):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if isDown and CommandMapping.g_instance.isFired(CommandMapping.CMD_TOGGLE_ARMOR_FLASHLIGHT, key):
            armorFlashlightCtrl = self.__guiSessionProvider.shared.armorFlashlight
            return armorFlashlightCtrl.toggle()
        return False
