# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_view.py
from adisp import process
from gui import GUI_NATIONS_ORDER_INDICES
import nations
from gui import DialogsInterface
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.category_view import InventoryCategoryView
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getBoosterType
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.meta.StorageCategoryStorageViewMeta import StorageCategoryStorageViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS as SC
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.shared.formatters import getItemPricesVO
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
_HANDLERS_MAP = {GUI_ITEM_TYPE.OPTIONALDEVICE: CONTEXT_MENU_HANDLER_TYPE.STORAGE_EQUIPMENT_ITEM,
 GUI_ITEM_TYPE.EQUIPMENT: CONTEXT_MENU_HANDLER_TYPE.STORAGE_EQUIPMENT_ITEM,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: CONTEXT_MENU_HANDLER_TYPE.STORAGE_BONS_ITEM,
 GUI_ITEM_TYPE.TURRET: CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,
 GUI_ITEM_TYPE.ENGINE: CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,
 GUI_ITEM_TYPE.GUN: CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,
 GUI_ITEM_TYPE.RADIO: CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,
 GUI_ITEM_TYPE.CHASSIS: CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM,
 GUI_ITEM_TYPE.SHELL: CONTEXT_MENU_HANDLER_TYPE.STORAGE_MODULES_SHELLS_ITEM}
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
        elif alias == STORAGE_CONSTANTS.STORAGE_MODULES_TAB:
            self.__views[STORAGE_CONSTANTS.INVENTORY_TAB_MODULES] = viewPy
        elif alias == STORAGE_CONSTANTS.STORAGE_SHELLS_TAB:
            self.__views[STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS] = viewPy
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
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self._buildItems()

    def _dispose(self):
        super(RegularInventoryCategoryTabView, self)._dispose()
        self.itemsCache.onSyncCompleted -= self.__onCacheResync

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
            criteria |= REQ_CRITERIA.TYPE_CRITERIA((GUI_ITEM_TYPE.SHELL,), storage_helpers.getStorageShellsCriteria(self.itemsCache, invVehicles, True))
        return criteria

    def _getVO(self, item):
        priceVO = getItemPricesVO(item.getSellPrice())[0]
        itemNationID = self._getItemNationID(item)
        nationFlagIcon = RES_SHOP.getNationFlagIcon(nations.NAMES[itemNationID]) if itemNationID != nations.NONE_INDEX else ''
        vo = storage_helpers.createStorageDefVO(item.intCD, storage_helpers.getStorageModuleName(item), storage_helpers.getStorageItemDescr(item), item.inventoryCount, priceVO, storage_helpers.getStorageItemIcon(item, SC.ICON_SIZE_SMALL), storage_helpers.getStorageItemIcon(item), 'altimage', itemType=getBoosterType(item), nationFlagIcon=nationFlagIcon, enabled=item.itemTypeID != GUI_ITEM_TYPE.BATTLE_BOOSTER, contextMenuId=_HANDLERS_MAP[item.itemTypeID])
        return vo

    def _getItemNationID(self, item):
        compatibleNations = item.descriptor.compatibleNations() if item.itemTypeName == SC.EQUIPMENT else []
        return compatibleNations[0] if len(compatibleNations) == 1 else item.nationID

    def __onCacheResync(self, *args):
        self._buildItems()

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(_TABS_SORT_ORDER[a.itemTypeID], _TABS_SORT_ORDER[b.itemTypeID]) or cmp(GUI_NATIONS_ORDER_INDICES[a.nationID], GUI_NATIONS_ORDER_INDICES[b.nationID]) or _IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator


class FiltrableInventoryCategoryTabView(RegularInventoryCategoryTabView):

    def __init__(self):
        super(FiltrableInventoryCategoryTabView, self).__init__()
        self._filterMask = 0
        self._totalCount = -1
        self._currentCount = -1
        self._selectedVehicle = None
        return

    def _getFilteredCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getVoList(self):
        baseCriteria = self._getRequestCriteria(self._invVehicles)
        filterCriteria = self._getFilteredCriteria()
        totalItems = self.itemsCache.items.getItems(self._getItemTypeID(), baseCriteria, nationID=None)
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
