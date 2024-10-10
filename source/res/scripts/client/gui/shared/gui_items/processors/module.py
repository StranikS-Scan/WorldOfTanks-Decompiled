# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/module.py
import typing
import logging
import AccountCommands
import BigWorld
from constants import EquipSideEffect
from gui import makeHtmlString
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import ItemRemovalByDemountKitEvent
from gui.shared.formatters import formatPrice, icons, getBWFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_EMPTY
from gui.shared.gui_items.gui_item_economics import getItemBuyPrice
from gui.shared.gui_items.processors import ItemProcessor, makeI18nSuccess, makeI18nError, VehicleItemProcessor, plugins, makeSuccess, Processor
from gui.shared.gui_items.processors.messages.items_processor_messages import OptDevicesDemountProcessorMessage, OptDeviceRemoveProcessorMessage, ItemDestroyProcessorMessage
from gui.shared.gui_items.vehicle_modules import VehicleTurret, VehicleGun
from gui.shared.money import Currency
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    pass
MULTIPLE_SELLING_TEMPLATE = 'multipleSelling/{}'
_logger = logging.getLogger(__name__)

def _getIconHtmlTagForCurrency(currency):
    getter = getattr(icons, currency)
    if getter:
        return getter()
    _logger.error('Could not fetch an icon getter for the following currency %s', currency)


def _formatCurrencyValue(currency, value):
    formatter = getBWFormatter(currency)
    return formatter(value)


def _wrapHtmlMessage(key, message):
    return makeHtmlString('html_templates:lobby/dialogs', key, {'message': message})


class ModuleProcessor(ItemProcessor):
    ITEMS_MSG_PREFIXES = {GUI_ITEM_TYPE.SHELL: 'shell',
     GUI_ITEM_TYPE.EQUIPMENT: 'artefact',
     GUI_ITEM_TYPE.OPTIONALDEVICE: 'artefact',
     GUI_ITEM_TYPE.BATTLE_BOOSTER: 'battleBooster',
     GUI_ITEM_TYPE.CREW_BOOKS: 'crewBooks'}
    DEFAULT_PREFIX = 'module'

    def __init__(self, item, opType, plugs=tuple()):
        ItemProcessor.__init__(self, item, plugs + (plugins.ModuleValidator(item),))
        self.opType = opType

    def _getMsgCtx(self):
        raise NotImplementedError

    def _formMessage(self, msg):
        _logger.debug('Generating response for ModuleProcessor: %s, %s', self.opType, msg)
        return '{itemType}_{opType}/{msg}'.format(itemType=self.ITEMS_MSG_PREFIXES.get(self.item.itemTypeID, self.DEFAULT_PREFIX), opType=self.opType, msg=msg)

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            errStr = 'server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'server_error_centerDown'
        return makeI18nError(sysMsgKey=self._formMessage(errStr), defaultSysMsgKey=self._formMessage('server_error'), auxData={'errStr': errStr}, **self._getMsgCtx())


class ModuleTradeProcessor(ModuleProcessor):

    def __init__(self, item, count, opType, plugs=tuple()):
        super(ModuleTradeProcessor, self).__init__(item, opType, plugs)
        self.count = count

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getOpPrice().price)}

    def _getOpPrice(self):
        raise NotImplementedError


class ModuleBuyer(ModuleTradeProcessor):

    def __init__(self, item, count, currency):
        super(ModuleBuyer, self).__init__(item, count, 'buy')
        self._currency, self._itemPrice = self._getItemCurrencyAndPrice(currency)
        self.addPlugins((plugins.MoneyValidator(self._getOpPrice().price), plugins.ModuleConfigValidator(item)))

    def _getItemCurrencyAndPrice(self, currency):
        itemPrice = getItemBuyPrice(self.item, currency, self.itemsCache.items.shop)
        if itemPrice is None:
            itemPrice = self.item.buyPrices.itemPrice
            currency = itemPrice.getCurrency(byWeight=True)
        return (currency, itemPrice)

    def _getOpPrice(self):
        return self._itemPrice * self.count

    def _getSysMsgType(self):
        return CURRENCY_TO_SM_TYPE.get(self._currency, SM_TYPE.PurchaseForCredits)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=self._formMessage('success'), type=self._getSysMsgType(), **self._getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to buy %s module(s) %s for currency %s (item price - %s)', self.count, self.item, self._currency, self._itemPrice)
        originalCurrency = self.item.buyPrices.itemPrice.getCurrency()
        goldForCredits = originalCurrency == Currency.GOLD and self._currency == Currency.CREDITS and getItemBuyPrice(self.item, self._currency, self.itemsCache.items.shop) is not None
        BigWorld.player().shop.buy(self.item.itemTypeID, self.item.nationID, self.item.intCD, self.count, int(goldForCredits), lambda code: self._response(code, callback))
        return


