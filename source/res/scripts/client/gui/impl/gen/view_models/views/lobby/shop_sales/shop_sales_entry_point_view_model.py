# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/shop_sales/shop_sales_entry_point_view_model.py
from frameworks.wulf import ViewModel

class ShopSalesEntryPointViewModel(ViewModel):
    __slots__ = ('onActionClick',)

    def __init__(self, properties=3, commands=1):
        super(ShopSalesEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getTimestamp(self):
        return self._getNumber(2)

    def setTimestamp(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ShopSalesEntryPointViewModel, self)._initialize()
        self._addNumberProperty('startDate', -1)
        self._addNumberProperty('endDate', -1)
        self._addNumberProperty('timestamp', -1)
        self.onActionClick = self._addCommand('onActionClick')
