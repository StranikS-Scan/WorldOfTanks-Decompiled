# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush_dyn_object_cache.py
from __future__ import absolute_import
import typing
import CGF
from dyn_objects_cache import DynObjectsBase

class _FortRushDynObjects(DynObjectsBase):

    def __init__(self):
        super(_FortRushDynObjects, self).__init__()
        self.__prefabPaths = []

    def init(self, dataSection):
        if self._initialized:
            return
        self.__prefabPaths = [ value.asString for key, value in dataSection['prefabs'].items() if key == 'path' and value.asString ]
        if self.__prefabPaths:
            CGF.cachePrefabs(self.__prefabPaths)
        super(_FortRushDynObjects, self).init(dataSection)

    def clear(self):
        if self.__prefabPaths:
            CGF.removePrefabsFromCache(list(self.__prefabPaths))
            del self.__prefabPaths[:]
        self._initialized = False
        super(_FortRushDynObjects, self).clear()

    def destroy(self):
        self.clear()
        super(_FortRushDynObjects, self).destroy()
