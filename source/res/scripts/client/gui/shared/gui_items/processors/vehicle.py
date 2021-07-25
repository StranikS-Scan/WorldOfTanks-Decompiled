# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/vehicle.py
import logging
from functools import partial
from itertools import chain
import BigWorld
import AccountCommands
from constants import RentType, SEASON_NAME_BY_TYPE, CLIENT_COMMAND_SOURCES
from AccountCommands import VEHICLE_SETTINGS_FLAG
from gui.shared.gui_items.processors.messages.items_processor_messages import ItemBuyProcessorMessage, BattleAbilitiesApplyProcessorMessage, LayoutApplyProcessorMessage, BattleBoostersApplyProcessorMessage, OptDevicesApplyProcessorMessage, ConsumablesApplyProcessorMessage, ShellsApplyProcessorMessage
from gui.shared.gui_items.vehicle_equipment import EMPTY_ITEM
from items import EQUIPMENT_TYPES
from items.components.c11n_constants import SeasonType
from adisp import process, async
from gui import SystemMessages, g_tankActiveCamouflage
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles
from gui.shared.formatters import icons
from gui.shared.formatters.time_formatters import formatTime, getTimeLeftInfo
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import ItemProcessor, Processor, makeI18nSuccess, makeI18nError, plugins as proc_plugs, makeSuccess, makeTextSuccess
from gui.shared.money import Money, MONEY_UNDEFINED, Currency, ZERO_MONEY
from helpers import time_utils, dependency
from gui.shared.gui_items.gui_item_economics import getVehicleBattleBoostersLayoutPrice, getVehicleConsumablesLayoutPrice, getVehicleOptionalDevicesLayoutPrice, getVehicleShellsLayoutPrice
from helpers.i18n import makeString
from items.components.detachment_constants import DetachmentSlotType
from skeletons.gui.game_control import IRestoreController, ITradeInController, IEpicBattleMetaGameController, IPersonalTradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from rent_common import parseRentID
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_SEASON_RENT_DURATION_KEY = {RentType.SEASON_RENT: 'season',
 RentType.SEASON_CYCLE_RENT: 'cycle'}

def getCrewAndShellsSumPrice(result, vehicle, crewType, buyShells):
    if crewType != -1:
        tankmenCount = len(vehicle.crew)
        itemsCache = dependency.instance(IItemsCache)
        tankmanCost = itemsCache.items.shop.tankmanCostWithGoodyDiscount[crewType]
        result += Money(**tankmanCost) * tankmenCount
    if buyShells:
        for shell in vehicle.gun.defaultAmmo:
            result += shell.buyPrices.itemPrice.price * shell.count

    return result


def getCustomizationItemSellCountForVehicle(item, vehicleIntCD):
    installedCount = item.installedCount(vehicleIntCD)
    if not item.isProgressive:
        return installedCount
    inventoryCount = item.fullInventoryCount(vehicleIntCD)
    availableForSell = installedCount + inventoryCount - item.descriptor.progression.autoGrantCount
    return min(installedCount, availableForSell)


class VehicleReceiveProcessor(ItemProcessor):

    def __init__(self, vehicle, buyShell=False, crewType=-1):
        self.item = vehicle
        self.buyShell = buyShell
        self.buyCrew = crewType != -1
        self.crewType = crewType
        self.price = self._getPrice()
        super(VehicleReceiveProcessor, self).__init__(vehicle, self._getPluginsList())

    def _getPluginsList(self):
        raise NotImplementedError

    def _getPrice(self):
        raise NotImplementedError

    def _getSysMsgType(self):
        raise NotImplementedError


