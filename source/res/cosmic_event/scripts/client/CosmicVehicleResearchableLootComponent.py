# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/CosmicVehicleResearchableLootComponent.py
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from cosmic_event.gui.shared.events import CosmicVehicleEvent, LootEvent
from VehicleResearchableLootComponent import VehicleResearchableLootComponent

class CosmicVehicleResearchableLootComponent(VehicleResearchableLootComponent):

    def set_isActive(self, _):
        if self.isActive:
            self.__sendEvent(CosmicVehicleEvent.START_LOOT_RESEARCHING, {'playerName': self.entity.publicInfo.name,
             'lifeTimeRemained': self.lifeTimeRemained,
             'vehicleGO': self.entity.entityGameObject,
             'ownerID': self.entity.id})
        else:
            self.__sendEvent(CosmicVehicleEvent.STOP_LOOT_RESEARCHING, {'playerName': self.entity.publicInfo.name,
             'vehicleGO': self.entity.entityGameObject})

    def _onAvatarReady(self):
        if self.isActive:
            self.__sendEvent(CosmicVehicleEvent.START_LOOT_RESEARCHING, {'playerName': self.entity.publicInfo.name,
             'lifeTimeRemained': self.lifeTimeRemained,
             'vehicleGO': self.entity.entityGameObject})

    def set_lootTransferTime(self, _):
        self.__sendEvent(CosmicVehicleEvent.LOOT_TRANSFER, {'fromEntityID': self.lootObtainedFromID,
         'destEntityID': self.entity.id})

    def set_researchDoneTime(self, _):
        isPC = self.entity.id == BigWorld.player().playerVehicleID
        self.__sendEvent(CosmicVehicleEvent.LOOT_RESEARCHING_DONE, {'isPC': isPC,
         'position': self.entity.position})

    def __sendEvent(self, event, ctx):
        g_eventBus.handleEvent(LootEvent(event, ctx=ctx), scope=EVENT_BUS_SCOPE.BATTLE)
