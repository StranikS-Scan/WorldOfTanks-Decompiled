# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/comp7_dyn_objects_cache.py
from __future__ import absolute_import
import logging
import ArenaType
import BigWorld
import CGF
from points_of_interest_shared import PoiType
from dyn_objects_cache import DynObjectsBase, _SpawnPointsConfig, _PointsOfInterestConfig
_CONFIG_PATH = 'scripts/dynamic_objects.xml'
_logger = logging.getLogger(__name__)

class Comp7DynObjects(DynObjectsBase):
    _AOE_HEAL_KEY = 'aoeHeal'
    _ILLUMINATION_FLARE_KEY = 'illuminationFlare'
    __ALL_KEYS = (_AOE_HEAL_KEY, _ILLUMINATION_FLARE_KEY)
    _SPAWNPOINT_VISUAL_PATH_KEY = 'spawnPointVisualPath'

    def __init__(self):
        super(Comp7DynObjects, self).__init__()
        self.__prefabPaths = {}
        self.__cachedPrefabs = set()
        self.__spawnPointConfig = None
        self.__pointsOfInterestConfig = None
        return

    def init(self, dataSection):
        if self._initialized:
            return
        for prefabKey in self.__ALL_KEYS:
            self.__prefabPaths[prefabKey] = self.__readPrefab(dataSection, prefabKey)

        self.__spawnPointConfig = _SpawnPointsConfig.createFromXML(dataSection['spawnPointsConfig'])
        self.__pointsOfInterestConfig = _PointsOfInterestConfig.createFromXML(dataSection['pointOfInterest'])
        self.__cachedPrefabs.update(self.__collectPrefabsToCache())
        self.__cachedPrefabs.update(set(self.__pointsOfInterestConfig.getPrefabs()))
        CGF.cachePrefabs(list(self.__cachedPrefabs))
        super(Comp7DynObjects, self).init(dataSection)

    def clear(self):
        if self.__cachedPrefabs:
            CGF.removePrefabsFromCache(list(self.__cachedPrefabs))
            self.__cachedPrefabs.clear()
        self.__spawnPointConfig = None
        self.__pointsOfInterestConfig = None
        self._initialized = False
        return

    def destroy(self):
        self.clear()
        self.__prefabPaths.clear()

    def getAoeHealPrefab(self):
        return self.__prefabPaths[self._AOE_HEAL_KEY]

    def getSpawnPointsConfig(self):
        return self.__spawnPointConfig

    def getPointOfInterestConfig(self):
        return self.__pointsOfInterestConfig

    def __collectPrefabsToCache(self):
        prefabs = set()
        for prefabKey, prefabPath in self.__prefabPaths.items():
            if prefabKey == self._ILLUMINATION_FLARE_KEY and not self.__isPoiTypePresentOnArena(PoiType.ILLUMINATION_FLARE):
                continue
            prefabs.add(prefabPath)

        return prefabs

    @staticmethod
    def __isPoiTypePresentOnArena(poiType):
        player = BigWorld.player()
        if player is None:
            return False
        else:
            arenaType = ArenaType.g_cache.get(player.arenaTypeID)
            return False if arenaType is None else any((poi['type'] == poiType for poi in arenaType.pointsOfInterest))

    @staticmethod
    def __readPrefab(dataSection, key):
        return dataSection[key].readString('prefab')