class VehicleBuyer(VehicleReceiveProcessor):

    def __init__(self, vehicle, buySlot, buyShell=False, crewType=-1, showNotEnoughSlotMsg=True):
        self.buySlot = buySlot
        self.showNotEnoughSlotMsg = showNotEnoughSlotMsg
        super(VehicleBuyer, self).__init__(vehicle, buyShell=buyShell, crewType=crewType)

    def _getPluginsList(self):
        return (proc_plugs.MoneyValidator(self.price),
         proc_plugs.VehicleSlotsConfirmator(self.showNotEnoughSlotMsg and not self.buySlot),
         proc_plugs.VehicleFreeLimitConfirmator(self.item, self.crewType),
         proc_plugs.CollectibleVehiclesValidator(self.item.intCD))

    def _getPrice(self):
        return getCrewAndShellsSumPrice(self.item.buyPrices.itemPrice.price, self.item, self.crewType, self.buyShell)

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def _errorHandler(self, code, errStr='', ctx=None, itemsCache=None):
        if not errStr:
            errStr = 'server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'server_error_centerDown'
        msg = 'vehicle_buy/{}'.format(errStr)
        slotsEnough = itemsCache.items.inventory.getFreeSlots(itemsCache.items.stats.vehicleSlots) > 0
        if not self.showNotEnoughSlotMsg and not slotsEnough:
            errStr = 'slot_error'
        return makeI18nError(sysMsgKey=msg, defaultSysMsgKey='vehicle_buy/server_error', auxData={'errStr': errStr}, vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_buy/success', vehName=self.item.userName, price=formatPrice(self.price, useStyle=True), type=self._getSysMsgType())

    def _getSysMsgType(self):
        return CURRENCY_TO_SM_TYPE.get(self.item.buyPrices.itemPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make request to buy vehicle: %s, %s, %s, %s', self.item, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, -1, lambda code: self._response(code, callback))


class VehicleRenter(VehicleReceiveProcessor):

    def __init__(self, vehicle, rentID, buyShell=False, crewType=-1):
        self.rentPackageID = rentID
        self.rentPrice = self.__getRentPrice(rentID, vehicle)
        self.rentPackage = vehicle.getRentPackage(rentID)
        super(VehicleRenter, self).__init__(vehicle, buyShell, crewType)

    def _getPluginsList(self):
        return (proc_plugs.MoneyValidator(self.price), proc_plugs.VehicleFreeLimitConfirmator(self.item, self.crewType))

    def _getPrice(self):
        return getCrewAndShellsSumPrice(self.rentPrice, self.item, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            msg = 'vehicle_rent/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_rent/server_error_centerDown'
        else:
            msg = 'vehicle_rent/{}'.format(errStr)
        return makeI18nError(sysMsgKey=msg, defaultSysMsgKey='vehicle_rent/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        rentType, packageID = parseRentID(self.rentPackageID)
        if rentType == RentType.TIME_RENT:
            rentPackageName = makeString(SYSTEM_MESSAGES.VEHICLE_RENT_TIMERENT, days=packageID)
        elif rentType in (RentType.SEASON_CYCLE_RENT, RentType.SEASON_RENT):
            seasonName = SEASON_NAME_BY_TYPE[self.rentPackage['seasonType']]
            durationKey = _SEASON_RENT_DURATION_KEY.get(rentType)
            rentPackageName = makeString('#system_messages:vehicle_rent/{}/{}'.format(seasonName, durationKey))
        else:
            raise SoftException('Unknown rent type [{}]!'.format(rentType))
        if not self.item.isDisabledForBuy and not self.item.isHidden:
            buyOption = makeString(SYSTEM_MESSAGES.VEHICLE_RENT_BUYOPTION)
        else:
            buyOption = ''
        return makeI18nSuccess('vehicle_rent/success', vehName=self.item.userName, rentPackageName=rentPackageName, price=formatPrice(self.price), type=self._getSysMsgType(), buyOption=buyOption)

    def _request(self, callback):
        _logger.debug('Make request to rent vehicle: %s, %s, %s, %s', self.item, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, self.rentPackageID, lambda code: self._response(code, callback, ctx={'rentID': self.rentPackageID}))

    def _getSysMsgType(self):
        return CURRENCY_TO_SM_TYPE.get(self.rentPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def __getRentPrice(self, rentID, vehicle):
        for package in vehicle.rentPackages:
            if package['rentID'] == rentID:
                return package['rentPrice']

        return MONEY_UNDEFINED


class VehicleRestoreProcessor(VehicleBuyer):

    def _getPrice(self):
        return getCrewAndShellsSumPrice(self.item.restorePrice, self.item, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr='', ctx=None, itemsCache=None):
        if not errStr:
            msg = 'vehicle_restore/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_restore/server_error_centerDown'
        else:
            msg = 'vehicle_restore/{}'.format(errStr)
        return makeI18nError(sysMsgKey=msg, defaultSysMsgKey='vehicle_restore/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_restore/success', vehName=self.item.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getSysMsgType(self):
        return SM_TYPE.Restore

    def _getPluginsList(self):
        return (proc_plugs.MoneyValidator(self.price), proc_plugs.VehicleSlotsConfirmator(not self.buySlot), proc_plugs.IsLongDisconnectedFromCenter())

    def _request(self, callback):
        _logger.debug('Make request to restore vehicle: %s, %s, %s, %s', self.item, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, -1, lambda code: self._response(code, callback))


class VehicleTradeInProcessorBase(VehicleBuyer):

    def __init__(self, vehicleToBuy, vehicleToTradeOff, buySlot, buyShell=False, crewType=-1):
        self.itemToTradeOff = vehicleToTradeOff
        super(VehicleTradeInProcessorBase, self).__init__(vehicleToBuy, buySlot, buyShell=buyShell, crewType=crewType)

    def _getPluginsList(self):
        return (proc_plugs.VehicleValidator(self.itemToTradeOff, setAll=True), proc_plugs.VehicleSellValidator(self.itemToTradeOff), proc_plugs.MoneyValidator(self.price))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_trade_in/success', vehName=self.item.userName, tradeOffVehName=self.itemToTradeOff.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getSysMsgType(self):
        return CURRENCY_TO_SM_TYPE.get(self.item.buyPrices.itemPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None, itemsCache=None):
        if not errStr:
            msg = 'vehicle_trade_in/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_trade_in/server_error_centerDown'
        else:
            msg = 'vehicle_trade_in/{}'.format(errStr)
        return makeI18nError(sysMsgKey=msg, defaultSysMsgKey='vehicle_trade_in/server_error', vehName=self.item.userName, tradeOffVehName=self.itemToTradeOff.userName)

    def _request(self, callback):
        _logger.debug('Make request to trade-in vehicle: %s, %s, %s, %s, %s, %s', self.item, self.itemToTradeOff, self.buyShell, self.buyCrew, self.crewType, self.price)
        self._getBuyingFunc()(self.itemToTradeOff.invID, self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, lambda code: self._response(code, callback))

    def _getBuyingFunc(self):
        raise NotImplementedError


class VehicleTradeInProcessor(VehicleTradeInProcessorBase):
    __tradeIn = dependency.descriptor(ITradeInController)

    def _getPrice(self):
        price = self.__tradeIn.getTradeInPrice(self.item).price
        return getCrewAndShellsSumPrice(price, self.item, self.crewType, self.buyShell)

    def _getBuyingFunc(self):
        return BigWorld.player().shop.tradeInVehicle

    def _getPluginsList(self):
        return super(VehicleTradeInProcessor, self)._getPluginsList() + (proc_plugs.VehicleTradeInValidator(self.item, self.itemToTradeOff),)


class VehiclePersonalTradeInProcessor(VehicleTradeInProcessorBase):
    __personalTradeIn = dependency.descriptor(IPersonalTradeInController)

    def _getPrice(self):
        price = self.__personalTradeIn.getPersonalTradeInPrice(self.item).price
        return getCrewAndShellsSumPrice(price, self.item, self.crewType, self.buyShell)

    def _getBuyingFunc(self):
        return BigWorld.player().shop.personalTradeInVehicle

    def _getPluginsList(self):
        return super(VehiclePersonalTradeInProcessor, self)._getPluginsList() + (proc_plugs.VehiclePersonalTradeInValidator(self.item, self.itemToTradeOff),)


class VehicleSlotBuyer(Processor):

    def __init__(self, showConfirm=True, showWarning=True):
        self.__hasDiscounts = bool(self.itemsCache.items.shop.personalSlotDiscounts)
        self.__frozenSlotPrice = None
        slotCost = self.__getSlotPrice()
        if self.__hasDiscounts and not slotCost:
            confirmationType = 'freeSlotConfirmation'
            ctx = {}
        else:
            confirmationType = 'buySlotConfirmation'
            ctx = {'goldCost': text_styles.concatStylesWithSpace(text_styles.gold(str(slotCost.gold)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))}
        super(VehicleSlotBuyer, self).__init__((proc_plugs.MessageInformator('buySlotNotEnoughCredits', activeHandler=lambda : not proc_plugs.MoneyValidator(slotCost).validate().success, isEnabled=showWarning), proc_plugs.MessageConfirmator(confirmationType, isEnabled=showConfirm, ctx=ctx), proc_plugs.MoneyValidator(slotCost)))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='vehicle_slot_buy/{}'.format(errStr), defaultSysMsgKey='vehicle_slot_buy/server_error')

    def _successHandler(self, code, ctx=None):
        price = self.__getSlotPrice()
        if price:
            money = formatPrice(price)
        else:
            money = formatGoldPrice(price.gold)
        dormText = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.quests.dormitories(), amount=1)
        slotText = backport.text(R.strings.system_messages.vehicle_slot_buy.success(), money=money)
        return makeTextSuccess(text=text_styles.concatStylesToMultiLine(dormText, slotText), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        _logger.debug('Attempt to request server for buying vehicle slot')
        BigWorld.player().stats.buySlot(lambda code: self._response(code, callback))

    def __getSlotPrice(self):
        if self.__frozenSlotPrice is not None:
            return self.__frozenSlotPrice
        else:
            price = self.itemsCache.items.shop.getVehicleSlotsPrice(self.itemsCache.items.stats.vehicleSlots)
            if self.__hasDiscounts:
                self.__frozenSlotPrice = Money(gold=price)
            return Money(gold=price)


class VehicleSeller(ItemProcessor):
    restore = dependency.descriptor(IRestoreController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    class MsgBitMask(object):
        EMPTY = 0
        DEMOUNT_KIT = 1
        DISMANTLING = 2
        EXC_INSTRUCTORS_FREE = 4
        EXC_INSTRUCTORS_PAID = 8

    def __init__(self, vehicle, shells=None, eqs=None, optDevs=None, inventory=None, customizationItems=None, boosters=None, isDismiss=False, itemsForDemountKit=None, allowRemove=False, freeExcludeInstructors=True):
        shells = shells or []
        eqs = eqs or []
        boosters = boosters or []
        optDevs = optDevs or []
        inventory = inventory or []
        customizationItems = customizationItems or []
        itemsForDemountKit = itemsForDemountKit or []
        nationGroupVehs = vehicle.getAllNationGroupVehs(self.itemsCache.items)
        self.vehicle = vehicle
        self.nationGroupVehs = nationGroupVehs
        self.shells = shells
        self.eqs = eqs
        self.optDevs = optDevs
        self.gainMoney, self.spendMoney = self.__getGainSpendMoney(vehicle, nationGroupVehs, shells, eqs, boosters, optDevs, inventory, customizationItems, itemsForDemountKit)
        self.excludeInstructorsMoney, self.instructorCount = self.__getEcxludeInstructorsMoney(vehicle, freeExcludeInstructors)
        self.inventory = set((m.intCD for m in inventory))
        self.customizationItems = set(customizationItems)
        self.boosters = boosters
        self.itemsForDemountKit = itemsForDemountKit
        plugins = [proc_plugs.VehicleValidator(vehicle, False, prop={'isBroken': True,
          'isLocked': True}),
         proc_plugs.VehicleSellValidator(vehicle),
         proc_plugs.MoneyValidator(self.spendMoney - self.gainMoney + self.excludeInstructorsMoney),
         proc_plugs.VehicleSellsLeftValidator(vehicle, not (vehicle.isRented and vehicle.rentalIsOver)),
         proc_plugs.BattleBoosterValidator(boosters),
         proc_plugs.DismountForDemountKitValidator(vehicle, itemsForDemountKit),
         proc_plugs.VehicleCrewDismissValidator(vehicle, isDismiss),
         _getUniqueVehicleSellConfirmator(vehicle)]
        super(VehicleSeller, self).__init__(vehicle, plugins)
        self.isDismiss = isDismiss
        self.allowRemove = allowRemove
        self.freeExcludeInstructors = freeExcludeInstructors
        self.isDismantlingForMoney = bool(self.spendMoney)
        self.isRemovedAfterRent = vehicle.isRented
        self.usedDemountKitsCount = len(itemsForDemountKit)

    def _errorHandler(self, code, errStr='', ctx=None):
        localKey = 'vehicle_sell/{}'
        defaultKey = 'vehicle_sell/server_error'
        if self.isRemovedAfterRent:
            localKey = 'vehicle_remove/{}'
            defaultKey = 'vehicle_remove/server_error'
        return makeI18nError(sysMsgKey=localKey.format(errStr), defaultSysMsgKey=defaultKey, vehName=self.vehicle.userName)

    def _successHandler(self, code, ctx=None):
        restoreInfo = ''
        sellForGold = self.vehicle.getSellPrice(preferred=True).getCurrency(byWeight=True) == Currency.GOLD
        if self.vehicle.isPremium and not self.vehicle.isUnique and not self.vehicle.isUnrecoverable and self.lobbyContext.getServerSettings().isVehicleRestoreEnabled() and not sellForGold:
            timeKey, formattedTime = getTimeLeftInfo(self.itemsCache.items.shop.vehiclesRestoreConfig.restoreDuration)
            restoreInfo = makeString('#system_messages:vehicle/restoreDuration/{}'.format(timeKey), time=formattedTime)
        g_tankActiveCamouflage[self.vehicle.intCD] = SeasonType.UNDEFINED
        makeMsg = partial(makeI18nSuccess, vehName=self.vehicle.userName)
        if self.isRemovedAfterRent:
            sysMsgKey = 'vehicle_remove/success'
        else:
            sysMsgKey = 'vehicle_sell/success'
            makeMsg = partial(makeMsg, restoreInfo=restoreInfo)
        if self.isDismantlingForMoney:
            sysMsgKey += '/dismantling'
            makeMsg = partial(makeMsg, gainMoney=formatPrice(self.gainMoney), spendMoney=formatPrice(self.spendMoney))
        else:
            makeMsg = partial(makeMsg, money=formatPrice(self.gainMoney))
        if self.usedDemountKitsCount:
            sysMsgKey += '/with_demount_kit'
            makeMsg = partial(makeMsg, countDK=self.usedDemountKitsCount)
        if self.instructorCount and self.isDismiss:
            if self.freeExcludeInstructors:
                sysMsgKey += '/exclude_instructors_free'
                makeMsg = partial(makeMsg, count=self.instructorCount)
            else:
                sysMsgKey += '/exclude_instructors_paid'
                makeMsg = partial(makeMsg, moneyExc=formatPrice(self.excludeInstructorsMoney), count=self.instructorCount)
        if self.isRemovedAfterRent:
            smType = SM_TYPE.Remove
        elif sellForGold:
            smType = SM_TYPE.SellingForGold
        else:
            smType = SM_TYPE.Selling
        return makeMsg(sysMsgKey=sysMsgKey, type=smType)

    def _request(self, callback):
        saleData = self.__splitDataByVehicle()
        _logger.debug('Make server request: %s, %s, %s, %s, %s, %s, %s, %s, %s', self.nationGroupVehs, bool(self.shells), bool(self.eqs), bool(self.boosters), bool(self.inventory), bool(self.optDevs), self.isDismantlingForMoney, self.isDismiss, saleData)
        BigWorld.player().inventory.sellVehicle(saleData, lambda code, errStr='': self._response(code, callback, errStr=errStr))

    def __getGainSpendMoney(self, currentVehicle, vehicles, vehShells, vehEqs, boosters, optDevicesToSell, inventory, customizationItems, itemsForDemountKit):
        moneyGain = currentVehicle.sellPrices.itemPrice.price
        for shell in vehShells:
            moneyGain += shell.sellPrices.itemPrice.price * shell.count

        for module in vehEqs + optDevicesToSell + boosters:
            moneyGain += module.sellPrices.itemPrice.price

        for module in inventory:
            moneyGain += module.sellPrices.itemPrice.price * module.inventoryCount

        for module in customizationItems:
            getCount = getCustomizationItemSellCountForVehicle
            moneyGain += module.sellPrices.itemPrice.price * reduce(lambda acc, veh: acc + getCount(module, veh.intCD), vehicles, 0)

        dismantlingToInventoryDevices = getDismantlingForMoneyToInventoryDevices(optDevicesToSell, itemsForDemountKit, *vehicles)
        moneySpend = calculateSpendMoney(self.itemsCache.items, dismantlingToInventoryDevices)
        return (moneyGain, moneySpend)

    def __getEcxludeInstructorsMoney(self, vehicle, freeExcludeInstructors):
        detachment = self.detachmentCache.getDetachment(vehicle.getLinkedDetachmentID())
        if not detachment:
            return (MONEY_UNDEFINED, 0)
        instructorCount = len([ locked for _, locked in detachment.getDescriptor().iterSlots(DetachmentSlotType.INSTRUCTORS, True, True) if not locked ])
        if instructorCount and not freeExcludeInstructors:
            recoverInstructorCost = self.itemsCache.items.shop.recoverInstructorCost * instructorCount
            return (recoverInstructorCost, instructorCount)
        return (MONEY_UNDEFINED, instructorCount)

    def __splitInventory(self):
        result = {}
        for vehicle in self.nationGroupVehs:
            vehInv = self.itemsCache.items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], (GUI_ITEM_TYPE.SHELL,) + GUI_ITEM_TYPE.VEHICLE_MODULES) | REQ_CRITERIA.INVENTORY).values()
            result[vehicle.invID] = set((m.intCD for m in vehInv)) & self.inventory

        full = reduce(lambda acc, inv: acc | inv, result.itervalues())
        unique = reduce(lambda acc, inv: acc ^ inv, result.itervalues())
        difference = full - unique
        for key in result.iterkeys():
            result[key] -= difference

        result[self.vehicle.invID].update(difference)
        return result

    def __splitDataByVehicle(self):
        result = []
        itemsFromInventory = self.__splitInventory()
        for vehicle in self.nationGroupVehs:
            itemsFromVehicle = set()
            seenCustItems = set()
            itemsForDemountKit = set()
            customizationItems = []
            for shell in list(self.shells):
                if shell.isInstalled(vehicle) and shell.intCD not in itemsFromVehicle:
                    itemsFromVehicle.add(shell.intCD)
                    self.shells.remove(shell)

            for booster in self.boosters:
                if booster.isInstalled(vehicle) and booster.intCD not in itemsFromVehicle:
                    itemsFromVehicle.add(booster.intCD)
                    self.boosters.remove(booster)

            for eq in list(self.eqs):
                if eq.isInstalled(vehicle) and eq.intCD not in itemsFromVehicle:
                    itemsFromVehicle.add(eq.intCD)
                    self.eqs.remove(eq)

            for od in list(self.optDevs):
                if od.isInstalled(vehicle) and od.intCD not in itemsFromVehicle:
                    itemsFromVehicle.add(od.intCD)
                    self.optDevs.remove(od)

            for ci in list(self.customizationItems):
                installedCount = getCustomizationItemSellCountForVehicle(ci, vehicle.intCD)
                if installedCount > 0 and ci.intCD not in seenCustItems:
                    customizationItems.append(ci.intCD)
                    customizationItems.append(installedCount)
                    seenCustItems.add(ci.intCD)
                    self.customizationItems.remove(ci)

            for od in list(self.itemsForDemountKit):
                if od.isInstalled(vehicle) and od.intCD not in itemsForDemountKit and od.intCD not in itemsFromVehicle:
                    itemsForDemountKit.add(od.intCD)
                    self.itemsForDemountKit.remove(od)

            result.append((vehicle.invID,
             int(self.isDismiss),
             int(self.allowRemove),
             int(self.freeExcludeInstructors),
             list(itemsFromVehicle),
             list(itemsFromInventory[vehicle.invID]),
             customizationItems,
             list(itemsForDemountKit)))

        return result


def getDismantlingForMoneyToInventoryDevices(optDevicesToSell, itemsForDemountKit, *vehicles):
    result = []
    itemsForDk = [ dev.intCD for dev in itemsForDemountKit ]
    for dev in getDismantlingToInventoryDevices(optDevicesToSell, *vehicles):
        if dev.intCD in itemsForDk:
            itemsForDk.remove(dev.intCD)
        result.append(dev)

    return result


def getDismantlingToInventoryDevices(optDevicesToSell, *vehicles):
    result = []
    optDevicesToSell = [ dev.intCD for dev in optDevicesToSell ]
    for vehicle in vehicles:
        vehDevices = vehicle.optDevices.installed if vehicle is not None else []
        for dev in vehDevices:
            if dev and not dev.isRemovable:
                if dev.intCD in optDevicesToSell:
                    optDevicesToSell.remove(dev.intCD)
                else:
                    result.append(dev)

    return result


def calculateSpendMoney(items, dismantlingToInventoryDevices):
    moneySpend = MONEY_UNDEFINED
    for dev in dismantlingToInventoryDevices:
        moneySpend += dev.getRemovalPrice(items).price

    return moneySpend


class VehicleSettingsProcessor(ItemProcessor):

    def __init__(self, vehicle, setting, value, plugins=None, source=CLIENT_COMMAND_SOURCES.UNDEFINED):
        self._setting = setting
        self._value = value
        self._source = source
        super(VehicleSettingsProcessor, self).__init__(vehicle, plugins or [])

    def _request(self, callback):
        _logger.debug('Make server request for changing vehicle settings: %s, %s, %s', self.item, self._setting, bool(self._value))
        BigWorld.player().inventory.changeVehicleSetting(self.item.invID, self._setting, bool(self._value), self._source, lambda code: self._response(code, callback))


class VehicleDetachmentXPAccelerator(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleDetachmentXPAccelerator, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.XP_TO_DET, value, (proc_plugs.VehicleDetachmentValidator(vehicle),))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='vehicle_detachment_accelerator/{}'.format(errStr), defaultSysMsgKey='vehicle_detachment_accelerator/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_detachment_accelerator/success' + str(self._value), vehName=self.item.userName, type=SM_TYPE.Information)


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


class VehicleAutoBattleBoosterEquipProcessor(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleAutoBattleBoosterEquipProcessor, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER, value)


class VehicleAutoStyleEquipProcessor(VehicleSettingsProcessor):

    def __init__(self, vehicle, value, source):
        super(VehicleAutoStyleEquipProcessor, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.AUTO_RENT_CUSTOMIZATION, value, source=source)


class VehicleRepairer(ItemProcessor):

    def __init__(self, vehicle):
        self._repairCost = Money(credits=vehicle.repairCost)
        super(VehicleRepairer, self).__init__(vehicle, (proc_plugs.MoneyValidator(self._repairCost),))

    def _request(self, callback):
        BigWorld.player().inventory.repair(self.item.invID, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        needed = Money(credits=self._repairCost.credits - self.itemsCache.items.stats.credits)
        return makeI18nError(sysMsgKey='vehicle_repair/{}'.format(errStr), defaultSysMsgKey='vehicle_repair/server_error', vehName=self.item.userName, needed=formatPrice(needed))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_repair/success', vehName=self.item.userName, money=formatPrice(self._repairCost), type=SM_TYPE.Repair)


@async
@process
def tryToLoadDefaultShellsLayout(vehicle, callback=None):
    defaultLayout = []
    for shell in vehicle.shells.layout.getItems():
        if shell.count > shell.inventoryCount:
            SystemMessages.pushI18nMessage('#system_messages:charge/inventory_error', vehicle=vehicle.userName, type=SystemMessages.SM_TYPE.Warning)
            yield lambda callback: callback(None)
            break
        defaultLayout.extend(shell.defaultLayoutValue)
    else:
        result = yield BuyAndInstallShellsProcessor(vehicle).request()
        if result and result.auxData:
            for m in result.auxData:
                SystemMessages.pushI18nMessage(m.userMsg, type=m.sysMsgType)

        if result and result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if callback is not None:
            callback(True)
            return

    if callback is not None:
        callback(False)
    return


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getUniqueVehicleSellConfirmator(vehicle, lobbyContext=None):
    sellForGold = vehicle.getSellPrice(preferred=True).getCurrency(byWeight=True) == Currency.GOLD
    if lobbyContext is not None and lobbyContext.getServerSettings().isVehicleRestoreEnabled():
        if not sellForGold and not vehicle.isUnrecoverable:
            if vehicle.isRecentlyRestored():
                return proc_plugs.MessageConfirmator('vehicleSell/restoreCooldown', ctx={'cooldown': formatTime(vehicle.restoreInfo.getRestoreCooldownTimeLeft(), time_utils.ONE_DAY)}, isEnabled=vehicle.isUnique)
            if vehicle.isPurchased:
                return proc_plugs.MessageConfirmator('vehicleSell/restoreUnlimited', isEnabled=vehicle.isUnique)
        dialogI18n = vehicle.isCrewLocked and 'vehicleSell/unique/crewLocked'
    else:
        dialogI18n = 'vehicleSell/unique'
    return proc_plugs.MessageConfirmator(dialogI18n, isEnabled=vehicle.isUnique)


class SetEnhancementProcessor(Processor):

    def __init__(self, slot, enhancementID, vehicle):
        super(SetEnhancementProcessor, self).__init__(plugins=[proc_plugs.VehicleValidator(vehicle)])
        self.vehicleInvID = vehicle.invID
        self.slot = slot
        self.enhancementID = enhancementID

    def _request(self, callback):
        BigWorld.player().setEnhancement(self.vehicleInvID, self.slot, self.enhancementID, lambda code, errStr: self._response(code, callback, errStr=errStr))


class DismountEnhancementProcessor(Processor):

    def __init__(self, slot, vehicle):
        super(DismountEnhancementProcessor, self).__init__(plugins=[proc_plugs.VehicleValidator(vehicle)])
        self.vehicleInvID = vehicle.invID
        self.slot = slot

    def _request(self, callback):
        BigWorld.player().dismountEnhancement(self.vehicleInvID, self.slot, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))


class OptDevicesInstaller(Processor):

    def __init__(self, vehicle):
        super(OptDevicesInstaller, self).__init__()
        self.__buyItems = [ item for item in vehicle.optDevices.layout.getItems() if not item.isInInventory and item not in vehicle.optDevices.installed ]
        self.__price = getVehicleOptionalDevicesLayoutPrice(vehicle).price
        self._vehicle = vehicle
        self.__devices = vehicle.optDevices.layout.getIntCDs()
        self._setupPlugins()

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self._vehicle), proc_plugs.MoneyValidator(self.__price, byCurrencyError=False), proc_plugs.OptionalDevicesInstallValidator(self._vehicle)))

    def _request(self, callback):
        BigWorld.player().inventory.equipOptDevsSequence(self._vehicle.invID, self.__devices, lambda code, errStr: self._response(code, callback, errStr))

    def _errorHandler(self, code, errStr='', ctx=None):
        return OptDevicesApplyProcessorMessage().makeErrorMsg(errStr)

    def _successHandler(self, code, ctx=None):
        buyMessages = [ ItemBuyProcessorMessage(item, 1).makeSuccessMsg() for item in self.__buyItems ]
        return makeSuccess(auxData=buyMessages)


