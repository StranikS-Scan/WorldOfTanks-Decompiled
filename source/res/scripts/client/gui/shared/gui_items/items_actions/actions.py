# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/items_actions/actions.py
import logging
from collections import namedtuple
import BigWorld
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.shared.economics import getGUIPrice
from gui.shared.gui_items.processors.common import TankmanBerthsBuyer
from gui.shared.gui_items.processors.goodies import BoosterBuyer
from helpers import dependency
from items import vehicles
from adisp import process
from gui.shared.utils import decorators
from gui import SystemMessages, DialogsInterface
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.processors.module import getInstallerProcessor
from gui.shared.gui_items.processors.module import BuyAndInstallItemProcessor
from gui.shared.gui_items.processors.module import ModuleSeller
from gui.shared.gui_items.processors.module import MultipleModulesSeller
from gui.shared.gui_items.processors.vehicle import tryToLoadDefaultShellsLayout
from gui.shared.gui_items.processors.vehicle import VehicleLayoutProcessor
from gui.shared.gui_items.processors.vehicle import VehicleBattleBoosterLayoutProcessor
from gui.shared.gui_items.processors.vehicle import BuyAndInstallBattleBoosterProcessor
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.gui_items.vehicle_equipment import EquipmentLayoutHelper
from gui.shared.gui_items.vehicle_equipment import ShellLayoutHelper
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.techtree import unlock
from gui.Scaleform.daapi.view.lobby.techtree.settings import RequestState
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import LocalSellModuleMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import BuyModuleMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeXpMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import RestoreExchangeCreditsMeta
from shared_utils import first, allEqual
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
ItemSellSpec = namedtuple('ItemSellSpec', 'typeIdx, intCD, count')

def showMessage(scopeMsg, msg, item, msgType=SystemMessages.SM_TYPE.Error, **kwargs):
    kwargs['userString'] = item.userName
    kwargs['type'] = msgType
    if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
        entity = 'vehicle'
    else:
        entity = 'item'
        kwargs['typeString'] = item.userType
    key = scopeMsg.format(entity, msg)
    SystemMessages.pushI18nMessage(key, **kwargs)


def showInventoryMsg(msg, item, msgType=SystemMessages.SM_TYPE.Error, **kwargs):
    scopeMsg = '#system_messages:inventory/{0:>s}/{1:>s}'
    showMessage(scopeMsg, msg, item, msgType=msgType, **kwargs)


def showUnlockMsg(msg, item, msgType=SystemMessages.SM_TYPE.Error, **kwargs):
    scopeMsg = '#system_messages:unlocks/{0:>s}/{1:>s}'
    showMessage(scopeMsg, msg, item, msgType=msgType, **kwargs)


def showShopMsg(msg, item, msgType=SystemMessages.SM_TYPE.Error, **kwargs):
    scopeMsg = '#system_messages:shop/{0:>s}/{1:>s}'
    showMessage(scopeMsg, msg, item, msgType=msgType, **kwargs)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getGunCD(item, vehicle, itemsCache=None):
    if item.itemTypeID == GUI_ITEM_TYPE.TURRET and itemsCache is not None:
        if not item.mayInstall(vehicle, gunCD=0)[0]:
            for gun in item.descriptor.guns:
                gunItem = itemsCache.items.getItemByCD(gun.compactDescr)
                if gunItem.isInInventory:
                    mayInstall = item.mayInstall(vehicle, slotIdx=0, gunCD=gun.compactDescr)
                    if mayInstall[0]:
                        return gun.compactDescr

    return 0


def processMsg(result):
    if result and result.userMsg:
        SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
    if result and hasattr(result, 'auxData') and not isinstance(result.auxData, dict) and result.auxData:
        for m in result.auxData:
            SystemMessages.pushI18nMessage(m.userMsg, type=m.sysMsgType)


class IGUIItemAction(object):

    def __init(self):
        self.__skipConfirm = False

    @property
    def skipConfirm(self):
        return self.__skipConfirm

    @skipConfirm.setter
    def skipConfirm(self, value):
        self.__skipConfirm = value

    def doAction(self):
        pass


