# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/tabs/__init__.py
import constants
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import RentLeftFormatter, getTimeLeftInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.gui_item_economics import ITEM_PRICES_EMPTY
from gui.shared.money import MONEY_UNDEFINED, Currency, Money
from gui.shared.utils import EXTRA_MODULE_INFO
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import i18n, time_utils, dependency
from helpers.i18n import makeString
from items import ITEM_TYPE_INDICES
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

def _getBtnVehCompareData(vehicle):
    comparisonBasket = dependency.instance(IVehicleComparisonBasket)
    state, tooltip = resolveStateTooltip(comparisonBasket, vehicle, enabledTooltip=VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_ADDTOCOMPARE, fullTooltip=VEH_COMPARE.STORE_COMPAREVEHICLEBTN_TOOLTIPS_DISABLED)
    return {'modeAvailable': comparisonBasket.isEnabled(),
     'btnEnabled': state,
     'btnTooltip': tooltip}


class StoreItemsTab(object):

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def __init__(self, nation, filtersData, actionsSelected, itemCD, itemsCache=None):
        self._nation = nation
        self._filterData = filtersData
        self._actionsSelected = actionsSelected
        self._itemCD = itemCD
        self._items = itemsCache.items
        self._scrollIdx = 0
        self._hasDiscounts = False

    def clear(self):
        self._nation = None
        self._filterData = None
        self._items = None
        self._actionsSelected = False
        self._itemCD = None
        self._scrollIdx = 0
        self._hasDiscounts = False
        return

    def getScrollIdx(self):
        return self._scrollIdx

    def hasDiscounts(self):
        return self._hasDiscounts

    def buildItems(self, invVehicles):
        criteria = self._getRequestCriteria(invVehicles) | self._getDiscountCriteria()
        items = self._items.getItems(self._getItemTypeID(), criteria, self._nation)
        dataProviderValues = []
        for idx, item in enumerate(sorted(items.itervalues(), cmp=self._getComparator())):
            if self._itemCD and item.intCD == self._itemCD:
                self._scrollIdx = idx
            if self._isItemOnDiscount(item):
                self._hasDiscounts = True
            extraModuleInfo, installedVehiclesCount = self._getExtraParams(item, invVehicles)
            dataProviderValues.append((item, extraModuleInfo, installedVehiclesCount))

        return dataProviderValues

    def itemWrapper(self, packedItem):
        item, extraModuleInfo, installedVehiclesCount = packedItem
        statusMessage, disabled, statusImgSrc, isCritLvl = self.__getStatusInfo(item)
        money = self._items.stats.money
        shop = self._items.shop
        prices = self._getItemPrices(item)
        actionPrcs = self._getActionAllPercents(item)
        showActionGoldAndCredits = False
        actionPercent = []
        if actionPrcs.isDefined():
            actionPrices = []
            for currency in Currency.ALL:
                actionPrice = actionPrcs.get(currency, None)
                if actionPrice is not None:
                    actionPrices.append(actionPrice)
                    actionPrcValue = actionPrice
                else:
                    actionPrcValue = 0
                actionPercent.append('-{}'.format(actionPrcValue))

            showActionGoldAndCredits = not actionPrices.count(actionPrices[0]) == len(actionPrices)
        return {'id': str(item.intCD),
         'name': self._getItemName(item),
         'desc': item.getShortInfo(),
         'inventoryId': self._getItemInventoryID(item),
         'inventoryCount': item.inventoryCount,
         'vehicleCount': installedVehiclesCount,
         Currency.CREDITS: money.getSignValue(Currency.CREDITS),
         Currency.GOLD: money.getSignValue(Currency.GOLD),
         Currency.CRYSTAL: money.getSignValue(Currency.CRYSTAL),
         'price': prices.getSum().price.toMoneyTuple(),
         'currency': prices.itemPrice.getCurrency(byWeight=False),
         'level': item.level,
         'nation': item.nationID,
         'type': self._getItemTypeIcon(item),
         'disabled': disabled,
         'statusMessage': statusMessage,
         'isCritLvl': isCritLvl,
         'statusImgSrc': statusImgSrc,
         'removable': item.isRemovable,
         'itemTypeName': item.itemTypeName,
         'goldShellsForCredits': shop.isEnabledBuyingGoldShellsForCredits,
         'goldEqsForCredits': shop.isEnabledBuyingGoldEqsForCredits,
         'actionPriceData': self._getItemActionData(item),
         'moduleLabel': item.getGUIEmblemID(),
         EXTRA_MODULE_INFO: extraModuleInfo,
         'vehCompareData': _getBtnVehCompareData(item) if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE else {},
         'highlightType': self._getItemHighlightType(item),
         'showActionGoldAndCredits': showActionGoldAndCredits,
         'actionPercent': actionPercent,
         'notForSaleText': '' if item.isForSale else MENU.SHOP_TABLE_NOTFORSALE}

    def _getItemTypeIcon(self, item):
        return item.icon

    def _getItemHighlightType(self, item):
        return SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def _getItemInventoryID(self, item):
        return None

    def _getItemActionData(self, item):
        return None

    def _getItemName(self, item):
        return item.longUserName

    def _getExtraParams(self, item, invVehicles):
        return (None, 0)

    def _getStatusParams(self, item):
        return ('', False)

    def _getStatusImg(self, item):
        pass

    def _getItemPrices(self, item):
        return ITEM_PRICES_EMPTY

    def _getComparator(self):
        return None

    def _getItemStatusLevel(self, item):
        raise NotImplementedError

    def _getItemTypeID(self):
        raise NotImplementedError

    def _getRequestCriteria(self, invVehicles):
        raise NotImplementedError

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        raise NotImplementedError

    def _getDiscountCriteria(self):
        raise NotImplementedError

    def _isItemOnDiscount(self, item):
        raise NotImplementedError

    @classmethod
    def getFilterInitData(cls):
        raise NotImplementedError

    @classmethod
    def getTableType(cls):
        raise NotImplementedError

    def __getStatusInfo(self, item):
        isCritLvl = self._getItemStatusLevel(item) == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        statusMessage, disabled = self._getStatusParams(item)
        if statusMessage:
            statusImgSrc = self._getStatusImg(item)
            styledStatus = text_styles.vehicleStatusCriticalText(statusMessage) if isCritLvl else text_styles.vehicleStatusInfoText(statusMessage)
        else:
            statusImgSrc = ''
            styledStatus = ''
        return (styledStatus,
         disabled,
         statusImgSrc,
         isCritLvl)

    def _getActionAllPercents(self, item):
        rentPrcs = self._getRentPercents(item)
        if rentPrcs.isDefined():
            return rentPrcs
        itemPrice = self._getItemPrices(item).getSum()
        return itemPrice.getActionPrcAsMoney()

    def _getRentPercents(self, item):
        if item.isRentable and item.isRentAvailable:
            minRentPricePackage = item.getRentPackage()
            if minRentPricePackage:
                actionPrc = item.getRentPackageActionPrc(minRentPricePackage['rentID'])
                if actionPrc > 0:
                    return Money(gold=actionPrc)
        return MONEY_UNDEFINED


