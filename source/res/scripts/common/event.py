# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Event.py
from debug_utils import LOG_CURRENT_EXCEPTION

class Event(object):
    """
    Allows delegates to subscribe for the event and to be called when event
    is triggered.
    
    Clearing events without event manager:
        onEvent1 = Event()
        onEvent2 = Event()
        ...
        onEvent1.clear()
        onEvent2.clear()
    
    Clearing events with event manager:
        em = EventManager()
        onEvent1 = Event(em)
        onEvent2 = Event(em)
        ...
        em.clear()
    """

    def __init__(self, manager=None):
        """
        :param manager - event manager that is used to clear all events thereby
        break all references.
        """
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

    def __iadd__(self, delegate):
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
    """
    Similar to Event. Difference is Handler allows only one delegate to be
    subscribed. One event manager could be used both for handlers and events.
    """

    def __init__(self, manager=None):
        """
        :param manager - event manager that is used to clear all handlers
        thereby break all references.
        """
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
    """
    Event manager that is used to clear all events thereby break all references.
    """

    def __init__(self):
        self.__events = []

    def register(self, event):
        self.__events.append(event)

    def clear(self):
        for event in self.__events:
            event.clear()
