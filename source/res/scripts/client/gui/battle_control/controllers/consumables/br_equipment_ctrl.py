# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/br_equipment_ctrl.py
import logging
import BigWorld
from helpers import dependency
from items import vehicles
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.battle_royale.constants import AmmoTypes
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

def createEquipmentById(equipmentId):
    return vehicles.g_cache.equipments()[equipmentId]


class SteelHunterEquipmentController(equipment_ctrl.EquipmentsController):
    __slots__ = ()
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def startControl(self, *args, **kwargs):
        super(SteelHunterEquipmentController, self).startControl()
        avatar = BigWorld.player()
        playerVehicle = avatar.vehicle
        if playerVehicle is not None:
            self.__applyEmptyItems()
        else:
            avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        return

    def stopControl(self):
        avatar = BigWorld.player()
        if avatar:
            avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        super(SteelHunterEquipmentController, self).stopControl()

    def clear(self, leave=True):
        super(SteelHunterEquipmentController, self).clear(leave)
        if not leave:
            self.__applyEmptyItems()

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            avatar_getter.getVehicleTypeDescriptor()
            BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
            self.__applyEmptyItems()

    def __applyEmptyItems(self):
        vehicleDescriptor = None
        observedVehicleId = BigWorld.player().observedVehicleID
        if observedVehicleId:
            vehicle = BigWorld.entities.get(observedVehicleId)
            if vehicle:
                vehicleDescriptor = vehicle.typeDescriptor
        if vehicleDescriptor is None:
            vehicleDescriptor = avatar_getter.getVehicleTypeDescriptor()
        if vehicleDescriptor and 'observer' in vehicleDescriptor.type.tags:
            return
        else:
            vehiclesSlotsConfig = self.__lobbyCtx.getServerSettings().battleRoyale.vehiclesSlotsConfig
            vehicleDescriptorName = None
            if vehicleDescriptor:
                vehicleDescriptorName = vehicleDescriptor.name
                vehConfig = vehiclesSlotsConfig.get(vehicleDescriptorName)
                if vehConfig:
                    for chargeName in AmmoTypes.CHARGES:
                        equipmentID = vehConfig.get(chargeName)
                        if equipmentID:
                            equipment = createEquipmentById(equipmentID)
                            self.setEquipment(equipment.compactDescr, 0, 0, 0, 0)

                    return
            _logger.error('Vehicle config has not been found! %s, config: %s', vehicleDescriptorName, vehiclesSlotsConfig)
            return


class SteelHunterReplayEquipmentController(equipment_ctrl.EquipmentsReplayPlayer, SteelHunterEquipmentController):
    __slots__ = ()
