# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/vehicles_watcher.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.gui_items.Vehicle import Vehicle

class BaseVehiclesWatcher(object):

    def start(self):
        self.__setUnsuitableState()
        g_clientUpdateManager.addCallbacks({'inventory': self._update,
         'eventsData': self._update})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__clearUnsuitableState()

    def _getUnsuitableVehicles(self, onClear=False):
        raise NotImplementedError

    def _update(self, *_):
        self.__setUnsuitableState()

    def __setUnsuitableState(self):
        vehicles = self._getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __clearUnsuitableState(self):
        vehicles = self._getUnsuitableVehicles(True)
        intCDs = set()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)
