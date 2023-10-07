# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_sell_dialog.py
import typing
from account_helpers.AccountSettings import AccountSettings
from goodies.goodie_constants import GOODIE_VARIETY
from gui import SystemMessages, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.customization.shared import TYPES_ORDER
from gui.Scaleform.daapi.view.meta.VehicleSellDialogMeta import VehicleSellDialogMeta
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.goodies.demount_kit import isDemountKitApplicableTo, getDemountKitForOptDevice
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.shared.formatters import text_styles, getRoleTextWithLabel
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getCrewCount
from gui.shared.gui_items.processors import plugins
from gui.shared.gui_items.processors.vehicle import VehicleSeller, getCustomizationItemSellCountForVehicle
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils import decorators
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shop import showBuyGoldForEquipment
from helpers import int2roman, dependency
from items import ITEM_TYPES
from items.components.c11n_constants import ItemTags
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from post_progression_common import TankSetupGroupsId
from skeletons.gui.game_control import IRestoreController, IWotPlusController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Set, Iterator, Optional, Tuple, Dict, Union, Any
    from gui.game_control.wot_plus_controller import WotPlusController
    from gui.shared.gui_items.fitting_item import FittingItem
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.artefacts import OptionalDevice, BattleBooster
    from gui.shared.gui_items.vehicle_modules import Shell
    from gui.shared.gui_items.customization.c11n_items import Customization
    from gui.shared.gui_items.gui_item import GUIItem
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.money import Money
    from helpers.server_settings import ServerSettings
_DK_CURRENCY = GOODIE_VARIETY.DEMOUNT_KIT_NAME
_WP_CURRENCY = 'wotPlusVSD'
_SETTINGS_KEY = 'vehicleSellDialog'
_SETTINGS_OPEN_ENTRY = 'isOpened'
_INVENTORY_SHELLS = 'inventoryShells'
_BARRACKS_DROP_DOWN_DATA_PROVIDER = [{'label': R.strings.menu.barracks.btnUnload()}, {'label': R.strings.menu.barracks.btnDissmiss()}]

