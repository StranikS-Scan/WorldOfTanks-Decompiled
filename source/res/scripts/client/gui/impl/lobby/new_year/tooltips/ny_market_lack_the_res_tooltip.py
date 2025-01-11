# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_market_lack_the_res_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_market_lack_the_res_tooltip_model import NyMarketLackTheResTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import INewYearController

class NyMarketLackTheResTooltip(ViewImpl):
    __slots__ = ()
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMarketLackTheResTooltip())
        settings.model = NyMarketLackTheResTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyMarketLackTheResTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMarketLackTheResTooltip, self).getViewModel()

    def _onLoading(self, resourceType, price):
        currentAmountOfCertainResourceType = self.__nyController.currencies.getResouceBalance(resourceType)
        with self.viewModel.transaction() as model:
            model.setResourceType(resourceType)
            model.setShortageValue(price - currentAmountOfCertainResourceType)
