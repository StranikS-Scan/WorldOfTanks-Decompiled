# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_vehicle_tooltip_view.py
from frameworks.wulf import ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_vehicle_tooltip_view_model import FunRandomVehicleTooltipViewModel, FunRandomVehicleStatus
from fun_random.gui.impl.lobby.common.fun_view_helpers import packVehicleParameters, hasVehicleConfig
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import Vehicle
_VEHICLE_STATUS_MAP = {Vehicle.VEHICLE_STATE.UNDAMAGED: FunRandomVehicleStatus.READY,
 Vehicle.VEHICLE_STATE.BATTLE: FunRandomVehicleStatus.IN_BATTLE}

class FunRandomVehicleTooltipView(ViewImpl):
    __slots__ = ('__vehicle',)

    def __init__(self, intCD, context):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.tooltips.FunRandomVehicleTooltipView(), model=FunRandomVehicleTooltipViewModel())
        self.__vehicle = context.buildItem(intCD)
        super(FunRandomVehicleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomVehicleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(FunRandomVehicleTooltipView, self)._onLoading(*args, **kwargs)
        self.__invalidateAll(self.__vehicle.name)

    def _finalize(self):
        self.__vehicle = None
        super(FunRandomVehicleTooltipView, self)._finalize()
        return

    @hasVehicleConfig()
    def __invalidateAll(self, vehicleName, config=None):
        with self.viewModel.transaction() as model:
            vehicleConfig = config.vehicles[vehicleName]
            model.setVehicleName(self.__vehicle.userName)
            model.setDescription(vehicleConfig.description)
            model.setNationName(self.__vehicle.nationName)
            state, _ = self.__vehicle.getState()
            model.setStatus(_VEHICLE_STATUS_MAP.get(state, FunRandomVehicleStatus.NOT_READY))
            packVehicleParameters(model.parameters, config.parameters, vehicleConfig)
