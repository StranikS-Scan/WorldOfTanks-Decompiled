# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/restore_devices_view.py
from ItemRestore import getOptionalDeviceRestorePrice
from constants import OPT_DEVICES_RESTORE_SETTING
from gui.Scaleform.daapi.view.lobby.storage import storage_helpers
from gui.Scaleform.daapi.view.lobby.storage.inventory.opt_devices_tab import _OptDeviceTypeFilter
from gui.Scaleform.daapi.view.meta.StorageRestoreDevicesContentMeta import StorageRestoreDevicesContentMeta
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import showStorage
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.Scaleform.daapi.view.lobby.storage.inventory.inventory_view import IN_GROUP_COMPARATOR
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.shared.money import Money, Currency
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from collections import namedtuple
_TYPE_FILTER_ITEMS = [{'id': int(_OptDeviceTypeFilter.ALL),
  'label': backport.text(R.strings.storage.devices.filters.all())},
 {'id': int(_OptDeviceTypeFilter.TROPHY),
  'label': backport.text(R.strings.storage.devices.filters.trophy())},
 {'id': int(_OptDeviceTypeFilter.DELUXE),
  'label': backport.text(R.strings.storage.devices.filters.deluxe())},
 {'id': int(_OptDeviceTypeFilter.MODERNIZED),
  'label': backport.text(R.strings.storage.devices.filters.modernized())}]
RestoreOptDeviceCtx = namedtuple('RestoreOptDeviceCtx', ('device', 'reason', 'count', 'restorePrice'))

