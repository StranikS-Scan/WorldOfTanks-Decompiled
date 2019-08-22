# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Loot.py
import BigWorld
from battleground.loot_object import loadLootById, ILootObject
from constants import NULL_ENTITY_ID
from debug_utils import LOG_DEBUG_DEV

class Loot(BigWorld.Entity):

    def __init__(self):
        self.gameObject = None
        return

    def __onLoad(self, gameObject):
        self.gameObject = gameObject
        self.gameObject.setMotor(self.matrix)
        self.gameObject.activate()

    def __onPickup(self):
        entityID = self.pickedUpBy
        LOG_DEBUG_DEV('__onPickup', BigWorld.time(), entityID)
        if self.gameObject is not None:
            self.gameObject.processPickup(entityID)
        return

    def onEnterWorld(self, *args):
        LOG_DEBUG_DEV('onEnterWorld', BigWorld.time(), self.pickedUpBy, self.typeID)
        self.gameObject = loadLootById(self.pickupRange, self.__onLoad, self.typeID)
        if self.pickedUpBy != NULL_ENTITY_ID:
            self.__onPickup()

    def onLeaveWorld(self):
        LOG_DEBUG_DEV('onLeaveWorld', BigWorld.time(), self.pickedUpBy)
        if self.gameObject is not None:
            self.gameObject.deactivate()
            self.gameObject.destroy()
            self.gameObject.stopLoading = True
            self.gameObject = None
        return

    def set_pickedUpBy(self, prev=None):
        self.__onPickup()
