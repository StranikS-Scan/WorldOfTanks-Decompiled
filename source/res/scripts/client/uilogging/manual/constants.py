# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/manual/constants.py
from enum import Enum
FEATURE = 'manual'

class ManualLogActions(Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'


class ManualLogKeys(Enum):
    LOBBY_MENU_BUTTON = 'lobby_menu_button'
    CHAPTER_VIDEO = 'chapter_video'
