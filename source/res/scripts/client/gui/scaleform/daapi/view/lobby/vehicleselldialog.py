# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/VehicleSellDialog.py
import BigWorld
from collections import defaultdict
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE
from account_helpers.AccountSettings import AccountSettings
from gui import SystemMessages, makeHtmlString
from gui.Scaleform.daapi.view.meta.VehicleSellDialogMeta import VehicleSellDialogMeta
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.tooltips import ACTION_TOOLTIPS_STATE, ACTION_TOOLTIPS_TYPE, getItemActionTooltipData
from gui.shared.gui_items.processors.vehicle import VehicleSeller
from gui.shared.gui_items.vehicle_modules import Shell
from gui.shared.utils import decorators, flashObject2Dict
from gui.ClientUpdateManager import g_clientUpdateManager

class VehicleSellDialog(VehicleSellDialogMeta):

    def __init__(self, ctx = None):
        """ Ctor """
        super(VehicleSellDialog, self).__init__()
        self.vehInvID = ctx.get('vehInvID', {})
        self.controlNumber = None
        return

    def onWindowClose(self):
        self.destroy()

    def getDialogSettings(self):
        """
        Called from flash.
        @return: <dict> dialog settings dict from `AccountSettings`
        """
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
        if vehicle.sellPrice != vehicle.defaultSellPrice:
            vehicleAction = getItemActionTooltipData(vehicle, False)
        vehicleData = {'intCD': vehicle.intCD,
         'userName': vehicle.userName,
         'icon': vehicle.icon,
         'level': vehicle.level,
         'isElite': vehicle.isElite,
         'isPremium': vehicle.isPremium,
         'type': vehicle.type,
         'nationID': vehicle.nationID,
         'sellPrice': vehicle.sellPrice,
         'action': vehicleAction,
         'hasCrew': vehicle.hasCrew,
         'isRented': vehicle.isRented}
        onVehicle = defaultdict(list)
        onVehicleOptionalDevices = onVehicle['optionalDevices']
        for o in vehicle.optDevices:
            data = None
            if o is not None:
                action = None
                if o.sellPrice != o.defaultSellPrice:
                    action = getItemActionTooltipData(o, False)
                data = {'intCD': o.intCD,
                 'isRemovable': o.isRemovable,
                 'userName': o.userName,
                 'sellPrice': o.sellPrice,
                 'toInventory': True,
                 'action': action}
            onVehicleOptionalDevices.append(data)

        onVehicleoShells = onVehicle['shells']
        for s in vehicle.shells:
            data = None
            if s is not None:
                action = None
                if s.sellPrice != s.defaultSellPrice:
                    action = getItemActionTooltipData(s, False)
                data = {'intCD': s.intCD,
                 'count': s.count,
                 'sellPrice': s.sellPrice,
                 'userName': s.userName,
                 'kind': s.type,
                 'toInventory': s in otherVehsShells or s.isPremium,
                 'action': action}
            onVehicleoShells.append(data)

        onVehicleEquipments = onVehicle['equipments']
        for e in vehicle.eqs:
            data = None
            if e is not None:
                action = None
                if e.sellPrice != e.defaultSellPrice:
                    action = getItemActionTooltipData(e, False)
                data = {'intCD': e.intCD,
                 'userName': e.userName,
                 'sellPrice': e.sellPrice,
                 'toInventory': True,
                 'action': action}
            onVehicleEquipments.append(data)

        inInventory = defaultdict(list)
        inInventoryModules = inInventory['modules']
        for m in modules:
            inInventoryModules.append({'intCD': m.intCD,
             'inventoryCount': m.inventoryCount,
             'toInventory': True,
             'sellPrice': m.sellPrice})

        inInventoryShells = inInventory['shells']
        for s in shells:
            action = None
            if s.sellPrice != s.defaultSellPrice:
                action = getItemActionTooltipData(s, False)
            inInventoryShells.append({'intCD': s.intCD,
             'count': s.inventoryCount,
             'sellPrice': s.sellPrice,
             'userName': s.userName,
             'kind': s.type,
             'toInventory': s in otherVehsShells or s.isPremium,
             'action': action})

        removePrice = (0, items.shop.paidRemovalCost)
        defRemovePrice = (0, items.shop.defaults.paidRemovalCost)
        removeAction = None
        if removePrice != defRemovePrice:
            removeAction = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'paidRemovalCost',
             'isBuying': True,
             'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
             'newPrice': removePrice,
             'oldPrice': defRemovePrice}
        removePrices = {'removePrice': removePrice,
         'action': removeAction}
        self.as_setDataS(vehicleData, onVehicle, inInventory, removePrices, items.stats.gold)
        return

    def setUserInput(self, value):
        if value == self.controlNumber:
            self.as_enableButtonS(True)
        else:
            self.as_enableButtonS(False)

    def setResultCredit(self, isGold, value):
        self.controlNumber = str(value)
        self.__setControlQuestion(isGold)
        self.as_setControlNumberS(isGold, self.controlNumber)

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
            SystemMessages.g_instance.pushMessage(result.userMsg, type=result.sysMsgType)

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

    def __setControlQuestion(self, usingGold = False):
        if usingGold:
            currencyFormatter = BigWorld.wg_getGoldFormat(long(self.controlNumber))
        else:
            currencyFormatter = BigWorld.wg_getIntegralFormat(long(self.controlNumber))
        question = makeHtmlString('html_templates:lobby/dialogs', 'vehicleSellQuestion', {'controlNumber': currencyFormatter})
        self.as_setCtrlQuestionS(str(question))

    def __shopResyncHandler(self, reason, diff):
        vehicle = g_itemsCache.items.getVehicle(self.vehInvID)
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or vehicle is not None and vehicle.rentalIsActive:
            self.onWindowClose()
        return
