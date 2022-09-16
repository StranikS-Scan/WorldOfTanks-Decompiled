# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/__init__.py
from gui.goodies.booster_state_provider import BoosterStateProvider
from gui.goodies.storage_novelty import StorageNovelty
from gui.goodies.goodies_cache import GoodiesCache
from skeletons.gui.storage_novelty import IStorageNovelty
from skeletons.gui.goodies import IGoodiesCache, IBoostersStateProvider
from helpers.dependency import DependencyManager
__all__ = ('getGoodiesCacheConfig', 'getStorageNoveltyConfig')

def getGoodiesCacheConfig(manager):
    cache = GoodiesCache()
    cache.init()
    provider = BoosterStateProvider()
    manager.addInstance(IGoodiesCache, cache, finalizer='fini')
    manager.addInstance(IBoostersStateProvider, provider, finalizer='fini')


def getStorageNoveltyConfig(manager):

    def _create():
        instance = StorageNovelty()
        instance.init()
        return instance

    manager.addRuntime(IStorageNovelty, _create, finalizer='fini')
