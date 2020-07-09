# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/pre_queue/entity.py
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.entities.bob.pre_queue.vehicles_watcher import BobVehiclesWatcher
from gui.prb_control.entities.bob.scheduler import BobScheduler
from gui.prb_control.entities.bob.pre_queue.actions_validator import BobActionsValidator
from gui.prb_control.entities.bob.pre_queue.ctx import BobQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IBobController
from gui.shared.event_dispatcher import showBobPrimeTimeWindow
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl import backport
from soft_exception import SoftException

class _BobSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure
        g_playerEvents.onEnqueuedBob += entity.onEnqueued
        g_playerEvents.onDequeuedBob += entity.onDequeued
        g_playerEvents.onEnqueuedBobFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromBobQueue += entity.onKickedFromQueue

    def unsubscribe(self, entity):
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure
        g_playerEvents.onEnqueuedBob -= entity.onEnqueued
        g_playerEvents.onDequeuedBob -= entity.onDequeued
        g_playerEvents.onEnqueuedBobFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromBobQueue -= entity.onKickedFromQueue


class BobEntryPoint(PreQueueEntryPoint):
    __bobController = dependency.descriptor(IBobController)

    def __init__(self):
        super(BobEntryPoint, self).__init__(FUNCTIONAL_FLAG.BOB, QUEUE_TYPE.BOB)

    def select(self, ctx, callback=None):
        status, _, _ = self.__bobController.getPrimeTimeStatus()
        if status in (PrimeTimeStatus.DISABLED, PrimeTimeStatus.FROZEN, PrimeTimeStatus.NO_SEASON):
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.arena_start_errors.join.EVENT_DISABLED()), type=SystemMessages.SM_TYPE.Error)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif status in self._getFilterStates():
            showBobPrimeTimeWindow()
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
            return
        else:
            super(BobEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.NOT_AVAILABLE)


class BobForcedEntryPoint(BobEntryPoint):

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class BobEntity(PreQueueEntity):

    def __init__(self):
        super(BobEntity, self).__init__(FUNCTIONAL_FLAG.BOB, QUEUE_TYPE.BOB, _BobSubscriber())
        self.__watcher = None
        return

    @prequeue_storage_getter(QUEUE_TYPE.BOB)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BobVehiclesWatcher()
        self.__watcher.start()
        result = super(BobEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(BobEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(BobEntity, self).leave(ctx, callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name in (PREBATTLE_ACTION_NAME.BOB, PREBATTLE_ACTION_NAME.BOB_FORCED) else super(BobEntity, self).doSelectAction(action)

    def isInQueue(self):
        return prb_getters.isInBobQueue()

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(BobEntity, self).queue(ctx, callback=callback)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return BobQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return BobActionsValidator(self)

    def _createScheduler(self):
        return BobScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueBob(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the Battle of Bloggers', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueBob()
        LOG_DEBUG('Sends request on dequeuing from the Battle of Bloggers')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
