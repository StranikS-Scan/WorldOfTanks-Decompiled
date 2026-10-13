# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_container.py
from __future__ import absolute_import
import typing
from Event import Event, SafeEvent, EventManager, ContextEvent
from synchronous_event import SynchronousEvent
from events_debugger import EventsDebugger
if typing.TYPE_CHECKING:
    from events_handler import EventsHandler

class EventsContainer(object):
    __slots__ = ('_eventManager', '_debugger', '_coreIntegration', 'onEventsContainerDestroy')

    def __init__(self):
        self._eventManager = EventManager()
        self.onEventsContainerDestroy = self._createEvent()
        self._coreIntegration = None
        self._debugger = None
        return

    def attachCoreEvents(self):
        self._coreIntegration = self._coreIntegration or self._createCoreIntegration()

    def clear(self):
        self._eventManager.clear()

    def destroy(self):
        self.onEventsContainerDestroy(self)
        self._coreIntegration = None
        self._debugger = None
        self.clear()
        return

    def debugEvents(self):
        self._debugger = self._debugger or self._createEventsDebugger()

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

    def _createCoreIntegration(self):
        return None
