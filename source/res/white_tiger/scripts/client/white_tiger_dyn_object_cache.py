# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger_dyn_object_cache.py
import typing
import CGF
from dyn_objects_cache import DynObjectsBase

class _WhiteTigerDynObjects(DynObjectsBase):

    def __init__(self):
        super(_WhiteTigerDynObjects, self).__init__()
        self.__prefabPaths = []

    def init(self, dataSection):
        if self._initialized:
            return
        self.__prefabPaths = [ value.asString for key, value in dataSection['prefabs'].items() if key == 'path' and value.asString ]
        if self.__prefabPaths:
            CGF.cacheGameObjects(self.__prefabPaths, False)
        super(_WhiteTigerDynObjects, self).init(dataSection)

    def destroy(self):
        super(_WhiteTigerDynObjects, self).clear()
        del self.__prefabPaths[:]
