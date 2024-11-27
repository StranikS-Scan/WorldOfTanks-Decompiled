# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_currency_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_currency_tooltip_model import NyCurrencyTooltipModel
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider

class NyCurrencyTooltip(ViewImpl):
    __slots__ = ('__currencyProvider',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyCurrencyTooltip())
        settings.model = NyCurrencyTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__currencyProvider = NyCurrencyProvider()
        super(NyCurrencyTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyCurrencyTooltip, self).getViewModel()

    def _onLoading(self, currency, isCurrencyAvailable=True, allowClick=False, *args, **kwargs):
        super(NyCurrencyTooltip, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            model.currency.setValue(currency)
            model.setAmount(self.__currencyProvider.getCurrencyCount(currency))
            model.setIsCurrencyAvailable(isCurrencyAvailable)
            model.setAllowClick(allowClick)
