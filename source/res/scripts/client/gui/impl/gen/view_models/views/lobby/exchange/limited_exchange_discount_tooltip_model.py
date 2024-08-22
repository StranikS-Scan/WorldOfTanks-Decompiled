# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/limited_exchange_discount_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.exchange.discount_presentation import DiscountPresentation
from gui.impl.gen.view_models.views.lobby.exchange.exchange_discount_tooltip_model import ExchangeDiscountTooltipModel

class LimitedExchangeDiscountTooltipModel(ExchangeDiscountTooltipModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(LimitedExchangeDiscountTooltipModel, self).__init__(properties=properties, commands=commands)

    def getDiscounts(self):
        return self._getArray(6)

    def setDiscounts(self, value):
        self._setArray(6, value)

    @staticmethod
    def getDiscountsType():
        return DiscountPresentation

    def getAllDiscountsLimitsAmount(self):
        return self._getNumber(7)

    def setAllDiscountsLimitsAmount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(LimitedExchangeDiscountTooltipModel, self)._initialize()
        self._addArrayProperty('discounts', Array())
        self._addNumberProperty('allDiscountsLimitsAmount', 0)
