# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleRespawnComponent.py
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleRespawnComponent(DynamicScriptComponent):
    onSetSpawnTime = Event.Event()

    def chooseSpawnGroup(self, groupName):
        self.cell.chooseSpawnGroup(groupName)

    def set_spawnTime(self, prev):
        self.onSetSpawnTime(self.entity.id, self.spawnTime)
