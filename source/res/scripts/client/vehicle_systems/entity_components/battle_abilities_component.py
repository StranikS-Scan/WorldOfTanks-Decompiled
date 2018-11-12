# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/entity_components/battle_abilities_component.py
import BigWorld
from . import VehicleComponent

class BattleAbilitiesComponent(VehicleComponent):

    def _getEquipmentComp(self):
        componentSystem = BigWorld.player().arena.componentSystem
        return getattr(componentSystem, 'arenaEquipmentComponent', None) if componentSystem is not None else None

    def set_inspiringEffect(self, prev=None):
        if not self.isStarted or self.inspiringEffect == prev:
            return
        else:
            data = self.inspiringEffect
            equipmentComp = self._getEquipmentComp()
            if equipmentComp is not None:
                if data is not None:
                    equipmentComp.updateInspiringSource(self.id, data.startTime, data.endTime, data.inactivationDelay, data.radius)
                else:
                    equipmentComp.updateInspiringSource(self.id, None, None, None, None)
            return

    def set_inspired(self, prev=None):
        if not self.isStarted or self.inspired == prev:
            return
        else:
            data = self.inspired
            equipmentComp = self._getEquipmentComp()
            if equipmentComp is not None:
                if data is not None:
                    equipmentComp.updateInspired(self.id, data.startTime, data.endTime, data.inactivationStartTime, data.inactivationEndTime)
                else:
                    equipmentComp.updateInspired(self.id, None, None, None, None)
            return

    def _removeInspire(self):
        if self.inspired or self.inspiringEffect:
            equipmentComp = self._getEquipmentComp()
            if equipmentComp is not None:
                equipmentComp.removeInspire(self.id)
        return
