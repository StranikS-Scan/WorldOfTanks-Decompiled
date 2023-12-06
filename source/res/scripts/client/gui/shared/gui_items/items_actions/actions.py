# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/items_actions/actions.py
import logging
from collections import namedtuple
from functools import partial
from itertools import chain
import typing
from typing import Callable
import wg_async as future_async
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from adisp import adisp_process, adisp_async
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.bootcamp.lobby.unlock import BCUnlockItemConfirmator
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import BuyModuleMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import LocalSellModuleMeta
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta, ExchangeCreditsForSlotMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeXpMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import RestoreExchangeCreditsMeta
from gui.Scaleform.daapi.view.lobby.techtree import unlock
from gui.Scaleform.daapi.view.lobby.techtree.settings import RequestState
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.goodies.demount_kit import getDemountKitForOptDevice
from gui.impl import backport
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PREMIUM_BOOSTER_IDS, BUY_AND_ACTIVATE_TIMEOUT
from gui.impl.gen import R
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.personal_reserves import personal_reserves_dialogs
from gui.impl.lobby.personal_reserves.personal_reserves_utils import canBuyBooster as utilsCanBuyBooster
from gui.shared import event_dispatcher as shared_events
from gui.shared.economics import getGUIPrice
from gui.shared.event_dispatcher import showDeconstructionMultDeviceDialog, showDeconstructionDeviceDialog
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.fitting_item import canBuyWithGoldExchange
from gui.shared.gui_items.gui_item_economics import getVehicleShellsLayoutPrice
from gui.shared.gui_items.processors import makeSuccess
from gui.shared.gui_items.processors.common import ConvertBlueprintFragmentProcessor, BuyBattleAbilitiesProcessor
from gui.shared.gui_items.processors.common import TankmanBerthsBuyer
from gui.shared.gui_items.processors.common import UseCrewBookProcessor
from gui.shared.gui_items.processors.tankman import TankmanFreeToOwnXpConvertor, TankmanRetraining, TankmanUnload, TankmanEquip, TankmanChangePassport, TankmanDismiss, TankmanRestore, TankmanChangeRole
from gui.shared.gui_items.processors.goodies import BoosterBuyer, BoosterActivator
from gui.shared.gui_items.processors.messages.items_processor_messages import ItemDeconstructionProcessorMessage, MultItemsDeconstructionProcessorMessage
from gui.shared.gui_items.processors.module import BuyAndInstallItemProcessor, BCBuyAndInstallItemProcessor, OptDeviceInstaller, ModuleDeconstruct
from gui.shared.gui_items.processors.module import ModuleSeller
from gui.shared.gui_items.processors.module import ModuleUpgradeProcessor
from gui.shared.gui_items.processors.module import MultipleModulesSeller
from gui.shared.gui_items.processors.module import getInstallerProcessor
from gui.shared.gui_items.processors.veh_post_progression import ChangeVehicleSetupEquipments, DiscardPairsProcessor, PurchasePairProcessor, PurchaseStepsProcessor, SetEquipmentSlotTypeProcessor, SwitchPrebattleAmmoPanelAvailability
from gui.shared.gui_items.processors.vehicle import OptDevicesInstaller, BuyAndInstallConsumablesProcessor, AutoFillVehicleLayoutProcessor, BuyAndInstallBattleBoostersProcessor, BuyAndInstallShellsProcessor, VehicleRepairer, InstallBattleAbilitiesProcessor
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.gui_items.processors.vehicle import tryToLoadDefaultShellsLayout
from gui.shared.money import ZERO_MONEY, Money, Currency
from gui.shared.utils import decorators
from gui.shared.utils.requesters import RequestCriteria, REQ_CRITERIA
from gui.shop import showBuyGoldForPersonalReserves, showBuyGoldForSlot
from helpers import dependency
from items import vehicles, ITEM_TYPE_NAMES, parseIntCompactDescr
from shared_utils import first, allEqual
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWotPlusController
from soft_exception import SoftException
from uilogging.personal_reserves.logging_constants import PersonalReservesLogDialogs
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.goodies.goodie_items import Booster
_logger = logging.getLogger(__name__)
ItemSellSpec = namedtuple('ItemSellSpec', ('typeIdx', 'intCD', 'count'))
ItemDeconstructSpec = namedtuple('ItemDeconstructSpec', ('typeIdx', 'intCD', 'vehicleCD'))

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


class GroupedItemAction(CachedItemAction):
    __slots__ = ('_groupID', '_groupSize')

    def __init__(self, groupID, groupSize):
        super(GroupedItemAction, self).__init__()
        self._groupID = groupID
        self._groupSize = groupSize

    @staticmethod
    def _pushGroupedMessages(result):
        if result and result.auxData:
            if result.success:
                SystemMessages.pushMessage(result.userMsg + ' ' + ', '.join((m.userMsg for m in result.auxData if m)), type=result.sysMsgType, priority=result.msgPriority, messageData=result.msgData)
            else:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


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

    @adisp_process
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

    @adisp_process
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

    @adisp_process
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

    @adisp_process
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

    @adisp_process
    def doAction(self):
        item = self._itemsCache.items.getItemByCD(self.__vehCD)
        if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
            _logger.error('Value of int-type descriptor is not refer to vehicle %r', self.__vehCD)
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

    @adisp_process
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

    @decorators.adisp_process('research')
    def __doUnlockItem(self, plugins):
        result = yield unlock.UnlockItemProcessor(self._unlockProps.parentID, self._unlockProps.unlockIdx, plugins=plugins).request()
        self._showResult(result)


