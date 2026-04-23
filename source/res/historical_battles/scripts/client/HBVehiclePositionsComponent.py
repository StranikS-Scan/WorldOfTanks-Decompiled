# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehiclePositionsComponent.py
import typing
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent
if typing.TYPE_CHECKING:
    from typing import List, Dict
    from Math import Vector3

class HBVehiclePositionsComponent(DynamicScriptComponent):

    def __init__(self):
        super(HBVehiclePositionsComponent, self).__init__()
        self.onReceive = Event.Event()

    def receivePosition(self, vehicleEntityID, position):
        self.onReceive([{'vehicleID': vehicleEntityID,
          'position': position}])

    def receivePositions(self, positions):
        self.onReceive(positions)
