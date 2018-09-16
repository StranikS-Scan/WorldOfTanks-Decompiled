# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/lobby/triggers.py
import BigWorld
import dossiers2
from AccountCommands import RES_SUCCESS
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from tutorial.control import game_vars, g_tutorialWeaver
from tutorial.control.lobby import aspects
from tutorial.control.triggers import Trigger, TriggerWithValidateVar, TriggerWithSubscription
from tutorial.logger import LOG_ERROR
__all__ = ('BonusTrigger', 'BattleCountRequester', 'ItemUnlockedTrigger', 'ItemInInventoryTrigger', 'ItemInstalledTrigger', 'EquipmentInstalledTrigger', 'CurrentVehicleChangedTrigger', 'FreeVehicleSlotChangedTrigger', 'PremiumPeriodChangedTrigger', 'PremiumDiscountUseTrigger')

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

    def __init__(self, triggerID, validateVarID, setVarID=None):
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

    def __init__(self, triggerID, validateVarID, setVarID, validateUpdateOnly=False):
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

    def __init__(self, triggerID, validateVarID, vehicleVarID, setVarID=None, validateUpdateOnly=False):
        super(_VehicleTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID, validateUpdateOnly=validateUpdateOnly)
        self._vehicleVarID = vehicleVarID

    def _getVehicle(self):
        return game_vars.getVehicleByIntCD(self.getVar(self._vehicleVarID))


class ItemInInventoryTrigger(_VehicleTrigger):

    def isOn(self):
        getter = game_vars.getItemByIntCD
        items = map(getter, self.getIterVar())
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

    def isOn(self, vehicle=None):
        getter = game_vars.getItemByIntCD
        items = map(getter, self.getIterVar())
        if vehicle is None:
            vehicle = self._getVehicle()
        if vehicle is None:
            return False
        else:
            return len([ item for item in items if item.isInstalled(vehicle) ]) > 0

    def _subscribe(self):
        diff = 'inventory.{0}.compDescr'.format(GUI_ITEM_TYPE.VEHICLE)
        g_clientUpdateManager.addCallbacks({diff: self.__onVehiclesUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onVehiclesUpdated(self, descrs):
        if descrs is not None:
            vehicle = self._getVehicle()
            if vehicle is not None and vehicle.invID in descrs:
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
            if vehicle is not None and vehicle.invID in eqs:
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
        self.__pIdx = -1

    def run(self):
        if not self.isSubscribed:
            self.__pIdx = g_tutorialWeaver.weave(pointcut=aspects.BuySlotPointcut, aspects=[aspects.BuySlotAspect(self)])
            self.isSubscribed = True
        self.isRunning = True
        self.toggle(isOn=self.isOn())

    def isOn(self, success=False):
        return success

    def clear(self):
        g_tutorialWeaver.clear(self.__pIdx)
        self.__pIdx = -1
        self.isSubscribed = False
        self.isRunning = False


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
        self.__pIdx = -1

    def run(self):
        if not self.isSubscribed:
            self.__pIdx = g_tutorialWeaver.weave(pointcut=aspects.BuyPremiumWithDiscountPointcut, aspects=[aspects.BuyPremiumWithDiscountAspect(self)])
            self.isSubscribed = True

    def isOn(self, success=False):
        return success

    def clear(self):
        g_tutorialWeaver.clear(self.__pIdx)
        self.__pIdx = -1
        self.isSubscribed = False


class PersonalSlotDiscountsUseTrigger(Trigger):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, triggerID):
        super(PersonalSlotDiscountsUseTrigger, self).__init__(triggerID)
        self._slotsDiscounts = self.itemsCache.items.shop.personalSlotDiscounts

    def run(self):
        if not self.isSubscribed:
            self.isSubscribed = True
            g_clientUpdateManager.addCallbacks({'goodies': self.__onDiscountsChange})

    def isOn(self):
        newDiscounts = self.itemsCache.items.shop.personalSlotDiscounts
        result = len(newDiscounts) < len(self._slotsDiscounts)
        self._slotsDiscounts = newDiscounts
        return result

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self._slotsDiscounts = None
        return

    def __onDiscountsChange(self, *args):
        self.toggle(isOn=self.isOn())


class FreeXPChangedTrigger(Trigger):

    def __init__(self, triggerID):
        super(FreeXPChangedTrigger, self).__init__(triggerID)
        self.__startProcessPointcutId = -1

    def run(self):
        if not self.isSubscribed:
            self.__startProcessPointcutId = g_tutorialWeaver.weave(pointcut=aspects.StartXpExchangePointcut, aspects=[aspects.StartXpExchangeAspect(self)])
            self.isSubscribed = True

    def clear(self):
        if self.isSubscribed:
            g_tutorialWeaver.clear(self.__startProcessPointcutId)
            self.__startProcessPointcutId = -1
        self.isSubscribed = False


class TimerTrigger(TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID=None, validateUpdateOnly=False):
        super(TimerTrigger, self).__init__(triggerID, validateVarID, setVarID, validateUpdateOnly)
        self.__timerCallback = None
        return

    def run(self):
        self.isRunning = True
        if self.__timerCallback is None:
            self.isSubscribed = True
            self.__timerCallback = BigWorld.callback(self.getVar(), self.__updateTimer)
        self.toggle(isOn=False)
        return

    def clear(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        self.isSubscribed = False
        self.isRunning = False
        return

    def __updateTimer(self, *args):
        self.__timerCallback = None
        self.toggle(isOn=True)
        return
