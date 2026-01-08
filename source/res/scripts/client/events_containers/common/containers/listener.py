# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_containers/common/containers/listener.py
from __future__ import absolute_import
import typing
from events_handler import EventsHandler, eventHandler, subscribeToEvents
from events_containers.common.containers.interfaces import IClientEventsContainerListener
if typing.TYPE_CHECKING:
    from events_containers.common.containers.interfaces import IClientEventsContainer

class ContainersListener(EventsHandler, IClientEventsContainerListener):

    def subscribeTo(self, events):
        subscribeToEvents(self, events, raiseException=False)

    def unsubscribeFrom(self, events):
        self._unsubscribeFromEvents(events)

    def lateSubscribeTo(self, events):
        if events is not None:
            events.lateSubscribe(self)
        return

    @eventHandler
    def onEventsContainerDestroy(self, events):
        self._unsubscribeFromEvents(events)
