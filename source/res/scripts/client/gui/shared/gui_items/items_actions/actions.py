# Embedded file name: scripts/client/gui/shared/gui_items/items_actions/actions.py
import BigWorld
from items import vehicles
from adisp import process
from gui.shared.utils import decorators
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, DialogsInterface
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared import g_itemsCache, event_dispatcher as shared_events
from gui.shared.gui_items.processors.module import getInstallerProcessor, BuyAndInstallItemProcessor
from gui.shared.gui_items.processors.vehicle import tryToLoadDefaultShellsLayout
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.techtree import unlock
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats, RequestState
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import LocalSellModuleMeta, BuyModuleMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeXpMeta, ExchangeCreditsMeta

def showMessage(scopeMsg, msg, item, msgType = SystemMessages.SM_TYPE.Error, **kwargs):
    kwargs['userString'] = item.userName
    kwargs['type'] = msgType
    if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
        entity = 'vehicle'
    else:
        entity = 'item'
        kwargs['typeString'] = item.userType
    key = scopeMsg.format(entity, msg)
    SystemMessages.pushI18nMessage(key, **kwargs)


def showInventoryMsg(msg, item, msgType = SystemMessages.SM_TYPE.Error, **kwargs):
    scopeMsg = '#system_messages:inventory/{0:>s}/{1:>s}'
    showMessage(scopeMsg, msg, item, msgType=msgType, **kwargs)


def showUnlockMsg(msg, item, msgType = SystemMessages.SM_TYPE.Error, **kwargs):
    scopeMsg = '#system_messages:unlocks/{0:>s}/{1:>s}'
    showMessage(scopeMsg, msg, item, msgType=msgType, **kwargs)


def showShopMsg(msg, item, msgType = SystemMessages.SM_TYPE.Error, **kwargs):
    scopeMsg = '#system_messages:shop/{0:>s}/{1:>s}'
    showMessage(scopeMsg, msg, item, msgType=msgType, **kwargs)


def getGunCD(item, vehicle):
    if item.itemTypeID == GUI_ITEM_TYPE.TURRET:
        if not item.mayInstall(vehicle, gunCD=0)[0]:
            for gun in item.descriptor['guns']:
                gunItem = g_itemsCache.items.getItemByCD(gun['compactDescr'])
                if gunItem.isInInventory:
                    mayInstall = item.mayInstall(vehicle, slotIdx=0, gunCD=gun['compactDescr'])
                    if mayInstall[0]:
                        return gun['compactDescr']

    return 0


def processMsg(result):
    if result and len(result.userMsg):
        SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
    if result and result.auxData:
        for m in result.auxData:
            SystemMessages.pushI18nMessage(m.userMsg, type=m.sysMsgType)


class IGUIItemAction(object):

    def doAction(self):
        pass


class BuyAction(IGUIItemAction):

    def _canBuy(self, item):
        canBuy, _ = item.mayPurchase(g_itemsCache.items.stats.money)
        return canBuy

    def _canBuyWithExchange(self, item):
        money = g_itemsCache.items.stats.money
        canBuy, buyReason = item.mayPurchase(money)
        canRentOrBuy, rentReason = item.mayRentOrBuy(money)
        canBuyWithExchange = item.mayPurchaseWithExchange(money, g_itemsCache.items.shop.exchangeRate)
        if not canRentOrBuy:
            if not canBuy and buyReason == 'credit_error':
                return canBuyWithExchange
            return canBuy
        return canRentOrBuy


class SellItemAction(IGUIItemAction):

    def __init__(self, itemTypeCD):
        super(SellItemAction, self).__init__()
        self.__itemTypeCD = itemTypeCD

    @process
    def doAction(self):
        item = g_itemsCache.items.getItemByCD(self.__itemTypeCD)
        if item.isInInventory:
            yield DialogsInterface.showDialog(LocalSellModuleMeta(self.__itemTypeCD))
        else:
            showInventoryMsg('not_found', item)
            yield lambda callback = None: callback
        return


class ModuleBuyAction(BuyAction):

    def __init__(self, intCD):
        super(ModuleBuyAction, self).__init__()
        self.__intCD = intCD

    @process
    def doAction(self):
        item = g_itemsCache.items.getItemByCD(self.__intCD)
        if not self._canBuy(item):
            if self._canBuyWithExchange(item):
                isOk, args = yield DialogsInterface.showDialog(ExchangeCreditsMeta(self.__intCD))
                if not isOk:
                    return
            else:
                showShopMsg('common_rent_or_buy_error', item)
        if self._canBuy(item):
            yield DialogsInterface.showDialog(BuyModuleMeta(self.__intCD, g_itemsCache.items.stats.money))
        else:
            yield lambda callback = None: callback
        return


