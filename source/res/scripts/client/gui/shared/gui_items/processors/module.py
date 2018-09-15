# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/module.py
import BigWorld
import AccountCommands
from gui import makeHtmlString
from gui.shared.gui_items.vehicle_modules import VehicleTurret, VehicleGun
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from debug_utils import LOG_DEBUG, LOG_UNEXPECTED
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE, CURRENCY_TO_SM_TYPE_DISMANTLING
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import getItemBuyPrice
from gui.shared.gui_items.processors import ItemProcessor, makeI18nSuccess, makeI18nError, VehicleItemProcessor, plugins, makeSuccess
from gui.shared.formatters import formatPrice, icons, getBWFormatter
from gui.shared.money import Money, Currency
from gui.shared.tooltips.formatters import packActionTooltipData
from helpers import i18n, dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory

def _getIconHtmlTagForCurrency(currency):
    getter = getattr(icons, currency)
    if getter:
        return getter()
    LOG_UNEXPECTED('Could not fetch an icon getter for the following currency', currency)


def _formatCurrencyValue(currency, value):
    formatter = getBWFormatter(currency)
    return formatter(value)


class ModuleProcessor(ItemProcessor):
    """
    Root module processor
    """
    ITEMS_MSG_PREFIXES = {GUI_ITEM_TYPE.SHELL: 'shell',
     GUI_ITEM_TYPE.EQUIPMENT: 'artefact',
     GUI_ITEM_TYPE.OPTIONALDEVICE: 'artefact',
     GUI_ITEM_TYPE.BATTLE_BOOSTER: 'battleBooster'}
    DEFAULT_PREFIX = 'module'

    def __init__(self, item, opType, plugs=tuple()):
        """
        Ctor.
        
        @param item: module to install
        @param opType: operation type
        @param plugs: plugins list
        """
        ItemProcessor.__init__(self, item, plugs + (plugins.ModuleValidator(item),))
        self.opType = opType

    def _getMsgCtx(self):
        raise NotImplemented

    def _formMessage(self, msg):
        LOG_DEBUG('Generating response for ModuleProcessor: ', self.opType, msg)
        return '%(itemType)s_%(opType)s/%(msg)s' % {'itemType': self.ITEMS_MSG_PREFIXES.get(self.item.itemTypeID, self.DEFAULT_PREFIX),
         'opType': self.opType,
         'msg': msg}

    def _errorHandler(self, code, errStr='', ctx=None):
        if not len(errStr):
            if code != AccountCommands.RES_CENTER_DISCONNECTED:
                msg = 'server_error'
            else:
                msg = 'server_error_centerDown'
        else:
            msg = errStr
        return makeI18nError(self._formMessage(msg), defaultSysMsgKey=self._formMessage('server_error'), **self._getMsgCtx())


class ModuleTradeProcessor(ModuleProcessor):
    """
    Root module trade
    """

    def __init__(self, item, count, opType, plugs=tuple()):
        """
        Ctor.
        
        @param item: module to install
        @param count: buying count
        @param opType: operation type
        @param plugs: plugins list
        """
        super(ModuleTradeProcessor, self).__init__(item, opType, plugs)
        self.count = count

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType,
         'count': BigWorld.wg_getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getOpPrice().price)}

    def _getOpPrice(self):
        """
        @return Returns an instance of ItemPrice
        """
        raise NotImplemented


