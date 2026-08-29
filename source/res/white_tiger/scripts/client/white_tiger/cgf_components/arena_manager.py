# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/arena_manager.py
from __future__ import absolute_import
import typing
import BigWorld
import CGF
from PlayerEvents import g_playerEvents
from constants import IS_CLIENT
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from WhiteTigerComponents import WTGunReloadedComponent, WTHealthComponent
from white_tiger.cgf_components import BossTag, HunterTag, PlayerVehicleTag
if IS_CLIENT:
    from Vehicle import Vehicle
    from WTIndexPool import WTIndexPool
else:

    class Vehicle(object):
        pass


    class WTIndexPool(object):
        pass


if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeSnapshot

def _isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()


class WTArenaSystem(CGF.System):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    VehicleActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(Vehicle))
    BossActivated = CGF.ActivateReaction(CGF.ReactRo(BossTag), CGF.ReactRw(Vehicle))
    HealthAccess = CGF.AccessReaction(CGF.Ro(WTHealthComponent))
    GunReloadAccess = CGF.AccessReaction(CGF.Ro(WTGunReloadedComponent))
    BossAccess = CGF.AccessReaction(CGF.Ro(BossTag))
    BossIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(BossTag), CGF.Ro(Vehicle))
    PlayerIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(PlayerVehicleTag), CGF.Ro(Vehicle))
    HunterIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(HunterTag), CGF.Ro(Vehicle))
    CampIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(WTIndexPool))
    Reactions = CGF.Reactions(VehicleActivated, BossActivated, HealthAccess, GunReloadAccess, BossAccess, BossIterate, PlayerIterate, HunterIterate, CampIterate)

    def update(self):
        q = CGF.CommandQueue(self.gom)
        for go, vehicle in self.reaction(self.VehicleActivated):
            self.onAdded(vehicle, go, q)

        healthAccess = self.reaction(self.HealthAccess)
        gunReloadAccess = self.reaction(self.GunReloadAccess)
        bossAccess = self.reaction(self.BossAccess)
        for _, vehicle in self.reaction(self.BossActivated):
            self.onBossAdded(vehicle, q, healthAccess, gunReloadAccess, bossAccess)

    def onMappingLoaded(self):
        if _isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def onMappingUnloaded(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        ammoCtrl = self.guiSessionProvider.shared.ammo
        if ammoCtrl:
            ammoCtrl.onGunReloadTimeSet -= self.__vehicleGunReloadTimeSet

    def onAdded(self, vehicle, go, queue):
        descriptor = vehicle.typeDescriptor
        if descriptor is not None:
            tags = descriptor.type.tags
            if WT_VEHICLE_TAGS.BOSS in tags:
                queue.createComponent(go, BossTag)
            if WT_VEHICLE_TAGS.HUNTER in tags:
                queue.createComponent(go, HunterTag)
        if vehicle.id == BigWorld.player().playerVehicleID:
            queue.createComponent(go, PlayerVehicleTag)
        return

    def onBossAdded(self, vehicle, queue, healthAccess, gunReloadedAccess, bossAccess):

        def vehicleHealth():
            veh = appearance.getVehicle()
            return veh.health if veh else 0

        appearance = vehicle.appearance
        appearanceGo = appearance.gameObject
        if appearanceGo is not None:
            if not healthAccess.contains(appearanceGo):
                descriptor = appearance.typeDescriptor
                queue.createComponent(appearanceGo, WTHealthComponent, lambda : vehicleHealth(), descriptor.maxHealth)
            if not gunReloadedAccess.contains(appearanceGo):
                queue.createComponent(appearanceGo, WTGunReloadedComponent)
            if not bossAccess.contains(appearanceGo):
                queue.createComponent(appearanceGo, BossTag)
        return

    def bossQuery(self):
        return self.reaction(self.BossIterate)

    def playerQuery(self):
        return self.reaction(self.PlayerIterate)

    def hunterQuery(self):
        return self.reaction(self.HunterIterate)

    def campsQuery(self):
        return self.reaction(self.CampIterate)

    def __onAvatarReady(self):
        ammoCtrl = self.guiSessionProvider.shared.ammo
        ammoCtrl.onGunReloadTimeSet += self.__vehicleGunReloadTimeSet

    def __vehicleGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None or vehicle.appearance is None:
            return
        else:
            q = CGF.CommandQueue(self.gom)
            if state.isReloading():
                q.removeComponent(vehicle.appearance.gameObject, WTGunReloadedComponent)
            elif vehicle.appearance.gameObject.findRead(WTGunReloadedComponent) is None:
                q.createComponent(vehicle.appearance.gameObject, WTGunReloadedComponent)
            return
