# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/Shop.py
import BigWorld
from PlayerEvents import g_playerEvents
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.tooltips import getItemActionTooltipData, getItemRentActionTooltipData
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.shared import REQ_CRITERIA, g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from gui.shared.utils import EXTRA_MODULE_INFO, CLIP_ICON_PATH
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from account_helpers.AccountSettings import AccountSettings
from gui import getNationIndex
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.ShopMeta import ShopMeta
from items import ITEM_TYPE_INDICES
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.Vehicle import Vehicle

class Shop(ShopMeta):

    def __init__(self, ctx = None):
        super(Shop, self).__init__(ctx)
        self.__tableType = None
        return

    def _populate(self):
        g_clientUpdateManager.addCallbacks({'stats.credits': self._onTableUpdate,
         'stats.gold': self._onTableUpdate,
         'cache.mayConsumeWalletResources': self._onTableUpdate,
         'inventory.1': self._onTableUpdate})
        g_playerEvents.onCenterIsLongDisconnected += self._update
        super(Shop, self)._populate()

    def _dispose(self):
        super(Shop, self)._dispose()
        self._clearTableData()
        self.__tableType = None
        g_playerEvents.onCenterIsLongDisconnected -= self._update
        return

    def buyItem(self, data):
        itemCD = int(data.id)
        item = g_itemsCache.items.getItemByCD(itemCD)
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_MODULE, itemCD)

    def requestTableData(self, nation, type, filter):
        Waiting.show('updateShop')
        AccountSettings.setFilter('shop_current', (nation, type))
        AccountSettings.setFilter('shop_' + type, filter)
        nation = int(nation) if nation >= 0 else None
        if nation is not None:
            nation = getNationIndex(nation)
        filter = list(filter)
        itemTypeID, requestCriteria, inventoryVehicles, checkExtra, extra = self._getRequestParameters(nation, type, filter)
        modulesAll = g_itemsCache.items.getItems(itemTypeID, requestCriteria, nation)
        shopRqs = g_itemsCache.items.shop
        isEnabledBuyingGoldShellsForCredits = shopRqs.isEnabledBuyingGoldShellsForCredits
        isEnabledBuyingGoldEqsForCredits = shopRqs.isEnabledBuyingGoldEqsForCredits
        self._clearTableData()
        self.__tableType = type
        dataProviderValues = []
        for module in sorted(modulesAll.itervalues()):
            extraModuleInfo = None
            if module.itemTypeID == GUI_ITEM_TYPE.GUN and module.isClipGun():
                extraModuleInfo = CLIP_ICON_PATH
            inventoryCount = 0
            vehicleCount = 0
            if module.isInInventory:
                inventoryCount = 1
                if type != self._VEHICLE:
                    inventoryCount = module.inventoryCount
            if type in (self._MODULE, self._OPTIONAL_DEVICE, self._EQUIPMENT):
                installedVehicles = module.getInstalledVehicles(inventoryVehicles)
                vehicleCount = len(installedVehicles)
            if checkExtra:
                if 'locked' not in extra and type not in (self._OPTIONAL_DEVICE, self._EQUIPMENT):
                    if not module.isUnlocked:
                        continue
                if 'inHangar' not in extra and type not in (self._OPTIONAL_DEVICE, self._EQUIPMENT):
                    if inventoryCount > 0 and not module.isRented:
                        continue
                if type == self._VEHICLE and 'rentals' not in extra:
                    if module.isRented:
                        continue
                if 'onVehicle' not in extra:
                    if vehicleCount > 0:
                        continue
            disabled = False
            statusMessage = ''
            money = g_itemsCache.items.stats.money
            if type == self._VEHICLE:
                if module.getState()[0] == Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER:
                    statusMessage = '#menu:store/vehicleStates/%s' % module.getState()[0]
                    disabled = not self._isPurchaseEnabled(module, money)
                elif BigWorld.player().isLongDisconnectedFromCenter:
                    statusMessage = MENU.SHOP_ERRORS_CENTERISDOWN
                    disabled = True
                elif inventoryCount > 0:
                    statusMessage = MENU.SHOP_ERRORS_INHANGAR
                    disabled = True
                    if module.isRentable:
                        disabled = not self._isPurchaseEnabled(module, money)
                elif not module.isUnlocked:
                    statusMessage = MENU.SHOP_ERRORS_UNLOCKNEEDED
                    disabled = True
                else:
                    disabled = not self._isPurchaseEnabled(module, money)
            elif type not in (self._SHELL, self._OPTIONAL_DEVICE, self._EQUIPMENT) and not module.isUnlocked:
                statusMessage = MENU.SHOP_ERRORS_UNLOCKNEEDED
                disabled = True
            else:
                disabled = not self._isPurchaseEnabled(module, money)
            dataProviderValues.append((module,
             inventoryCount,
             vehicleCount,
             disabled,
             statusMessage,
             isEnabledBuyingGoldShellsForCredits,
             isEnabledBuyingGoldEqsForCredits,
             extraModuleInfo))

        self._table.setDataProviderValues(dataProviderValues)
        self._table.as_setGoldS(g_itemsCache.items.stats.gold)
        self._table.as_setCreditsS(g_itemsCache.items.stats.credits)
        self._table.as_setTableTypeS(self.__tableType)
        Waiting.hide('updateShop')
        return

    def _isPurchaseEnabled(self, item, money):
        canBuy, buyReason = item.mayPurchase(money)
        canRentOrBuy, rentReason = item.mayRentOrBuy(money)
        canBuyWithExchange = item.mayPurchaseWithExchange(money, g_itemsCache.items.shop.exchangeRate)
        if not canRentOrBuy:
            if not canBuy and buyReason == 'credit_error':
                if item.itemTypeID in (GUI_ITEM_TYPE.VEHICLE, GUI_ITEM_TYPE.OPTIONALDEVICE):
                    return canBuyWithExchange
            return canBuy
        return canRentOrBuy

    def requestFilterData(self, filterType):
        self._updateFilterOptions(filterType)

    def _update(self, *args):
        self.as_updateS()

    def getName(self):
        return STORE_TYPES.SHOP

    def _getRequestParameters(self, nation, type, filter):
        checkExtra = False
        extra = []
        requestCriteria = super(Shop, self)._getRequestParameters(nation, type, filter)
        inventoryVehicles = g_itemsCache.items.getVehicles(requestCriteria | REQ_CRITERIA.INVENTORY).values()
        requestCriteria = requestCriteria | ~REQ_CRITERIA.HIDDEN
        if type == self._MODULE:
            typeSize = int(filter.pop(0))
            requestType = filter[0:typeSize]
            requestTypeIds = map(lambda x: ITEM_TYPE_INDICES[x], requestType)
            filter = filter[typeSize:]
            fitsType = filter.pop(0)
            compact = filter.pop(0)
            if not compact:
                LOG_ERROR('compact value has invalid value: ', compact)
                Waiting.hide('updateShop')
                return
            checkExtra = True
            extra = filter[:]
            itemTypeID = tuple(requestTypeIds)
            if fitsType == 'myVehicle':
                vehicle = g_itemsCache.items.getItemByCD(int(compact))
                requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], requestTypeIds)
            elif fitsType != 'otherVehicles':
                requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(inventoryVehicles, requestTypeIds)
        elif type == self._SHELL:
            filterSize = int(filter.pop(0))
            requestType = filter[0:filterSize]
            filter = filter[filterSize:]
            fitsType = filter.pop(0)
            compact = filter.pop(0)
            if not compact:
                LOG_ERROR('compact value has invalid value: ', compact)
                Waiting.hide('updateShop')
                return
            itemTypeID = GUI_ITEM_TYPE.SHELL
            requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type in requestType)
            if fitsType == 'myVehicleGun':
                vehicle = g_itemsCache.items.getItemByCD(int(compact))
                shellsList = map(lambda x: x.intCD, vehicle.gun.defaultAmmo)
                requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
            elif fitsType != 'otherGuns':
                shellsList = set()
                myGuns = g_itemsCache.items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
                for gun in myGuns:
                    shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

                for vehicle in inventoryVehicles:
                    shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

                requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        elif type == self._VEHICLE:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
            typeSize = int(filter.pop(0))
            requestType = filter[0:typeSize]
            extra = filter[typeSize:]
            checkExtra = True
            if 'all' not in requestType:
                requestType = map(lambda x: x.lower(), requestType)
                requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type.lower() in requestType)
            itemTypeID = GUI_ITEM_TYPE.VEHICLE
        else:
            fitsType = filter.pop(0)
            compact = filter.pop(0)
            if not compact:
                LOG_ERROR('compact value has invalid value: ', compact)
                Waiting.hide('updateShop')
                return
            extra = filter
            checkExtra = type in (self._OPTIONAL_DEVICE, self._EQUIPMENT)
            itemTypeID = GUI_ITEM_TYPE_INDICES[type]
            if fitsType == 'myVehicle':
                vehicle = g_itemsCache.items.getItemByCD(int(compact))
                requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [itemTypeID])
            elif fitsType != 'otherVehicles':
                requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(inventoryVehicles, [itemTypeID])
        return (itemTypeID,
         requestCriteria,
         inventoryVehicles,
         checkExtra,
         extra)

    def itemWrapper(self, packedItem):
        module, inventoryCount, vehicleCount, disabled, statusMessage, isEnabledBuyingGoldShellsForCredits, isEnabledBuyingGoldEqsForCredits, extraModuleInfo = packedItem
        credits, gold = g_itemsCache.items.stats.money
        name = module.userName if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS else module.longUserName
        price = module.altPrice or module.buyPrice
        defaultPrice = module.defaultAltPrice or module.defaultPrice
        rentLeftTimeStr = RentLeftFormatter(module.rentInfo).getRentLeftStr()
        minRentPricePackage = module.getRentPackage()
        action = None
        if price != defaultPrice and not minRentPricePackage:
            action = getItemActionTooltipData(module)
        elif minRentPricePackage:
            price = minRentPricePackage['rentPrice']
            if minRentPricePackage['rentPrice'] != minRentPricePackage['defaultRentPrice']:
                action = getItemRentActionTooltipData(module, minRentPricePackage)
        return {'id': str(module.intCD),
         'name': name,
         'desc': module.getShortInfo(),
         'inventoryId': None,
         'inventoryCount': inventoryCount,
         'vehicleCount': vehicleCount,
         'credits': credits,
         'gold': gold,
         'price': price,
         'currency': 'credits' if price[1] == 0 else 'gold',
         'level': module.level,
         'nation': module.nationID,
         'type': module.itemTypeName if module.itemTypeID not in (GUI_ITEM_TYPE.VEHICLE,
                  GUI_ITEM_TYPE.OPTIONALDEVICE,
                  GUI_ITEM_TYPE.SHELL,
                  GUI_ITEM_TYPE.EQUIPMENT) else module.icon,
         'disabled': disabled,
         'statusMessage': statusMessage,
         'statusLevel': Vehicle.VEHICLE_STATE_LEVEL.WARNING,
         'removable': module.isRemovable if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else True,
         'tankType': module.type if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else type,
         'isPremium': module.isPremium if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else False,
         'isElite': module.isElite if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else False,
         'itemTypeName': module.itemTypeName,
         'goldShellsForCredits': isEnabledBuyingGoldShellsForCredits,
         'goldEqsForCredits': isEnabledBuyingGoldEqsForCredits,
         'actionPriceData': action,
         'rentLeft': rentLeftTimeStr,
         'moduleLabel': module.getGUIEmblemID(),
         EXTRA_MODULE_INFO: extraModuleInfo}
