# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVFXComponent.py
from __future__ import absolute_import
import logging
import GenericComponents
import Math
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.helpers.prefab_helpers import PrefabHandlerComponent
_logger = logging.getLogger(__name__)

class WTVFXComponent(PrefabHandlerComponent, DynamicScriptComponent):

    def _onAvatarReady(self):
        if not self.entity or not hasattr(self.entity, 'appearance') or self.entity.appearance is not None:
            self.createGameObject()
            return
        else:
            self.entity.events.onAppearanceReady += self.createGameObject
            return

    def createGameObject(self):
        self._unsubscribe()
        if not self.prefabPath:
            _logger.error('WTVFXComponent.createGameObject: no "prefabPath" specified!')
            return
        if not self.vehiclePart:
            _logger.error('WTVFXComponent.createGameObject: no "vehiclePart" specified!')
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
        self._unsubscribe()
        self.destroyGameObject()
        super(WTVFXComponent, self).onDestroy()

    def _unsubscribe(self):
        if not self.entity or not hasattr(self.entity, 'appearance'):
            return
        self.entity.events.onAppearanceReady -= self.createGameObject
