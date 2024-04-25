# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/simple_price_view_model.py
from frameworks.wulf import ViewModel

class SimplePriceViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SimplePriceViewModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getDiscount(self):
        return self._getNumber(1)

    def setDiscount(self, value):
        self._setNumber(1, value)

    def getOldValue(self):
        return self._getNumber(2)

    def setOldValue(self, value):
        self._setNumber(2, value)

    def getIsEnough(self):
        return self._getBool(3)

    def setIsEnough(self, value):
        self._setBool(3, value)

    def getIsDiscount(self):
        return self._getBool(4)

    def setIsDiscount(self, value):
        self._setBool(4, value)

    def getValue(self):
        return self._getNumber(5)

    def setValue(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SimplePriceViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('discount', 0)
        self._addNumberProperty('oldValue', 0)
        self._addBoolProperty('isEnough', False)
        self._addBoolProperty('isDiscount', False)
        self._addNumberProperty('value', 0)
