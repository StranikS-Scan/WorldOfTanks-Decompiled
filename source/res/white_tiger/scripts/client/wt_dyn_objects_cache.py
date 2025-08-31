# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/wt_dyn_objects_cache.py
import BigWorld
import CGF
from dyn_objects_cache import DynObjectsBase
from vehicle_systems.stricted_loading import makeCallbackWeak

class WTBattleDynObjects(DynObjectsBase):

    def __init__(self):
        super(WTBattleDynObjects, self).__init__()
        self.__cachedIDs = []
        self.__resourcesCache = None
        return

    def init(self, dataSection):
        if self._initialized:
            return
        self.__cachedIDs = [ value.asString for key, value in dataSection['prefabs'].items() if key == 'path' and value.asString ]
        if self.__cachedIDs:
            BigWorld.loadResourceListBG(self.__cachedIDs, makeCallbackWeak(self.__onResourcesLoaded))
            CGF.cacheGameObjects(self.__cachedIDs, False)
        super(WTBattleDynObjects, self).init(dataSection)

    def __onResourcesLoaded(self, resourceRefs):
        self.__resourcesCache = resourceRefs

    def destroy(self):
        self.__resourcesCache = None
        super(WTBattleDynObjects, self).destroy()
        return

    def clear(self):
        if self.__cachedIDs:
            CGF.clearGameObjectsCache(self.__cachedIDs)
        self.__cachedIDs = []
        super(WTBattleDynObjects, self).clear()

    def getInspiringEffect(self):
        return {}

    def getHealPointEffect(self):
        return {}
