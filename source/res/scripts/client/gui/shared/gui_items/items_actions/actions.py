# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/items_actions/actions.py
from collections import namedtuple
import async as future_async
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from adisp import process, async
from debug_utils import LOG_ERROR
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.bootcamp.lobby.unlock import BCUnlockItemConfirmator
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import BuyModuleMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import LocalSellModuleMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeXpMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import RestoreExchangeCreditsMeta
from gui.Scaleform.daapi.view.lobby.techtree import unlock
from gui.Scaleform.daapi.view.lobby.techtree.settings import RequestState
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.impl import backport
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.shared import event_dispatcher as shared_events
from gui.shared.economics import getGUIPrice
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import canBuyWithGoldExchange
from gui.shared.gui_items.gui_item_economics import getVehicleShellsLayoutPrice
from gui.shared.gui_items.processors.common import ConvertBlueprintFragmentProcessor
from gui.shared.gui_items.processors.common import TankmanBerthsBuyer
from gui.shared.gui_items.processors.common import UseCrewBookProcessor
from gui.shared.gui_items.processors.goodies import BoosterBuyer
from gui.shared.gui_items.processors.module import BuyAndInstallItemProcessor, BCBuyAndInstallItemProcessor, OptDeviceInstaller
from gui.shared.gui_items.processors.module import ModuleSeller
from gui.shared.gui_items.processors.module import ModuleUpgradeProcessor
from gui.shared.gui_items.processors.module import MultipleModulesSeller
from gui.shared.gui_items.processors.module import getInstallerProcessor
from gui.shared.gui_items.processors.vehicle import OptDevicesInstaller, BuyAndInstallConsumablesProcessor, AutoFillVehicleLayoutProcessor, BuyAndInstallBattleBoostersProcessor, BuyAndInstallShellsProcessor, VehicleRepairer, InstallBattleAbilitiesProcessor
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.gui_items.processors.vehicle import tryToLoadDefaultShellsLayout
from gui.shared.money import ZERO_MONEY, Money
from gui.shared.utils import decorators
from helpers import dependency
from items import vehicles
from shared_utils import first, allEqual
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
ItemSellSpec = namedtuple('ItemSellSpec', ('typeIdx', 'intCD', 'count'))

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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _needExchangeForBuy(price, itemsCache=None):
    money = itemsCache.items.stats.money
    rate = itemsCache.items.shop.exchangeRate
    return canBuyWithGoldExchange(price, money, rate) and money.getShortage(price).credits > 0


class IGUIItemAction(object):
    __slots__ = ('__skipConfirm',)

    def __init__(self):
        self.__skipConfirm = False

    @property
    def skipConfirm(self):
        return self.__skipConfirm

    @skipConfirm.setter
    def skipConfirm(self, value):
        self.__skipConfirm = value

    def doAction(self):
        pass

    def isAsync(self):
        return False


class CachedItemAction(IGUIItemAction):
    _itemsCache = dependency.descriptor(IItemsCache)


class BuyAction(CachedItemAction):
    tradeIn = dependency.descriptor(ITradeInController)

    def _mayObtainForMoney(self, item):
        money = self._itemsCache.items.stats.money
        canBuy, _ = item.mayObtainForMoney(money)
        return canBuy

    def _mayObtainWithMoneyExchange(self, item):
        items = self._itemsCache.items
        money = items.stats.money
        return item.mayObtainWithMoneyExchange(money, items.shop.exchangeRate)


class SellItemAction(CachedItemAction):

    def __init__(self, itemTypeCD):
        super(SellItemAction, self).__init__()
        self.__itemTypeCD = itemTypeCD

    @process
    def doAction(self):
        item = self._itemsCache.items.getItemByCD(self.__itemTypeCD)
        if item.isInInventory:
            yield DialogsInterface.showDialog(LocalSellModuleMeta(self.__itemTypeCD))
        else:
            showInventoryMsg('not_found', item)
            yield lambda callback=None: callback
        return


