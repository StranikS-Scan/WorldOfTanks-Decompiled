# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/vehicle_specs/rts_vehicle_builder.py
import typing
import logging
from helpers import dependency
from items import vehicles
from vehicle_conf_customizer import customizer
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from gui.shared.gui_items.Vehicle import Vehicle, sortCrew
_logger = logging.getLogger(__name__)

class RtsVehicleBuilder(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def createVehicle(self, vehicleIntCd):
        if vehicleIntCd is None:
            return
        else:
            serverSettings = self.lobbyContext.getServerSettings()
            cfg = serverSettings.getRTSVehiclesCustomizationConfig().asDict()
            vehCD = vehicles.makeCompactDescrBy(intCD=vehicleIntCd)
            vehInfo = customizer.buildCustomizedVehicle(cfg, vehCD, 0, _logger)
            vehicle = Vehicle(vehInfo['vehCompDescr'])
            if not vehicle.isSupply:
                self._updateCrew(vehicle, vehInfo['vehCrew'])
                self._updateConsumables(vehicle, vehInfo['vehiclePresetData']['consumableSlots'])
                self._updateAmmo(vehicle, vehInfo['vehAmmo'])
            return vehicle

    def _updateCrew(self, vehicle, crew):
        crewItems = list()
        crewRoles = vehicle.descriptor.type.crewRoles
        for idx, tankmanCd in enumerate(crew):
            tankman = vehicle.itemsFactory.createTankman(strCompactDescr=tankmanCd, inventoryID=-1, vehicle=vehicle, proxy=None)
            crewItems.append((idx, tankman))

        vehicle.crew = sortCrew(crewItems, crewRoles)
        return

    def _getConsumableByName(self, name):
        cd = vehicles.g_cache.equipments()[vehicles.g_cache.equipmentIDs().get(name)].compactDescr
        return self.itemsCache.items.getItemByCD(cd)

    def _updateConsumables(self, vehicle, consumables):
        installedComsumables = [ self._getConsumableByName(consumableName) for consumableName in consumables ]
        vehicle.consumables.setInstalled(*installedComsumables)

    def _updateAmmo(self, vehicle, ammo):
        ammoListSize = vehicle.shells.getShellsCount() * 2
        shells = [ self.itemsFactory.createShell(shellCD, count, None, False) for shellCD, count in zip(ammo[:ammoListSize:2], ammo[1:ammoListSize + 1:2]) ]
        vehicle.shells.setInstalled(*shells)
        return
