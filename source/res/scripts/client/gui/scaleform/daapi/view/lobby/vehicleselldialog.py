# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleSellDialog.py
import BigWorld
from account_helpers.AccountSettings import AccountSettings
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import SystemMessages, makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.VehicleSellDialogMeta import VehicleSellDialogMeta
from gui.Scaleform.genConsts.CURRENCIES_CONSTANTS import CURRENCIES_CONSTANTS
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared import g_itemsCache
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.formatters import text_styles
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.vehicle import VehicleSeller
from gui.shared.gui_items.vehicle_modules import Shell
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.utils import decorators, flashObject2Dict
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import int2roman, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRestoreController

class VehicleSellDialog(VehicleSellDialogMeta):
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, ctx=None):
        """ Ctor """
        super(VehicleSellDialog, self).__init__()
        self.vehInvID = ctx.get('vehInvID', {})
        self.controlNumber = None
        return

    def onWindowClose(self):
        self.destroy()

    def getDialogSettings(self):
        return dict(AccountSettings.getSettings('vehicleSellDialog'))

    def setDialogSettings(self, isOpened):
        """
        Saving given dialog settings. Called from flash.
        @param isOpened: <bool> is dialog opened by default
        """
        settings = self.getDialogSettings()
        settings['isOpened'] = isOpened
        AccountSettings.setSettings('vehicleSellDialog', settings)

    def _populate(self):
        super(VehicleSellDialog, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.gold': self.onSetGoldHndlr})
        g_itemsCache.onSyncCompleted += self.__shopResyncHandler
        items = g_itemsCache.items
        vehicle = items.getVehicle(self.vehInvID)
        sellPrice = vehicle.sellPrice
        sellForGold = sellPrice.gold > 0
        priceTextColor = CURRENCIES_CONSTANTS.GOLD_COLOR if sellForGold else CURRENCIES_CONSTANTS.CREDITS_COLOR
        priceTextValue = _ms(DIALOGS.VEHICLESELLDIALOG_PRICE_SIGN_ADD) + _ms(BigWorld.wg_getIntegralFormat(sellPrice.gold if sellForGold else sellPrice.credits))
        currencyIcon = CURRENCIES_CONSTANTS.GOLD if sellForGold else CURRENCIES_CONSTANTS.CREDITS
        invVehs = items.getVehicles(REQ_CRITERIA.INVENTORY)
        if vehicle.isPremium or vehicle.level >= 3:
            self.as_visibleControlBlockS(True)
            self.__initCtrlQuestion()
        else:
            self.as_visibleControlBlockS(False)
        modules = items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE([vehicle]) | REQ_CRITERIA.INVENTORY).values()
        shells = items.getItems(criteria=REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.SHELL]) | REQ_CRITERIA.INVENTORY).values()
        otherVehsShells = set()
        for invVeh in invVehs.itervalues():
            if invVeh.invID != self.vehInvID:
                for shot in invVeh.descriptor.gun['shots']:
                    otherVehsShells.add(shot['shell']['compactDescr'])

        vehicleAction = None
        if sellPrice != vehicle.defaultSellPrice:
            vehicleAction = packItemActionTooltipData(vehicle, False)
        if vehicle.isElite:
            description = TOOLTIPS.tankcaruseltooltip_vehicletype_elite(vehicle.type)
        else:
            description = DIALOGS.vehicleselldialog_vehicletype(vehicle.type)
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(vehicle.level)), text_styles.main(_ms(DIALOGS.VEHICLESELLDIALOG_VEHICLE_LEVEL)))
        tankmenGoingToBuffer, deletedTankmen = self.restore.getTankmenDeletedBySelling(vehicle)
        deletedCount = len(deletedTankmen)
        if deletedCount > 0:
            recoveryBufferFull = True
            deletedStr = formatDeletedTankmanStr(deletedTankmen[0])
            maxCount = self.restore.getMaxTankmenBufferLength()
            currCount = len(self.restore.getDismissedTankmen())
            if deletedCount == 1:
                crewTooltip = text_styles.concatStylesToMultiLine(text_styles.middleTitle(_ms(TOOLTIPS.VEHICLESELLDIALOG_CREW_ALERTICON_RECOVERY_HEADER)), text_styles.main(_ms(TOOLTIPS.VEHICLESELLDIALOG_CREW_ALERTICON_RECOVERY_BODY, maxVal=maxCount, curVal=currCount, sourceName=tankmenGoingToBuffer[-1].fullUserName, targetInfo=deletedStr)))
            else:
                crewTooltip = text_styles.concatStylesToMultiLine(text_styles.middleTitle(_ms(TOOLTIPS.VEHICLESELLDIALOG_CREW_ALERTICON_RECOVERY_HEADER)), text_styles.main(_ms(TOOLTIPS.DISMISSTANKMANDIALOG_BUFFERISFULLMULTIPLE_BODY, deletedStr=deletedStr, extraCount=deletedCount - 1, maxCount=maxCount, currCount=currCount)))
        else:
            crewTooltip = None
            recoveryBufferFull = False
        barracksDropDownData = [{'label': _ms(MENU.BARRACKS_BTNUNLOAD)}, {'label': _ms(MENU.BARRACKS_BTNDISSMISS)}]
        sellVehicleData = {'intCD': vehicle.intCD,
         'userName': vehicle.userName,
         'icon': vehicle.icon,
         'level': vehicle.level,
         'isElite': vehicle.isElite,
         'isPremium': vehicle.isPremium,
         'type': vehicle.type,
         'nationID': vehicle.nationID,
         'sellPrice': sellPrice,
         'priceTextValue': priceTextValue,
         'priceTextColor': priceTextColor,
         'currencyIcon': currencyIcon,
         'action': vehicleAction,
         'hasCrew': vehicle.hasCrew,
         'isRented': vehicle.isRented,
         'description': description,
         'levelStr': levelStr,
         'priceLabel': _ms(DIALOGS.VEHICLESELLDIALOG_VEHICLE_EMPTYSELLPRICE),
         'crewLabel': _ms(DIALOGS.VEHICLESELLDIALOG_CREW_LABEL),
         'crewTooltip': crewTooltip,
         'barracksDropDownData': barracksDropDownData,
         'crewRecoveryBufferFull': recoveryBufferFull}
        onVehicleOptionalDevices = []
        for o in vehicle.optDevices:
            if o is not None:
                action = None
                if o.sellPrice != o.defaultSellPrice:
                    action = packItemActionTooltipData(o, False)
                data = {'intCD': o.intCD,
                 'isRemovable': o.isRemovable,
                 'userName': o.userName,
                 'sellPrice': o.sellPrice,
                 'toInventory': True,
                 'action': action}
                onVehicleOptionalDevices.append(data)

        onVehicleoShells = []
        for shell in vehicle.shells:
            if shell is not None:
                action = None
                if shell.sellPrice != shell.defaultSellPrice:
                    action = packItemActionTooltipData(shell, False)
                data = {'intCD': shell.intCD,
                 'count': shell.count,
                 'sellPrice': shell.sellPrice,
                 'userName': shell.userName,
                 'kind': shell.type,
                 'toInventory': shell in otherVehsShells or shell.isPremium,
                 'action': action}
                onVehicleoShells.append(data)

        onVehicleEquipments = []
        for equipmnent in vehicle.eqs:
            if equipmnent is not None:
                action = None
                if equipmnent.sellPrice != equipmnent.defaultSellPrice:
                    action = packItemActionTooltipData(equipmnent, False)
                data = {'intCD': equipmnent.intCD,
                 'userName': equipmnent.userName,
                 'sellPrice': equipmnent.sellPrice,
                 'toInventory': True,
                 'action': action}
                onVehicleEquipments.append(data)

        inInventoryModules = []
        for m in modules:
            inInventoryModules.append({'intCD': m.intCD,
             'inventoryCount': m.inventoryCount,
             'toInventory': True,
             'sellPrice': m.sellPrice})

        inInventoryShells = []
        for s in shells:
            action = None
            if s.sellPrice != s.defaultSellPrice:
                action = packItemActionTooltipData(s, False)
            inInventoryShells.append({'intCD': s.intCD,
             'count': s.inventoryCount,
             'sellPrice': s.sellPrice,
             'userName': s.userName,
             'kind': s.type,
             'toInventory': s in otherVehsShells or s.isPremium,
             'action': action})

        removePrice = items.shop.paidRemovalCost
        removePrices = Money(gold=removePrice)
        defRemovePrice = Money(gold=items.shop.defaults.paidRemovalCost)
        removeAction = None
        if removePrices != defRemovePrice:
            removeAction = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'paidRemovalCost', True, removePrices, defRemovePrice)
        settings = self.getDialogSettings()
        isSlidingComponentOpened = settings['isOpened']
        self.as_setDataS({'accountGold': items.stats.gold,
         'sellVehicleVO': sellVehicleData,
         'optionalDevicesOnVehicle': onVehicleOptionalDevices,
         'shellsOnVehicle': onVehicleoShells,
         'equipmentsOnVehicle': onVehicleEquipments,
         'modulesInInventory': inInventoryModules,
         'shellsInInventory': inInventoryShells,
         'removeActionPrice': removeAction,
         'removePrice': removePrice,
         'isSlidingComponentOpened': isSlidingComponentOpened})
        return

    def setUserInput(self, value):
        if value == self.controlNumber:
            self.as_enableButtonS(True)
        else:
            self.as_enableButtonS(False)

    def setResultCredit(self, isGold, value):
        self.controlNumber = str(value)
        question = self.__getControlQuestion(isGold)
        self.as_setControlQuestionDataS(isGold, self.controlNumber, question)

    def _dispose(self):
        super(VehicleSellDialog, self)._dispose()
        g_itemsCache.onSyncCompleted -= self.__shopResyncHandler
        g_clientUpdateManager.removeCallback('stats.gold', self.onSetGoldHndlr)

    def checkControlQuestion(self, dismiss):
        items = g_itemsCache.items
        vehicle = items.getVehicle(self.vehInvID)
        checkUsefullTankmen = False
        for tankman in vehicle.crew:
            if tankman[1]:
                if tankman[1].roleLevel >= 100 or len(tankman[1].skills):
                    checkUsefullTankmen = dismiss
                    break

        if vehicle.isPremium or vehicle.level >= 3 or checkUsefullTankmen:
            self.as_visibleControlBlockS(True)
            self.__initCtrlQuestion()
        else:
            self.as_visibleControlBlockS(False)

    def onSetGoldHndlr(self, gold):
        self.as_checkGoldS(gold)

    @decorators.process('sellVehicle')
    def __doSellVehicle(self, vehicle, shells, eqs, optDevs, inventory, isDismissCrew):
        removalCost = g_itemsCache.items.shop.paidRemovalCost
        result = yield VehicleSeller(vehicle, removalCost, shells, eqs, optDevs, inventory, isDismissCrew).request()
        if len(result.userMsg):
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def sell(self, vehicleCD, shells, eqs, optDevs, inventory, isDismissCrew):
        """
        Make server request to sell given @vehicle. Called from flash.
        
        @param vehicle: <dict> vehicle packed data to sell
        @param shells: <list> list of shells items to sell
        @param eqs: <list> list of equipment items to sell
        @param optDevs: <list> list of optional devices to sell
        @param inventory: <list> list of inventory items to sell
        @param isDismissCrew: <bool> is dismiss crew
        """
        getItem = lambda data: g_itemsCache.items.getItemByCD(int(data['intCD']))
        getShellItem = lambda data: Shell(int(data['intCD']), int(data['count']), proxy=g_itemsCache.items)
        try:
            vehicle = g_itemsCache.items.getItemByCD(int(vehicleCD))
            shells = [ getShellItem(flashObject2Dict(shell)) for shell in shells ]
            eqs = [ getItem(flashObject2Dict(eq)) for eq in eqs ]
            optDevs = [ getItem(flashObject2Dict(dev)) for dev in optDevs ]
            inventory = [ getItem(flashObject2Dict(module)) for module in inventory ]
            self.__doSellVehicle(vehicle, shells, eqs, optDevs, inventory, isDismissCrew)
        except Exception:
            LOG_ERROR('There is error while selling vehicle')
            LOG_CURRENT_EXCEPTION()

    def __initCtrlQuestion(self):
        self.as_enableButtonS(False)

    def __getControlQuestion(self, usingGold=False):
        if usingGold:
            currencyFormatter = BigWorld.wg_getGoldFormat(long(self.controlNumber))
        else:
            currencyFormatter = BigWorld.wg_getIntegralFormat(long(self.controlNumber))
        question = makeHtmlString('html_templates:lobby/dialogs', 'vehicleSellQuestion', {'controlNumber': currencyFormatter})
        return question

    def __shopResyncHandler(self, reason, diff):
        vehicle = g_itemsCache.items.getVehicle(self.vehInvID)
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or vehicle is not None and vehicle.rentalIsActive:
            self.onWindowClose()
        return
