# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_rate_base_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.exchange.currency_tab_model import CurrencyTabModel
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_discount_model import ExchangeRateDiscountModel
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_model import ExchangeRateModel

class ExchangeRateBaseModel(ViewModel):
    __slots__ = ('onClose', 'onExchange', 'onOpenAllDiscountsWindow', 'onSelectedValueUpdated')

    def __init__(self, properties=9, commands=4):
        super(ExchangeRateBaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def exchangeRate(self):
        return self._getViewModel(0)

    @staticmethod
    def getExchangeRateType():
        return ExchangeRateModel

    @property
    def discount(self):
        return self._getViewModel(1)

    @staticmethod
    def getDiscountType():
        return ExchangeRateDiscountModel

    @property
    def balance(self):
        return self._getViewModel(2)

    @staticmethod
    def getBalanceType():
        return CurrencyTabModel

    def getGoldAmountForExchange(self):
        return self._getNumber(3)

    def setGoldAmountForExchange(self, value):
        self._setNumber(3, value)

    def getResourceAmountForExchange(self):
        return self._getNumber(4)

    def setResourceAmountForExchange(self, value):
        self._setNumber(4, value)

    def getMaxResourceAmountForExchange(self):
        return self._getNumber(5)

    def setMaxResourceAmountForExchange(self, value):
        self._setNumber(5, value)

    def getMaxGoldAmountForExchange(self):
        return self._getNumber(6)

    def setMaxGoldAmountForExchange(self, value):
        self._setNumber(6, value)

    def getBackground(self):
        return self._getResource(7)

    def setBackground(self, value):
        self._setResource(7, value)

    def getAmountOfPersonalDiscounts(self):
        return self._getNumber(8)

    def setAmountOfPersonalDiscounts(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(ExchangeRateBaseModel, self)._initialize()
        self._addViewModelProperty('exchangeRate', ExchangeRateModel())
        self._addViewModelProperty('discount', ExchangeRateDiscountModel())
        self._addViewModelProperty('balance', CurrencyTabModel())
        self._addNumberProperty('goldAmountForExchange', 0)
        self._addNumberProperty('resourceAmountForExchange', 0)
        self._addNumberProperty('maxResourceAmountForExchange', 0)
        self._addNumberProperty('maxGoldAmountForExchange', 0)
        self._addResourceProperty('background', R.invalid())
        self._addNumberProperty('amountOfPersonalDiscounts', 0)
        self.onClose = self._addCommand('onClose')
        self.onExchange = self._addCommand('onExchange')
        self.onOpenAllDiscountsWindow = self._addCommand('onOpenAllDiscountsWindow')
        self.onSelectedValueUpdated = self._addCommand('onSelectedValueUpdated')
