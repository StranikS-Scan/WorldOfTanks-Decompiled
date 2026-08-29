# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/wt_dyn_objects_cache.py
import BigWorld
import logging
import typing
from dyn_objects_cache import DynObjectsBase
from PrefabsLoading import PrefabDataListLoader
from vehicle_systems.stricted_loading import makeCallbackWeak
if typing.TYPE_CHECKING:
    from PrefabsLoading import PrefabData
_logger = logging.getLogger(__name__)

class WTBattleDynObjects(DynObjectsBase):

    def __init__(self):
        super(WTBattleDynObjects, self).__init__()
        self.__resourcesCache = {}

    def init(self, dataSection):
        if self._initialized:
            return
        self.__cachePrefabs(dataSection)
        super(WTBattleDynObjects, self).init(dataSection)

    def destroy(self):
        self.clear()
        super(WTBattleDynObjects, self).destroy()

    def clear(self):
        self.__resourcesCache = {}
        self.__resourcesCache = None
        self._initialized = False
        super(WTBattleDynObjects, self).clear()
        return

    def __cachePrefabs(self, dataSection):
        prefabsPaths = {value.asString for key, value in dataSection['WtPrefabs'].items() if key == 'path' and value.asString}
        if not prefabsPaths:
            _logger.warning('No valid prefab paths found in WtPrefabs/path entries; skipping preload')
            return
        prefabsLoader = PrefabDataListLoader('WtPrefabs', list(prefabsPaths))
        BigWorld.loadResourceListBG((prefabsLoader,), makeCallbackWeak(self.__onPrefabsLoaded))

    def __onPrefabsLoaded(self, resourceRefs):
        self.__resourcesCache = resourceRefs['WtPrefabs']
        if self.__resourcesCache:
            _logger.info('WtPrefabs loaded successfully: %d items', len(resourceRefs['WtPrefabs']))
