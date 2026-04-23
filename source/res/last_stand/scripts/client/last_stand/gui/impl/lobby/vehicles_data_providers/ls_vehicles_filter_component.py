# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/vehicles_data_providers/ls_vehicles_filter_component.py
from __future__ import absolute_import
import typing
import Event
from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from last_stand.skeletons.ls_controller import ILSController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
_VEHICLE_UPDATES = (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE)
ALL_MODE_VEHICLE_CRITERIA = ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP

class LSVehiclesFilterComponent(IVehicleFilter):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lsCtrl = dependency.descriptor(ILSController)

    def __init__(self, onlySuitableVehicles=True):
        self.onDiff = Event.Event()
        self.__vehicles = {}
        self.__criteria = self._lsCtrl.getVehiclesCriteria() if onlySuitableVehicles else ALL_MODE_VEHICLE_CRITERIA

    @property
    def criteria(self):
        return self.__criteria

    @property
    def vehicles(self):
        return self.__vehicles

    def initialize(self):
        self.__createVehiclesDict()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    def destroy(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.onDiff.clear()

    def __onCacheResync(self, reason, diff):
        if reason not in _VEHICLE_UPDATES:
            return
        fullUpdate = reason is CACHE_SYNC_REASON.SHOP_RESYNC
        if GUI_ITEM_TYPE.VEHICLE not in diff and not fullUpdate:
            return
        self.__createVehiclesDict()
        self.onDiff(self.vehicles if fullUpdate else diff[GUI_ITEM_TYPE.VEHICLE])

    def __createVehiclesDict(self):
        self.__vehicles = self._lsCtrl.getSuitableVehicles(self.__criteria)
