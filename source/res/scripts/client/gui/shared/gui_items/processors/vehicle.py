# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/vehicle.py
import logging
import BigWorld
import AccountCommands
from constants import RentType, SEASON_NAME_BY_TYPE, CLIENT_COMMAND_SOURCES
from AccountCommands import VEHICLE_SETTINGS_FLAG
from bootcamp.Bootcamp import g_bootcamp
from items import EQUIPMENT_TYPES
from items.components.crewSkins_constants import NO_CREW_SKIN_ID
from account_shared import LayoutIterator
from adisp import process, async
from gui import SystemMessages
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles
from gui.shared.formatters import icons
from gui.shared.formatters.time_formatters import formatTime, getTimeLeftInfo
from gui.shared.gui_items.processors import ItemProcessor, Processor, makeI18nSuccess, makeI18nError, plugins as proc_plugs, makeSuccess, makeCrewSkinCompensationMessage
from gui.shared.gui_items.vehicle_equipment import ShellLayoutHelper
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from helpers import time_utils, dependency
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers.i18n import makeString
from shared_utils import findFirst
from skeletons.gui.game_control import IRestoreController
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
            result += shell.buyPrices.itemPrice.price * shell.defaultCount

    return result


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
        return (proc_plugs.MoneyValidator(self.price), proc_plugs.VehicleSlotsConfirmator(self.showNotEnoughSlotMsg and not self.buySlot), proc_plugs.VehicleFreeLimitConfirmator(self.item, self.crewType))

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
        return makeI18nSuccess(sysMsgKey='vehicle_buy/success', vehName=self.item.userName, price=formatPrice(self.price), type=self._getSysMsgType())

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


