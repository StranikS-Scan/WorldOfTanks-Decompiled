# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/tooltip/vehicle_for_choose.py
import typing
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.pub import ViewImpl
from frameworks.wulf import Array
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.awards.tooltips import awards_vehicle_for_choose_tooltip_view_model as a

class VehicleForChooseTooltipContent(ViewImpl):
    __slots__ = ()

    @property
    def viewModel(self):
        return super(VehicleForChooseTooltipContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(VehicleForChooseTooltipContent, self)._initialize(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            vList = Array()
            for vehData in kwargs.get('vehicles', []):
                vR = VehicleInfoModel()
                vR.setIsElite(vehData.get('isElite', False))
                vR.setVehicleName(vehData.get('vehicleName', ''))
                vR.setVehicleType(vehData.get('vehicleType', ''))
                vR.setVehicleLvl(vehData.get('vehicleLvlNum', 1))
                vList.addViewModel(vR)

            tx.setVehiclesList(vList)
