# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/shop_currency_tooltip_view_model.py
from frameworks.wulf import ViewModel

class ShopCurrencyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ShopCurrencyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsPortalCoinTooltip(self):
        return self._getBool(0)

    def setIsPortalCoinTooltip(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(ShopCurrencyTooltipViewModel, self)._initialize()
        self._addBoolProperty('isPortalCoinTooltip', False)