class VehicleBuyAction(BuyAction):

    def __init__(self, vehCD):
        super(VehicleBuyAction, self).__init__()
        self.__vehCD = vehCD

    @process
    def doAction(self):
        item = g_itemsCache.items.getItemByCD(self.__vehCD)
        if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
            LOG_ERROR('Value of int-type descriptor is not refer to vehicle', self.__vehCD)
            return
        else:
            if item.isInInventory and not item.isRented:
                showInventoryMsg('already_exists', item, msgType=SystemMessages.SM_TYPE.Warning)
            else:
                price = item.minRentPrice or item.buyPrice
                if price is None:
                    showShopMsg('not_found', item)
                    return
                if not self._canRentOrBuy(item):
                    if self._canBuyWithExchange(item):
                        isOk, args = yield DialogsInterface.showDialog(ExchangeCreditsMeta(self.__vehCD))
                        if not isOk:
                            return
                    else:
                        showShopMsg('common_rent_or_buy_error', item)
                if self._canRentOrBuy(item):
                    shared_events.showVehicleBuyDialog(item)
                yield lambda callback = None: callback
            return

    def _canRentOrBuy(self, item):
        canRentOrBuy, reason = item.mayRentOrBuy(g_itemsCache.items.stats.money)
        LOG_DEBUG('canRentOrBuy, reason', canRentOrBuy, reason)
        return canRentOrBuy


class UnlockItemAction(IGUIItemAction):

    def __init__(self, unlockCD, vehCD, unlockIdx, xpCost):
        super(UnlockItemAction, self).__init__()
        self.__unlockCD = unlockCD
        self.__vehCD = vehCD
        self.__unlockIdx = unlockIdx
        self.__xpCost = xpCost

    @process
    def doAction(self):
        if not self._isEnoughXpToUnlock():
            isOk, args = yield DialogsInterface.showDialog(ExchangeXpMeta(self.__unlockCD, self.__vehCD, self.__xpCost))
            if isOk and self._isEnoughXpToUnlock() and not self._isUnlocked():
                self._unlockItem()
        else:
            self._unlockItem()

    def _unlockItem(self):
        costCtx = self._getCostCtx(self.__vehCD, self.__xpCost)
        unlockCtx = unlock.UnlockItemCtx(self.__unlockCD, self.__vehCD, self.__unlockIdx, self.__xpCost)
        plugins = [unlock.UnlockItemConfirmator(unlockCtx, costCtx), unlock.UnlockItemValidator(unlockCtx)]
        self._doUnlockItem(unlockCtx, costCtx, plugins)

    def _isUnlocked(self):
        item = g_itemsCache.items.getItemByCD(self.__unlockCD)
        return item.isUnlocked

    def _isEnoughXpToUnlock(self):
        stats = g_itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        return unlockStats.getVehTotalXP(self.__vehCD) >= self.__xpCost

    def _getCostCtx(self, vehCD, xpCost):
        stats = g_itemsCache.items.stats
        return unlock.makeCostCtx(UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP).getVehXP(vehCD), xpCost)

    @decorators.process('research')
    def _doUnlockItem(self, unlockCtx, costCtx, plugins):
        result = yield unlock.UnlockItemProcessor(unlockCtx.vehCD, unlockCtx.unlockIdx, plugins=plugins).request()
        item = g_itemsCache.items.getItemByCD(unlockCtx.unlockCD)
        if result.success:
            costCtx['xpCost'] = BigWorld.wg_getIntegralFormat(costCtx['xpCost'])
            costCtx['freeXP'] = BigWorld.wg_getIntegralFormat(costCtx['freeXP'])
            showUnlockMsg('unlock_success', item, msgType=SystemMessages.SM_TYPE.PowerLevel, **costCtx)
        elif len(result.userMsg):
            showUnlockMsg(result.userMsg, item)


class InstallItemAction(BuyAction):

    def __init__(self, itemCD, rootCD):
        super(InstallItemAction, self).__init__()
        self._itemCD = itemCD
        self._rootCD = rootCD

    def doAction(self):
        if RequestState.inProcess('install'):
            SystemMessages.pushI18nMessage('#system_messages:inventory/item/equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        self.installItem(self._itemCD, self._rootCD, 'install')

    @process
    def installItem(self, itemCD, rootCD, state):
        itemTypeID, nationID, itemID = vehicles.parseIntCompactDescr(itemCD)
        raise itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES or AssertionError
        vehicle = g_itemsCache.items.getItemByCD(rootCD)
        if not vehicle.isInInventory:
            raise AssertionError('Vehicle must be in inventory')
            item = g_itemsCache.items.getItemByCD(itemCD)
            conflictedEqs = item.getConflictedEquipments(vehicle)
            RequestState.sent(state)
            if item.isInInventory:
                Waiting.show('applyModule')
                result = yield getInstallerProcessor(vehicle, item, conflictedEqs=conflictedEqs).request()
                processMsg(result)
                vehicle = result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN) and g_itemsCache.items.getItemByCD(vehicle.intCD)
                yield tryToLoadDefaultShellsLayout(vehicle)
            Waiting.hide('applyModule')
        RequestState.received(state)
        yield lambda callback = None: callback
        return


