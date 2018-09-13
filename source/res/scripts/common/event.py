# Embedded file name: scripts/common/Event.py
from debug_utils import *

class Event(object):

    def __init__(self, manager = None):
        self.__delegates = set()
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args):
        for delegate in set(self.__delegates):
            try:
                delegate(*args)
            except:
                LOG_CURRENT_EXCEPTION()

    def __iadd__(self, delegate):
        self.__delegates.add(delegate)
        return self

    def __isub__(self, delegate):
        self.__delegates.discard(delegate)
        return self

    def clear(self):
        self.__delegates.clear()

    def __repr__(self):
        return 'Event(%s):%s' % (len(self.__delegates), repr(self.__delegates))


class Handler(object):

    def __init__(self, manager = None):
        self.__delegate = None
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args):
        if self.__delegate is not None:
            return self.__delegate(*args)
        else:
            return

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
