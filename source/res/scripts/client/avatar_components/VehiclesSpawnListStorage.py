# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/VehiclesSpawnListStorage.py
import logging
import cPickle
from VehiclesSpawnListStorageCommon import convertTuplesToVehicleSpawnData
from Event import Event
_logger = logging.getLogger(__name__)

class VehiclesSpawnListStorage(object):

    def __init__(self):
        super(VehiclesSpawnListStorage, self).__init__()
        self.onSpawnListUpdated = Event()

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        pass

    def updateSpawnList(self, spawnListData):
        spawnList = convertTuplesToVehicleSpawnData(cPickle.loads(spawnListData))
        self.onSpawnListUpdated(spawnList)