class SellMultipleItems(IGUIItemAction):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemSellSpecs):
        super(SellMultipleItems, self).__init__()
        self.__items = itemSellSpecs

    @process
    def doAction(self):
        Waiting.show('storage/forSell')
        if allEqual(self.__items, lambda i: i.intCD):
            item = self._itemsCache.items.getItemByCD(first(self.__items).intCD)
            result = yield ModuleSeller(item, min(item.inventoryCount, MAX_ITEMS_FOR_OPERATION)).request()
        else:
            result = yield MultipleModulesSeller(self.__items).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        Waiting.hide('storage/forSell')


class ModuleBuyAction(BuyAction):

    def __init__(self, intCD):
        super(ModuleBuyAction, self).__init__()
        self.__intCD = intCD

    @process
    def doAction(self):
        item = self._itemsCache.items.getItemByCD(self.__intCD)
        if not self._mayObtainForMoney(item):
            if self._mayObtainWithMoneyExchange(item):
                isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemMeta(self.__intCD))
                if not isOk:
                    return
            else:
                showShopMsg('common_rent_or_buy_error', item)
        if self._mayObtainForMoney(item):
            yield DialogsInterface.showDialog(BuyModuleMeta(self.__intCD, self._itemsCache.items.stats.money))
        else:
            yield lambda callback=None: callback
        return


class ChangeVehicleNationAction(IGUIItemAction):

    def __init__(self, vehCD):
        super(ChangeVehicleNationAction, self).__init__()
        self.__vehCD = vehCD

    @process
    def doAction(self):
        AccountSettings.setSettings(NATION_CHANGE_VIEWED, True)
        shared_events.showChangeVehicleNationDialog(self.__vehCD)
        yield lambda callback=None: callback
        return


class VehicleBuyAction(BuyAction):

    def __init__(self, vehCD, isTradeIn=False, actionType=None, previousAlias=None, returnAlias=None, returnCallback=None):
        super(VehicleBuyAction, self).__init__()
        self.__vehCD = vehCD
        self.__isTradeIn = isTradeIn
        self.__previousAlias = previousAlias
        self.__returnCallback = returnCallback
        self.__returnAlias = returnAlias
        self.__actionType = actionType

    @process
    def doAction(self):
        item = self._itemsCache.items.getItemByCD(self.__vehCD)
        if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
            LOG_ERROR('Value of int-type descriptor is not refer to vehicle', self.__vehCD)
            return
        else:
            if item.isInInventory and not item.isRented:
                showInventoryMsg('already_exists', item, msgType=SystemMessages.SM_TYPE.Warning)
            else:
                price = getGUIPrice(item, self._itemsCache.items.stats.money, self._itemsCache.items.shop.exchangeRate)
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
                    shared_events.showVehicleBuyDialog(item, self.__actionType, self.__isTradeIn, self.__previousAlias, returnAlias=self.__returnAlias, returnCallback=self.__returnCallback)
                yield lambda callback=None: callback
            return

    def _mayObtainForMoney(self, item):
        money = self.tradeIn.addTradeInPriceIfNeeded(item, self._itemsCache.items.stats.money)
        canBuy, _ = item.mayObtainForMoney(money)
        return canBuy

    def _mayObtainWithMoneyExchange(self, item):
        items = self._itemsCache.items
        money = self.tradeIn.addTradeInPriceIfNeeded(item, items.stats.money)
        return item.mayObtainWithMoneyExchange(money, items.shop.exchangeRate)


