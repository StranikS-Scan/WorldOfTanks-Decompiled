# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_rate_discount_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ShowFormat(Enum):
    FAVORABLE = 'favorable'
    TEMPORARY = 'temporary'
    LIMITED = 'limited'


class ExchangeRateDiscountTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ExchangeRateDiscountTooltipModel, self).__init__(properties=properties, commands=commands)

    def getExchangeRateFrom(self):
        return self._getNumber(0)

    def setExchangeRateFrom(self, value):
        self._setNumber(0, value)

    def getExchangeRateTo(self):
        return self._getNumber(1)

    def setExchangeRateTo(self, value):
        self._setNumber(1, value)

    def getDiscountExchangeRateFrom(self):
        return self._getNumber(2)

    def setDiscountExchangeRateFrom(self, value):
        self._setNumber(2, value)

    def getDiscountExchangeRateTo(self):
        return self._getNumber(3)

    def setDiscountExchangeRateTo(self, value):
        self._setNumber(3, value)

    def getShowFormat(self):
        return ShowFormat(self._getString(4))

    def setShowFormat(self, value):
        self._setString(4, value.value)

    def getSelectedAmountOfExchange(self):
        return self._getNumber(5)

    def setSelectedAmountOfExchange(self, value):
        self._setNumber(5, value)

    def getWholeAmountOfDiscount(self):
        return self._getNumber(6)

    def setWholeAmountOfDiscount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ExchangeRateDiscountTooltipModel, self)._initialize()
        self._addNumberProperty('exchangeRateFrom', 1)
        self._addNumberProperty('exchangeRateTo', 1)
        self._addNumberProperty('discountExchangeRateFrom', 1)
        self._addNumberProperty('discountExchangeRateTo', 1)
        self._addStringProperty('showFormat', ShowFormat.FAVORABLE.value)
        self._addNumberProperty('selectedAmountOfExchange', 0)
        self._addNumberProperty('wholeAmountOfDiscount', 0)
