# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Event.py
from debug_utils import LOG_CURRENT_EXCEPTION

class Event(object):

    def __init__(self, manager=None):
        self.__delegates = []
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args, **kwargs):
        for delegate in self.__delegates[:]:
            try:
                delegate(*args, **kwargs)
            except:
                LOG_CURRENT_EXCEPTION()
                raise

    def __iadd__(self, delegate):
        if not callable(delegate):
            raise TypeError('Event listener is not callable.')
        if delegate not in self.__delegates:
            self.__delegates.append(delegate)
        return self

    def __isub__(self, delegate):
        if delegate in self.__delegates:
            self.__delegates.remove(delegate)
        return self

    def clear(self):
        del self.__delegates[:]

    def __repr__(self):
        return 'Event(%s):%s' % (len(self.__delegates), repr(self.__delegates))


class Handler(object):

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

    def __init__(self):
        self.__events = []

    def register(self, event):
        self.__events.append(event)

    def clear(self):
        for event in self.__events:
            event.clear()


class SuspendedEvent(Event):

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
