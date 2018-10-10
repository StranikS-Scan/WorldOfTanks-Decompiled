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
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.utils import flashObject2Dict
_SHOP_TABS = {STORE_CONSTANTS.SHELL: shop.ShopShellTab,
 STORE_CONSTANTS.MODULE: shop.ShopModuleTab,
 STORE_CONSTANTS.VEHICLE: shop.ShopVehicleTab,
 STORE_CONSTANTS.RESTORE_VEHICLE: shop.ShopRestoreVehicleTab,
 STORE_CONSTANTS.TRADE_IN_VEHICLE: shop.ShopTradeInVehicleTab,
 STORE_CONSTANTS.OPTIONAL_DEVICE: shop.ShopOptionalDeviceTab,
 STORE_CONSTANTS.EQUIPMENT: shop.ShopEquipmentTab,
 STORE_CONSTANTS.BATTLE_BOOSTER: shop.ShopBattleBoosterTab}

class Shop(ShopMeta):

    def buyItem(self, itemCD, allowTradeIn):
        dataCompactId = int(itemCD)
        item = self.itemsCache.items.getItemByCD(dataCompactId)
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, dataCompactId, allowTradeIn)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_MODULE, dataCompactId)

    def requestTableData(self, nation, actionsSelected, tabType, f):
        Waiting.show('updateShop')
        f = flashObject2Dict(f)
        itemCD = AccountSettings.getFilter('scroll_to_item')
        AccountSettings.setFilter('shop_current', (nation, tabType, actionsSelected))
        AccountSettings.setFilter('shop_' + tabType, flashObject2Dict(f))
        AccountSettings.setFilter('scroll_to_item', None)
        self._setTableData(f, nation, tabType, actionsSelected, itemCD)
        Waiting.hide('updateShop')
        return

    def getName(self):
        return STORE_TYPES.SHOP

    def _populate(self):
        super(Shop, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self._onTableUpdate)
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self._onTableUpdate,
         'inventory.1': self._onTableUpdate})
        g_playerEvents.onCenterIsLongDisconnected += self._update

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onCenterIsLongDisconnected -= self._update
        super(Shop, self)._dispose()

    def _getTabClass(self, tabType):
        return _SHOP_TABS[tabType]
