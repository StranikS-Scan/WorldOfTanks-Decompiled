# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/auto_shoot_gun_control.py
import Keys
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import AUTO_SHOOT_DEV_KEYS, AutoShootDevCommand
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class DevAutoShootGunControl(InputHandlerCommand):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _KEY_TO_COMMAND_MAP = {Keys.KEY_RIGHTARROW: AutoShootDevCommand.RATE_UP,
     Keys.KEY_LEFTARROW: AutoShootDevCommand.RATE_DOWN,
     Keys.KEY_UPARROW: AutoShootDevCommand.RATE_SPEED_UP,
     Keys.KEY_DOWNARROW: AutoShootDevCommand.RATE_SPEED_DOWN,
     Keys.KEY_RSHIFT: AutoShootDevCommand.CLAMP_BURST,
     Keys.KEY_RCONTROL: AutoShootDevCommand.RESET}

    def handleKeyEvent(self, isDown, key, mods, event=None):
        return super(DevAutoShootGunControl, self).handleKeyEvent(isDown, key, mods, event=event) if not self.__handleDevKeyEvent(isDown, key) else True

    def __handleDevKeyEvent(self, isDown, key):
        if not (key in self._KEY_TO_COMMAND_MAP and isDown):
            return False
        else:
            autoShootCtrl = self.__sessionProvider.shared.autoShootCtrl
            if autoShootCtrl is None:
                return False
            autoShootCtrl.processAutoShootDevCmd(self._KEY_TO_COMMAND_MAP[key])
            return True


def createAutoShootGunControl():
    return DevAutoShootGunControl() if AUTO_SHOOT_DEV_KEYS else InputHandlerCommand()