class VehicleSellDialog(VehicleSellDialogMeta):
    __itemsCache = dependency.descriptor(IItemsCache)
    __restore = dependency.descriptor(IRestoreController)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __wotPlus = dependency.descriptor(IWotPlusController)
    __slots__ = ('__vehInvID', '__vehicle', '__nationGroupVehicles', '__controlNumber', '__enteredControlNumber', '__income', '__accountMoney', '__isCrewDismissal', '__vehicleSellPrice', '__items', '__otherVehicleShells', '__isDemountKitEnabled')

    def __init__(self, ctx=None):
        super(VehicleSellDialog, self).__init__()
        self.__vehInvID = ctx.get('vehInvID', 0)
        self.__vehicle = None
        self.__nationGroupVehicles = list()
        self.__controlNumber = None
        self.__enteredControlNumber = None
        self.__income = _VSDMoney()
        self.__accountMoney = _VSDMoney()
        self.__isCrewDismissal = False
        self.__vehicleSellPrice = MONEY_UNDEFINED
        self.__items = list()
        self.__otherVehicleShells = set()
        self.__isDemountKitEnabled = False
        return

    def onSelectionChanged(self, itemID, toInventory, currency):
        item = self.__items[itemID]
        item.toInventory = toInventory
        item.removeCurrency = currency
        self.__updateTotalCost()
        self.__updateSubmitButton()

    def setCrewDismissal(self, checkTankman):
        self.__isCrewDismissal = checkTankman
        if self.__useCtrlQuestion:
            self.__sendControlQuestion()
            self.as_visibleControlBlockS(True)
            self.setUserInput('')
        else:
            self.as_visibleControlBlockS(False)
            self.setUserInput(self.__controlNumber)

    def setUserInput(self, userInput):
        self.__enteredControlNumber = userInput
        self.__updateSubmitButton()

    def sell(self):
        shells = []
        eqs = []
        optDevicesToSell = []
        inventory = []
        customizationItems = []
        boosters = []
        sellMap = {FITTING_TYPES.SHELL: shells,
         _INVENTORY_SHELLS: inventory,
         FITTING_TYPES.EQUIPMENT: eqs,
         FITTING_TYPES.OPTIONAL_DEVICE: optDevicesToSell,
         FITTING_TYPES.MODULE: inventory,
         FITTING_TYPES.CUSTOMIZATION: customizationItems,
         FITTING_TYPES.BOOSTER: boosters}
        itemsForDemountKit = []
        itemsForFreeDemount = []
        for item in self.__items:
            guiItem = item.guiItem
            if item.toInventory:
                if guiItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.removeCurrency == _DK_CURRENCY:
                    itemsForDemountKit.append(guiItem)
                if guiItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.removeCurrency == _WP_CURRENCY:
                    itemsForFreeDemount.append(guiItem)
            container = sellMap[item.itemType]
            container.append(guiItem)

        self.__doSellVehicle(self.__vehicle, shells, eqs, optDevicesToSell, inventory, customizationItems, self.__isCrewDismissal, itemsForDemountKit, itemsForFreeDemount, boosters)

    def onWindowClose(self):
        self.destroy()

    def setDialogSettings(self, isOpened):
        _setSlidingComponentOpened(isOpened)

    def _populate(self):
        super(VehicleSellDialog, self)._populate()
        self.__subscribe()
        vehInvID = self.__vehInvID
        self.__items = list()
        self.__vehicle = self.__itemsCache.items.getVehicle(vehInvID)
        self.__nationGroupVehicles = self.__getNationGroupVehicles(self.__vehicle.intCD)
        self.__otherVehicleShells = self.__getOtherVehiclesShells(vehInvID)
        self.__vehicleSellPrice = self.__vehicle.sellPrices.itemPrice.price
        self.__accountMoney = _VSDMoney(self.__itemsCache.items.stats.money)
        if self.__getIsDemountKitEnabled():
            for optDevice in self.__vehicle.optDevices.setupLayouts.getUniqueItems():
                if optDevice is not None and not optDevice.isRemovable:
                    demountKit, currency = getDemountKitForOptDevice(optDevice)
                    if demountKit is not None and currency == Currency.GOLD:
                        self.__accountMoney[_DK_CURRENCY] = demountKit.inventoryCount

            self.__isDemountKitEnabled = True
        if self.__wotPlus.isEnabled():
            devicesSlotsNumber = self.__vehicle.descriptor.supplySlots.getAmountForType(ITEM_TYPES.optionalDevice)
            if self.__vehicle.isSetupSwitchActive(TankSetupGroupsId.EQUIPMENT_AND_SHELLS):
                devicesSlotsNumber *= 2
            self.__accountMoney[_WP_CURRENCY] = devicesSlotsNumber
        optionalDevicesOnVehicle = []
        shellsOnVehicle = []
        equipmentsOnVehicle = []
        battleBoostersOnVehicle = []
        customizationOnVehicle = []
        currentBalance = _VSDMoney(self.__accountMoney)
        for vehicle in self.__nationGroupVehicles:
            onVehicleOptionalDevices, currentBalance = self.__prepareVehicleOptionalDevices(vehicle, currentBalance)
            optionalDevicesOnVehicle.extend(onVehicleOptionalDevices)
            shellsOnVehicle.extend(self.__prepareOnVehicleShells(vehicle))
            equipmentsOnVehicle.extend(self.__prepareVehicleEquipments(vehicle))
            battleBoostersOnVehicle.extend(self.__prepareVehicleBoosters(vehicle))
            customizationOnVehicle.extend(self.__prepareVehicleCustomizations(vehicle))

        data = {'accountMoney': self.__accountMoney.toDict(),
         'sellVehicleVO': self.__getSellVehicleData(),
         'modulesInInventory': self.__prepareInventoryModules(),
         'shellsInInventory': self.__prepareInventoryShells(),
         'isSlidingComponentOpened': _getSlidingComponentOpened(),
         'optionalDevicesOnVehicle': optionalDevicesOnVehicle,
         'shellsOnVehicle': shellsOnVehicle,
         'equipmentsOnVehicle': equipmentsOnVehicle,
         'battleBoostersOnVehicle': battleBoostersOnVehicle,
         'customizationOnVehicle': customizationOnVehicle}
        self.as_setDataS(data)
        self.__updateTotalCost()
        self.setCrewDismissal(self.__isCrewDismissal)
        return

    def _dispose(self):
        super(VehicleSellDialog, self)._dispose()
        self.__unsubscribe()

    def __getCrewData(self):
        tankmenGoingToBuffer, deletedTankmen = self.__restore.getTankmenDeletedBySelling(*self.__nationGroupVehicles)
        deletedCount = len(deletedTankmen)
        if deletedCount > 0:
            deletedStr = formatDeletedTankmanStr(deletedTankmen[0])
            maxCount = self.__restore.getMaxTankmenBufferLength()
            currCount = len(self.__restore.getDismissedTankmen())
            header = backport.text(R.strings.tooltips.vehicleSellDialog.crew.alertIcon.recovery.header())
            if deletedCount == 1:
                crewTooltip = text_styles.concatStylesToMultiLine(text_styles.middleTitle(header), text_styles.main(backport.text(R.strings.tooltips.vehicleSellDialog.crew.alertIcon.recovery.body(), maxVal=maxCount, curVal=currCount, sourceName=tankmenGoingToBuffer[-1].fullUserName, targetInfo=deletedStr)))
            else:
                crewTooltip = text_styles.concatStylesToMultiLine(text_styles.middleTitle(header), text_styles.main(backport.text(R.strings.tooltips.dismissTankmanDialog.bufferIsFullMultiple.body(), deletedStr=deletedStr, extraCount=deletedCount - 1, maxCount=maxCount, currCount=currCount)))
        else:
            crewTooltip = None
        if self.__vehicle.isCrewLocked:
            hasCrew = False
        else:
            hasCrew = any([ veh.hasCrew for veh in self.__nationGroupVehicles ])
        return (hasCrew, crewTooltip)

    def __addVSDItem(self, item):
        item.setItemID(len(self.__items))
        self.__items.append(item)

    def __getSellVehicleData(self):
        sellCurrency = self.__vehicleSellPrice.getCurrency(byWeight=True)
        sellForGold = sellCurrency == Currency.GOLD
        priceTextColor = CURRENCIES_CONSTANTS.GOLD_COLOR if sellForGold else CURRENCIES_CONSTANTS.CREDITS_COLOR
        add = backport.text(R.strings.dialogs.vehicleSellDialog.price.sign.add())
        priceTextValue = add + backport.getIntegralFormat(self.__vehicleSellPrice.getSignValue(sellCurrency))
        currencyIcon = CURRENCIES_CONSTANTS.GOLD if sellForGold else CURRENCIES_CONSTANTS.CREDITS
        vehicleAction = None
        if self.__vehicle.sellPrices.itemPrice.isActionPrice():
            vehicleAction = packItemActionTooltipData(self.__vehicle, False)
        vehType = self.__vehicle.type
        levelText = backport.text(R.strings.dialogs.vehicleSellDialog.vehicle.level())
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(self.__vehicle.level)), text_styles.main(levelText))
        if self.__vehicle.isElite:
            description = backport.text(R.strings.tooltips.tankCaruselTooltip.vehicleType.elite.dyn(vehType.replace('-', '_'))())
        else:
            description = backport.text(R.strings.dialogs.vehicleSellDialog.vehicleType.dyn(vehType.replace('-', '_'))())
        description = text_styles.concatStylesToSingleLine(levelStr, description)
        roleStr = getRoleTextWithLabel(self.__vehicle.role, self.__vehicle.roleLabel)
        hasCrew, crewTooltip = self.__getCrewData()
        barracksDropDownData = []
        for buttons in _BARRACKS_DROP_DOWN_DATA_PROVIDER:
            barracksDropDownData.append({key:backport.text(value) for key, value in buttons.iteritems()})

        return {'intCD': self.__vehicle.intCD,
         'userName': self.__vehicle.userName,
         'icon': self.__vehicle.icon,
         'level': self.__vehicle.level,
         'isElite': self.__vehicle.isElite,
         'isPremium': self.__vehicle.isPremium,
         'hasNationGroup': self.__vehicle.hasNationGroup,
         'type': vehType,
         'nationID': self.__vehicle.nationID,
         'sellPrice': self.__vehicleSellPrice.toMoneyTuple(),
         'priceTextValue': priceTextValue,
         'priceTextColor': priceTextColor,
         'currencyIcon': currencyIcon,
         'action': vehicleAction,
         'hasCrew': hasCrew,
         'isRented': self.__vehicle.isRented,
         'description': description,
         'roleStr': roleStr,
         'priceLabel': backport.text(R.strings.dialogs.vehicleSellDialog.vehicle.emptySellPrice()),
         'crewLabel': backport.text(R.strings.dialogs.vehicleSellDialog.crew.label()),
         'inNationGroupDescription': backport.text(R.strings.dialogs.vehicleSellDialog.message.multinational()),
         'crewTooltip': crewTooltip,
         'barracksDropDownData': barracksDropDownData,
         'isPostProgressionUnlocked': self.__vehicle.postProgressionAvailability(unlockOnly=True).result}

    def __prepareInventoryModules(self):
        moduleList = self.__itemsCache.items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE(self.__nationGroupVehicles) | REQ_CRITERIA.INVENTORY).values()
        inInventoryModules = []
        for module in moduleList:
            data = _ModulesData(module)
            self.__addVSDItem(data)
            inInventoryModules.append(data.toFlashVO())

        return inInventoryModules

    def __prepareVehicleOptionalDevices(self, vehicle, currentBalance):
        onVehicleOptionalDevices = []
        for optDevice in vehicle.optDevices.setupLayouts.getUniqueItems():
            data = _OptionalDeviceData(optDevice)
            removeCurrency = _findCurrency(currentBalance, data.itemRemovalPrice)
            if removeCurrency is not None:
                currentBalance -= data.itemRemovalPrice.extract(removeCurrency)
            data.removeCurrency = removeCurrency
            self.__addVSDItem(data)
            onVehicleOptionalDevices.append(data.toFlashVO())

        return (onVehicleOptionalDevices, currentBalance)

    def __prepareVehicleEquipments(self, vehicle):
        onVehicleEquipments = []
        for equipment in vehicle.consumables.setupLayouts.getUniqueItems():
            if equipment.isBuiltIn:
                continue
            data = _VSDItemData(equipment, FITTING_TYPES.EQUIPMENT)
            self.__addVSDItem(data)
            onVehicleEquipments.append(data.toFlashVO())

        return onVehicleEquipments

    def __prepareVehicleBoosters(self, vehicle):
        onVehicleBattleBoosters = []
        installedItems = vehicle.battleBoosters.setupLayouts.getUniqueItems()
        for booster in installedItems:
            data = _BoosterData(booster)
            self.__addVSDItem(data)
            onVehicleBattleBoosters.append(data.toFlashVO())

        return onVehicleBattleBoosters

    def __prepareVehicleCustomizations(self, vehicle):
        installedCustomizations = self.__itemsCache.items.getItems(itemTypeID=GUI_ITEM_TYPE.STYLE, criteria=REQ_CRITERIA.CUSTOMIZATION.IS_INSTALLED_ON_VEHICLE(vehicle)).values()
        if not installedCustomizations:
            criteria = REQ_CRITERIA.CUSTOMIZATION.IS_INSTALLED_ON_VEHICLE(vehicle)
            criteria |= ~REQ_CRITERIA.CUSTOMIZATION.HAS_TAGS([ItemTags.NATIONAL_EMBLEM])
            installedCustomizations = self.__itemsCache.items.getItems(itemTypeID=GUI_ITEM_TYPE.CUSTOMIZATIONS, criteria=criteria).itervalues()
            installedCustomizations = sorted(installedCustomizations, key=lambda item: TYPES_ORDER.index(item.itemTypeID))
        customizationOnVehicle = []
        for customization in installedCustomizations:
            count = getCustomizationItemSellCountForVehicle(customization, vehicle.intCD)
            if count:
                data = _CustomizationData(customization, count)
                self.__addVSDItem(data)
                customizationOnVehicle.append(data.toFlashVO())

        return customizationOnVehicle

    def __prepareInventoryShells(self):
        shellList = self.__itemsCache.items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE(self.__nationGroupVehicles, [GUI_ITEM_TYPE.SHELL]) | REQ_CRITERIA.INVENTORY).values()
        inInventoryShells = []
        for shell in shellList:
            data = _ShellData(shell, True, shell.intCD in self.__otherVehicleShells)
            self.__addVSDItem(data)
            inInventoryShells.append(data.toFlashVO())

        return inInventoryShells

    def __prepareOnVehicleShells(self, vehicle):
        onVehicleShells = []
        for shell in vehicle.shells.setupLayouts.getUniqueItems():
            data = _ShellData(shell, False, shell.intCD in self.__otherVehicleShells)
            self.__addVSDItem(data)
            onVehicleShells.append(data.toFlashVO())

        return onVehicleShells

    def __subscribe(self):
        g_clientUpdateManager.addCallbacks({'stats.gold': self.__onSetGoldHandler,
         'stats.crystal': self.__onSetCrystalHandler,
         'stats.equipCoin': self.__onSetEquipCoinHandler,
         'stats.vehicleSellsLeft': self.__onSellLimitUpdate,
         'stats.tankmenBerthsCount': self.__onBerthsCountUpdate,
         'goodies': self.__onSetGoodiesHandler})
        self.__itemsCache.onSyncCompleted += self.__shopResyncHandler

    def __unsubscribe(self):
        self.__itemsCache.onSyncCompleted -= self.__shopResyncHandler
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onSetGoldHandler(self, gold):
        self.__updateMoney(Currency.GOLD, gold)
        self.__updateSubmitButton()

    def __onSetCrystalHandler(self, crystals):
        self.__updateMoney(Currency.CRYSTAL, crystals)
        self.__updateSubmitButton()

    def __onSetEquipCoinHandler(self, equipCoin):
        self.__updateMoney(Currency.EQUIP_COIN, equipCoin)
        self.__updateSubmitButton()

    def __onSellLimitUpdate(self, *_):
        self.__updateSubmitButton()

    def __onBerthsCountUpdate(self, *_):
        self.__updateSubmitButton()

    def __onSetGoodiesHandler(self, goodies):
        demountKitGold = self.__goodiesCache.getDemountKit(currency=Currency.GOLD)
        if demountKitGold is not None and demountKitGold.enabled and demountKitGold.goodieID in goodies:
            self.__updateMoney(_DK_CURRENCY, demountKitGold.inventoryCount)
            self.__updateSubmitButton()
        return

    def __updateMoney(self, currency, value):
        self.__accountMoney[currency] = value
        self.as_updateAccountMoneyS(currency, value)

    def __updateSubmitButton(self):
        controlNumberValid = self.__enteredControlNumber == self.__controlNumber
        expenses = -self.__income
        shortage = expenses.getShortage(self.__accountMoney)
        shortage[Currency.GOLD] = 0
        shortage[_WP_CURRENCY] = 0
        nationGroupVehs = self.__vehicle.getAllNationGroupVehs(self.__itemsCache.items)
        barracksBerthsNeeded = getCrewCount(nationGroupVehs)
        crewValid = True
        if not self.__isCrewDismissal:
            crewValid = plugins.BarracksSlotsValidator(barracksBerthsNeeded).validate().success
        isInLimit = True
        if not (self.__vehicle.isRented and self.__vehicle.rentalIsOver):
            isInLimit = plugins.VehicleSellsLeftValidator(self.__vehicle).validate().success
        tooltip = ''
        acceptButtonTooltip = R.strings.tooltips.vehicleSellDialog.acceptButtonTooltip
        formattedItems = []
        if not shortage.isEmpty():
            formattedItems.append(backport.text(acceptButtonTooltip.notEnoughCurrency.body()))
        if not crewValid:
            formattedItems.append(backport.text(acceptButtonTooltip.notEnoughTankmenBerths.body()))
        if not isInLimit:
            formattedItems.append(backport.text(acceptButtonTooltip.vehicleSellLimit.body()))
        warningMessage = '.\n'.join(formattedItems) + '.'
        if formattedItems:
            header = backport.text(acceptButtonTooltip.notEnable.header())
            tooltip = makeTooltip(header, warningMessage)
        elif not controlNumberValid:
            header = backport.text(acceptButtonTooltip.controlNumberValid.header())
            body = backport.text(acceptButtonTooltip.controlNumberValid.body())
            tooltip = makeTooltip(header, body)
        self.as_enableButtonS(controlNumberValid and shortage.isEmpty() and crewValid and isInLimit, tooltip)
        self.as_setSellEnabledS(shortage.isEmpty() and crewValid and isInLimit, str(warningMessage))

    def __getControlQuestion(self, usingGold=False):
        if usingGold:
            currencyFormatter = backport.getGoldFormat(long(self.__controlNumber))
        else:
            currencyFormatter = backport.getIntegralFormat(long(self.__controlNumber))
        question = makeHtmlString('html_templates:lobby/dialogs', 'vehicleSellQuestion', {'controlNumber': currencyFormatter})
        return question

    def __shopResyncHandler(self, reason, _):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or self.__vehicle.rentalIsActive:
            self.onWindowClose()
            if self.__isDemountKitEnabled != self.__getIsDemountKitEnabled():
                event_dispatcher.showVehicleSellDialog(self.__vehInvID)

    def __updateTotalCost(self):
        optionalDevices = _VSDMoney()
        common = _VSDMoney()
        for item in self.__items:
            if item.toInventory:
                if item.guiItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isRemovableForMoney:
                    currency = item.removeCurrency
                    optionalDevices -= item.itemRemovalPrice.extract(currency)
            if item.guiItem.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                optionalDevices += item.itemSellPrice
            common += item.itemSellPrice

        self.__income = _VSDMoney()
        self.__income += _VSDMoney(self.__vehicleSellPrice)
        self.__income += common
        self.__income += optionalDevices
        self.as_setTotalS(common[Currency.CREDITS], self.__income.toDict())
        if self.__useCtrlQuestion:
            self.__sendControlQuestion()

    def __sendControlQuestion(self):
        credits_ = self.__income[Currency.CREDITS]
        gold = self.__income[Currency.GOLD]
        isGold = credits_ == 0
        controlNumber = gold if isGold else credits_
        self.__controlNumber = str(controlNumber)
        question = self.__getControlQuestion(isGold)
        self.as_setControlQuestionDataS(isGold, self.__controlNumber, question)

    def __getOtherVehiclesShells(self, vehInvID):
        result = set()
        invVehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
        for invVeh in invVehs.itervalues():
            if invVeh.invID != vehInvID:
                for shot in invVeh.descriptor.gun.shots:
                    result.add(shot.shell.compactDescr)

        return result

    def __getIsDemountKitEnabled(self):
        demountKit = self.__goodiesCache.getDemountKit(currency=Currency.GOLD)
        return demountKit is not None and demountKit.enabled

    def __getNationGroupVehicles(self, vehicleCD):
        result = [ self.__itemsCache.items.getItemByCD(cd) for cd in iterVehTypeCDsInNationGroup(vehicleCD) ]
        result.append(self.__vehicle)
        result.sort(reverse=True, key=lambda v: v.activeInNationGroup)
        return result

    @property
    def __useCtrlQuestion(self):
        if self.__vehicle.level >= 3 or self.__vehicle.isPremium:
            return True
        if self.__isCrewDismissal:
            for _, tankman in self.__vehicle.crew:
                if tankman and (tankman.roleLevel >= 100 or tankman.skills):
                    return True

        return False

    @decorators.adisp_process('sellVehicle')
    def __doSellVehicle(self, vehicle, shells, eqs, optDevicesToSell, inventory, customizationItems, isDismissCrew, itemsForDemountKit, itemsForFreeDemount, boosters):
        vehicleSeller = VehicleSeller(vehicle, shells, eqs, optDevicesToSell, inventory, customizationItems, boosters, isDismissCrew, itemsForDemountKit, itemsForFreeDemount)
        currentMoneyGold = self.__itemsCache.items.stats.money.get(Currency.GOLD, 0)
        spendMoneyGold = vehicleSeller.spendMoney.get(Currency.GOLD, 0)
        if currentMoneyGold < spendMoneyGold:
            showBuyGoldForEquipment(spendMoneyGold)
        else:
            result = yield vehicleSeller.request()
            SystemMessages.pushMessagesFromResult(result)
            self.destroy()


