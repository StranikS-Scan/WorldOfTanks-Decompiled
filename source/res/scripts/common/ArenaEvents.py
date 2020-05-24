# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ArenaEvents.py
import Event

class ArenaEvents(object):

    def __init__(self):
        self.__eventManager = em = Event.EventManager()
        self.onArenaStarted = Event.SafeEvent(em)
        self.onArenaStoped = Event.SafeEvent(em)
        self.onVehicleCreated = Event.SafeEvent(em)

    def destroy(self):
        self.__eventManager.clear()

    def clear(self):
        self.__eventManager.clear()

    def debugEvents(self, arena):
        self.__eventsDebugger = EventsDebugger(arena)

    @staticmethod
    def subscribeOnEvents(up, requiredEvents, events, subscriber):
        for eventName in requiredEvents:
            event = getattr(events, eventName)
            processor = getattr(subscriber, eventName)
            if up:
                event += processor
            event -= processor


class EventsDebugger(object):
    ARENA_EVENTS = ('onArenaStarted', 'onArenaStoped', 'onVehicleCreated')

    def __init__(self, arena):
        events = arena.events
        for eventName in self.ARENA_EVENTS:
            event = getattr(events, eventName)
            processor = getattr(self, eventName)
            event += processor

    def onArenaStarted(self, vehicle):
        pass

    def onArenaStoped(self, vehicle):
        pass

    def onVehicleCreated(self, vehicle):
        pass
