# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/vehicle_composition.py
import typing
import enum
import BigWorld
import Compound
import CGF
import Math
import GenericComponents
import math_utils
from constants import IS_UE_EDITOR
from items.components import component_constants
from items.components.c11n_constants import HANGER_POSTFIX, AttachmentType
from vehicle_systems.tankStructure import TankNodeNames, TankPartNames, TankCollisionPartNames
from vehicle_systems.components.vehicle_appearance_component import VehicleAppearanceComponent
from helpers import isPlayerAccount
from objects_hierarchy import PrefabsMapItem, ExtraSlotsMapItem
if typing.TYPE_CHECKING:
    from CGF import GameObject
    from Vehicle import Vehicle
    from items.vehicles import VehicleDescriptor
    from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
    from SimulatedVehicle import SimulatedVehicle
    from common_tank_appearance import CommonTankAppearance
    from gui.hangar_vehicle_appearance import HangarVehicleAppearance
    from typing import Iterable
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
    gameObject.removeComponent(Compound.CompoundBasedComposerComponent)


def createVehicleComposition(gameObject, vehicleGameObject=CGF.GameObject.INVALID_GAME_OBJECT, prefabMap=None, followNodes=True, extraSlots=None, dynSlotNodes=None):
    dynSlotNodes = dynSlotNodes or {}
    if IS_UE_EDITOR:

        def predicate(_, nodeName):
            return nodeName.startswith('HP_') or nodeName.endswith('Collision') or nodeName == TankPartNames.GUN or nodeName in dynSlotNodes

    else:

        def predicate(_, nodeName):
            return nodeName.startswith('HP_') or nodeName == TankPartNames.GUN or nodeName in dynSlotNodes

    def nodeInteractTypeResolver(_, nodeName):
        return Compound.NodeInteractType.NONE if not followNodes else Compound.NodeInteractType.FOLLOW

    slotsMap = {node:node for node in dynSlotNodes}
    slotsMap.update(_VEHICLE_SLOTS_MAP)
    gameObject.createComponent(Compound.CompoundBasedComposerComponent, vehicleGameObject, predicate, nodeInteractTypeResolver, slotsMap, prefabMap or [], extraSlots or [])


def _getSlotTransform(scale, rotation, position):
    rotationYPR = Math.Vector3(rotation.y, rotation.x, rotation.z)
    return math_utils.createSRTMatrix(scale, rotationYPR, position)


VEHICLE_PART_TO_SLOT = {TankPartNames.CHASSIS: VehicleSlots.CHASSIS.value,
 TankPartNames.HULL: VehicleSlots.HULL.value,
 TankPartNames.TURRET: VehicleSlots.TURRET.value,
 TankPartNames.GUN: VehicleSlots.GUN_INCLINATION.value}
DESTROYED_VEHICLE_PART_TO_SLOT = {TankPartNames.CHASSIS: VehicleSlots.CHASSIS.value,
 TankPartNames.HULL: VehicleSlots.HULL.value,
 TankPartNames.TURRET: VehicleSlots.TURRET.value,
 TankPartNames.GUN: VehicleSlots.GUN_JOINT.value}
ATTACHMENT_TYPE_TO_SLOT = {AttachmentType.GUN: VehicleSlots.GUN_RECOIL.value,
 AttachmentType.GUN_RIGHT: VehicleSlots.GUN_RECOIL_R.value,
 AttachmentType.GUN_LEFT: VehicleSlots.GUN_RECOIL_L.value}

def getExtraSlotMap(vDesc, appearance):
    extraSlotMap = []
    for partName in TankPartNames.ALL:
        customizationSlots = getattr(vDesc, partName).slotsAnchors
        for slot in customizationSlots:
            if slot.type in component_constants.ALLOWED_ATTACHMENT_SLOTS:
                slotTransform = _getSlotTransform(slot.scale, slot.rotation, slot.position)
                for attachment in appearance.attachments:
                    if attachment.slotId == slot.slotId:
                        transform = math_utils.createSRTMatrix(attachment.scale, attachment.rotation, Math.Vector3(0, 0, 0))
                        slotTransform.preMultiply(transform)
                        break

                if appearance.isDestroyed:
                    parentSlot = str(DESTROYED_VEHICLE_PART_TO_SLOT.get(partName))
                elif slot.applyType in ATTACHMENT_TYPE_TO_SLOT:
                    parentSlot = str(ATTACHMENT_TYPE_TO_SLOT[slot.applyType])
                else:
                    parentSlot = str(VEHICLE_PART_TO_SLOT.get(partName))
                extraSlotMap.append(ExtraSlotsMapItem(str(slot.slotId), parentSlot, slotTransform))
                if slot.hangerId != 0:
                    hangerSlotRotation = slot.hangerRotation + slot.rotation
                    hangerSlotTransform = _getSlotTransform(slot.scale, hangerSlotRotation, slot.position)
                    extraSlotMap.append(ExtraSlotsMapItem(str(slot.slotId) + HANGER_POSTFIX, parentSlot, hangerSlotTransform))

    return extraSlotMap


def createDetachedTurretComposition(gameObject, prefabMap=None, extraSlots=None):
    gameObject.createComponent(Compound.CompoundBasedComposerComponent, CGF.GameObject.INVALID_GAME_OBJECT, lambda *args: True, lambda *args: Compound.NodeInteractType.NONE, _DETACHED_TURRET_SLOTS_MAP, prefabMap or [], extraSlots or [])


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


def getObjectSlots(typeDescriptor):
    slots = []
    for parentName, slot in typeDescriptor.objectSlots:
        tr = Math.createRTMatrix(slot.rotation, slot.position)
        slots.append(ExtraSlotsMapItem(slot.name, parentName, tr))

    return slots


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