class BookBuyer(ModuleBuyer):

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getOpPrice().price, justValue=True)}


class ModuleSeller(ModuleTradeProcessor):

    def __init__(self, item, count):
        super(ModuleSeller, self).__init__(item, count, 'sell')

    def _getOpPrice(self):
        return self.item.sellPrices.itemPrice * self.count

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Selling, **self._getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to sell item: %s, %s', self.item, self.count)
        itemTypeID, _, _ = vehicles.parseIntCompactDescr(self.item.intCD)
        BigWorld.player().inventory.sell(itemTypeID, self.item.intCD, self.count, lambda code: self._response(code, callback))


class ModuleDeconstruct(ModuleSeller):

    def _successHandler(self, code, ctx=None):
        msgCtx = self._getMsgCtx()
        msgCtx['kind'] = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.deconstructing.head())
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Deconstructing, **msgCtx)


class MultipleModulesSeller(Processor):

    def __init__(self, items, plugs=None):
        super(MultipleModulesSeller, self).__init__(plugs)
        self.__items = items

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=MULTIPLE_SELLING_TEMPLATE.format('success'), type=SM_TYPE.MultipleSelling, **self._getMsgCtx())

    def _getPrice(self):
        price = ITEM_PRICE_EMPTY
        for _, itemCD, count in self.__items:
            item = self.itemsCache.items.getItemByCD(itemCD)
            price = price + item.sellPrices.itemPrice * count

        return price

    def _getMsgCtx(self):
        return {'money': formatPrice(self._getPrice().price)}

    def _request(self, callback):
        BigWorld.player().inventory.sellMultiple(self.__items, lambda code: self._response(code, callback))


class ModuleInstallProcessor(ModuleProcessor, VehicleItemProcessor):

    def __init__(self, vehicle, item, itemType, slotIdx, install=True, conflictedEqs=None, plugs=tuple(), skipConfirm=False):
        opType = 'apply' if install else 'remove'
        conflictedEqs = conflictedEqs or tuple()
        ModuleProcessor.__init__(self, item=item, opType=opType, plugs=plugs)
        VehicleItemProcessor.__init__(self, vehicle=vehicle, module=item, allowableTypes=itemType)
        addPlugins = []
        if install:
            addPlugins += (plugins.CompatibilityInstallValidator(vehicle, item, slotIdx), plugins.MessageConfirmator('removeIncompatibleEqs', ctx={'name': "', '".join([ eq.userName for eq in conflictedEqs ]),
              'reason': _wrapHtmlMessage('incompatibleReason', backport.text(R.strings.dialogs.removeIncompatibleEqs.message.reason()))}, isEnabled=bool(conflictedEqs) and not skipConfirm))
        else:
            addPlugins += (plugins.CompatibilityRemoveValidator(vehicle, item),)
        self.install = install
        self.slotIdx = slotIdx
        self.addPlugins(addPlugins)

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType}

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=self._formMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())


