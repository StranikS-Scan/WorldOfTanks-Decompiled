# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Loot.py
import BigWorld
import CGF
import Math
from battleground.loot_object import loadLootById

class Loot(BigWorld.Entity):

    def __init__(self, *args, **kwargs):
        super(Loot, self).__init__(*args, **kwargs)
        self.__lootDescr = None
        return

    def onEnterWorld(self, *args):
        self.__lootDescr = loadLootById(self.typeID)
        if self.__lootDescr is not None:
            CGF.loadGameObjectIntoHierarchy(self.__lootDescr.prefab, self.entityGameObject, Math.Vector3())
        return

    def onLeaveWorld(self):
        self.__lootDescr = None
        return

    def set_pickedUpBy(self, prev=None):
        if self.__lootDescr is not None:
            CGF.loadGameObject(self.__lootDescr.prefabPickup, self.spaceID, self.position)
        return
