# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/Inventory.py
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.store.tabs import inventory
from gui.Scaleform.daapi.view.meta.InventoryMeta import InventoryMeta
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.shared import event_dispatcher as shared_event_dispatcher
from gui.shared.utils import flashObject2Dict
from adisp import process
from items import ITEM_TYPE_INDICES
from items import vehicles
_INVENTORY_TABS = {STORE_CONSTANTS.SHELL: inventory.InventoryShellTab,
 STORE_CONSTANTS.MODULE: inventory.InventoryModuleTab,
 STORE_CONSTANTS.VEHICLE: inventory.InventoryVehicleTab,
 STORE_CONSTANTS.OPTIONAL_DEVICE: inventory.InventoryOptionalDeviceTab,
 STORE_CONSTANTS.EQUIPMENT: inventory.InventoryEquipmentTab}

class Inventory(InventoryMeta):

    def sellItem(self, itemCD):
        dataCompactId = int(itemCD)
        item = self.itemsCache.items.getItemByCD(dataCompactId)
        if ITEM_TYPE_INDICES[item.itemTypeName] == vehicles._VEHICLE:
            shared_event_dispatcher.showVehicleSellDialog(int(item.invID))
        else:
            self.__sellItem(item.intCD)

    def requestTableData(self, nation, actionsSelected, type, filter):
        """
        Request table data for selected tab
        :param type: <str> tab ID
        :param nation: <int> gui nation
        :param actionsSelected: <bool> discount's checkbox value
        :param filter: <obj> filter data
        """
        Waiting.show('updateInventory')
        filter = flashObject2Dict(filter)
        itemCD = AccountSettings.getFilter('scroll_to_item')
        AccountSettings.setFilter('inventory_current', (nation, type, actionsSelected))
        AccountSettings.setFilter('inventory_' + type, filter)
        AccountSettings.setFilter('scroll_to_item', None)
        self._setTableData(filter, nation, type, actionsSelected, itemCD)
        Waiting.hide('updateInventory')
        return

    def getName(self):
        """
        Get component name
        :return: <str>
        """
        return STORE_TYPES.INVENTORY

    def _populate(self):
        """
        Prepare and set init data into Flash
        Subscribe on account updates
        """
        g_clientUpdateManager.addCallbacks({'inventory': self._onTableUpdate})
        super(Inventory, self)._populate()

    def _getTabClass(self, type):
        """
        Get component tab class by type
        :param type: <str> tab ID
        :return:<ShopItemsTab>
        """
        return _INVENTORY_TABS[type]

    @process
    def __sellItem(self, itemTypeCompactDescr):
        isOk, args = yield DialogsInterface.showDialog(SellModuleMeta(itemTypeCompactDescr))
        LOG_DEBUG('Sell module confirm dialog results', isOk, args)
