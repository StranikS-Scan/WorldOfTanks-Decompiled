# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Event.py
from debug_utils import LOG_CURRENT_EXCEPTION

class Event(list):
    __slots__ = ('__weakref__',)

    def __init__(self, manager=None):
        list.__init__(self)
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args, **kwargs):
        for delegate in self[:]:
            try:
                delegate(*args, **kwargs)
            except:
                LOG_CURRENT_EXCEPTION()
                raise

    def __iadd__(self, delegate):
        if not callable(delegate):
            raise TypeError('Event listener is not callable.')
        if delegate not in self:
            self.append(delegate)
        return self

    def __isub__(self, delegate):
        if delegate in self:
            self.remove(delegate)
        return self

    def clear(self):
        del self[:]

    def __repr__(self):
        return 'Event(%s)(%s):%s' % (self.__class__.__name__, len(self), repr(self[:]))


class SafeEvent(Event):
    __slots__ = ()

    def __init__(self, manager=None):
        super(SafeEvent, self).__init__(manager)

    def __call__(self, *args, **kwargs):
        for delegate in self[:]:
            try:
                delegate(*args, **kwargs)
            except:
                LOG_CURRENT_EXCEPTION()


class SafeComponentEvent(SafeEvent):

    def __init__(self, manager=None, component=None):
        super(SafeComponentEvent, self).__init__(manager)
        self.__component = component

    def __call__(self, *args, **kwargs):
        if self.__component is None or not self.__component.isActive:
            return
        else:
            super(SafeEvent, self).__call__(*args, **kwargs)
            return

    def clear(self):
        self.__component = None
        super(SafeComponentEvent, self).clear()
        return


class Handler(object):
    __slots__ = ('__delegate',)

    def __init__(self, manager=None):
        self.__delegate = None
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args, **kwargs):
        return self.__delegate(*args, **kwargs) if self.__delegate is not None else None

    def set(self, delegate):
        self.__delegate = delegate

    def clear(self):
        self.__delegate = None
        return


class EventManager(object):
    __slots__ = ('__events',)

    def __init__(self):
        self.__events = []

    def register(self, event):
        self.__events.append(event)

    def clear(self):
        for event in self.__events:
            event.clear()


class SuspendedEvent(Event):
    __slots__ = ('__manager',)

    def __init__(self, manager):
        super(SuspendedEvent, self).__init__(manager)
        self.__manager = manager

    def clear(self):
        self.__manager = None
        super(SuspendedEvent, self).clear()
        return

    def __call__(self, *args, **kwargs):
        if self.__manager.isSuspended():
            self.__manager.suspendEvent(self, *args, **kwargs)
        else:
            super(SuspendedEvent, self).__call__(*args, **kwargs)


class SuspendedEventManager(EventManager):
    __slots__ = ('__isSuspended', '__suspendedEvents')

    def __init__(self):
        super(SuspendedEventManager, self).__init__()
        self.__isSuspended = False
        self.__suspendedEvents = []

    def suspendEvent(self, e, *args, **kwargs):
        self.__suspendedEvents.append((e, args, kwargs))

    def isSuspended(self):
        return self.__isSuspended

    def suspend(self):
        self.__isSuspended = True

    def resume(self):
        if self.__isSuspended:
            self.__isSuspended = False
            while self.__suspendedEvents:
                e, args, kwargs = self.__suspendedEvents.pop(0)
                e(*args, **kwargs)

    def clear(self):
        self.__isSuspended = False
        self.__suspendedEvents = []
        super(SuspendedEventManager, self).clear()


class EventsSubscriber(object):

    def __init__(self):
        super(EventsSubscriber, self).__init__()
        self.__subscribeList = []
        self.__contextSubscribeList = []

    def subscribeToContextEvent(self, event, delegate, *contextIDs):
        event.subscribe(delegate, *contextIDs)
        self.__contextSubscribeList.append((event, delegate))

    def subscribeToEvent(self, event, delegate):
        event += delegate
        self.__subscribeList.append((event, delegate))

    def unsubscribeFromAllEvents(self):
        for event, delegate in self.__subscribeList:
            event -= delegate

        for event, delegate in self.__contextSubscribeList:
            event.unsubscribe(delegate)

        self.__subscribeList = []


class ContextEvent(object):
    __allContexts = object()

    def __init__(self, manager=None):
        self.__contextSubscribers = {}
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, contextID, *args, **kwargs):
        subscribers = self.__contextSubscribers.get(contextID)
        if subscribers:
            for subscriber in subscribers:
                subscriber(contextID, *args, **kwargs)

        subscribers = self.__contextSubscribers.get(self.__allContexts)
        if subscribers:
            for subscriber in subscribers:
                subscriber(contextID, *args, **kwargs)

    def subscribe(self, delegate, *contextIDs):
        if contextIDs:
            for contextID in contextIDs:
                self.__contextSubscribers.setdefault(contextID, set())
                self.__contextSubscribers[contextID].add(delegate)

        else:
            self.__contextSubscribers.setdefault(self.__allContexts, set())
            self.__contextSubscribers[self.__allContexts].add(delegate)

    def unsubscribe(self, delegate):
        for contextSubscribers in self.__contextSubscribers.itervalues():
            contextSubscribers.discard(delegate)

    def clear(self):
        self.__contextSubscribers.clear()