class ModuleBuyer(ModuleTradeProcessor):
    """
    Module buyer
    """

    def __init__(self, item, count, currency):
        """
        Ctor.
        
        @param item: module to install
        @param count: buying count
        @param currency: currency to be used for buying
        """
        super(ModuleBuyer, self).__init__(item, count, 'buy')
        self._currency, self._itemPrice = self._getItemCurrencyAndPrice(currency)
        self.addPlugins((plugins.MoneyValidator(self._getOpPrice().price), plugins.ModuleConfigValidator(item)))

    def _getItemCurrencyAndPrice(self, currency):
        """
        Determines the item price and currency based on alternative and original coast. Note that by default
        the method tries to determine the coast in credits. If the item price is not defined in credits (or the item
        can not be bought for credits right now), the method returns the coast in the original currency.
        
        :param currency: the preferred currency, Currency.CREDITS by default, see class constructor.
        
        :return: an instance of tuple(currency, ItemPrice)
        """
        itemPrice = getItemBuyPrice(self.item, currency, self.itemsCache.items.shop)
        if itemPrice is None:
            itemPrice = self.item.buyPrices.itemPrice
            currency = itemPrice.getCurrency(byWeight=True)
        return (currency, itemPrice)

    def _getOpPrice(self):
        """
        Gets ItemPrice required to buy the specified amount of items.
        
        :return: an instance of ItemPrice
        """
        return self._itemPrice * self.count

    def _getSysMsgType(self):
        return CURRENCY_TO_SM_TYPE.get(self._currency, SM_TYPE.PurchaseForCredits)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=self._getSysMsgType(), **self._getMsgCtx())

    def _request(self, callback):
        LOG_DEBUG('Make server request to buy {} module(s) {} for currency {} (item price - {})'.format(self.count, self.item, self._currency, self._itemPrice))
        originalCurrency = self.item.buyPrices.itemPrice.getCurrency()
        goldForCredits = originalCurrency == Currency.GOLD and self._currency == Currency.CREDITS and getItemBuyPrice(self.item, self._currency, self.itemsCache.items.shop) is not None
        BigWorld.player().shop.buy(self.item.itemTypeID, self.item.nationID, self.item.intCD, self.count, int(goldForCredits), lambda code: self._response(code, callback))
        return


class ModuleSeller(ModuleTradeProcessor):
    """
    Module seller
    """

    def __init__(self, item, count):
        """
        Ctor.
        
        @param item: module to install
        @param count: module buying count
        """
        super(ModuleSeller, self).__init__(item, count, 'sell')

    def _getOpPrice(self):
        return self.item.sellPrices.itemPrice * self.count

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Selling, **self._getMsgCtx())

    def _request(self, callback):
        LOG_DEBUG('Make server request to sell item', self.item, self.count)
        BigWorld.player().inventory.sell(self.item.itemTypeID, self.item.intCD, self.count, lambda code: self._response(code, callback))


class ModuleInstallProcessor(ModuleProcessor, VehicleItemProcessor):
    """
    Root modules installer.
    """

    def __init__(self, vehicle, item, itemType, slotIdx, install=True, conflictedEqs=None, plugs=tuple(), skipConfirm=False):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param item: module to install
        @param slotIdx: vehicle equipment slot index to install
        @param itemType: item type
        @param install: flag to designated process
        @param conflictedEqs: conflicted items
        @param plugs: plugins list
        """
        opType = 'apply' if install else 'remove'
        conflictedEqs = conflictedEqs or tuple()
        ModuleProcessor.__init__(self, item=item, opType=opType, plugs=plugs)
        VehicleItemProcessor.__init__(self, vehicle=vehicle, module=item, allowableTypes=itemType)
        addPlugins = []
        if install:
            addPlugins += (plugins.CompatibilityInstallValidator(vehicle, item, slotIdx), plugins.MessageConfirmator('removeIncompatibleEqs', ctx={'name': "', '".join([ eq.userName for eq in conflictedEqs ])}, isEnabled=bool(conflictedEqs) and not skipConfirm))
        else:
            addPlugins += (plugins.CompatibilityRemoveValidator(vehicle, item),)
        self.install = install
        self.slotIdx = slotIdx
        self.addPlugins(addPlugins)

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType}

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())


class OptDeviceInstaller(ModuleInstallProcessor):
    """
    Vehicle opt devices installer.
    """

    def __init__(self, vehicle, item, slotIdx, install=True, isUseMoney=False, conflictedEqs=None, skipConfirm=False):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param item: module to install
        @param slotIdx: vehicle equipment slot index to install
        @param install: true if device is being installed, false if being demounted
        @param isUseMoney: if False - it means the user selected 'destroy' device, otherwise - de-install for money
        @param conflictedEqs: conflicted items
        """
        super(OptDeviceInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.OPTIONALDEVICE,), slotIdx, install, conflictedEqs, skipConfirm=skipConfirm)
        self.removalPrice = item.getRemovalPrice(self.itemsCache.items)
        action = None
        if self.removalPrice.isActionPrice():
            action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'paidRemovalCost', True, self.removalPrice.price, self.removalPrice.defPrice)
        addPlugins = []
        if install:
            addPlugins += (plugins.MessageConfirmator('installConfirmationNotRemovable', ctx={'name': item.userName}, isEnabled=not item.isRemovable and not skipConfirm),)
        else:
            addPlugins += (plugins.DemountDeviceConfirmator('removeConfirmationNotRemovableMoney', ctx={'name': item.userName,
              'price': self.removalPrice,
              'action': action,
              'item': item}, isEnabled=not item.isRemovable and isUseMoney and not skipConfirm), plugins.DestroyDeviceConfirmator('removeConfirmationNotRemovable', itemName=item.userName, isEnabled=not item.isRemovable and not isUseMoney and not skipConfirm))
        self.addPlugins(addPlugins)
        self.useMoney = isUseMoney
        return

    def _successHandler(self, code, ctx=None):
        item = self.item if self.install else None
        self.vehicle.optDevices[self.slotIdx] = item
        smType = CURRENCY_TO_SM_TYPE_DISMANTLING.get(self.removalPrice.price.getCurrency(), SM_TYPE.DismantlingForGold)
        return makeI18nSuccess(self._formMessage('money_success'), type=smType, **self._getMsgCtx()) if not self.install and not self.item.isRemovable and self.useMoney else super(OptDeviceInstaller, self)._successHandler(code, ctx)

    def _request(self, callback):
        itemCD = self.item.intCD if self.install else 0
        BigWorld.player().inventory.equipOptionalDevice(self.vehicle.invID, itemCD, self.slotIdx, self.useMoney, lambda code: self._response(code, callback))

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType,
         'money': formatPrice(self.removalPrice.price)}


