# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/main_prize_discount_tooltip_view_model.py
from frameworks.wulf import ViewModel

class MainPrizeDiscountTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MainPrizeDiscountTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getOldPrice(self):
        return self._getNumber(0)

    def setOldPrice(self, value):
        self._setNumber(0, value)

    def getCurrentPrice(self):
        return self._getNumber(1)

    def setCurrentPrice(self, value):
        self._setNumber(1, value)

    def getDiscount(self):
        return self._getNumber(2)

    def setDiscount(self, value):
        self._setNumber(2, value)

    def getActiveDiscount(self):
        return self._getNumber(3)

    def setActiveDiscount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(MainPrizeDiscountTooltipViewModel, self)._initialize()
        self._addNumberProperty('oldPrice', 0)
        self._addNumberProperty('currentPrice', 0)
        self._addNumberProperty('discount', 0)
        self._addNumberProperty('activeDiscount', 0)