class CachedItemAction(IGUIItemAction):
    itemsCache = dependency.descriptor(IItemsCache)


class BuyAction(CachedItemAction):
    tradeIn = dependency.descriptor(ITradeInController)

    def _mayObtainForMoney(self, item):
        money = self.itemsCache.items.stats.money
        canBuy, _ = item.mayObtainForMoney(money)
        return canBuy

    def _mayObtainWithMoneyExchange(self, item):
        items = self.itemsCache.items
        money = items.stats.money
        return item.mayObtainWithMoneyExchange(money, items.shop.exchangeRate)


class SellItemAction(CachedItemAction):

    def __init__(self, itemTypeCD):
        super(SellItemAction, self).__init__()
        self.__itemTypeCD = itemTypeCD

    @process
    def doAction(self):
        item = self.itemsCache.items.getItemByCD(self.__itemTypeCD)
        if item.isInInventory:
            yield DialogsInterface.showDialog(LocalSellModuleMeta(self.__itemTypeCD))
        else:
            showInventoryMsg('not_found', item)
            yield lambda callback=None: callback
        return


class SellMultipleItems(IGUIItemAction):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemSellSpecs):
        super(SellMultipleItems, self).__init__()
        self.__items = itemSellSpecs

    @process
    def doAction(self):
        Waiting.show(STORAGE.FORSELL_WAITING)
        if allEqual(self.__items, lambda i: i.intCD):
            item = self.itemsCache.items.getItemByCD(first(self.__items).intCD)
            result = yield ModuleSeller(item, min(item.inventoryCount, MAX_ITEMS_FOR_OPERATION)).request()
        else:
            result = yield MultipleModulesSeller(self.__items).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        Waiting.hide(STORAGE.FORSELL_WAITING)


class ModuleBuyAction(BuyAction):

    def __init__(self, intCD):
        super(ModuleBuyAction, self).__init__()
        self.__intCD = intCD

    @process
    def doAction(self):
        item = self.itemsCache.items.getItemByCD(self.__intCD)
        if not self._mayObtainForMoney(item):
            if self._mayObtainWithMoneyExchange(item):
                isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemMeta(self.__intCD))
                if not isOk:
                    return
            else:
                showShopMsg('common_rent_or_buy_error', item)
        if self._mayObtainForMoney(item):
            yield DialogsInterface.showDialog(BuyModuleMeta(self.__intCD, self.itemsCache.items.stats.money))
        else:
            yield lambda callback=None: callback
        return


class VehicleBuyAction(BuyAction):

    def __init__(self, vehCD, isTradeIn=False, previousAlias=None):
        super(VehicleBuyAction, self).__init__()
        self.__vehCD = vehCD
        self.__isTradeIn = isTradeIn
        self.__previousAlias = previousAlias

    @process
    def doAction(self):
        item = self.itemsCache.items.getItemByCD(self.__vehCD)
        if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
            _logger.error('Value of int-type descriptor is not refer to vehicle %r', self.__vehCD)
            return
        else:
            if item.isInInventory and not item.isRented:
                showInventoryMsg('already_exists', item, msgType=SystemMessages.SM_TYPE.Warning)
            else:
                price = getGUIPrice(item, self.itemsCache.items.stats.money, self.itemsCache.items.shop.exchangeRate)
                if price is None:
                    showShopMsg('not_found', item)
                    return
                if not self._mayObtainForMoney(item):
                    if self._mayObtainWithMoneyExchange(item):
                        if item.isRestoreAvailable():
                            meta = RestoreExchangeCreditsMeta(self.__vehCD)
                        else:
                            meta = ExchangeCreditsSingleItemMeta(self.__vehCD)
                        isOk, _ = yield DialogsInterface.showDialog(meta)
                        if not isOk:
                            return
                    else:
                        showShopMsg('common_rent_or_buy_error', item)
                if self._mayObtainForMoney(item):
                    shared_events.showVehicleBuyDialog(item, self.__isTradeIn, self.__previousAlias)
                yield lambda callback=None: callback
            return

    def _mayObtainForMoney(self, item):
        money = self.tradeIn.addTradeInPriceIfNeeded(item, self.itemsCache.items.stats.money)
        canBuy, _ = item.mayObtainForMoney(money)
        return canBuy

    def _mayObtainWithMoneyExchange(self, item):
        items = self.itemsCache.items
        money = self.tradeIn.addTradeInPriceIfNeeded(item, items.stats.money)
        return item.mayObtainWithMoneyExchange(money, items.shop.exchangeRate)