class _UnlockItem(CachedItemAction):
    _itemConfirmatorCls = unlock.UnlockItemConfirmator
    _itemValidatorCls = unlock.UnlockItemValidator

    def __init__(self, itemCD, unlockProps):
        super(_UnlockItem, self).__init__()
        self.__costCtx = None
        self._item = self._itemsCache.items.getItemByCD(itemCD)
        self._unlockProps = unlockProps
        g_clientUpdateManager.addCallbacks({'serverSettings.blueprints_config.isEnabled': self.__onBlueprintsModeChanged,
         'serverSettings.blueprints_config.useBlueprintsForUnlock': self.__onBlueprintsModeChanged})
        return

    def _isEnoughXpToUnlock(self):
        stats = self._itemsCache.items.stats
        unlockStats = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP)
        return unlockStats.getVehTotalXP(self._unlockProps.parentID) >= self._unlockProps.xpCost

    def _createPlugins(self):
        self.__costCtx = self.__getCostCtx()
        unlockCtx = unlock.UnlockItemCtx(self._item.intCD, self._item.itemTypeID, self._unlockProps.parentID, self._unlockProps.unlockIdx)
        plugins = [self._itemConfirmatorCls(unlockCtx, self.__costCtx, isEnabled=not self.skipConfirm), self._itemValidatorCls(unlockCtx, self.__costCtx)]
        return plugins

    def _showResult(self, result):
        if result.success:
            self.__costCtx['vehXP'] = backport.getIntegralFormat(self.__costCtx['vehXP'])
            self.__costCtx['freeXP'] = backport.getIntegralFormat(self.__costCtx['freeXP'])
            showUnlockMsg('unlock_success', self._item, msgType=SystemMessages.SM_TYPE.PowerLevel, **self.__costCtx)
        elif result.userMsg:
            showUnlockMsg(result.userMsg, self._item)
        self.__clear()

    def __getCostCtx(self):
        stats = self._itemsCache.items.stats
        availableXP = UnlockStats(stats.unlocks, stats.vehiclesXPs, stats.freeXP).getVehXP(self._unlockProps.parentID)
        return unlock.makeCostCtx(availableXP, self._unlockProps.xpCost, self._unlockProps.discount)

    def __onBlueprintsModeChanged(self, _):
        if self._item.itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            return
        self._unlockProps = g_techTreeDP.getUnlockProps(self._item.intCD, self._item.level)
        self.__costCtx = self.__getCostCtx()

    def __clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__costCtx = None
        return


class UnlockItemAction(_UnlockItem):

    @process
    def doAction(self):
        if not self._isEnoughXpToUnlock():
            isOk, _ = yield DialogsInterface.showDialog(ExchangeXpMeta(self._item.intCD, self._unlockProps.parentID, self._unlockProps.xpCost))
            if isOk and self._isEnoughXpToUnlock() and not self._item.isUnlocked:
                self.__unlockItem()
        else:
            self.__unlockItem()

    def __unlockItem(self):
        plugins = self._createPlugins()
        self.__doUnlockItem(plugins)

    @decorators.process('research')
    def __doUnlockItem(self, plugins):
        result = yield unlock.UnlockItemProcessor(self._unlockProps.parentID, self._unlockProps.unlockIdx, plugins=plugins).request()
        self._showResult(result)


class BCUnlockItemAction(UnlockItemAction):
    _itemConfirmatorCls = BCUnlockItemConfirmator
    _itemValidatorCls = unlock.UnlockItemValidator


class UnlockItemActionWithResult(_UnlockItem):

    @async
    @process
    def doAsyncAction(self, callback):
        result = None
        if not self._isEnoughXpToUnlock():
            isOk, _ = yield DialogsInterface.showDialog(ExchangeXpMeta(self._item.intCD, self._unlockProps.parentID, self._unlockProps.xpCost))
            if isOk and self._isEnoughXpToUnlock() and not self._item.isUnlocked:
                result = yield self.__unlockAsyncItem()
        else:
            result = yield self.__unlockAsyncItem()
        callback(result)
        return

    @async
    @decorators.process('research')
    def __unlockAsyncItem(self, callback):
        plugins = self._createPlugins()
        result = yield unlock.UnlockItemProcessor(self._unlockProps.parentID, self._unlockProps.unlockIdx, plugins=plugins).request()
        self._showResult(result)
        callback(result)


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
        vehicle = self._itemsCache.items.getItemByCD(rootCD)
        if not vehicle.isInInventory:
            raise SoftException('Vehicle (intCD={}) must be in inventory'.format(rootCD))
        item = self._itemsCache.items.getItemByCD(itemCD)
        conflictedEqs = item.getConflictedEquipments(vehicle)
        RequestState.sent(state)
        if item.isInInventory:
            proc = getInstallerProcessor(vehicle, item, conflictedEqs=conflictedEqs, skipConfirm=self.skipConfirm)
            if not proc.IS_GAMEFACE_SUPPORTED:
                Waiting.show('applyModule')
            result = yield proc.request()
            processMsg(result)
            if result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                vehicle = self._itemsCache.items.getItemByCD(vehicle.intCD)
                yield tryToLoadDefaultShellsLayout(vehicle)
            if not proc.IS_GAMEFACE_SUPPORTED:
                Waiting.hide('applyModule')
        RequestState.received(state)
        yield lambda callback=None: callback
        return


