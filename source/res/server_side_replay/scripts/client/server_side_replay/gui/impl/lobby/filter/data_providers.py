# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/filter/data_providers.py
from typing import Optional
from Event import Event
from constants import MAX_VEHICLE_LEVEL
from state import ToggleGroupType
from ..sort_helpers import SortHeap
from ..utils import getRentCriteria
from . import GRADE_PREMIUM, VEHICLE_LOCATION_IN_HANGAR
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class _ItemCallProxy(object):

    def __init__(self, item):
        self._item = item

    def __getattr__(self, name):
        attr = getattr(self._item, name)
        return self._proxy(attr) if callable(attr) else attr

    def _proxy(self, method):

        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        return wrapper


class FilterableItemsDataProvider(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, state):
        self.onDataChanged = Event()
        self._state = state
        self.__initialItemsCount = None
        self.__itemsCount = None
        self.__vehSortHeap = None
        self.__items = None
        return

    def __getitem__(self, item):
        return self.items()[item]

    def items(self):
        if self.__items is None:
            self.__items = self.__vehSortHeap.getSortedList() if self.__vehSortHeap else []
        return self.__items

    @property
    def initialItemsCount(self):
        if self.__initialItemsCount is None:
            self.__initialItemsCount = len(self._getInitialItems())
        return self.__initialItemsCount

    @property
    def itemsCount(self):
        if self.__itemsCount is None:
            self.__itemsCount = len(self.items())
        return self.__itemsCount

    def reinit(self):
        self.__items = None
        self.__itemsCount = None
        self.__initialItemsCount = None
        return

    def update(self):
        filteredItems = self._getFilteredItems()
        self._sort(filteredItems)
        self.__items = None
        self.__itemsCount = None
        self.onDataChanged()
        return

    def updateRoot(self, item):
        if self.__vehSortHeap:
            self.__vehSortHeap.updateRoot(item=item, keys=self._getSortKeyCriteria(), criteria=self._getConditionSortCriteria())

    def _getInitialFilterCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getFilterCriteria(self):
        criteria = self._getInitialFilterCriteria()
        for extraCriteria in self._getFiltersList():
            if extraCriteria:
                criteria |= extraCriteria

        return criteria

    def _getSortCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getInitialItems(self):
        criteria = self._getInitialFilterCriteria()
        return self._itemsGetter(criteria, initial=True)

    def _getFilteredItems(self):
        criteria = self._getFilterCriteria()
        return self._itemsGetter(criteria)

    def _getFiltersList(self):
        raise NotImplementedError

    def _sort(self, filteredItems):
        self.__vehSortHeap = SortHeap(items=filteredItems.values() if hasattr(filteredItems, 'values') else filteredItems, keys=self._getSortKeyCriteria(), criteria=self._getConditionSortCriteria())

    def _getSortKeyCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getConditionSortCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _itemsGetter(self, criteria, initial=False):
        raise NotImplementedError


class CompoundDataProvider(object):

    def __init__(self, **dataProviders):
        self.onDataChanged = Event()
        msg = 'All data providers must be derived from FilterableItemsDataProvider'
        self.__dataProviders = dataProviders
        self.__updatingCount = 0

    def __getitem__(self, item):
        return self.__dataProviders[item]

    def __len__(self):
        return len(self.__dataProviders)

    def reinit(self, *args, **kwargs):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.reinit(*args, **kwargs)

    def update(self):
        self.__updatingCount += len(self)
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.update()

    def subscribe(self):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.onDataChanged += self._onProviderDataChanged

    def unsubscribe(self):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.onDataChanged -= self._onProviderDataChanged

    @property
    def itemsCount(self):
        return sum((provider.itemsCount for provider in self.__dataProviders.itervalues()))

    @property
    def initialItemsCount(self):
        return sum((provider.initialItemsCount for provider in self.__dataProviders.itervalues()))

    def _onProviderDataChanged(self):
        self.__updatingCount -= 1
        if self.__updatingCount == 0:
            self.onDataChanged()


class VehiclesDataProvider(FilterableItemsDataProvider):

    def __init__(self, state, tankman=None, vehicle=None):
        self.__tankman = tankman
        self.__vehicle = vehicle
        super(VehiclesDataProvider, self).__init__(state)

    def items(self):
        items = super(VehiclesDataProvider, self).items()
        if items and self.__vehicle and self.__vehicle not in items:
            items = [self.__vehicle] + items
        return items

    @property
    def tankman(self):
        return self.__tankman

    @property
    def vehicle(self):
        return self.__vehicle

    def reinit(self, tankman=None, vehicle=None):
        self.__tankman = tankman
        self.__vehicle = vehicle
        super(VehiclesDataProvider, self).reinit()

    def updateRoot(self, vehicle):
        self.__vehicle = vehicle
        super(VehiclesDataProvider, self).updateRoot(vehicle)

    def _getFiltersList(self):
        return [self._getFilterByVehicleTypeCriteria(),
         self._getFilterByVehicleTierCriteria(),
         self._getFilterByVehicleGradeCriteria(),
         self._getFilterByVehicleLocationCriteria(),
         self._getSearchCriteria()]

    def _getInitialFilterCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~getRentCriteria()
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET
        criteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
        criteria |= REQ_CRITERIA.VEHICLE.ACTIVE_OR_MAIN_IN_NATION_GROUP
        if self.tankman:
            criteria |= REQ_CRITERIA.VEHICLE.HAS_ROLES(self.tankman.descriptor.nativeRoles)
            criteria |= REQ_CRITERIA.NATIONS([self.tankman.nationID])
        return criteria

    def _getFilterByVehicleTypeCriteria(self):
        vehicleTypes = self._state[ToggleGroupType.VEHICLETYPE.value]
        return REQ_CRITERIA.VEHICLE.CLASSES(tuple(vehicleTypes)) if vehicleTypes else None

    def _getFilterByVehicleTierCriteria(self):
        vehicleTiers = self._state[ToggleGroupType.VEHICLETIER.value]
        vehicleTiers = {int(t) for t in vehicleTiers}
        return REQ_CRITERIA.VEHICLE.LEVELS(vehicleTiers) if vehicleTiers else None

    def _getFilterByVehicleGradeCriteria(self):
        vehicleGrades = self._state[ToggleGroupType.VEHICLEGRADE.value]
        criteria = REQ_CRITERIA.VEHICLE.PREMIUM
        return criteria if GRADE_PREMIUM in vehicleGrades else ~criteria

    def _getFilterByVehicleLocationCriteria(self):
        vehicleLocations = self._state[ToggleGroupType.LOCATION.value]
        return REQ_CRITERIA.INVENTORY if VEHICLE_LOCATION_IN_HANGAR in vehicleLocations else None

    def _getSearchCriteria(self):
        return REQ_CRITERIA.VEHICLE.NAME_VEHICLE_WITH_SHORT(self._state.searchString.lower()) if self._state.searchString else None

    def _getSortKeyCriteria(self):
        criteria = REQ_CRITERIA.CUSTOM(lambda item: VEHICLE_TYPES_ORDER_INDICES[item.type])
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: MAX_VEHICLE_LEVEL - item.level)
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: item.searchableUserName)
        return criteria

    def _getConditionSortCriteria(self):
        criteria = REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD((self.vehicle.compactDescr,))
        criteria |= REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.INVENTORY
        return criteria

    def _itemsGetter(self, criteria, initial=False):
        return self.itemsCache.items.getVehicles(criteria)
