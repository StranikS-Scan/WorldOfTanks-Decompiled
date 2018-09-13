# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DAAPIDataProvider.py
from abc import ABCMeta, abstractmethod, abstractproperty
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class DAAPIDataProvider(DAAPIModule):
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