class OptDeviceInstaller(ModuleInstallProcessor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehicle, item, slotIdx, install=True, allSetups=True, financeOperation=False, conflictedEqs=None, skipConfirm=False, showWaiting=True):
        super(OptDeviceInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.OPTIONALDEVICE,), slotIdx, install, conflictedEqs, skipConfirm=skipConfirm)
        self.removalPrice = item.getRemovalPrice(self.itemsCache.items)
        self.showWaiting = showWaiting
        addPlugins = []
        if install:
            addPlugins += (plugins.MessageConfirmator('installConfirmationNotRemovable_{}'.format(self.removalPrice.price.getCurrency()), ctx={'name': item.userName,
              'complex': _wrapHtmlMessage('confirmationNotRemovable', backport.text(R.strings.dialogs.confirmationNotRemovable.message.complex())),
              'destroy': _wrapHtmlMessage('confirmationNotRemovable', backport.text(R.strings.dialogs.confirmationNotRemovable.message.destroy()))}, isEnabled=not item.isRemovable and not skipConfirm),)
        else:
            addPlugins += (plugins.DemountDeviceConfirmator(isEnabled=not item.isRemovable and financeOperation and not skipConfirm, item=self.item, vehicle=vehicle), plugins.DestroyDeviceConfirmator(isEnabled=not item.isRemovable and not financeOperation and not skipConfirm, item=item))
        self.addPlugins(addPlugins)
        self.financeOperation = financeOperation
        self.allSetups = allSetups

    def _successHandler(self, code, ctx=None):
        item = self.item if self.install else None
        self.vehicle.optDevices.installed[self.slotIdx] = item
        useDemountKit = self.requestCtx.get('useDemountKit', False)
        if not self.install and not self.item.isRemovable and self.financeOperation:
            return OptDeviceRemoveProcessorMessage(self.item, removalPrice=self.removalPrice.price, useDemountKit=useDemountKit).makeSuccessMsg()
        else:
            return ItemDestroyProcessorMessage(self.item).makeSuccessMsg() if not self.install and not self.financeOperation and self.allSetups else super(OptDeviceInstaller, self)._successHandler(code, ctx)

    def _request(self, callback):
        if self.showWaiting:
            from gui.Scaleform.Waiting import Waiting
            Waiting.show('applyModule')
        useDemountKit = self.requestCtx.get('useDemountKit', False)
        if not self.install and useDemountKit:
            g_eventBus.handleEvent(ItemRemovalByDemountKitEvent(ItemRemovalByDemountKitEvent.DECLARED, self.slotIdx), EVENT_BUS_SCOPE.LOBBY)
        BigWorld.player().inventory.equipOptionalDevice(self.vehicle.invID, self.item.intCD, self.slotIdx, self.allSetups, self.financeOperation, lambda code, ext=None: self._response(code, callback, ctx=ext), useDemountKit, self.install)
        return

    def _response(self, code, callback, errStr='', ctx=None):
        super(OptDeviceInstaller, self)._response(code, callback, errStr=errStr, ctx=ctx)
        if self.showWaiting:
            from gui.Scaleform.Waiting import Waiting
            Waiting.hide('applyModule')

    def _errorHandler(self, code, errStr='', ctx=None):
        g_eventBus.handleEvent(ItemRemovalByDemountKitEvent(ItemRemovalByDemountKitEvent.CANCELED), EVENT_BUS_SCOPE.LOBBY)
        return OptDevicesDemountProcessorMessage().makeErrorMsg(errStr)


class EquipmentInstaller(ModuleInstallProcessor):

    def __init__(self, vehicle, item, slotIdx, install=True, conflictedEqs=None, skipConfirm=False):
        super(EquipmentInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.EQUIPMENT,), slotIdx, install, conflictedEqs, skipConfirm=skipConfirm)

    def _successHandler(self, code, ctx=None):
        item = self.item if self.install else None
        self.vehicle.consumables.installed[self.slotIdx] = item
        return super(EquipmentInstaller, self)._successHandler(code, ctx)

    def _request(self, callback):
        itemCD = self.item.intCD if self.install else 0
        newLayout = self.vehicle.consumables.getIntCDs()
        newLayout.extend(self.vehicle.battleBoosters.getIntCDs())
        newLayout[self.slotIdx] = itemCD
        BigWorld.player().inventory.equipEquipments(self.vehicle.invID, newLayout, lambda code: self._response(code, callback))


