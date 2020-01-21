# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/__init__.py
from gui.goodies.demount_kit import DemountKitNovelty
from gui.goodies.goodies_cache import GoodiesCache
from skeletons.gui.demount_kit import IDemountKitNovelty
from skeletons.gui.goodies import IGoodiesCache
__all__ = ('getGoodiesCacheConfig', 'getDemountKitNoveltyConfig')

def getGoodiesCacheConfig(manager):
    cache = GoodiesCache()
    cache.init()
    manager.addInstance(IGoodiesCache, cache, finalizer='fini')


def getDemountKitNoveltyConfig(manager):

    def _create():
        instance = DemountKitNovelty()
        instance.init()
        return instance

    manager.addRuntime(IDemountKitNovelty, _create, finalizer='fini')
