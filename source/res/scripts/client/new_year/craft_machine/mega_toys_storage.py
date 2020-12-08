# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/mega_toys_storage.py
from helpers import dependency
from new_year.ny_constants import SyncDataKeys
from skeletons.new_year import INewYearController
from .data_nodes import IAbstractDataNode

class MegaToysStorage(IAbstractDataNode):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(MegaToysStorage, self).__init__()
        self.__uniqueMegaToysCount = 0

    def getUniqueMegaToysCount(self):
        return self.__uniqueMegaToysCount

    def updateData(self):
        pass

    def _onInit(self):
        self.__uniqueMegaToysCount = self._nyController.getUniqueMegaToysCount()
        self._nyController.onDataUpdated += self.__onDataUpdated

    def _onDestroy(self):
        self._nyController.onDataUpdated -= self.__onDataUpdated

    def __onDataUpdated(self, keys):
        if SyncDataKeys.INVENTORY_TOYS in keys:
            uniqueMegaToysCount = self._nyController.getUniqueMegaToysCount()
            if uniqueMegaToysCount != self.__uniqueMegaToysCount:
                self.__uniqueMegaToysCount = uniqueMegaToysCount
                self._raiseOnDataChanged()
