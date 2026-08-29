# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_event_buy_lootboxes_tooltip_view_model.py
from frameworks.wulf import ViewModel

class WtEventBuyLootboxesTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtEventBuyLootboxesTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getAmountLeft(self):
        return self._getNumber(0)

    def setAmountLeft(self, value):
        self._setNumber(0, value)

    def getAmountMax(self):
        return self._getNumber(1)

    def setAmountMax(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WtEventBuyLootboxesTooltipViewModel, self)._initialize()
        self._addNumberProperty('amountLeft', 0)
        self._addNumberProperty('amountMax', 10)
