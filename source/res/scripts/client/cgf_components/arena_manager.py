# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/arena_manager.py
import BigWorld
import CGF
import Health
import Vehicle
import Projectiles
from cgf_script.managers_registrator import onAddedQuery
from cgf_components import BossTag, HunterTag, PlayerVehicleTag
from wt_settings import g_wt_config

class ArenaManager(CGF.ComponentManager):

    @onAddedQuery(Vehicle.Vehicle, CGF.GameObject)
    def onAdded(self, vehicle, go):
        descriptor = vehicle.typeDescriptor
        if descriptor is not None:
            vehCD = vehicle.typeDescriptor.type.compactDescr
            if g_wt_config.isAnyTypeBoss(vehCD):
                go.createComponent(BossTag)
            elif g_wt_config.isHunterVehicle(vehCD):
                go.createComponent(HunterTag)
        if vehicle.id == BigWorld.player().playerVehicleID:
            go.createComponent(PlayerVehicleTag)
        return

    @onAddedQuery(BossTag, Vehicle.Vehicle)
    def onBossAdded(self, _, vehicle):
        appearance = vehicle.appearance
        if appearance is not None:
            if appearance.findComponentByType(Health.HealthComponent) is None:
                descriptor = appearance.typeDescriptor
                appearance.createComponent(Health.HealthComponent, lambda : appearance.vehicleHealth, descriptor.maxHealth)
            if appearance.findComponentByType(Projectiles.GunReloadedComponent) is None:
                appearance.createComponent(Projectiles.GunReloadedComponent)
            if appearance.findComponentByType(BossTag) is None:
                appearance.createComponent(BossTag)
        return
