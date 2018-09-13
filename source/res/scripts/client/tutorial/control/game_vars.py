# Embedded file name: scripts/client/tutorial/control/game_vars.py
from CurrentVehicle import g_currentVehicle
from tutorial.data.chapter import VehicleCondition

def _getCvTypeName():
    result = None
    if g_currentVehicle.isPresent():
        result = g_currentVehicle.item.name
    return result


_vehicleVarGetters = {VehicleCondition.CV_TYPE_NAME: _getCvTypeName}

def vehicle(varID):
    getters = _vehicleVarGetters.get(varID)
    result = None
    if getters is not None:
        result = getters()
    return result
