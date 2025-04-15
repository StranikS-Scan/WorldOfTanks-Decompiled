# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehiclePositionsComponent.py
from typing import Dict
import BigWorld
import Event
from Math import Vector3

class HBVehiclePositionsComponent(BigWorld.DynamicScriptComponent):

    def __init__(self):
        self.onReceive = Event.Event()

    def receivePosition(self, vehicleEntityID, position):
        self.onReceive({vehicleEntityID: position})

    def receivePositions(self, package):
        self.onReceive(package)
