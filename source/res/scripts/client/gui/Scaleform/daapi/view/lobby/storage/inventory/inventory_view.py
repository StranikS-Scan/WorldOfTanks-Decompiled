# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_view.py
import copy
from gui import GUI_NATIONS_ORDER_INDICES
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.category_view import InventoryCategoryView
from gui.Scaleform.daapi.view.meta.StorageCategoryStorageViewMeta import StorageCategoryStorageViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.crew_book import orderCmp as crewBookCmp
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.storage_novelty import IStorageNovelty
from skeletons.gui.lobby_context import ILobbyContext
from constants import SwitchState
from gui.shared.event_dispatcher import showSellDialog
VERSION = 1
_TABS_DATA = ({'id': STORAGE_CONSTANTS.INVENTORY_TAB_ALL,
  'label': R.strings.storage.storage.tabs.all,
  'linkage': STORAGE_CONSTANTS.STORAGE_REGULAR_ITEMS_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT,
  'label': R.strings.storage.storage.tabs.equipment,
  'linkage': STORAGE_CONSTANTS.STORAGE_DEVICES_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE,
  'label': R.strings.storage.storage.tabs.consumable,
  'linkage': STORAGE_CONSTANTS.STORAGE_CONSUMABLES_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_MODULES,
  'label': R.strings.storage.storage.tabs.modules,
  'linkage': STORAGE_CONSTANTS.STORAGE_MODULES_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS,
  'label': R.strings.storage.storage.tabs.shells,
  'linkage': STORAGE_CONSTANTS.STORAGE_SHELLS_TAB},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_CREW_BOOKS,
  'label': R.strings.storage.storage.tabs.crewBooks,
  'linkage': STORAGE_CONSTANTS.STORAGE_CREW_BOOKS_TAB})

def _getTabDataIndexById(tabID):
    for i, section in enumerate(_TABS_DATA):
        if section['id'] == tabID:
            return i


_TABS_ITEM_TYPES = {STORAGE_CONSTANTS.INVENTORY_TAB_ALL: GUI_ITEM_TYPE.VEHICLE_COMPONENTS + (GUI_ITEM_TYPE.CREW_BOOKS, GUI_ITEM_TYPE.DEMOUNT_KIT, GUI_ITEM_TYPE.RECERTIFICATION_FORM),
 STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT: GUI_ITEM_TYPE.OPTIONALDEVICE,
 STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE: (GUI_ITEM_TYPE.EQUIPMENT,
                                              GUI_ITEM_TYPE.BATTLE_BOOSTER,
                                              GUI_ITEM_TYPE.DEMOUNT_KIT,
                                              GUI_ITEM_TYPE.RECERTIFICATION_FORM),
 STORAGE_CONSTANTS.INVENTORY_TAB_MODULES: GUI_ITEM_TYPE.VEHICLE_MODULES,
 STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS: GUI_ITEM_TYPE.SHELL,
 STORAGE_CONSTANTS.INVENTORY_TAB_CREW_BOOKS: GUI_ITEM_TYPE.CREW_BOOKS}
TABS_SORT_ORDER = {n:idx for idx, n in enumerate((GUI_ITEM_TYPE.OPTIONALDEVICE,
 GUI_ITEM_TYPE.EQUIPMENT,
 GUI_ITEM_TYPE.BATTLE_BOOSTER,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.RADIO,
 GUI_ITEM_TYPE.SHELL,
 GUI_ITEM_TYPE.CREW_BOOKS,
 GUI_ITEM_TYPE.DEMOUNT_KIT,
 GUI_ITEM_TYPE.RECERTIFICATION_FORM))}

def _defaultInGroupComparator(a, b):
    return cmp(storage_helpers.getStorageItemName(a), storage_helpers.getStorageItemName(b))


_OPT_DEVICE_TYPE_ORDER = (REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE,
 REQ_CRITERIA.OPTIONAL_DEVICE.TROPHY,
 REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE,
 REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED)

def _getDeviceCategoriesOrder(optDevice):
    categories = optDevice.descriptor.categories
    return min((storage_helpers.OPT_DEVICE_CATEGORIES_ORDER.get(category, storage_helpers.CATEGORIES_COUNT) for category in categories)) if categories else storage_helpers.CATEGORIES_COUNT


def _upgradableDeviceComparator(a, b):
    if a.isUpgradable != b.isUpgradable:
        if a.isUpgradable:
            return 1
        return -1


def _optionalDevicesComparator(a, b):

    def getKey(module):
        moduleIdx = -1
        for idx, criteria in enumerate(_OPT_DEVICE_TYPE_ORDER):
            if criteria(module):
                moduleIdx = idx

        return (moduleIdx,
         module.level,
         module.isUpgradable,
         _getDeviceCategoriesOrder(module),
         storage_helpers.getStorageItemName(module))

    return cmp(getKey(a), getKey(b))


def _shellsComparator(a, b):
    return cmp(a.descriptor.caliber, b.descriptor.caliber) or _defaultInGroupComparator(a, b)