class BuyAndInstallConsumablesProcessor(Processor):

    def __init__(self, vehicle):
        super(BuyAndInstallConsumablesProcessor, self).__init__()
        self._vehicle = vehicle
        self._setupPlugins()

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self._vehicle), proc_plugs.MoneyValidator(getVehicleConsumablesLayoutPrice(self._vehicle).price, byCurrencyError=False), proc_plugs.ConsumablesInstallValidator(self._vehicle)))

    def _request(self, callback):
        BigWorld.player().inventory.setAndFillLayouts(self._vehicle.invID, None, self.__getLayoutRaw(), EQUIPMENT_TYPES.regular, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))
        return

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        if ctx:
            additionalMessages = [ ItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, Money.makeFromMoneyTuple(price)).makeSuccessMsg() for cd, price, count in ctx.get('eqs', []) ]
        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        return ConsumablesApplyProcessorMessage(self._vehicle).makeErrorMsg(errStr)

    def __getLayoutRaw(self):
        layout = [ (item.defaultLayoutValue if item is not None else (0, 0)) for item in self._vehicle.consumables.layout ]
        currentBoosters = [ (item.defaultLayoutValue if item is not None else (0, 0)) for item in self._vehicle.battleBoosters.installed ]
        layout.extend(currentBoosters)
        return [ v for v in chain.from_iterable(layout) ]


