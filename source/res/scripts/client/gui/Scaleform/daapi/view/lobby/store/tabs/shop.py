# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/tabs/shop.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.store.tabs import StoreItemsTab, StoreModuleTab, StoreVehicleTab, StoreShellTab, StoreArtefactTab, StoreOptionalDeviceTab, StoreEquipmentTab
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import moneyWithIcon
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import Currency
from gui.shared.tooltips.formatters import getActionPriceData
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n
from skeletons.gui.game_control import ITradeInController

class ShopItemsTab(StoreItemsTab):
    tradeIn = dependency.descriptor(ITradeInController)

    def _getItemPrice(self, item):
        return item.altPrice or item.buyPrice

    def _getItemDefaultPrice(self, item):
        return item.defaultAltPrice or item.defaultPrice

    def _getItemActionData(self, item):
        actionData = None
        if self._isItemOnDiscount(item):
            actionData = getActionPriceData(item)
        return actionData

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.HIDDEN

    def _isPurchaseEnabled(self, item, money):
        canBuy, _ = item.mayPurchase(money)
        return canBuy

    def _getStatusParams(self, item):
        statusMessage = ''
        money = self._items.stats.money
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

    def _getDiscountCriteria(self):
        if self._actionsSelected:
            return REQ_CRITERIA.DISCOUNT_BUY
        else:
            return REQ_CRITERIA.EMPTY

    def _isItemOnDiscount(self, item):
        return item.actionPrc != 0

    def _getComparator(self):
        """
         If filter discount percent is selected sort items from high to low discount
        """
        if self._actionsSelected:

            def comparator(a, b):
                creditsActionPrcA, goldActionPrcA = self._getActionAllPercents(a)
                creditsActionPrcB, goldActionPrcB = self._getActionAllPercents(b)
                maxPrcA = max(creditsActionPrcA, goldActionPrcA)
                maxPrcB = max(creditsActionPrcB, goldActionPrcB)
                return maxPrcB - maxPrcA

            return comparator
        else:
            return None
            return None


class ShopModuleTab(ShopItemsTab, StoreModuleTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopModuleTab, self)._getRequestCriteria(invVehicles)
        fitsType = self._filterData['fitsType']
        requestTypeIds = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], requestTypeIds)
        elif fitsType != 'otherVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, requestTypeIds)
        return self._getExtraCriteria(self._filterData['extra'], requestCriteria, invVehicles)

    def _getStatusParams(self, item):
        statusMessage = ''
        money = self._items.stats.money
        if not item.isUnlocked:
            statusMessage = MENU.SHOP_ERRORS_UNLOCKNEEDED
            disabled = True
        else:
            disabled = not self._isPurchaseEnabled(item, money)
        return (statusMessage, disabled)


class ShopVehicleTab(ShopItemsTab, StoreVehicleTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.SHOP_VEHICLES_FILTERS_VO_CLASS, True)

    def _getItemPrice(self, item):
        return item.restorePrice if item.isRestorePossible() else super(ShopVehicleTab, self)._getItemPrice(item)

    def _isPurchaseEnabled(self, item, money):
        money = self.tradeIn.addTradeInPriceIfNeeded(item, money)
        mayObtainForMoney, _ = item.mayObtainForMoney(money)
        return True if mayObtainForMoney else item.mayObtainWithMoneyExchange(money, self._items.shop.exchangeRate)

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = REQ_CRITERIA.EMPTY | ~REQ_CRITERIA.CUSTOM(lambda item: item.isHidden and not item.isRestorePossible()) | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        requestCriteria |= self._getVehicleRiterias(self._filterData['selectedTypes'], self._filterData['selectedLevels'])
        return self._getExtraCriteria(self._filterData['extra'], requestCriteria, invVehicles)

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
        money = self._items.stats.money
        if item.getState()[0] == Vehicle.VEHICLE_STATE.RENTAL_IS_OVER:
            statusMessage = '#menu:store/vehicleStates/%s' % item.getState()[0]
            disabled = not self._isPurchaseEnabled(item, money)
        elif BigWorld.player().isLongDisconnectedFromCenter:
            statusMessage = MENU.SHOP_ERRORS_CENTERISDOWN
            disabled = True
        elif item.inventoryCount > 0:
            statusMessage = MENU.SHOP_ERRORS_INHANGAR
            disabled = True
            if not item.isPurchased:
                disabled = not self._isPurchaseEnabled(item, money)
        elif not item.isUnlocked:
            statusMessage = MENU.SHOP_ERRORS_UNLOCKNEEDED
            disabled = True
        else:
            disabled = not self._isPurchaseEnabled(item, money)
        return (statusMessage, disabled)

    def _getDiscountCriteria(self):
        if self._actionsSelected:
            return REQ_CRITERIA.VEHICLE.DISCOUNT_RENT_OR_BUY
        else:
            return REQ_CRITERIA.EMPTY

    def _isItemOnDiscount(self, item):
        return False if item.isRestorePossible() else super(ShopVehicleTab, self)._isItemOnDiscount(item)


