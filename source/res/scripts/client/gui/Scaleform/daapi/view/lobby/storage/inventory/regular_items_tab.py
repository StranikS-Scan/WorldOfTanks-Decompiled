# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/regular_items_tab.py
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import getBuyOptionalDevicesUrl, getBuyEquipmentUrl
from gui.Scaleform.daapi.view.meta.RegularItemsTabViewMeta import RegularItemsTabViewMeta
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.shared.event_dispatcher import showWebShop

class RegularItemsTabView(RegularItemsTabViewMeta):

    def sellItem(self, itemId):
        self._sellItems(itemId)

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