class BuyAndInstallItemAction(InstallItemAction):
    _buyAndInstallItemProcessorCls = BuyAndInstallItemProcessor

    def doAction(self):
        if RequestState.inProcess('buyAndInstall'):
            SystemMessages.pushI18nMessage('#system_messages:shop/item/buy_and_equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        self.buyAndInstallItem(self._itemCD, self._rootCD, 'buyAndInstall')

    @process
    def buyAndInstallItem(self, itemCD, rootCD, state):
        itemTypeID, _, __ = vehicles.parseIntCompactDescr(itemCD)
        if itemTypeID not in GUI_ITEM_TYPE.VEHICLE_MODULES:
            raise SoftException('Specified type (itemTypeID={}) is not type of module'.format(itemTypeID))
        vehicle = self._itemsCache.items.getItemByCD(rootCD)
        if not vehicle.isInInventory:
            raise SoftException('Vehicle (intCD={}) must be in inventory'.format(rootCD))
        item = self._itemsCache.items.getItemByCD(itemCD)
        conflictedEqs = item.getConflictedEquipments(vehicle)
        if not self._mayObtainForMoney(item) and self._mayObtainWithMoneyExchange(item):
            isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemMeta(itemCD, vehicle.intCD))
            if not isOk:
                return
        if self._mayObtainForMoney(item):
            vehicle = self._itemsCache.items.getItemByCD(rootCD)
            gunCD = getGunCD(item, vehicle)
            proc = self._buyAndInstallItemProcessorCls(vehicle, item, 0, gunCD, conflictedEqs=conflictedEqs, skipConfirm=self.skipConfirm)
            result = yield proc.request()
            processMsg(result)
            if result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                item = self._itemsCache.items.getItemByCD(itemCD)
                vehicle = self._itemsCache.items.getItemByCD(rootCD)
                if item.isInstalled(vehicle):
                    yield tryToLoadDefaultShellsLayout(vehicle)
        RequestState.received(state)
        yield lambda callback=None: callback
        return


class BCBuyAndInstallItemAction(BuyAndInstallItemAction):
    _buyAndInstallItemProcessorCls = BCBuyAndInstallItemProcessor


class VehicleAutoFillLayoutAction(IGUIItemAction):

    def __init__(self, vehicle):
        super(VehicleAutoFillLayoutAction, self).__init__()
        self.__vehicle = vehicle

    @decorators.process('techMaintenance')
    def doAction(self):
        result = yield AutoFillVehicleLayoutProcessor(self.__vehicle).request()
        self._showResult(result)

    @staticmethod
    def _showResult(result):
        if result and result.auxData:
            for m in result.auxData:
                SystemMessages.pushI18nMessage(m.userMsg, type=m.sysMsgType)

        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class AsyncGUIItemAction(IGUIItemAction):
    __slots__ = ()

    @async
    @process
    def doAction(self, callback):
        confirm = True
        if not self.skipConfirm:
            confirm = yield self._confirm()
        if confirm:
            result = yield self._action()
            self._showResult(result)
            callback(result.success)
        else:
            callback(False)

    def isAsync(self):
        return True

    @async
    def _confirm(self, callback):
        callback(True)

    @async
    @process
    def _action(self, callback):
        result = yield lambda callback: callback(None)
        callback(result)

    def _showResult(self, result):
        processMsg(result)


class AmmunitionBuyAndInstall(AsyncGUIItemAction):
    __slots__ = ('_vehicle', '_changedItems', '__confirmOnlyExchange')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, changeItems, confirmOnlyExchange=False):
        self._vehicle = vehicle
        self._changedItems = changeItems
        self.__confirmOnlyExchange = confirmOnlyExchange
        super(AmmunitionBuyAndInstall, self).__init__()

    @async
    @future_async.async
    def _confirm(self, callback):
        if self._changedItems and _needExchangeForBuy(sum([ item.getBuyPrice().price for item in self._changedItems if not item.isInInventory ], ZERO_MONEY)):
            startState = BuyAndExchangeStateEnum.EXCHANGE_CONTENT
        elif self._changedItems:
            startState = BuyAndExchangeStateEnum.BUY_CONTENT
        else:
            startState = BuyAndExchangeStateEnum.BUY_NOT_REQUIRED
        if self.__confirmOnlyExchange and startState != BuyAndExchangeStateEnum.EXCHANGE_CONTENT:
            callback(True)
        else:
            result = yield future_async.await(shared_events.showTankSetupConfirmDialog(items=self._changedItems, vehInvID=self._vehicle.invID, startState=startState))
            callback(result.result[0] if not result.busy else False)


