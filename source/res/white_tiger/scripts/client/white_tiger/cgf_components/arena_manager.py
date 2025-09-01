# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/arena_manager.py
import typing
import BigWorld
import CGF
from PlayerEvents import g_playerEvents
from constants import IS_CLIENT
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS, ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.managers_registrator import onAddedQuery
from WhiteTigerComponents import WTGunReloadedComponent, WTHealthComponent
from white_tiger.cgf_components import BossTag, HunterTag, PlayerVehicleTag
if IS_CLIENT:
    from Vehicle import Vehicle
else:

    class Vehicle(object):
        pass


if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeSnapshot

def _isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, CGF.DomainOption.DomainClient)
class WTArenaManager(CGF.ComponentManager):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def activate(self):
        if _isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def deactivate(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        ammoCtrl = self.guiSessionProvider.shared.ammo
        if ammoCtrl:
            ammoCtrl.onGunReloadTimeSet -= self.__vehicleGunReloadTimeSet

    @onAddedQuery(Vehicle, CGF.GameObject)
    def onAdded(self, vehicle, go):
        descriptor = vehicle.typeDescriptor
        if descriptor is not None:
            tags = descriptor.type.tags
            if WT_VEHICLE_TAGS.BOSS in tags:
                go.createComponent(BossTag)
            if WT_VEHICLE_TAGS.HUNTER in tags:
                go.createComponent(HunterTag)
        if vehicle.id == BigWorld.player().playerVehicleID:
            go.createComponent(PlayerVehicleTag)
        return

    @onAddedQuery(BossTag, Vehicle)
    def onBossAdded(self, _, vehicle):

        def vehicleHealth():
            veh = appearance.getVehicle()
            return veh.health if veh else 0

        appearance = vehicle.appearance
        if appearance is not None:
            if appearance.findComponentByType(WTHealthComponent) is None:
                descriptor = appearance.typeDescriptor
                appearance.createComponent(WTHealthComponent, lambda : vehicleHealth(), descriptor.maxHealth)
            if appearance.findComponentByType(WTGunReloadedComponent) is None:
                appearance.createComponent(WTGunReloadedComponent)
            if appearance.findComponentByType(BossTag) is None:
                appearance.createComponent(BossTag)
        return

    def __onAvatarReady(self):
        ammoCtrl = self.guiSessionProvider.shared.ammo
        ammoCtrl.onGunReloadTimeSet += self.__vehicleGunReloadTimeSet

    def __vehicleGunReloadTimeSet(self, currShellCD, state, skipAutoLoader):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None:
            return
        else:
            if state.isReloading():
                vehicle.appearance.removeComponentByType(WTGunReloadedComponent)
            elif vehicle.appearance.findComponentByType(WTGunReloadedComponent) is None:
                vehicle.appearance.createComponent(WTGunReloadedComponent)
            return
