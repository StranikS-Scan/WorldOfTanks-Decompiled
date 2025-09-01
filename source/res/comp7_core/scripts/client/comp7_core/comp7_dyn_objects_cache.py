# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/comp7_dyn_objects_cache.py
import logging
import CGF
from dyn_objects_cache import DynObjectsBase, _SpawnPointsConfig, _PointsOfInterestConfig
_CONFIG_PATH = 'scripts/dynamic_objects.xml'
_logger = logging.getLogger(__name__)

class Comp7DynObjects(DynObjectsBase):
    _AOE_HEAL_KEY = 'aoeHeal'
    __ALL_KEYS = (_AOE_HEAL_KEY,)
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
        self.__cachedPrefabs.update(set(self.__prefabPaths.values()))
        self.__cachedPrefabs.update(set(self.__pointsOfInterestConfig.getPrefabs()))
        CGF.cacheGameObjects(list(self.__cachedPrefabs), False)
        super(Comp7DynObjects, self).init(dataSection)

    def clear(self):
        if self.__cachedPrefabs:
            CGF.clearGameObjectsCache(list(self.__cachedPrefabs))
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

    @staticmethod
    def __readPrefab(dataSection, key):
        return dataSection[key].readString('prefab')
