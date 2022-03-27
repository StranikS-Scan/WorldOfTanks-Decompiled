# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/vehicle_specs/rts_roster_vehicle_specs.py
from gui.shared.gui_items.Vehicle import Vehicle
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_vehicle_specs_view_model import RosterVehicleSpecsViewModel
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_parameters import RtsVehicleParameters
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_builder import RtsVehicleBuilder
from gui.impl.lobby.rts.vehicle_specs.rts_roster_vehicle import g_rtsRosterVehicle
from gui.impl.lobby.rts.vehicle_specs.rts_vehicle_equipment import updateVehicleEquipment

class RosterVehicleSpecs(object):

    def __init__(self, model):
        self._model = model
        self._vehicleParameters = RtsVehicleParameters(self._model.parameters)

    def vehicleSelected(self, vehicleIntCd):
        vehicle = self._createVehicle(vehicleIntCd)
        g_rtsRosterVehicle.setVehicle(vehicle)
        self._vehicleParameters.setVehicle(vehicle, forceUpdate=True)
        if vehicle and not vehicle.isSupply:
            updateVehicleEquipment(self._model, vehicle)

    def _createVehicle(self, vehicleIntCd):
        return RtsVehicleBuilder().createVehicle(vehicleIntCd)