class BCUnlockItemAction(UnlockItemAction):
    _itemConfirmatorCls = BCUnlockItemConfirmator
    _itemValidatorCls = unlock.UnlockItemValidator


class UnlockItemActionWithResult(_UnlockItem):

    @adisp_async
    @adisp_process
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

    @adisp_async
    @decorators.adisp_process('research')
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

    @adisp_process
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
            result = yield proc.request()
            SystemMessages.pushMessagesFromResult(result)
        RequestState.received(state)
        yield lambda callback=None: callback
        return


class BuyAndInstallItemAction(InstallItemAction):
    _buyAndInstallItemProcessorCls = BuyAndInstallItemProcessor

    @adisp_process
    def doAction(self):
        if RequestState.inProcess('buyAndInstall'):
            SystemMessages.pushI18nMessage('#system_messages:shop/item/buy_and_equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        yield self.buyAndInstallItem(self._itemCD, self._rootCD, 'buyAndInstall')

    @adisp_async
    @adisp_process
    def buyAndInstallItem(self, itemCD, rootCD, state, callback):
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
            SystemMessages.pushMessagesFromResult(result)
            if result.success and item.itemTypeID in (GUI_ITEM_TYPE.TURRET, GUI_ITEM_TYPE.GUN):
                item = self._itemsCache.items.getItemByCD(itemCD)
                vehicle = self._itemsCache.items.getItemByCD(rootCD)
                if item.isInstalled(vehicle):
                    yield tryToLoadDefaultShellsLayout(vehicle)
            callback((result, proc.requestCtx))
        RequestState.received(state)
        yield lambda callback=None: partial(callback, (False, {}))
        return


class BuyAndInstallWithOptionalSellItemAction(BuyAndInstallItemAction):
    AUTO_SELL_KEY = 'sellPreviousModule'

    @adisp_process
    def doAction(self):
        if RequestState.inProcess('buyAndInstall'):
            SystemMessages.pushI18nMessage('#system_messages:shop/item/buy_and_equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
        itemToSellCD = self._getItemToBeReplaced(self._itemCD)
        isSuccess, data = yield self.buyAndInstallItem(self._itemCD, self._rootCD, 'buyAndInstall')
        _logger.debug('buyAndInstallAction was a success: %s data: %s', isSuccess, data)
        if self.AUTO_SELL_KEY in data and data[self.AUTO_SELL_KEY]:
            self.sellModule(itemToSellCD)

    def _getItemToBeReplaced(self, itemCD):
        vehicle = self._itemsCache.items.getItemByCD(self._rootCD)
        itemTypeIdx, _, _ = parseIntCompactDescr(itemCD)
        installedModuleCD = vehicle.descriptor.getComponentsByType(ITEM_TYPE_NAMES[itemTypeIdx])[0].compactDescr
        return installedModuleCD

    @adisp_process
    def sellModule(self, moduleToSellCD):
        moduleToSell = self._itemsCache.items.getItemByCD(moduleToSellCD)
        _logger.debug('sellModule module %s isInInventory=%s itemsCache synced %s', moduleToSell.userName, moduleToSell.isInInventory, self._itemsCache.isSynced())
        if moduleToSell.isInInventory:
            result = yield ModuleSeller(moduleToSell, count=1).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        else:
            yield lambda callback=None: callback
        return


class BCBuyAndInstallItemAction(BuyAndInstallItemAction):
    _buyAndInstallItemProcessorCls = BCBuyAndInstallItemProcessor


class VehicleAutoFillLayoutAction(IGUIItemAction):

    def __init__(self, vehicle):
        super(VehicleAutoFillLayoutAction, self).__init__()
        self.__vehicle = vehicle

    @decorators.adisp_process('techMaintenance')
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

    @adisp_async
    @adisp_process
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

    @adisp_async
    def _confirm(self, callback):
        callback(True)

    @adisp_async
    @adisp_process
    def _action(self, callback):
        result = yield lambda callback: callback(None)
        callback(result)

    def _showResult(self, result):
        SystemMessages.pushMessagesFromResult(result)


class AmmunitionBuyAndInstall(AsyncGUIItemAction):
    __slots__ = ('_vehicle', '_changedItems', '__confirmOnlyExchange')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, changeItems, confirmOnlyExchange=False):
        self._vehicle = vehicle
        self._changedItems = changeItems
        self.__confirmOnlyExchange = confirmOnlyExchange
        super(AmmunitionBuyAndInstall, self).__init__()

    @adisp_async
    @future_async.wg_async
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
            result = yield future_async.wg_await(shared_events.showTankSetupConfirmDialog(items=self._changedItems, vehicle=self._vehicle, startState=startState))
            callback(result.result[0] if not result.busy else False)


class BuyAndInstallOptDevices(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False):
        optDevices = vehicle.optDevices
        changeItems = [ item for item in optDevices.layout.getItems() if not vehicle.optDevices.setupLayouts.isInSetup(item) ]
        super(BuyAndInstallOptDevices, self).__init__(vehicle, changeItems, confirmOnlyExchange)

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield OptDevicesInstaller(self._vehicle).request()
        callback(result)


class BuyAndInstallConsumables(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False):
        changeItems = [ item for item in vehicle.consumables.layout.getItems() if not vehicle.consumables.setupLayouts.isInSetup(item) ]
        super(BuyAndInstallConsumables, self).__init__(vehicle, changeItems, confirmOnlyExchange)

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield BuyAndInstallConsumablesProcessor(self._vehicle).request()
        callback(result)


class BuyAndInstallBattleBoosters(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False):
        changeItems = [ item for item in vehicle.battleBoosters.layout.getItems() if not vehicle.battleBoosters.setupLayouts.isInSetup(item) ]
        super(BuyAndInstallBattleBoosters, self).__init__(vehicle, changeItems, confirmOnlyExchange)

    @adisp_async
    @decorators.adisp_process('techMaintenance')
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

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield BuyAndInstallShellsProcessor(self.__vehicle).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
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
            result = yield future_async.wg_await(shared_events.showRefillShellsDialog(price=self.__price, shells=self.__vehicle.shells.layout.getItems(), startState=startState))
            callback(result.result[0] if not result.busy else False)


class VehicleRepairAction(AsyncGUIItemAction):

    def __init__(self, vehicle, wrappedViewClass, repairClazz):
        super(VehicleRepairAction, self).__init__()
        self.__vehicle = vehicle
        self.__wrappedViewClass = wrappedViewClass
        self.__repairClazz = repairClazz

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield VehicleRepairer(self.__vehicle).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        if self.__vehicle.repairCost > 0:
            price = Money(credits=self.__vehicle.repairCost)
            startState = BuyAndExchangeStateEnum.EXCHANGE_CONTENT if _needExchangeForBuy(price) else None
        else:
            startState = BuyAndExchangeStateEnum.BUY_NOT_REQUIRED
        result = yield future_async.wg_await(shared_events.showNeedRepairDialog(vehicle=self.__vehicle, startState=startState, wrappedViewClass=self.__wrappedViewClass, repairClazz=self.__repairClazz))
        callback(result.result if not result.busy else False)
        return


class BuyVehicleSlotAction(CachedItemAction):
    __itemsCache = dependency.descriptor(IItemsCache)
    __DEFAULT_FLOW = -1
    __NO_ENOUGH_CREDITS_FLOW = 0
    __NO_ENOUGH_GOLD_FLOW = 1

    def __init__(self):
        super(BuyVehicleSlotAction, self).__init__()
        self.__price = self.__itemsCache.items.shop.getVehicleSlotsPrice(self.__itemsCache.items.stats.vehicleSlots)
        self.__currency = self.__price.getCurrency()

    @decorators.adisp_process('buySlot')
    def doAction(self):
        isEnoughMoney, status = self.__checkMoney()
        if not isEnoughMoney:
            if status == self.__NO_ENOUGH_GOLD_FLOW:
                showBuyGoldForSlot(self.__price)
                return
            if status == self.__NO_ENOUGH_CREDITS_FLOW:
                isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsForSlotMeta(name=backport.text(R.strings.dialogs.buySlot.hangarSlot.header()), count=1, price=self.__price.get(Currency.CREDITS)))
                if not isOk:
                    return
        result = yield VehicleSlotBuyer().request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def __checkMoney(self):
        availableMoney = self.__itemsCache.items.stats.money
        if self.__currency == Currency.GOLD and availableMoney.gold < self.__price.gold:
            return (False, self.__NO_ENOUGH_GOLD_FLOW)
        return (False, self.__NO_ENOUGH_CREDITS_FLOW) if self.__currency == Currency.CREDITS and availableMoney.credits < self.__price.credits and _needExchangeForBuy(self.__price) else (True, self.__DEFAULT_FLOW)


