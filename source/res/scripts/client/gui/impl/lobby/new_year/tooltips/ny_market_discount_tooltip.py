# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_market_discount_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_market_discount_tooltip_model import NyMarketDiscountTooltipModel
from gui.impl.pub import ViewImpl

class NyMarketDiscountTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMarketDiscountTooltip())
        settings.model = NyMarketDiscountTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyMarketDiscountTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMarketDiscountTooltip, self).getViewModel()

    def _onLoading(self, discount, collection, year, prevNYLevel, currentToys, totalToys):
        with self.viewModel.transaction() as model:
            model.setDiscount(discount)
            model.setCollection(collection)
            model.setYear(year)
            model.setPrevNYLevel(prevNYLevel)
            model.setCurrentToysCount(currentToys)
            model.setTotalToysCount(totalToys)
