# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/dev_commands_control.py
import BigWorld
import Keys
from constants import HAS_DEV_RESOURCES, IS_DEVELOPMENT
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand

class DevCommandsControl(InputHandlerCommand):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and HAS_DEV_RESOURCES:
            avatar = BigWorld.player()
            if key == Keys.KEY_X:
                avatar.base.setDevelopmentFeature(0, 'reload_mechanics', 0, '')
                return False
        return False


def createDevCommandsControl():
    return DevCommandsControl() if IS_DEVELOPMENT else InputHandlerCommand()