class ShopRestoreVehicleTab(ShopVehicleTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.SHOP_VEHICLES_FILTERS_VO_CLASS, False)

    def _getItemPrice(self, item):
        return item.restorePrice

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE
        requestCriteria |= self._getVehicleRiterias(self._filterData['selectedTypes'], self._filterData['selectedLevels'])
        return requestCriteria


class ShopTradeInVehicleTab(ShopVehicleTab):

    @classmethod
    def getFilterInitData(cls):
        return (STORE_CONSTANTS.SHOP_VEHICLES_FILTERS_VO_CLASS, False)

    def itemWrapper(self, packedItem):
        item, _, _ = packedItem
        vo = super(ShopTradeInVehicleTab, self).itemWrapper(packedItem)
        tradeInPrice = ''
        tradeInInfo = self.tradeIn.getTradeInInfo(item)
        if tradeInInfo is not None:
            tradeInPrice = moneyWithIcon(tradeInInfo.maxDiscountPrice, currType=Currency.GOLD)
            if tradeInInfo.hasMultipleTradeOffs:
                tradeInPrice = i18n.makeString(MENU.SHOP_MENU_VEHICLE_TRADEINVEHICLE_PRICE, discountValue=tradeInPrice)
        vo['tradeInPrice'] = tradeInPrice
        vo['isInTradeIn'] = True
        return vo

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.VEHICLE.CAN_TRADE_IN


class ShopShellTab(ShopItemsTab, StoreShellTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopShellTab, self)._getRequestCriteria(invVehicles)
        itemTypes = self._filterData['itemTypes']
        requestCriteria |= REQ_CRITERIA.CUSTOM(lambda item: item.type in itemTypes)
        fitsType = self._filterData['fitsType']
        if fitsType == 'myVehicleGun':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            shellsList = map(lambda x: x.intCD, vehicle.gun.defaultAmmo)
            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        elif fitsType != 'otherGuns':
            shellsList = set()
            myGuns = self._items.getItems(GUI_ITEM_TYPE.GUN, REQ_CRITERIA.INVENTORY).values()
            for gun in myGuns:
                shellsList.update(map(lambda x: x.intCD, gun.defaultAmmo))

            for vehicle in invVehicles:
                shellsList.update(map(lambda x: x.intCD, vehicle.gun.defaultAmmo))

            requestCriteria |= REQ_CRITERIA.IN_CD_LIST(shellsList)
        return requestCriteria


class ShopArtefactTab(ShopItemsTab, StoreArtefactTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopArtefactTab, self)._getRequestCriteria(invVehicles)
        fitsType = self._filterData['fitsType']
        itemTypeID = self._getItemTypeID()
        if fitsType == 'myVehicle':
            vehicle = self._items.getItemByCD(int(self._filterData['vehicleCD']))
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [itemTypeID])
        elif fitsType != 'otherVehicles':
            requestCriteria |= REQ_CRITERIA.VEHICLE.SUITABLE(invVehicles, [itemTypeID])
        return requestCriteria


class ShopOptionalDeviceTab(ShopArtefactTab, StoreOptionalDeviceTab):

    def _getRequestCriteria(self, invVehicles):
        requestCriteria = super(ShopOptionalDeviceTab, self)._getRequestCriteria(invVehicles)
        requestCriteria |= REQ_CRITERIA.OPTIONAL_DEVICE.SIMPLE
        return requestCriteria

    def _isPurchaseEnabled(self, item, money):
        canBuy, _ = item.mayPurchase(money)
        canBuyWithExchange = item.mayPurchaseWithExchange(money, self._items.shop.exchangeRate)
        return canBuy or canBuyWithExchange


class ShopEquipmentTab(ShopArtefactTab, StoreEquipmentTab):
    pass
