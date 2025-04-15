# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleLivesComponent.py
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleLivesComponent(DynamicScriptComponent):
    onIncreasedLives = Event.Event()
    onLivesExhausted = Event.Event()
    onVehicleDestroyed = Event.Event()

    def set_lives(self, prev):
        if self.lives > prev:
            self.onIncreasedLives(self.entity)
        elif self.lives < prev:
            self.onVehicleDestroyed(self.entity, self.lives)
        if self.lives == 0:
            self.onLivesExhausted(self.entity)
