# Embedded file name: scripts/client/gui/Scaleform/framework/entities/EventSystemEntity.py
from gui.Scaleform.framework.entities.DisposableEntity import DisposableEntity
from gui.shared import g_eventBus, EVENT_BUS_SCOPE

class EventSystemEntity(DisposableEntity):

    def fireEvent(self, event, scope = EVENT_BUS_SCOPE.DEFAULT):
        g_eventBus.handleEvent(event, scope=scope)

    def addListener(self, eventType, handler, scope = EVENT_BUS_SCOPE.DEFAULT):
        g_eventBus.addListener(eventType, handler, scope=scope)

    def removeListener(self, eventType, handler, scope = EVENT_BUS_SCOPE.DEFAULT):
        g_eventBus.removeListener(eventType, handler, scope)
