# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/main_prize_discount_tooltip_view_model.py
from frameworks.wulf import ViewModel

class MainPrizeDiscountTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(MainPrizeDiscountTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getMaxAmount(self):
        return self._getNumber(0)

    def setMaxAmount(self, value):
        self._setNumber(0, value)

    def getCurrentAmount(self):
        return self._getNumber(1)

    def setCurrentAmount(self, value):
        self._setNumber(1, value)

    def getDiscount(self):
        return self._getNumber(2)

    def setDiscount(self, value):
        self._setNumber(2, value)

    def getCurrentCost(self):
        return self._getNumber(3)

    def setCurrentCost(self, value):
        self._setNumber(3, value)

    def getTotalCost(self):
        return self._getNumber(4)

    def setTotalCost(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(MainPrizeDiscountTooltipViewModel, self)._initialize()
        self._addNumberProperty('maxAmount', 0)
        self._addNumberProperty('currentAmount', 0)
        self._addNumberProperty('discount', 0)
        self._addNumberProperty('currentCost', 0)
        self._addNumberProperty('totalCost', 0)
