# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/opt_devices_tab.py
from collections import OrderedDict
from enum import IntEnum
from PlayerEvents import g_playerEvents
from gui.shared.event_dispatcher import showSellDialog
from gui.Scaleform.daapi.view.meta.StorageDevicesTabViewMeta import StorageDevicesTabViewMeta
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import TABS_SORT_ORDER, IN_GROUP_COMPARATOR
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyOptionalDevicesUrl
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.event_dispatcher import showShop
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA

class _OptDeviceTypeFilter(IntEnum):
    ALL = 0
    SIMPLE = 1
    DELUXE = 2
    TROPHY = 4
    MODERNIZED = 8


_TYPE_FILTER_ITEMS = [{'id': int(_OptDeviceTypeFilter.ALL),
  'label': backport.text(R.strings.storage.devices.filters.all())},
 {'id': int(_OptDeviceTypeFilter.SIMPLE),
  'label': backport.text(R.strings.storage.devices.filters.simple())},
 {'id': int(_OptDeviceTypeFilter.TROPHY),
  'label': backport.text(R.strings.storage.devices.filters.trophy())},
 {'id': int(_OptDeviceTypeFilter.DELUXE),
  'label': backport.text(R.strings.storage.devices.filters.deluxe())},
 {'id': int(_OptDeviceTypeFilter.MODERNIZED),
  'label': backport.text(R.strings.storage.devices.filters.modernized())}]
_BIT_TO_DEVICE_TYPE_MAP = OrderedDict(((_OptDeviceTypeFilter.SIMPLE, REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE),
 (_OptDeviceTypeFilter.TROPHY, REQ_CRITERIA.OPTIONAL_DEVICE.TROPHY),
 (_OptDeviceTypeFilter.DELUXE, REQ_CRITERIA.OPTIONAL_DEVICE.DELUXE),
 (_OptDeviceTypeFilter.MODERNIZED, REQ_CRITERIA.OPTIONAL_DEVICE.MODERNIZED)))

class OptDevicesTabView(StorageDevicesTabViewMeta):

    def _populate(self):
        super(OptDevicesTabView, self)._populate()
        self.__updateBalance()
        g_playerEvents.onClientUpdated += self.__onClientUpdate

    def _dispose(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdate
        super(OptDevicesTabView, self)._dispose()

    def _getTypeFilters(self, items):
        return {'items': items,
         'minSelectedItems': 0,
         'filterTypeName': backport.text(R.strings.storage.storage.tabs.devices.filter.type.label())}

    def navigateToStore(self):
        showShop(getBuyOptionalDevicesUrl())

    def upgradeItem(self, itemId):
        optDevice = self._itemsCache.items.getItemByCD(int(itemId))
        ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_OPT_DEVICE, optDevice, None, None, None)
        return

    def _initFilter(self):
        index = 0
        if self._filterMask in _BIT_TO_DEVICE_TYPE_MAP:
            index = _BIT_TO_DEVICE_TYPE_MAP.keys().index(self._filterMask) + 1
        self.as_initModulesFilterS({'enabled': True,
         'selectedIndex': index,
         'data': _TYPE_FILTER_ITEMS})

    def _getClientSectionKey(self):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE

    def _getFilteredCriteria(self):
        criteria = _BIT_TO_DEVICE_TYPE_MAP.get(self._filterMask, REQ_CRITERIA.EMPTY)
        if self._selectedVehicle:
            if not self._selectedVehicle.optDevices.layout.getCapacity():
                criteria |= REQ_CRITERIA.NONE
            else:
                criteria |= REQ_CRITERIA.VEHICLE.SUITABLE([self._selectedVehicle], self._getItemTypeIDs())
        return criteria

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.INVENTORY

    def _getComparator(self):

        def _comparator(a, b):
            return cmp(TABS_SORT_ORDER[a.itemTypeID], TABS_SORT_ORDER[b.itemTypeID]) or IN_GROUP_COMPARATOR[a.itemTypeID](a, b)

        return _comparator

    def _buildItems(self):
        super(OptDevicesTabView, self)._buildItems()
        self.as_showDummyScreenS(not self._dataProvider.collection)

    def sellItem(self, itemId):
        showSellDialog(int(itemId))

    def __onClientUpdate(self, diff, _):
        if Currency.EQUIP_COIN in diff.get('stats', {}):
            self.__updateBalance()

    def __updateBalance(self):
        money = self._itemsCache.items.stats.money
        balanceStr = backport.getIntegralFormat(money.get(Currency.EQUIP_COIN, 0))
        self.as_setBalanceValueS(balanceStr)
