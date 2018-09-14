# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/vehicle.py
import AccountCommands
import BigWorld
from AccountCommands import VEHICLE_SETTINGS_FLAG
from account_shared import LayoutIterator
from adisp import process, async
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared import g_itemsCache
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles, icons
from gui.shared.formatters.time_formatters import formatTime, getTimeLeftInfo
from gui.shared.gui_items.processors import ItemProcessor, Processor, makeI18nSuccess, makeI18nError, plugins, makeSuccess
from gui.shared.money import Money, ZERO_MONEY, Currency
from helpers import time_utils, dependency
from helpers.i18n import makeString
from shared_utils import findFirst
from skeletons.gui.game_control import IRestoreController

def getCrewAndShellsSumPrice(result, vehicle, crewType, buyShells):
    if crewType != -1:
        tankmenCount = len(vehicle.crew)
        tankmanCost = g_itemsCache.items.shop.tankmanCostWithGoodyDiscount[crewType]
        result += Money(tankmanCost['credits'] * tankmenCount, tankmanCost['gold'] * tankmenCount)
    if buyShells:
        for shell in vehicle.gun.defaultAmmo:
            result += shell.buyPrice * shell.defaultCount

    return result


class VehicleReceiveProcessor(ItemProcessor):
    """
    Base processor to receive Vehicle
    """

    def __init__(self, vehicle, buyShell=False, crewType=-1):
        """
        :param vehicle:  <Vehicle>
        :param buyShell: <bool> flag if need to buy shells
        :param crewType: <int> int flag, mean crew skill type
        """
        self.item = vehicle
        self.buyShell = buyShell
        self.buyCrew = crewType != -1
        self.crewType = crewType
        self.price = self._getPrice()
        super(VehicleReceiveProcessor, self).__init__(vehicle, self._getPluginsList())

    def _getPluginsList(self):
        """
        Gets plugins collection
        :return: <tuple(ProcessorPlugin, ...)>
        """
        raise NotImplementedError

    def _getPrice(self):
        """
        Gets item price for operation
        :return: <Money>
        """
        raise NotImplementedError

    def _getSysMsgType(self):
        """
        :return: <str> system message type
        """
        raise NotImplementedError


