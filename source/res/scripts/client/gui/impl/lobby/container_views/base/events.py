# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/container_views/base/events.py
from functools import partial
from Event import Event
from debug_utils import LOG_DEBUG_DEV
from entity_events import EntityEvents
from events_debugger import EventsDebugger

class EventsProviderSourceProxy(object):

    def __init__(self, component, eventsProvider):
        self.__component = component
        self.__eventsProvider = eventsProvider

    def __getattr__(self, name):
        attr = getattr(self.__eventsProvider, name)
        return self._proxy(attr) if callable(attr) and isinstance(attr, Event) else attr

    def _proxy(self, method):

        def wrapper(*args, **kwargs):
            return method(self.__component, *args, **kwargs)

        return wrapper


class ContainerLifecycleEvents(EntityEvents):

    def __init__(self):
        EntityEvents.__init__(self)
        self.onLoading = self._createEvent()
        self.onLoaded = self._createEvent()
        self.initialize = self._createEvent()
        self.finalize = self._createEvent()
        self.onReady = self._createEvent()
        self.onShown = self._createEvent()
        self.onHidden = self._createEvent()
        self.onFocus = self._createEvent()
        self.swapStates = self._createEvent()
        self.swapShowingStates = self._createEvent()

    def debugEvents(self):
        self._debugger = ContainerLifecycleEventsDebugger(self)

    def events(self):
        events = []
        for name, value in self.__dict__.items():
            if isinstance(value, Event):
                events.append((name, value))

        return events


class ComponentEventsBase(EntityEvents):

    def __init__(self):
        EntityEvents.__init__(self)
        self.onMouseEnter = self._createEvent()
        self.onMouseLeave = self._createEvent()
        self.logClick = self._createEvent()

    def debugEvents(self):
        self._debugger = ComponentEventsDebugger(self)

    def events(self):
        events = []
        for name, value in self.__dict__.items():
            if isinstance(value, Event):
                events.append((name, value))

        return events


class ContainerLifecycleEventsDebugger(EventsDebugger):

    def __init__(self, events):
        for event in dir(events):
            if event.startswith('on') and event not in dir(self):
                setattr(self, event, partial(self._logEvent, event=event))

        super(ContainerLifecycleEventsDebugger, self).__init__(events)

    def _getDebugPrefix(self):
        pass

    def _logEvent(self, event, *args, **kwargs):
        prefix = self._getDebugPrefix()
        LOG_DEBUG_DEV('{prefix} {event} called with args={args}, kwargs={kwargs}'.format(prefix=prefix, event=event, args=args, kwargs=kwargs))


class ComponentEventsDebugger(ContainerLifecycleEventsDebugger):

    def _getDebugPrefix(self):
        pass
