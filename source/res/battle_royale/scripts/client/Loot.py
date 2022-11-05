# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Loot.py
from battleground.loot_object import loadLootById, ILootObject
from constants import NULL_ENTITY_ID
from entity_game_object import EntityGameObject

class Loot(EntityGameObject):

    def onEnterWorld(self, *args):
        super(Loot, self).onEnterWorld(*args)
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
