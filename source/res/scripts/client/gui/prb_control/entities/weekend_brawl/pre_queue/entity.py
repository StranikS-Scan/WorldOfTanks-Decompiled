# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/weekend_brawl/pre_queue/entity.py
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control import prb_getters
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.entities.weekend_brawl.pre_queue.vehicles_watcher import WeekendBrawlVehiclesWatcher
from gui.prb_control.entities.weekend_brawl.scheduler import WeekendBrawlScheduler
from gui.prb_control.entities.weekend_brawl.pre_queue.actions_validator import WeekendBrawlActionsValidator
from gui.prb_control.entities.weekend_brawl.pre_queue.ctx import WeekendBrawlQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.ranked_battles.constants import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IWeekendBrawlController
from gui.shared.event_dispatcher import showWeekendBrawlPrimeTimeWindow
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl import backport
from soft_exception import SoftException

class _WeekendBrawlSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure
        g_playerEvents.onEnqueuedWeekendBrawl += entity.onEnqueued
        g_playerEvents.onDequeuedWeekendBrawl += entity.onDequeued
        g_playerEvents.onEnqueuedWeekendBrawlFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromWeekendBrawlQueue += entity.onKickedFromQueue

    def unsubscribe(self, entity):
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure
        g_playerEvents.onEnqueuedWeekendBrawl -= entity.onEnqueued
        g_playerEvents.onDequeuedWeekendBrawl -= entity.onDequeued
        g_playerEvents.onEnqueuedWeekendBrawlFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromWeekendBrawlQueue -= entity.onKickedFromQueue


class WeekendBrawlEntryPoint(PreQueueEntryPoint):
    __wBrawlController = dependency.descriptor(IWeekendBrawlController)

    def __init__(self):
        super(WeekendBrawlEntryPoint, self).__init__(FUNCTIONAL_FLAG.WEEKEND_BRAWL, QUEUE_TYPE.WEEKEND_BRAWL)

    def select(self, ctx, callback=None):
        status, _, _ = self.__wBrawlController.getPrimeTimeStatus()
        if status in (PrimeTimeStatus.DISABLED, PrimeTimeStatus.FROZEN, PrimeTimeStatus.NO_SEASON):
            SystemMessages.pushMessage(backport.text(R.strings.weekend_brawl.systemMessage.notAvailable()), type=SystemMessages.SM_TYPE.Error)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif status in self._getFilterStates():
            showWeekendBrawlPrimeTimeWindow()
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
            return
        else:
            super(WeekendBrawlEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.NOT_AVAILABLE)


class WeekendBrawlForcedEntryPoint(WeekendBrawlEntryPoint):

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class WeekendBrawlEntity(PreQueueEntity):

    def __init__(self):
        super(WeekendBrawlEntity, self).__init__(FUNCTIONAL_FLAG.WEEKEND_BRAWL, QUEUE_TYPE.WEEKEND_BRAWL, _WeekendBrawlSubscriber())
        self.__watcher = None
        return

    @prequeue_storage_getter(QUEUE_TYPE.WEEKEND_BRAWL)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = WeekendBrawlVehiclesWatcher()
        self.__watcher.start()
        result = super(WeekendBrawlEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(WeekendBrawlEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(WeekendBrawlEntity, self).leave(ctx, callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name in (PREBATTLE_ACTION_NAME.WEEKEND_BRAWL, PREBATTLE_ACTION_NAME.WEEKEND_BRAWL_FORCED) else super(WeekendBrawlEntity, self).doSelectAction(action)

    def isInQueue(self):
        return prb_getters.isInWeekendBrawlQueue()

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(WeekendBrawlEntity, self).queue(ctx, callback=callback)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return WeekendBrawlQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return WeekendBrawlActionsValidator(self)

    def _createScheduler(self):
        return WeekendBrawlScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueWeekendBrawl(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the WeekendBrawl battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueWeekendBrawl()
        LOG_DEBUG('Sends request on dequeuing from the WeekendBrawl battle')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
