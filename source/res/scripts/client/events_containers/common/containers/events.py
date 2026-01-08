# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_containers/common/containers/events.py
from __future__ import absolute_import
from Event import LateEvent
from events_containers.common.containers.interfaces import IClientEventsContainer
from events_containers.common.containers.listener import ContainersListener
from events_container import EventsContainer
from events_debugger import EventsDebugger

class ClientEventsContainer(EventsContainer, IClientEventsContainer):

    def __init__(self):
        super(ClientEventsContainer, self).__init__()
        self.onEventsContainerDestroy = self._createEvent()
        self._cgfIntegration = None
        return

    @property
    def hasListeners(self):
        return self._eventManager.hasAnyListener

    def destroy(self):
        self.onEventsContainerDestroy(self)
        self._cgfIntegration = None
        super(ClientEventsContainer, self).destroy()
        return

    def attachCFGEvents(self):
        self._cgfIntegration = self._cgfIntegration or self._createCGFIntegration()

    def _createLateEvent(self, lateCallback):
        return LateEvent(lateCallback, self._eventManager)

    def _createTimeIntervalEvent(self, interval, timeCallback=None):
        from gui.shared.utils.TimeInterval import TimeIntervalEvent
        return TimeIntervalEvent(interval, timeCallback, self._eventManager)

    def _createCGFIntegration(self):
        return ClientEventsContainerCGFIntegration(self)

    def _createEventsDebugger(self):
        return ClientEventsContainerDebugger(self)


class ClientEventsContainerCGFIntegration(ContainersListener):

    def __init__(self, events):
        self._attachToEventsContainer(events)

    def _attachToEventsContainer(self, events):
        self.subscribeTo(events)


class ClientEventsContainerDebugger(EventsDebugger):
    IGNORED_EVENTS = ('onEventsContainerDestroy',)

    def _getDebugPrefix(self):
        pass

    def _shouldHandle(self, eventName):
        return eventName not in self.IGNORED_EVENTS
