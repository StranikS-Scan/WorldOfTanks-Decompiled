# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Event.py
from functools import partial
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
        self._subscribeList = []
        self._contextSubscribeList = []

    def subscribeToContextEvent(self, event, delegate, *contextIDs):
        event.subscribe(delegate, *contextIDs)
        self._contextSubscribeList.append((event, delegate))

    def subscribeToEvent(self, event, delegate):
        event += delegate
        self._subscribeList.append((event, delegate))

    def subscribeToContextEvents(self, *subscribers):
        for event, delegate, contextIDs in subscribers:
            event.subscribe(delegate, *contextIDs)
            self._contextSubscribeList.append((event, delegate))

    def subscribeToEvents(self, *subscribers):
        for subscriber in subscribers:
            event, delegate = subscriber
            event += delegate
            self._subscribeList.append(subscriber)

    def unsubscribeFromAllEvents(self):
        for event, delegate in self._subscribeList:
            event -= delegate

        for event, delegate in self._contextSubscribeList:
            event.unsubscribe(delegate)

        self._subscribeList = []


class SuspendableEventSubscriber(EventsSubscriber):

    def __init__(self):
        super(SuspendableEventSubscriber, self).__init__()
        self.__suspendedSubscribes = []
        self.__suspendedContextSubscribes = []

    def pause(self, eventsList=None):
        if eventsList is None:
            for event, subscriber in self._subscribeList:
                if eventsList is None:
                    event -= subscriber
                if event in eventsList:
                    event -= subscriber
                    self.__suspendedSubscribes.append((event, subscriber))

            for event, subscriber in self._contextSubscribeList:
                if eventsList is None:
                    event.unsubscribe(subscriber)
                if event in eventsList:
                    event.unsubscribe(subscriber)
                    self.__suspendedContextSubscribes.append((event, subscriber))

        return

    def resume(self):
        subscribers = self.__suspendedSubscribes or self._subscribeList
        for event, subscriber in subscribers:
            event += subscriber

        subscribers = self.__suspendedContextSubscribes or self._contextSubscribeList
        for event, subscriber in subscribers:
            event.subscribe(subscriber)


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


class EventCallback(object):
    __slots__ = ('event', '_callback')

    def __init__(self, event, callback):
        self.event = event
        self._callback = callback
        self.event += self.callback

    def callback(self, *args, **kwargs):
        self._callback(*args, **kwargs)
        self.event -= self.callback


class PriorityEvent(Event):

    def __repr__(self):
        return 'PriorityEvent(%s)(%s):%s' % (self.__class__.__name__, len(self), repr(self[:]))

    def __iadd__(self, delegate):
        if not callable(delegate):
            raise TypeError('Event listener is not callable.')
        if not hasattr(delegate, '__cmp__'):
            raise TypeError('Event listener is not comparable.')
        if delegate not in self:
            self.append(delegate)
            self[:] = sorted(self)
        return self


class AroundFunctionEvents(EventManager):

    class Bypass(Exception):
        pass

    __slots__ = ('callable', 'before', 'after')

    def __init__(self, fun, eventClassFactory=Event):
        super(AroundFunctionEvents, self).__init__()
        self.callable = fun
        self.before = eventClassFactory(self)
        self.after = eventClassFactory(self)

    def __call__(self, *args, **kwargs):
        try:
            self.before(*args, **kwargs)
            res = self.callable(*args, **kwargs)
        except AroundFunctionEvents.Bypass:
            res = None

        self.after(*args, **kwargs)
        return res

    def pre(self, handler):
        self.before += handler
        return handler

    def post(self, handler):
        self.after += handler
        return handler

    def around(self, handler):
        self.before += partial(handler, isBefore=True)
        self.after += handler
        return handler
