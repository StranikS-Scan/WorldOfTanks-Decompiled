# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/AppearanceCacheController.py
import logging
from vehicle_systems import appearance_cache
from items import vehicles
from helpers import uniprof
_logger = logging.getLogger(__name__)

class AppearanceCacheController(object):

    def __init__(self):
        super(AppearanceCacheController, self).__init__()
        self.__appearanceCache = set()
        self.__idCounter = 0
        self.__idMap = {}

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        if hasattr(self, 'onSpawnListUpdated'):
            self.onSpawnListUpdated += self.updateAppearanceCache

    def onBecomeNonPlayer(self):
        if hasattr(self, 'onSpawnListUpdated'):
            self.onSpawnListUpdated -= self.updateAppearanceCache

    @uniprof.regionDecorator(label='AppearanceCacheController.updateAppearanceCache', scope='wrap')
    def updateAppearanceCache(self, spawnList):
        if not appearance_cache.isPrecacheEnabled():
            return
        else:
            toAdd = spawnList.difference(self.__appearanceCache)
            toRemove = self.__appearanceCache.difference(spawnList)
            for data in toAdd:
                self.__idCounter += 1
                appearanceId = -self.__idCounter
                self.__idMap[data] = appearanceId
                AppearanceCacheController._cacheAppearance(appearanceId, {'vehicleCD': data.vehicleCD,
                 'outfitCD': data.outfitCD,
                 'isAlive': True})

            for data in toRemove:
                appearanceId = self.__idMap.get(data)
                if id is None:
                    continue
                del self.__idMap[data]
                AppearanceCacheController._removeAppearance(appearanceId)

            self.__appearanceCache = spawnList
            _logger.debug('[AppearanceCacheController] Cache updated=%s', spawnList)
            return

    @staticmethod
    def _cacheAppearance(vId, vInfo):
        vInfo['vehicleType'] = vehicles.VehicleDescr(compactDescr=vInfo['vehicleCD'])
        appearance_cache.cacheApperance(vId, vInfo)

    @staticmethod
    def _removeAppearance(vId):
        appearance_cache.removeAppearance(vId)
