# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_container.py
from Event import Event, SafeEvent, EventManager, ContextEvent
from synchronous_event import SynchronousEvent
from events_debugger import EventsDebugger

class EventsContainer(object):
    __slots__ = ('_eventManager', '_debugger')

    def __init__(self):
        self._eventManager = EventManager()
        self._debugger = None
        return

    def _createEvent(self):
        return SafeEvent(self._eventManager)

    def _createSynchronousEvent(self):
        return SynchronousEvent(self._eventManager)

    def _createUnsafeEvent(self):
        return Event(self._eventManager)

    def _createContextEvent(self):
        return ContextEvent(self._eventManager)

    def _createEventsDebugger(self):
        return EventsDebugger(self)

    def clear(self):
        self._eventManager.clear()

    def destroy(self):
        self._debugger = None
        self.clear()
        return

    def debugEvents(self):
        self._debugger = self._debugger or self._createEventsDebugger()