class BuyAndInstallShellsProcessor(Processor):

    def __init__(self, vehicle):
        super(BuyAndInstallShellsProcessor, self).__init__()
        self.__vehicle = vehicle
        self._setupPlugins()

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self.__vehicle), proc_plugs.MoneyValidator(getVehicleShellsLayoutPrice(self.__vehicle).price, byCurrencyError=False), proc_plugs.ShellsInstallValidator(self.__vehicle)))

    def _request(self, callback):
        BigWorld.player().inventory.setAndFillLayouts(self.__vehicle.invID, self.__getShellsRaw(), None, 0, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))
        return

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        totalPrice = ZERO_MONEY
        if ctx:
            for cd, price, count in ctx.get('shells', []):
                money = Money.makeFromMoneyTuple(price)
                additionalMessages.append(ItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, money).makeSuccessMsg())
                totalPrice += money

            if totalPrice:
                additionalMessages.append(ShellsApplyProcessorMessage(self.__vehicle, totalPrice).makeSuccessMsg())
        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        return ShellsApplyProcessorMessage(self.__vehicle).makeErrorMsg(errStr)

    def __getShellsRaw(self):
        itemsIntAndCount = [ item.defaultLayoutValue for item in self.__vehicle.shells.layout ]
        return [ v for v in chain.from_iterable(itemsIntAndCount) ]


