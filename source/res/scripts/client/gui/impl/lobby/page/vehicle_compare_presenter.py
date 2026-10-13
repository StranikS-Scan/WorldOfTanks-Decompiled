# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/vehicle_compare_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.page.footer.vehicle_compare_model import VehicleCompareModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

class VehicleComparePresenter(ViewComponent[VehicleCompareModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self):
        super(VehicleComparePresenter, self).__init__(model=VehicleCompareModel)

    def _getEvents(self):
        return ((self.__comparisonBasket.onChange, self.__onCountChanged), (self.__comparisonBasket.onSwitchChange, self.__updateIsEnabled))

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleComparePresenter, self)._onLoading(*args, **kwargs)
        self.__updateVehicles()
        self.__updateIsEnabled()

    def __onCountChanged(self, _):
        self.__updateVehicles()

    def __updateIsEnabled(self):
        self.getViewModel().setIsEnabled(self.__comparisonBasket.isEnabled())

    def __updateVehicles(self):
        with self.viewModel.transaction() as tx:
            vehicleCDs = self.__comparisonBasket.getVehiclesCDs()
            vehiclesModel = tx.getVehicles()
            vehiclesModel.clear()
            vehiclesModel.reserve(len(vehicleCDs))
            for vehicleCD in vehicleCDs:
                vehicleModel = VehicleModel()
                fillVehicleModel(vehicleModel, self.__itemsCache.items.getItemByCD(vehicleCD))
                vehiclesModel.addViewModel(vehicleModel)

            vehiclesModel.invalidate()
