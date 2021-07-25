# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/detachment/__init__.py
from gui.detachment.detachment_cache import DetachmentCache
from gui.detachment.detachment_states import DetachmentStates
from skeletons.gui.detachment import IDetachmentCache, IDetachementStates
__all__ = ('getDetachmentCacheConfig', 'IGNORE_SKILLS')

def getDetachmentCacheConfig(manager):
    states = DetachmentStates()
    states.init()
    cache = DetachmentCache()
    cache.init()
    manager.addInstance(IDetachementStates, states, finalizer='fini')
    manager.addInstance(IDetachmentCache, cache, finalizer='fini')


IGNORE_SKILLS = ('commander_sixthSense',)