class CommonModuleInstallProcessor(ModuleProcessor, VehicleItemProcessor):

    def __init__(self, vehicle, item, itemType, install=True, conflictedEqs=None, plugs=tuple(), skipConfirm=False):
        opType = 'apply' if install else 'remove'
        conflictedEqs = conflictedEqs or tuple()
        ModuleProcessor.__init__(self, item=item, opType=opType, plugs=plugs)
        VehicleItemProcessor.__init__(self, vehicle=vehicle, module=item, allowableTypes=itemType)
        if install:
            self.addPlugin(plugins.MessageConfirmator('removeIncompatibleEqs', ctx={'name': "', '".join([ eq.userName for eq in conflictedEqs ]),
             'reason': _wrapHtmlMessage('incompatibleReason', backport.text(R.strings.dialogs.removeIncompatibleEqs.message.reason()))}, isEnabled=bool(conflictedEqs) and not skipConfirm))
        self.install = install

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType}

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        removedItems = []
        for eqKd in ctx.get('incompatibleEqs', []):
            item = self.itemsCache.items.getItemByCD(eqKd)
            removedItems.append(item.userName)

        if removedItems:
            additionalMessages.append(makeI18nSuccess(self._formMessage('incompatibleEqs'), items="', '".join(removedItems), type=SM_TYPE.Information))
        additionalMessages.append(makeI18nSuccess(sysMsgKey=self._formMessage('success'), type=SM_TYPE.Information, auxData=additionalMessages, **self._getMsgCtx()))
        equipSideEffects = ctx.get('equipSideEffects', [])
        if EquipSideEffect.AMMO_AUTO_LOADED in equipSideEffects:
            additionalMessages.append(makeI18nSuccess(sysMsgKey='charge/success', type=SM_TYPE.Information, auxData=additionalMessages))
        elif EquipSideEffect.AMMO_AUTO_LOAD_FAILED in equipSideEffects:
            additionalMessages.append(makeI18nSuccess(sysMsgKey='charge/inventory_error', vehicle=self.vehicle.userName, type=SM_TYPE.Warning, auxData=additionalMessages))
        return makeSuccess(auxData=additionalMessages)


class TurretInstaller(CommonModuleInstallProcessor):

    def __init__(self, vehicle, item, conflictedEqs=None, skipConfirm=False):
        super(TurretInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.TURRET,), True, conflictedEqs, skipConfirm=skipConfirm)
        self.gunCD = 0
        mayInstallCurrent = item.mayInstall(vehicle, gunCD=self.gunCD)
        if not mayInstallCurrent[0]:
            self._findAvailableGun(vehicle, item)
        self.addPlugin(plugins.TurretCompatibilityInstallValidator(vehicle, item, self.gunCD))

    def _skippedWarnings(self):
        return ['error_too_heavy']

    def _findAvailableGun(self, vehicle, item):
        for gun in item.descriptor.guns:
            gunItem = self.itemsCache.items.getItemByCD(gun.compactDescr)
            if gunItem.isInInventory:
                mayInstall = item.mayInstall(vehicle, slotIdx=0, gunCD=gun.compactDescr)
                if mayInstall[0]:
                    self.gunCD = gun.compactDescr
                    break

    def _request(self, callback):
        BigWorld.player().inventory.equipTurret(self.vehicle.invID, self.item.intCD, self.gunCD, lambda code, ext: self._response(code, callback, ctx=ext))

    def _successHandler(self, code, ctx=None):
        if self.gunCD:
            gun = self.itemsCache.items.getItemByCD(self.gunCD)
            return makeI18nSuccess(sysMsgKey=self._formMessage('success_gun_change'), type=SM_TYPE.Information, gun=gun.userName, **self._getMsgCtx())
        return super(TurretInstaller, self)._successHandler(code, ctx)


class PreviewVehicleTurretInstaller(TurretInstaller):

    def _findAvailableGun(self, vehicle, item):
        for gun in item.descriptor.guns:
            mayInstall = item.mayInstall(vehicle, slotIdx=0, gunCD=gun.compactDescr)
            if mayInstall[0]:
                self.gunCD = gun.compactDescr
                break

    def _request(self, callback):
        vehDescr = self.vehicle.descriptor
        vehDescr.installTurret(self.item.intCD, self.gunCD)
        self.vehicle.turret = VehicleTurret(vehDescr.turret.compactDescr, descriptor=vehDescr.turret)
        if self.gunCD:
            self.vehicle.descriptor.installComponent(self.gunCD)
            self.vehicle.gun = VehicleGun(self.gunCD, descriptor=self.vehicle.descriptor.gun)
        callback(makeSuccess())


class OtherModuleInstaller(CommonModuleInstallProcessor):

    def __init__(self, vehicle, item, conflictedEqs=None, skipConfirm=False):
        super(OtherModuleInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.CHASSIS,
         GUI_ITEM_TYPE.ENGINE,
         GUI_ITEM_TYPE.FUEL_TANK,
         GUI_ITEM_TYPE.RADIO,
         GUI_ITEM_TYPE.SHELL), True, conflictedEqs, skipConfirm=skipConfirm)
        self.addPlugin(plugins.CompatibilityInstallValidator(vehicle, item, 0))

    def _request(self, callback):
        _logger.debug('Request to equip module: %s, %s', self.vehicle, self.item)
        BigWorld.player().inventory.equip(self.vehicle.invID, self.item.intCD, lambda code, ext: self._response(code, callback, ctx=ext))


