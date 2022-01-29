# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/tooltips/buy_loot_box_tooltip_model.py
from frameworks.wulf import ViewModel

class BuyLootBoxTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BuyLootBoxTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAmountLeft(self):
        return self._getNumber(0)

    def setAmountLeft(self, value):
        self._setNumber(0, value)

    def getAmountMax(self):
        return self._getNumber(1)

    def setAmountMax(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BuyLootBoxTooltipModel, self)._initialize()
        self._addNumberProperty('amountLeft', 0)
        self._addNumberProperty('amountMax', 10)
