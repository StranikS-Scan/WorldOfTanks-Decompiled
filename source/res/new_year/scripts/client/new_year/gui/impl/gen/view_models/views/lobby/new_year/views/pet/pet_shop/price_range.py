# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/pet_shop/price_range.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class PriceRange(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PriceRange, self).__init__(properties=properties, commands=commands)

    def getRange(self):
        return self._getArray(0)

    def setRange(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRangeType():
        return int

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getIsDynamic(self):
        return self._getBool(2)

    def setIsDynamic(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PriceRange, self)._initialize()
        self._addArrayProperty('range', Array())
        self._addNumberProperty('price', 0)
        self._addBoolProperty('isDynamic', False)
