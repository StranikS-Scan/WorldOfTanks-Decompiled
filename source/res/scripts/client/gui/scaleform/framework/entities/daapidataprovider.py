# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DAAPIDataProvider.py
from abc import ABCMeta, abstractmethod, abstractproperty
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule
from gui.shared.utils import sortByFields

class DAAPIDataProvider(BaseDAAPIModule):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(DAAPIDataProvider, self).__init__()
        self._itemWrapper = lambda x: x

    def _dispose(self):
        super(DAAPIDataProvider, self)._dispose()
        self.clearItemWrapper()

    @abstractproperty
    def collection(self):
        pass

    @abstractmethod
    def buildList(self, *args):
        pass

    @abstractmethod
    def emptyItem(self):
        pass

    def setItemWrapper(self, wrapper):
        self._itemWrapper = wrapper

    def clearItemWrapper(self):
        self._itemWrapper = lambda x: x

    def lengthHandler(self):
        return self.pyLength()

    def requestItemAtHandler(self, idx):
        return self.pyRequestItemAt(idx)

    def requestItemRangeHandler(self, startIndex, endIndex):
        return self.pyRequestItemRange(startIndex, endIndex)

    def refresh(self):
        self.flashObject.invalidate(self.pyLength())

    def pyLength(self):
        return len(self.collection)

    def pyRequestItemAt(self, idx):
        if -1 < idx < self.pyLength():
            return self._itemWrapper(self.collection[int(idx)])
        else:
            return None

    def pyRequestItemRange(self, startIndex, endIndex):
        return map(self._itemWrapper, self.collection[int(startIndex):int(endIndex) + 1])


class SortableDAAPIDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(SortableDAAPIDataProvider, self).__init__()
        self._sort = ()

    @property
    def sortedCollection(self):
        return sortByFields(self._sort, self.collection)

    def sortOnHandler(self, fieldName, options):
        return self.pySortOn(fieldName, options)

    def getSelectedIdxHandler(self):
        return self.pyGetSelectedIdx()

    def pyRequestItemAt(self, idx):
        if -1 < idx < self.pyLength():
            return self._itemWrapper(self.sortedCollection[int(idx)])
        else:
            return None

    def pyRequestItemRange(self, startIndex, endIndex):
        return map(self._itemWrapper, self.sortedCollection[int(startIndex):int(endIndex) + 1])

    def pySortOn(self, fields, order):
        self._sort = tuple(zip(fields, order))

    def pyGetSelectedIdx(self):
        return -1
