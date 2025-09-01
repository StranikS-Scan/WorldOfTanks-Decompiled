# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_events/events_listener.py
import typing
from events_handler import EventsHandler, eventHandler, subscribeToEvents
from vehicles.components.component_events.events_interfaces import IComponentListener
if typing.TYPE_CHECKING:
    from vehicles.components.component_events.events_interfaces import IComponentEvents

class ComponentListener(EventsHandler, IComponentListener):

    def subscribeTo(self, events):
        subscribeToEvents(self, events, raiseException=False)

    def unsubscribeFrom(self, events):
        self._unsubscribeFromEvents(events)

    @eventHandler
    def onComponentEventsDestroy(self, events):
        self._unsubscribeFromEvents(events)