class BuyBerthsAction(CachedItemAction):

    def __init__(self, berthPrice, countPacksBerths, groupID=0, groupSize=1):
        super(BuyBerthsAction, self).__init__()
        self.__berthPrice = berthPrice
        self.__countPacksBerths = countPacksBerths

    @decorators.adisp_process('buyBerths')
    def doAction(self):
        result = yield TankmanBerthsBuyer(self.__berthPrice, self.__countPacksBerths).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class TankmanRestoreAction(GroupedItemAction):

    def __init__(self, tankmanInvID, useBerthCount=1, groupID=0, groupSize=1):
        super(TankmanRestoreAction, self).__init__(groupID, groupSize)
        self.__tankmanInvID = tankmanInvID
        self.__useBerth = useBerthCount

    @decorators.adisp_process('updating')
    def doAction(self):
        tankman = self._itemsCache.items.getTankman(self.__tankmanInvID)
        result = yield TankmanRestore(tankman, self.__useBerth, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)


class BuyBoosterAction(CachedItemAction):

    def __init__(self, booster, count, currency):
        super(BuyBoosterAction, self).__init__()
        self.booster = booster
        self.count = count
        self.currency = currency

    @adisp_async
    @decorators.adisp_process('buyItem')
    def doAction(self, callback):
        result = yield BoosterBuyer(self.booster, self.count, self.currency).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)


