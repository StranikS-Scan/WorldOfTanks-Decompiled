# Embedded file name: scripts/client/tutorial/control/lobby/triggers.py
import BigWorld
import dossiers2
from AccountCommands import RES_SUCCESS
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from tutorial.control import game_vars
from tutorial.control.triggers import Trigger, TriggerWithValidateVar, TriggerWithSubscription
from tutorial.logger import LOG_ERROR
__all__ = ['BonusTrigger',
 'BattleCountRequester',
 'ItemUnlockedTrigger',
 'ItemInInventoryTrigger',
 'ItemInstalledTrigger',
 'EquipmentInstalledTrigger',
 'CurrentVehicleChangedTrigger',
 'FreeVehicleSlotChangedTrigger',
 'PremiumPeriodChangedTrigger',
 'PremiumDiscountUseTrigger']

class BonusTrigger(Trigger):

    def __init__(self, triggerID, bonusID):
        super(BonusTrigger, self).__init__(triggerID)
        self.bonusID = bonusID

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            g_clientUpdateManager.addCallbacks({'stats.tutorialsCompleted': self.onTutorialCompleted})
        self.toggle(isOn=self.isOn(self._bonuses.getCompleted()))

    def isOn(self, tutorialsCompleted):
        result = False
        if self.bonusID > -1:
            result = tutorialsCompleted & 1 << self.bonusID != 0
        return result

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def onTutorialCompleted(self, completed):
        if completed is not None:
            self.toggle(isOn=self.isOn(completed))
        return


class BattleCountRequester(TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None):
        super(BattleCountRequester, self).__init__(triggerID, validateVarID, setVarID=setVarID)

    def run(self):
        self.isRunning = True
        self._gui.showWaiting('request-battle-count')
        BigWorld.player().stats.get('dossier', self.__cb_onGetDossier)

    def isOn(self, battlesCount):
        return battlesCount >= self.getVar()

    def __cb_onGetDossier(self, resultID, dossierCompDescr):
        self._gui.hideWaiting('request-battle-count')
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error on request dossier', resultID, dossierCompDescr)
            self.isRunning = False
            return
        dossierDescr = dossiers2.getAccountDossierDescr(dossierCompDescr)
        self.toggle(isOn=self.isOn(dossierDescr['a15x15']['battlesCount']))


class ItemUnlockedTrigger(TriggerWithSubscription):

    def __init__(self, triggerID, validateVarID, setVarID, validateUpdateOnly = False):
        super(ItemUnlockedTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID, validateUpdateOnly=validateUpdateOnly)

    def isOn(self):
        var = self.getIterVar()
        result = var & game_vars.getUnlockedItems()
        isOn = len(result) > 0
        if isOn:
            self.setVar(result.pop())
        return isOn

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self.__onUnlocksUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onUnlocksUpdated(self, unlocks):
        if unlocks is not None:
            self.toggle(isOn=self.isOn())
        return


class _VehicleTrigger(TriggerWithSubscription):

    def __init__(self, triggerID, validateVarID, vehicleVarID, setVarID = None, validateUpdateOnly = False):
        super(_VehicleTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID, validateUpdateOnly=validateUpdateOnly)
        self._vehicleVarID = vehicleVarID

    def _getVehicle(self):
        return game_vars.getVehicleByIntCD(self.getVar(self._vehicleVarID))


class ItemInInventoryTrigger(_VehicleTrigger):

    def isOn(self):
        getter = game_vars.getItemByIntCD
        items = map(lambda intCD: getter(intCD), self.getIterVar())
        vehicle = self._getVehicle()
        for item in items:
            if item.isInInventory:
                return True
            if vehicle is not None and item.isInstalled(vehicle):
                return True

        return False

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onInventoryUpdated(self, _):
        self.toggle(isOn=self.isOn())


