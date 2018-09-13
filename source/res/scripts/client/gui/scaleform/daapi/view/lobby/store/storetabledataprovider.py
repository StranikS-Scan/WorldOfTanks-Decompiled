# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/StoreTableDataProvider.py
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider

class StoreTableDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(StoreTableDataProvider, self).__init__()
        self.__list = []

    @property
    def collection(self):
        return self.__list

    def buildList(self, dpList):
        self.__list = dpList

    def emptyItem(self):
        return None

    def clearList(self):
        while len(self.__list):
            self.__list.pop()

        self.__list = None
        return
