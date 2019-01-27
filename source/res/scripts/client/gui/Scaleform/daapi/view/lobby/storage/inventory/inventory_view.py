# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_view.py
import copy
from account_helpers import AccountSettings
from adisp import process
from gui import DialogsInterface
from gui import GUI_NATIONS_ORDER_INDICES
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.category_view import InventoryCategoryView
from gui.Scaleform.daapi.view.meta.ItemsWithVehicleFilterTabViewMeta import ItemsWithVehicleFilterTabViewMeta
from gui.Scaleform.daapi.view.meta.StorageCategoryStorageViewMeta import StorageCategoryStorageViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
VERSION = 1
_TABS_DATA = ({'id': STORAGE_CONSTANTS.INVENTORY_TAB_ALL,
  'label': STORAGE.STORAGE_TABS_ALL,
  'linkage': STORAGE_CONSTANTS.STORAGE_REGULAR_ITEMS_TAB,
  'selected': True},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT,
  'label': STORAGE.STORAGE_TABS_EQUIPMENT,
  'linkage': STORAGE_CONSTANTS.STORAGE_REGULAR_ITEMS_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE,
  'label': STORAGE.STORAGE_TABS_CONSUMABLE,
  'linkage': STORAGE_CONSTANTS.STORAGE_REGULAR_ITEMS_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_MODULES,
  'label': STORAGE.STORAGE_TABS_MODULES,
  'linkage': STORAGE_CONSTANTS.STORAGE_MODULES_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS,
  'label': STORAGE.STORAGE_TABS_SHELLS,
  'linkage': STORAGE_CONSTANTS.STORAGE_SHELLS_TAB})
_TABS_ITEM_TYPES = {STORAGE_CONSTANTS.INVENTORY_TAB_ALL: GUI_ITEM_TYPE.VEHICLE_COMPONENTS,
 STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT: GUI_ITEM_TYPE.OPTIONALDEVICE,
 STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE: (GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.BATTLE_BOOSTER),
 STORAGE_CONSTANTS.INVENTORY_TAB_MODULES: GUI_ITEM_TYPE.VEHICLE_MODULES,
 STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS: GUI_ITEM_TYPE.SHELL}
_TABS_SORT_ORDER = dict(((n, idx) for idx, n in enumerate((GUI_ITEM_TYPE.OPTIONALDEVICE,
 GUI_ITEM_TYPE.EQUIPMENT,
 GUI_ITEM_TYPE.BATTLE_BOOSTER,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.RADIO,
 GUI_ITEM_TYPE.SHELL))))

def _defaultInGroupComparator(a, b):
    return cmp(storage_helpers.getStorageModuleName(a), storage_helpers.getStorageModuleName(b))


def _optionalDevicesComparator(a, b):
    return (1 if a.isDeluxe() else 0) - (1 if b.isDeluxe() else 0) or _defaultInGroupComparator(a, b)


def _shellsComparator(a, b):
    return cmp(a.descriptor.caliber, b.descriptor.caliber) or _defaultInGroupComparator(a, b)


def _gunsComparator(a, b):
    return cmp(a.descriptor.level, b.descriptor.level) or cmp(a.descriptor.shots[0].shell.caliber, b.descriptor.shots[0].shell.caliber) or _defaultInGroupComparator(a, b)


_IN_GROUP_COMPARATOR = {GUI_ITEM_TYPE.OPTIONALDEVICE: _optionalDevicesComparator,
 GUI_ITEM_TYPE.EQUIPMENT: _defaultInGroupComparator,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: _defaultInGroupComparator,
 GUI_ITEM_TYPE.TURRET: _defaultInGroupComparator,
 GUI_ITEM_TYPE.ENGINE: _defaultInGroupComparator,
 GUI_ITEM_TYPE.GUN: _gunsComparator,
 GUI_ITEM_TYPE.RADIO: _defaultInGroupComparator,
 GUI_ITEM_TYPE.CHASSIS: _defaultInGroupComparator,
 GUI_ITEM_TYPE.SHELL: _shellsComparator}