class VehicleBuyer(VehicleReceiveProcessor):

    def __init__(self, vehicle, buySlot, buyShell=False, crewType=-1):
        """
        Processor for vehicle buying
        :param vehicle: <Vehicle>
        :param buySlot: <bool> flag if need to buy slot
        :param buyShell: <bool> flag if need to buy shells
        :param crewType: <int> int flag, mean crew skill type
        """
        self.buySlot = buySlot
        super(VehicleBuyer, self).__init__(vehicle, buyShell=buyShell, crewType=crewType)

    def _getPluginsList(self):
        """
        Gets plugins collection
        :return: <tuple(ProcessorPlugin, ...)>
        """
        return (plugins.MoneyValidator(self.price), plugins.VehicleSlotsConfirmator(not self.buySlot), plugins.VehicleFreeLimitConfirmator(self.item, self.crewType))

    def _getPrice(self):
        """
        Gets common buy price with shells, slot, crew
        :return: <Money>
        """
        return getCrewAndShellsSumPrice(self.item.buyPrice, self.item, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr='', ctx=None):
        """
        :param code: <int> server response code
        :param errStr: <str> string error reason
        :param ctx: <obj> localization context
        :return: <ResultMsg> error message
        """
        if not errStr:
            msg = 'vehicle_buy/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_buy/server_error_centerDown'
        else:
            msg = 'vehicle_buy/%s' % errStr
        return makeI18nError(msg, defaultSysMsgKey='vehicle_buy/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        """
        :param code: <int> server response code
        :param ctx: <obj> localization context
        :return: <ResultMsg> success message
        """
        return makeI18nSuccess('vehicle_buy/success', vehName=self.item.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getSysMsgType(self):
        """
        :return: <str> system message type
        """
        return CURRENCY_TO_SM_TYPE.get(self.item.buyPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def _request(self, callback):
        """
        Sends buy vehicle request to server
        :param callback: <function>
        """
        LOG_DEBUG('Make request to buy vehicle', self.item, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, -1, lambda code: self._response(code, callback))


class VehicleRenter(VehicleReceiveProcessor):

    def __init__(self, vehicle, rentPackage, buyShell=False, crewType=-1):
        """
        Vehicle rent processor
        :param vehicle: <Vehicle>
        :param rentPackage: <int> rent period
        :param buyShell: <bool> flag if need to buy shells
        :param crewType: <int> int flag, mean crew skill type
        """
        self.rentPackage = rentPackage
        self.rentPrice = self.__getRentPrice(rentPackage, vehicle)
        super(VehicleRenter, self).__init__(vehicle, buyShell, crewType)

    def _getPluginsList(self):
        """
        Gets plugins collection
        :return: <tuple(ProcessorPlugin, ...)>
        """
        return (plugins.MoneyValidator(self.price), plugins.VehicleFreeLimitConfirmator(self.item, self.crewType))

    def _getPrice(self):
        """
        Gets common rent price with shells, slot, crew
        :return: <Money>
        """
        return getCrewAndShellsSumPrice(self.rentPrice, self.item, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr='', ctx=None):
        """
        :param code: <int> server response code
        :param errStr: <str> string error reason
        :param ctx: <obj> localization context
        :return: <ResultMsg> error message
        """
        if not len(errStr):
            msg = 'vehicle_rent/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_rent/server_error_centerDown'
        else:
            msg = 'vehicle_rent/%s' % errStr
        return makeI18nError(msg, defaultSysMsgKey='vehicle_rent/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        """
        :param code: <int> server response code
        :param ctx: <obj> localization context
        :return: <ResultMsg> success message
        """
        return makeI18nSuccess('vehicle_rent/success', vehName=self.item.userName, days=ctx.get('days', 0), price=formatPrice(self.price), type=self._getSysMsgType())

    def _request(self, callback):
        """
        Sends rent vehicle request to server
        :param callback: <function>
        """
        LOG_DEBUG('Make request to rent vehicle', self.item, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, self.rentPackage, lambda code: self._response(code, callback, ctx={'days': self.rentPackage}))

    def _getSysMsgType(self):
        """
        :return: <str> system message type
        """
        return CURRENCY_TO_SM_TYPE.get(self.rentPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def __getRentPrice(self, rentPackage, vehicle):
        """
        :param rentPackage: <int> rent period
        :param vehicle: <Vehicle>
        :return: <Money> rent package price
        """
        for package in vehicle.rentPackages:
            if package['days'] == rentPackage:
                return Money(*package['rentPrice'])

        return ZERO_MONEY


class VehicleRestoreProcessor(VehicleBuyer):

    def _getPrice(self):
        """
        Gets common restore price with shells, slot, crew
        :return: <Money>
        """
        return getCrewAndShellsSumPrice(self.item.restorePrice, self.item, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr='', ctx=None):
        """
        :param code: <int> server response code
        :param errStr: <str> string error reason
        :param ctx: <obj> localization context
        :return: <ResultMsg> error message
        """
        if not len(errStr):
            msg = 'vehicle_restore/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_restore/server_error_centerDown'
        else:
            msg = 'vehicle_restore/%s' % errStr
        return makeI18nError(msg, defaultSysMsgKey='vehicle_restore/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        """
        :param code: <int> server response code
        :param ctx: <obj> localization context
        :return: <ResultMsg> success message
        """
        return makeI18nSuccess('vehicle_restore/success', vehName=self.item.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getSysMsgType(self):
        """
        :return: <str> system message type
        """
        return SM_TYPE.Restore

    def _getPluginsList(self):
        return (plugins.MoneyValidator(self.price), plugins.VehicleSlotsConfirmator(not self.buySlot), plugins.IsLongDisconnectedFromCenter())

    def _request(self, callback):
        """
        Sends restore vehicle request to server
        :param callback: <function>
        """
        LOG_DEBUG('Make request to restore vehicle', self.item, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, -1, lambda code: self._response(code, callback))


class VehicleTradeInProcessor(VehicleBuyer):

    def __init__(self, vehicleToBuy, vehicleToTradeOff, buySlot, buyShell=False, crewType=-1):
        """
        Processor for vehicle buying
        :param vehicle: <Vehicle>
        :param vehicleToTradeOff: <Vehicle>
        :param buySlot: <bool> flag if need to buy slot
        :param buyShell: <bool> flag if need to buy shells
        :param crewType: <int> int flag, mean crew skill type
        """
        self.itemToTradeOff = vehicleToTradeOff
        super(VehicleTradeInProcessor, self).__init__(vehicleToBuy, buySlot, buyShell=buyShell, crewType=crewType)

    def _getPluginsList(self):
        """
        Gets plugins collection
        :return: <tuple(ProcessorPlugin, ...)>
        """
        barracksBerthsNeeded = len(filter(lambda (idx, item): item is not None, self.itemToTradeOff.crew))
        return (plugins.VehicleValidator(self.itemToTradeOff, setAll=True),
         plugins.VehicleTradeInValidator(self.item, self.itemToTradeOff),
         plugins.VehicleSellValidator(self.itemToTradeOff),
         plugins.MoneyValidator(self.price),
         plugins.BarracksSlotsValidator(barracksBerthsNeeded))

    def _getPrice(self):
        """
        Gets common buy price with shells, slot, crew
        :return: <Money>
        """
        return super(VehicleTradeInProcessor, self)._getPrice() - self.itemToTradeOff.tradeOffPrice

    def _errorHandler(self, code, errStr='', ctx=None):
        """
        :param code: <int> server response code
        :param errStr: <str> string error reason
        :param ctx: <obj> localization context
        :return: <ResultMsg> error message
        """
        if not errStr:
            msg = 'vehicle_trade_in/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_trade_in/server_error_centerDown'
        else:
            msg = 'vehicle_trade_in/%s' % errStr
        return makeI18nError(msg, vehName=self.item.userName, defaultSysMsgKey='vehicle_trade_in/server_error', tradeOffVehName=self.itemToTradeOff.userName)

    def _successHandler(self, code, ctx=None):
        """
        :param code: <int> server response code
        :param ctx: <obj> localization context
        :return: <ResultMsg> success message
        """
        return makeI18nSuccess('vehicle_trade_in/success', vehName=self.item.userName, tradeOffVehName=self.itemToTradeOff.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getSysMsgType(self):
        """
        :return: <str> system message type
        """
        return CURRENCY_TO_SM_TYPE.get(self.item.buyPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def _request(self, callback):
        """
        Sends trade-in vehicle request to server
        :param callback: <function>
        """
        LOG_DEBUG('Make request to trade-in vehicle', self.item, self.itemToTradeOff, self.buyShell, self.buyCrew, self.crewType, self.price)
        BigWorld.player().shop.tradeInVehicle(self.itemToTradeOff.invID, self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, lambda code: self._response(code, callback))


class VehicleSlotBuyer(Processor):

    def __init__(self, showConfirm=True, showWarning=True):
        self.__hasDiscounts = bool(g_itemsCache.items.shop.personalSlotDiscounts)
        self.__frozenSlotPrice = None
        slotCost = self.__getSlotPrice()
        if self.__hasDiscounts and not slotCost:
            confirmationType = 'freeSlotConfirmation'
            ctx = {}
        else:
            confirmationType = 'buySlotConfirmation'
            ctx = {'goldCost': text_styles.concatStylesWithSpace(text_styles.gold(str(slotCost.gold)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))}
        super(VehicleSlotBuyer, self).__init__((plugins.MessageInformator('buySlotNotEnoughCredits', activeHandler=lambda : not plugins.MoneyValidator(slotCost).validate().success, isEnabled=showWarning), plugins.MessageConfirmator(confirmationType, isEnabled=showConfirm, ctx=ctx), plugins.MoneyValidator(slotCost)))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('vehicle_slot_buy/%s' % errStr, defaultSysMsgKey='vehicle_slot_buy/server_error')

    def _successHandler(self, code, ctx=None):
        price = self.__getSlotPrice()
        if price == ZERO_MONEY:
            money = formatGoldPrice(price.gold)
        else:
            money = formatPrice(price)
        return makeI18nSuccess('vehicle_slot_buy/success', money=money, type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        LOG_DEBUG('Attempt to request server for buying vehicle slot')
        BigWorld.player().stats.buySlot(lambda code: self._response(code, callback))

    def __getSlotPrice(self):
        if self.__frozenSlotPrice is not None:
            return self.__frozenSlotPrice
        else:
            price = g_itemsCache.items.shop.getVehicleSlotsPrice(g_itemsCache.items.stats.vehicleSlots)
            if self.__hasDiscounts:
                self.__frozenSlotPrice = Money(gold=price)
            return Money(gold=price)


class VehicleSeller(ItemProcessor):
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, vehicle, dismantlingGoldCost, shells=[], eqs=[], optDevs=[], inventory=[], isCrewDismiss=False):
        self.gainMoney, self.spendMoney = self.__getGainSpendMoney(vehicle, shells, eqs, optDevs, inventory, dismantlingGoldCost)
        barracksBerthsNeeded = len(filter(lambda (idx, item): item is not None, vehicle.crew))
        bufferOverflowCtx = {}
        isBufferOverflowed = False
        if isCrewDismiss:
            tankmenGoingToBuffer, deletedTankmen = self.restore.getTankmenDeletedBySelling(vehicle)
            countOfDeleted = len(deletedTankmen)
            if countOfDeleted > 0:
                isBufferOverflowed = True
                bufferOverflowCtx['deleted'] = deletedTankmen[-1]
                bufferOverflowCtx['dismissed'] = tankmenGoingToBuffer[-1]
                if countOfDeleted > 1:
                    bufferOverflowCtx['multiple'] = True
                    bufferOverflowCtx['extraCount'] = countOfDeleted - 1
        super(VehicleSeller, self).__init__(vehicle, (plugins.VehicleValidator(vehicle, False, prop={'isBroken': True,
          'isLocked': True}),
         plugins.VehicleSellValidator(vehicle),
         plugins.MoneyValidator(self.spendMoney),
         plugins.VehicleSellsLeftValidator(vehicle, not (vehicle.isRented and vehicle.rentalIsOver)),
         plugins.BarracksSlotsValidator(barracksBerthsNeeded, isEnabled=not isCrewDismiss),
         plugins.BufferOverflowConfirmator(bufferOverflowCtx, isEnabled=isBufferOverflowed),
         _getUniqueVehicleSellConfirmator(vehicle)))
        self.vehicle = vehicle
        self.shells = shells
        self.eqs = eqs
        self.optDevs = optDevs
        self.inventory = inventory
        self.isCrewDismiss = isCrewDismiss
        self.isDismantlingForGold = self.__dismantlingForGoldDevicesCount(vehicle, optDevs) > 0
        self.isRemovedAfterRent = vehicle.isRented

    def _errorHandler(self, code, errStr='', ctx=None):
        localKey = 'vehicle_sell/%s'
        defaultKey = 'vehicle_sell/server_error'
        if self.isRemovedAfterRent:
            localKey = 'vehicle_remove/%s'
            defaultKey = 'vehicle_remove/server_error'
        return makeI18nError(localKey % errStr, defaultSysMsgKey=defaultKey, vehName=self.vehicle.userName)

    def _successHandler(self, code, ctx=None):
        restoreInfo = ''
        if self.vehicle.isPremium and not self.vehicle.isUnique and not self.vehicle.isUnrecoverable and g_lobbyContext.getServerSettings().isVehicleRestoreEnabled() and not self.vehicle.sellForGold:
            timeKey, formattedTime = getTimeLeftInfo(g_itemsCache.items.shop.vehiclesRestoreConfig.restoreDuration)
            restoreInfo = makeString('#system_messages:vehicle/restoreDuration/%s' % timeKey, time=formattedTime)
        if self.isDismantlingForGold:
            localKey = 'vehicle_sell/success_dismantling'
            smType = SM_TYPE.Selling
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/success_dismantling'
                smType = SM_TYPE.Remove
            return makeI18nSuccess(localKey, vehName=self.vehicle.userName, gainMoney=formatPrice(self.gainMoney), spendMoney=formatPrice(self.spendMoney), restoreInfo=restoreInfo, type=smType)
        else:
            localKey = 'vehicle_sell/success'
            smType = SM_TYPE.Selling
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/success'
                smType = SM_TYPE.Remove
            return makeI18nSuccess(localKey, vehName=self.vehicle.userName, money=formatPrice(self.gainMoney), restoreInfo=restoreInfo, type=smType)

    def _request(self, callback):
        itemsFromVehicle = list()
        itemsFromInventory = list()
        isSellShells = len(self.shells) > 0
        for shell in self.shells:
            itemsFromVehicle.append(shell.intCD)

        isSellEqs = len(self.eqs) > 0
        for eq in self.eqs:
            itemsFromVehicle.append(eq.intCD)

        isSellFromInv = len(self.inventory) > 0
        for module in self.inventory:
            itemsFromInventory.append(module.intCD)

        isSellOptDevs = len(self.optDevs) > 0
        for dev in self.optDevs:
            itemsFromVehicle.append(dev.intCD)

        LOG_DEBUG('Make server request:', self.vehicle.invID, isSellShells, isSellEqs, isSellFromInv, isSellOptDevs, self.isDismantlingForGold, self.isCrewDismiss, itemsFromVehicle, itemsFromInventory)
        BigWorld.player().inventory.sellVehicle(self.vehicle.invID, self.isCrewDismiss, itemsFromVehicle, itemsFromInventory, lambda code: self._response(code, callback))

    def __dismantlingForGoldDevicesCount(self, vehicle, optDevicesToSell):
        result = 0
        if vehicle is None:
            return result
        else:
            optDevicesToSell = [ dev.intCD for dev in optDevicesToSell ]
            for dev in vehicle.optDevices:
                if dev is None:
                    continue
                if not dev.isRemovable and dev.intCD not in optDevicesToSell:
                    result += 1

            return result

    def __getGainSpendMoney(self, vehicle, vehShells, vehEqs, vehOptDevs, inventory, dismantlingGoldCost):
        moneyGain = vehicle.sellPrice
        for shell in vehShells:
            moneyGain += shell.sellPrice * shell.count

        for module in vehEqs + vehOptDevs:
            moneyGain += module.sellPrice

        for module in inventory:
            moneyGain += module.sellPrice * module.inventoryCount

        moneySpend = dismantlingGoldCost * Money(gold=self.__dismantlingForGoldDevicesCount(vehicle, vehOptDevs))
        return (moneyGain, moneySpend)

    def __accumulatePrice(self, result, price, count=1):
        result += price * count
        return result


class VehicleSettingsProcessor(ItemProcessor):

    def __init__(self, vehicle, setting, value, plugins=list()):
        self._setting = setting
        self._value = value
        super(VehicleSettingsProcessor, self).__init__(vehicle, plugins)

    def _request(self, callback):
        LOG_DEBUG('Make server request for changing vehicle settings', self.item, self._setting, bool(self._value))
        BigWorld.player().inventory.changeVehicleSetting(self.item.invID, self._setting, bool(self._value), lambda code: self._response(code, callback))


class VehicleTmenXPAccelerator(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleTmenXPAccelerator, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.XP_TO_TMAN, value, (plugins.MessageConfirmator('xpToTmenCheckbox', isEnabled=value),))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('vehicle_tmenxp_accelerator/%s' % errStr, defaultSysMsgKey='vehicle_tmenxp_accelerator/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('vehicle_tmenxp_accelerator/success' + str(self._value), vehName=self.item.userName, type=SM_TYPE.Information)


class VehicleFavoriteProcessor(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleFavoriteProcessor, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.GROUP_0, value)


class VehicleAutoRepairProcessor(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleAutoRepairProcessor, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.AUTO_REPAIR, value)


class VehicleAutoLoadProcessor(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleAutoLoadProcessor, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.AUTO_LOAD, value)


class VehicleAutoEquipProcessor(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleAutoEquipProcessor, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.AUTO_EQUIP, value)


class VehicleLayoutProcessor(Processor):
    """
    Apply equipments and shells layout
    """

    def __init__(self, vehicle, shellsLayout=None, eqsLayout=None):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param shellsLayout: shells
        @param eqsLayout: equipments
        """
        super(VehicleLayoutProcessor, self).__init__()
        self.vehicle = vehicle
        self.shellsLayout = shellsLayout
        self.eqsLayout = eqsLayout
        shellsPrice = self.getShellsLayoutPrice()
        eqsPrice = self.getEqsLayoutPrice()
        isWalletValidatorEnabled = bool(shellsPrice.gold or eqsPrice.gold)
        self.addPlugins((plugins.VehicleLockValidator(vehicle), plugins.WalletValidator(isWalletValidatorEnabled), plugins.VehicleLayoutValidator(shellsPrice, eqsPrice)))

    def _request(self, callback):
        BigWorld.player().inventory.setAndFillLayouts(self.vehicle.invID, self.shellsLayout, self.eqsLayout, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))

    def __getSysMsgType(self, price):
        return CURRENCY_TO_SM_TYPE.get(price.getCurrency(byWeight=False), SM_TYPE.Information)

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        if len(ctx.get('shells', [])):
            totalPrice = ZERO_MONEY
            for shellCompDescr, price, count in ctx.get('shells', []):
                price = Money(*price)
                shell = g_itemsCache.items.getItemByCD(shellCompDescr)
                additionalMessages.append(makeI18nSuccess('shell_buy/success', name=shell.userName, count=count, money=formatPrice(price), type=self.__getSysMsgType(price)))
                totalPrice += price

            additionalMessages.append(makeI18nSuccess('layout_apply/success_money_spent', money=formatPrice(totalPrice), type=self.__getSysMsgType(totalPrice)))
        if len(ctx.get('eqs', [])):
            for eqCompDescr, price, count in ctx.get('eqs', []):
                price = Money(*price)
                equipment = g_itemsCache.items.getItemByCD(eqCompDescr)
                additionalMessages.append(makeI18nSuccess('artefact_buy/success', kind=equipment.userType, name=equipment.userName, count=count, money=formatPrice(price), type=self.__getSysMsgType(price)))

        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        if not len(errStr):
            msg = 'server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'server_error_centerDown'
        else:
            msg = errStr
        return makeI18nError('layout_apply/%s' % msg, defaultSysMsgKey='layout_apply/server_error', vehName=self.vehicle.userName, type=SM_TYPE.Error)

    def getShellsLayoutPrice(self):
        """
        @return: price that should be paid to fill layout
        """
        if self.shellsLayout is None:
            return ZERO_MONEY
        else:
            price = ZERO_MONEY
            for shellCompDescr, count, isBoughtForCredits in LayoutIterator(self.shellsLayout):
                if not shellCompDescr or not count:
                    continue
                shell = g_itemsCache.items.getItemByCD(int(shellCompDescr))
                vehShell = findFirst(lambda s: s.intCD == shellCompDescr, self.vehicle.shells)
                vehCount = vehShell.count if vehShell is not None else 0
                buyCount = count - shell.inventoryCount - vehCount
                if buyCount:
                    buyPrice = buyCount * shell.buyPrice
                    if isBoughtForCredits:
                        buyPrice = buyPrice.exchange(Currency.GOLD, Currency.CREDITS, g_itemsCache.items.shop.exchangeRateForShellsAndEqs)
                    price += buyPrice

            return price

    def getEqsLayoutPrice(self):
        """
        @return: price that should be paid to fill layout
        """
        if self.eqsLayout is None:
            return ZERO_MONEY
        else:
            price = ZERO_MONEY
            for idx, (eqCompDescr, count, isBoughtForCredits) in enumerate(LayoutIterator(self.eqsLayout)):
                if not eqCompDescr or not count:
                    continue
                equipment = g_itemsCache.items.getItemByCD(int(eqCompDescr))
                vehEquipment = self.vehicle.eqs[idx]
                vehCount = 1 if vehEquipment is not None else 0
                buyCount = count - equipment.inventoryCount - vehCount
                if buyCount:
                    buyPrice = buyCount * equipment.buyPrice
                    if isBoughtForCredits:
                        buyPrice = buyPrice.exchange(Currency.GOLD, Currency.CREDITS, g_itemsCache.items.shop.exchangeRateForShellsAndEqs)
                    price += buyPrice

            return price