class BuyAndInstallItemAction(InstallItemAction):

    def doAction(self):
        if RequestState.inProcess('buyAndInstall'):
            SystemMessages.pushI18nMessage('#system_messages:shop/item/buy_and_equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        self.buyAndInstallItem(self._itemCD, self._rootCD, 'buyAndInstall')

    @process
    def buyAndInstallItem(self, itemCD, rootCD, state):
        itemTypeID, nationID, itemID = vehicles.parseIntCompactDescr(itemCD)
        raise itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES or AssertionError
        vehicle = g_itemsCache.items.getItemByCD(rootCD)
        if not vehicle.isInInventory:
            raise AssertionError('Vehicle must be in inventory')
            item = g_itemsCache.items.getItemByCD(itemCD)
            conflictedEqs = item.getConflictedEquipments(vehicle)
            if not self._canBuy(item) and self._canBuyWithExchange(item):
                isOk, args = yield DialogsInterface.showDialog(ExchangeCreditsMeta(itemCD, vehicle.intCD))
                if not isOk:
                    return
            if self._canBuy(item):
                Waiting.show('buyAndInstall')
                vehicle = g_itemsCache.items.getItemByCD(rootCD)
                gunCD = getGunCD(item, vehicle)
                result = yield BuyAndInstallItemProcessor(vehicle, item, 0, gunCD, conflictedEqs=conflictedEqs).request()
                processMsg(result)
                if result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                    item = g_itemsCache.items.getItemByCD(itemCD)
                    vehicle = g_itemsCache.items.getItemByCD(rootCD)
                    item.isInstalled(vehicle) and (yield tryToLoadDefaultShellsLayout(vehicle))
            Waiting.hide('buyAndInstall')
        RequestState.received(state)
        yield lambda callback = None: callback
        return


class SetVehicleModuleAction(BuyAction):

    def __init__(self, vehInvID, newItemCD, slotIdx, oldItemCD, isRemove):
        super(SetVehicleModuleAction, self).__init__()
        self.__vehInvID = vehInvID
        self.__newItemCD = newItemCD
        self.__slotIdx = slotIdx
        self.__oldItemCD = oldItemCD
        self.__isRemove = isRemove

    @process
    def doAction(self):
        vehicle = g_itemsCache.items.getVehicle(self.__vehInvID)
        if vehicle is None:
            return
        else:
            isUseGold = self.__isRemove and self.__oldItemCD is not None
            LOG_DEBUG('isUseGold, self.__isRemove, self.__oldItemCD', isUseGold, self.__isRemove, self.__oldItemCD)
            newComponentItem = g_itemsCache.items.getItemByCD(int(self.__newItemCD))
            if newComponentItem is None:
                return
            oldComponentItem = None
            if self.__oldItemCD:
                oldComponentItem = g_itemsCache.items.getItemByCD(int(self.__oldItemCD))
            if not self.__isRemove:
                if oldComponentItem and oldComponentItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                    result = yield getInstallerProcessor(vehicle, oldComponentItem, self.__slotIdx, False, True).request()
                    processMsg(result)
                    if not result.success:
                        return
            if not self.__isRemove and not newComponentItem.isInInventory:
                conflictedEqs = newComponentItem.getConflictedEquipments(vehicle)
                if not self._canBuy(newComponentItem) and self._canBuyWithExchange(newComponentItem):
                    isOk, args = yield DialogsInterface.showDialog(ExchangeCreditsMeta(newComponentItem.intCD, vehicle.intCD))
                    if not isOk:
                        return
                if self._canBuy(newComponentItem):
                    Waiting.show('buyAndInstall')
                    vehicle = g_itemsCache.items.getVehicle(self.__vehInvID)
                    gunCD = getGunCD(newComponentItem, vehicle)
                    result = yield BuyAndInstallItemProcessor(vehicle, newComponentItem, self.__slotIdx, gunCD, conflictedEqs=conflictedEqs).request()
                    processMsg(result)
                    if result.success and newComponentItem.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                        newComponentItem = g_itemsCache.items.getItemByCD(int(self.__newItemCD))
                        vehicle = g_itemsCache.items.getItemByCD(vehicle.intCD)
                        if newComponentItem.isInstalled(vehicle):
                            yield tryToLoadDefaultShellsLayout(vehicle)
                    Waiting.hide('buyAndInstall')
                else:
                    yield lambda callback = None: callback
            else:
                Waiting.show('applyModule')
                conflictedEqs = newComponentItem.getConflictedEquipments(vehicle)
                result = yield getInstallerProcessor(vehicle, newComponentItem, self.__slotIdx, not self.__isRemove, isUseGold, conflictedEqs).request()
                processMsg(result)
                Waiting.hide('applyModule')
            return
