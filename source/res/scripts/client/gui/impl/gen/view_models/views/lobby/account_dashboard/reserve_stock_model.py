# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/reserve_stock_model.py
from frameworks.wulf import ViewModel

class ReserveStockModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=11, commands=1):
        super(ReserveStockModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def getIsEnabledGold(self):
        return self._getBool(1)

    def setIsEnabledGold(self, value):
        self._setBool(1, value)

    def getCreditCurrentAmount(self):
        return self._getNumber(2)

    def setCreditCurrentAmount(self, value):
        self._setNumber(2, value)

    def getCreditMaxAmount(self):
        return self._getNumber(3)

    def setCreditMaxAmount(self, value):
        self._setNumber(3, value)

    def getOpeningTime(self):
        return self._getNumber(4)

    def setOpeningTime(self, value):
        self._setNumber(4, value)

    def getOpeningSoonThreshold(self):
        return self._getNumber(5)

    def setOpeningSoonThreshold(self, value):
        self._setNumber(5, value)

    def getIsPremiumActive(self):
        return self._getBool(6)

    def setIsPremiumActive(self, value):
        self._setBool(6, value)

    def getIsSubscriptionActive(self):
        return self._getBool(7)

    def setIsSubscriptionActive(self, value):
        self._setBool(7, value)

    def getIsSubscriptionAvailable(self):
        return self._getBool(8)

    def setIsSubscriptionAvailable(self, value):
        self._setBool(8, value)

    def getGoldCurrentAmount(self):
        return self._getNumber(9)

    def setGoldCurrentAmount(self, value):
        self._setNumber(9, value)

    def getGoldMaxAmount(self):
        return self._getNumber(10)

    def setGoldMaxAmount(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(ReserveStockModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isEnabledGold', False)
        self._addNumberProperty('creditCurrentAmount', 0)
        self._addNumberProperty('creditMaxAmount', 0)
        self._addNumberProperty('openingTime', 0)
        self._addNumberProperty('openingSoonThreshold', 0)
        self._addBoolProperty('isPremiumActive', False)
        self._addBoolProperty('isSubscriptionActive', False)
        self._addBoolProperty('isSubscriptionAvailable', False)
        self._addNumberProperty('goldCurrentAmount', 0)
        self._addNumberProperty('goldMaxAmount', 0)
        self.onClick = self._addCommand('onClick')
