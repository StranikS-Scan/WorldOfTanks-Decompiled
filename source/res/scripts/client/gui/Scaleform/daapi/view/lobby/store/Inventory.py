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
 STORE_CONSTANTS.EQUIPMENT: inventory.InventoryEquipmentTab,
 STORE_CONSTANTS.BATTLE_BOOSTER: inventory.InventoryBattleBoosterTab}

class Inventory(InventoryMeta):

    def sellItem(self, itemCD):
        dataCompactId = int(itemCD)
        item = self.itemsCache.items.getItemByCD(dataCompactId)
        if ITEM_TYPE_INDICES[item.itemTypeName] == vehicles._VEHICLE:
            shared_event_dispatcher.showVehicleSellDialog(int(item.invID))
        else:
            self.__sellItem(item.intCD)

    def requestTableData(self, nation, actionsSelected, tabID, f):
        Waiting.show('updateInventory')
        f = flashObject2Dict(f)
        itemCD = AccountSettings.getFilter('scroll_to_item')
        AccountSettings.setFilter('inventory_current', (nation, tabID, actionsSelected))
        AccountSettings.setFilter('inventory_' + tabID, f)
        AccountSettings.setFilter('scroll_to_item', None)
        self._setTableData(f, nation, tabID, actionsSelected, itemCD)
        Waiting.hide('updateInventory')
        return

    def getName(self):
        return STORE_TYPES.INVENTORY

    def _populate(self):
        g_clientUpdateManager.addCallbacks({'inventory': self._onTableUpdate})
        super(Inventory, self)._populate()

    def _getTabClass(self, tabType):
        return _INVENTORY_TABS[tabType]

    @process
    def __sellItem(self, itemTypeCompactDescr):
        isOk, args = yield DialogsInterface.showDialog(SellModuleMeta(itemTypeCompactDescr))
        LOG_DEBUG('Sell module confirm dialog results', isOk, args)