class GunModuleInstaller(CommonModuleInstallProcessor):

    def __init__(self, vehicle, item, conflictedEqs=None, skipConfirm=False):
        super(GunModuleInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.GUN,), True, conflictedEqs, skipConfirm=skipConfirm)
        self.addPlugin(plugins.CompatibilityInstallValidator(vehicle, item, 0))

    def _request(self, callback):
        BigWorld.player().inventory.equip(self.vehicle.invID, self.item.intCD, lambda code, ext: self._response(code, callback, ctx=ext))

    def _skippedWarnings(self):
        return ['error_need_turret', 'error_too_heavy']


def previewInstallModule(vehicle, item, moduleName, itemsFactory):
    vehicle.descriptor.installComponent(item.intCD)
    itemDescr = getattr(vehicle.descriptor, moduleName)
    module = itemsFactory.createGuiItem(item.itemTypeID, itemDescr.compactDescr, descriptor=itemDescr)
    setattr(vehicle, moduleName, module)


class PreviewVehicleModuleInstaller(OtherModuleInstaller):
    OTHER_PREVIEW_MODULES = {GUI_ITEM_TYPE.CHASSIS: 'chassis',
     GUI_ITEM_TYPE.ENGINE: 'engine',
     GUI_ITEM_TYPE.RADIO: 'radio'}
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def _request(self, callback):
        itemTypeID = self.item.itemTypeID
        moduleName = self.OTHER_PREVIEW_MODULES[itemTypeID]
        previewInstallModule(self.vehicle, self.item, moduleName, self.itemsFactory)
        callback(makeSuccess())


class PreviewVehicleGunInstaller(GunModuleInstaller):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def _request(self, callback):
        moduleName = 'gun'
        previewInstallModule(self.vehicle, self.item, moduleName, self.itemsFactory)
        callback(makeSuccess())


