# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleBattleUpgrades.py
import BigWorld
from wotdecorators import noexcept

class HWVehicleBattleUpgrades(BigWorld.DynamicScriptComponent):

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
        if vehicle.isMyVehicle:
            BigWorld.player().waitOnEnterWorld.startWait(vehicleID)
        vehicle.respawnVehicle(vehicleID, newVehCompactDescr, newVehOutfitCompactDescr)
        return