class VehicleTradeInProcessor(VehicleBuyer):

    def __init__(self, vehicleToBuy, vehicleToTradeOff, buySlot, buyShell=False, crewType=-1):
        self.itemToTradeOff = vehicleToTradeOff
        super(VehicleTradeInProcessor, self).__init__(vehicleToBuy, buySlot, buyShell=buyShell, crewType=crewType)

    def _getPluginsList(self):
        barracksBerthsNeeded = len([ item for item in self.itemToTradeOff.crew if item[1] is not None ])
        return (proc_plugs.VehicleValidator(self.itemToTradeOff, setAll=True),
         proc_plugs.VehicleTradeInValidator(self.item, self.itemToTradeOff),
         proc_plugs.VehicleSellValidator(self.itemToTradeOff),
         proc_plugs.MoneyValidator(self.price),
         proc_plugs.BarracksSlotsValidator(barracksBerthsNeeded))

    def _getPrice(self):
        return super(VehicleTradeInProcessor, self)._getPrice() - self.itemToTradeOff.tradeOffPrice

    def _errorHandler(self, code, errStr='', ctx=None, itemsCache=None):
        if not errStr:
            msg = 'vehicle_trade_in/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_trade_in/server_error_centerDown'
        else:
            msg = 'vehicle_trade_in/{}'.format(errStr)
        return makeI18nError(sysMsgKey=msg, defaultSysMsgKey='vehicle_trade_in/server_error', vehName=self.item.userName, tradeOffVehName=self.itemToTradeOff.userName)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_trade_in/success', vehName=self.item.userName, tradeOffVehName=self.itemToTradeOff.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getSysMsgType(self):
        return CURRENCY_TO_SM_TYPE.get(self.item.buyPrices.itemPrice.getCurrency(byWeight=False), SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make request to trade-in vehicle: %s, %s, %s, %s, %s, %s', self.item, self.itemToTradeOff, self.buyShell, self.buyCrew, self.crewType, self.price)
        BigWorld.player().shop.tradeInVehicle(self.itemToTradeOff.invID, self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, lambda code: self._response(code, callback))


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
        return makeI18nSuccess(sysMsgKey='vehicle_slot_buy/success', money=money, type=SM_TYPE.FinancialTransactionWithGold)

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

    def __init__(self, vehicle, shells=None, eqs=None, optDevs=None, inventory=None, customizationItems=None, isCrewDismiss=False):
        shells = shells or []
        eqs = eqs or []
        optDevs = optDevs or []
        inventory = inventory or []
        customizationItems = customizationItems or []
        self.vehicle = vehicle
        self.shells = shells
        self.eqs = eqs
        self.optDevs = optDevs
        self.inventory = inventory
        self.customizationItems = customizationItems
        self.gainMoney, self.spendMoney = self.__getGainSpendMoney(vehicle, shells, eqs, optDevs, inventory, customizationItems)
        barracksBerthsNeeded = len([ item for item in vehicle.crew if item[1] is not None ])
        bufferOverflowCtx = {}
        isBufferOverflowed = False
        crewSkinsNeedDeletion = []
        self.__compensationAmount = ItemPrice(Money(), Money())
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
            if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
                freeCountByItem = {}
                for _, tankman in vehicle.crew:
                    if tankman is not None and tankman.skinID != NO_CREW_SKIN_ID:
                        crewSkinItem = self.itemsCache.items.getCrewSkin(tankman.skinID)
                        if freeCountByItem.setdefault(crewSkinItem.getID(), crewSkinItem.getFreeCount()) < crewSkinItem.getMaxCount():
                            freeCountByItem[crewSkinItem.getID()] += 1
                        else:
                            crewSkinsNeedDeletion.append(crewSkinItem)
                            self.__compensationAmount += crewSkinItem.getBuyPrice()

        self.__compensationRequired = bool(crewSkinsNeedDeletion)
        plugins = [proc_plugs.VehicleValidator(vehicle, False, prop={'isBroken': True,
          'isLocked': True}),
         proc_plugs.VehicleSellValidator(vehicle),
         proc_plugs.MoneyValidator(self.spendMoney - self.gainMoney),
         proc_plugs.VehicleSellsLeftValidator(vehicle, not (vehicle.isRented and vehicle.rentalIsOver)),
         proc_plugs.BarracksSlotsValidator(barracksBerthsNeeded, isEnabled=not isCrewDismiss),
         proc_plugs.BufferOverflowConfirmator(bufferOverflowCtx, isEnabled=isBufferOverflowed),
         _getUniqueVehicleSellConfirmator(vehicle)]
        if self.lobbyContext.getServerSettings().isCrewSkinsEnabled():
            ctx = {'price': self.__compensationAmount,
             'action': None,
             'items': crewSkinsNeedDeletion}
            skinsPlugin = proc_plugs.CrewSkinsCompensationDialogConfirmator('crewSkins/skinWillBeDeleted', proc_plugs.CrewSkinsRemovalCompensationDialogMeta.OUT_OF_STORAGE_SUFFIX, ctx=ctx, isEnabled=bool(crewSkinsNeedDeletion))
            plugins.append(skinsPlugin)
        super(VehicleSeller, self).__init__(vehicle, plugins)
        self.isCrewDismiss = isCrewDismiss
        self.isDismantlingForMoney = len(getDismantlingToInventoryDevices(vehicle, optDevs)) > 0
        self.isRemovedAfterRent = vehicle.isRented
        return

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
        compMsg = None
        if self.__compensationRequired:
            compMsg = makeCrewSkinCompensationMessage(self.__compensationAmount)
        if self.isDismantlingForMoney:
            localKey = 'vehicle_sell/success_dismantling'
            smType = SM_TYPE.Selling
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/success_dismantling'
                smType = SM_TYPE.Remove
            return makeI18nSuccess(sysMsgKey=localKey, vehName=self.vehicle.userName, gainMoney=formatPrice(self.gainMoney), spendMoney=formatPrice(self.spendMoney), restoreInfo=restoreInfo, type=smType, auxData=compMsg)
        else:
            localKey = 'vehicle_sell/success'
            if not sellForGold:
                smType = SM_TYPE.Selling
            else:
                smType = SM_TYPE.SellingForGold
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/success'
                smType = SM_TYPE.Remove
            return makeI18nSuccess(sysMsgKey=localKey, vehName=self.vehicle.userName, money=formatPrice(self.gainMoney), restoreInfo=restoreInfo, type=smType, auxData=compMsg)
            return

    def _request(self, callback):
        itemsFromVehicle = list()
        itemsFromInventory = list()
        customizationItems = list()
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

        _logger.debug('Make server request: %s, %s, %s, %s, %s, %s, %s, %s, %s', self.vehicle.invID, isSellShells, isSellEqs, isSellFromInv, isSellOptDevs, self.isDismantlingForMoney, self.isCrewDismiss, itemsFromVehicle, itemsFromInventory)
        BigWorld.player().inventory.sellVehicle(self.vehicle.invID, self.isCrewDismiss, itemsFromVehicle, itemsFromInventory, customizationItems, lambda code: self._response(code, callback))

    def __getGainSpendMoney(self, vehicle, vehShells, vehEqs, optDevicesToSell, inventory, customizationItems):
        moneyGain = vehicle.sellPrices.itemPrice.price
        for shell in vehShells:
            moneyGain += shell.sellPrices.itemPrice.price * shell.count

        for module in vehEqs + optDevicesToSell:
            moneyGain += module.sellPrices.itemPrice.price

        for module in inventory + customizationItems:
            moneyGain += module.sellPrices.itemPrice.price * module.inventoryCount

        for module in customizationItems:
            moneyGain += module.sellPrices.itemPrice.price * module.getInstalledOnVehicleCount(self.vehicle.intCD)

        dismantlingToInventoryDevices = getDismantlingToInventoryDevices(vehicle, optDevicesToSell)
        moneySpend = calculateSpendMoney(self.itemsCache.items, dismantlingToInventoryDevices)
        return (moneyGain, moneySpend)

    def __accumulatePrice(self, result, price, count=1):
        result += price * count
        return result


def getDismantlingToInventoryDevices(vehicle, optDevicesToSell):
    optDevicesToSell = {dev.intCD for dev in optDevicesToSell}
    vehDevices = vehicle.optDevices if vehicle is not None else []
    return [ dev for dev in vehDevices if dev and not dev.isRemovable and dev.intCD not in optDevicesToSell ]


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


class VehicleTmenXPAccelerator(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleTmenXPAccelerator, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.XP_TO_TMAN, value, (proc_plugs.MessageConfirmator('xpToTmenCheckbox', isEnabled=value),))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='vehicle_tmenxp_accelerator/{}'.format(errStr), defaultSysMsgKey='vehicle_tmenxp_accelerator/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='vehicle_tmenxp_accelerator/success' + str(self._value), vehName=self.item.userName, type=SM_TYPE.Information)


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


class VehicleLayoutProcessor(Processor):

    def __init__(self, vehicle, shellsLayoutHelper=None, eqsLayoutHelper=None, skipConfirm=False):
        super(VehicleLayoutProcessor, self).__init__()
        self.vehicle = vehicle
        self.shellsLayoutHelper = shellsLayoutHelper
        self.eqsLayoutHelper = eqsLayoutHelper
        self._setupPlugins(skipConfirm)

    def _setupPlugins(self, skipConfirm):
        shellsPrice = self.getShellsLayoutPrice()
        eqsPrice = self.getEqsLayoutPrice()
        isWalletValidatorEnabled = bool(shellsPrice.gold or eqsPrice.gold)
        self.addPlugins((proc_plugs.VehicleLockValidator(self.vehicle), proc_plugs.WalletValidator(isWalletValidatorEnabled), proc_plugs.VehicleLayoutValidator(shellsPrice, eqsPrice)))

    def _request(self, callback):
        shellsRaw = self.shellsLayoutHelper.getRawLayout() if self.shellsLayoutHelper else None
        eqsRaw = self.eqsLayoutHelper.getRawLayout() if self.eqsLayoutHelper else None
        BigWorld.player().inventory.setAndFillLayouts(self.vehicle.invID, shellsRaw, eqsRaw, self._getEquipmentType(), lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))
        return

    def _getEquipmentType(self):
        return EQUIPMENT_TYPES.regular

    def _getSysMsgType(self, price):
        return CURRENCY_TO_SM_TYPE.get(price.getCurrency(byWeight=False), SM_TYPE.Information)

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        if ctx.get('shells', []):
            totalPrice = MONEY_UNDEFINED
            for shellCompDescr, price, count in ctx.get('shells', []):
                price = Money.makeFromMoneyTuple(price)
                shell = self.itemsCache.items.getItemByCD(shellCompDescr)
                additionalMessages.append(makeI18nSuccess('shell_buy/success', name=shell.userName, count=count, money=formatPrice(price), type=self._getSysMsgType(price)))
                totalPrice += price

            additionalMessages.append(makeI18nSuccess('layout_apply/success_money_spent', money=formatPrice(totalPrice), type=self._getSysMsgType(totalPrice)))
        if ctx.get('eqs', []):
            for eqCompDescr, price, count in ctx.get('eqs', []):
                price = Money.makeFromMoneyTuple(price)
                equipment = self.itemsCache.items.getItemByCD(eqCompDescr)
                additionalMessages.append(makeI18nSuccess(sysMsgKey='artefact_buy/success', kind=equipment.userType, name=equipment.userName, count=count, money=formatPrice(price), type=self._getSysMsgType(price)))

        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            msg = 'server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'server_error_centerDown'
        else:
            msg = errStr
        return makeI18nError(sysMsgKey='layout_apply/{}'.format(msg), defaultSysMsgKey='layout_apply/server_error', vehName=self.vehicle.userName, type=SM_TYPE.Error)

    def getShellsLayoutPrice(self):
        if self.shellsLayoutHelper is None:
            return MONEY_UNDEFINED
        else:
            price = MONEY_UNDEFINED
            if g_bootcamp.isRunning():
                return price
            for shellCompDescr, count, isBuyingForAltPrice in LayoutIterator(self.shellsLayoutHelper.getRawLayout()):
                if not shellCompDescr or not count:
                    continue
                shell = self.itemsCache.items.getItemByCD(int(shellCompDescr))
                vehShell = findFirst(lambda s, intCD=shellCompDescr: s.intCD == intCD, self.vehicle.shells)
                vehCount = vehShell.count if vehShell is not None else 0
                buyCount = count - shell.inventoryCount - vehCount
                if buyCount:
                    itemPrice = shell.buyPrices.itemAltPrice if isBuyingForAltPrice else shell.buyPrices.itemPrice
                    buyPrice = buyCount * itemPrice.price
                    price += buyPrice

            return price

    def getEqsLayoutPrice(self):
        if self.eqsLayoutHelper is None:
            return MONEY_UNDEFINED
        else:
            price = MONEY_UNDEFINED
            regularEqsLayout = self.eqsLayoutHelper.getRegularRawLayout()
            for idx, (eqCompDescr, count, isBuyingForAltPrice) in enumerate(LayoutIterator(regularEqsLayout)):
                if not eqCompDescr or not count:
                    continue
                equipment = self.itemsCache.items.getItemByCD(int(eqCompDescr))
                vehEquipment = self.vehicle.equipment.regularConsumables[idx]
                vehCount = 1 if vehEquipment is not None else 0
                buyCount = count - equipment.inventoryCount - vehCount
                if buyCount:
                    itemPrice = equipment.buyPrices.itemAltPrice if isBuyingForAltPrice else equipment.buyPrices.itemPrice
                    buyPrice = buyCount * itemPrice.price
                    price += buyPrice

            return price


