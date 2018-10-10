# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/data_providers.py
from abc import abstractmethod
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider

class BaseRallyListDataProvider(SortableDAAPIDataProvider):

    def __init__(self):
        super(BaseRallyListDataProvider, self).__init__()
        self.clear()
        self._selectedIdx = -1
        self.__selectedRallyIndex = -1

    @property
    def selectedRallyIndex(self):
        return self.__selectedRallyIndex

    @selectedRallyIndex.setter
    def selectedRallyIndex(self, index):
        self.__selectedRallyIndex = index

    @abstractmethod
    def getVO(self, unitIndex=None):
        return None

    @abstractmethod
    def updateList(self, selectedID, result):
        return self._selectedIdx

    def fini(self):
        self.clear()
        self.destroy()

    def clear(self):
        self.__list = []
        self.__mapping = {}

    def updateItems(self, diff):
        self.flashObject.update(diff)

    @property
    def collection(self):
        return self.__list

    @property
    def mapping(self):
        return self.__mapping

    def requestUpdatedItemsHandler(self, indexes):
        return [ item for item in enumerate(self.__list) if item[0] in indexes ]

    def emptyItem(self):
        return None

    def getItem(self, index):
        return self.__list[index] if 0 <= index < len(self.__list) else None

    def getRally(self, index):
        cfdUnitID = 0
        if index >= 0:
            try:
                cfdUnitID = self.__list[index]['cfdUnitID']
                self.__selectedRallyIndex = index
            except IndexError:
                self.__selectedRallyIndex = -1
                LOG_ERROR('Item not found', index)

        if cfdUnitID:
            vo = self.getVO(cfdUnitID)
        else:
            vo = None
        return (cfdUnitID, vo)

    def rebuildList(self, selectedID, result):
        self._selectedIdx = self.buildList(selectedID, result)
        self.refresh()
        return self._selectedIdx

    def rebuildIndexes(self):
        self.__mapping = dict(((item[1]['cfdUnitID'], item[0]) for item in enumerate(self.__list)))