class InventoryCategoryStorageView(StorageCategoryStorageViewMeta):

    def __init__(self):
        super(InventoryCategoryStorageView, self).__init__()
        self.__currentTabId = STORAGE_CONSTANTS.INVENTORY_TAB_ALL
        self.__views = {}

    def onOpenTab(self, tabId):
        self.__currentTabId = tabId
        if self.__currentTabId in self.__views:
            self.__views[self.__currentTabId].setTabId(self.__currentTabId)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(InventoryCategoryStorageView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == STORAGE_CONSTANTS.STORAGE_REGULAR_ITEMS_TAB:
            self.__views[STORAGE_CONSTANTS.INVENTORY_TAB_ALL] = viewPy
            self.__views[STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT] = viewPy
            self.__views[STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE] = viewPy
        if alias not in (STORAGE_CONSTANTS.STORAGE_MODULES_TAB, STORAGE_CONSTANTS.STORAGE_SHELLS_TAB):
            viewPy.setTabId(self.__currentTabId)

    def _populate(self):
        super(InventoryCategoryStorageView, self)._populate()
        self.as_setTabsDataS(_TABS_DATA)


class RegularInventoryCategoryTabView(InventoryCategoryView):

    def __init__(self):
        super(RegularInventoryCategoryTabView, self).__init__()
        self._currentTabId = STORAGE_CONSTANTS.INVENTORY_TAB_ALL

    def _populate(self):
        super(RegularInventoryCategoryTabView, self)._populate()
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._buildItems()

    def _dispose(self):
        super(RegularInventoryCategoryTabView, self)._dispose()
        self._itemsCache.onSyncCompleted -= self.__onCacheResync

    @process
    def _sellItems(self, itemId):
        yield DialogsInterface.showDialog(SellModuleMeta(int(itemId)))

    def setTabId(self, tabId):
        self._currentTabId = tabId
        self._buildItems()

    def _getItemTypeID(self):
        return _TABS_ITEM_TYPES[self._currentTabId]

    def _getRequestCriteria(self, invVehicles):
        criteria = REQ_CRITERIA.INVENTORY
        if self._currentTabId in (STORAGE_CONSTANTS.INVENTORY_TAB_ALL, STORAGE_CONSTANTS.INVENTORY_TAB_MODULES):
            criteria |= REQ_CRITERIA.TYPE_CRITERIA(GUI_ITEM_TYPE.VEHICLE_MODULES, REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles))
        if self._currentTabId in (STORAGE_CONSTANTS.INVENTORY_TAB_ALL, STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS):
            criteria |= REQ_CRITERIA.TYPE_CRITERIA((GUI_ITEM_TYPE.SHELL,), storage_helpers.getStorageShellsCriteria(self._itemsCache, invVehicles, True))
        return criteria

    def _getVO(self, item):
        return storage_helpers.getItemVo(item)

    def __onCacheResync(self, *args):
        self._buildItems()

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(_TABS_SORT_ORDER[a.itemTypeID], _TABS_SORT_ORDER[b.itemTypeID]) or cmp(GUI_NATIONS_ORDER_INDICES[a.nationID], GUI_NATIONS_ORDER_INDICES[b.nationID]) or _IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator


class FiltrableInventoryCategoryTabView(ItemsWithVehicleFilterTabViewMeta):
    filterItems = None

    def __init__(self):
        super(FiltrableInventoryCategoryTabView, self).__init__()
        self._filterMask = 0
        self._totalCount = -1
        self._currentCount = -1
        self._selectedVehicle = None
        self.__isActive = False
        self._loadFilters()
        return

    def setActiveState(self, isActive):
        self.__isActive = isActive

    @process
    def sellItem(self, itemId):
        yield DialogsInterface.showDialog(SellModuleMeta(int(itemId)))

    def onFiltersChange(self, filterMask):
        self._filterMask = filterMask
        self._buildItems()

    def resetFilter(self):
        self._filterMask = 0
        self._selectedVehicle = None
        self.as_updateVehicleFilterButtonS()
        self.as_resetFilterS(self._filterMask)
        self._buildItems()
        return

    def resetVehicleFilter(self):
        self._selectedVehicle = None
        self.as_updateVehicleFilterButtonS()
        self._buildItems()
        return

    def _loadFilters(self):
        if storage_helpers.isStorageSessionTimeout():
            return
        else:
            filterDict = AccountSettings.getSessionSettings(self._getClientSectionKey())
            self._filterMask = filterDict['filterMask']
            vehicleCD = filterDict['vehicleCD']
            self._selectedVehicle = self._itemsCache.items.getItemByCD(vehicleCD) if vehicleCD else None
            return

    def _saveFilters(self):
        vehicleCD = self._selectedVehicle.intCD if self._selectedVehicle else None
        filterDict = {'filterMask': self._filterMask,
         'vehicleCD': vehicleCD}
        AccountSettings.setSessionSettings(self._getClientSectionKey(), filterDict)
        return

    def _getClientSectionKey(self):
        raise NotImplementedError

    def _getFilteredCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _initFilter(self):
        items = self._getInitFilterItems()
        for item in items:
            if self._filterMask & item['filterValue'] == item['filterValue']:
                item.update({'selected': True})

        typeFilters = {'items': items,
         'minSelectedItems': 0}
        self.as_initFilterS(typeFilters, self._makeVehicleVO(self._selectedVehicle))

    def _populate(self):
        super(FiltrableInventoryCategoryTabView, self)._populate()
        self._initFilter()
        self.addListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        self._buildItems()

    def _dispose(self):
        self._saveFilters()
        self.removeListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        super(FiltrableInventoryCategoryTabView, self)._dispose()

    def _buildItems(self):
        super(FiltrableInventoryCategoryTabView, self)._buildItems()
        self.__updateUI()

    def _getVO(self, item):
        return storage_helpers.getItemVo(item)

    def _getVoList(self):
        baseCriteria = self._getRequestCriteria(self._invVehicles)
        filterCriteria = self._getFilteredCriteria()
        totalItems = self._itemsCache.items.getItems(self._getItemTypeID(), baseCriteria, nationID=None)
        self._totalCount = sum((item.inventoryCount for item in totalItems.values()))
        dataProviderListVoItems = []
        for item in sorted(totalItems.itervalues(), cmp=self._getComparator()):
            if filterCriteria(item):
                dataProviderListVoItems.append(self._getVO(item))

        self._currentCount = sum((item['count'] for item in dataProviderListVoItems))
        return dataProviderListVoItems

    @staticmethod
    def _makeVehicleVO(vehicle):
        if vehicle is None:
            return
        else:
            vo = makeVehicleVO(vehicle)
            vo.update({'type': '{}_elite'.format(vehicle.type) if vehicle.isPremium else vehicle.type})
            return vo

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(_TABS_SORT_ORDER[a.itemTypeID], _TABS_SORT_ORDER[b.itemTypeID]) or cmp(GUI_NATIONS_ORDER_INDICES[a.nationID], GUI_NATIONS_ORDER_INDICES[b.nationID]) or _IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator

    def _getInitFilterItems(self):
        return copy.deepcopy(self.filterItems) if self.filterItems is not None else []

    def __updateUI(self):
        self.__updateFilterCounter()
        self.__updateScreen()

    def __updateFilterCounter(self):
        if self._totalCount != -1 and self._currentCount != -1:
            shouldShow = self._filterMask != 0 or bool(self._selectedVehicle)
            if shouldShow:
                countString = self._formatCountString(self._currentCount, self._totalCount)
            else:
                countString = self._formatTotalCountString(self._totalCount)
            self.as_updateCounterS(shouldShow, countString, self._currentCount == 0)

    def __updateScreen(self):
        hasNoItems = self._totalCount == 0
        hasNoFilterResults = not hasNoItems and self._currentCount == 0
        filterWarningVO = None
        if hasNoFilterResults:
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        elif hasNoItems:
            self.as_showDummyScreenS(hasNoItems)
        self.as_showFilterWarningS(filterWarningVO)
        return

    def __onVehicleSelected(self, event):
        if event.ctx and event.ctx.get('vehicleId') and self.__isActive:
            self._selectedVehicle = vehicle = self._itemsCache.items.getItemByCD(event.ctx['vehicleId'])
            self.as_updateVehicleFilterButtonS(self._makeVehicleVO(vehicle))
            self._buildItems()

    def __onCacheResync(self, *args):
        self._buildItems()
