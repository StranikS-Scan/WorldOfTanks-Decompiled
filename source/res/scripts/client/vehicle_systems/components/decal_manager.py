# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/decal_manager.py
import CGF
import GpuDecals
import GenericComponents
from vehicle_systems.vehicle_composition import findParentVehicleAppearance
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames
from GenericComponents import DecalComponent, SlotMarkerComponent

class DecalComponentSystem(CGF.System):
    DecalActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(DecalComponent))
    DecalReceiverActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(GpuDecals.GpuDecalsReceiverComponent))
    DecalReceiverWithSlotActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(GpuDecals.GpuDecalsReceiverComponent), CGF.Ro(SlotMarkerComponent))
    DecalReceiverDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactHas(GpuDecals.GpuDecalsReceiverComponent))
    DecalComponentAccess = CGF.AccessReaction(CGF.Rw(DecalComponent))
    ReceiverAccess = CGF.AccessReaction(CGF.Rw(GpuDecals.GpuDecalsReceiverComponent))
    Reactions = CGF.Reactions(DecalActivated, DecalReceiverActivated, DecalReceiverWithSlotActivated, DecalReceiverDeactivated, DecalComponentAccess, ReceiverAccess)

    def update(self):
        decalAccess = self.reaction(self.DecalComponentAccess)
        receiverAccess = self.reaction(self.ReceiverAccess)
        for go in self.reaction(self.DecalReceiverDeactivated):
            appearance = findParentVehicleAppearance(go)
            if appearance is None:
                continue
            decals = CGF.findInHierarchyWithReaction(appearance.gameObject, decalAccess)
            for decal in decals:
                if decal.receiver == go:
                    self.__unbindReceiver(decal)

        for go, decal in self.reaction(self.DecalActivated):
            if self.__bindReceiver(decal, decal.receiver, receiverAccess):
                return
            appearance = findParentVehicleAppearance(go)
            if appearance is None:
                return
            part = GenericComponents.findSlot(appearance.gameObject, TankPartIndexes.getName(decal.partHandle))
            self.__bindReceiver(decal, part, receiverAccess)

        for go, _ in self.reaction(self.DecalReceiverActivated):
            appearance = findParentVehicleAppearance(go)
            if appearance is None:
                return
            decals = CGF.findInHierarchyWithReaction(appearance.gameObject, decalAccess)
            for decal in decals:
                if decal.receiver == go:
                    self.__bindReceiver(decal, decal.receiver, receiverAccess)

        for go, _, slotMarker in self.reaction(self.DecalReceiverWithSlotActivated):
            appearance = findParentVehicleAppearance(go)
            if appearance is None:
                return
            partIdx = TankPartNames.getIdx(slotMarker.slotName)
            decals = CGF.findInHierarchyWithReaction(appearance.gameObject, decalAccess)
            for decal in decals:
                if decal.partHandle == partIdx:
                    if not self.__isReceiverBinded(decal):
                        self.__bindReceiver(decal, go, receiverAccess)

        return

    @staticmethod
    def __bindReceiver(decal, receiver, receiverAccess):
        if not receiver.valid:
            return False
        else:
            component = receiverAccess.find(receiver)
            if component is None or component.blockIdx == GpuDecals.INVALID_BLOCK_IDX:
                return False
            decal.receiverId = component.blockIdx
            return True

    @staticmethod
    def __unbindReceiver(decal):
        decal.receiverId = GpuDecals.INVALID_BLOCK_IDX
        return True

    @staticmethod
    def __isReceiverBinded(decal):
        return decal.receiverId != GpuDecals.INVALID_BLOCK_IDX