def _getDialogSettings():
    return dict(AccountSettings.getSettings(_SETTINGS_KEY))


def _setSlidingComponentOpened(value):
    settings = _getDialogSettings()
    settings[_SETTINGS_OPEN_ENTRY] = value
    AccountSettings.setSettings(_SETTINGS_KEY, settings)


def _getSlidingComponentOpened():
    settings = _getDialogSettings()
    return settings[_SETTINGS_OPEN_ENTRY]


def _getCurrencyIterator():
    order = (_WP_CURRENCY, _DK_CURRENCY) + Currency.BY_WEIGHT
    for c in order:
        yield c


def _findCurrency(have, price):
    firstCurrency = None
    for c in _getCurrencyIterator():
        value = price[c]
        if value:
            firstCurrency = firstCurrency or c
            if have[c] >= value:
                return c

    return firstCurrency


class _VSDMoney(dict):

    def __init__(self, money=None, **kwargs):
        super(_VSDMoney, self).__init__()
        if money:
            for c, v in money.iteritems():
                self[c] = v

        for currency, value in kwargs.iteritems():
            self[currency] = value

    def toDict(self):
        return {c:v for c, v in self.iteritems()}

    def __getitem__(self, currency):
        return self.get(currency, 0)

    def __add__(self, other):
        copy = _VSDMoney(self)
        for c, v in other.iteritems():
            copy[c] += v

        return copy

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        copy = _VSDMoney(self)
        for c, v in other.iteritems():
            copy[c] -= v

        return copy

    def __isub__(self, other):
        return self.__sub__(other)

    def __neg__(self):
        return _VSDMoney({c:-v for c, v in self.iteritems()})

    def __mul__(self, n):
        return _VSDMoney({c:v * n for c, v in self.iteritems()})

    def __rmul__(self, n):
        return self.__mul__(n)

    def extract(self, currency):
        return _VSDMoney() if not currency else _VSDMoney(**{currency: self[currency]})

    def isEmpty(self):
        for c in self.values():
            if c != 0:
                return False

        return True

    def getShortage(self, have):
        return _VSDMoney({c:v - have[c] for c, v in self.iteritems() if v > have[c]})


