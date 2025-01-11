# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_market_card_tooltip_model.py
from frameworks.wulf import ViewModel

class NyMarketCardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NyMarketCardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getKitState(self):
        return self._getString(0)

    def setKitState(self, value):
        self._setString(0, value)

    def getKitName(self):
        return self._getString(1)

    def setKitName(self, value):
        self._setString(1, value)

    def getCurrentTabName(self):
        return self._getString(2)

    def setCurrentTabName(self, value):
        self._setString(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getPriceWithDiscount(self):
        return self._getNumber(4)

    def setPriceWithDiscount(self, value):
        self._setNumber(4, value)

    def getDiscount(self):
        return self._getNumber(5)

    def setDiscount(self, value):
        self._setNumber(5, value)

    def getNotEnoughResource(self):
        return self._getBool(6)

    def setNotEnoughResource(self, value):
        self._setBool(6, value)

    def getPrevNYLevel(self):
        return self._getNumber(7)

    def setPrevNYLevel(self, value):
        self._setNumber(7, value)

    def getCurrentToysCount(self):
        return self._getNumber(8)

    def setCurrentToysCount(self, value):
        self._setNumber(8, value)

    def getTotalToysCount(self):
        return self._getNumber(9)

    def setTotalToysCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(NyMarketCardTooltipModel, self)._initialize()
        self._addStringProperty('kitState', '')
        self._addStringProperty('kitName', '')
        self._addStringProperty('currentTabName', 'ny22')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('priceWithDiscount', 0)
        self._addNumberProperty('discount', 0)
        self._addBoolProperty('notEnoughResource', False)
        self._addNumberProperty('prevNYLevel', 0)
        self._addNumberProperty('currentToysCount', 0)
        self._addNumberProperty('totalToysCount', 0)
