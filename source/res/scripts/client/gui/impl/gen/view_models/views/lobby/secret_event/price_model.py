# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/price_model.py
from frameworks.wulf import ViewModel

class PriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PriceModel, self).__init__(properties=properties, commands=commands)

    def getCurrencyType(self):
        return self._getString(0)

    def setCurrencyType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def getIsDiscount(self):
        return self._getBool(2)

    def setIsDiscount(self, value):
        self._setBool(2, value)

    def getIsEnough(self):
        return self._getBool(3)

    def setIsEnough(self, value):
        self._setBool(3, value)

    def getDiscountValue(self):
        return self._getNumber(4)

    def setDiscountValue(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(PriceModel, self)._initialize()
        self._addStringProperty('currencyType', '')
        self._addNumberProperty('value', 0)
        self._addBoolProperty('isDiscount', False)
        self._addBoolProperty('isEnough', True)
        self._addNumberProperty('discountValue', 0)
