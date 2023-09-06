# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/arena_descr.py
from gui.battle_control.arena_info import settings
from gui.battle_control.arena_info.arena_descrs import ArenaWithLabelDescription

class ArenaDescription(ArenaWithLabelDescription):

    def getScreenIcon(self):
        return settings.DEFAULT_SCREEN_MAP_IMAGE_RES_PATH
