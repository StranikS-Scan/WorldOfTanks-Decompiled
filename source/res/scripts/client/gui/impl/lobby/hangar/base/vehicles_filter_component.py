# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/vehicles_filter_component.py
from __future__ import absolute_import
import typing
from future.utils import viewkeys
import Event
from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
_VEHICLE_UPDATES = (CACHE_SYNC_REASON.SHOP_RESYNC, CACHE_SYNC_REASON.DOSSIER_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE)

class VehiclesFilterComponent(IVehicleFilter):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, criteria):
        self.__criteria = criteria
        self.onDiff = Event.Event()
        self._vehicles = {}

    @property
    def criteria(self):
        return self.__criteria

    @property
    def vehicles(self):
        return self._vehicles

    def initialize(self):
        self.__createVehiclesDict()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    def destroy(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.onDiff.clear()

    def _setCriteria(self, criteria):
        oldVehiclesCDs = set(self._vehicles)
        self.__criteria = criteria
        self.__createVehiclesDict()
        self.onDiff(oldVehiclesCDs ^ viewkeys(self._vehicles))

    def __onCacheResync(self, reason, diff):
        if reason not in _VEHICLE_UPDATES:
            return
        fullUpdate = reason is CACHE_SYNC_REASON.SHOP_RESYNC
        if GUI_ITEM_TYPE.VEHICLE not in diff and not fullUpdate:
            return
        self.__createVehiclesDict()
        self.onDiff(self.vehicles if fullUpdate else diff[GUI_ITEM_TYPE.VEHICLE])

    def __createVehiclesDict(self):
        self._vehicles = self._itemsCache.items.getVehicles(self.__criteria)
