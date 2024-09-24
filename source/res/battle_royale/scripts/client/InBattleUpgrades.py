# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/InBattleUpgrades.py
import BigWorld
from aih_constants import CTRL_MODE_NAME
from wotdecorators import noexcept

class UpgradeInProgressComponent(object):
    pass


class InBattleUpgrades(BigWorld.DynamicScriptComponent):

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        pass

    def upgradeVehicle(self, indCD):
        self.cell.upgradeVehicle(indCD)

    def onVehicleUpgraded(self, newVehCompactDescr, newVehOutfitCompactDescr):
        vehicle = self.entity
        vehicle.isUpgrading = True
        if vehicle.entityGameObject.findComponentByType(UpgradeInProgressComponent):
            vehicle.entityGameObject.removeComponentByType(UpgradeInProgressComponent)
        vehicle.entityGameObject.createComponent(UpgradeInProgressComponent)
        self.__onVehicleUpgraded(vehicle, newVehCompactDescr, newVehOutfitCompactDescr)

        def removeUpgrageInProgressComponent():
            if vehicle and vehicle.entityGameObject:
                vehicle.entityGameObject.removeComponentByType(UpgradeInProgressComponent)

        BigWorld.callback(0, removeUpgrageInProgressComponent)
        vehicle.isUpgrading = False

    @noexcept
    def __onVehicleUpgraded(self, vehicle, newVehCompactDescr, newVehOutfitCompactDescr):
        vehicleID = vehicle.id
        if vehicle.isPlayerVehicle:
            inputHandler = BigWorld.player().inputHandler
            arcadeState = None
            if inputHandler.ctrlModeName == CTRL_MODE_NAME.ARCADE:
                arcadeState = inputHandler.ctrl.camera.cloneState()
            inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE, initialVehicleMatrix=vehicle.matrix, arcadeState=arcadeState)
        progressionCtrl = vehicle.guiSessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.vehicleVisualChangingStarted(vehicleID)
        vehicle.respawnVehicle(vehicleID, newVehCompactDescr, newVehOutfitCompactDescr)
        return

    def testClientMethod(self):
        pass

    def set_upgradeReadinessTime(self, prev):
        vehicle = self.entity
        ctrl = vehicle.guiSessionProvider.dynamic.progression
        if ctrl is not None and vehicle.id == BigWorld.player().playerVehicleID:
            ctrl.updateVehicleReadinessTime(self.upgradeReadinessTime.totalTime, self.upgradeReadinessTime.reason)
        return


def onBattleRoyalePrerequisites(vehicle, oldTypeDescriptor, forceReloading):
    if 'battle_royale' not in vehicle.typeDescriptor.type.tags:
        return forceReloading
    if not oldTypeDescriptor:
        return True
    for moduleName in ('gun', 'turret', 'chassis'):
        oldModule = getattr(oldTypeDescriptor, moduleName)
        newModule = getattr(vehicle.typeDescriptor, moduleName)
        if oldModule.id != newModule.id:
            forceReloading = True
            if moduleName == 'gun' and vehicle.id == BigWorld.player().getObservedVehicleID():
                player = BigWorld.player()
                if player.isObserver():
                    vehicle.guiSessionProvider.shared.ammo.clearAmmo()
                    vehicle.guiSessionProvider.shared.ammo.setGunSettings(newModule)
                player.gunRotator.switchActiveGun([0])

    if forceReloading:
        vehicle.isForceReloading = True
    return forceReloading