class _VSDItemData(object):
    __slots__ = ('_itemSellPrice', '_itemRemovalPrice', '_flashData', '__fittingItem', '__itemType')

    def __init__(self, item, itemType=None):
        super(_VSDItemData, self).__init__()
        self.__fittingItem = item
        self._itemRemovalPrice = None
        self.__itemType = itemType
        itemPrice = item.sellPrices.itemPrice
        self._itemSellPrice = _VSDMoney(item.sellPrices.itemPrice.price)
        self._flashData = {'count': 1,
         'toInventory': True,
         'userName': item.userName,
         'sellPrice': itemPrice.price.toMoneyTuple()}
        if itemPrice.isActionPrice():
            self._flashData['action'] = packItemActionTooltipData(item, False)
        return

    def toFlashVO(self):
        return self._flashData

    def setItemID(self, value):
        self._flashData['itemID'] = value

    @property
    def itemSellPrice(self):
        return self._itemSellPrice * self._flashData['count']

    @property
    def itemRemovalPrice(self):
        return self._itemRemovalPrice

    @property
    def guiItem(self):
        return self.__fittingItem

    @property
    def toInventory(self):
        return self._flashData['toInventory']

    @toInventory.setter
    def toInventory(self, value):
        self._flashData['toInventory'] = value

    @property
    def removeCurrency(self):
        return self._flashData.get('removeCurrency', None)

    @removeCurrency.setter
    def removeCurrency(self, value):
        self._flashData['removeCurrency'] = value

    @property
    def isRemovableForMoney(self):
        return not self._flashData.get('isRemovable', True)

    @property
    def itemType(self):
        return self.__itemType