class UnlockItemAction(CachedItemAction):

    def __init__(self, unlockCD, vehCD, unlockIdx, xpCost):
        super(UnlockItemAction, self).__init__()
        self.__unlockCD = unlockCD
        self.__vehCD = vehCD
        self.__unlockIdx = unlockIdx
        self.__xpCost = xpCost

    @process
    def doAction(self):
        if not self._isEnoughXpToUnlock():
            isOk, _ = yield DialogsInterface.showDialog(ExchangeXpMeta(self.__unlockCD, self.__vehCD, self.__xpCost))
            if isOk and self._isEnoughXpToUnlock() and not self._isUnlocked():
                self._unlockItem()
        else:
            self._unlockItem()

    def _unlockItem(self):
        costCtx = self._getCostCtx(self.__vehCD, self.__xpCost)
        unlockCtx = unlock.UnlockItemCtx(self.__unlockCD, self.__vehCD, self.__unlockIdx, self.__xpCost)
        plugins = [unlock.UnlockItemConfirmator(unlockCtx, costCtx, isEnabled=not self.skipConfirm), unlock.UnlockItemValidator(unlockCtx)]
        self._doUnlockItem(unlockCtx, costCtx, plugins)

    def _isUnlocked(self):
        item = self.itemsCache.items.getItemByCD(self.__unlockCD)
        return item.isUnlocked

    def _isEnoughXpToUnlock(self):
        stats = self.itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        return unlockStats.getVehTotalXP(self.__vehCD) >= self.__xpCost

    def _getCostCtx(self, vehCD, xpCost):
        stats = self.itemsCache.items.stats
        return unlock.makeCostCtx(UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP).getVehXP(vehCD), xpCost)

    @decorators.process('research')
    def _doUnlockItem(self, unlockCtx, costCtx, plugins):
        result = yield unlock.UnlockItemProcessor(unlockCtx.vehCD, unlockCtx.unlockIdx, plugins=plugins).request()
        item = self.itemsCache.items.getItemByCD(unlockCtx.unlockCD)
        if result.success:
            costCtx['xpCost'] = BigWorld.wg_getIntegralFormat(costCtx['xpCost'])
            costCtx['freeXP'] = BigWorld.wg_getIntegralFormat(costCtx['freeXP'])
            showUnlockMsg('unlock_success', item, msgType=SystemMessages.SM_TYPE.PowerLevel, **costCtx)
        elif result.userMsg:
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
        itemTypeID, _, __ = vehicles.parseIntCompactDescr(itemCD)
        if itemTypeID not in GUI_ITEM_TYPE.VEHICLE_MODULES:
            raise SoftException('Specified type (itemTypeID={}) is not type of module'.format(itemTypeID))
        vehicle = self.itemsCache.items.getItemByCD(rootCD)
        if not vehicle.isInInventory:
            raise SoftException('Vehicle (intCD={}) must be in inventory'.format(rootCD))
        item = self.itemsCache.items.getItemByCD(itemCD)
        conflictedEqs = item.getConflictedEquipments(vehicle)
        RequestState.sent(state)
        if item.isInInventory:
            Waiting.show('applyModule')
            result = yield getInstallerProcessor(vehicle, item, conflictedEqs=conflictedEqs, skipConfirm=self.skipConfirm).request()
            processMsg(result)
            if result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                vehicle = self.itemsCache.items.getItemByCD(vehicle.intCD)
                yield tryToLoadDefaultShellsLayout(vehicle)
            Waiting.hide('applyModule')
        RequestState.received(state)
        yield lambda callback=None: callback
        return


