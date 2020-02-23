# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/regular_items_tab.py
from async import await, async
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyOptionalDevicesUrl, getBuyEquipmentUrl
from gui.Scaleform.daapi.view.meta.RegularItemsTabViewMeta import RegularItemsTabViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.shared.event_dispatcher import showWebShop, showBattleBoosterSellDialog
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.dialogs import dialogs

class RegularItemsTabView(RegularItemsTabViewMeta):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def sellItem(self, itemId):
        dataCompactId = int(itemId)
        item = self.__itemsCache.items.getItemByCD(dataCompactId)
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            showBattleBoosterSellDialog(dataCompactId)
        else:
            self._sellItems(itemId)

    @async
    def upgradeItem(self, itemId):
        module = self.__itemsCache.items.getItemByCD(int(itemId))
        result, _ = yield await(dialogs.trophyDeviceUpgradeConfirm(module))
        if result:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_MODULE, module, None, None)
        return

    def navigateToStore(self):
        if self._currentTabId == STORAGE_CONSTANTS.INVENTORY_TAB_ALL:
            showWebShop()
        if self._currentTabId == STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT:
            showWebShop(getBuyOptionalDevicesUrl())
        elif self._currentTabId == STORAGE_CONSTANTS.INVENTORY_TAB_CONSUMABLE:
            showWebShop(getBuyEquipmentUrl())

    def _buildItems(self):
        super(RegularItemsTabView, self)._buildItems()
        self.as_showDummyScreenS(len(self._dataProvider.collection) == 0)