class ActivateBoosterAction(CachedItemAction):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, booster):
        super(ActivateBoosterAction, self).__init__()
        self.booster = booster

    @adisp_process
    def doAction(self):
        canActivate = True
        if not self.skipConfirm:
            canActivate = yield self.canActivate()
        if canActivate:
            result = yield BoosterActivator(self.booster).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @adisp_async
    @adisp_process
    def canActivate(self, callback):
        booster = self.booster
        if not booster.isInAccount:
            callback(False)
        canActivate = True
        if self.isReplacement():
            canActivate = yield self.canReplace()
        callback(canActivate)

    def isReplacement(self):
        activeBoosterTypes = [ boosterType for boosterType, _, _ in self.goodiesCache.getActiveResources() ]
        return self.booster.boosterType in activeBoosterTypes

    def isPremium(self, booster):
        return booster.boosterID in PREMIUM_BOOSTER_IDS

    def isUpgrade(self, newBooster, currentBooster):
        return self.isPremium(newBooster) and not self.isPremium(currentBooster)

    @adisp_async
    @adisp_process
    def canReplace(self, callback):
        booster = self.booster
        criteria = RequestCriteria(REQ_CRITERIA.BOOSTER.BOOSTER_TYPES([booster.boosterType]), REQ_CRITERIA.BOOSTER.ACTIVE)
        boosters = self.goodiesCache.getBoosters(criteria=criteria).values()
        currentBooster = boosters[0]
        canActivate = False
        if self.isUpgrade(booster, currentBooster):
            dialog = personal_reserves_dialogs.getUpgradeBoosterDialog(booster=booster, previousBooster=currentBooster)
            canActivate = yield personal_reserves_dialogs.showDialogAndLogInteraction(dialog, dialogLogItem=PersonalReservesLogDialogs.BUY_AND_UPGRADE)
        callback(canActivate)


class BuyAndActivateBooster(ActivateBoosterAction):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, booster):
        super(BuyAndActivateBooster, self).__init__(booster)
        self.currency = Currency.GOLD
        self.__asyncEvent = future_async.AsyncEvent()

    def canBuyBooster(self, booster):
        return utilsCanBuyBooster(booster, self._itemsCache)

    @adisp_process
    def doAction(self):
        booster = self.booster
        canActivate = booster.isInAccount
        mustBuy = not canActivate
        canDoAction = False
        if mustBuy:
            canPurchase, reason = self.canBuyBooster(booster)
            if not canPurchase:
                if reason == GUI_ITEM_ECONOMY_CODE.getCurrencyError(self.currency):
                    yield self.handleGoldPurchase(booster)
                _logger.info('[BuyAndActivateBooster] booster can not be bought, reason %s', reason)
                return
        if self.isReplacement():
            canDoAction = yield self.canReplace()
        elif mustBuy:
            dialog = personal_reserves_dialogs.getBuyAndActivateBoosterDialog(booster)
            canDoAction = yield personal_reserves_dialogs.showDialogAndLogInteraction(dialog, dialogLogItem=PersonalReservesLogDialogs.BUY_AND_ACTIVATE)
        if canDoAction and mustBuy:
            action = BuyBoosterAction(booster, 1, self.currency)
            canActivate = yield action.doAction()
            if canActivate and not booster.isInAccount:
                yield self.waitForClientUpdate()
        if canDoAction and canActivate:
            action = ActivateBoosterAction(booster)
            action.skipConfirm = True
            action.doAction()

    @adisp_async
    @adisp_process
    def handleGoldPurchase(self, booster, callback):
        dialog = personal_reserves_dialogs.getBuyGoldDialog(booster)
        isConfirm = yield personal_reserves_dialogs.showDialogAndLogInteraction(dialog, dialogLogItem=PersonalReservesLogDialogs.BUY_GOLD)
        if isConfirm:
            showBuyGoldForPersonalReserves(booster.getBuyPrice().price.get(self.currency, 0))
        callback(False)

    @adisp_async
    @future_async.wg_async
    def waitForClientUpdate(self, callback):
        _logger.debug('[BuyAndActivate] waiting for cache update')
        clientUpdated = True
        Waiting.show('synchronize')
        g_playerEvents.onClientUpdated += self.__checkBoosterCount
        try:
            try:
                clientUpdated = yield future_async.await(self.__asyncEvent.wait(), timeout=BUY_AND_ACTIVATE_TIMEOUT)
            except future_async.TimeoutError:
                _logger.warning('TimeoutError: while waiting for client update after buying booster. Timeout period %d', BUY_AND_ACTIVATE_TIMEOUT)
                clientUpdated = False

        finally:
            g_playerEvents.onClientUpdated -= self.__checkBoosterCount
            Waiting.hide('synchronize')
            callback(clientUpdated)

    def __checkBoosterCount(self, diff, _):
        if self.booster.count > 0:
            g_playerEvents.onClientUpdated -= self.__checkBoosterCount
            self.__asyncEvent.set()


