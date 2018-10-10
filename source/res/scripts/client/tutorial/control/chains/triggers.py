# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/chains/triggers.py
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.gui.game_control import IIGRController
from skeletons.gui.server_events import IEventsCache
from tutorial.control import game_vars, g_tutorialWeaver
from tutorial.control.chains import aspects
from tutorial.control.triggers import Trigger, TriggerWithSubscription
from tutorial.logger import LOG_DEBUG
__all__ = ('SimpleDialogTrigger', 'BuyNextLevelVehicleTrigger', 'CurrentVehicleRequiredLevelTrigger', 'RentedVehicleTrigger', 'CurrentVehicleMaintenanceStateTrigger', 'CurrentVehicleLockedTrigger', 'TankmanPriceDiscountTrigger', 'QueueTrigger', 'FightButtonDisabledTrigger', 'CurrentVehicleNeedChangeTrigger', 'IsInSandBoxPreQueueTrigger')

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


class RentedVehicleTrigger(Trigger):

    def run(self):
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        super(RentedVehicleTrigger, self).run()

    def clear(self):
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        super(RentedVehicleTrigger, self).clear()

    def isOn(self):
        return game_vars.isCurrentVehicleRented()

    def __onCurrentVehicleChanged(self):
        self.toggle(isOn=self.isOn())


class _CurrentVehicleViewStateTrigger(Trigger, IGlobalListener):

    def run(self):
        if not self.isSubscribed:
            self.startGlobalListening()
            self.isSubscribed = True
        super(_CurrentVehicleViewStateTrigger, self).run()

    def clear(self):
        if self.isSubscribed:
            self.stopGlobalListening()
            self.isSubscribed = False
        super(_CurrentVehicleViewStateTrigger, self).clear()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.toggle(isOn=self.isOn())

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.toggle(isOn=self.isOn())

    def onPrbEntitySwitched(self):
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


class CurrentVehicleNeedChangeTrigger(_CurrentVehicleViewStateTrigger):

    def isOn(self):
        return game_vars.getCurrentVehicleState() in (Vehicle.VEHICLE_STATE.CREW_NOT_FULL,
         Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         Vehicle.VEHICLE_STATE.BATTLE,
         Vehicle.VEHICLE_STATE.DAMAGED,
         Vehicle.VEHICLE_STATE.DESTROYED,
         Vehicle.VEHICLE_STATE.EXPLODED,
         Vehicle.VEHICLE_STATE.IGR_RENTAL_IS_OVER,
         Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY,
         Vehicle.VEHICLE_STATE.LOCKED,
         Vehicle.VEHICLE_STATE.RENTAL_IS_OVER)


class QueueTrigger(_CurrentVehicleViewStateTrigger):

    def onEnqueued(self, queueType, *args):
        self.toggle(isOn=self.isOn())

    def onDequeued(self, queueType, *args):
        self.toggle(isOn=self.isOn())

    def isOn(self):
        return self.prbEntity is not None and self.prbEntity.isInQueue()


class TankmanPriceDiscountTrigger(TriggerWithSubscription):

    def isOn(self, *args):
        index = self.getVar()
        currentGoldPrice = game_vars.getTankmanCurrentPrice(index)
        defaultGoldPrice = game_vars.getTankmanDefaultPrice(index)
        return currentGoldPrice != defaultGoldPrice and currentGoldPrice.gold == 0

    def _subscribe(self):
        g_clientUpdateManager.addCallbacks({'shop': self.__onDiscountsChange,
         'goodies': self.__onDiscountsChange})

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onDiscountsChange(self, _):
        self.toggle(isOn=self.isOn())


class IsInSandBoxPreQueueTrigger(Trigger, IGlobalListener):

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            self.startGlobalListening()
        self.toggle(isOn=self.isOn())

    def isOn(self):
        state = self.prbDispatcher.getFunctionalState()
        return bool(state.isInPreQueue(queueType=QUEUE_TYPE.SANDBOX))

    def onPreQueueSettingsChanged(self, _):
        self.toggle(isOn=self.isOn())

    def onPrbEntitySwitched(self):
        self.toggle(isOn=self.isOn())

    def toggle(self, isOn=True, **kwargs):
        super(IsInSandBoxPreQueueTrigger, self).toggle(isOn=isOn, benefit=False)

    def clear(self):
        if self.isSubscribed:
            self.stopGlobalListening()
        self.isSubscribed = False
        self.isRunning = False


class IsInSandBoxOrRandomPreQueueTrigger(IsInSandBoxPreQueueTrigger):

    def isOn(self):
        state = self.prbDispatcher.getFunctionalState()
        return state.isInPreQueue(queueType=QUEUE_TYPE.SANDBOX) or state.isInPreQueue(queueType=QUEUE_TYPE.RANDOMS)

    def onPrbEntitySwitched(self):
        if self.isOn():
            self.toggle(isOn=True)


class FightButtonDisabledTrigger(Trigger, IGlobalListener):
    igrCtrl = dependency.descriptor(IIGRController)
    eventsCache = dependency.descriptor(IEventsCache)

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            self.startGlobalListening()
            g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
            g_currentVehicle.onChanged += self.__onVehicleChanged
            self.eventsCache.onSyncCompleted += self.__onEventsCacheResync
            self.igrCtrl.onIgrTypeChanged -= self.__onIGRChanged
        self.toggle(isOn=self.isOn())

    def clear(self):
        if self.isSubscribed:
            self.stopGlobalListening()
            g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
            g_currentVehicle.onChanged -= self.__onVehicleChanged
            self.eventsCache.onSyncCompleted -= self.__onEventsCacheResync
            self.igrCtrl.onIgrTypeChanged -= self.__onIGRChanged
        self.isSubscribed = False
        self.isRunning = False

    def isOn(self):
        items = battle_selector_items.getItems()
        state = self.prbDispatcher.getFunctionalState()
        selected = items.update(state)
        result = self.prbEntity.canPlayerDoAction()
        isFightBtnDisabled = not result.isValid or selected.isFightButtonForcedDisabled()
        return isFightBtnDisabled

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.toggle(isOn=self.isOn())

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.toggle(isOn=self.isOn())

    def onPrbEntitySwitched(self):
        self.toggle(isOn=self.isOn())

    def onPreQueueSettingsChanged(self, _):
        self.toggle(isOn=self.isOn())

    def __handleFightButtonUpdated(self, _):
        self.toggle(isOn=self.isOn())

    def __onVehicleChanged(self, *args):
        self.toggle(isOn=self.isOn())

    def __onEventsCacheResync(self, *args):
        self.toggle(isOn=self.isOn())

    def __onIGRChanged(self, *args):
        self.toggle(isOn=self.isOn())
