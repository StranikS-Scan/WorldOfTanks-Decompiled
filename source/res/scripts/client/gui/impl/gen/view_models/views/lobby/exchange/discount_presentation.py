# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/discount_presentation.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.exchange.exchange_rate_model import ExchangeRateModel

class DiscountPresentation(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DiscountPresentation, self).__init__(properties=properties, commands=commands)

    @property
    def exchangeRate(self):
        return self._getViewModel(0)

    @staticmethod
    def getExchangeRateType():
        return ExchangeRateModel

    def getSelectedAmountOfDiscount(self):
        return self._getNumber(1)

    def setSelectedAmountOfDiscount(self, value):
        self._setNumber(1, value)

    def getWholeAmountOfDiscount(self):
        return self._getNumber(2)

    def setWholeAmountOfDiscount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(DiscountPresentation, self)._initialize()
        self._addViewModelProperty('exchangeRate', ExchangeRateModel())
        self._addNumberProperty('selectedAmountOfDiscount', 0)
        self._addNumberProperty('wholeAmountOfDiscount', 0)