class EquipmentInstaller(ModuleInstallProcessor):
    """
    Vehicle equipment installer.
    """

    def __init__(self, vehicle, item, slotIdx, install=True, conflictedEqs=None, skipConfirm=False):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param item: equipment to install
        @param slotIdx: vehicle equipment slot index to install
        @param install: flag to designated process
        @param conflictedEqs: conflicted items
        """
        super(EquipmentInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.EQUIPMENT,), slotIdx, install, conflictedEqs, skipConfirm=skipConfirm)

    def _successHandler(self, code, ctx=None):
        item = self.item if self.install else None
        self.vehicle.equipment.regularConsumables[self.slotIdx] = item
        return super(EquipmentInstaller, self)._successHandler(code, ctx)

    def _request(self, callback):
        itemCD = self.item.intCD if self.install else 0
        newLayout = self.vehicle.equipment.getConsumablesIntCDs()
        newLayout[self.slotIdx] = itemCD
        BigWorld.player().inventory.equipEquipments(self.vehicle.invID, newLayout, lambda code: self._response(code, callback))


class CommonModuleInstallProcessor(ModuleProcessor, VehicleItemProcessor):
    """
    Vehicle other modules installer.
    """

    def __init__(self, vehicle, item, itemType, install=True, conflictedEqs=None, plugs=tuple(), skipConfirm=False):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param item: equipment to install
        @param itemType: vehicle module type
        @param install: flag to designated process
        @param conflictedEqs: conflicted items
        @param plugs: plugins list
        """
        opType = 'apply' if install else 'remove'
        conflictedEqs = conflictedEqs or tuple()
        ModuleProcessor.__init__(self, item=item, opType=opType, plugs=plugs)
        VehicleItemProcessor.__init__(self, vehicle=vehicle, module=item, allowableTypes=itemType)
        if install:
            self.addPlugin(plugins.MessageConfirmator('removeIncompatibleEqs', ctx={'name': "', '".join([ eq.userName for eq in conflictedEqs ])}, isEnabled=bool(conflictedEqs) and not skipConfirm))
        self.install = install

    def _getMsgCtx(self):
        return {'name': self.item.userName,
         'kind': self.item.userType}

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        removedItems = []
        for eqKd in ctx.get('incompatibleEqs', []):
            item = self.itemsCache.items.getItemByCD(eqKd)
            removedItems.append(item.name)

        if removedItems:
            additionalMessages.append(makeI18nSuccess(self._formMessage('incompatibleEqs'), items="', '".join(removedItems), type=SM_TYPE.Information))
        additionalMessages.append(makeI18nSuccess(self._formMessage('success'), type=SM_TYPE.Information, auxData=additionalMessages, **self._getMsgCtx()))
        return makeSuccess(auxData=additionalMessages)