class VehicleBattleBoosterLayoutProcessor(VehicleLayoutProcessor):

    def __init__(self, vehicle, battleBooster, eqsLayout, skipConfirm=False):
        self.battleBooster = battleBooster
        super(VehicleBattleBoosterLayoutProcessor, self).__init__(vehicle, None, eqsLayout, skipConfirm)
        return

    def _setupPlugins(self, skipConfirm):
        if self.battleBooster:
            self.addPlugin(proc_plugs.BattleBoosterConfirmator('confirmBattleBoosterInstall', 'confirmBattleBoosterInstallNotSuitable', self.vehicle, self.battleBooster, isEnabled=not skipConfirm))

    def _getEquipmentType(self):
        return EQUIPMENT_TYPES.battleBoosters


class BuyAndInstallBattleBoosterProcessor(VehicleBattleBoosterLayoutProcessor):

    def __init__(self, vehicle, battleBooster, eqsLayout, count, skipConfirm=False):
        self.count = count
        super(BuyAndInstallBattleBoosterProcessor, self).__init__(vehicle, battleBooster, eqsLayout, skipConfirm)

    def _setupPlugins(self, skipConfirm):
        itemPrice = self.battleBooster.buyPrices.getSum().price
        self.addPlugins((proc_plugs.MoneyValidator(itemPrice * self.count), proc_plugs.BattleBoosterConfirmator('confirmBattleBoosterBuyAndInstall', 'confirmBattleBoosterInstallNotSuitable', self.vehicle, self.battleBooster, isEnabled=not skipConfirm)))

    def _request(self, callback):
        BigWorld.player().shop.buy(self.battleBooster.itemTypeID, self.battleBooster.nationID, self.battleBooster.intCD, self.count, 0, lambda code: self._buyResponse(code, callback))

    def _buyResponse(self, code, callback):
        _logger.debug('Server response on buy battle booster: %s', code)
        if code < 0:
            return callback(self._errorHandler(code))
        price = self.battleBooster.getBuyPrice().price
        price *= self.count
        message = makeI18nSuccess(sysMsgKey='battleBooster_buy/success', kind=self.battleBooster.userType, name=self.battleBooster.userName, count=self.count, money=formatPrice(price), type=self._getSysMsgType(price))
        SystemMessages.pushI18nMessage(message.userMsg, type=message.sysMsgType)
        super(BuyAndInstallBattleBoosterProcessor, self)._request(callback)


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
    for shell in vehicle.shells:
        if shell.defaultCount > shell.inventoryCount:
            SystemMessages.pushI18nMessage('#system_messages:charge/inventory_error', vehicle=vehicle.userName, type=SystemMessages.SM_TYPE.Warning)
            yield lambda callback: callback(None)
            break
        defaultLayout.extend(shell.defaultLayoutValue)
    else:
        shellsLayoutHelper = ShellLayoutHelper(vehicle, defaultLayout)
        result = yield VehicleLayoutProcessor(vehicle, shellsLayoutHelper).request()
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
