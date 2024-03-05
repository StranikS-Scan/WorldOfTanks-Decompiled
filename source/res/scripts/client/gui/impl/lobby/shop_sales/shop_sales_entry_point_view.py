# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/shop_sales/shop_sales_entry_point_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.shop_sales.shop_sales_entry_point_view_model import ShopSalesEntryPointViewModel
from skeletons.gui.game_control import IShopSalesEventController
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from gui.impl.gen import R
_logger = logging.getLogger(__name__)

class ShopSalesEntryPointView(ViewImpl):
    __shopSales = dependency.descriptor(IShopSalesEventController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.shop_sales.ShopSalesEntryPointView())
        settings.flags = flags
        settings.model = ShopSalesEntryPointViewModel()
        super(ShopSalesEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShopSalesEntryPointView, self).getViewModel()

    def _getEvents(self):
        return ((self.__shopSales.onSettingsChanged, self.__updateViewModel), (self.__shopSales.onPhaseChanged, self.__updateViewModel), (self.viewModel.onActionClick, self.__openShopSales))

    def _onLoading(self, *args, **kwargs):
        super(ShopSalesEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __openShopSales(self):
        self.__shopSales.openMainView()

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setStartDate(self.__shopSales.activePhaseStartTime)
            tx.setEndDate(self.__shopSales.activePhaseFinishTime)
            tx.setTimestamp(getServerUTCTime())
