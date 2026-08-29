# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/commands/input_handler_command.py
import typing
from components_base.component import Component
if typing.TYPE_CHECKING:
    from typing import Any, Optional

class InputHandlerCommand(Component):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        return False