class TurretInstaller(CommonModuleInstallProcessor):
    """
    Vehicle turret installer.
    """

    def __init__(self, vehicle, item, conflictedEqs=None, skipConfirm=False):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param item: equipment to install
        @param conflictedEqs: conflicted items
        """
        super(TurretInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.TURRET,), True, conflictedEqs, skipConfirm=skipConfirm)
        self.gunCD = 0
        mayInstallCurrent = item.mayInstall(vehicle, gunCD=self.gunCD)
        if not mayInstallCurrent[0]:
            self._findAvailableGun(vehicle, item)
        self.addPlugin(plugins.TurretCompatibilityInstallValidator(vehicle, item, self.gunCD))

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
            return makeI18nSuccess(self._formMessage('success_gun_change'), type=SM_TYPE.Information, gun=gun.userName, **self._getMsgCtx())
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
    """
    Vehicle rest modules installer: sheels, fuel tanks, etc.
    """

    def __init__(self, vehicle, item, conflictedEqs=None, skipConfirm=False):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param item: equipment to install
        @param conflictedEqs: conflicted items
        """
        super(OtherModuleInstaller, self).__init__(vehicle, item, (GUI_ITEM_TYPE.CHASSIS,
         GUI_ITEM_TYPE.GUN,
         GUI_ITEM_TYPE.ENGINE,
         GUI_ITEM_TYPE.FUEL_TANK,
         GUI_ITEM_TYPE.RADIO,
         GUI_ITEM_TYPE.SHELL), True, conflictedEqs, skipConfirm=skipConfirm)
        self.addPlugin(plugins.CompatibilityInstallValidator(vehicle, item, 0))

    def _request(self, callback):
        LOG_DEBUG('Request to equip module', self.vehicle, self.item)
        BigWorld.player().inventory.equip(self.vehicle.invID, self.item.intCD, lambda code, ext: self._response(code, callback, ctx=ext))


class PreviewVehicleModuleInstaller(OtherModuleInstaller):
    OTHER_PREVIEW_MODULES = {GUI_ITEM_TYPE.GUN: 'gun',
     GUI_ITEM_TYPE.CHASSIS: 'chassis',
     GUI_ITEM_TYPE.ENGINE: 'engine',
     GUI_ITEM_TYPE.RADIO: 'radio'}
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def _request(self, callback):
        itemTypeID = self.item.itemTypeID
        moduleName = self.OTHER_PREVIEW_MODULES[itemTypeID]
        self.vehicle.descriptor.installComponent(self.item.intCD)
        itemDescr = getattr(self.vehicle.descriptor, moduleName)
        module = self.itemsFactory.createGuiItem(itemTypeID, itemDescr.compactDescr, descriptor=itemDescr)
        setattr(self.vehicle, moduleName, module)
        callback(makeSuccess())


