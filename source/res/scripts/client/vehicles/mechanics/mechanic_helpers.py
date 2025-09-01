# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_helpers.py
import typing
import BigWorld
from vehicles.mechanics.mechanic_constants import VEHICLE_MECHANIC_DYN_COMPONENT_NAMES as _DYN_COMPONENTS_NAMES, VEHICLE_MECHANIC_TO_PARAMS
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
    from Vehicle import Vehicle
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

def getVehicleMechanic(mechanic, vehicle):
    return vehicle.dynamicComponents.get(_DYN_COMPONENTS_NAMES[mechanic], None) if vehicle is not None else None


def getPlayerVehicleMechanic(mechanic):
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get(_DYN_COMPONENTS_NAMES[mechanic], None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


def getVehicleMechanicParams(mechanic, descr):
    return descr.mechanicsParams.get(VEHICLE_MECHANIC_TO_PARAMS[mechanic])