class VehicleRepairer(ItemProcessor):

    def __init__(self, vehicle):
        self._repairCost = Money(credits=vehicle.repairCost)
        super(VehicleRepairer, self).__init__(vehicle, (plugins.MoneyValidator(self._repairCost),))

    def _request(self, callback):
        BigWorld.player().inventory.repair(self.item.invID, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        needed = Money(credits=self._repairCost.credits - g_itemsCache.items.stats.credits)
        return makeI18nError('vehicle_repair/%s' % errStr, defaultSysMsgKey='vehicle_repair/server_error', vehName=self.item.userName, needed=formatPrice(needed))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('vehicle_repair/success', vehName=self.item.userName, money=formatPrice(self._repairCost), type=SM_TYPE.Repair)


@async
@process
def tryToLoadDefaultShellsLayout(vehicle, callback=None):
    defaultLayout = []
    for shell in vehicle.shells:
        if shell.defaultCount > shell.inventoryCount:
            SystemMessages.pushI18nMessage('#system_messages:charge/inventory_error', vehicle=vehicle.userName, type=SystemMessages.SM_TYPE.Warning)
            yield lambda callback: callback(None)
            break
        defaultLayout.extend(shell.defaultLayoutValue)
    else:
        result = yield VehicleLayoutProcessor(vehicle, defaultLayout).request()
        if result and result.auxData:
            for m in result.auxData:
                SystemMessages.pushI18nMessage(m.userMsg, type=m.sysMsgType)

        if result and len(result.userMsg):
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if callback is not None:
            callback(True)
            return

    if callback is not None:
        callback(False)
    return


def _getUniqueVehicleSellConfirmator(vehicle):
    """
    return confirmation plugin for unique vehicle
    :param vehicle: <Vehicle>
    :return: <MessageConfirmator>
    """
    if g_lobbyContext.getServerSettings().isVehicleRestoreEnabled():
        if not vehicle.sellForGold and not vehicle.isUnrecoverable:
            if vehicle.isRecentlyRestored():
                return plugins.MessageConfirmator('vehicleSell/restoreCooldown', ctx={'cooldown': formatTime(vehicle.restoreInfo.getRestoreCooldownTimeLeft(), time_utils.ONE_DAY)}, isEnabled=vehicle.isUnique)
            return vehicle.isPurchased and plugins.MessageConfirmator('vehicleSell/restoreUnlimited', isEnabled=vehicle.isUnique)
    return plugins.MessageConfirmator('vehicleSell/unique', isEnabled=vehicle.isUnique)
