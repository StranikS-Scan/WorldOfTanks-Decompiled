# Embedded file name: scripts/client/gui/shared/gui_items/processors/vehicle.py
import BigWorld
import AccountCommands
from account_shared import LayoutIterator
from adisp import process, async
from debug_utils import LOG_DEBUG
from AccountCommands import VEHICLE_SETTINGS_FLAG
from gui.shared.gui_items.service_items import Price
from shared_utils import findFirst
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.shared import g_itemsCache
from gui.shared.formatters import formatPrice
from gui.shared.gui_items.processors import ItemProcessor, Processor, makeI18nSuccess, makeI18nError, plugins, makeSuccess

def getCrewAndShellsSumPrice(result, vehicle, crewType, buyShells):
    if crewType != -1:
        tankmenCount = len(vehicle.crew)
        tankmanCost = g_itemsCache.items.shop.tankmanCostWithGoodyDiscount[crewType]
        result[0] += tankmanCost['credits'] * tankmenCount
        result[1] += tankmanCost['gold'] * tankmenCount
    if buyShells:
        for shell in vehicle.gun.defaultAmmo:
            result[0] += shell.buyPrice[0] * shell.defaultCount
            result[1] += shell.buyPrice[1] * shell.defaultCount

    return result


class VehicleRenter(ItemProcessor):

    def __init__(self, vehicle, rentPackage, buyShell = False, crewType = -1):
        self.buyShell = buyShell
        self.buyCrew = crewType != -1
        self.crewType = crewType
        self.vehicle = vehicle
        self.rentPackage = rentPackage
        self.rentPrice = self.__getRentPrice(rentPackage, vehicle)
        self.price = self._getPrice()
        super(VehicleRenter, self).__init__(vehicle, self._getPluginsList())

    def _getPluginsList(self):
        return (plugins.MoneyValidator(self.price), plugins.VehicleFreeLimitConfirmator(self.vehicle, self.crewType))

    def _getPrice(self):
        return getCrewAndShellsSumPrice(self.rentPrice, self.vehicle, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr = '', ctx = None):
        if not len(errStr):
            msg = 'vehicle_rent/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_rent/server_error_centerDown'
        else:
            msg = 'vehicle_rent/%s' % errStr
        return makeI18nError(msg, vehName=self.item.userName)

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('vehicle_rent/success', vehName=self.item.userName, days=ctx.get('days', 0), price=formatPrice(self.price), type=self._getSysMsgType())

    def _request(self, callback):
        LOG_DEBUG('Make request to buy or rent vehicle', self.vehicle, self.crewType, self.buyShell, self.price)
        BigWorld.player().shop.buyVehicle(self.item.nationID, self.item.innationID, self.buyShell, self.buyCrew, self.crewType, self._getRentInfo(), lambda code: self._response(code, callback, ctx={'days': self._getRentInfo()}))

    def _getRentInfo(self):
        return self.rentPackage

    def _getSysMsgType(self):
        if self.item.buyPrice[1] > 0:
            return SM_TYPE.PurchaseForGold
        return SM_TYPE.PurchaseForCredits

    def __getRentPrice(self, rentPackage, vehicle):
        for package in vehicle.rentPackages:
            if package['days'] == rentPackage:
                return list(package['rentPrice'])

        return [0, 0]


class VehicleBuyer(VehicleRenter):

    def __init__(self, vehicle, buySlot, buyShell = False, crewType = -1):
        self.buySlot = buySlot
        super(VehicleBuyer, self).__init__(vehicle, None, buyShell=buyShell, crewType=crewType)
        return

    def _getPluginsList(self):
        return (plugins.MoneyValidator(self.price), plugins.VehicleSlotsConfirmator(not self.buySlot), plugins.VehicleFreeLimitConfirmator(self.vehicle, self.crewType))

    def _getPrice(self):
        return getCrewAndShellsSumPrice(list(self.vehicle.buyPrice), self.vehicle, self.crewType, self.buyShell)

    def _errorHandler(self, code, errStr = '', ctx = None):
        if not len(errStr):
            msg = 'vehicle_buy/server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'vehicle_buy/server_error_centerDown'
        else:
            msg = 'vehicle_buy/%s' % errStr
        return makeI18nError(msg, vehName=self.item.userName)

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('vehicle_buy/success', vehName=self.item.userName, price=formatPrice(self.price), type=self._getSysMsgType())

    def _getRentInfo(self):
        return -1


