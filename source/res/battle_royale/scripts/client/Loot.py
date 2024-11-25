# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Loot.py
import BigWorld
import CGF
import Math
from battleground.loot_object import loadLootById
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from battle_royale.gui.shared.events import LootEvent

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
        g_eventBus.handleEvent(LootEvent(LootEvent.LOOT_PICKED_UP, ctx={'id': self.id}), scope=EVENT_BUS_SCOPE.BATTLE)
        if self.__lootDescr is not None:
            CGF.loadGameObject(self.__lootDescr.prefabPickup, self.spaceID, self.position)
        return
