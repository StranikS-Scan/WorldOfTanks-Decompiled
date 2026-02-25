# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/MeteoriteZone.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from cosmic_event.gui.shared.events import MeteoriteZoneEvent

class MeteoriteZone(BigWorld.Entity):

    def set_isActive(self, _):
        self.__sendEvent(MeteoriteZoneEvent.STATE_CHANGED, {'entity': self})

    def set_vehiclesInZone(self, *args, **kwargs):
        self.__sendEvent(MeteoriteZoneEvent.VEHICLE_DAMAGE, {'vehicles': self.vehiclesInZone})

    def __sendEvent(self, event, ctx):
        g_eventBus.handleEvent(MeteoriteZoneEvent(event, ctx=ctx), scope=EVENT_BUS_SCOPE.BATTLE)
