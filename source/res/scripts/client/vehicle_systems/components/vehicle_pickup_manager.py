# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_pickup_manager.py
import CGF
import Math
import math
from vehicle_systems.components.vehicle_pickup_component import VehiclePickupComponent

class VehiclePickupSystem(CGF.System):
    PickupActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(VehiclePickupComponent), CGF.Ro(CGF.TransformComponent))
    Reactions = CGF.Reactions(PickupActivated)

    def update(self):
        dt = self.clock.updateDelta
        q = CGF.CommandQueue(self.gom)
        for go, pickup, tr in self.reaction(self.PickupActivated):
            pickup.time += dt
            if pickup.time > VehiclePickupComponent.MAX_LIFETIME:
                q.removeComponent(go, VehiclePickupComponent)
            tankUp = tr.worldTransform.applyToAxis(1)
            angle = math.degrees(tankUp.angle(Math.Vector3(0, 1, 0)))
            if angle < VehiclePickupComponent.MAX_ANGLE_DEVIATION:
                q.removeComponent(go, VehiclePickupComponent)