class ConvertBlueprintFragmentAction(IGUIItemAction):

    def __init__(self, vehicleCD, fragmentCount=1, fragmentPosition=-1, usedNationalFragments=None):
        super(ConvertBlueprintFragmentAction, self).__init__()
        self.__vehicleCD = vehicleCD
        self.__fragmentPosition = fragmentPosition
        self.__fragmentCount = fragmentCount
        self.__usedNationalFragments = usedNationalFragments

    @decorators.adisp_process('blueprints/convertFragments')
    def doAction(self):
        result = yield ConvertBlueprintFragmentProcessor(self.__vehicleCD, self.__fragmentCount, self.__fragmentPosition, self.__usedNationalFragments).request()
        if not result or not result.success:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_CONVERSION_ERROR, type=result.sysMsgType)


class UseCrewBookAction(GroupedItemAction):

    def __init__(self, bookCD, vehicleInvID, bookCount, tankmanInvID, groupID=0, groupSize=1):
        super(UseCrewBookAction, self).__init__(groupID, groupSize)
        self.__bookCD = bookCD
        self.__bookCount = bookCount
        self.__vehicleInvID = vehicleInvID
        self.__tankmanInvID = tankmanInvID

    @decorators.adisp_process('crewBooks/useCrewBook')
    def doAction(self):
        result = yield UseCrewBookProcessor(self.__bookCD, self.__bookCount, self.__vehicleInvID, self.__tankmanInvID, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)


class UseFreeXpToTankman(GroupedItemAction):

    def __init__(self, selectedXpForConvert, tankmanInvID, groupID=0, groupSize=1):
        super(UseFreeXpToTankman, self).__init__(groupID, groupSize)
        self.__tankmanInvID = tankmanInvID
        self.__selectedXpForConvert = selectedXpForConvert

    @decorators.adisp_process('updatingSkillWindow')
    def doAction(self):
        result = yield TankmanFreeToOwnXpConvertor(self.__tankmanInvID, self.__selectedXpForConvert, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)

    @staticmethod
    def _pushGroupedMessages(result):
        if result:
            if result.success:
                msg = result.userMsg
                if result.auxData:
                    msg += ' ' + ', '.join((m.userMsg for m in result.auxData if m))
                SystemMessages.pushMessage(msg, type=result.sysMsgType, priority=result.msgPriority, messageData=result.msgData)
            else:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class TankmanRetrainingAction(GroupedItemAction):

    def __init__(self, tankmanInvID, vehicleIntCD, tmanCostTypeIdx, groupID=0, groupSize=1):
        super(TankmanRetrainingAction, self).__init__(groupID, groupSize)
        self.__tankmanInvID = tankmanInvID
        self.__vehicleIntCD = vehicleIntCD
        self.__tmanCostTypeIdx = tmanCostTypeIdx

    @decorators.adisp_process('retraining')
    def doAction(self):
        result = yield TankmanRetraining(self.__tankmanInvID, self.__vehicleIntCD, self.__tmanCostTypeIdx, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)


class TankmanChangeRoleAction(GroupedItemAction):

    def __init__(self, tankmanInvID, role, vehicleIntCD, vehSlotIdx=-1, groupID=0, groupSize=1):
        super(TankmanChangeRoleAction, self).__init__(groupID, groupSize)
        self.__tankmanInvID = tankmanInvID
        self.__vehicleIntCD = vehicleIntCD
        self.__role = role
        self.__vehSlotIdx = vehSlotIdx

    @decorators.adisp_process('changingRole')
    def doAction(self):
        result = yield TankmanChangeRole(self.__tankmanInvID, self.__role, self.__vehicleIntCD, self.__vehSlotIdx, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)