class _ShellData(_VSDItemData):
    __slots__ = ()

    def __init__(self, shell, inInventory, onOtherVehicle):
        super(_ShellData, self).__init__(shell, _INVENTORY_SHELLS if inInventory else FITTING_TYPES.SHELL)
        self._flashData['kind'] = shell.type
        self._flashData['count'] = shell.inventoryCount if inInventory else shell.count
        self.toInventory = onOtherVehicle or shell.isPremium


class _BoosterData(_VSDItemData):
    __slots__ = ()

    def __init__(self, booster):
        super(_BoosterData, self).__init__(booster, FITTING_TYPES.BOOSTER)
        if not booster.isForSale:
            self._flashData['sellPrice'] = MONEY_UNDEFINED.toMoneyTuple()
            self._flashData['onlyToInventory'] = True


class _CustomizationData(_VSDItemData):
    __slots__ = ()

    def __init__(self, customization, count):
        super(_CustomizationData, self).__init__(customization, FITTING_TYPES.CUSTOMIZATION)
        self._flashData['onlyToInventory'] = customization.isRentable or customization.isHidden
        self._flashData['count'] = count


class _ModulesData(_VSDItemData):
    __slots__ = ()

    def __init__(self, module):
        super(_ModulesData, self).__init__(module, FITTING_TYPES.MODULE)
        self._flashData['count'] = module.inventoryCount