class BuyAndInstallBattleBoostersProcessor(Processor):

    def __init__(self, vehicle):
        super(BuyAndInstallBattleBoostersProcessor, self).__init__()
        self.__vehicle = vehicle
        self.__boosters = self.__vehicle.battleBoosters.layout.getItems()
        self._setupPlugins()

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self.__vehicle), proc_plugs.MoneyValidator(getVehicleBattleBoostersLayoutPrice(self.__vehicle).price, byCurrencyError=False), proc_plugs.BattleBoostersInstallValidator(self.__vehicle)))

    def _request(self, callback):
        BigWorld.player().inventory.setAndFillLayouts(self.__vehicle.invID, None, self.__getLayoutRaw(), EQUIPMENT_TYPES.battleBoosters, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))
        return

    def _successHandler(self, code, ctx=None):
        return makeSuccess(auxData=[ ItemBuyProcessorMessage(i, 1).makeSuccessMsg() for i in self.__boosters if not i.isInInventory ])

    def _errorHandler(self, code, errStr='', ctx=None):
        return BattleBoostersApplyProcessorMessage().makeErrorMsg(errStr)

    def __getLayoutRaw(self):
        desiredBoosters = [ (item.defaultLayoutValue if item is not None else (0, 0)) for item in self.__vehicle.battleBoosters.layout ]
        layout = [ (item.defaultLayoutValue if item is not None else (0, 0)) for item in self.__vehicle.consumables.installed ]
        layout.extend(desiredBoosters)
        return [ v for v in chain.from_iterable(layout) ]


