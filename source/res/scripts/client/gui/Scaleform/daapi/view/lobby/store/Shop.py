# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/Shop.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.lobby.store.tabs import shop
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.ShopMeta import ShopMeta
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
_SHOP_TABS = {FITTING_TYPES.SHELL: shop.ShopShellTab,
 FITTING_TYPES.MODULE: shop.ShopModuleTab,
 FITTING_TYPES.VEHICLE: shop.ShopVehicleTab,
 FITTING_TYPES.OPTIONAL_DEVICE: shop.ShopOptionalDeviceTab,
 FITTING_TYPES.EQUIPMENT: shop.ShopEquipmentTab}

class Shop(ShopMeta):

    def buyItem(self, data):
        itemCD = int(data.id)
        item = g_itemsCache.items.getItemByCD(itemCD)
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_MODULE, itemCD)

    def requestTableData(self, nation, type, filter):
        Waiting.show('updateShop')
        AccountSettings.setFilter('shop_current', (nation, type))
        AccountSettings.setFilter('shop_' + type, filter)
        self._setTableData(filter, nation, type)
        Waiting.hide('updateShop')

    def getName(self):
        return STORE_TYPES.SHOP

    def _populate(self):
        g_clientUpdateManager.addCallbacks({'stats.credits': self._onTableUpdate,
         'stats.gold': self._onTableUpdate,
         'cache.mayConsumeWalletResources': self._onTableUpdate,
         'inventory.1': self._onTableUpdate})
        g_playerEvents.onCenterIsLongDisconnected += self._update
        super(Shop, self)._populate()

    def _dispose(self):
        super(Shop, self)._dispose()
        g_playerEvents.onCenterIsLongDisconnected -= self._update

    def _getTab(self, type, nation, filter):
        return _SHOP_TABS[type](nation, filter)

    def _update(self, *args):
        self.as_updateS()
