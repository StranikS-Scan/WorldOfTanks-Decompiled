# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tooltips/deconstruct_from_vehicle_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.tank_setup.tooltips.deconstruct_from_vehicle_tooltip_model import DeconstructFromVehicleTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class DeconstructFromVehicleTooltip(ViewImpl):
    __slots__ = ('equipmentName', 'vehicleNames')

    def __init__(self, equipmentName, vehicleNames, layoutID=R.views.lobby.tanksetup.tooltips.DeconstructFromVehicleTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = DeconstructFromVehicleTooltipModel()
        self.equipmentName = equipmentName
        self.vehicleNames = vehicleNames
        super(DeconstructFromVehicleTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DeconstructFromVehicleTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(DeconstructFromVehicleTooltip, self)._initialize(*args, **kwargs)
        with self.viewModel.transaction() as model:
            vehicleNames = model.getVehicleNames()
            vehicleNames.clear()
            for vehicle in self.vehicleNames:
                vehicleNames.addString(vehicle)

            vehicleNames.invalidate()
            model.setEquipmentName(self.equipmentName)
