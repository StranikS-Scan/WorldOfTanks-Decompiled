# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/arena_manager.py
import BigWorld
import CGF
import Statuses
import Vehicle
import InstantStatuses
from cgf_script.managers_registrator import onAddedQuery
from cgf_components import BossTag, HunterTag, PlayerVehicleTag

class ArenaManager(CGF.ComponentManager):

    @onAddedQuery(Vehicle.Vehicle, CGF.GameObject)
    def onAdded(self, vehicle, go):
        descriptor = vehicle.typeDescriptor
        if descriptor is not None:
            tags = descriptor.type.tags
            if 'event_boss' in tags:
                go.createComponent(BossTag)
            if 'event_hunter' in tags:
                go.createComponent(HunterTag)
        if vehicle.id == BigWorld.player().playerVehicleID:
            go.createComponent(PlayerVehicleTag)
        return

    @onAddedQuery(BossTag, Vehicle.Vehicle)
    def onBossAdded(self, _, vehicle):
        appearance = vehicle.appearance
        if appearance is not None:
            if appearance.findComponentByType(Statuses.HealthComponent) is None:
                descriptor = appearance.typeDescriptor
                appearance.createComponent(Statuses.HealthComponent, lambda : appearance.vehicleHealth, descriptor.maxHealth)
            if appearance.findComponentByType(InstantStatuses.GunReloadedComponent) is None:
                appearance.createComponent(InstantStatuses.GunReloadedComponent)
            if appearance.findComponentByType(BossTag) is None:
                appearance.createComponent(BossTag)
        return