class StoreModuleTab(StoreItemsTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.EXT_FIT_ITEMS_FILTERS_VO_CLASS, False)

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.MODULE

    def _getItemTypeID(self):
        return tuple((ITEM_TYPE_INDICES[x] for x in self._filterData['itemTypes']))

    def _getExtraParams(self, item, invVehicles):
        installedVehicles = item.getInstalledVehicles(invVehicles)
        return (item.getExtraIconInfo(), len(installedVehicles))

    def _getItemTypeIcon(self, item):
        return item.itemTypeName


class StoreVehicleTab(StoreItemsTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.VEHICLES_FILTERS_VO_CLASS, True)

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.VEHICLE

    def itemWrapper(self, packedItem):
        item, _, _ = packedItem
        vo = super(StoreVehicleTab, self).itemWrapper(packedItem)
        vo.update({'tankType': item.type,
         'isPremium': item.isPremium,
         'isElite': item.isElite,
         'rentLeft': self.__getItemRentInfo(item),
         'restoreInfo': self.__getItemRestoreInfo(item),
         'canTradeIn': item.canTradeIn})
        return vo

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.VEHICLE

    def _getVehicleRiterias(self, selectedTypes, selectedLevels):
        requestCriteria = REQ_CRITERIA.EMPTY
        selectedVehiclesIds = []
        for idx, vehicleType in enumerate(VEHICLE_TYPES_ORDER):
            if selectedTypes[idx]:
                selectedVehiclesIds.append(vehicleType)

        if selectedVehiclesIds:
            requestCriteria |= REQ_CRITERIA.VEHICLE.CLASSES(selectedVehiclesIds)
        selectedLevelIds = []
        for level in VEHICLE_LEVELS:
            if selectedLevels[level - 1]:
                selectedLevelIds.append(level)

        if selectedLevelIds:
            requestCriteria |= REQ_CRITERIA.VEHICLE.LEVELS(selectedLevelIds)
        return requestCriteria

    def __getItemRestoreInfo(self, item):
        if item.isRestorePossible():
            if constants.IS_CHINA and item.rentalIsActive:
                return text_styles.alert(MENU.VEHICLE_RESTORELEFT_DISABLEDBYRENT)
            if item.hasLimitedRestore():
                restoreLeftTime = item.restoreInfo.getRestoreTimeLeft()
                timeKey, formattedTime = getTimeLeftInfo(restoreLeftTime)
                msg = i18n.makeString('#menu:vehicle/restoreLeft/%s' % timeKey, time=formattedTime)
                if restoreLeftTime < time_utils.ONE_DAY:
                    return '{} {}'.format(icons.alert(), text_styles.alert(msg))
                return text_styles.stats(msg)
            if item.hasRestoreCooldown():
                timeKey, formattedTime = getTimeLeftInfo(item.restoreInfo.getRestoreCooldownTimeLeft())
                msg = i18n.makeString('#menu:vehicle/restoreCooldownLeft/%s' % timeKey, time=formattedTime)
                return text_styles.stats(msg)

    def __getItemRentInfo(self, item):
        if item.isRented:
            formatter = RentLeftFormatter(item.rentInfo, item.isPremiumIGR)
            return formatter.getRentLeftStr('#tooltips:vehicle/rentLeft/%s', formatter=lambda key, countType, count, _=None: ''.join([makeString(key % countType), ': ', str(count)]))
        elif item.isRentable and item.isRentAvailable:
            minRentPricePackage = item.getRentPackage()
            priceText = ''
            discountText = ''
            if minRentPricePackage:
                minRentPriceValue = minRentPricePackage['rentPrice']
                actionPrc = item.getRentPackageActionPrc(minRentPricePackage['rentID'])
                currency = minRentPriceValue.getCurrency()
                price = minRentPriceValue.getSignValue(currency)
                priceText = makeHtmlString('html_templates:lobby/quests/actions', currency, {'value': price})
                if actionPrc != 0:
                    discountText = makeString('#menu:shop/menu/vehicle/rent/discount', discount=text_styles.gold('{} %'.format(actionPrc)))
            rentText = makeString('#menu:shop/menu/vehicle/rent/available', price=priceText)
            return '{}  {}'.format(rentText, discountText)
        else:
            return ''


