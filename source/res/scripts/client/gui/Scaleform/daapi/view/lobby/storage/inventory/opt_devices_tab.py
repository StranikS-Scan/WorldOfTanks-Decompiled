# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/opt_devices_tab.py
from collections import OrderedDict
from enum import IntEnum
from PlayerEvents import g_playerEvents
from constants import OPT_DEVICES_RESTORE_SETTING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.shared.event_dispatcher import showSellDialog, showShop, showStorageRestoreDevices
from gui.Scaleform.daapi.view.meta.StorageDevicesTabViewMeta import StorageDevicesTabViewMeta
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import TABS_SORT_ORDER, IN_GROUP_COMPARATOR
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyOptionalDevicesUrl
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.money import Currency
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from helpers import dependency

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
_FILTER_ORDER = list(_BIT_TO_DEVICE_TYPE_MAP)
_FILTER_INDEX_BY_MASK = dict(((mask, i + 1) for i, mask in enumerate(_FILTER_ORDER)))

class OptDevicesTabView(StorageDevicesTabViewMeta):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def _populate(self):
        super(OptDevicesTabView, self)._populate()
        self.__updateBalance()
        self.__updateRestoreButton()
        g_playerEvents.onClientUpdated += self._onClientUpdate
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange

    def _dispose(self):
        g_playerEvents.onClientUpdated -= self._onClientUpdate
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        super(OptDevicesTabView, self)._dispose()

    def _getTypeFilters(self, items):
        return {'items': items,
         'minSelectedItems': 0,
         'filterTypeName': backport.text(R.strings.storage.storage.tabs.devices.filter.type.label())}

    def navigateToStore(self):
        showShop(getBuyOptionalDevicesUrl())

    def onRestoreButtonClick(self):
        storageView = self.app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_STORAGE))
        if storageView is not None:
            storageView.destroy()
            showStorageRestoreDevices()
        return

    def upgradeItem(self, itemId):
        optDevice = self._itemsCache.items.getItemByCD(int(itemId))
        if optDevice is None:
            return
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_OPT_DEVICE, optDevice, None, None, None)
            return

    def _initFilter(self):
        index = _FILTER_INDEX_BY_MASK.get(self._filterMask, 0)
        self.as_initModulesFilterS({'enabled': True,
         'selectedIndex': index,
         'data': self._getFilterItems()})

    def _getFilterItems(self):
        return _TYPE_FILTER_ITEMS

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

    def _getRequestCriteria(self, _):
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

    def _onServerSettingsChange(self, diff):
        if OPT_DEVICES_RESTORE_SETTING in diff:
            self.__updateRestoreButton()

    def _getOptDevicesRestoreState(self):
        return self.__lobbyContext.getServerSettings().isOptionalDeviceRestoreEnabled()

    def _onClientUpdate(self, diff, _):
        stats = diff.get('stats')
        if stats and Currency.EQUIP_COIN in stats:
            self.__updateBalance()
        recycleBin = diff.get('recycleBin')
        if recycleBin and 'optional_devices' in recycleBin:
            self.__updateRestoreButton()

    def __updateBalance(self):
        money = self._itemsCache.items.stats.money
        balanceStr = backport.getIntegralFormat(money.get(Currency.EQUIP_COIN, 0))
        self.as_setBalanceValueS(balanceStr)

    def __updateRestoreButton(self):
        deletedCount = self.__getDeletedOptDevicesCount() if self._getOptDevicesRestoreState() else 0
        self.as_setRestoreButtonDataS({'isVisible': deletedCount > 0,
         'counterValue': deletedCount})

    def __getDeletedOptDevicesCount(self):
        optDevicesDict = self._itemsCache.items.recycleBin.getOptDevices()
        return 0 if not optDevicesDict else sum((sum(counts) for counts in optDevicesDict.itervalues()))
