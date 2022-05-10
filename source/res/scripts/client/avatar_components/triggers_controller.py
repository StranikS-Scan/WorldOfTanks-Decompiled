# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/triggers_controller.py
import Event

class TriggersController(object):

    def __init__(self):
        self.__enabled = False
        self.onTrigger = Event.Event()

    def onBecomePlayer(self):
        self.__enabled = True

    def onBecomeNonPlayer(self):
        self.__enabled = False

    def externalTrigger(self, eventId, extra):
        if not self.__enabled:
            return
        self.onTrigger(eventId, extra)

    def handleKey(self, isDown, key, mods):
        pass
