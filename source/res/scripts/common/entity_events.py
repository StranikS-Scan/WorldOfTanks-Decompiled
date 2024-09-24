# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/entity_events.py
from Event import Event, SafeEvent, EventManager, ContextEvent
from synchronous_event import SynchronousEvent
from events_debugger import EventsDebugger

class EntityEvents(object):
    __slots__ = ('_eventManager', '_debugger', 'onDynComponentGroupAdded', 'onDynComponentGroupRemoved')

    def __init__(self):
        self._eventManager = EventManager()
        self.onDynComponentGroupAdded = self._createEvent()
        self.onDynComponentGroupRemoved = self._createEvent()
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

    def createEvent(self):
        return self._createEvent()

    def clear(self):
        self._eventManager.clear()

    def destroy(self):
        self.clear()

    def debugEvents(self):
        self._debugger = EventsDebugger(self)
