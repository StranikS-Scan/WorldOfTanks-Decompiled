# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/entity.py
import logging
import BigWorld
from constants import QUEUE_TYPE
from gui.prb_control.entities.event import isHangarShallBeLoaded
from helpers import dependency
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueEntity, PreQueueSubscriber
from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
from gui.prb_control.entities.event.pre_queue.vehicles_watcher import EventBattlesVehiclesWatcher
from gui.prb_control.entities.event.pre_queue.actions_validator import EventBattleActionsValidator
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from gui.periodic_battles.models import PrimeTimeStatus
from soft_exception import SoftException
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)

class EventBattleEntryPoint(PreQueueEntryPoint):
    __gameEventController = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        super(EventBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, QUEUE_TYPE.EVENT_BATTLES)

    def select(self, ctx, callback=None):
        status, _, _ = self.__gameEventController.getPrimeTimeStatus()
        if status == PrimeTimeStatus.FROZEN:
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(EventBattleEntryPoint, self).select(ctx, callback)
            return


class EventBattleEntity(PreQueueEntity):
    gameEventController = dependency.descriptor(IEventBattlesController)
    prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self):
        super(EventBattleEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, QUEUE_TYPE.EVENT_BATTLES, PreQueueSubscriber())
        self.storage = prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)()
        self.__watcher = None
        self.__waitForRequeue = False
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = EventBattlesVehiclesWatcher()
        self.__watcher.start()
        g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and isHangarShallBeLoaded(ctx):
            g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).fini(ctx, woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName in (PREBATTLE_ACTION_NAME.EVENT_BATTLE,) else super(EventBattleEntity, self).doSelectAction(action)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(EventBattleEntity, self).queue(ctx, callback=callback)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(EventBattleEntity, self).leave(ctx, callback=callback)

    def requeue(self, vehicle):
        if not self.isInQueue():
            raise SoftException('Player is not in the queue')
        self.doAction()
        self.prebattleVehicle.select(vehicle)
        self.__waitForRequeue = True

    def onEnqueued(self, *args):
        super(EventBattleEntity, self).onEnqueued(*args)
        self.__waitForRequeue = False

    def onDequeued(self, *args):
        super(EventBattleEntity, self).onDequeued(*args)
        if self.__waitForRequeue:
            self.__waitForRequeue = False
            if self.gameEventController.getQuickTicketCount() or self.gameEventController.getQuickHunterTicketCount():
                self.doAction()

    def _createActionsValidator(self):
        return EventBattleActionsValidator(self)

    def _createScheduler(self):
        return EventScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the event battles %s', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles()
        _logger.debug('Sends request on dequeuing from the event battles')

    def _makeQueueCtxByAction(self, action=None):
        vehicle = self.prebattleVehicle.item
        if not vehicle:
            raise SoftException('Vehicle cannot be None')
        invID = vehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return EventBattleQueueCtx(vehInvID=invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadEventBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