class ItemInstalledTrigger(_VehicleTrigger):

    def isOn(self, vehicle = None):
        getter = game_vars.getItemByIntCD
        items = map(lambda intCD: getter(intCD), self.getIterVar())
        if vehicle is None:
            vehicle = self._getVehicle()
        if vehicle is None:
            return False
        else:
            return len(filter(lambda item: item.isInstalled(vehicle), items)) > 0

    def _subscribe(self):
        diff = 'inventory.{0}.compDescr'.format(GUI_ITEM_TYPE.VEHICLE)
        g_clientUpdateManager.addCallbacks({diff: self.__onVehiclesUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onVehiclesUpdated(self, descrs):
        if descrs is not None:
            vehicle = self._getVehicle()
            if vehicle is not None and vehicle.inventoryID in descrs:
                self.toggle(isOn=self.isOn(vehicle=vehicle))
        return


class EquipmentInstalledTrigger(ItemInstalledTrigger):

    def _subscribe(self):
        diff = 'inventory.{0}.eqs'.format(GUI_ITEM_TYPE.VEHICLE)
        g_clientUpdateManager.addCallbacks({diff: self.__onEquipmentUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onEquipmentUpdated(self, eqs):
        if eqs is not None:
            vehicle = self._getVehicle()
            if vehicle is not None and vehicle.inventoryID in eqs:
                self.toggle(isOn=self.isOn(vehicle=vehicle))
        return


class CurrentVehicleChangedTrigger(Trigger):

    def run(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged

    def clear(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def __onCurrentVehicleChanged(self):
        self.toggle(isOn=self.isOn())


class FreeVehicleSlotChangedTrigger(Trigger):

    def __init__(self, triggerID):
        super(FreeVehicleSlotChangedTrigger, self).__init__(triggerID)
        self.__slots = game_vars.getFreeVehiclesSlots()

    def isOn(self):
        return self.__slots < game_vars.getFreeVehiclesSlots()

    def run(self):
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'stats.slots': self.__onSlotsChanged})
            self.isSubscribed = True

    def clear(self):
        if self.isSubscribed:
            g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False

    def __onSlotsChanged(self, _):
        self.toggle(isOn=self.isOn())


class PremiumPeriodChangedTrigger(Trigger):

    def __init__(self, triggerID):
        super(PremiumPeriodChangedTrigger, self).__init__(triggerID)
        self.__snap = game_vars.getPremiumExpiryTime()

    def isOn(self, *args):
        return self.__snap <= game_vars.getPremiumExpiryTime()

    def run(self):
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'account.premiumExpiryTime': self.__onPremiumExpiryTimeChanged})
            self.isSubscribed = True

    def clear(self):
        if self.isSubscribed:
            g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False

    def __onPremiumExpiryTimeChanged(self, _):
        self.toggle(isOn=self.isOn())


class PremiumDiscountUseTrigger(Trigger):

    def __init__(self, triggerID):
        super(PremiumDiscountUseTrigger, self).__init__(triggerID)
        self._premiumDiscounts = g_itemsCache.items.shop.personalPremiumPacketsDiscounts

    def run(self):
        if not self.isSubscribed:
            self.isSubscribed = True
            g_clientUpdateManager.addCallbacks({'goodies': self.__onDiscountsChange})

    def isOn(self):
        newDiscounts = g_itemsCache.items.shop.personalPremiumPacketsDiscounts
        result = len(newDiscounts) < len(self._premiumDiscounts)
        self._premiumDiscounts = newDiscounts
        return result

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self._premiumDiscounts = None
        return

    def __onDiscountsChange(self, *args):
        self.toggle(isOn=self.isOn())


class FreeXPChangedTrigger(Trigger):

    def __init__(self, triggerID):
        super(FreeXPChangedTrigger, self).__init__(triggerID)
        self.__freeXP = game_vars.getFreeXP()

    def isOn(self, *args):
        return self.__freeXP <= game_vars.getFreeXP()

    def run(self):
        if not self.isSubscribed:
            g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__onFreeXPChanged})
            self.isSubscribed = True

    def clear(self):
        if self.isSubscribed:
            g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False

    def __onFreeXPChanged(self, _):
        self.toggle(isOn=self.isOn())
