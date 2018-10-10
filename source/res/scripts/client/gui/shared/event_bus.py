# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_bus.py
from collections import defaultdict
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING

class EVENT_BUS_SCOPE(object):
    GLOBAL = 0
    LOBBY = 1
    STATS = 2
    BATTLE = 3
    STRONGHOLD = 4
    DEFAULT = GLOBAL
    ALL = (GLOBAL,
     LOBBY,
     STATS,
     BATTLE,
     STRONGHOLD)


class EventBus(object):
    __slots__ = ('__scopes',)

    def __init__(self):
        self.__scopes = defaultdict(lambda : defaultdict(set))

    def addListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.DEFAULT):
        if handler in self.__scopes[scope][eventType]:
            LOG_WARNING('Handler is already subscribed', eventType, handler, scope)
            return
        self.__scopes[scope][eventType].add(handler)

    def removeListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.DEFAULT):
        handlers = self.__scopes[scope][eventType]
        if handler in handlers:
            handlers.remove(handler)

    def handleEvent(self, event, scope=EVENT_BUS_SCOPE.DEFAULT):
        handlers = self.__scopes[scope][event.eventType]
        for handler in handlers.copy():
            try:
                handler(event)
            except TypeError:
                LOG_CURRENT_EXCEPTION()

    def clear(self):
        for _, events in self.__scopes.iteritems():
            events.clear()

        self.__scopes.clear()


class SharedEvent(object):

    def __init__(self, eventType=None):
        super(SharedEvent, self).__init__()
        self.eventType = eventType

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


SharedEventType = type(SharedEvent)
