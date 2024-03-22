# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/clan_supply/constants.py
from enum import Enum
FEATURE = 'clan_supply'

class ClanSupplyLogAction(Enum):
    CLOSE = 'close'
    OPEN = 'open'


class ClanSupplyLogKeys(Enum):
    QUESTS_SCREEN = 'tour_task_screen_window'
    PROGRESSION_SCREEN = 'map_screen_window'
    CLAN_LANDING = 'clan_landing'
    NOTIFICATION = 'notification'
    HANGAR_HEADER = 'hangar_header'
    BACK_BUTTON = 'back_button'
    SIDEBAR_PROGRESSION = 'sidebar_map'
    SIDEBAR_QUEST = 'sidebar_quest'
