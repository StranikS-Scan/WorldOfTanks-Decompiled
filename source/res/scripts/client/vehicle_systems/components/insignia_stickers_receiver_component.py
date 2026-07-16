# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/insignia_stickers_receiver_component.py
import CGF
import GenericComponents
import GpuDecals
import Math
from VehicleStickers import Insignia
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_EDITOR
from helpers import dependency, isPlayerAccount
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.vehicle_composition import findParentVehicleAppearance, VehicleSlots

@registerComponent
class InsigniaStickersReceiverComponent(object):
    category = 'Render'
    editorTitle = 'Insignia Stickers Receiver Component'
    domain = CGF.Domain.ClientEditor
    vehiclePart = ComponentProperty(type=CGF.PropertyType.String, editorName='Vehicle Part', value=Insignia.Types.SINGLE, annotations={'comboBox': {Insignia.Types.SINGLE: Insignia.Types.SINGLE,
                  Insignia.Types.DUAL_LEFT: Insignia.Types.DUAL_LEFT,
                  Insignia.Types.DUAL_RIGHT: Insignia.Types.DUAL_RIGHT}})


class InsigniaStickersReceiverSystem(CGF.System):
    InsigniaAcitvated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(InsigniaStickersReceiverComponent), CGF.ReactRw(GpuDecals.GpuDecalsReceiverComponent), CGF.Ro(GenericComponents.DynamicModelComponent), CGF.Ro(CGF.TransformComponent))
    InsigniaIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Rw(InsigniaStickersReceiverComponent), CGF.Rw(GpuDecals.GpuDecalsReceiverComponent), CGF.Ro(GenericComponents.DynamicModelComponent), CGF.Ro(CGF.TransformComponent))
    TransformAccess = CGF.AccessReaction(CGF.TransformComponent)
    hangarSpace = dependency.descriptor(IHangarSpace)
    Reactions = CGF.Reactions(InsigniaAcitvated, InsigniaIterate, TransformAccess)

    def onMappingLoaded(self):
        if not IS_EDITOR and isPlayerAccount() and self.hangarSpace:
            self.hangarSpace.onVehicleChanged += self.vehicleChanged

    def onMappingUnloaded(self):
        if not IS_EDITOR and isPlayerAccount() and self.hangarSpace:
            self.hangarSpace.onVehicleChanged -= self.vehicleChanged
            appearance = self.hangarSpace.getVehicleEntityAppearance()
            if appearance is not None:
                appearance.onDecalsUpdated -= self.onDecalsUpdated
        return

    def update(self):
        transformAccess = self.reaction(self.TransformAccess)
        for go, insignia, receiver, model, tr in self.reaction(self.InsigniaAcitvated):
            self.attach(go, insignia, receiver, model, tr, transformAccess)

    def onDecalsUpdated(self):
        transformAccess = self.reaction(self.TransformAccess)
        insigniaIterate = self.reaction(self.InsigniaIterate)
        for go, insignia, receiver, model, tr in insigniaIterate:
            self.attach(go, insignia, receiver, model, tr, transformAccess)

    def attach(self, gameobject, vehicleStickersReceiver, gpuDecalsReceiver, dynamicModelComponent, transformComponent, transformAccess):
        appearance = findParentVehicleAppearance(gameobject)
        if appearance is not None and gpuDecalsReceiver.blockIdx != GpuDecals.INVALID_BLOCK_IDX:
            gunGo = GenericComponents.findSlot(appearance.gameObject, VehicleSlots.GUN.value)
            if not gunGo.valid:
                return
            gunWorldTransform = transformAccess.find(gunGo).worldTransform
            offsetToRootMatrix = transformComponent.worldTransform
            offsetToRootMatrix.invert()
            offsetToRootMatrix.preMultiply(gunWorldTransform)
            offsetToRootMatrix = Math.createSRTMatrix(offsetToRootMatrix.scale, Math.Vector3(), offsetToRootMatrix.translation)
            modelLink = CGF.ComponentLink(gameobject, GenericComponents.DynamicModelComponent)
            appearance.vehicleStickers.attachInsigniaReceiverStickers(vehicleStickersReceiver.vehiclePart, modelLink, offsetToRootMatrix, gpuDecalsReceiver.blockIdx)
        return

    def vehicleChanged(self):
        appearance = self.hangarSpace.getVehicleEntityAppearance()
        if appearance is not None:
            appearance.onDecalsUpdated += self.onDecalsUpdated
        return
