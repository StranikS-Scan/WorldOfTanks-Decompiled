# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/vehicles_watcher.py
import typing
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TAGS as _TAGS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IEventBattlesController

class EventBattlesVehiclesWatcher(BaseVehiclesWatcher):
    gameEventCtrl = dependency.descriptor(IEventBattlesController)
    itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        self.__setTicketsShortageState()
        super(EventBattlesVehiclesWatcher, self).start()

    def stop(self):
        self.__clearTicketsShortageState()
        super(EventBattlesVehiclesWatcher, self).stop()

    def _update(self, *_):
        super(EventBattlesVehiclesWatcher, self)._update()
        if self.gameEventCtrl.hasEnoughTickets():
            self.__clearTicketsShortageState()
        else:
            self.__setTicketsShortageState()

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_NO_TAG(_TAGS.EVENT_VEHS)).values()
        return vehs

    def __getTicketsShortageVehicles(self):
        vehs = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({_TAGS.EVENT_BOSS}) | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({_TAGS.EVENT_SPECIAL_BOSS})).values()
        return vehs

    def __setTicketsShortageState(self):
        if self.gameEventCtrl.hasEnoughTickets():
            return
        vehicles = self.__getTicketsShortageVehicles()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.TICKETS_SHORTAGE)
            self._vehicleCdsWithChangedState.add(vehicle.intCD)

    def __clearTicketsShortageState(self):
        vehicles = self.__getTicketsShortageVehicles()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            self._vehicleCdsWithChangedState.add(vehicle.intCD)
