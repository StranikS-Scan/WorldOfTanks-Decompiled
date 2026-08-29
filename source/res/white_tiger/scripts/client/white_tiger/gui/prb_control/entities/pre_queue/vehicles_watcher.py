# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/vehicles_watcher.py
import typing
from helpers import dependency
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.shared.gui_items.Vehicle import Vehicle
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWhiteTigerController
from white_tiger.gui.gui_constants import VEHICLE_STATE
from wt_settings import g_wt_config

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
        if g_wt_config.hasTokensByName('wtevent:boss1'):
            self.__clearTicketsShortageState()
        else:
            self.__setTicketsShortageState()

    def __getTicketsShortageVehicles(self):
        return [ data.vehicle for data in g_wt_config.getBossVehiclesData().itervalues() ]

    def __setTicketsShortageState(self):
        if g_wt_config.hasTokensByName('wtevent:boss1'):
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