class StoreShellTab(StoreItemsTab):

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.SHELL

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.EXT_FIT_ITEMS_FILTERS_VO_CLASS, False)

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.SHELL


class StoreArtefactTab(StoreItemsTab):

    def _getExtraParams(self, item, invVehicles):
        return (None, len(item.getInstalledVehicles(invVehicles)))

    def _parseFilter(self, filtersList):
        fitsType = filtersList.pop(0)
        vehicleCD = filtersList.pop(0)
        extra = filtersList
        return {'vehicleCD': vehicleCD,
         'extra': extra,
         'fitsType': fitsType}

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.FIT_ITEMS_FILTERS_VO_CLASS, False)

    def _getItemName(self, item):
        return item.userName


class StoreOptionalDeviceTab(StoreArtefactTab):

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.OPTIONAL_DEVICE

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE

    def _isItemRemovable(self, item):
        return item.isRemovable

    def _getItemHighlightType(self, item):
        return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS if item.isDeluxe() else super(StoreOptionalDeviceTab, self)._getItemHighlightType(item)


class StoreEquipmentTab(StoreArtefactTab):

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.EQUIPMENT

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.EQUIPMENT

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(StoreEquipmentTab, self)._getRequestCriteria(invVehicles)
        requestCriteria |= REQ_CRITERIA.EQUIPMENT.BUILTIN
        return requestCriteria


class StoreBattleBoosterTab(StoreArtefactTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.BATTLE_BOOSTER_FILTER_VO_CLASS, False)

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.BATTLE_BOOSTER

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.BATTLE_BOOSTER

    def _getItemHighlightType(self, item):
        return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER

    def _parseFilter(self, filtersList):
        extra = filtersList
        return {'extra': extra}

    def _getRequestCriteria(self, invVehicles):
        targetType = self._filterData['targetType']
        if targetType == STORE_CONSTANTS.FOR_EQUIPMENT_FIT:
            return REQ_CRITERIA.BATTLE_BOOSTER.OPTIONAL_DEVICE_EFFECT
        return REQ_CRITERIA.BATTLE_BOOSTER.CREW_EFFECT if targetType == STORE_CONSTANTS.FOR_CREW_FIT else REQ_CRITERIA.BATTLE_BOOSTER.ALL


class StoreCrewBookTab(StoreArtefactTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.CREW_BOOK_FILTER_VO_CLASS, False)

    @classmethod
    def getTableType(cls):
        return STORE_CONSTANTS.CREW_BOOKS

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.CREW_BOOKS
