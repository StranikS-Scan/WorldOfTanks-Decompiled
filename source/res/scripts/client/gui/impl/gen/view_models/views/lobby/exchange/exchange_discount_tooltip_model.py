# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_discount_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_model import ExchangeRateModel

class CurrencyType(Enum):
    CREDITS = 'credits'
    GOLD = 'gold'
    FREEXP = 'freeXP'


class ExchangeDiscountTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ExchangeDiscountTooltipModel, self).__init__(properties=properties, commands=commands)

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

    @property
    def personalExchangeRate(self):
        return self._getViewModel(2)

    @staticmethod
    def getPersonalExchangeRateType():
        return ExchangeRateModel

    def getIsTemporary(self):
        return self._getBool(3)

    def setIsTemporary(self, value):
        self._setBool(3, value)

    def getCurrencyTypeFrom(self):
        return CurrencyType(self._getString(4))

    def setCurrencyTypeFrom(self, value):
        self._setString(4, value.value)

    def getCurrencyTypeTo(self):
        return CurrencyType(self._getString(5))

    def setCurrencyTypeTo(self, value):
        self._setString(5, value.value)

    def _initialize(self):
        super(ExchangeDiscountTooltipModel, self)._initialize()
        self._addViewModelProperty('defaultExchangeRate', ExchangeRateModel())
        self._addViewModelProperty('commonExchangeRate', ExchangeRateModel())
        self._addViewModelProperty('personalExchangeRate', ExchangeRateModel())
        self._addBoolProperty('isTemporary', False)
        self._addStringProperty('currencyTypeFrom', CurrencyType.GOLD.value)
        self._addStringProperty('currencyTypeTo', CurrencyType.CREDITS.value)
