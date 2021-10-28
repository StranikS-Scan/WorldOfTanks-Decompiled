# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ItemPickup.py
import random
import BigWorld
from battleground.event_loot_object import loadLootByName, ILootObject
from debug_utils import LOG_DEBUG_DEV
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
NULL_ENTITY_ID = 0

class ItemPickup(BigWorld.Entity):

    def __init__(self):
        super(ItemPickup, self).__init__()
        self.__arenaLootComponent = None
        self.gameObject = None
        self.typeName = self.visualAppearanceID
        self.range = 0
        self.randomDelay = random.uniform(0.0, 0.5)
        self.__loadLootCallbackId = None
        return

    def onEnterWorld(self, *args):
        LOG_DEBUG_DEV('onEnterWorld', BigWorld.time())
        self.__loadLootCallbackId = BigWorld.callback(self.randomDelay, self.loadLoot)

    def loadLoot(self):
        self.__loadLootCallbackId = None
        self.gameObject = loadLootByName(self.range, self.__onLoad, self.typeName)
        return

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('onLeaveWorld', BigWorld.time())
        self.__getArenaLootComponent().removeLoot(self)
        if self.__loadLootCallbackId is not None:
            BigWorld.cancelCallback(self.__loadLootCallbackId)
            self.__loadLootCallbackId = None
        if self.gameObject is not None:
            self.gameObject.deactivate()
            self.gameObject.stopLoading = True
            self.gameObject = None
        return

    def set_isPickedUp(self, prev=None):
        if self.isPickedUp:
            self.__onPickup()

    def __getArenaLootComponent(self):
        if self.__arenaLootComponent:
            return self.__arenaLootComponent
        cs = BigWorld.player().arena.componentSystem
        self.__arenaLootComponent = getattr(cs, 'loot')
        return self.__arenaLootComponent

    def __onLoad(self, gameObject):
        self.gameObject = gameObject
        self.gameObject.setPosition(self.position)
        self.gameObject.activate()
        self.__getArenaLootComponent().addLoot(self)

    def __onPickup(self):
        LOG_DEBUG_DEV('__onPickup', BigWorld.time())
        if self.gameObject is not None:
            self.gameObject.processPickup(NULL_ENTITY_ID)
        g_eventBus.handleEvent(events.PickUpEvent(events.PickUpEvent.ON_PICKUP, ctx={'pickUpType': self.typeName}), scope=EVENT_BUS_SCOPE.BATTLE)
        return
