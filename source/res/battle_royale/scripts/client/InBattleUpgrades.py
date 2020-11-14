# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/InBattleUpgrades.py
import BigWorld
from debug_utils import LOG_NOTE

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
        if vehicle.isPlayerVehicle:
            inputHandler = BigWorld.player().inputHandler
            inputHandler.onControlModeChanged('arcade')
        progressionCtrl = vehicle.guiSessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.vehicleVisualChangingStarted(vehicle.id)
        vehicle.respawnVehicle(vehicle.id, newVehCompactDescr, newVehOutfitCompactDescr)
        vehicle.isUpgrading = False
        return

    def set_upgradeReadinessTime(self, prev):
        LOG_NOTE('Vehicle upgrade readiness time changed')
        vehicle = self.entity
        ctrl = vehicle.guiSessionProvider.dynamic.progression
        if ctrl is not None and vehicle.id == BigWorld.player().playerVehicleID:
            ctrl.updateVehicleReadinessTime(self.upgradeReadinessTime.time, self.upgradeReadinessTime.reason)
        return