class BuyAndInstallItemProcessor(ModuleBuyer):
    lobbyContext = dependency.descriptor(ILobbyContext)
    _installConfirmatorPluginCls = _storeConfirmatorPluginCls = plugins.BuyAndInstallConfirmator

    def __init__(self, vehicle, item, slotIdx, gunCompDescr, conflictedEqs=None, skipConfirm=False):
        self.__vehInvID = vehicle.invID
        self.__slotIdx = int(slotIdx)
        self.__gunCompDescr = gunCompDescr
        self.__vehicle = vehicle
        self._installedModuleCD = vehicle.descriptor.getComponentsByType(item.itemTypeName)[0].compactDescr
        conflictedEqs = conflictedEqs or tuple()
        conflictMsg = ''
        if conflictedEqs:
            self.__makeConflictMsg("', '".join([ eq.userName for eq in conflictedEqs ]))
        self.__mayInstall, self._installReason = item.mayInstall(vehicle, slotIdx)
        super(BuyAndInstallItemProcessor, self).__init__(item, 1, Currency.CREDITS)
        self.addPlugins([plugins.ModuleValidator(item)])
        if self.__mayInstall:
            self.addPlugins([plugins.VehicleValidator(vehicle, True, prop={'isBroken': True,
              'isLocked': True}), plugins.CompatibilityInstallValidator(vehicle, item, slotIdx), self._installConfirmatorPluginCls('confirmBuyAndInstall', ctx=self._getItemConfirmationData(conflictMsg), isEnabled=not skipConfirm, item=self.item)])
            if item.itemTypeID == GUI_ITEM_TYPE.TURRET:
                self.addPlugin(plugins.TurretCompatibilityInstallValidator(vehicle, item, self.__gunCompDescr))
            self.addPlugin(plugins.MessageConfirmator('removeIncompatibleEqs', ctx={'name': "', '".join([ eq.userName for eq in conflictedEqs ]),
             'reason': _wrapHtmlMessage('incompatibleReason', backport.text(R.strings.dialogs.removeIncompatibleEqs.message.reason()))}, isEnabled=bool(conflictedEqs) and not skipConfirm))
        else:
            self.addPlugins([self._storeConfirmatorPluginCls('confirmBuyNotInstall', ctx=self._getItemConfirmationData(conflictMsg), isEnabled=not skipConfirm, item=item)])

    def _getItemConfirmationData(self, conflictMsg):
        return {'installedModuleCD': self._installedModuleCD,
         'currency': self._currency,
         'installReason': self._installReason}

    def __makeConflictMsg(self, conflictedText):
        attrs = {'conflicted': conflictedText}
        return makeHtmlString('html_templates:lobby/shop/system_messages', 'conflicted', attrs)

    def _successHandler(self, code, ctx=None):
        if self.__mayInstall:
            _logger.debug('code: %s, ctx: %s', code, ctx)
            if self.item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                auxData = [makeI18nSuccess(sysMsgKey=self._formApplyMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())]
            elif self.item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                auxData = [makeI18nSuccess(sysMsgKey=self._formApplyMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())]
            elif self.item.itemTypeID == GUI_ITEM_TYPE.TURRET:
                if self.__gunCompDescr:
                    gun = self.itemsCache.items.getItemByCD(self.__gunCompDescr)
                    auxData = [makeI18nSuccess(sysMsgKey=self._formApplyMessage('success_gun_change'), type=SM_TYPE.Information, gun=gun.userName, **self._getMsgCtx())]
                else:
                    auxData = self.__getAdditionalMessages(ctx)
            else:
                auxData = self.__getAdditionalMessages(ctx)
            return makeI18nSuccess(sysMsgKey=self._formMessage('success'), auxData=auxData, type=self._getSysMsgType(), **self._getMsgCtx())
        else:
            return super(BuyAndInstallItemProcessor, self)._successHandler(code, ctx)

    def __getAdditionalMessages(self, ctx):
        additionalMessages = []
        removedItems = []
        if ctx:
            for eqKd in ctx.get('incompatibleEqs', []):
                item = self.itemsCache.items.getItemByCD(eqKd)
                removedItems.append(item.name)

        if removedItems:
            additionalMessages.append(makeI18nSuccess(sysMsgKey=self._formApplyMessage('incompatibleEqs'), items="', '".join(removedItems), type=SM_TYPE.Information))
        additionalMessages.append(makeI18nSuccess(sysMsgKey=self._formApplyMessage('success'), type=SM_TYPE.Information, auxData=additionalMessages[:], **self._getMsgCtx()))
        return additionalMessages

    def _formApplyMessage(self, msg):
        return '{itemType}_{opType}/{msg}'.format(itemType=self.ITEMS_MSG_PREFIXES.get(self.item.itemTypeID, self.DEFAULT_PREFIX), opType='apply', msg=msg)

    def _request(self, callback):
        from gui.Scaleform.Waiting import Waiting
        Waiting.show('applyModule')
        if self.__mayInstall:
            _logger.debug('Make server request to buyAndInstallModule module: %s, %s, %s, %s, %s', self.__vehInvID, self.item.intCD, self.__slotIdx, self.__gunCompDescr, self._currency)
            BigWorld.player().shop.buyAndEquipItem(self.__vehInvID, self.item.intCD, self.__slotIdx, False, self.__gunCompDescr, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
        else:
            super(BuyAndInstallItemProcessor, self)._request(callback)

    def _response(self, code, callback, ctx=None, errStr=''):
        super(BuyAndInstallItemProcessor, self)._response(code, callback, errStr, ctx)
        from gui.Scaleform.Waiting import Waiting
        Waiting.hide('applyModule')


class BCBuyAndInstallItemProcessor(BuyAndInstallItemProcessor):
    _installConfirmatorPluginCls = _storeConfirmatorPluginCls = plugins.BCBuyAndInstallConfirmator

    def _getItemConfirmationData(self, conflictMsg):
        return {'price': self._getOpPrice().price.get(self._currency)}


class ModuleUpgradeProcessor(ModuleProcessor):

    def __init__(self, item, vehicle, setupIdx, slotIdx, validateMoney=True, plugs=tuple()):
        super(ModuleUpgradeProcessor, self).__init__(item, 'upgrade', plugs)
        addPlugins = []
        self.__upgradePrice = item.getUpgradePrice(self.itemsCache.items)
        if validateMoney:
            addPlugins += (plugins.MoneyValidator(self.__upgradePrice.price),)
        if vehicle is not None:
            addPlugins += (plugins.VehicleValidator(vehicle, True, prop={'isBroken': True,
              'isLocked': True}),)
        self.vehicle = vehicle
        self.slotIdx = slotIdx
        self.setupIdx = setupIdx
        self.addPlugins(addPlugins)
        return

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType,
         'money': formatPrice(self.__upgradePrice.price)}

    def _successHandler(self, code, ctx=None):
        msg = 'success/analogWasDemounted' if ctx and ctx.get('isAnalogWasDemounted', False) else 'success'
        currency = self.__upgradePrice.getCurrency(byWeight=True)
        smType = SM_TYPE.UpgradeForEquipCoins if currency == Currency.EQUIP_COIN else SM_TYPE.UpgradeForCredits
        return makeI18nSuccess(sysMsgKey=self._formMessage(msg), type=smType, **self._getMsgCtx())

    def _request(self, callback):
        if self.vehicle is not None and self.item.isInSetup(self.vehicle):
            _logger.debug('Request to upgrade module: %s, %s %s %s', self.item.intCD, self.vehicle.invID, self.setupIdx, self.slotIdx)
            BigWorld.player().inventory.upgradeOptDev(0, self.vehicle.invID, self.setupIdx, self.slotIdx, lambda code, ext={}: self._response(code, callback, ctx=ext))
        else:
            _logger.debug('Request to upgrade module: %s', self.item.intCD)
            BigWorld.player().inventory.upgradeOptDev(self.item.intCD, 0, 0, 0, lambda code, ext={}: self._response(code, callback, ctx=ext))
        return


