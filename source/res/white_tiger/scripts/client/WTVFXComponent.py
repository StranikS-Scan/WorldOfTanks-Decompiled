# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVFXComponent.py
import logging
import GenericComponents
import Math
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.helpers.prefab_helpers import PrefabHandlerComponent
_logger = logging.getLogger(__name__)

class WTVFXComponent(PrefabHandlerComponent, DynamicScriptComponent):

    def _onAvatarReady(self):
        self.createGameObject()

    def onAppearanceReady(self):
        self.setAppearanceReady()

    def createGameObject(self):
        if not self.prefabPath:
            _logger.error('WTVFXComponent._onAvatarReady: no "prefabPath" specified!')
            return
        if not self.vehiclePart:
            _logger.error('WTVFXComponent._onAvatarReady: no "vehiclePart" specified!')
            return
        vehicle = self.entity
        from vehicle_systems import vehicle_composition
        entityGameObject = vehicle.entityGameObject
        if self.vehiclePart == 'hull':
            requestedSlot = vehicle_composition.VehicleSlots.HULL
        elif self.vehiclePart == 'turret':
            requestedSlot = vehicle_composition.VehicleSlots.TURRET
        else:
            requestedSlot = vehicle_composition.VehicleSlots.GUN_INCLINATION
        go = GenericComponents.findSlot(entityGameObject, requestedSlot.value)
        self.loadGameObject(self.entity, self.prefabPath, go, Math.Vector3(0, 0, 0))

    def onDestroy(self):
        self.destroyGameObject()
        super(WTVFXComponent, self).onDestroy()
