# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/fillers_storage.py
from helpers import dependency
from new_year.ny_constants import SyncDataKeys
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from .data_nodes import IAbstractDataNode

class FillersStorage(IAbstractDataNode):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def getFillerCount(self):
        return self._itemsCache.items.festivity.getFillersCount()

    def updateData(self):
        pass

    def _onInit(self):
        self._nyController.onDataUpdated += self.__onDataUpdated

    def _onDestroy(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated

    def __onDataUpdated(self, keys):
        if SyncDataKeys.FILLERS in keys:
            self._raiseOnDataChanged()