def _gunsComparator(a, b):
    return cmp(a.descriptor.level, b.descriptor.level) or cmp(a.descriptor.shots[0].shell.caliber, b.descriptor.shots[0].shell.caliber) or _defaultInGroupComparator(a, b)


def _crewBookComparator(a, b):
    return crewBookCmp(a, b) or _defaultInGroupComparator(a, b)


IN_GROUP_COMPARATOR = {GUI_ITEM_TYPE.OPTIONALDEVICE: _optionalDevicesComparator,
 GUI_ITEM_TYPE.EQUIPMENT: _defaultInGroupComparator,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: _defaultInGroupComparator,
 GUI_ITEM_TYPE.TURRET: _defaultInGroupComparator,
 GUI_ITEM_TYPE.ENGINE: _defaultInGroupComparator,
 GUI_ITEM_TYPE.GUN: _gunsComparator,
 GUI_ITEM_TYPE.RADIO: _defaultInGroupComparator,
 GUI_ITEM_TYPE.CHASSIS: _defaultInGroupComparator,
 GUI_ITEM_TYPE.SHELL: _shellsComparator,
 GUI_ITEM_TYPE.CREW_BOOKS: _crewBookComparator,
 GUI_ITEM_TYPE.DEMOUNT_KIT: _defaultInGroupComparator,
 GUI_ITEM_TYPE.RECERTIFICATION_FORM: _defaultInGroupComparator}

class InventoryCategoryStorageView(StorageCategoryStorageViewMeta):
    __storageNovelty = dependency.descriptor(IStorageNovelty)

    def __init__(self):
        super(InventoryCategoryStorageView, self).__init__()
        self.__currentTabId = STORAGE_CONSTANTS.INVENTORY_TAB_ALL
        self.__views = {}

    def onOpenTab(self, tabId):
        self.__currentTabId = tabId
        if self.__currentTabId in self.__views:
            self.__views[self.__currentTabId].setTabId(self.__currentTabId)

    def setActiveState(self, isActive):
        self.setActive(isActive)

    def setActiveTab(self, tabId):
        self.__currentTabId = tabId
        tabsData = self._getTabsData()
        activeIdx = 0
        for i, tab in enumerate(tabsData):
            if tab['id'] == self.__currentTabId:
                activeIdx = i
                break

        tabsData[activeIdx]['selected'] = True
        self.as_setTabsDataS(tabsData)

    def _populate(self):
        super(InventoryCategoryStorageView, self)._populate()
        self.__storageNovelty.onUpdated += self._updateTabCounters
        self._updateTabCounters()

    def _destroy(self):
        super(InventoryCategoryStorageView, self)._destroy()
        self.__storageNovelty.onUpdated -= self._updateTabCounters

    def _getTabsData(self):
        tabsData = copy.deepcopy(_TABS_DATA)
        for item in tabsData:
            item['label'] = backport.text(item['label']())

        return tuple(tabsData)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(InventoryCategoryStorageView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == STORAGE_CONSTANTS.STORAGE_REGULAR_ITEMS_TAB:
            self.__views[STORAGE_CONSTANTS.INVENTORY_TAB_ALL] = viewPy
        if alias not in (STORAGE_CONSTANTS.STORAGE_MODULES_TAB,
         STORAGE_CONSTANTS.STORAGE_SHELLS_TAB,
         STORAGE_CONSTANTS.STORAGE_DEVICES_TAB,
         STORAGE_CONSTANTS.STORAGE_CREW_BOOKS_TAB,
         STORAGE_CONSTANTS.STORAGE_CONSUMABLES_TAB):
            viewPy.setTabId(self.__currentTabId)

    def _updateTabCounters(self):
        idx = _getTabDataIndexById(STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE)
        self.as_setTabCounterS(idx, self.__storageNovelty.noveltyCount)


class RegularInventoryCategoryTabView(InventoryCategoryView):
    __lobbyContext = dependency.descriptor(ILobbyContext)

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

    def _sellItems(self, itemId):
        showSellDialog(int(itemId))

    def setTabId(self, tabId):
        self._currentTabId = tabId
        self._buildItems()

    def _getItemList(self):
        criteria = self._getRequestCriteria(self._invVehicles)
        items = {}
        for itemType in self._getItemTypeIDs():
            if itemType == GUI_ITEM_TYPE.DEMOUNT_KIT:
                items.update(self._goodiesCache.getDemountKits(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED))
            if itemType == GUI_ITEM_TYPE.RECERTIFICATION_FORM:
                if self.__lobbyContext.getServerSettings().recertificationFormState() != SwitchState.DISABLED.value:
                    items.update(self._goodiesCache.getRecertificationForms(REQ_CRITERIA.DEMOUNT_KIT.IN_ACCOUNT | REQ_CRITERIA.DEMOUNT_KIT.IS_ENABLED))
            items.update(self._itemsCache.items.getItems(itemType, criteria, nationID=None))

        return items

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
            return cmp(TABS_SORT_ORDER[a.itemTypeID], TABS_SORT_ORDER[b.itemTypeID]) or cmp(GUI_NATIONS_ORDER_INDICES[a.nationID], GUI_NATIONS_ORDER_INDICES[b.nationID]) or IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator
