# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/shards_storage.py
from helpers import dependency
from new_year.ny_constants import SyncDataKeys
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from .data_nodes import IAbstractDataNode

class ShardsStorage(IAbstractDataNode):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def getShardsCount(self):
        return self._itemsCache.items.festivity.getShardsCount()

    def updateData(self):
        pass

    def _onInit(self):
        self._nyController.onDataUpdated += self.__onDataUpdated

    def _onDestroy(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TOY_FRAGMENTS in keys:
            self._raiseOnDataChanged()
