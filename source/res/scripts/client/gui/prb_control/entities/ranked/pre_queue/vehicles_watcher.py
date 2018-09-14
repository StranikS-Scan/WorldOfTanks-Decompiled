# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/vehicles_watcher.py
from itertools import chain
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from helpers import dependency

class RankedVehiclesWatcher(object):
    """
    Ranked vehicles watcher class: listens for proper events
    and updates the states of vehicles selected
    """
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def start(self):
        """
        Starts listening for events
        """
        self.__setUnsuitableState()
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryChanged})

    def stop(self):
        """
        Stops listening for events
        """
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__clearUnsuitableState()

    def __getUnsuitableVehicles(self):
        """
        Gets all unsupported vehicles
        """
        config = self.lobbyContext.getServerSettings().rankedBattles
        vehLevels = range(MIN_VEHICLE_LEVEL, config.minLevel) + range(config.maxLevel + 1, MAX_VEHICLE_LEVEL + 1)
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(vehLevels)).itervalues()
        eventVehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE).itervalues()
        return chain(vehs, eventVehs)

    def __setUnsuitableState(self):
        """
        Sets to all unsupported vehicles custom state
        """
        vehicles = self.__getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __clearUnsuitableState(self):
        """
        Unsets to all unsupported vehicles custom state
        """
        vehicles = self.__getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __onInventoryChanged(self, diff):
        """
        Listener for inventory update envent
        Args:
            diff: inventory update diff
        """
        self.__setUnsuitableState()
