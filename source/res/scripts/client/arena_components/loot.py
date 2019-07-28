# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/loot.py
from Event import Event
from arena_component_system.client_arena_component_system import ClientArenaComponent

class LootComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__lootEntities = {}
        self.onLootAdded = Event()
        self.onLootRemoved = Event()

    def addLoot(self, loot):
        self.__lootEntities[loot.id] = loot
        self.onLootAdded(loot)

    def removeLoot(self, loot):
        if loot.id in self.__lootEntities:
            del self.__lootEntities[loot.id]
            self.onLootRemoved(loot)

    def getLootEntities(self):
        return self.__lootEntities

    def getLootByID(self, lootID):
        return self.__lootEntities[lootID] if lootID in self.__lootEntities else None
