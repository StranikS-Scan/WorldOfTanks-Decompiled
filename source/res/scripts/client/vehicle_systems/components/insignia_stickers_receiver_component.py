# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/insignia_stickers_receiver_component.py
import CGF
import GenericComponents
import GpuDecals
import Math
from VehicleStickers import Insignia
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery
from constants import IS_EDITOR
from helpers import dependency, isPlayerAccount
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.vehicle_composition import findParentVehicleAppearance, VehicleSlots

@registerComponent
class InsigniaStickersReceiverComponent(object):
    category = 'Render'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    vehiclePart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Vehicle Part', value=Insignia.Types.SINGLE, annotations={'comboBox': {Insignia.Types.SINGLE: Insignia.Types.SINGLE,
                  Insignia.Types.DUAL_LEFT: Insignia.Types.DUAL_LEFT,
                  Insignia.Types.DUAL_RIGHT: Insignia.Types.DUAL_RIGHT}})


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class InsigniaStickersReceiverManager(CGF.ComponentManager):
    receiverQuery = CGF.QueryConfig(CGF.GameObject, InsigniaStickersReceiverComponent, GpuDecals.GpuDecalsReceiverComponent, GenericComponents.DynamicModelComponent, GenericComponents.TransformComponent)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def activate(self):
        if not IS_EDITOR and isPlayerAccount() and self.hangarSpace:
            self.hangarSpace.onVehicleChanged += self.vehicleChanged

    def deactivate(self):
        if not IS_EDITOR and isPlayerAccount() and self.hangarSpace:
            self.hangarSpace.onVehicleChanged -= self.vehicleChanged
            appearance = self.hangarSpace.getVehicleEntityAppearance()
            if appearance is not None:
                appearance.onDecalsUpdated -= self.onDecalsUpdated
        return

    @onAddedQuery(CGF.GameObject, InsigniaStickersReceiverComponent, GpuDecals.GpuDecalsReceiverComponent, GenericComponents.DynamicModelComponent, GenericComponents.TransformComponent, tickGroup='postTickUpdate')
    def onAdded(self, gameobject, vehicleStickersReceiver, gpuDecalsReceiver, dynamicModelComponent, transformComponent):
        self.attach(gameobject, vehicleStickersReceiver, gpuDecalsReceiver, dynamicModelComponent, transformComponent)

    def onDecalsUpdated(self):
        for gameobject, vehicleStickersReceiver, gpuDecalsReceiver, dynamicModelComponent, transformComponent in self.receiverQuery:
            self.attach(gameobject, vehicleStickersReceiver, gpuDecalsReceiver, dynamicModelComponent, transformComponent)

    def attach(self, gameobject, vehicleStickersReceiver, gpuDecalsReceiver, dynamicModelComponent, transformComponent):
        appearance = findParentVehicleAppearance(gameobject)
        if appearance is not None and gpuDecalsReceiver.blockIdx != GpuDecals.INVALID_BLOCK_IDX:
            gunGo = GenericComponents.findSlot(appearance.gameObject, VehicleSlots.GUN.value)
            if not gunGo.isValid():
                return
            gunWorldTransform = gunGo.findComponentByType(GenericComponents.TransformComponent).worldTransform
            offsetToRootMatrix = transformComponent.worldTransform
            offsetToRootMatrix.invert()
            offsetToRootMatrix.preMultiply(gunWorldTransform)
            offsetToRootMatrix = Math.createSRTMatrix(offsetToRootMatrix.scale, Math.Vector3(), offsetToRootMatrix.translation)
            appearance.vehicleStickers.attachInsigniaReceiverStickers(vehicleStickersReceiver.vehiclePart, dynamicModelComponent, dynamicModelComponent.getRootSuperModel(), offsetToRootMatrix, gpuDecalsReceiver.blockIdx)
        return

    def vehicleChanged(self):
        appearance = self.hangarSpace.getVehicleEntityAppearance()
        if appearance is not None:
            appearance.onDecalsUpdated += self.onDecalsUpdated
        return
