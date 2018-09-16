# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from helpers import dependency

class EpicVehiclesWatcher(object):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def start(self):
        self.__setUnsuitableState()
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryChanged})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__clearUnsuitableState()

    def __getUnsuitableVehicles(self):
        config = self.lobbyContext.getServerSettings().epicBattles
        vehLevels = list(set(range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)) - set(config.validVehicleLevels))
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        return chain(vehs)

    def __setUnsuitableState(self):
        vehicles = self.__getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __clearUnsuitableState(self):
        vehicles = self.__getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __onInventoryChanged(self, diff):
        self.__setUnsuitableState()
