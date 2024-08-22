# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_rate_all_personal_discounts_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.exchange.discount_presentation import DiscountPresentation
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_model import ExchangeRateModel

class CurrencyType(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    FREEXP = 'freeXP'


class ExchangeRateAllPersonalDiscountsModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=6, commands=1):
        super(ExchangeRateAllPersonalDiscountsModel, self).__init__(properties=properties, commands=commands)

    @property
    def defaultExchangeRate(self):
        return self._getViewModel(0)

    @staticmethod
    def getDefaultExchangeRateType():
        return ExchangeRateModel

    @property
    def commonExchangeRate(self):
        return self._getViewModel(1)

    @staticmethod
    def getCommonExchangeRateType():
        return ExchangeRateModel

    def getCurrencyTypeFrom(self):
        return CurrencyType(self._getString(2))

    def setCurrencyTypeFrom(self, value):
        self._setString(2, value.value)

    def getCurrencyTypeTo(self):
        return CurrencyType(self._getString(3))

    def setCurrencyTypeTo(self, value):
        self._setString(3, value.value)

    def getAllDiscountsLimitsAmount(self):
        return self._getNumber(4)

    def setAllDiscountsLimitsAmount(self, value):
        self._setNumber(4, value)

    def getDiscounts(self):
        return self._getArray(5)

    def setDiscounts(self, value):
        self._setArray(5, value)

    @staticmethod
    def getDiscountsType():
        return DiscountPresentation

    def _initialize(self):
        super(ExchangeRateAllPersonalDiscountsModel, self)._initialize()
        self._addViewModelProperty('defaultExchangeRate', ExchangeRateModel())
        self._addViewModelProperty('commonExchangeRate', ExchangeRateModel())
        self._addStringProperty('currencyTypeFrom', CurrencyType.GOLD.value)
        self._addStringProperty('currencyTypeTo', CurrencyType.CREDITS.value)
        self._addNumberProperty('allDiscountsLimitsAmount', 0)
        self._addArrayProperty('discounts', Array())
        self.onClose = self._addCommand('onClose')
