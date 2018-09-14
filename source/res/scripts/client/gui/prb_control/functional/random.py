# Embedded file name: scripts/client/gui/prb_control/functional/random.py
import BigWorld
import ArenaType
from CurrentVehicle import g_currentVehicle
from account_helpers import gameplay_ctx
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from PlayerEvents import g_playerEvents
from gui.prb_control import prb_getters
from gui.prb_control.context import pre_queue_ctx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.functional import prequeue
from gui.prb_control.functional import unit
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
__all__ = ('RandomQueueFunctional',)

class _RandomEventsSubscriber(prequeue.PlayersEventsSubscriber):

    def subscribe(self, functional):
        g_playerEvents.onEnqueuedRandom += functional.onEnqueued
        g_playerEvents.onDequeuedRandom += functional.onDequeued
        g_playerEvents.onEnqueueRandomFailure += functional.onEnqueueError
        g_playerEvents.onKickedFromRandomQueue += functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena += functional.onKickedFromArena

    def unsubscribe(self, functional):
        g_playerEvents.onEnqueuedRandom -= functional.onEnqueued
        g_playerEvents.onDequeuedRandom -= functional.onDequeued
        g_playerEvents.onEnqueueRandomFailure -= functional.onEnqueueError
        g_playerEvents.onKickedFromRandomQueue -= functional.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= functional.onKickedFromArena


class RandomQueueFunctional(prequeue.AccountQueueFunctional):

    def __init__(self):
        super(RandomQueueFunctional, self).__init__(QUEUE_TYPE.RANDOMS, _RandomEventsSubscriber(), FUNCTIONAL_FLAG.RANDOM_BATTLES)

    def isInQueue(self):
        return prb_getters.isInRandomQueue()

    @vehicleAmmoCheck
    def queue(self, ctx, callback = None):
        super(RandomQueueFunctional, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        isProcessed = False
        newEntry = None
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.SQUAD:
            newEntry = unit.SquadEntry(accountsToInvite=action.accountsToInvite)
            isProcessed = True
        elif name == PREBATTLE_ACTION_NAME.RANDOM_QUEUE:
            isProcessed = True
        return SelectResult(isProcessed, newEntry)

    def _doQueue(self, ctx):
        mapID = ctx.getDemoArenaTypeID()
        if mapID:
            LOG_DEBUG('Demonstrator mapID:', ArenaType.g_cache[mapID].geometryName)
        BigWorld.player().enqueueRandom(ctx.getVehicleInventoryID(), gameplaysMask=ctx.getGamePlayMask(), arenaTypeID=mapID)
        LOG_DEBUG('Sends request on queuing to the random battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueRandom()
        LOG_DEBUG('Sends request on dequeuing from the random battle')

    def _makeQueueCtxByAction(self, action = None):
        invID = g_currentVehicle.invID
        if not invID:
            raise AssertionError('Inventory ID of vehicle can not be zero')
            arenaTypeID = action is not None and action.mapID
        else:
            arenaTypeID = 0
        return pre_queue_ctx.RandomQueueCtx(invID, arenaTypeID=arenaTypeID, gamePlayMask=gameplay_ctx.getMask(), waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