class BuyAndInstallOptDevices(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False):
        optDevices = vehicle.optDevices
        changeItems = [ item for item in optDevices.layout.getItems() if item not in optDevices.installed ]
        super(BuyAndInstallOptDevices, self).__init__(vehicle, changeItems, confirmOnlyExchange)

    @async
    @decorators.process('techMaintenance')
    def _action(self, callback):
        result = yield OptDevicesInstaller(self._vehicle).request()
        callback(result)


class BuyAndInstallConsumables(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False):
        changeItems = [ item for item in vehicle.consumables.layout.getItems() if item not in vehicle.consumables.installed ]
        super(BuyAndInstallConsumables, self).__init__(vehicle, changeItems, confirmOnlyExchange)

    @async
    @decorators.process('techMaintenance')
    def _action(self, callback):
        result = yield BuyAndInstallConsumablesProcessor(self._vehicle).request()
        callback(result)


class BuyAndInstallBattleBoosters(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False):
        changeItems = [ item for item in vehicle.battleBoosters.layout.getItems() if item not in vehicle.battleBoosters.installed ]
        super(BuyAndInstallBattleBoosters, self).__init__(vehicle, changeItems, confirmOnlyExchange)

    @async
    @decorators.process('techMaintenance')
    def _action(self, callback):
        result = yield BuyAndInstallBattleBoostersProcessor(self._vehicle).request()
        callback(result)


class BuyAndInstallShells(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__price', '__confirmOnlyExchange')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, confirmOnlyExchange=False):
        super(BuyAndInstallShells, self).__init__()
        self.__vehicle = vehicle
        self.__confirmOnlyExchange = confirmOnlyExchange
        self.__price = getVehicleShellsLayoutPrice(vehicle)

    @async
    @decorators.process('techMaintenance')
    def _action(self, callback):
        result = yield BuyAndInstallShellsProcessor(self.__vehicle).request()
        callback(result)

    @async
    @future_async.async
    def _confirm(self, callback):
        if _needExchangeForBuy(self.__price.price):
            startState = BuyAndExchangeStateEnum.EXCHANGE_CONTENT
        elif self.__price.price:
            startState = BuyAndExchangeStateEnum.BUY_CONTENT
        else:
            startState = BuyAndExchangeStateEnum.BUY_NOT_REQUIRED
        if self.__confirmOnlyExchange and startState != BuyAndExchangeStateEnum.EXCHANGE_CONTENT:
            callback(True)
        else:
            result = yield future_async.await(shared_events.showRefillShellsDialog(price=self.__price, shells=self.__vehicle.shells.layout.getItems(), startState=startState))
            callback(result.result[0] if not result.busy else False)


class VehicleRepairAction(AsyncGUIItemAction):

    def __init__(self, vehicle):
        super(VehicleRepairAction, self).__init__()
        self.__vehicle = vehicle

    @async
    @decorators.process('techMaintenance')
    def _action(self, callback):
        result = yield VehicleRepairer(self.__vehicle).request()
        callback(result)

    @async
    @future_async.async
    def _confirm(self, callback):
        if self.__vehicle.repairCost > 0:
            price = Money(credits=self.__vehicle.repairCost)
            startState = BuyAndExchangeStateEnum.EXCHANGE_CONTENT if _needExchangeForBuy(price) else None
        else:
            startState = BuyAndExchangeStateEnum.BUY_NOT_REQUIRED
        result = yield future_async.await(shared_events.showNeedRepairDialog(vehicle=self.__vehicle, startState=startState))
        callback(result.result if not result.busy else False)
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
        items = self._itemsCache.items
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


class ConvertBlueprintFragmentAction(IGUIItemAction):

    def __init__(self, vehicleCD, fragmentCount=1, fragmentPosition=-1):
        super(ConvertBlueprintFragmentAction, self).__init__()
        self.__vehicleCD = vehicleCD
        self.__fragmentPosition = fragmentPosition
        self.__fragmentCount = fragmentCount

    @decorators.process('blueprints/convertFragments')
    def doAction(self):
        result = yield ConvertBlueprintFragmentProcessor(self.__vehicleCD, fragmentPosition=self.__fragmentPosition, count=self.__fragmentCount).request()
        if not result or not result.success:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_CONVERSION_ERROR, type=result.sysMsgType)