class TankmanChangePassportAction(IGUIItemAction):

    def __init__(self, tankmanInvID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        super(TankmanChangePassportAction, self).__init__()
        self.__tankmanInvID = tankmanInvID
        self.__firstNameID = firstNameID
        self.__firstNameGroup = firstNameGroup
        self.__lastNameID = lastNameID
        self.__lastNameGroup = lastNameGroup
        self.__iconID = iconID
        self.__iconGroup = iconGroup

    @decorators.adisp_process('updating')
    def doAction(self):
        yield TankmanChangePassport(self.__tankmanInvID, self.__firstNameID, self.__firstNameGroup, self.__lastNameID, self.__lastNameGroup, self.__iconID, self.__iconGroup).request()


class TankmanUnloadAction(GroupedItemAction):

    def __init__(self, vehicleInvID, vehicleSlotIdx, groupID=0, groupSize=1):
        super(TankmanUnloadAction, self).__init__(groupID, groupSize)
        self.__vehicleInvID = vehicleInvID
        self.__vehicleSlotIdx = vehicleSlotIdx

    @decorators.adisp_process('updating')
    def doAction(self):
        result = yield TankmanUnload(self.__vehicleInvID, self.__vehicleSlotIdx, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)


class TankmanEquipAction(GroupedItemAction):

    def __init__(self, tankmanInvID, vehicleInvID, vehicleSlotIdx, groupID=0, groupSize=1):
        super(TankmanEquipAction, self).__init__(groupID, groupSize)
        self.__tankmanInvID = tankmanInvID
        self.__vehicleInvID = vehicleInvID
        self.__vehicleSlotIdx = vehicleSlotIdx

    @decorators.adisp_process('updating')
    def doAction(self):
        result = yield TankmanEquip(self.__tankmanInvID, self.__vehicleInvID, self.__vehicleSlotIdx, self._groupID, self._groupSize).request()
        self._pushGroupedMessages(result)


class TankmanDismissAction(CachedItemAction):

    def __init__(self, tankmanInvID):
        super(TankmanDismissAction, self).__init__()
        self.__tankmanInvID = tankmanInvID

    @decorators.adisp_process('updating')
    def doAction(self):
        tankman = self._itemsCache.items.getTankman(self.__tankmanInvID)
        result = yield TankmanDismiss(tankman).request()
        SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)


class UpgradeOptDeviceAction(AsyncGUIItemAction):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, module, vehicle, setupIdx, slotIdx, onDeconstructed=None, parent=None):
        super(UpgradeOptDeviceAction, self).__init__()
        self.__parent = parent
        self.__device = module
        self.__vehicle = vehicle
        self.__setupIdx = setupIdx
        self.__slotIdx = slotIdx
        self.__onDeconstructed = onDeconstructed

    @adisp_async
    @decorators.adisp_process('moduleUpgrade')
    def _action(self, callback):
        result = yield ModuleUpgradeProcessor(self.__device, self.__vehicle, self.__setupIdx, self.__slotIdx).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        from gui.impl.dialogs import dialogs
        if self.__device.isModernized:
            confirmDialog = partial(dialogs.modernizedDeviceUpgradeConfirm, vehicle=self.__vehicle, onDeconstructed=self.__onDeconstructed)
        else:
            confirmDialog = dialogs.trophyDeviceUpgradeConfirm
        result, data = yield future_async.wg_await(confirmDialog(self.__device, parent=self.__parent))
        if result and data and data.get('needMoreCurrency', False):
            exchangeResult = yield future_async.wg_await(dialogs.showExchangeToUpgradeDeviceDialog(device=self.__device, parent=self.__parent))
            callback(not exchangeResult.busy and exchangeResult.result)
        else:
            callback(result)


class DeconstructOptDevice(AsyncGUIItemAction):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, module, vehicle, slotIdx, parent=None):
        super(DeconstructOptDevice, self).__init__()
        self.__module = module
        self.__parent = parent
        self.__vehicle = vehicle
        self.__slotIdx = slotIdx
        self.__deconstructStorageProcessor = ModuleDeconstruct(module, min(module.inventoryCount, MAX_ITEMS_FOR_OPERATION))
        self.__deconstructOnVehicleProcessor = OptDeviceInstaller(vehicle, module, slotIdx, install=False, allSetups=True, financeOperation=False, skipConfirm=True, showWaiting=False)

    @adisp_async
    @decorators.adisp_process('storage/forDeconstruct')
    def _action(self, callback):
        if self.__vehicle is not None:
            result = yield self.__deconstructOnVehicleProcessor.request()
        else:
            result = yield self.__deconstructStorageProcessor.request()
        callback(result)
        return

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        isOk, count = yield showDeconstructionDeviceDialog(self.__module.intCD, fromVehicle=self.__vehicle is not None)
        self.__deconstructStorageProcessor.count = count
        callback(isOk)
        return

    def _showResult(self, result):
        if result.success:
            count = 1 if self.__vehicle else self.__deconstructStorageProcessor.count
            msgRes = ItemDeconstructionProcessorMessage(self.__module, count).makeSuccessMsg()
            SystemMessages.pushMessagesFromResult(msgRes)
        else:
            SystemMessages.pushMessagesFromResult(result)


