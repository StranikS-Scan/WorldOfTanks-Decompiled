# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/attachment_slot_manager.py
from functools import partial
import CGF
import Math
import GenericComponents
import math_utils
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery
from vehicle_systems.tankStructure import TankPartNames
from vehicle_systems.vehicle_composition import VehicleSlots, findParentVehicleAppearance
VEHICLE_SLOT_TO_PART = {VehicleSlots.CHASSIS.value: TankPartNames.CHASSIS,
 VehicleSlots.HULL.value: TankPartNames.HULL,
 VehicleSlots.TURRET.value: TankPartNames.TURRET,
 VehicleSlots.GUN_INCLINATION.value: TankPartNames.GUN}
DESTROYED_VEHICLE_SLOT_TO_PART = {VehicleSlots.CHASSIS.value: TankPartNames.CHASSIS,
 VehicleSlots.HULL.value: TankPartNames.HULL,
 VehicleSlots.TURRET.value: TankPartNames.TURRET,
 VehicleSlots.GUN_JOINT.value: TankPartNames.GUN}

@registerComponent
class AttachmentSlotComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    slotId = ComponentProperty(type=CGFMetaTypes.INT, editorName='ID', value=0)

    def __init__(self, slotId):
        super(AttachmentSlotComponent, self).__init__()
        self.slotId = slotId
        self.scale = None
        self.rotation = None
        self.prefabPath = None
        return

    def update(self, scale, rotation, prefabPath):
        if self.scale == scale and self.rotation == rotation and self.prefabPath == prefabPath:
            return False
        self.scale = scale
        self.rotation = rotation
        self.prefabPath = prefabPath
        return True

    def clear(self):
        self.scale = None
        self.rotation = None
        self.prefabPath = None
        return True


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class AttachmentSlotManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GenericComponents.SlotMarkerComponent)
    def onAddedSlotMarker(self, gameObject, slotMarker):
        appearance = findParentVehicleAppearance(gameObject)
        if appearance:
            vehicleDescriptor = appearance.typeDescriptor
            if appearance.isDestroyed:
                partName = DESTROYED_VEHICLE_SLOT_TO_PART.get(slotMarker.slotName)
            else:
                partName = VEHICLE_SLOT_TO_PART.get(slotMarker.slotName)
            if partName and hasattr(vehicleDescriptor, partName):
                customizationSlots = getattr(vehicleDescriptor, partName).slotsAnchors
                for slot in customizationSlots:
                    if slot.type == 'attachment' and not slot.hiddenForUser:
                        go = CGF.GameObject(gameObject.spaceID, 'AttachmentSlot')
                        go.createComponent(GenericComponents.TransformComponent, _getSlotTransform(slot))
                        go.createComponent(GenericComponents.HierarchyComponent, gameObject)
                        attachmentSlot = go.createComponent(AttachmentSlotComponent, slot.slotId)
                        go.activate()
                        go.transferOwnership()
                        _updateAttachmentSlot(appearance, go, attachmentSlot)


def _getSlotTransform(slot):
    rotationYPR = Math.Vector3(slot.rotation.y, slot.rotation.x, slot.rotation.z)
    return math_utils.createSRTMatrix(slot.scale, rotationYPR, slot.position)


def _getAttachmentTransform(attachment):
    return math_utils.createSRTMatrix(attachment.scale, attachment.rotation, Math.Vector3(0, 0, 0))


def _getAttachmentFromSlot(appearance, slotId):
    for attachment in appearance.attachments:
        if attachment.slotId == slotId:
            return attachment

    return None


def _updateAttachmentSlot(appearance, gameObject, attachmentSlot):

    def _onLoaded(prefabPath, go):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        findResult = hierarchy.findComponentInParent(go, AttachmentSlotComponent)
        if findResult is not None and len(findResult) > 1 and findResult[1].prefabPath != prefabPath:
            CGF.removeGameObject(go)
        return

    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    attachment = _getAttachmentFromSlot(appearance, attachmentSlot.slotId)
    if attachment and attachmentSlot.update(attachment.scale, attachment.rotation, attachment.modelName):
        children = hierarchy.getChildren(gameObject) or []
        for child in children:
            CGF.removeGameObject(child)

        if attachment.modelName:
            CGF.loadGameObjectIntoHierarchy(attachment.modelName, gameObject, _getAttachmentTransform(attachment), hierarchyLoadedCallback=partial(_onLoaded, attachment.modelName))
    elif not attachment:
        attachmentSlot.clear()
        children = hierarchy.getChildren(gameObject) or []
        for child in children:
            CGF.removeGameObject(child)


def updateAttachments(appearance):
    hierarchy = CGF.HierarchyManager(appearance.gameObject.spaceID)
    attachmentSlots = hierarchy.findComponentsInHierarchy(appearance.gameObject, AttachmentSlotComponent)
    for gameObject, attachmentSlot in attachmentSlots:
        _updateAttachmentSlot(appearance, gameObject, attachmentSlot)
