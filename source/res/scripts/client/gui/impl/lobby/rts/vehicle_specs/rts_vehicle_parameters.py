# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/vehicle_specs/rts_vehicle_parameters.py
import typing
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.impl.lobby.vehicle_parameters.vehicle_parameters import VehicleParameters
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.impl.gen.view_models.views.lobby.vehicle_parameters.vehicle_parameter_group_view_model import VehicleParameterGroupViewModel
from gui.impl.lobby.rts.vehicle_specs.rts_supply_params import RtsSupplyParams
if typing.TYPE_CHECKING:
    from gui.shared.items_parameters.comparator import _ParameterInfo
    from gui.shared.gui_items.Vehicle import Vehicle

class RtsVehicleParameters(VehicleParameters):

    def getParameterGroups(self):
        return ('supplyParameters',) if self._vehicle and self._vehicle.isSupply else super(RtsVehicleParameters, self).getParameterGroups()

    def getParametersForGroup(self, groupName):
        return RtsSupplyParams.getParametersForSupply(self._vehicle) if self._vehicle and self._vehicle.isSupply else super(RtsVehicleParameters, self).getParametersForGroup(groupName)

    def _createGroup(self, group):
        if self._vehicle and self._vehicle.isSupply:
            groupModel = VehicleParameterGroupViewModel()
            groupModel.setIsExpanded(True)
            return groupModel
        return super(RtsVehicleParameters, self)._createGroup(group)

    def _getComparator(self, vehicle):
        if self._vehicle and self._vehicle.isSupply:
            vehicleParamsObject = RtsSupplyParams(vehicle)
            vehicleParams = vehicleParamsObject.getParamsDict()
            bonuses = vehicleParamsObject.getBonuses(vehicle)
            penalties = vehicleParamsObject.getPenalties(vehicle)
            compatibleArtefacts = g_paramsCache.getCompatibleArtefacts(vehicle)
            return VehiclesComparator(vehicleParams, vehicleParams, compatibleArtefacts, bonuses, penalties)
        return super(RtsVehicleParameters, self)._getComparator(vehicle)
