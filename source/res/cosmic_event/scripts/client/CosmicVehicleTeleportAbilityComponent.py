# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicVehicleTeleportAbilityComponent.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from cosmic_event.gui.shared.events import Teleport

class CosmicVehicleTeleportAbilityComponent(BigWorld.DynamicScriptComponent):

    def set_teleportPosition(self, prev):
        self.__sendEvent(Teleport.PREPARED, {'position': self.teleportPosition})

    def set_teleportGlimpseFrom(self, _):
        self.__sendEvent(Teleport.ACTIVATED, {'go': self.teleportGlimpseFrom})

    def set_teleportGlimpseTo(self, _):
        self.__sendEvent(Teleport.ACTIVATED, {'go': self.teleportGlimpseTo})

    def onDestroy(self):
        self.__sendEvent(Teleport.EXHAUSTED, {'go': self.entity.entityGameObject})

    def __sendEvent(self, event, ctx):
        g_eventBus.handleEvent(Teleport(event, ctx=ctx), scope=EVENT_BUS_SCOPE.BATTLE)
