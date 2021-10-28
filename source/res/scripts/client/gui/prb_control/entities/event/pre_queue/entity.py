# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/entity.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.event.pre_queue.actions_validator import EventActionsValidator
from gui.prb_control.items import SelectResult
from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.prb_getters import isInEventBattlesQueue
from CurrentVehicle import g_currentVehicle
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_event_controller import IGameEventController

class EventBattleSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattles += entity.onEnqueued
        g_playerEvents.onDequeuedEventBattles += entity.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattles += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattles -= entity.onEnqueued
        g_playerEvents.onDequeuedEventBattles -= entity.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattles -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class EventBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(EventBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, QUEUE_TYPE.EVENT_BATTLES)


class EventBattleEntity(PreQueueEntity):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(EventBattleEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, QUEUE_TYPE.EVENT_BATTLES, EventBattleSubscriber())
        self.__eventStartQueuedTime = 0.0

    @property
    def eventStartQueuedTime(self):
        return self.__eventStartQueuedTime

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.EVENT_BATTLE:
            g_eventDispatcher.loadHangar()
            return SelectResult(True)
        return super(EventBattleEntity, self).doSelectAction(action)

    def isInQueue(self):
        return isInEventBattlesQueue()

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(EventBattleEntity, self).leave(ctx, callback=callback)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(EventBattleEntity, self).queue(ctx, callback=callback)

    def _makeQueueCtxByAction(self, action=None):
        return EventBattleQueueCtx([g_currentVehicle.item.invID], difficultyLevel=self.gameEventController.getSelectedDifficultyLevel(), waitingID='prebattle/join')

    def _doQueue(self, ctx):
        LOG_DEBUG_DEV('EventBattleEntity _doQueue level', ctx.getDifficultyLevel())
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryIDs(), ctx.getDifficultyLevel())
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles()
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _goToQueueUI(self):
        self.__eventStartQueuedTime = BigWorld.time()
        g_eventDispatcher.loadEventBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def _createActionsValidator(self):
        return EventActionsValidator(self)

    def _createScheduler(self):
        return EventScheduler(self)
