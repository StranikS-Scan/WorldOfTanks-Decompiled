# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/vehicle_tooltip_view.py
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.vehicle_tooltip_view_model import VehicleTooltipViewModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.tooltips.vehicle import StatusBlockConstructor

class VehicleTooltipView(ViewImpl):

    def __init__(self, intCD, context):
        settings = ViewSettings(R.views.battle_royale.lobby.tooltips.VehicleTooltipView())
        settings.model = VehicleTooltipViewModel()
        self.__context = context
        self.__vehicle = context.buildItem(intCD)
        super(VehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(VehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleTooltipView, self)._onLoading(args, kwargs)
        with self.getViewModel().transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        title = self.__vehicle.userName
        nationName = self.__vehicle.nationName
        model.setVehicleName(title)
        model.setVehicleNation(nationName)
        self.__fillStatus(self.__vehicle, model)

    def __fillStatus(self, vehicle, model):
        statusConfig = self.__context.getStatusConfiguration(vehicle)
        _, __, status = StatusBlockConstructor(vehicle, statusConfig).construct()
        model.setStatusText(status['header'])
        model.setStatusLevel(status['level'])
