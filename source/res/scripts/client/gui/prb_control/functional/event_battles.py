# Embedded file name: scripts/client/gui/prb_control/functional/event_battles.py
import BigWorld
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from PlayerEvents import g_playerEvents
from gui.prb_control.prb_getters import isInEventBattlesQueue
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.functional import prequeue
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.prb_control.storage import prequeue_storage_getter

class _EventBattlesEventsSubscriber(prequeue.PlayersEventsSubscriber):

    def subscribe(self, functional):
        g_playerEvents.onEnqueuedEventBattles += functional.onEnqueued
        g_playerEvents.onDequeuedEventBattles += functional.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure += functional.onEnqueueError
        g_playerEvents.onKickedFromEventBattles += functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena += functional.onKickedFromArena

    def unsubscribe(self, functional):
        g_playerEvents.onEnqueuedEventBattles -= functional.onEnqueued
        g_playerEvents.onDequeuedEventBattles -= functional.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure -= functional.onEnqueueError
        g_playerEvents.onKickedFromEventBattles -= functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= functional.onKickedFromArena


class EventBattlesQueueFunctional(prequeue.AccountQueueFunctional):

    def __init__(self, flags = FUNCTIONAL_FLAG.EVENT_BATTLES):
        super(EventBattlesQueueFunctional, self).__init__(QUEUE_TYPE.EVENT_BATTLES, _EventBattlesEventsSubscriber(), flags)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def isInQueue(self):
        return isInEventBattlesQueue()

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryIDs(), ctx.getBattleType(), canAddToSquad=ctx.canAddToSquad())
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles()
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
