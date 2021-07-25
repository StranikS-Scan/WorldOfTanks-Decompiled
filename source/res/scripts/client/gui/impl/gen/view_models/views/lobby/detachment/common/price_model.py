# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/price_model.py
from frameworks.wulf import ViewModel

class PriceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PriceModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(0)

    def setValue(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getIsEnough(self):
        return self._getBool(2)

    def setIsEnough(self, value):
        self._setBool(2, value)

    def getHasDiscount(self):
        return self._getBool(3)

    def setHasDiscount(self, value):
        self._setBool(3, value)

    def getDiscountValue(self):
        return self._getReal(4)

    def setDiscountValue(self, value):
        self._setReal(4, value)

    def _initialize(self):
        super(PriceModel, self)._initialize()
        self._addNumberProperty('value', 0)
        self._addStringProperty('type', '')
        self._addBoolProperty('isEnough', False)
        self._addBoolProperty('hasDiscount', False)
        self._addRealProperty('discountValue', 0.0)