class UseCrewBookAction(IGUIItemAction):

    def __init__(self, bookCD, vehicleCD, tankmanId=None):
        super(UseCrewBookAction, self).__init__()
        self.__bookCD = bookCD
        self.__vehicleCD = vehicleCD
        self.__tankmanId = tankmanId

    @decorators.process('crewBooks/useCrewBook')
    def doAction(self):
        result = yield UseCrewBookProcessor(self.__bookCD, self.__vehicleCD, self.__tankmanId).request()
        if result.success:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.CREWBOOKS_FAILED, type=result.sysMsgType)


class UpgradeOptDeviceAction(AsyncGUIItemAction):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, module, vehicle, slotIdx, parent=None):
        super(UpgradeOptDeviceAction, self).__init__()
        self.__parent = parent
        self.__module = module
        self.__vehicle = vehicle
        self.__slotIdx = slotIdx

    @async
    @decorators.process('moduleUpgrade')
    def _action(self, callback):
        result = yield ModuleUpgradeProcessor(self.__module, self.__vehicle, self.__slotIdx).request()
        callback(result)

    @async
    @future_async.async
    def _confirm(self, callback):
        from gui.impl.dialogs import dialogs
        result, data = yield future_async.await(dialogs.trophyDeviceUpgradeConfirm(self.__module, parent=self.__parent))
        if result and data.get('needCreditsExchange', False):
            exchangeResult = yield future_async.await(dialogs.showExchangeToUpgradeDeviceDialog(self.__module, parent=self.__parent))
            callback(not exchangeResult.busy and exchangeResult.result)
        else:
            callback(result)


class InstallBattleAbilities(AsyncGUIItemAction):
    __slots__ = ('__vehicle',)

    def __init__(self, vehicle):
        super(InstallBattleAbilities, self).__init__()
        self.__vehicle = vehicle

    @async
    @decorators.process('techMaintenance')
    def _action(self, callback):
        result = yield InstallBattleAbilitiesProcessor(self.__vehicle).request()
        callback(result)


class RemoveOptionalDevice(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__device', '__slotID', '__destroy', '__forFitting', '__removeProcessor')
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, vehicle, device, slotID, destroy=False, forFitting=False):
        super(RemoveOptionalDevice, self).__init__()
        self.__vehicle = vehicle
        self.__device = device
        self.__slotID = slotID
        self.__destroy = destroy
        self.__forFitting = forFitting
        self.__removeProcessor = OptDeviceInstaller(self.__vehicle, self.__device, self.__slotID, install=False, financeOperation=not self.__destroy, skipConfirm=True)

    @async
    @future_async.async
    def _confirm(self, callback):
        if self.__device.isRemovable:
            callback(True)
        elif self.__destroy:
            isOk, _ = yield future_async.await_callback(shared_events.showOptionalDeviceDestroy)(self.__device.intCD)
            callback(isOk)
        else:
            demountKit = self.__goodiesCache.getDemountKit()
            isDkEnabled = demountKit and demountKit.enabled
            if self.__device.isDeluxe or not isDkEnabled:
                dialog = shared_events.showOptionalDeviceDemountSinglePrice
            else:
                dialog = shared_events.showOptionalDeviceDemount
            isOk, data = yield future_async.await_callback(dialog)(self.__device.intCD, forFitting=self.__forFitting)
            self.__removeProcessor.requestCtx['useDemountKit'] = data.get('useDemountKit', False)
            callback(isOk)

    @async
    @process
    def _action(self, callback):
        result = yield self.__removeProcessor.request()
        callback(result)
