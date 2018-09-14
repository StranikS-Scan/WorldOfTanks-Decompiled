# Embedded file name: scripts/client/tutorial/control/chains/triggers.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.prb_helpers import GlobalListener
from tutorial.control import game_vars, g_tutorialWeaver
from tutorial.logger import LOG_DEBUG
from tutorial.control.chains import aspects
from tutorial.control.triggers import Trigger, TriggerWithSubscription
__all__ = ('SimpleDialogTrigger', 'BuyNextLevelVehicleTrigger', 'CurrentVehicleRequiredLevelTrigger', 'CurrentPremiumVehicleTrigger', 'CurrentVehicleMaintenanceStateTrigger', 'CurrentVehicleLockedTrigger', 'TankmanPriceDiscountTrigger', 'QueueTrigger')

class SimpleDialogTrigger(Trigger):

    def __init__(self, triggerID):
        super(SimpleDialogTrigger, self).__init__(triggerID)
        self.__pointcutIdx = -1

    def run(self):
        if self.isSubscribed:
            return
        self.__pointcutIdx = g_tutorialWeaver.weave(pointcut=aspects.SimpleDialogClosePointcut, aspects=(aspects.SimpleDialogResultAspect(self),))
        self.isSubscribed = True

    def clear(self):
        if self.isSubscribed:
            g_tutorialWeaver.clear(idx=self.__pointcutIdx)
            self.isSubscribed = False
        super(SimpleDialogTrigger, self).clear()

    def setResult(self, result):
        LOG_DEBUG('Dialog returns result', result)
        self.toggle(isOn=result)


class BuyNextLevelVehicleTrigger(TriggerWithSubscription):

    def isOn(self):
        return len(game_vars.getVehiclesByLevel(self.getVar() + 1)) > 0

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onInventoryUpdated(self, _):
        self.toggle(isOn=self.isOn())


class CurrentVehicleRequiredLevelTrigger(TriggerWithSubscription):

    def isOn(self):
        return game_vars.getCurrentVehicleLevel() == self.getVar()

    def _subscribe(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged

    def _unsubscribe(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def __onCurrentVehicleChanged(self):
        self.toggle(isOn=self.isOn())


class CurrentPremiumVehicleTrigger(Trigger):

    def run(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        super(CurrentPremiumVehicleTrigger, self).run()

    def clear(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        super(CurrentPremiumVehicleTrigger, self).clear()

    def isOn(self):
        return game_vars.isCurrentVehiclePremium()

    def __onCurrentVehicleChanged(self):
        self.toggle(isOn=self.isOn())


class _CurrentVehicleViewStateTrigger(Trigger, GlobalListener):

    def run(self):
        self.startGlobalListening()
        super(_CurrentVehicleViewStateTrigger, self).run()

    def clear(self):
        self.stopGlobalListening()
        super(_CurrentVehicleViewStateTrigger, self).clear()

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.toggle(isOn=self.isOn())

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.toggle(isOn=self.isOn())

    def onPrbFunctionalInited(self):
        self.toggle(isOn=self.isOn())

    def onUnitFunctionalInited(self):
        self.toggle(isOn=self.isOn())

    def onPrbFunctionalFinished(self):
        self.toggle(isOn=self.isOn())

    def onUnitFunctionalFinished(self):
        self.toggle(isOn=self.isOn())


class CurrentVehicleMaintenanceStateTrigger(_CurrentVehicleViewStateTrigger):

    def isOn(self):
        return game_vars.getCurrentVehicleViewState().isMaintenanceEnabled()


class CurrentVehicleOptionalDevicesStateTrigger(_CurrentVehicleViewStateTrigger):

    def isOn(self):
        return game_vars.getCurrentVehicleViewState().isOptionalDevicesOpsEnabled()


class CurrentVehicleLockedTrigger(_CurrentVehicleViewStateTrigger):

    def isOn(self):
        return game_vars.getCurrentVehicleViewState().isLocked()


class QueueTrigger(_CurrentVehicleViewStateTrigger):

    def onPreQueueFunctionalInited(self):
        self.toggle(isOn=self.isOn())

    def onPreQueueFunctionalFinished(self):
        self.toggle(isOn=self.isOn())

    def isOn(self):
        return self.preQueueFunctional.isInQueue()


class TankmanPriceDiscountTrigger(TriggerWithSubscription):

    def isOn(self, *args):
        index = self.getVar()
        return game_vars.getTankmanCurrentPrice(index) != game_vars.getTankmanDefaultPrice(index)

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'shop': self.__onShopUpdated})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onShopUpdated(self, _):
        self.toggle(isOn=self.isOn())
