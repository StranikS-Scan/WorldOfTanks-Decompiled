# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWGameplayDataStorage.py
import logging
import BigWorld
import Event
from constants import ARENA_BONUS_TYPE
from ids_generators import Int32IDGenerator
logger = logging.getLogger(__name__)

class HWGameplayDataStorage(BigWorld.DynamicScriptComponent):

    def __init__(self):
        self.onStorageDataAdded = Event.Event()
        self.onStorageDataDeleted = Event.Event()
        self.__idGenerator = Int32IDGenerator()
        self.__storage = {}
        self.__isEnabled = self.entity.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        self.__isEnabled = False

    def addData(self, storageKey, vehicleId, data):
        logger.debug('Add data=%s to storage with key=%s for vehicleId=%s', data, storageKey, vehicleId)
        genId = self.__idGenerator.next()
        self.__storage.setdefault(storageKey, {}).setdefault(vehicleId, {})[genId] = data
        self.onStorageDataAdded(storageKey, vehicleId, data)
        return genId

    def delData(self, storageKey, vehicleId, genId):
        logger.debug('Delete data of vehicleId=%s, storage key=%s', vehicleId, storageKey)
        self.__storage.get(storageKey, {}).get(vehicleId, {}).pop(genId, None)
        self.onStorageDataDeleted(storageKey, vehicleId)
        return

    def getAllVehicleData(self, storageKey, vehicleId):
        data = self.__storage.get(storageKey, {}).get(vehicleId, {}).values()
        logger.debug('Getting all storage data=%s of vehicleId=%s for storage key=%s', data, vehicleId, storageKey)
        return data
