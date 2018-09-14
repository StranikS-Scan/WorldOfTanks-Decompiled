# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/Inventory.py
from account_helpers.AccountSettings import AccountSettings
from constants import IS_RENTALS_ENABLED
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import getNationIndex, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips import getItemActionTooltipData
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.meta.InventoryMeta import InventoryMeta
from gui.Scaleform.genConsts.STORE_TYPES import STORE_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from gui.shared.utils import CLIP_ICON_PATH, EXTRA_MODULE_INFO
from gui.shared import g_itemsCache, REQ_CRITERIA, event_dispatcher as shared_event_dispatcher
from adisp import process
from helpers.i18n import makeString
from items import ITEM_TYPE_INDICES
from items import vehicles

class Inventory(InventoryMeta):

    def __init__(self, ctx = None):
        super(Inventory, self).__init__(ctx)
        self.__tableType = None
        return

    def _populate(self):
        g_clientUpdateManager.addCallbacks({'': self._onTableUpdate})
        super(Inventory, self)._populate()

    def getName(self):
        return STORE_TYPES.INVENTORY

    def _dispose(self):
        super(Inventory, self)._dispose()
        self._clearTableData()
        self.__tableType = None
        return

    def _update(self, *args):
        self.as_updateS()

    @process
    def __sellItem(self, itemTypeCompactDescr):
        isOk, args = yield DialogsInterface.showDialog(SellModuleMeta(itemTypeCompactDescr))
        LOG_DEBUG('Sell module confirm dialog results', isOk, args)

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
                if type == self._VEHICLE and 'brocken' not in extra:
                    if module.repairCost > 0:
                        continue
                if type == self._VEHICLE and 'locked' not in extra:
                    if not module.isUnlocked:
                        continue
                if type == self._VEHICLE and 'premiumIGR' not in extra:
                    if module.isPremiumIGR:
                        continue
                if type == self._VEHICLE and IS_RENTALS_ENABLED and 'rentals' not in extra:
                    if module.isRented and not module.isPremiumIGR:
                        continue
                if 'onVehicle' in extra:
                    if vehicleCount == 0 and inventoryCount == 0:
                        continue
            disable = False
            statusMessage = ''
            if type == self._VEHICLE:
                if module.getState()[0] in (Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER, Vehicle.VEHICLE_STATE.IGR_RENTAL_IS_ORVER) or not module.canSell:
                    statusMessage = makeString('#menu:store/vehicleStates/%s' % module.getState()[0])
                    disable = not module.canSell
            elif type in (self._MODULE, self._OPTIONAL_DEVICE, self._EQUIPMENT) and not module.isInInventory:
                if type == self._OPTIONAL_DEVICE:
                    if not module.descriptor['removable']:
                        statusMessage = makeString(MENU.INVENTORY_DEVICE_ERRORS_NOT_REMOVABLE)
                        disable = True
                    else:
                        statusMessage = makeString(MENU.INVENTORY_DEVICE_ERRORS_RESERVED)
                        disable = True
                else:
                    statusMessage = makeString(MENU.INVENTORY_ERRORS_RESERVED)
                    disable = True
            dataProviderValues.append((module,
             inventoryCount,
             vehicleCount,
             disable,
             statusMessage,
             isEnabledBuyingGoldShellsForCredits,
             isEnabledBuyingGoldEqsForCredits,
             extraModuleInfo))

        self._table.setDataProviderValues(dataProviderValues)
        self._table.as_setGoldS(g_itemsCache.items.stats.gold)
        self._table.as_setCreditsS(g_itemsCache.items.stats.credits)
        self._table.as_setTableTypeS(self.__tableType)
        Waiting.hide('updateInventory')
        return

    def _getRequestParameters(self, nation, type, filter):
        checkExtra = False
        extra = []
        requestCriteria = super(Inventory, self)._getRequestParameters(nation, type, filter)
        inventoryVehicles = g_itemsCache.items.getVehicles(requestCriteria | REQ_CRITERIA.INVENTORY).values()
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
                if not vehicle.hasTurrets:
                    requestCriteria |= ~REQ_CRITERIA.IN_CD_LIST([vehicle.turret.intCD])
            elif fitsType == 'myVehicles':
                requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(inventoryVehicles, requestTypeIds)
            else:
                requestCriteria |= ~REQ_CRITERIA.VEHICLE.SUITABLE(inventoryVehicles, requestTypeIds)
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
            elif fitsType == 'myVehiclesInventoryGuns':
                shellsList = set()
                myGuns = g_itemsCache.items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
                for gun in myGuns:
                    shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

                for vehicle in inventoryVehicles:
                    shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

                requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
            else:
                shellsList = set()
                myGuns = g_itemsCache.items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
                for gun in myGuns:
                    shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

                for vehicle in inventoryVehicles:
                    shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

                requestCriteria |= ~REQ_CRITERIA.IN_CD_LIST(shellsList)
        elif type == self._VEHICLE:
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
            elif fitsType == 'myVehicles':
                requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(inventoryVehicles, [itemTypeID])
            else:
                requestCriteria |= ~REQ_CRITERIA.VEHICLE.SUITABLE(inventoryVehicles, [itemTypeID])
        if not checkExtra or 'onVehicle' not in extra:
            requestCriteria |= REQ_CRITERIA.INVENTORY
        return (itemTypeID,
         requestCriteria,
         inventoryVehicles,
         checkExtra,
         extra)

    def itemWrapper(self, packedItem):
        module, inventoryCount, vehicleCount, disable, statusMessage, isEnabledBuyingGoldShellsForCredits, isEnabledBuyingGoldEqsForCredits, extraModuleInfo = packedItem
        credits, gold = g_itemsCache.items.stats.money
        statusLevel = Vehicle.VEHICLE_STATE_LEVEL.INFO
        inventoryId = None
        isRented = False
        rentLeftTimeStr = ''
        if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            statusLevel = module.getState()[1]
            if module.isRented:
                isRented = True
                formatter = RentLeftFormatter(module.rentInfo, module.isPremiumIGR)
                rentLeftTimeStr = formatter.getRentLeftStr('#tooltips:vehicle/rentLeft/%s', formatter=lambda key, countType, count, _ = None: ''.join([makeString(key % countType), ': ', str(count)]))
            if module.isInInventory:
                inventoryId = module.invID
        name = module.userName if module.itemTypeID in GUI_ITEM_TYPE.ARTEFACTS else module.longUserName
        action = None
        if module.sellPrice != module.defaultSellPrice and not isRented:
            action = getItemActionTooltipData(module, False)
        return {'id': str(module.intCD),
         'name': name,
         'desc': module.getShortInfo(),
         'inventoryId': inventoryId,
         'inventoryCount': inventoryCount,
         'vehicleCount': vehicleCount,
         'credits': credits,
         'gold': gold,
         'price': module.sellPrice,
         'currency': 'credits' if module.sellPrice[1] == 0 else 'gold',
         'level': module.level,
         'nation': module.nationID,
         'type': module.itemTypeName if module.itemTypeID not in (GUI_ITEM_TYPE.VEHICLE,
                  GUI_ITEM_TYPE.OPTIONALDEVICE,
                  GUI_ITEM_TYPE.SHELL,
                  GUI_ITEM_TYPE.EQUIPMENT) else module.icon,
         'disabled': disable,
         'statusMessage': statusMessage,
         'statusLevel': statusLevel,
         'removable': module.isRemovable if module.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else True,
         'tankType': module.type if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else None,
         'isPremium': module.isPremium if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else False,
         'isElite': module.isElite if module.itemTypeID == GUI_ITEM_TYPE.VEHICLE else False,
         'itemTypeName': module.itemTypeName,
         'goldShellsForCredits': isEnabledBuyingGoldShellsForCredits,
         'goldEqsForCredits': isEnabledBuyingGoldEqsForCredits,
         'actionPriceData': action,
         'rentLeft': rentLeftTimeStr,
         'moduleLabel': module.getGUIEmblemID(),
         EXTRA_MODULE_INFO: extraModuleInfo}
