# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/tabs/__init__.py
from gui.shared import g_itemsCache
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import CLIP_ICON_PATH, EXTRA_MODULE_INFO
from helpers.i18n import makeString
from items import ITEM_TYPE_INDICES

class StoreItemsTab(object):

    def __init__(self, nation, filtersList):
        self._nation = nation
        self.filterData = self._parseFilter(filtersList)

    def clear(self):
        self._nation = None
        self.filterData = None
        return

    def buildItems(self, invVehicles):
        items = g_itemsCache.items.getItems(self._getItemTypeID(), self._getRequestCriteria(invVehicles), self._nation)
        shopRqs = g_itemsCache.items.shop
        isEnabledBuyingGoldShellsForCredits = shopRqs.isEnabledBuyingGoldShellsForCredits
        isEnabledBuyingGoldEqsForCredits = shopRqs.isEnabledBuyingGoldEqsForCredits
        dataProviderValues = []
        for item in sorted(items.itervalues()):
            extraModuleInfo, vehiclesCount = self._getExtraParams(item, invVehicles)
            statusMessage, disabled = self._getStatusParams(item)
            dataProviderValues.append((item,
             item.inventoryCount,
             vehiclesCount,
             disabled,
             statusMessage,
             isEnabledBuyingGoldShellsForCredits,
             isEnabledBuyingGoldEqsForCredits,
             extraModuleInfo))

        return dataProviderValues

    def itemWrapper(self, packedItem):
        item, inventoryCount, vehicleCount, disable, statusMessage, isEnabledBuyingGoldShellsForCredits, isEnabledBuyingGoldEqsForCredits, extraModuleInfo = packedItem
        money = g_itemsCache.items.stats.money
        return {'id': str(item.intCD),
         'name': self._getItemName(item),
         'desc': item.getShortInfo(),
         'inventoryId': self._getItemInventoryID(item),
         'inventoryCount': inventoryCount,
         'vehicleCount': vehicleCount,
         'credits': money.credits,
         'gold': money.gold,
         'price': self._getItemPrice(item),
         'currency': self._getCurrency(item),
         'level': item.level,
         'nation': item.nationID,
         'type': self._getItemType(item),
         'disabled': disable,
         'statusMessage': statusMessage,
         'statusLevel': self._getItemStatusLevel(item),
         'removable': self._isItemRemovable(item),
         'tankType': self._getTankType(item),
         'isPremium': self._isItemPremium(item),
         'isElite': self._isItemElite(item),
         'itemTypeName': item.itemTypeName,
         'goldShellsForCredits': isEnabledBuyingGoldShellsForCredits,
         'goldEqsForCredits': isEnabledBuyingGoldEqsForCredits,
         'actionPriceData': self._getItemActionData(item),
         'rentLeft': self._getItemRentLeftTime(item),
         'moduleLabel': item.getGUIEmblemID(),
         EXTRA_MODULE_INFO: extraModuleInfo}

    def _isItemPremium(self, item):
        return False

    def _isItemElite(self, item):
        return False

    def _getTankType(self, item):
        return None

    def _isItemRemovable(self, item):
        return True

    def _getItemType(self, item):
        return item.icon

    def _getItemInventoryID(self, item):
        return None

    def _getItemRentLeftTime(self, item):
        pass

    def _getItemActionData(self, item):
        return None

    def _getItemName(self, item):
        return item.longUserName

    def _getExtraParams(self, item, invVehicles):
        return (None, 0)

    def _getStatusParams(self, item):
        return ('', False)

    def _getItemStatusLevel(self, item):
        raise NotImplementedError

    def _getItemTypeID(self):
        raise NotImplementedError

    def _getRequestCriteria(self, invVehicles):
        raise NotImplementedError

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        raise NotImplementedError

    def _getItemPrice(self, item):
        raise NotImplementedError

    def _getCurrency(self, item):
        raise NotImplementedError

    def _parseFilter(self, filtersList):
        raise NotImplementedError


class StoreModuleTab(StoreItemsTab):

    def _getItemTypeID(self):
        return tuple(self.filterData['requestTypeIds'])

    def _getExtraParams(self, item, invVehicles):
        extraModuleInfo = None
        if item.itemTypeID == GUI_ITEM_TYPE.GUN and item.isClipGun():
            extraModuleInfo = CLIP_ICON_PATH
        installedVehicles = item.getInstalledVehicles(invVehicles)
        return (extraModuleInfo, len(installedVehicles))

    def _parseFilter(self, filtersList):
        typeSize = int(filtersList.pop(0))
        requestType = filtersList[0:typeSize]
        requestTypeIds = map(lambda x: ITEM_TYPE_INDICES[x], requestType)
        filtersList = filtersList[typeSize:]
        fitsType = filtersList.pop(0)
        vehicleCD = filtersList.pop(0)
        extra = filtersList[:]
        return {'extra': extra,
         'vehicleCD': vehicleCD,
         'fitsType': fitsType,
         'requestTypeIds': requestTypeIds}

    def _getItemType(self, item):
        return item.itemTypeName


class StoreVehicleTab(StoreItemsTab):

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    def _parseFilter(self, filtersList):
        typeSize = int(filtersList.pop(0))
        requestType = filtersList[0:typeSize]
        extra = filtersList[typeSize:]
        return {'extra': extra,
         'requestType': requestType}

    def _getItemRentLeftTime(self, item):
        if item.isRented:
            formatter = RentLeftFormatter(item.rentInfo, item.isPremiumIGR)
            return formatter.getRentLeftStr('#tooltips:vehicle/rentLeft/%s', formatter=lambda key, countType, count, _=None: ''.join([makeString(key % countType), ': ', str(count)]))
        else:
            return None

    def _getTankType(self, item):
        return item.type

    def _isItemPremium(self, item):
        return item.isPremium

    def _isItemElite(self, item):
        return item.isElite


class StoreShellTab(StoreItemsTab):

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.SHELL

    def _parseFilter(self, filtersList):
        filterSize = int(filtersList.pop(0))
        requestType = filtersList[0:filterSize]
        filtersList = filtersList[filterSize:]
        fitsType = filtersList.pop(0)
        vehicleCD = filtersList.pop(0)
        return {'vehicleCD': vehicleCD,
         'requestType': requestType,
         'fitsType': fitsType}


class StoreArtefactTab(StoreItemsTab):

    def _parseFilter(self, filtersList):
        fitsType = filtersList.pop(0)
        vehicleCD = filtersList.pop(0)
        extra = filtersList
        return {'vehicleCD': vehicleCD,
         'extra': extra,
         'fitsType': fitsType}

    def _getItemName(self, item):
        return item.userName


class StoreOptionalDeviceTab(StoreArtefactTab):

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE

    def _isItemRemovable(self, item):
        return item.isRemovable


class StoreEquipmentTab(StoreArtefactTab):

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.EQUIPMENT
