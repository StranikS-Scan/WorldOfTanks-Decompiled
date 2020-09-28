# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/vehicles_watcher.py
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.wt_event.wt_event_helpers import hasEnoughTickets, isBossAndNotSpecialBossVehicle
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class EventBattlesVehiclesWatcher(BaseVehiclesWatcher):
    itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        self.__setTicketsShortageState()
        super(EventBattlesVehiclesWatcher, self).start()

    def stop(self):
        super(EventBattlesVehiclesWatcher, self).stop()
        self.__clearTicketsShortageState()

    def _update(self, *_):
        super(EventBattlesVehiclesWatcher, self)._update(self)
        self.__updateTicketsShortageState()

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE).values()
        return vehs

    def _getTicketsShortageVehicles(self):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.CUSTOM(isBossAndNotSpecialBossVehicle)).values()
        return vehs

    def __setTicketsShortageState(self):
        if hasEnoughTickets():
            return
        vehicles = self._getTicketsShortageVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.EVENT_TICKETS_SHORTAGE)
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __clearTicketsShortageState(self):
        vehicles = self._getTicketsShortageVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __updateTicketsShortageState(self):
        if hasEnoughTickets():
            self.__clearTicketsShortageState()
        else:
            self.__setTicketsShortageState()