class VehicleSlotBuyer(Processor):

    def __init__(self, showConfirm = True, showWarning = True):
        self.__hasDiscounts = bool(g_itemsCache.items.shop.personalSlotDiscounts)
        self.__frozenSlotPrice = None
        slotCost = self.__getSlotPrice()
        if self.__hasDiscounts and slotCost.gold == 0:
            confirmationType = 'freeSlotConfirmation'
            ctx = {}
        else:
            confirmationType = 'buySlotConfirmation'
            ctx = {'gold': slotCost[1]}
        super(VehicleSlotBuyer, self).__init__((plugins.MessageInformator('buySlotNotEnoughCredits', activeHandler=lambda : not plugins.MoneyValidator(slotCost).validate().success, isEnabled=showWarning), plugins.MessageConfirmator(confirmationType, isEnabled=showConfirm, ctx=ctx), plugins.MoneyValidator(slotCost)))
        return

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('vehicle_slot_buy/%s' % errStr)
        return makeI18nError('vehicle_slot_buy/server_error')

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('vehicle_slot_buy/success', money=formatPrice(self.__getSlotPrice()), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        LOG_DEBUG('Attempt to request server for buying vehicle slot')
        BigWorld.player().stats.buySlot(lambda code: self._response(code, callback))

    def __getSlotPrice(self):
        if self.__frozenSlotPrice is not None:
            price = self.__frozenSlotPrice
        else:
            price = g_itemsCache.items.shop.getVehicleSlotsPrice(g_itemsCache.items.stats.vehicleSlots)
            if self.__hasDiscounts:
                self.__frozenSlotPrice = price
        return Price(0, price)


class VehicleSeller(ItemProcessor):

    def __init__(self, vehicle, dismantlingGoldCost, shells = [], eqs = [], optDevs = [], inventory = [], isCrewDismiss = False):
        self.gainMoney, self.spendMoney = self.__getGainSpendMoney(vehicle, shells, eqs, optDevs, inventory, dismantlingGoldCost)
        barracksBerthsNeeded = len(filter(lambda (idx, item): item is not None, vehicle.crew))
        super(VehicleSeller, self).__init__(vehicle, (plugins.VehicleValidator(vehicle, False, prop={'isBroken': True,
          'isLocked': True}),
         plugins.VehicleSellValidator(vehicle),
         plugins.MoneyValidator(self.spendMoney),
         plugins.VehicleSellsLeftValidator(vehicle, not (vehicle.isRented and vehicle.rentalIsOver)),
         plugins.BarracksSlotsValidator(barracksBerthsNeeded, isEnabled=not isCrewDismiss),
         plugins.MessageConfirmator('vehicleSell/unique', isEnabled=vehicle.isUnique)))
        self.vehicle = vehicle
        self.shells = shells
        self.eqs = eqs
        self.optDevs = optDevs
        self.inventory = inventory
        self.isCrewDismiss = isCrewDismiss
        self.isDismantlingForGold = self.__dismantlingForGoldDevicesCount(vehicle, optDevs) > 0
        self.isRemovedAfterRent = vehicle.isRented

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            localKey = 'vehicle_sell/%s'
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/%s'
            return makeI18nError(localKey % errStr, vehName=self.vehicle.userName)
        localKey = 'vehicle_sell/server_error'
        if self.isRemovedAfterRent:
            localKey = 'vehicle_remove/server_error'
        return makeI18nError(localKey, vehName=self.vehicle.userName)

    def _successHandler(self, code, ctx = None):
        if self.isDismantlingForGold:
            localKey = 'vehicle_sell/success_dismantling'
            smType = SM_TYPE.Selling
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/success_dismantling'
                smType = SM_TYPE.Remove
            return makeI18nSuccess(localKey, vehName=self.vehicle.userName, gainMoney=formatPrice(self.gainMoney), spendMoney=formatPrice(self.spendMoney), type=smType)
        else:
            localKey = 'vehicle_sell/success'
            smType = SM_TYPE.Selling
            if self.isRemovedAfterRent:
                localKey = 'vehicle_remove/success'
                smType = SM_TYPE.Remove
            return makeI18nSuccess(localKey, vehName=self.vehicle.userName, money=formatPrice(self.gainMoney), type=smType)

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
        moneyGain = list(vehicle.sellPrice)
        for shell in vehShells:
            self.__accumulatePrice(moneyGain, shell.sellPrice, shell.count)

        for module in vehEqs + vehOptDevs:
            self.__accumulatePrice(moneyGain, module.sellPrice)

        for module in inventory:
            self.__accumulatePrice(moneyGain, module.sellPrice, module.inventoryCount)

        moneySpend = (0, self.__dismantlingForGoldDevicesCount(vehicle, vehOptDevs) * dismantlingGoldCost)
        return (moneyGain, moneySpend)

    def __accumulatePrice(self, result, price, count = 1):
        for i in xrange(2):
            result[i] += price[i] * count

        return result


class VehicleSettingsProcessor(ItemProcessor):

    def __init__(self, vehicle, setting, value, plugins = list()):
        self._setting = setting
        self._value = value
        super(VehicleSettingsProcessor, self).__init__(vehicle, plugins)

    def _request(self, callback):
        LOG_DEBUG('Make server request for changing vehicle settings', self.item, self._setting, bool(self._value))
        BigWorld.player().inventory.changeVehicleSetting(self.item.invID, self._setting, bool(self._value), lambda code: self._response(code, callback))


class VehicleTmenXPAccelerator(VehicleSettingsProcessor):

    def __init__(self, vehicle, value):
        super(VehicleTmenXPAccelerator, self).__init__(vehicle, VEHICLE_SETTINGS_FLAG.XP_TO_TMAN, value, (plugins.MessageConfirmator('xpToTmenCheckbox', isEnabled=value),))

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('vehicle_tmenxp_accelerator/%s' % errStr, vehName=self.item.userName)
        return makeI18nError('vehicle_tmenxp_accelerator/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx = None):
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

    def __init__(self, vehicle, shellsLayout = None, eqsLayout = None):
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
        isWalletValidatorEnabled = bool(shellsPrice[1] or eqsPrice[1])
        self.addPlugins((plugins.VehicleLockValidator(vehicle), plugins.WalletValidator(isWalletValidatorEnabled), plugins.VehicleLayoutValidator(shellsPrice, eqsPrice)))

    def _request(self, callback):
        BigWorld.player().inventory.setAndFillLayouts(self.vehicle.invID, self.shellsLayout, self.eqsLayout, lambda code, errStr, ext: self._response(code, callback, errStr=errStr, ctx=ext))

    def __getSysMsgType(self, price):
        if price[1] > 0:
            return SM_TYPE.PurchaseForGold
        return SM_TYPE.PurchaseForCredits

    def _successHandler(self, code, ctx = None):
        additionalMessages = []
        if len(ctx.get('shells', [])):
            totalPrice = [0, 0]
            for shellCompDescr, price, count in ctx.get('shells', []):
                shell = g_itemsCache.items.getItemByCD(shellCompDescr)
                additionalMessages.append(makeI18nSuccess('shell_buy/success', name=shell.userName, count=count, money=formatPrice(price), type=self.__getSysMsgType(price)))
                totalPrice[0] += price[0]
                totalPrice[1] += price[1]

            additionalMessages.append(makeI18nSuccess('layout_apply/success_money_spent', money=formatPrice(totalPrice), type=self.__getSysMsgType(totalPrice)))
        if len(ctx.get('eqs', [])):
            for eqCompDescr, price, count in ctx.get('eqs', []):
                equipment = g_itemsCache.items.getItemByCD(eqCompDescr)
                additionalMessages.append(makeI18nSuccess('artefact_buy/success', kind=equipment.userType, name=equipment.userName, count=count, money=formatPrice(price), type=self.__getSysMsgType(price)))

        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr = '', ctx = None):
        if not len(errStr):
            msg = 'server_error' if code != AccountCommands.RES_CENTER_DISCONNECTED else 'server_error_centerDown'
        else:
            msg = errStr
        return makeI18nError('layout_apply/%s' % msg, vehName=self.vehicle.userName, type=SM_TYPE.Error)

    def getShellsLayoutPrice(self):
        """
        @return: price that should be paid to fill layout
        """
        goldPrice = 0
        creditsPrice = 0
        if self.shellsLayout is None:
            return (creditsPrice, goldPrice)
        else:
            for shellCompDescr, count, isBoughtForCredits in LayoutIterator(self.shellsLayout):
                if not shellCompDescr or not count:
                    continue
                shell = g_itemsCache.items.getItemByCD(int(shellCompDescr))
                vehShell = findFirst(lambda s: s.intCD == shellCompDescr, self.vehicle.shells)
                vehCount = vehShell.count if vehShell is not None else 0
                buyCount = count - shell.inventoryCount - vehCount
                if buyCount:
                    if shell.buyPrice[1] and not isBoughtForCredits:
                        goldPrice += shell.buyPrice[1] * buyCount
                    elif shell.buyPrice[1] and isBoughtForCredits:
                        creditsPrice += shell.buyPrice[1] * buyCount * g_itemsCache.items.shop.exchangeRateForShellsAndEqs
                    elif shell.buyPrice[0]:
                        creditsPrice += shell.buyPrice[0] * buyCount

            return (creditsPrice, goldPrice)

    def getEqsLayoutPrice(self):
        """
        @return: price that should be paid to fill layout
        """
        goldPrice = 0
        creditsPrice = 0
        if self.eqsLayout is None:
            return (creditsPrice, goldPrice)
        else:
            for idx, (eqCompDescr, count, isBoughtForCredits) in enumerate(LayoutIterator(self.eqsLayout)):
                if not eqCompDescr or not count:
                    continue
                equipment = g_itemsCache.items.getItemByCD(int(eqCompDescr))
                vehEquipment = self.vehicle.eqs[idx]
                vehCount = 1 if vehEquipment is not None else 0
                buyCount = count - equipment.inventoryCount - vehCount
                if buyCount:
                    if equipment.buyPrice[1] and not isBoughtForCredits:
                        goldPrice += equipment.buyPrice[1] * buyCount
                    elif equipment.buyPrice[1] and isBoughtForCredits:
                        creditsPrice += equipment.buyPrice[1] * buyCount * g_itemsCache.items.shop.exchangeRateForShellsAndEqs
                    elif equipment.buyPrice[0]:
                        creditsPrice += equipment.buyPrice[0] * buyCount

            return (creditsPrice, goldPrice)


class VehicleRepairer(ItemProcessor):

    def __init__(self, vehicle):
        self._repairCost = (vehicle.repairCost, 0)
        super(VehicleRepairer, self).__init__(vehicle, (plugins.MoneyValidator(self._repairCost),))

    def _request(self, callback):
        BigWorld.player().inventory.repair(self.item.invID, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            needed = (self._repairCost[0] - g_itemsCache.items.stats.credits, 0)
            return makeI18nError('vehicle_repair/%s' % errStr, vehName=self.item.userName, needed=formatPrice(needed))
        return makeI18nError('vehicle_repair/server_error', vehName=self.item.userName)

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('vehicle_repair/success', vehName=self.item.userName, money=formatPrice(self._repairCost), type=SM_TYPE.Repair)


@async
@process
def tryToLoadDefaultShellsLayout(vehicle, callback = None):
    defaultLayout = []
    for shell in vehicle.shells:
        if shell.defaultCount > shell.inventoryCount:
            SystemMessages.g_instance.pushI18nMessage('#system_messages:charge/inventory_error', type=SystemMessages.SM_TYPE.Warning)
            yield lambda callback: callback(None)
            break
        defaultLayout.extend(shell.defaultLayoutValue)
    else:
        result = yield VehicleLayoutProcessor(vehicle, defaultLayout).request()
        if result and result.auxData:
            for m in result.auxData:
                SystemMessages.g_instance.pushI18nMessage(m.userMsg, type=m.sysMsgType)

        if result and len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if callback is not None:
            callback(True)
            return

    if callback is not None:
        callback(False)
    return
