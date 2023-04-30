# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/reserve_stock_model.py
from frameworks.wulf import ViewModel

class ReserveStockModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=10, commands=1):
        super(ReserveStockModel, self).__init__(properties=properties, commands=commands)

    def getIsCreditReserveEnabled(self):
        return self._getBool(0)

    def setIsCreditReserveEnabled(self, value):
        self._setBool(0, value)

    def getIsGoldReserveEnabled(self):
        return self._getBool(1)

    def setIsGoldReserveEnabled(self, value):
        self._setBool(1, value)

    def getCreditCurrentAmount(self):
        return self._getNumber(2)

    def setCreditCurrentAmount(self, value):
        self._setNumber(2, value)

    def getCreditMaxAmount(self):
        return self._getNumber(3)

    def setCreditMaxAmount(self, value):
        self._setNumber(3, value)

    def getGoldCurrentAmount(self):
        return self._getNumber(4)

    def setGoldCurrentAmount(self, value):
        self._setNumber(4, value)

    def getGoldMaxAmount(self):
        return self._getNumber(5)

    def setGoldMaxAmount(self, value):
        self._setNumber(5, value)

    def getOpeningTime(self):
        return self._getNumber(6)

    def setOpeningTime(self, value):
        self._setNumber(6, value)

    def getOpeningSoonThreshold(self):
        return self._getNumber(7)

    def setOpeningSoonThreshold(self, value):
        self._setNumber(7, value)

    def getIsPremiumActive(self):
        return self._getBool(8)

    def setIsPremiumActive(self, value):
        self._setBool(8, value)

    def getIsWotPlusActive(self):
        return self._getBool(9)

    def setIsWotPlusActive(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(ReserveStockModel, self)._initialize()
        self._addBoolProperty('isCreditReserveEnabled', True)
        self._addBoolProperty('isGoldReserveEnabled', True)
        self._addNumberProperty('creditCurrentAmount', 0)
        self._addNumberProperty('creditMaxAmount', 0)
        self._addNumberProperty('goldCurrentAmount', 0)
        self._addNumberProperty('goldMaxAmount', 0)
        self._addNumberProperty('openingTime', 0)
        self._addNumberProperty('openingSoonThreshold', 0)
        self._addBoolProperty('isPremiumActive', False)
        self._addBoolProperty('isWotPlusActive', False)
        self.onClick = self._addCommand('onClick')
