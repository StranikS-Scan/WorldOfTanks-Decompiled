# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/tabs/shop.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.store.tabs import StoreItemsTab, StoreModuleTab, StoreVehicleTab, StoreShellTab, StoreArtefactTab, StoreOptionalDeviceTab, StoreEquipmentTab
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips.formatters import getActionPriceData
from gui.shared.utils.requesters import REQ_CRITERIA

class ShopItemsTab(StoreItemsTab):

    def _getItemPrice(self, item):
        return item.rentOrBuyPrice

    def _getCurrency(self, item):
        return item.rentOrBuyPrice.getCurrency()

    def _getItemActionData(self, item):
        return getActionPriceData(item)

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.HIDDEN

    def _isPurchaseEnabled(self, item, money):
        canBuy, buyReason = item.mayPurchase(money)
        canRentOrBuy, rentReason = item.mayRentOrBuy(money)
        canBuyWithExchange = item.mayPurchaseWithExchange(money, g_itemsCache.items.shop.exchangeRate)
        if not canRentOrBuy:
            if not canBuy and buyReason == 'credits_error':
                if item.itemTypeID in (GUI_ITEM_TYPE.VEHICLE, GUI_ITEM_TYPE.OPTIONALDEVICE):
                    return canBuyWithExchange
            return canBuy
        return canRentOrBuy

    def _getStatusParams(self, item):
        statusMessage = ''
        money = g_itemsCache.items.stats.money
        return (statusMessage, not self._isPurchaseEnabled(item, money))

    def _getItemStatusLevel(self, item):
        return Vehicle.VEHICLE_STATE_LEVEL.WARNING

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        if 'locked' not in extra:
            requestCriteria |= REQ_CRITERIA.UNLOCKED
        if 'inHangar' not in extra:
            requestCriteria |= ~REQ_CRITERIA.INVENTORY
        if 'onVehicle' not in extra:
            requestCriteria |= ~REQ_CRITERIA.CUSTOM(lambda item: item.getInstalledVehicles(invVehicles))
        return requestCriteria


class ShopModuleTab(ShopItemsTab, StoreModuleTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopModuleTab, self)._getRequestCriteria(invVehicles)
        fitsType = self.filterData['fitsType']
        requestTypeIds = self.filterData['requestTypeIds']
        if fitsType == 'myVehicle':
            vehicle = g_itemsCache.items.getItemByCD(int(self.filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], requestTypeIds)
        elif fitsType != 'otherVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, requestTypeIds)
        return self._getExtraCriteria(self.filterData['extra'], requestCriteria, invVehicles)

    def _getStatusParams(self, item):
        statusMessage = ''
        money = g_itemsCache.items.stats.money
        if not item.isUnlocked:
            statusMessage = MENU.SHOP_ERRORS_UNLOCKNEEDED
            disabled = True
        else:
            disabled = not self._isPurchaseEnabled(item, money)
        return (statusMessage, disabled)


class ShopVehicleTab(ShopItemsTab, StoreVehicleTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopVehicleTab, self)._getRequestCriteria(invVehicles)
        requestCriteria = requestCriteria | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        requestType = self.filterData['requestType']
        extra = self.filterData['extra']
        if 'all' not in requestType:
            requestType = map(lambda x: x.lower(), requestType)
            requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type.lower() in requestType)
        return self._getExtraCriteria(extra, requestCriteria, invVehicles)

    def _getExtraCriteria(self, extra, requestCriteria, invVehicles):
        if 'locked' not in extra:
            requestCriteria |= REQ_CRITERIA.UNLOCKED
        if 'inHangar' not in extra:
            requestCriteria |= ~REQ_CRITERIA.CUSTOM(lambda item: item.inventoryCount > 0 and not item.isRented)
        if 'rentals' not in extra:
            requestCriteria |= ~REQ_CRITERIA.VEHICLE.RENT
        return requestCriteria

    def _getStatusParams(self, item):
        statusMessage = ''
        money = g_itemsCache.items.stats.money
        if item.getState()[0] == Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER:
            statusMessage = '#menu:store/vehicleStates/%s' % item.getState()[0]
            disabled = not self._isPurchaseEnabled(item, money)
        elif BigWorld.player().isLongDisconnectedFromCenter:
            statusMessage = MENU.SHOP_ERRORS_CENTERISDOWN
            disabled = True
        elif item.inventoryCount > 0:
            statusMessage = MENU.SHOP_ERRORS_INHANGAR
            disabled = True
            if item.isRentable:
                disabled = not self._isPurchaseEnabled(item, money)
        elif not item.isUnlocked:
            statusMessage = MENU.SHOP_ERRORS_UNLOCKNEEDED
            disabled = True
        else:
            disabled = not self._isPurchaseEnabled(item, money)
        return (statusMessage, disabled)


class ShopShellTab(ShopItemsTab, StoreShellTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopShellTab, self)._getRequestCriteria(invVehicles)
        requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type in self.filterData['requestType'])
        fitsType = self.filterData['fitsType']
        if fitsType == 'myVehicleGun':
            vehicle = g_itemsCache.items.getItemByCD(int(self.filterData['vehicleCD']))
            shellsList = map(lambda x: x.intCD, vehicle.gun.defaultAmmo)
            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        elif fitsType != 'otherGuns':
            shellsList = set()
            myGuns = g_itemsCache.items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
            for gun in myGuns:
                shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

            for vehicle in invVehicles:
                shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        return requestCriteria


class ShopArtefactTab(ShopItemsTab, StoreArtefactTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopArtefactTab, self)._getRequestCriteria(invVehicles)
        fitsType = self.filterData['fitsType']
        itemTypeID = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = g_itemsCache.items.getItemByCD(int(self.filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [itemTypeID])
        elif fitsType != 'otherVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, [itemTypeID])
        return requestCriteria


class ShopOptionalDeviceTab(ShopArtefactTab, StoreOptionalDeviceTab):
    pass


class ShopEquipmentTab(ShopArtefactTab, StoreEquipmentTab):
    pass
