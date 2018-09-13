# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/data_providers.py
from abc import abstractmethod
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
__author__ = 'd_dichkovsky'

class BaseRallyListDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(BaseRallyListDataProvider, self).__init__()
        self.clear()
        self._selectedIdx = -1

    @abstractmethod
    def getVO(self, unitIndex = None):
        return None

    @abstractmethod
    def updateList(self, selectedID, result):
        return self._selectedIdx

    def fini(self):
        self.clear()
        self._dispose()

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
        return filter(lambda item: item[0] in indexes, enumerate(self.__list))

    def emptyItem(self):
        return None

    def getRally(self, index):
        cfdUnitID = 0
        if index >= 0:
            try:
                cfdUnitID = self.__list[index]['cfdUnitID']
            except IndexError:
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
        self.__mapping = dict(map(lambda item: (item[1]['cfdUnitID'], item[0]), enumerate(self.__list)))
