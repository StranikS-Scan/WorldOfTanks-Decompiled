# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_pickup_manager.py
import CGF
import Math
import math
import GenericComponents
from cgf_script.managers_registrator import autoregister, onProcessQuery
from vehicle_systems.components.vehicle_pickup_component import VehiclePickupComponent

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class VehiclePickupManager(CGF.ComponentManager):

    @onProcessQuery(CGF.GameObject, VehiclePickupComponent, GenericComponents.TransformComponent)
    def processPickup(self, go, vehiclePickupComponent, vehicleTransform):
        dt = self.clock.gameDelta
        vehiclePickupComponent.time += dt
        if vehiclePickupComponent.time > VehiclePickupComponent.MAX_LIFETIME:
            go.removeComponent(vehiclePickupComponent)
        tankUp = vehicleTransform.worldTransform.applyToAxis(1)
        angle = math.degrees(tankUp.angle(Math.Vector3(0, 1, 0)))
        if angle < VehiclePickupComponent.MAX_ANGLE_DEVIATION:
            go.removeComponent(vehiclePickupComponent)