class BuyAndInstallItemAction(InstallItemAction):

    def doAction(self):
        if RequestState.inProcess('buyAndInstall'):
            SystemMessages.pushI18nMessage('#system_messages:shop/item/buy_and_equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        self.buyAndInstallItem(self._itemCD, self._rootCD, 'buyAndInstall')

    @process
    def buyAndInstallItem(self, itemCD, rootCD, state):
        itemTypeID, _, __ = vehicles.parseIntCompactDescr(itemCD)
        if itemTypeID not in GUI_ITEM_TYPE.VEHICLE_MODULES:
            raise SoftException('Specified type (itemTypeID={}) is not type of module'.format(itemTypeID))
        vehicle = self.itemsCache.items.getItemByCD(rootCD)
        if not vehicle.isInInventory:
            raise SoftException('Vehicle (intCD={}) must be in inventory'.format(rootCD))
        item = self.itemsCache.items.getItemByCD(itemCD)
        conflictedEqs = item.getConflictedEquipments(vehicle)
        if not self._mayObtainForMoney(item) and self._mayObtainWithMoneyExchange(item):
            isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemMeta(itemCD, vehicle.intCD))
            if not isOk:
                return
        if self._mayObtainForMoney(item):
            Waiting.show('buyAndInstall')
            vehicle = self.itemsCache.items.getItemByCD(rootCD)
            gunCD = getGunCD(item, vehicle)
            result = yield BuyAndInstallItemProcessor(vehicle, item, 0, gunCD, conflictedEqs=conflictedEqs, skipConfirm=self.skipConfirm).request()
            processMsg(result)
            if result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                item = self.itemsCache.items.getItemByCD(itemCD)
                vehicle = self.itemsCache.items.getItemByCD(rootCD)
                if item.isInstalled(vehicle):
                    yield tryToLoadDefaultShellsLayout(vehicle)
            Waiting.hide('buyAndInstall')
        RequestState.received(state)
        yield lambda callback=None: callback
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
        vehicle = self.itemsCache.items.getVehicle(self.__vehInvID)
        if vehicle is None:
            return
        else:
            isUseMoney = self.__isRemove and self.__oldItemCD is not None
            _logger.debug('isUseMoney - %r, self.__isRemove - %r, self.__oldItemCD - %r', isUseMoney, self.__isRemove, self.__oldItemCD)
            newComponentItem = self.itemsCache.items.getItemByCD(int(self.__newItemCD))
            if newComponentItem is None:
                return
            oldComponentItem = None
            if self.__oldItemCD:
                oldComponentItem = self.itemsCache.items.getItemByCD(int(self.__oldItemCD))
            if not self.__isRemove:
                if oldComponentItem and oldComponentItem.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.BATTLE_BOOSTER):
                    Waiting.show('installEquipment')
                    result = yield getInstallerProcessor(vehicle, oldComponentItem, self.__slotIdx, False, True, skipConfirm=self.skipConfirm).request()
                    processMsg(result)
                    Waiting.hide('installEquipment')
                    if not result.success:
                        return
            if not self.__isRemove and not newComponentItem.isInInventory and not newComponentItem.itemTypeID == GUI_ITEM_TYPE.BATTLE_ABILITY:
                conflictedEqs = newComponentItem.getConflictedEquipments(vehicle)
                if not self._mayObtainForMoney(newComponentItem) and self._mayObtainWithMoneyExchange(newComponentItem):
                    isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemMeta(newComponentItem.intCD, vehicle.intCD))
                    if not isOk:
                        return
                if self._mayObtainForMoney(newComponentItem):
                    Waiting.show('buyAndInstall')
                    vehicle = self.itemsCache.items.getVehicle(self.__vehInvID)
                    gunCD = getGunCD(newComponentItem, vehicle)
                    result = yield BuyAndInstallItemProcessor(vehicle, newComponentItem, self.__slotIdx, gunCD, conflictedEqs=conflictedEqs, skipConfirm=self.skipConfirm).request()
                    processMsg(result)
                    if result.success and newComponentItem.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                        newComponentItem = self.itemsCache.items.getItemByCD(int(self.__newItemCD))
                        vehicle = self.itemsCache.items.getItemByCD(vehicle.intCD)
                        if newComponentItem.isInstalled(vehicle):
                            yield tryToLoadDefaultShellsLayout(vehicle)
                    Waiting.hide('buyAndInstall')
                else:
                    yield lambda callback=None: callback
            else:
                Waiting.show('applyModule')
                conflictedEqs = newComponentItem.getConflictedEquipments(vehicle)
                result = yield getInstallerProcessor(vehicle, newComponentItem, self.__slotIdx, not self.__isRemove, isUseMoney, conflictedEqs, self.skipConfirm).request()
                processMsg(result)
                if result.success and newComponentItem.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                    newComponentItem = self.itemsCache.items.getItemByCD(int(self.__newItemCD))
                    vehicle = self.itemsCache.items.getItemByCD(vehicle.intCD)
                    if newComponentItem.isInstalled(vehicle):
                        yield tryToLoadDefaultShellsLayout(vehicle)
                Waiting.hide('applyModule')
            return


