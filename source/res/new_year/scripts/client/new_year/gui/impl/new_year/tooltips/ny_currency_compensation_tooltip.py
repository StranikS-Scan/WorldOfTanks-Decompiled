# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/new_year/tooltips/ny_currency_compensation_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen.resources import R
from gui.impl.pub import ViewImpl
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_currency_compensation_tooltip_model import NyCurrencyCompensationTooltipModel

class NYCurrencyCompensationTooltip(ViewImpl):
    __slots__ = ('__amount',)

    def __init__(self, amount):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyCurrencyCompensationTooltip())
        settings.model = NyCurrencyCompensationTooltipModel()
        self.__amount = amount
        super(NYCurrencyCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NYCurrencyCompensationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NYCurrencyCompensationTooltip, self)._onLoading(args, kwargs)
        self.viewModel.setCurrencyAmount(self.__amount)