class AutoFillVehicleLayoutProcessor(Processor):

    def __init__(self, vehicle):
        super(AutoFillVehicleLayoutProcessor, self).__init__()
        self.__vehicle = vehicle
        self._setupPlugins()

    def _setupPlugins(self):
        price = self.__getPrice()
        self.addPlugins((proc_plugs.VehicleValidator(self.__vehicle),
         proc_plugs.MoneyValidator(price),
         proc_plugs.ShellsInstallValidator(self.__vehicle),
         proc_plugs.ConsumablesInstallValidator(self.__vehicle)))

    def _request(self, callback):
        BigWorld.player().inventory.setAndFillLayouts(self.__vehicle.invID, self.__getShellsRaw(), self.__getConsumablesRaw(), EQUIPMENT_TYPES.regular, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        totalPrice = ZERO_MONEY
        if ctx:
            for cd, price, count in ctx.get('shells', []):
                money = Money.makeFromMoneyTuple(price)
                additionalMessages.append(ItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, money).makeSuccessMsg())
                totalPrice += money

            if totalPrice:
                additionalMessages.append(LayoutApplyProcessorMessage(self.__vehicle, totalPrice).makeSuccessMsg())
            additionalMessages.extend([ ItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, Money.makeFromMoneyTuple(price)).makeSuccessMsg() for cd, price, count in ctx.get('eqs', []) ])
        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        return LayoutApplyProcessorMessage(self.__vehicle).makeErrorMsg(errStr)

    def __getShellsRaw(self):
        itemsIntAndCount = [ item.defaultLayoutValue for item in self.__vehicle.shells.layout ]
        return [ v for v in chain.from_iterable(itemsIntAndCount) ]

    def __getConsumablesRaw(self):
        itemsIntAndCount = [ (item.defaultLayoutValue if item is not None else (0, 0)) for item in self.__vehicle.consumables.layout ]
        return [ v for v in chain.from_iterable(itemsIntAndCount) ]

    def __getPrice(self):
        return getVehicleShellsLayoutPrice(self.__vehicle).price + getVehicleConsumablesLayoutPrice(self.__vehicle).price


