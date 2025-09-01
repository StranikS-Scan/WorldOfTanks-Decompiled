# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_info.py
import typing
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VEHICLE_MECHANIC_TAGS, VEHICLE_MECHANIC_TO_PARAMS, TRACKABLE_VEHICLE_MECHANICS
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescr

def hasVehicleMechanic(vehicleDescriptor, mechanic):
    if mechanic in VEHICLE_MECHANIC_TO_PARAMS:
        return VEHICLE_MECHANIC_TO_PARAMS[mechanic] in vehicleDescriptor.mechanicsParams
    return vehicleDescriptor.hasTag(VEHICLE_MECHANIC_TAGS[mechanic]) if mechanic in VEHICLE_MECHANIC_TAGS else False


def getVehicleMechanics(vehicleDescriptor):
    return tuple((mechanic for mechanic in TRACKABLE_VEHICLE_MECHANICS if hasVehicleMechanic(vehicleDescriptor, mechanic)))
