# Embedded file name: scripts/client/gui/prb_control/functional/sandbox_queue.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE, MAX_VEHICLE_LEVEL, PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters
from gui.prb_control.context import pre_queue_ctx
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.functional import prequeue
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import SANDBOX_MAX_VEHICLE_LEVEL, QUEUE_RESTRICTION, FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storage import prequeue_storage_getter
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.gui_items.Vehicle import Vehicle

class _VehiclesWatcher(object):

    def start(self):
        self.__setUnsuitableState()
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryChanged})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__clearUnsuitableState()

    def __getUnsuitableVehicles(self):
        return g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(range(SANDBOX_MAX_VEHICLE_LEVEL + 1, MAX_VEHICLE_LEVEL + 1))).itervalues()

    def __setUnsuitableState(self):
        vehicles = self.__getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.setCustomState(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __clearUnsuitableState(self):
        vehicles = self.__getUnsuitableVehicles()
        intCDs = set()
        for vehicle in vehicles:
            vehicle.clearCustomState()
            intCDs.add(vehicle.intCD)

        if intCDs:
            g_prbCtrlEvents.onVehicleClientStateChanged(intCDs)

    def __onInventoryChanged(self, _):
        self.__setUnsuitableState()


class _SandboxEventsSubscriber(prequeue.PlayersEventsSubscriber):

    def subscribe(self, functional):
        g_playerEvents.onEnqueuedSandbox += functional.onEnqueued
        g_playerEvents.onDequeuedSandbox += functional.onDequeued
        g_playerEvents.onEnqueuedSandboxFailure += functional.onEnqueueError
        g_playerEvents.onKickedFromSandboxQueue += functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena += functional.onKickedFromArena

    def unsubscribe(self, functional):
        g_playerEvents.onEnqueuedSandbox -= functional.onEnqueued
        g_playerEvents.onDequeuedSandbox -= functional.onDequeued
        g_playerEvents.onEnqueuedSandboxFailure -= functional.onEnqueueError
        g_playerEvents.onKickedFromSandboxQueue -= functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= functional.onKickedFromArena


class SandboxQueueFunctional(prequeue.AccountQueueFunctional):

    def __init__(self):
        super(SandboxQueueFunctional, self).__init__(QUEUE_TYPE.SANDBOX, _SandboxEventsSubscriber(), FUNCTIONAL_FLAG.SANDBOX)
        self.__watcher = None
        return

    @prequeue_storage_getter(QUEUE_TYPE.SANDBOX)
    def storage(self):
        return None

    def init(self, ctx = None):
        self.storage.release()
        self.__watcher = _VehiclesWatcher()
        self.__watcher.start()
        g_lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        return super(SandboxQueueFunctional, self).init(ctx)

    def fini(self, woEvents = False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and self._flags & FUNCTIONAL_FLAG.SWITCH == 0:
            if self._flags & FUNCTIONAL_FLAG.RANDOM_BATTLES == FUNCTIONAL_FLAG.RANDOM_BATTLES:
                self.storage.suspend()
        g_lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(SandboxQueueFunctional, self).fini(woEvents)
        return

    def isInQueue(self):
        return prb_getters.isInSandboxQueue()

    @vehicleAmmoCheck
    def queue(self, ctx, callback = None):
        super(SandboxQueueFunctional, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        isProcessed = False
        if action.actionName == PREBATTLE_ACTION_NAME.SANDBOX:
            isProcessed = True
        return SelectResult(isProcessed, None)

    def canPlayerDoAction(self):
        if not g_currentVehicle.isPresent():
            return (False, '')
        else:
            vehicle = g_currentVehicle.item
            if vehicle.level <= SANDBOX_MAX_VEHICLE_LEVEL:
                return super(SandboxQueueFunctional, self).canPlayerDoAction()
            return (False, QUEUE_RESTRICTION.LIMIT_LEVEL)

    def getConfirmDialogMeta(self, ctx):
        if not self.hasLockedState() and ctx.getEntityType() == PREBATTLE_TYPE.SQUAD:
            meta = rally_dialog_meta.createLeavePreQueueMeta(ctx, self._queueType)
        else:
            meta = super(SandboxQueueFunctional, self).getConfirmDialogMeta(ctx)
        return meta

    def _doQueue(self, ctx):
        BigWorld.player().enqueueSandbox(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the PvE tutorial battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueSandbox()
        LOG_DEBUG('Sends request on dequeuing from the PvE tutorial battle')

    def _makeQueueCtxByAction(self, action = None):
        invID = g_currentVehicle.invID
        raise invID or AssertionError('Inventory ID of vehicle can not be zero')
        return pre_queue_ctx.SandboxQueueCtx(invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadSandboxQueue()
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def _exitFromQueueUI(self):
        g_eventDispatcher.unloadSandboxQueue()

    def __onServerSettingChanged(self, *args):
        if not g_lobbyContext.getServerSettings().isSandboxEnabled():

            def __leave(_ = True):
                g_prbCtrlEvents.onPreQueueFunctionalDestroyed()

            if self.isInQueue():
                self.dequeue(pre_queue_ctx.DequeueCtx(waitingID='prebattle/leave'), callback=__leave)
            else:
                __leave()
