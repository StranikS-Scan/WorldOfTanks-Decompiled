# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/lobby/tooltips/multicurrency_tooltip_view.py
from frameworks.wulf import ViewSettings
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tooltips.multicurrency_tooltip_view_model import MulticurrencyTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class MulticurrencyTooltipView(ViewImpl):
    __slots__ = ('__isFullPriceReached', '__resourceType', '__limit', '__maxValue', '__curValue')

    def __init__(self, isFullPriceReached, resourceType, limit, maxValue, curValue):
        settings = ViewSettings(R.views.tech_tree_trade_in.lobby.tooltips.MulticurrencyTooltipView())
        settings.model = MulticurrencyTooltipViewModel()
        self.__isFullPriceReached = isFullPriceReached
        self.__resourceType = resourceType
        self.__limit = limit
        self.__maxValue = maxValue
        self.__curValue = curValue
        super(MulticurrencyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MulticurrencyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setIsFullPriceReached(self.__isFullPriceReached)
            tx.setResourceType(self.__resourceType)
            tx.setLimit(self.__limit)
            tx.setMaxValue(self.__maxValue)
            tx.setCurValue(self.__curValue)
