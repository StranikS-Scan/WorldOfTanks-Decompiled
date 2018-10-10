# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/__init__.py
from gui.goodies.goodies_cache import GoodiesCache
from skeletons.gui.goodies import IGoodiesCache
__all__ = ('getGoodiesCacheConfig',)

def getGoodiesCacheConfig(manager):
    cache = GoodiesCache()
    cache.init()
    manager.addInstance(IGoodiesCache, cache, finalizer='fini')
