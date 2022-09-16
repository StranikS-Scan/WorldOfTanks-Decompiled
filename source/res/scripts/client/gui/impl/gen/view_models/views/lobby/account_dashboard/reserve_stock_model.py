# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/reserve_stock_model.py
from frameworks.wulf import ViewModel

class ReserveStockModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(ReserveStockModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getCreditCurrentAmount(self):
        return self._getNumber(1)

    def setCreditCurrentAmount(self, value):
        self._setNumber(1, value)

    def getCreditMaxAmount(self):
        return self._getNumber(2)

    def setCreditMaxAmount(self, value):
        self._setNumber(2, value)

    def getOpeningTime(self):
        return self._getNumber(3)

    def setOpeningTime(self, value):
        self._setNumber(3, value)

    def getOpeningSoonThreshold(self):
        return self._getNumber(4)

    def setOpeningSoonThreshold(self, value):
        self._setNumber(4, value)

    def getIsPremiumActive(self):
        return self._getBool(5)

    def setIsPremiumActive(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ReserveStockModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('creditCurrentAmount', 0)
        self._addNumberProperty('creditMaxAmount', 0)
        self._addNumberProperty('openingTime', 0)
        self._addNumberProperty('openingSoonThreshold', 0)
        self._addBoolProperty('isPremiumActive', False)
        self.onClick = self._addCommand('onClick')
