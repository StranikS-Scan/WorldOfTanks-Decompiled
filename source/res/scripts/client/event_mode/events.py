# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/event_mode/events.py
import Event

class _EventModeEvents(object):

    def __init__(self):
        self.__manager = Event.EventManager()
        self.onUIStateChanged = self._createEvent()
        self.onUIComponentLifetime = self._createEvent()

    def destroy(self):
        self.__manager.clear()

    def _createEvent(self):
        return Event.Event(self.__manager)


g_eventModeEvents = _EventModeEvents()