class DeconstructMultOptDevice(AsyncGUIItemAction):
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(DeconstructMultOptDevice, self).__init__()
        self.ctx = ctx
        self.__sellItems = ctx.cart.storage.values()
        self.__vehItems = list(chain(*ctx.cart.onVehicle.values()))
        self.__upgradeDevicePair = ctx.upgradedPair

    @adisp_async
    @decorators.adisp_process('storage/forDeconstruct')
    def _action(self, callback):
        if self.__sellItems:
            if allEqual(self.__sellItems, lambda i: i.intCD):
                itemToSell = first(self.__sellItems)
                item = self._itemsCache.items.getItemByCD(itemToSell.intCD)
                result = yield ModuleSeller(item, min(item.inventoryCount, MAX_ITEMS_FOR_OPERATION, itemToSell.count)).request()
            else:
                result = yield MultipleModulesSeller(self.__sellItems).request()
            if not result.success:
                callback(result)
                return
        if self.__vehItems:
            for itemSpec in self.__vehItems:
                _item = self._itemsCache.items.getItemByCD(itemSpec.intCD)
                _vehicle = self._itemsCache.items.getItemByCD(itemSpec.vehicleCD)
                _slotIdx = None
                for layoutIdx, setup in _vehicle.optDevices.setupLayouts.setups.iteritems():
                    if _item in setup:
                        _slotIdx = setup.index(_item)
                        break

                processor = OptDeviceInstaller(_vehicle, _item, _slotIdx, install=False, allSetups=True, financeOperation=False, skipConfirm=True, showWaiting=False)
                result = yield processor.request()
                if not result.success:
                    callback(result)
                    return

        modules = []
        itemsDict = {}
        for itemSpec in self.__sellItems + self.__vehItems:
            itemsList = itemsDict.setdefault(itemSpec.intCD, [])
            itemsList.append(itemSpec)

        for intCD, itemSpecs in sorted(itemsDict.items(), key=self.__sortItemsKey):
            item = self._itemsCache.items.getItemByCD(intCD)
            count = sum(((itemSpec.count if isinstance(itemSpec, ItemSellSpec) else 1) for itemSpec in itemSpecs))
            modules.append((item, count))

        if modules:
            decResult = MultItemsDeconstructionProcessorMessage(modules).makeSuccessMsg()
            self._showResult(decResult)
        if self.__upgradeDevicePair:
            _item, vehicleCD = self.__upgradeDevicePair
            _vehicle = None
            _setupIdx = None
            _slotIdx = None
            if vehicleCD:
                _vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
                _slotIdx = None
                _setupIdx = None
                for layoutIdx, setup in _vehicle.optDevices.setupLayouts.setups.iteritems():
                    if _item in setup:
                        _setupIdx = layoutIdx
                        _slotIdx = setup.index(_item)
                        break

            result = yield ModuleUpgradeProcessor(_item, _vehicle, _setupIdx, _slotIdx, validateMoney=False).request()
            callback(result)
        callback(makeSuccess())
        return

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        isOk, _ = yield future_async.wg_await(showDeconstructionMultDeviceDialog)(self.ctx)
        callback(isOk)

    def __sortItemsKey(self, item):
        itemCD, _ = item
        item = self._itemsCache.items.getItemByCD(itemCD)
        return (-item.level, item.userName)


