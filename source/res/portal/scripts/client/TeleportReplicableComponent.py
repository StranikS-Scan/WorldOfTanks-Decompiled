# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/TeleportReplicableComponent.py
import Event
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
            if self.teleportingFinishTime > 0.01:
                self.onTeleportingChanged(self.go, self.teleportingVehicleID, self.teleportingFinishTime)

    def set_isTeleportLinked(self, prev):
        if not self.go:
            return
        if self.isTeleportLinked != prev:
            self.onTeleportLinked(self.go)

    def set_isCooldown(self, prev):
        if not self.go:
            return
        if self.isCooldown != prev:
            self.onCooldownChanged(self.go, self.isCooldown)

    def set_teleportingVehicleID(self, prev):
        if not self.go:
            return
        if self.teleportingVehicleID != 0:
            self.onTeleportOccupied(self.go, self.teleportingVehicleID)
        else:
            self.onTeleportFreed(self.go)

    def set_teleportingFinishTime(self, prev):
        if not self.go:
            return
        self.onTeleportingChanged(self.go, self.teleportingVehicleID, self.teleportingFinishTime)
