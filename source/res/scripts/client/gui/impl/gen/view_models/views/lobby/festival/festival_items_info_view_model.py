# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_items_info_view_model.py
from frameworks.wulf import ViewModel

class FestivalItemsInfoViewModel(ViewModel):
    __slots__ = ()

    def getReceivedItems(self):
        return self._getNumber(0)

    def setReceivedItems(self, value):
        self._setNumber(0, value)

    def getTotalItems(self):
        return self._getNumber(1)

    def setTotalItems(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(FestivalItemsInfoViewModel, self)._initialize()
        self._addNumberProperty('receivedItems', 0)
        self._addNumberProperty('totalItems', 0)
