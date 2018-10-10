# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_view.py
import nations
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import showStorageModuleInfo, getBoosterType
from gui.Scaleform.daapi.view.meta.StorageCategoryStorageViewMeta import StorageCategoryStorageViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS as SC
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared.event_dispatcher import showWebShop
from gui.shared.formatters import getItemPricesVO
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyEquipmentUrl, getBuyOptionalDevicesUrl
_TABS_DATA = ({'id': STORAGE_CONSTANTS.INVENTORY_TAB_ALL,
  'label': STORAGE.STORAGE_TABS_ALL,
  'selected': True},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT,
  'label': STORAGE.STORAGE_TABS_EQUIPMENT},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE,
  'label': STORAGE.STORAGE_TABS_CONSUMABLE},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_MODULES,
  'label': STORAGE.STORAGE_TABS_MODULES},
 {'id': STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS,
  'label': STORAGE.STORAGE_TABS_SHELLS})
_TABS_ITEM_TYPES = {STORAGE_CONSTANTS.INVENTORY_TAB_ALL: GUI_ITEM_TYPE.VEHICLE_COMPONENTS,
 STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT: GUI_ITEM_TYPE.OPTIONALDEVICE,
 STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE: (GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.BATTLE_BOOSTER),
 STORAGE_CONSTANTS.INVENTORY_TAB_MODULES: GUI_ITEM_TYPE.VEHICLE_MODULES,
 STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS: GUI_ITEM_TYPE.SHELL}
_TABS_SORT_ORDER = dict(((n, idx) for idx, n in enumerate((GUI_ITEM_TYPE.OPTIONALDEVICE,
 GUI_ITEM_TYPE.EQUIPMENT,
 GUI_ITEM_TYPE.BATTLE_BOOSTER,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.RADIO,
 GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.SHELL))))

class InventoryCategoryStorageView(StorageCategoryStorageViewMeta):

    def __init__(self):
        super(InventoryCategoryStorageView, self).__init__()
        self.__currentTabId = STORAGE_CONSTANTS.INVENTORY_TAB_ALL

    @process
    def sellItem(self, itemId):
        yield DialogsInterface.showDialog(SellModuleMeta(int(itemId)))

    def onOpenTab(self, tabId):
        self.__currentTabId = tabId
        self._update()

    def navigateToStore(self):
        if self.__currentTabId == STORAGE_CONSTANTS.INVENTORY_TAB_ALL:
            showWebShop()
        if self.__currentTabId == STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT:
            showWebShop(getBuyOptionalDevicesUrl())
        elif self.__currentTabId == STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE:
            showWebShop(getBuyEquipmentUrl())

    def _populate(self):
        super(InventoryCategoryStorageView, self)._populate()
        self.as_setTabsDataS(_TABS_DATA)
        self.itemsCache.onSyncCompleted += self.__onCacheResync

    def _dispose(self):
        super(InventoryCategoryStorageView, self)._dispose()
        self.itemsCache.onSyncCompleted -= self.__onCacheResync

    def showItemInfo(self, itemId):
        showStorageModuleInfo(int(itemId))

    def _getComparator(self):

        def _comparator(a, b):
            if a.itemTypeID == b.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                preResult = (1 if a.isDeluxe() else 0) - (1 if b.isDeluxe() else 0)
            else:
                preResult = cmp(_TABS_SORT_ORDER[a.itemTypeID], _TABS_SORT_ORDER[b.itemTypeID])
            return preResult or cmp(storage_helpers.getStorageModuleName(a), storage_helpers.getStorageModuleName(b))

        return _comparator

    def _getVO(self, item):
        priceVO = getItemPricesVO(item.getSellPrice())[0]
        itemNationID = self._getItemNationID(item)
        nationFlagIcon = RES_SHOP.getNationFlagIcon(nations.NAMES[itemNationID]) if itemNationID != nations.NONE_INDEX else ''
        vo = storage_helpers.createStorageDefVO(item.intCD, storage_helpers.getStorageModuleName(item), storage_helpers.getStorageItemDescr(item), item.inventoryCount, priceVO, storage_helpers.getStorageItemIcon(item, SC.ICON_SIZE_SMALL), storage_helpers.getStorageItemIcon(item), 'altimage', itemType=getBoosterType(item), nationFlagIcon=nationFlagIcon, enabled=item.itemTypeID != GUI_ITEM_TYPE.BATTLE_BOOSTER)
        return vo

    def _getItemTypeID(self):
        return _TABS_ITEM_TYPES[self.__currentTabId]

    def _getItemNationID(self, item):
        compatibleNations = item.descriptor.compatibleNations() if item.itemTypeName == SC.EQUIPMENT else []
        return compatibleNations[0] if len(compatibleNations) == 1 else item.nationID

    def _getRequestCriteria(self, invVehicles):
        criteria = super(InventoryCategoryStorageView, self)._getRequestCriteria(invVehicles)
        criteria |= REQ_CRITERIA.INVENTORY
        tabID = self.__currentTabId
        if tabID in (STORAGE_CONSTANTS.INVENTORY_TAB_ALL, STORAGE_CONSTANTS.INVENTORY_TAB_MODULES):
            criteria |= REQ_CRITERIA.TYPE_CRITERIA(GUI_ITEM_TYPE.VEHICLE_MODULES, REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles))
        if tabID in (STORAGE_CONSTANTS.INVENTORY_TAB_ALL, STORAGE_CONSTANTS.INVENTORY_TAB_SHELLS):
            criteria |= REQ_CRITERIA.TYPE_CRITERIA((GUI_ITEM_TYPE.SHELL,), storage_helpers.getStorageShellsCriteria(self.itemsCache, invVehicles, True))
        return criteria

    def _buildItems(self):
        super(InventoryCategoryStorageView, self)._buildItems()
        self.as_showDummyScreenS(len(self._dataProvider.collection) == 0)

    def __onCacheResync(self, *args):
        self._buildItems()
        self._dataProvider.refresh()