class BuyAndInstallItemProcessor(ModuleBuyer):

    def __init__(self, vehicle, item, slotIdx, gunCompDescr, conflictedEqs=None, skipConfirm=False):
        self.__vehInvID = vehicle.invID
        self.__slotIdx = int(slotIdx)
        self.__gunCompDescr = gunCompDescr
        self.__vehicle = vehicle
        conflictedEqs = conflictedEqs or tuple()
        conflictMsg = ''
        if conflictedEqs:
            self.__makeConflictMsg("', '".join([ eq.userName for eq in conflictedEqs ]))
        self.__mayInstall, installReason = item.mayInstall(vehicle, slotIdx)
        super(BuyAndInstallItemProcessor, self).__init__(item, 1, Currency.CREDITS)
        self.addPlugins([plugins.ModuleValidator(item)])
        if self.__mayInstall:
            self.addPlugins([plugins.VehicleValidator(vehicle, True, prop={'isBroken': True,
              'isLocked': True}), plugins.CompatibilityInstallValidator(vehicle, item, slotIdx), plugins.ModuleBuyerConfirmator('confirmBuyAndInstall', ctx={'userString': item.userName,
              'typeString': self.item.userType,
              'conflictedEqs': conflictMsg,
              'currencyIcon': _getIconHtmlTagForCurrency(self._currency),
              'value': _formatCurrencyValue(self._currency, self._getOpPrice().price.get(self._currency))}, isEnabled=not skipConfirm)])
            if item.itemTypeID == GUI_ITEM_TYPE.TURRET:
                self.addPlugin(plugins.TurretCompatibilityInstallValidator(vehicle, item, self.__gunCompDescr))
            elif item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                self.addPlugin(plugins.MessageConfirmator('installConfirmationNotRemovable', ctx={'name': item.userName}, isEnabled=not item.isRemovable and not skipConfirm))
            self.addPlugin(plugins.MessageConfirmator('removeIncompatibleEqs', ctx={'name': "', '".join([ eq.userName for eq in conflictedEqs ])}, isEnabled=bool(conflictedEqs) and not skipConfirm))
        else:
            self.addPlugins([plugins.ModuleBuyerConfirmator('confirmBuyNotInstall', ctx={'userString': item.userName,
              'typeString': self.item.userType,
              'currencyIcon': _getIconHtmlTagForCurrency(self._currency),
              'value': _formatCurrencyValue(self._currency, self._getOpPrice().price.get(self._currency)),
              'reason': self.__makeInstallReasonMsg(installReason)}, isEnabled=not skipConfirm)])

    def __makeConflictMsg(self, conflictedText):
        attrs = {'conflicted': conflictedText}
        return makeHtmlString('html_templates:lobby/shop/system_messages', 'conflicted', attrs)

    def __makeInstallReasonMsg(self, installReason):
        reasonTxt = ''
        if installReason is not None:
            reasonTxt = '#menu:moduleFits/' + installReason.replace(' ', '_')
        return i18n.makeString(reasonTxt)

    def _successHandler(self, code, ctx=None):
        if self.__mayInstall:
            LOG_DEBUG('code, ctx', code, ctx)
            if self.item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
                auxData = [makeI18nSuccess(self._formApplyMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())]
            elif self.item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                auxData = [makeI18nSuccess(self._formApplyMessage('success'), type=SM_TYPE.Information, **self._getMsgCtx())]
            elif self.item.itemTypeID == GUI_ITEM_TYPE.TURRET:
                if self.__gunCompDescr:
                    gun = self.itemsCache.items.getItemByCD(self.__gunCompDescr)
                    auxData = [makeI18nSuccess(self._formApplyMessage('success_gun_change'), type=SM_TYPE.Information, gun=gun.userName, **self._getMsgCtx())]
                else:
                    auxData = self.__getAdditionalMessages(ctx)
            else:
                auxData = self.__getAdditionalMessages(ctx)
            return makeI18nSuccess(self._formMessage('success'), auxData=auxData, type=self._getSysMsgType(), **self._getMsgCtx())
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
            additionalMessages.append(makeI18nSuccess(self._formApplyMessage('incompatibleEqs'), items="', '".join(removedItems), type=SM_TYPE.Information))
        additionalMessages.append(makeI18nSuccess(self._formApplyMessage('success'), type=SM_TYPE.Information, auxData=additionalMessages, **self._getMsgCtx()))
        return additionalMessages

    def _formApplyMessage(self, msg):
        return '%(itemType)s_%(opType)s/%(msg)s' % {'itemType': self.ITEMS_MSG_PREFIXES.get(self.item.itemTypeID, self.DEFAULT_PREFIX),
         'opType': 'apply',
         'msg': msg}

    def _request(self, callback):
        if self.__mayInstall:
            LOG_DEBUG('Make server request to buyAndInstallModule module', self.__vehInvID, self.item.intCD, self.__slotIdx, self.__gunCompDescr, self._currency)
            BigWorld.player().shop.buyAndEquipItem(self.__vehInvID, self.item.intCD, self.__slotIdx, False, self.__gunCompDescr, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
        else:
            super(BuyAndInstallItemProcessor, self)._request(callback)


def getInstallerProcessor(vehicle, newComponentItem, slotIdx=0, install=True, isUseMoney=False, conflictedEqs=None, skipConfirm=False):
    """
    Select proper installer by type
    """
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
        return EquipmentInstaller(vehicle, newComponentItem, slotIdx, install, conflictedEqs, skipConfirm)
    elif newComponentItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
        return OptDeviceInstaller(vehicle, newComponentItem, slotIdx, install, isUseMoney, conflictedEqs, skipConfirm)
    elif newComponentItem.itemTypeID == GUI_ITEM_TYPE.TURRET:
        return TurretInstaller(vehicle, newComponentItem, conflictedEqs, skipConfirm)
    else:
        return OtherModuleInstaller(vehicle, newComponentItem, conflictedEqs, skipConfirm)


def getPreviewInstallerProcessor(vehicle, newComponentItem, conflictedEqs=None):
    if newComponentItem.itemTypeID == GUI_ITEM_TYPE.TURRET:
        return PreviewVehicleTurretInstaller(vehicle, newComponentItem, conflictedEqs)
    else:
        return PreviewVehicleModuleInstaller(vehicle, newComponentItem, conflictedEqs)
