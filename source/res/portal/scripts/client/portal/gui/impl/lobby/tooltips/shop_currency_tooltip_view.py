# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/shop_currency_tooltip_view.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.shop_currency_tooltip_view_model import ShopCurrencyTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class ShopCurrencyTooltipView(ViewImpl):
    __slots__ = ('_isPortalCoinTooltip',)

    def __init__(self, isPortalCoinTooltip=False):
        settings = ViewSettings(R.views.portal.lobby.tooltips.ShopCurrencyTooltipView())
        settings.model = ShopCurrencyTooltipViewModel()
        self._isPortalCoinTooltip = isPortalCoinTooltip
        super(ShopCurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShopCurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ShopCurrencyTooltipView, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            vm.setIsPortalCoinTooltip(self._isPortalCoinTooltip)
