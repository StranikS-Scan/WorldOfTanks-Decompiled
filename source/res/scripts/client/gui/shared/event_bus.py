# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/event_bus.py
import heapq
import logging
from BWUtil import AsyncReturn
from collections import defaultdict
from debug_utils import LOG_CURRENT_EXCEPTION
from adisp import process, isAsync
from async import async, await, await_callback
_logger = logging.getLogger(__name__)

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


class EventPriority(object):
    HIGH = 0
    LOW = 1
    DEFAULT = LOW


class _PriorityQueue(object):

    def __init__(self):
        self._queue = []
        self._finder = {}

    def add(self, item, priority):
        entry = (priority, item)
        self._finder[item] = entry
        heapq.heappush(self._queue, entry)

    def remove(self, item):
        entry = self._finder.pop(item)
        self._queue.remove(entry)
        heapq.heapify(self._queue)

    def __contains__(self, item):
        entry = self._finder.get(item)
        return entry in self._queue

    def __iter__(self):
        for _, item in self._queue[:]:
            yield item


class EventBus(object):
    __slots__ = ('__handlers', '__restrictions')

    def __init__(self):
        self.__handlers = defaultdict(lambda : defaultdict(_PriorityQueue))
        self.__restrictions = defaultdict(lambda : defaultdict(_PriorityQueue))

    def addListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.DEFAULT, priority=EventPriority.DEFAULT):
        queue = self.__handlers[scope][eventType]
        if handler in queue:
            _logger.warning('Handler is already subscribed. eventType: %s; handler: %s; scope: %d; priority: %d', eventType, handler, scope, priority)
            return
        queue.add(handler, priority)

    def removeListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.DEFAULT):
        queue = self.__handlers[scope][eventType]
        if handler in queue:
            queue.remove(handler)

    def addRestriction(self, eventType, restriction, scope=EVENT_BUS_SCOPE.DEFAULT, priority=EventPriority.DEFAULT):
        queue = self.__restrictions[scope][eventType]
        if restriction in queue:
            _logger.warning('Restriction is already subscribed. eventType: %s; restriction: %s; scope: %d; priority: %d', eventType, restriction, scope, priority)
            return
        queue.add(restriction, priority)

    def removeRestriction(self, eventType, restriction, scope=EVENT_BUS_SCOPE.DEFAULT):
        queue = self.__restrictions[scope][eventType]
        if restriction not in queue:
            _logger.warning('Restriction is not subscribed. eventType: %s; restriction: %s; scope: %d', eventType, restriction, scope)
            return
        queue.remove(restriction)

    @async
    def handleEvent(self, event, scope=EVENT_BUS_SCOPE.DEFAULT):
        confirmed = yield await(self.__verify(event, scope))
        if not confirmed:
            return
        handlers = self.__handlers[scope][event.eventType]
        for handler in handlers:
            try:
                handler(event)
            except TypeError:
                LOG_CURRENT_EXCEPTION()

    def clear(self):
        for _, events in self.__handlers.iteritems():
            events.clear()

        self.__handlers.clear()
        for _, events in self.__restrictions.iteritems():
            events.clear()

        self.__restrictions.clear()

    @async
    def __verify(self, event, scope):
        restrictions = self.__restrictions[scope][event.eventType]
        for restriction in restrictions:
            try:
                if isAsync(restriction):
                    proceed = yield await_callback(self.__verifyAsyncProcess)(restriction, event)
                else:
                    proceed = restriction(event)
                if not proceed:
                    raise AsyncReturn(False)
            except TypeError:
                LOG_CURRENT_EXCEPTION()

        raise AsyncReturn(True)

    @process
    def __verifyAsyncProcess(self, restriction, event, callback=None):
        proceed = yield restriction(event)
        if not proceed:
            _logger.debug('Event was restricted. eventType: %s; restriction: %s', event.eventType, restriction)
            callback(False)
            return
        callback(True)


class SharedEvent(object):

    def __init__(self, eventType=None):
        super(SharedEvent, self).__init__()
        self.eventType = eventType

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


SharedEventType = type(SharedEvent)
