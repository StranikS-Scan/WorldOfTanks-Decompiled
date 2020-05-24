# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/EventSystemEntity.py
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, EventPriority

class EventSystemEntity(DisposableEntity):

    def fireEvent(self, event, scope=EVENT_BUS_SCOPE.DEFAULT):
        g_eventBus.handleEvent(event, scope=scope)

    def addListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.DEFAULT, priority=EventPriority.DEFAULT):
        g_eventBus.addListener(eventType, handler, scope=scope, priority=priority)

    def removeListener(self, eventType, handler, scope=EVENT_BUS_SCOPE.DEFAULT):
        g_eventBus.removeListener(eventType, handler, scope)

    def addRestriction(self, eventType, restriction, scope=EVENT_BUS_SCOPE.DEFAULT, priority=EventPriority.DEFAULT):
        g_eventBus.addRestriction(eventType, restriction, scope=scope, priority=priority)

    def removeRestriction(self, eventType, restriction, scope=EVENT_BUS_SCOPE.DEFAULT):
        g_eventBus.removeRestriction(eventType, restriction, scope)