class BattleAbilityInstaller(ModuleInstallProcessor):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, vehicle, item, slotIdx, install=True, conflictedEqs=None, skipConfirm=False):
        super(BattleAbilityInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.BATTLE_ABILITY,), slotIdx, install, conflictedEqs, skipConfirm=skipConfirm)

    def _request(self, callback):
        selectedSkill = next((skillID for skillID, levelInfo in self.__epicMetaGameCtrl.getAllUnlockedSkillInfoBySkillId().iteritems() if self.item.innationID == levelInfo.eqID), -1)
        currentSkills = self.__epicMetaGameCtrl.getSelectedSkills(self.vehicle.intCD)[:]
        previousSkill = currentSkills[self.slotIdx] if len(currentSkills) >= self.slotIdx else -1
        for idx, skillID in enumerate(currentSkills):
            if idx == self.slotIdx:
                if self.install:
                    currentSkills[idx] = selectedSkill
                else:
                    currentSkills[idx] = -1
            if skillID == selectedSkill and skillID != -1:
                currentSkills[idx] = previousSkill

        self.__epicMetaGameCtrl.changeEquippedSkills(currentSkills, self.vehicle.intCD, lambda code, _: self._response(code, callback))

    def _successHandler(self, code, ctx=None):
        return makeSuccess()


def getInstallerProcessor(vehicle, newComponentItem, slotIdx=0, install=True, isUseMoney=False, conflictedEqs=None, skipConfirm=False):
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
        return EquipmentInstaller(vehicle, newComponentItem, slotIdx, install, conflictedEqs, skipConfirm)
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        return OptDeviceInstaller(vehicle, newComponentItem, slotIdx, install, isUseMoney, conflictedEqs, skipConfirm)
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.TURRET:
        return TurretInstaller(vehicle, newComponentItem, conflictedEqs, skipConfirm)
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.BATTLE_ABILITY:
        return BattleAbilityInstaller(vehicle, newComponentItem, slotIdx, install, conflictedEqs, skipConfirm)
    return GunModuleInstaller(vehicle, newComponentItem, conflictedEqs, skipConfirm) if newComponentItem.itemTypeID == GUI_ITEM_TYPE.GUN else OtherModuleInstaller(vehicle, newComponentItem, conflictedEqs, skipConfirm)


def getPreviewInstallerProcessor(vehicle, newComponentItem, conflictedEqs=None):
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.TURRET:
        return PreviewVehicleTurretInstaller(vehicle, newComponentItem, conflictedEqs)
    return PreviewVehicleGunInstaller(vehicle, newComponentItem, conflictedEqs) if newComponentItem.itemTypeID == GUI_ITEM_TYPE.GUN else PreviewVehicleModuleInstaller(vehicle, newComponentItem, conflictedEqs)
