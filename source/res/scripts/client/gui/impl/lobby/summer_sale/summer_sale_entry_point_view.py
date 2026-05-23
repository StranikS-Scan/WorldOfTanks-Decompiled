# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/summer_sale_entry_point_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.server_events.events_dispatcher import showMissionsTemporary
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.summer_sale.summer_sale_entry_point_view_model import SummerSaleEntryPointViewModel, StatusEnum
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from skeletons.gui.game_control import ISummerSaleController
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(summerSale=ISummerSaleController)
def isSummerSaleEntryPointAvailable(summerSale=None):
    return summerSale.isEnabled()


class SummerSaleEntryPointView(ViewImpl):
    __summerSaleController = dependency.descriptor(ISummerSaleController)
    __slots__ = ('__isSingle',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.summer_sale.SummerSaleEntryPointView())
        settings.flags = ViewFlags.VIEW
        settings.model = SummerSaleEntryPointViewModel()
        super(SummerSaleEntryPointView, self).__init__(settings)
        self.__isSingle = True

    @property
    def viewModel(self):
        return super(SummerSaleEntryPointView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SummerSaleEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.viewModel.toSummerSaleEvent, self.__onClick),)

    def __onClick(self):
        showMissionsTemporary()

    def __getStatus(self):
        if self.__summerSaleController.isEnding():
            return StatusEnum.ENDING
        return StatusEnum.ACTIVE if self.__summerSaleController.isEnabled() else StatusEnum.DISABLE

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setIsAloneBanner(self.__isSingle)
            tx.setTimer(self.__summerSaleController.getLocalEndDate())
            tx.setStatus(self.__getStatus())
