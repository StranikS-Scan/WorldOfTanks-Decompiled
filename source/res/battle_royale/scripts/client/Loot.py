# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Loot.py
from battleground.loot_object import loadLootById, ILootObject
from constants import NULL_ENTITY_ID
from entity_game_object import EntityGameObject
from gui.shared.events import LootEvent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE

class ILootHandler(object):

    def onCreated(self, loot):
        pass

    def onDestroyed(self, loot):
        pass


class _LootHandler(ILootHandler):

    def onCreated(self, loot):
        event = LootEvent(LootEvent.LOOT_SPAWNED, ctx={'id': loot.id,
         'position': loot.position})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)

    def onDestroyed(self, loot):
        event = LootEvent(LootEvent.LOOT_PICKED_UP, ctx={'id': loot.id,
         'position': loot.position})
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.BATTLE)


class Loot(EntityGameObject):

    def __init__(self, *args, **kwargs):
        super(Loot, self).__init__(*args, **kwargs)
        self.__handler = None
        return

    def onEnterWorld(self, *args):
        super(Loot, self).onEnterWorld(*args)
        self.__handler = _LootHandler()
        self.__handler.onCreated(self)
        if self.pickedUpBy != NULL_ENTITY_ID:
            self.__onPickup()

    def set_pickedUpBy(self, prev=None):
        self.__onPickup()

    def _loadGameObject(self):
        lootObj = loadLootById(self.pickupRange, self._registerGameObject, self.typeID)
        return lootObj

    def __onPickup(self):
        entityID = self.pickedUpBy
        if self.gameObject is not None:
            self.gameObject.processPickup(entityID)
        return

    def onLeaveWorld(self):
        super(Loot, self).onLeaveWorld()
        self.__handler.onDestroyed(self)
        self.__handler = None
        return