class InstallBattleAbilitiesProcessor(Processor):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, vehicle):
        super(InstallBattleAbilitiesProcessor, self).__init__()
        self.__vehicle = vehicle
        self._setupPlugins()

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self.__vehicle), proc_plugs.BattleAbilitiesValidator(self.__vehicle)))

    def _request(self, callback):
        self.__epicMetaGameCtrl.changeEquippedSkills(self.__getCurrentSkills(), self.__vehicle.intCD, lambda code, _: self._response(code, callback))

    def _successHandler(self, code, ctx=None):
        return makeSuccess()

    def _errorHandler(self, code, errStr='', ctx=None):
        return BattleAbilitiesApplyProcessorMessage().makeErrorMsg(errStr)

    def __getCurrentSkills(self):
        skillToAbilitiesIds = {skillID:[ sl.eqID for sl in skillLevels ] for skillID, skillLevels in self.__epicMetaGameCtrl.getAllUnlockedSkillLevelsBySkillId().iteritems()}
        currentSkills = [-1] * self.__epicMetaGameCtrl.getNumAbilitySlots(self.__vehicle.descriptor.type)
        for slotIdx, item in enumerate(self.__vehicle.battleAbilities.layout):
            for skillID, battleAbilitiesIDs in skillToAbilitiesIds.iteritems():
                if item != EMPTY_ITEM and item.innationID in battleAbilitiesIDs:
                    currentSkills[slotIdx] = skillID

        return currentSkills
