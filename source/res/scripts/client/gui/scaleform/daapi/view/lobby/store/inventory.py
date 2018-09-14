# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/Inventory.py
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.store.tabs import inventory
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.meta.InventoryMeta import InventoryMeta
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.shared import g_itemsCache, event_dispatcher as shared_event_dispatcher
from adisp import process
from items import ITEM_TYPE_INDICES
from items import vehicles
_INVENTORY_TABS = {FITTING_TYPES.SHELL: inventory.InventoryShellTab,
 FITTING_TYPES.MODULE: inventory.InventoryModuleTab,
 FITTING_TYPES.VEHICLE: inventory.InventoryVehicleTab,
 FITTING_TYPES.OPTIONAL_DEVICE: inventory.InventoryOptionalDeviceTab,
 FITTING_TYPES.EQUIPMENT: inventory.InventoryEquipmentTab}

class Inventory(InventoryMeta):

    def sellItem(self, data):
        dataCompactId = int(data.id)
        item = g_itemsCache.items.getItemByCD(dataCompactId)
        if ITEM_TYPE_INDICES[item.itemTypeName] == vehicles._VEHICLE:
            shared_event_dispatcher.showVehicleSellDialog(int(item.invID))
        else:
            self.__sellItem(item.intCD)

    def requestTableData(self, nation, type, filter):
        Waiting.show('updateInventory')
        AccountSettings.setFilter('inventory_current', (nation, type))
        AccountSettings.setFilter('inventory_' + type, filter)
        self._setTableData(filter, nation, type)
        Waiting.hide('updateInventory')

    def getName(self):
        return STORE_TYPES.INVENTORY

    def _populate(self):
        g_clientUpdateManager.addCallbacks({'inventory': self._onTableUpdate})
        super(Inventory, self)._populate()

    def _update(self, *args):
        self.as_updateS()

    def _getTab(self, type, nation, filter):
        return _INVENTORY_TABS[type](nation, filter)

    @process
    def __sellItem(self, itemTypeCompactDescr):
        isOk, args = yield DialogsInterface.showDialog(SellModuleMeta(itemTypeCompactDescr))
        LOG_DEBUG('Sell module confirm dialog results', isOk, args)
