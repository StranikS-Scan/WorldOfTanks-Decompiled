# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/training/legacy/vehicles_watcher.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from helpers import dependency

class TrainingVehiclesWatcher(object):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def start(self):
        self._setState(True)
        g_clientUpdateManager.addCallbacks({'inventory': self._onInventoryUpdate})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._setState(False)

    def _getUnsuitableVehicles(self):
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE)

    def _onInventoryUpdate(self, diff):
        self._setState(True)

    def _setState(self, unsuitable):
        vehicles = self._getUnsuitableVehicles()
        for vehicle in vehicles.itervalues():
            if unsuitable:
                vehicle.setCustomState(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
            vehicle.clearCustomState()

        if vehicles:
            g_prbCtrlEvents.onVehicleClientStateChanged(vehicles.keys())
