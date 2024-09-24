# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_composition.py
import typing
import enum
import Compound
import GenericComponents
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames
from helpers import isPlayerAccount
import CGF
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
    from SimulatedVehicle import SimulatedVehicle

class VehicleSlots(enum.Enum):
    CHASSIS = TankPartNames.CHASSIS
    HULL = TankPartNames.HULL
    TURRET = TankPartNames.TURRET
    GUN = TankPartNames.GUN
    GUN_INCLINATION = TankNodeNames.GUN_INCLINATION
    GUN_FIRE = 'HP_gunFire'


def removeComposition(gameObject):
    gameObject.removeComponentByType(Compound.CompoundBasedComposerComponent)


def createVehicleComposition(gameObject, prefabMap=None, followNodes=True):

    def predicate(_, nodeName):
        return nodeName.startswith('HP_')

    gameObject.createComponent(Compound.CompoundBasedComposerComponent, predicate, _VEHICLE_SLOTS_MAP, prefabMap or [], followNodes)


def createDetachedTurretComposition(gameObject, prefabMap=None):
    gameObject.createComponent(Compound.CompoundBasedComposerComponent, lambda *args: True, _DETACHED_TURRET_SLOTS_MAP, prefabMap or [], False)


def findParentVehicle(gameObject):
    from Vehicle import Vehicle
    from SimulatedVehicle import SimulatedVehicle
    from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, GenericComponents.EntityGOSync)
    if findResult is not None and len(findResult) > 1:
        entity = findResult[1].entity
        if entity is None:
            return
        if isPlayerAccount():
            if isinstance(entity, ClientSelectableCameraVehicle):
                return entity
        elif isinstance(entity, (Vehicle, SimulatedVehicle)):
            return entity
    return


_VEHICLE_SLOTS_MAP = {TankNodeNames.HULL_SWINGING: VehicleSlots.HULL.value,
 TankPartNames.GUN: VehicleSlots.GUN.value,
 TankPartNames.TURRET: VehicleSlots.TURRET.value,
 TankPartNames.CHASSIS: VehicleSlots.CHASSIS.value,
 VehicleSlots.GUN_FIRE.value: VehicleSlots.GUN_FIRE.value,
 VehicleSlots.GUN_INCLINATION.value: VehicleSlots.GUN_INCLINATION.value}
_DETACHED_TURRET_SLOTS_MAP = {TankNodeNames.GUN_JOINT: VehicleSlots.GUN.value,
 TankPartNames.TURRET: VehicleSlots.TURRET.value}
