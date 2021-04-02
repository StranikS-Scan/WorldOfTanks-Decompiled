# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/InBattleUpgrades.py
import BigWorld
from debug_utils import LOG_NOTE
from wotdecorators import noexcept

class InBattleUpgrades(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(InBattleUpgrades, self).__init__()
        if self.entity.guiSessionProvider.arenaVisitor.bonus.hasInBattleUpgrade():
            self.entity.autoUpgradeOnChangeDescriptor = False

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        pass

    def upgradeVehicle(self, indCD):
        self.cell.upgradeVehicle(indCD)

    def onVehicleUpgraded(self, newVehCompactDescr, newVehOutfitCompactDescr):
        vehicle = self.entity
        vehicle.isUpgrading = True
        self.__onVehicleUpgraded(vehicle, newVehCompactDescr, newVehOutfitCompactDescr)
        vehicle.isUpgrading = False

    @noexcept
    def __onVehicleUpgraded(self, vehicle, newVehCompactDescr, newVehOutfitCompactDescr):
        vehicleID = vehicle.id
        if vehicle.isPlayerVehicle:
            inputHandler = BigWorld.player().inputHandler
            inputHandler.onControlModeChanged('arcade')
        progressionCtrl = vehicle.guiSessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.vehicleVisualChangingStarted(vehicleID)
        vehicle.respawnVehicle(vehicleID, newVehCompactDescr, newVehOutfitCompactDescr)
        return

    def testClientMethod(self):
        pass

    def set_upgradeReadinessTime(self, prev):
        LOG_NOTE('Vehicle upgrade readiness time changed')
        vehicle = self.entity
        ctrl = vehicle.guiSessionProvider.dynamic.progression
        if ctrl is not None and vehicle.id == BigWorld.player().playerVehicleID:
            ctrl.updateVehicleReadinessTime(self.upgradeReadinessTime.time, self.upgradeReadinessTime.reason)
        return


def onBattleRoyalePrerequisites(vehicle, oldTypeDescriptor):
    if 'battle_royale' not in vehicle.typeDescriptor.type.tags:
        return False
    if not oldTypeDescriptor:
        return True
    forceReloding = False
    for moduleName in ('gun', 'turret', 'chassis'):
        oldModule = getattr(oldTypeDescriptor, moduleName)
        newModule = getattr(vehicle.typeDescriptor, moduleName)
        if oldModule.id != newModule.id:
            forceReloding = True
            vehicle.isForceReloading = True
            if moduleName == 'gun' and vehicle.id == BigWorld.player().getObservedVehicleID():
                player = BigWorld.player()
                if player.isObserver():
                    player.reloadCurrentVehicleGunSettings()
                    vehicle.guiSessionProvider.shared.ammo.clearAmmo()
                player.gunRotator.switchActiveGun(0)

    return forceReloding
