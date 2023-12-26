# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_market_discount_tooltip_model.py
from frameworks.wulf import ViewModel

class NyMarketDiscountTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NyMarketDiscountTooltipModel, self).__init__(properties=properties, commands=commands)

    def getDiscount(self):
        return self._getNumber(0)

    def setDiscount(self, value):
        self._setNumber(0, value)

    def getCollection(self):
        return self._getString(1)

    def setCollection(self, value):
        self._setString(1, value)

    def getYear(self):
        return self._getString(2)

    def setYear(self, value):
        self._setString(2, value)

    def getPrevNYLevel(self):
        return self._getNumber(3)

    def setPrevNYLevel(self, value):
        self._setNumber(3, value)

    def getCurrentToysCount(self):
        return self._getNumber(4)

    def setCurrentToysCount(self, value):
        self._setNumber(4, value)

    def getTotalToysCount(self):
        return self._getNumber(5)

    def setTotalToysCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(NyMarketDiscountTooltipModel, self)._initialize()
        self._addNumberProperty('discount', 0)
        self._addStringProperty('collection', '')
        self._addStringProperty('year', '')
        self._addNumberProperty('prevNYLevel', 0)
        self._addNumberProperty('currentToysCount', 0)
        self._addNumberProperty('totalToysCount', 0)