_DEMOUNT_KIT_ONE = _VSDMoney(**{_DK_CURRENCY: 1})
_WOT_PLUS_ONE = _VSDMoney(**{_WP_CURRENCY: 1})

class _OptionalDeviceData(_VSDItemData):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __wotPlus = dependency.descriptor(IWotPlusController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, optDevice):
        super(_OptionalDeviceData, self).__init__(optDevice, FITTING_TYPES.OPTIONAL_DEVICE)
        isWotPlusEnabled = self.__wotPlus.isWotPlusEnabled()
        self._flashData['isRemovable'] = optDevice.isRemovable
        self._flashData['isModernized'] = optDevice.isModernized
        self._flashData['isWotPlusEnabled'] = isWotPlusEnabled
        removalPrice = optDevice.getRemovalPrice(self.__itemsCache.items)
        if removalPrice.isActionPrice():
            self._flashData['removeActionPrice'] = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'paidRemovalCost', True, removalPrice.price, removalPrice.defPrice)
        serverSettings = self.__lobbyContext.getServerSettings()
        isFreeEquipmentDemountingEnabled = serverSettings.isFreeEquipmentDemountingEnabled()
        if isFreeEquipmentDemountingEnabled and isWotPlusEnabled and self.__wotPlus.isFreeToDemount(optDevice):
            self._itemRemovalPrice = _WOT_PLUS_ONE
        else:
            self._itemRemovalPrice = _VSDMoney(removalPrice.price)
            if isDemountKitApplicableTo(optDevice):
                self._itemRemovalPrice += _DEMOUNT_KIT_ONE
        self._flashData['removePrice'] = self._itemRemovalPrice.toDict()
        self._flashData['alertIconDataID'] = self.__getAlertIconTooltip(optDevice)

    @classmethod
    def __getAlertIconTooltip(cls, optDevice):
        return '#tooltips:vehicleSellDialog/renderer/alertIconSell' if not optDevice.isModernized else '#tooltips:vehicleSellDialog/renderer/alertIconDeconstruct'
