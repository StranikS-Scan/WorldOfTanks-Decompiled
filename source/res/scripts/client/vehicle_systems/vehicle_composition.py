# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_composition.py
import typing
import enum
import BigWorld
import Compound
import GenericComponents
from constants import IS_UE_EDITOR
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames, TankCollisionPartNames
from vehicle_systems.components.vehicle_appearance_component import VehicleAppearanceComponent
from helpers import isPlayerAccount
import CGF
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
    from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
    from SimulatedVehicle import SimulatedVehicle
    from common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
    TAppearance = typing.Union[HangarVehicleAppearance, CommonTankAppearance, None]

class VehicleSlots(enum.Enum):
    CHASSIS = TankPartNames.CHASSIS
    HULL = TankPartNames.HULL
    TURRET = TankPartNames.TURRET
    GUN_JOINT = TankNodeNames.GUN_JOINT
    GUN = TankPartNames.GUN
    GUN_INCLINATION = TankNodeNames.GUN_INCLINATION
    GUN_FIRE = TankNodeNames.GUN_FIRE
    GUN_RECOIL = TankNodeNames.GUN_RECOIL
    GUN_RECOIL_L = TankNodeNames.GUN_RECOIL_L
    GUN_RECOIL_R = TankNodeNames.GUN_RECOIL_R
    TURRET_COLLISION = TankCollisionPartNames.TURRET
    GUN_COLLISION = TankCollisionPartNames.GUN


def removeComposition(gameObject):
    gameObject.removeComponentByType(Compound.CompoundBasedComposerComponent)


def createVehicleComposition(gameObject, prefabMap=None, followNodes=True):
    if IS_UE_EDITOR:

        def predicate(_, nodeName):
            return nodeName.startswith('HP_') or nodeName.endswith('Collision') or nodeName == TankPartNames.GUN

    else:

        def predicate(_, nodeName):
            return nodeName.startswith('HP_')

    def nodeInteractTypeResolver(_, nodeName):
        return Compound.NodeInteractType.NONE if not followNodes else Compound.NodeInteractType.FOLLOW

    gameObject.createComponent(Compound.CompoundBasedComposerComponent, predicate, nodeInteractTypeResolver, _VEHICLE_SLOTS_MAP, prefabMap or [])


def createDetachedTurretComposition(gameObject, prefabMap=None):
    gameObject.createComponent(Compound.CompoundBasedComposerComponent, lambda *args: True, lambda *args: Compound.NodeInteractType.NONE, _DETACHED_TURRET_SLOTS_MAP, prefabMap or [])


def findParentVehicle(gameObject):
    from Vehicle import Vehicle
    from SimulatedVehicle import SimulatedVehicle
    from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
    from DetachedTurret import DetachedTurret
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, GenericComponents.EntityGOSync)
    if findResult is not None and len(findResult) > 1:
        entity = findResult[1].entity
        if entity is None:
            return
        if isPlayerAccount():
            if isinstance(entity, ClientSelectableCameraVehicle):
                return entity
        else:
            if isinstance(entity, (Vehicle, SimulatedVehicle)):
                return entity
            if isinstance(entity, DetachedTurret):
                return BigWorld.entity(entity.vehicleID)
    return


def findParentVehicleAppearance(gameObject):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, VehicleAppearanceComponent)
    return findResult[1].appearance if findResult is not None and len(findResult) > 1 else None


_VEHICLE_SLOTS_MAP = {TankNodeNames.HULL_SWINGING: VehicleSlots.HULL.value,
 TankPartNames.GUN: VehicleSlots.GUN.value,
 TankPartNames.TURRET: VehicleSlots.TURRET.value,
 TankPartNames.CHASSIS: VehicleSlots.CHASSIS.value,
 TankNodeNames.GUN_FIRE: VehicleSlots.GUN_FIRE.value,
 TankNodeNames.GUN_INCLINATION: VehicleSlots.GUN_INCLINATION.value,
 TankNodeNames.GUN_RECOIL: VehicleSlots.GUN_RECOIL.value,
 TankNodeNames.GUN_RECOIL_L: VehicleSlots.GUN_RECOIL_L.value,
 TankNodeNames.GUN_RECOIL_R: VehicleSlots.GUN_RECOIL_R.value,
 TankNodeNames.GUN_JOINT: VehicleSlots.GUN_JOINT.value,
 TankCollisionPartNames.TURRET: VehicleSlots.TURRET_COLLISION.value,
 TankCollisionPartNames.GUN: VehicleSlots.GUN_COLLISION.value}
_DETACHED_TURRET_SLOTS_MAP = {TankNodeNames.GUN_JOINT: VehicleSlots.GUN_JOINT.value,
 TankPartNames.TURRET: VehicleSlots.TURRET.value}
