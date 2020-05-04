# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/trigger_controller.py
import Event
from constants import ARENA_BONUS_TYPE

class TriggerController(object):

    def __init__(self):
        self.__enabled = False
        self.onTrigger = Event.Event()

    def onBecomePlayer(self):
        self.__enabled = self.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES

    def onBecomeNonPlayer(self):
        self.__enabled = False

    def externalTrigger(self, eventId, extra):
        if not self.__enabled:
            return
        self.onTrigger(eventId, extra)

    def handleKey(self, isDown, key, mods):
        pass
