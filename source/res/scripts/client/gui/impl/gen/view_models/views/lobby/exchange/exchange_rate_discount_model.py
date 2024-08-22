# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_rate_discount_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_model import ExchangeRateModel

class DiscountType(Enum):
    LIMITED = 'limited'
    UNLIMITED = 'unlimited'


class ShowFormat(Enum):
    COEFFICIENT = 'coefficient'
    INTEGER = 'integer'
    TEMPORARY = 'temporary'
    LIMITED = 'limited'


class ExchangeRateDiscountModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ExchangeRateDiscountModel, self).__init__(properties=properties, commands=commands)

    @property
    def exchangeRate(self):
        return self._getViewModel(0)

    @staticmethod
    def getExchangeRateType():
        return ExchangeRateModel

    def getIsDiscountAvailable(self):
        return self._getBool(1)

    def setIsDiscountAvailable(self, value):
        self._setBool(1, value)

    def getDiscountType(self):
        return DiscountType(self._getString(2))

    def setDiscountType(self, value):
        self._setString(2, value.value)

    def getShowFormat(self):
        return ShowFormat(self._getString(3))

    def setShowFormat(self, value):
        self._setString(3, value.value)

    def getAmountOfDiscount(self):
        return self._getNumber(4)

    def setAmountOfDiscount(self, value):
        self._setNumber(4, value)

    def getDiscountLifetime(self):
        return self._getNumber(5)

    def setDiscountLifetime(self, value):
        self._setNumber(5, value)

    def getDiscountPercent(self):
        return self._getNumber(6)

    def setDiscountPercent(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ExchangeRateDiscountModel, self)._initialize()
        self._addViewModelProperty('exchangeRate', ExchangeRateModel())
        self._addBoolProperty('isDiscountAvailable', False)
        self._addStringProperty('discountType', DiscountType.LIMITED.value)
        self._addStringProperty('showFormat', ShowFormat.COEFFICIENT.value)
        self._addNumberProperty('amountOfDiscount', 0)
        self._addNumberProperty('discountLifetime', 0)
        self._addNumberProperty('discountPercent', 0)
