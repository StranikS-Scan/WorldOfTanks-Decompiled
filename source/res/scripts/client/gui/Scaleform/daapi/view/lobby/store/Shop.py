# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/Shop.py
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.store.tabs import shop
from gui.Scaleform.daapi.view.meta.ShopMeta import ShopMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.utils import flashObject2Dict
_SHOP_TABS = {STORE_CONSTANTS.SHELL: shop.ShopShellTab,
 STORE_CONSTANTS.MODULE: shop.ShopModuleTab,
 STORE_CONSTANTS.VEHICLE: shop.ShopVehicleTab,
 STORE_CONSTANTS.RESTORE_VEHICLE: shop.ShopRestoreVehicleTab,
 STORE_CONSTANTS.OPTIONAL_DEVICE: shop.ShopOptionalDeviceTab,
 STORE_CONSTANTS.EQUIPMENT: shop.ShopEquipmentTab}

class Shop(ShopMeta):

    def buyItem(self, itemCD):
        dataCompactId = int(itemCD)
        item = g_itemsCache.items.getItemByCD(dataCompactId)
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, dataCompactId)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_MODULE, dataCompactId)

    def requestTableData(self, nation, type, filter):
        """
        Request table data for selected tab
        :param type: <str> tab ID
        :param nation: <int> gui nation
        :param filter: <obj> filter data
        """
        Waiting.show('updateShop')
        AccountSettings.setFilter('shop_current', (nation, type))
        filter = flashObject2Dict(filter)
        AccountSettings.setFilter('shop_' + type, flashObject2Dict(filter))
        self._setTableData(filter, nation, type)
        Waiting.hide('updateShop')

    def getName(self):
        """
        Get component name
        :return: <str>
        """
        return STORE_TYPES.SHOP

    def _populate(self):
        """
        Prepare and set init data into Flash
        Subscribe on account updates
        """
        g_clientUpdateManager.addCallbacks({'stats.credits': self._onTableUpdate,
         'stats.gold': self._onTableUpdate,
         'cache.mayConsumeWalletResources': self._onTableUpdate,
         'inventory.1': self._onTableUpdate})
        g_playerEvents.onCenterIsLongDisconnected += self._update
        super(Shop, self)._populate()

    def _dispose(self):
        """
        Clear attrs and subscriptions
        """
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onCenterIsLongDisconnected -= self._update
        super(Shop, self)._dispose()

    def _getTabClass(self, type):
        """
        Get component tab class by type
        :param type: <str> tab ID
        :return:<ShopItemsTab>
        """
        return _SHOP_TABS[type]

    def _getObtainingVehicleSubFilterData(self):
        result = [{'id': STORE_CONSTANTS.BUY_VEHICLE_OBTAINING_TYPE,
          'label': MENU.BARRACKS_OBTAININGVEHICLETYPE_DROPDOWNITEM_BUYINGVEHICLE}]
        if self._isVehicleRestoreEnabled():
            result.append({'id': STORE_CONSTANTS.RESTORE_VEHICLE_OBTAINING_TYPE,
             'label': MENU.BARRACKS_OBTAININGVEHICLETYPE_DROPDOWNITEM_RESTOREVEHICLE})
        return result
