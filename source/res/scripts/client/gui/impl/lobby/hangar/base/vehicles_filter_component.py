# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/vehicles_filter_component.py
from __future__ import absolute_import
import typing
import Event
from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
VEHICLE_UPDATES = (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE)

class VehiclesFilterComponent(IVehicleFilter):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, baseCriteria):
        self._baseCriteria = baseCriteria
        self.onChanged = Event.Event()
        self.onDiff = Event.Event()
        self._vehicles = {}

    @property
    def vehicles(self):
        return self._vehicles

    def initialize(self):
        self._vehicles = self.__createVehicleDict()
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self.__notify()

    def destroy(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.onChanged.clear()
        self.onDiff.clear()

    def __onCacheResync(self, reason, diff):
        if reason not in VEHICLE_UPDATES:
            return
        fullUpdate = reason is CACHE_SYNC_REASON.SHOP_RESYNC
        if GUI_ITEM_TYPE.VEHICLE not in diff and not fullUpdate:
            return
        self._vehicles = self.__createVehicleDict()
        self.onDiff(self.vehicles if fullUpdate else diff[GUI_ITEM_TYPE.VEHICLE])
        if not fullUpdate:
            self.__notify()

    def __createVehicleDict(self):
        return self._itemsCache.items.getVehicles(self._baseCriteria)

    def __notify(self):
        self.onChanged(self._vehicles)
