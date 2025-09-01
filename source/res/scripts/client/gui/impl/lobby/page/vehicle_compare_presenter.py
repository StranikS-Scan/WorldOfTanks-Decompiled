# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/vehicle_compare_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.page.footer.vehicle_compare_model import VehicleCompareModel
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket

class VehicleComparePresenter(ViewComponent[VehicleCompareModel]):
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self):
        super(VehicleComparePresenter, self).__init__(model=VehicleCompareModel)

    def _getEvents(self):
        return ((self.__comparisonBasket.onChange, self.__onCountChanged), (self.__comparisonBasket.onSwitchChange, self.__updateIsEnabled))

    def _onLoading(self, *args, **kwargs):
        super(VehicleComparePresenter, self)._onLoading(*args, **kwargs)
        self.__updateVehicleCount()
        self.__updateIsEnabled()

    def __onCountChanged(self, _):
        self.__updateVehicleCount()

    def __updateIsEnabled(self):
        self.getViewModel().setIsEnabled(self.__comparisonBasket.isEnabled())

    def __updateVehicleCount(self):
        self.getViewModel().setVehicleCount(self.__comparisonBasket.getVehiclesCount())
