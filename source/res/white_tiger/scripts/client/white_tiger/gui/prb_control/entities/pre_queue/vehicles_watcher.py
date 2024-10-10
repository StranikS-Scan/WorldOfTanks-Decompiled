# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/vehicles_watcher.py
import typing
from helpers import dependency
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.gui_constants import VEHICLE_TAGS, VEHICLE_STATE

class WhiteTigerBattlesVehiclesWatcher(BaseVehiclesWatcher):
    __wtController = dependency.descriptor(IWhiteTigerController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self):
        self.__setTicketsShortageState()
        super(WhiteTigerBattlesVehiclesWatcher, self).start()

    def stop(self):
        self.__clearTicketsShortageState()
        super(WhiteTigerBattlesVehiclesWatcher, self).stop()

    def _update(self, *_):
        super(WhiteTigerBattlesVehiclesWatcher, self)._update()
        if self.__wtController.hasEnoughTickets():
            self.__clearTicketsShortageState()
        else:
            self.__setTicketsShortageState()

    def _getUnsuitableVehicles(self, onClear=False):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_NO_TAG(VEHICLE_TAGS.WT_VEHICLES)).values()
        return vehs

    def __getTicketsShortageVehicles(self):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({VEHICLE_TAGS.WT_BOSS}) | REQ_CRITERIA.VEHICLE.HAS_NO_TAG({VEHICLE_TAGS.WT_SPECIAL_BOSS})).values()
        return vehs

    def __setTicketsShortageState(self):
        if self.__wtController.hasEnoughTickets():
            return
        vehicles = self.__getTicketsShortageVehicles()
        for vehicle in vehicles:
            vehicle.setCustomState(VEHICLE_STATE.WT_TICKETS_SHORTAGE)
            self._vehicleCdsWithChangedState.add(vehicle.intCD)

    def __clearTicketsShortageState(self):
        vehicles = self.__getTicketsShortageVehicles()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            self._vehicleCdsWithChangedState.add(vehicle.intCD)
