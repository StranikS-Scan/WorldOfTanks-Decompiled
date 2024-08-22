# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/container_views/base/context.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ContextBase(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        raise NotImplementedError


class TankmanContext(ContextBase):
    __slots__ = ('_tankmanID', '_tankman', '_tankmanCurrentVehicle', '_tankmanNativeVehicle')

    def __init__(self, tankmanID, *args, **kwargs):
        self._tankmanID = None
        self._tankman = None
        super(TankmanContext, self).__init__(tankmanID)
        return

    @property
    def tankmanID(self):
        return self._tankmanID

    @property
    def tankman(self):
        return self._tankman

    def update(self, tankmanID):
        self._tankmanID = tankmanID
        self._tankman = self.itemsCache.items.getTankman(self._tankmanID)
