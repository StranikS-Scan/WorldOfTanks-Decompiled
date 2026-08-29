# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/chat_hotkey/constants.py
from enum import Enum
FEATURE = 'chat_hotkey'

class ChatHotkeyLogActions(Enum):
    HOTKEY_CLICKED = 'hotkey_clicked'
    COMMAND_SELECTED = 'command_selected'
