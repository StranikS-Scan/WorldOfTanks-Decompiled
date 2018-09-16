# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_shadow_manager.py
import BigWorld
from svarog_script.py_component import Component

class VehicleShadowManager(Component):

    def __init__(self, playerTargetChangeEvent=None):
        super(VehicleShadowManager, self).__init__()
        self.__vehicleID = None
        self.__compoundModel = None
        self.__playerTargetChangeEvent = playerTargetChangeEvent
        return

    def isVehicleAvailable(self, player):
        return player.getVehicleAttached() is not None

    def changePlayerTarget(self, isStatic):
        player = BigWorld.player()
        vehicle = player.getVehicleAttached()
        if self.isVehicleAvailable(player):
            self.__vehicleID = vehicle.id
            BigWorld.setPlayerTarget(vehicle.appearance.compoundModel)
        else:
            BigWorld.setPlayerTarget(None)
        return

    def activate(self):
        if self.__playerTargetChangeEvent:
            self.__playerTargetChangeEvent += self.changePlayerTarget

    def deactivate(self):
        if self.__playerTargetChangeEvent:
            self.__playerTargetChangeEvent -= self.changePlayerTarget
        self.unregisterCompoundModel(self.__compoundModel)
        if BigWorld.player().getVehicleAttached().id == self.__vehicleID:
            BigWorld.setPlayerTarget(None)
        return

    def updatePlayerTarget(self, compoundModel):
        BigWorld.setPlayerTarget(compoundModel)

    def registerCompoundModel(self, compoundModel):
        self.__compoundModel = compoundModel
        BigWorld.registerShadowCaster(compoundModel)

    def unregisterCompoundModel(self, compoundModel):
        BigWorld.unregisterShadowCaster(compoundModel)

    def destroy(self):
        pass