class InstallBattleAbilities(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__classVehs', '__setupItems')

    def __init__(self, vehicle, classVehs=False, setupItems=None):
        super(InstallBattleAbilities, self).__init__()
        self.__vehicle = vehicle
        self.__classVehs = classVehs
        self.__setupItems = setupItems

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield InstallBattleAbilitiesProcessor(self.__vehicle, self.__classVehs).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        if not self.__setupItems:
            callback(True)
        else:
            dialogResult = yield future_async.wg_await(shared_events.showBattleAbilitiesConfirmDialog(items=self.__setupItems, withInstall=bool(self.__setupItems), vehicleType=self.__vehicle.type, applyForAllVehiclesByType=self.__classVehs))
            if dialogResult is None or dialogResult.busy:
                callback(False)
            isOK, _ = dialogResult.result
            callback(isOK)
        return


class BuyBattleAbilities(AsyncGUIItemAction):
    __slots__ = ('__skillIDs',)

    def __init__(self, skillIDs):
        super(BuyBattleAbilities, self).__init__()
        self.__skillIDs = skillIDs

    @adisp_async
    @decorators.adisp_process('buyItem')
    def _action(self, callback):
        result = yield BuyBattleAbilitiesProcessor(self.__skillIDs).request()
        callback(result)


class RemoveOptionalDevice(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__device', '__slotID', '__destroy', '__forFitting', '__everywhere', '__removeProcessor')
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def __init__(self, vehicle, device, slotID, destroy=False, forFitting=False, everywhere=True):
        super(RemoveOptionalDevice, self).__init__()
        self.__vehicle = vehicle
        self.__device = device
        self.__slotID = slotID
        self.__destroy = destroy
        self.__forFitting = forFitting
        self.__everywhere = everywhere
        self.__removeProcessor = OptDeviceInstaller(self.__vehicle, self.__device, self.__slotID, install=False, allSetups=self.__everywhere, financeOperation=not self.__destroy and self.__everywhere, skipConfirm=True)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        isFreeToDemount = self.__wotPlusController.isFreeToDemount(self.__device)
        if self.__device.isRemovable:
            callback(True)
        elif self.__destroy:
            if isFreeToDemount:
                callback(False)
                return
            isOk, _ = yield future_async.await_callback(shared_events.showOptionalDeviceDestroy)(self.__device.intCD)
            callback(isOk)
        else:
            if isFreeToDemount:
                callback(True)
                return
            if self.__everywhere:
                demountKit, _ = getDemountKitForOptDevice(self.__device)
                isDkEnabled = demountKit and demountKit.enabled
                if self.__device.isDeluxe or not isDkEnabled:
                    dialog = shared_events.showOptionalDeviceDemountSinglePrice
                else:
                    dialog = shared_events.showOptionalDeviceDemount
            else:
                dialog = partial(shared_events.showOptionalDeviceDemountFromSlot, vehicle=self.__vehicle)
            isOk, data = yield future_async.await_callback(dialog)(self.__device.intCD, forFitting=self.__forFitting)
            self.__removeProcessor.requestCtx['useDemountKit'] = data.get('useDemountKit', False)
            callback(isOk)

    @adisp_async
    @adisp_process
    def _action(self, callback):
        result = yield self.__removeProcessor.request()
        callback(result)


class ChangeSetupEquipmentsIndex(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__groupID', '__layoutIdx')

    def __init__(self, vehicle, groupID, layoutIdx):
        super(ChangeSetupEquipmentsIndex, self).__init__()
        self.__vehicle = vehicle
        self.__groupID = groupID
        self.__layoutIdx = layoutIdx

    @adisp_async
    @adisp_process
    def _action(self, callback):
        result = yield ChangeVehicleSetupEquipments(self.__vehicle, self.__groupID, self.__layoutIdx).request()
        callback(result)


class SwitchPrebattleAmmoPanelAvailabilityAction(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__groupID', '__enabled')

    def __init__(self, vehicle, groupID, enabled):
        super(SwitchPrebattleAmmoPanelAvailabilityAction, self).__init__()
        self.__vehicle = vehicle
        self.__groupID = groupID
        self.__enabled = enabled

    @adisp_async
    @adisp_process
    def _action(self, callback):
        result = yield SwitchPrebattleAmmoPanelAvailability(self.__vehicle, self.__groupID, self.__enabled).request()
        callback(result)


class DiscardPostProgressionPairs(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__stepIDs', '__modIDs')

    def __init__(self, vehicle, stepIDs, modIDs):
        super(DiscardPostProgressionPairs, self).__init__()
        self.__vehicle = vehicle
        self.__stepIDs = stepIDs
        self.__modIDs = modIDs

    @adisp_async
    @decorators.adisp_process('loadPage')
    def _action(self, callback):
        result = yield DiscardPairsProcessor(self.__vehicle, self.__stepIDs, self.__modIDs).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        result = yield future_async.wg_await(shared_events.showDestroyPairModificationsDialog)(self.__vehicle, self.__stepIDs)
        callback(result.result[0] if not result.busy else False)


class PurchasePostProgressionPair(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__stepID', '__modificationID')

    def __init__(self, vehicle, stepID, modificationID):
        super(PurchasePostProgressionPair, self).__init__()
        self.__vehicle = vehicle
        self.__stepID = stepID
        self.__modificationID = modificationID

    @adisp_async
    @decorators.adisp_process('loadPage')
    def _action(self, callback):
        result = yield PurchasePairProcessor(self.__vehicle, self.__stepID, self.__modificationID).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        result = yield future_async.wg_await(shared_events.showPostProgressionPairModDialog)(self.__vehicle, self.__stepID, self.__modificationID)
        callback(result.result[0] if not result.busy else False)


class PurchasePostProgressionSteps(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__stepIDs')

    def __init__(self, vehicle, stepIDs):
        super(PurchasePostProgressionSteps, self).__init__()
        self.__vehicle = vehicle
        self.__stepIDs = stepIDs

    @adisp_async
    @decorators.adisp_process('loadPage')
    def _action(self, callback):
        result = yield PurchaseStepsProcessor(self.__vehicle, self.__stepIDs).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        result = yield future_async.wg_await(shared_events.showPostProgressionResearchDialog)(self.__vehicle, self.__stepIDs)
        callback(result.result[0] if not result.busy else False)


class SetEquipmentSlotType(AsyncGUIItemAction):
    __slots__ = ('__vehicle', '__slotID')
    __uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, vehicle):
        super(SetEquipmentSlotType, self).__init__()
        self.__vehicle = vehicle
        self.__slotID = 0

    @adisp_async
    @decorators.adisp_process('loadContent')
    def _action(self, callback):
        result = yield SetEquipmentSlotTypeProcessor(self.__vehicle, self.__slotID).request()
        callback(result)

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        if self.__uiLoader.windowsManager.getViewByLayoutID(layoutID=R.views.lobby.common.SelectSlotSpecDialog()):
            callback(False)
            return
        Waiting.show('loadModalWindow', softStart=True)
        from gui.impl.lobby.common.select_slot_spec_dialog import showDialog
        result = yield future_async.wg_await(showDialog(self.__vehicle))
        if result.busy:
            callback(False)
        else:
            isOk, idx = result.result
            _logger.debug('Select slot specialization dialog result: isOk: %r, idx: %r', isOk, idx)
            if isOk and idx > 0:
                self.__slotID = idx
                callback(True)
            else:
                callback(False)
