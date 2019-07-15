# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleSellDialog.py
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import SystemMessages, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.customization.shared import TYPES_ORDER
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.VehicleSellDialogMeta import VehicleSellDialogMeta
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.ingame_shop import showBuyGoldForEquipment
from gui.shared.formatters import text_styles
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.vehicle import VehicleSeller, calculateSpendMoney, getDismantlingToInventoryDevices
from gui.shared.gui_items.vehicle_modules import Shell
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils import decorators, flashObject2Dict
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import int2roman, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache

class VehicleSellDialog(VehicleSellDialogMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, ctx=None):
        super(VehicleSellDialog, self).__init__()
        self.__vehInvID = ctx.get('vehInvID', {})
        self.__controlNumber = None
        self.__spendMoney = MONEY_UNDEFINED
        self.__checkUsefulTankman = False
        return

    def onWindowClose(self):
        self.destroy()

    def getDialogSettings(self):
        return dict(AccountSettings.getSettings('vehicleSellDialog'))

    def setDialogSettings(self, isOpened):
        settings = self.getDialogSettings()
        settings['isOpened'] = isOpened
        AccountSettings.setSettings('vehicleSellDialog', settings)

    def _populate(self):
        super(VehicleSellDialog, self)._populate()
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.onSetGoldHndlr)
        self.itemsCache.onSyncCompleted += self.__shopResyncHandler
        items = self.itemsCache.items
        vehicle = items.getVehicle(self.__vehInvID)
        sellPrice = vehicle.sellPrices.itemPrice.price
        sellCurrency = sellPrice.getCurrency(byWeight=True)
        sellForGold = sellCurrency == Currency.GOLD
        priceTextColor = CURRENCIES_CONSTANTS.GOLD_COLOR if sellForGold else CURRENCIES_CONSTANTS.CREDITS_COLOR
        priceTextValue = _ms(DIALOGS.VEHICLESELLDIALOG_PRICE_SIGN_ADD) + _ms(backport.getIntegralFormat(sellPrice.getSignValue(sellCurrency)))
        currencyIcon = CURRENCIES_CONSTANTS.GOLD if sellForGold else CURRENCIES_CONSTANTS.CREDITS
        invVehs = items.getVehicles(REQ_CRITERIA.INVENTORY)
        self.checkControlQuestion(self.__checkUsefulTankman)
        modules = items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE([vehicle]) | REQ_CRITERIA.INVENTORY).values()
        shells = items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.SHELL]) | REQ_CRITERIA.INVENTORY).values()
        installedCustomizations = items.getItems(itemTypeID=GUI_ITEM_TYPE.STYLE, criteria=REQ_CRITERIA.CUSTOMIZATION.IS_INSTALLED_ON_VEHICLE(vehicle)).values()
        if not installedCustomizations:
            installedCustomizations = items.getItems(itemTypeID=GUI_ITEM_TYPE.CUSTOMIZATIONS, criteria=REQ_CRITERIA.CUSTOMIZATION.IS_INSTALLED_ON_VEHICLE(vehicle)).itervalues()
            installedCustomizations = sorted(installedCustomizations, key=lambda item: TYPES_ORDER.index(item.itemTypeID))
        otherVehsShells = set()
        for invVeh in invVehs.itervalues():
            if invVeh.invID != self.__vehInvID:
                for shot in invVeh.descriptor.gun.shots:
                    otherVehsShells.add(shot.shell.compactDescr)

        vehicleAction = None
        if vehicle.sellPrices.itemPrice.isActionPrice():
            vehicleAction = packItemActionTooltipData(vehicle, False)
        if vehicle.isElite:
            description = TOOLTIPS.tankcaruseltooltip_vehicletype_elite(vehicle.type)
        else:
            description = DIALOGS.vehicleselldialog_vehicletype(vehicle.type)
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(vehicle.level)), text_styles.main(_ms(DIALOGS.VEHICLESELLDIALOG_VEHICLE_LEVEL)))
        tankmenGoingToBuffer, deletedTankmen = self.restore.getTankmenDeletedBySelling(vehicle)
        deletedCount = len(deletedTankmen)
        if deletedCount > 0:
            deletedStr = formatDeletedTankmanStr(deletedTankmen[0])
            maxCount = self.restore.getMaxTankmenBufferLength()
            currCount = len(self.restore.getDismissedTankmen())
            if deletedCount == 1:
                crewTooltip = text_styles.concatStylesToMultiLine(text_styles.middleTitle(_ms(TOOLTIPS.VEHICLESELLDIALOG_CREW_ALERTICON_RECOVERY_HEADER)), text_styles.main(_ms(TOOLTIPS.VEHICLESELLDIALOG_CREW_ALERTICON_RECOVERY_BODY, maxVal=maxCount, curVal=currCount, sourceName=tankmenGoingToBuffer[-1].fullUserName, targetInfo=deletedStr)))
            else:
                crewTooltip = text_styles.concatStylesToMultiLine(text_styles.middleTitle(_ms(TOOLTIPS.VEHICLESELLDIALOG_CREW_ALERTICON_RECOVERY_HEADER)), text_styles.main(_ms(TOOLTIPS.DISMISSTANKMANDIALOG_BUFFERISFULLMULTIPLE_BODY, deletedStr=deletedStr, extraCount=deletedCount - 1, maxCount=maxCount, currCount=currCount)))
        else:
            crewTooltip = None
        if vehicle.isCrewLocked:
            hasCrew = False
        else:
            hasCrew = vehicle.hasCrew
        barracksDropDownData = [{'label': _ms(MENU.BARRACKS_BTNUNLOAD)}, {'label': _ms(MENU.BARRACKS_BTNDISSMISS)}]
        sellVehicleData = {'intCD': vehicle.intCD,
         'userName': vehicle.userName,
         'icon': vehicle.icon,
         'level': vehicle.level,
         'isElite': vehicle.isElite,
         'isPremium': vehicle.isPremium,
         'type': vehicle.type,
         'nationID': vehicle.nationID,
         'sellPrice': sellPrice.toMoneyTuple(),
         'priceTextValue': priceTextValue,
         'priceTextColor': priceTextColor,
         'currencyIcon': currencyIcon,
         'action': vehicleAction,
         'hasCrew': hasCrew,
         'isRented': vehicle.isRented,
         'description': description,
         'levelStr': levelStr,
         'priceLabel': _ms(DIALOGS.VEHICLESELLDIALOG_VEHICLE_EMPTYSELLPRICE),
         'crewLabel': _ms(DIALOGS.VEHICLESELLDIALOG_CREW_LABEL),
         'crewTooltip': crewTooltip,
         'barracksDropDownData': barracksDropDownData}
        currentGoldBalance = self.itemsCache.items.stats.money.get(Currency.GOLD, 0)
        onVehicleOptionalDevices = []
        for o in vehicle.optDevices:
            if o is not None:
                itemPrice = o.sellPrices.itemPrice
                action = None
                if itemPrice.isActionPrice():
                    action = packItemActionTooltipData(o, False)
                removalPrice = o.getRemovalPrice(items)
                removeAction = None
                if removalPrice.isActionPrice():
                    removeAction = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'paidRemovalCost', True, removalPrice.price, removalPrice.defPrice)
                removalPriceInGold = removalPrice.price.get(Currency.GOLD, 0)
                enoughGold = currentGoldBalance >= removalPriceInGold
                if enoughGold:
                    currentGoldBalance -= removalPriceInGold
                data = {'intCD': o.intCD,
                 'isRemovable': o.isRemovable,
                 'userName': o.userName,
                 'sellPrice': itemPrice.price.toMoneyTuple(),
                 'toInventory': enoughGold,
                 'action': action,
                 'removePrice': removalPrice.price.toMoneyTuple(),
                 'removeActionPrice': removeAction}
                onVehicleOptionalDevices.append(data)

        onVehicleoShells = []
        for shell in vehicle.shells:
            if shell is not None:
                itemPrice = shell.sellPrices.itemPrice
                action = None
                if itemPrice.isActionPrice():
                    action = packItemActionTooltipData(shell, False)
                data = {'intCD': shell.intCD,
                 'count': shell.count,
                 'sellPrice': itemPrice.price.toMoneyTuple(),
                 'userName': shell.userName,
                 'kind': shell.type,
                 'toInventory': shell in otherVehsShells or shell.isPremium,
                 'action': action}
                onVehicleoShells.append(data)

        onVehicleEquipments = []
        for equipment in vehicle.equipment.regularConsumables.getInstalledItems():
            action = None
            if equipment.isBuiltIn:
                continue
            if equipment.sellPrices.itemPrice.isActionPrice():
                action = packItemActionTooltipData(equipment, False)
            data = {'intCD': equipment.intCD,
             'userName': equipment.userName,
             'sellPrice': equipment.sellPrices.itemPrice.price.toMoneyTuple(),
             'toInventory': True,
             'action': action}
            onVehicleEquipments.append(data)

        onVehicleBattleBoosters = []
        for booster in vehicle.equipment.battleBoosterConsumables.getInstalledItems():
            data = {'intCD': booster.intCD,
             'userName': booster.userName,
             'sellPrice': MONEY_UNDEFINED.toMoneyTuple(),
             'onlyToInventory': True}
            onVehicleBattleBoosters.append(data)

        inInventoryModules = []
        for m in modules:
            inInventoryModules.append({'intCD': m.intCD,
             'inventoryCount': m.inventoryCount,
             'toInventory': True,
             'sellPrice': m.sellPrices.itemPrice.price.toMoneyTuple()})

        inInventoryShells = []
        for s in shells:
            action = None
            itemPrice = s.sellPrices.itemPrice
            if itemPrice.isActionPrice():
                action = packItemActionTooltipData(s, False)
            inInventoryShells.append({'intCD': s.intCD,
             'count': s.inventoryCount,
             'sellPrice': itemPrice.price.toMoneyTuple(),
             'userName': s.userName,
             'kind': s.type,
             'toInventory': s in otherVehsShells or s.isPremium,
             'action': action})

        customizationOnVehicle = []
        for c in installedCustomizations:
            action = None
            itemPrice = c.sellPrices.itemPrice
            if itemPrice.isActionPrice():
                action = packItemActionTooltipData(c, False)
            count = c.getInstalledOnVehicleCount(vehicle.intCD)
            data = {'intCD': c.intCD,
             'userName': c.userName,
             'sellPrice': (itemPrice.price * count).toMoneyTuple(),
             'toInventory': True,
             'onlyToInventory': c.isRentable or c.isHidden,
             'count': count,
             'action': action}
            customizationOnVehicle.append(data)

        settings = self.getDialogSettings()
        isSlidingComponentOpened = settings['isOpened']
        self.as_setDataS({'accountMoney': items.stats.money.toMoneyTuple(),
         'sellVehicleVO': sellVehicleData,
         'optionalDevicesOnVehicle': onVehicleOptionalDevices,
         'shellsOnVehicle': onVehicleoShells,
         'equipmentsOnVehicle': onVehicleEquipments,
         'modulesInInventory': inInventoryModules,
         'shellsInInventory': inInventoryShells,
         'isSlidingComponentOpened': isSlidingComponentOpened,
         'battleBoostersOnVehicle': onVehicleBattleBoosters,
         'customizationOnVehicle': customizationOnVehicle})
        return

    def onChangeConfiguration(self, optDevicesToStorage):
        self.__updateSpendMoneyByOptDevicesToStorage(optDevicesToStorage)
        self.checkControlQuestion(self.__checkUsefulTankman)

    def checkControlQuestion(self, checkTankman):
        self.__checkUsefulTankman = checkTankman
        if self.__useCtrlQuestion(self.__getCurrentVehicle(), self.__checkUsefulTankman):
            self.as_visibleControlBlockS(True)
            self.setUserInput('')
        else:
            self.as_visibleControlBlockS(False)
            self.setUserInput(self.__controlNumber)

    def setUserInput(self, userInput):
        goldEnough = self.__enoughCurrency(Currency.GOLD)
        crystalEnough = self.__enoughCurrency(Currency.CRYSTAL)
        controlNumberValid = userInput == self.__controlNumber
        self.as_enableButtonS(controlNumberValid and crystalEnough and (goldEnough or isIngameShopEnabled()))

    def setResultCredit(self, isGold, value):
        self.__controlNumber = str(value)
        question = self.__getControlQuestion(isGold)
        self.as_setControlQuestionDataS(isGold, self.__controlNumber, question)

    def _dispose(self):
        super(VehicleSellDialog, self)._dispose()
        self.itemsCache.onSyncCompleted -= self.__shopResyncHandler
        g_clientUpdateManager.removeCurrencyCallback(Currency.GOLD, self.onSetGoldHndlr)

    def onSetGoldHndlr(self, gold):
        self.as_checkGoldS(gold)

    @decorators.process('sellVehicle')
    def __doSellVehicle(self, vehicle, shells, eqs, optDevicesToSell, inventory, customizationItems, isDismissCrew):
        vehicleSeller = VehicleSeller(vehicle, shells, eqs, optDevicesToSell, inventory, customizationItems, isDismissCrew)
        currentMoneyGold = self.itemsCache.items.stats.money.get(Currency.GOLD, 0)
        spendMoneyGold = vehicleSeller.spendMoney.get(Currency.GOLD, 0)
        if isIngameShopEnabled() and currentMoneyGold < spendMoneyGold:
            showBuyGoldForEquipment(spendMoneyGold)
        else:
            result = yield vehicleSeller.request()
            SystemMessages.pushMessages(result)
            self.destroy()

    def sell(self, vehicleCD, shells, eqs, optDevicesToSell, inventory, customizationItems, isDismissCrew):

        def getItem(data):
            return self.itemsCache.items.getItemByCD(int(data['intCD']))

        def getShellItem(data):
            return Shell(int(data['intCD']), int(data['count']), proxy=self.itemsCache.items)

        try:
            vehicle = self.itemsCache.items.getItemByCD(int(vehicleCD))
            shells = [ getShellItem(flashObject2Dict(shell)) for shell in shells ]
            eqs = [ item for item in (getItem(flashObject2Dict(eq)) for eq in eqs) if not item.isBuiltIn ]
            optDevicesToSell = [ getItem(flashObject2Dict(dev)) for dev in optDevicesToSell ]
            inventory = [ getItem(flashObject2Dict(module)) for module in inventory ]
            customizationItems = [ getItem(flashObject2Dict(cust_item)) for cust_item in customizationItems ]
            self.__doSellVehicle(vehicle, shells, eqs, optDevicesToSell, inventory, customizationItems, isDismissCrew)
        except Exception:
            LOG_ERROR('There is error while selling vehicle')
            LOG_CURRENT_EXCEPTION()

    @staticmethod
    def __useCtrlQuestion(vehicle, checkUsefulTankman=True):
        if vehicle.level >= 3 or vehicle.isPremium:
            return True
        if checkUsefulTankman:
            for _, tankman in vehicle.crew:
                if tankman and (tankman.roleLevel >= 100 or tankman.skills):
                    return True

        return False

    def __getControlQuestion(self, usingGold=False):
        if usingGold:
            currencyFormatter = backport.getGoldFormat(long(self.__controlNumber))
        else:
            currencyFormatter = backport.getIntegralFormat(long(self.__controlNumber))
        question = makeHtmlString('html_templates:lobby/dialogs', 'vehicleSellQuestion', {'controlNumber': currencyFormatter})
        return question

    def __enoughCurrency(self, currency):
        return self.__spendMoney.get(currency, 0) <= self.itemsCache.items.stats.money.get(currency, 0)

    def __shopResyncHandler(self, reason, diff):
        vehicle = self.__getCurrentVehicle()
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or vehicle is not None and vehicle.rentalIsActive:
            self.onWindowClose()
        return

    def __getCurrentVehicle(self):
        return self.itemsCache.items.getVehicle(self.__vehInvID)

    def __updateSpendMoneyByOptDevicesToStorage(self, optDevicesToSell):
        self.__spendMoney = calculateSpendMoney(self.itemsCache.items, getDismantlingToInventoryDevices(self.__getCurrentVehicle(), optDevicesToSell))
