# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/decal_manager.py
import CGF
import GenericComponents
import GpuDecals
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from vehicle_systems.vehicle_composition import findParentVehicleAppearance
from vehicle_systems.tankStructure import TankPartIndexes, TankPartNames

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class DecalComponentManager(CGF.ComponentManager):

    @onAddedQuery(GenericComponents.DecalComponent, CGF.GameObject)
    def onDecalAdded(self, decal, go):
        if self.__bindReceiver(decal, decal.receiver):
            return
        else:
            appearance = findParentVehicleAppearance(go)
            if appearance is None:
                return
            part = GenericComponents.findSlot(appearance.gameObject, TankPartIndexes.getName(decal.partHandle))
            self.__bindReceiver(decal, part)
            return

    @onAddedQuery(CGF.No(GenericComponents.SlotMarkerComponent), GpuDecals.GpuDecalsReceiverComponent, CGF.GameObject)
    def onReceiverAdded(self, receiver, go):
        appearance = findParentVehicleAppearance(go)
        if appearance is None:
            return
        else:
            hm = CGF.HierarchyManager(self.spaceID)
            decals = hm.findComponentsInHierarchy(appearance.gameObject, GenericComponents.DecalComponent)
            for _, decal in decals:
                if decal.receiver == go:
                    self.__bindReceiver(decal, decal.receiver)

            return

    @onAddedQuery(GenericComponents.SlotMarkerComponent, GpuDecals.GpuDecalsReceiverComponent, CGF.GameObject)
    def onSlotReceiverAdded(self, slotMarker, receiver, go):
        appearance = findParentVehicleAppearance(go)
        if appearance is None:
            return
        else:
            partIdx = TankPartNames.getIdx(slotMarker.slotName)
            hm = CGF.HierarchyManager(self.spaceID)
            decals = hm.findComponentsInHierarchy(appearance.gameObject, GenericComponents.DecalComponent)
            for _, decal in decals:
                if decal.partHandle == partIdx:
                    if not self.__isReceiverBinded(decal):
                        self.__bindReceiver(decal, go)

            return

    @onRemovedQuery(GpuDecals.GpuDecalsReceiverComponent, CGF.GameObject)
    def onReceiverRemoved(self, receiver, go):
        appearance = findParentVehicleAppearance(go)
        if appearance is None:
            return
        else:
            hm = CGF.HierarchyManager(self.spaceID)
            decals = hm.findComponentsInHierarchy(appearance.gameObject, GenericComponents.DecalComponent)
            for _, decal in decals:
                if decal.receiver == go:
                    self.__unbindReceiver(decal)

            return

    @staticmethod
    def __bindReceiver(decal, receiver):
        if not receiver.isValid():
            return False
        else:
            component = receiver.findComponentByType(GpuDecals.GpuDecalsReceiverComponent)
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
