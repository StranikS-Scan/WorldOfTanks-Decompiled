# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_event_handle_key.py
import constants
import CommandMapping
from gui.battle_control import event_dispatcher as gui_event_dispatcher

class AvatarEventHandleKey(object):

    def __init__(self):
        pass

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        pass

    def handleKey(self, isDown, key, mods):
        cmdMap = CommandMapping.g_instance
        if self.arenaBonusType == constants.ARENA_BONUS_TYPE.EVENT_BATTLES and cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_VISIBLE, CommandMapping.CMD_EVENT_MAP_VISIBLE), key):
            gui_event_dispatcher.setEventMinimapCmd(key, isDown)
            return True
