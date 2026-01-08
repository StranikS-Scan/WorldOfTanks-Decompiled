# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/entity_events.py
from events_container import EventsContainer

class EntityEvents(EventsContainer):
    __slots__ = ('onDynComponentGroupAdded', 'onDynComponentGroupRemoved')

    def __init__(self):
        super(EntityEvents, self).__init__()
        self.onDynComponentGroupAdded = self._createEvent()
        self.onDynComponentGroupRemoved = self._createEvent()

    def createEvent(self):
        return self._createEvent()