class SetVehicleLayoutAction(IGUIItemAction):

    def __init__(self, vehicle, shellsLayout=None, eqsLayout=None, battleBooster=None):
        super(SetVehicleLayoutAction, self).__init__()
        self._vehicle = vehicle
        self._shellsLayout = shellsLayout
        self._eqsLayout = eqsLayout
        self._battleBooster = battleBooster

    @decorators.process('techMaintenance')
    def doAction(self):
        if self._battleBooster is not None:
            boosterLayout = (self._battleBooster.intCD, 1) if self._battleBooster else (0, 0)
            eqsLayout = EquipmentLayoutHelper(self._vehicle, self._eqsLayout, boosterLayout)
            result = yield VehicleBattleBoosterLayoutProcessor(self._vehicle, self._battleBooster, eqsLayout, self.skipConfirm).request()
        else:
            shellsHelper = ShellLayoutHelper(self._vehicle, self._shellsLayout)
            eqsHelper = EquipmentLayoutHelper(self._vehicle, self._eqsLayout)
            result = yield VehicleLayoutProcessor(self._vehicle, shellsHelper, eqsHelper, self.skipConfirm).request()
        self._showResult(result)
        return

    @staticmethod
    def _showResult(result):
        if result and result.auxData:
            for m in result.auxData:
                SystemMessages.pushI18nMessage(m.userMsg, type=m.sysMsgType)

        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class BuyAndInstallItemVehicleLayout(SetVehicleLayoutAction):

    def __init__(self, vehicle, shellsLayout=None, eqsLayout=None, battleBooster=None, count=1):
        super(BuyAndInstallItemVehicleLayout, self).__init__(vehicle, shellsLayout, eqsLayout, battleBooster)
        self._count = count

    @decorators.process('buyItem')
    def doAction(self):
        if self._battleBooster is not None:
            boosterLayout = (self._battleBooster.intCD, 1)
            helper = EquipmentLayoutHelper(self._vehicle, self._eqsLayout, boosterLayout)
            result = yield BuyAndInstallBattleBoosterProcessor(self._vehicle, self._battleBooster, helper, self._count, self.skipConfirm).request()
            self._showResult(result)
        else:
            _logger.error('Extend BuyAndInstallItemVehicleLayout action to support a new type of item!')
        return


class BuyVehicleSlotAction(CachedItemAction):

    @decorators.process('buySlot')
    def doAction(self):
        result = yield VehicleSlotBuyer().request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class BuyBerthsAction(CachedItemAction):

    @decorators.process('buyBerths')
    def doAction(self):
        items = self.itemsCache.items
        berthPrice, berthsCount = items.shop.getTankmanBerthPrice(items.stats.tankmenBerthsCount)
        result = yield TankmanBerthsBuyer(berthPrice, berthsCount).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class BuyBoosterAction(CachedItemAction):

    def __init__(self, boosterID, count, currency):
        super(BuyBoosterAction, self).__init__()
        self.__boosterID = boosterID
        self.__count = count
        self.__currency = currency

    @decorators.process('buyItem')
    def doAction(self):
        result = yield BoosterBuyer(self.__boosterID, self.__count, self.__currency).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
