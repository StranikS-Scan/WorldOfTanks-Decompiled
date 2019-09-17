# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/entity_components/vehicle_race_component.py
import BigWorld
from . import VehicleComponent

class VehicleRaceComponent(VehicleComponent):

    def set_raceFinishTime(self, prev=0.0):
        ctrl = self.guiSessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRaceFinished(self.id, self.raceFinishTime)
        return

    def set_racePosition(self, _):
        if self.isPlayerVehicle:
            BigWorld.player().onNewRacePosition(self.racePosition)
