# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/TeleportReplicableComponent.py
import Event
from items.utils import isclose
from script_component.DynamicScriptComponent import DynamicScriptComponent
from portal_common_cgf.teleport.components import TeleportReplicableComponent as TeleportReplicableComponentBase

class TeleportReplicableComponent(DynamicScriptComponent, TeleportReplicableComponentBase):
    onTeleportingChanged = Event.Event()
    onCooldownChanged = Event.Event()
    onTeleportLinked = Event.Event()
    onTeleportOccupied = Event.Event()
    onTeleportFreed = Event.Event()

    @property
    def go(self):
        return self.entity.entityGameObject

    def _onAvatarReady(self):
        if self.index != 0:
            self.onTeleportLinked(self.go)
            for i, vehicleID in enumerate(self.teleportingVehicleIDs):
                if vehicleID != 0 and i < len(self.teleportingFinishTimes):
                    finishTime = self.teleportingFinishTimes[i]
                    if finishTime > 0.01:
                        self.onTeleportingChanged(self.go, vehicleID, finishTime)

    def set_isTeleportLinked(self, prev):
        if not self.go:
            return
        if self.isTeleportLinked != prev:
            self.onTeleportLinked(self.go)

    def set_cooldownVehicleIDs(self, prev):
        if not self.go:
            return
        prevSet = prev or ()
        currSet = self.cooldownVehicleIDs
        self.onCooldownChanged(self.go, prevSet, currSet)

    def set_teleportingVehicleIDs(self, prev):
        if not self.go:
            return
        prevSet = prev or ()
        currSet = self.teleportingVehicleIDs
        for i, vehicleID in enumerate(prevSet):
            if vehicleID == 0 or vehicleID in currSet:
                continue
            finishTime = self.teleportingFinishTimes[i] if i < len(self.teleportingFinishTimes) else 0.0
            if not isclose(finishTime, 0.0):
                self.onTeleportingChanged(self.go, vehicleID, 0.0)
            self.onTeleportFreed(self.go)

        for vehicleID in currSet:
            if vehicleID != 0 and vehicleID not in prevSet:
                self.onTeleportOccupied(self.go, vehicleID)

    def set_teleportingFinishTimes(self, prev):
        if not self.go:
            return
        prevSet = prev or ()
        currSet = self.teleportingFinishTimes
        for i, finishTime in enumerate(currSet):
            vehicleID = self.teleportingVehicleIDs[i] if i < len(self.teleportingVehicleIDs) else 0
            prevFinish = prevSet[i] if i < len(prevSet) else 0.0
            if finishTime != prevFinish and vehicleID != 0:
                self.onTeleportingChanged(self.go, vehicleID, finishTime)

    def set_teleportingStartTimes(self, prev):
        if not self.go:
            return
        prevSet = prev or ()
        currSet = self.teleportingStartTimes
        for i, startTime in enumerate(currSet):
            vehicleID = self.teleportingVehicleIDs[i] if i < len(self.teleportingVehicleIDs) else 0
            prevStart = prevSet[i] if i < len(prevSet) else 0.0
            if startTime != prevStart and vehicleID != 0:
                self.onTeleportingChanged(self.go, vehicleID, self.teleportingFinishTimes[i] if i < len(self.teleportingFinishTimes) else 0.0)
