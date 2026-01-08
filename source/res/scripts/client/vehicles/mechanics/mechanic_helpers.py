# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_helpers.py
from __future__ import absolute_import
import typing
from future.utils import viewvalues
import BigWorld
from vehicles.mechanics.common import IMechanicComponentLogic
from vehicles.mechanics.mechanic_constants import VEHICLE_MECHANIC_DYN_COMPONENT_NAMES as _DYN_COMPONENTS_NAMES, VEHICLE_MECHANIC_TO_PARAMS, VEHICLE_MECHANIC_TAGS, TRACKABLE_VEHICLE_DESCR_MECHANICS
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor, VehicleDescr
    from Vehicle import Vehicle
    from vehicles.mechanics.common import IMechanicComponent
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

def isValidMechanicComponent(component):
    return isinstance(component, IMechanicComponentLogic) and component.isValid


def isVehicleMechanicComponent(component, mechanic):
    return isValidMechanicComponent(component) and component.vehicleMechanic is mechanic


def hasVehicleMechanicComponent(vehicle, mechanic):
    return getVehicleMechanicComponent(vehicle, mechanic) is not None


def getVehicleMechanicComponent(vehicle, mechanic):
    return findVehicleMechanicDynamicComponent(vehicle.dynamicComponents, mechanic) if vehicle is not None else None


def getVehicleMechanicsComponents(vehicle, criteria=isValidMechanicComponent):
    return {component.vehicleMechanic:component for component in viewvalues(vehicle.dynamicComponents if vehicle is not None else {}) if criteria(component)}


def getPlayerVehicleMechanicComponent(mechanic):
    vehicle = BigWorld.player().getVehicleAttached()
    return findVehicleMechanicDynamicComponent(vehicle.dynamicComponents, mechanic) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


def findVehicleMechanicDynamicComponent(dynamicComponents, mechanic):
    component = dynamicComponents.get(_DYN_COMPONENTS_NAMES[mechanic])
    return component if isVehicleMechanicComponent(component, mechanic) else None


def hasVehicleDescrMechanic(vehicleDescriptor, mechanic):
    if mechanic in VEHICLE_MECHANIC_TO_PARAMS:
        return VEHICLE_MECHANIC_TO_PARAMS[mechanic] in vehicleDescriptor.mechanicsParams
    return vehicleDescriptor.hasTag(VEHICLE_MECHANIC_TAGS[mechanic]) if mechanic in VEHICLE_MECHANIC_TAGS else False


def getVehicleDescrMechanics(vehicleDescriptor):
    return tuple((mechanic for mechanic in TRACKABLE_VEHICLE_DESCR_MECHANICS if hasVehicleDescrMechanic(vehicleDescriptor, mechanic)))


def getVehicleDescrMechanicParams(vehicleDescriptor, mechanic):
    return vehicleDescriptor.mechanicsParams.get(VEHICLE_MECHANIC_TO_PARAMS[mechanic])