class RestoreDevicesContentView(StorageRestoreDevicesContentMeta):

    def __init__(self):
        super(RestoreDevicesContentView, self).__init__()
        self.__goodiesCache = dependency.instance(IGoodiesCache)
        self._devices = []
        self._money = {}
        self.__restoreCtx = {}

    def _populate(self):
        self.__setMoney()
        self.__resetViewData()
        self._devices = self.__collectOptDevices()
        super(RestoreDevicesContentView, self)._populate()

    def _dispose(self):
        self.__resetViewData()
        popoverView = self.app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.STORAGE_VEHICLE_SELECTOR_POPOVER))
        if popoverView is not None:
            popoverView.destroy()
        super(RestoreDevicesContentView, self)._dispose()
        return

    def _getComparator(self):
        optDevComparator = IN_GROUP_COMPARATOR[GUI_ITEM_TYPE.OPTIONALDEVICE]

        def _compareEntries(left, right):
            leftDevice, leftReason = left[0], left[1]
            rightDevice, rightReason = right[0], right[1]
            res = optDevComparator(leftDevice, rightDevice)
            return res or cmp(leftReason, rightReason)

        return _compareEntries

    def _getVoList(self):
        self._totalCount = len(self._devices)
        filterCriteria = self._getFilteredCriteria()
        comparator = self._getComparator()
        voList = []
        for item in sorted(self._devices, cmp=comparator):
            optDev = item[0]
            if filterCriteria(optDev):
                voList.append(self._getVO(item))

        self._currentCount = len(voList)
        return voList

    def _getVO(self, item):
        optDev, reason, count = item
        result = storage_helpers.getDeletedOptDevicesVo(optDev)
        price, isEnoughStatuses, restoreEnabled = self.__getRestorePrice(optDev, reason)
        self.__restoreCtx[optDev.intCD, reason] = RestoreOptDeviceCtx(optDev, reason, count, price)
        result.update({'actionButtonLabel': backport.text(R.strings.storage.buttonLabel.restore()),
         'timerText': backport.text(R.strings.storage.restoreTimeLeft.timeless()),
         'timerIcon': RES_ICONS.MAPS_ICONS_LIBRARY_CLOCKICON_1,
         'availableToRestore': text_styles.concatStylesToSingleLine(text_styles.main(backport.text(R.strings.storage.devices.restore.availableToRestore())), text_styles.stats(count)),
         'price': {'price': price},
         'isEnoughStatuses': isEnoughStatuses,
         'enabled': restoreEnabled,
         'infoTooltipData': {'specialAlias': TOOLTIPS_CONSTANTS.STORAGE_RESTORE_DEVICE_INFO,
                             'specialArgs': [result['id'], reason, price]},
         'restoreReason': reason})
        return result

    def restoreItem(self, itemId, reason):
        from gui.impl.lobby.tank_setup.dialogs.restore_opt_devices import RestoreOptDevicesWindow
        ctx = self.__restoreCtx[int(itemId), int(reason)]
        window = RestoreOptDevicesWindow(ctx, self._money, self.getParentWindow())
        window.load()

    def _getFilterItems(self):
        return _TYPE_FILTER_ITEMS

    def _onServerSettingsChange(self, diff):
        if OPT_DEVICES_RESTORE_SETTING in diff and not self._getOptDevicesRestoreState():
            showStorage(defaultSection=STORAGE_CONSTANTS.STORAGE, tabId=STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT)

    def _onClientUpdate(self, diff, _):
        super(RestoreDevicesContentView, self)._onClientUpdate(diff, _)
        stats = diff.get('stats')
        recycleBin = diff.get('recycleBin')
        if not stats and not recycleBin:
            return
        if stats:
            self.__setMoney()
        if recycleBin:
            self._devices = self.__collectOptDevices()
            if not self._devices:
                showStorage(defaultSection=STORAGE_CONSTANTS.STORAGE, tabId=STORAGE_CONSTANTS.INVENTORY_TAB_EQUIPMENT)
                return
        self._buildItems()

    def __resetViewData(self):
        self._devices = []
        self._totalCount = -1
        self._currentCount = -1
        self._filterMask = int(_OptDeviceTypeFilter.ALL)

    def __collectOptDevices(self):
        items = self._itemsCache.items
        optDevicesDict = items.recycleBin.getOptDevices()
        if not optDevicesDict:
            return []
        else:
            devices = []
            for intCD, counts in optDevicesDict.iteritems():
                optDev = items.getItemByCD(intCD)
                if optDev is None:
                    continue
                for reason, count in enumerate(counts):
                    if count:
                        devices.append((optDev, reason, count))

            return devices

    def __setMoney(self):
        moneyDict = self._itemsCache.items.stats.money.toSignDict()
        dk = self.__goodiesCache.getDemountKit(currency=Currency.GOLD)
        moneyDict[Currency.DEMOUNT_KIT] = dk.count if dk is not None else 0
        self._money = moneyDict
        return

    def __getRestorePrice(self, device, reason, count=1):
        items = self._itemsCache.items
        itemPrice = device.buyPrices.itemPrice.defPrice.toSignDict()
        sellPrice = device.sellPrices.itemPrice.defPrice.toSignDict()
        removalPrice = device.getRemovalPrice(items).price.toSignDict()
        paidRemovalCostGold = items.shop.defaults.paidRemovalCost
        paidRemovalCost = Money(gold=paidRemovalCostGold).toSignDict()
        restorePriceDict = getOptionalDeviceRestorePrice(reason, count, device.isModernized, itemPrice, sellPrice, removalPrice, paidRemovalCost)
        restorePriceDict = self.__normalizeRestorePrice(restorePriceDict, paidRemovalCostGold)
        return self.__buildPriceAndStatuses(restorePriceDict)

    def __normalizeRestorePrice(self, restorePriceDict, paidRemovalCostGold):
        gold = restorePriceDict.get(Currency.GOLD, 0)
        if not gold:
            return restorePriceDict
        else:
            dkBalance = self._money.get(Currency.DEMOUNT_KIT, 0)
            if dkBalance <= 0:
                return restorePriceDict
            if paidRemovalCostGold <= 0 or gold % paidRemovalCostGold != 0:
                return restorePriceDict
            dkNeeded = gold // paidRemovalCostGold
            if dkNeeded <= 0:
                return restorePriceDict
            result = dict(restorePriceDict)
            result.pop(Currency.GOLD, None)
            result[Currency.DEMOUNT_KIT] = dkNeeded
            return result

    def __buildPriceAndStatuses(self, priceDict):
        prices = []
        statuses = []
        allEnough = True
        for cur in Currency.DEMOUNT_ORDER:
            amount = priceDict.get(cur, 0)
            if not amount:
                continue
            prices.append((cur, amount))
            enough = self._money.get(cur, 0) >= amount
            statuses.append((cur, enough))
            allEnough = allEnough and enough

        return (tuple(prices), tuple(statuses), allEnough)
