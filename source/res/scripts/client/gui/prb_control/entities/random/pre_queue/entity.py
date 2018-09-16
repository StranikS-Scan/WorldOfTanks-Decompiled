# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/pre_queue/entity.py
import BigWorld
import ArenaType
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers import gameplay_ctx
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control import prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.random.pre_queue.ctx import RandomQueueCtx
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG

class RandomSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedRandom += entity.onEnqueued
        g_playerEvents.onDequeuedRandom += entity.onDequeued
        g_playerEvents.onEnqueueRandomFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromRandomQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedRandom -= entity.onEnqueued
        g_playerEvents.onDequeuedRandom -= entity.onDequeued
        g_playerEvents.onEnqueueRandomFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromRandomQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class RandomEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(RandomEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.RANDOMS)


class RandomEntity(PreQueueEntity):

    def __init__(self):
        super(RandomEntity, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.RANDOMS, RandomSubscriber())

    def isInQueue(self):
        return prb_getters.isInRandomQueue()

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(RandomEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.RANDOM else super(RandomEntity, self).doSelectAction(action)

    def _doQueue(self, ctx):
        mapID = ctx.getDemoArenaTypeID()
        if mapID:
            LOG_DEBUG('Demonstrator mapID:', ArenaType.g_cache[mapID].geometryName)
        BigWorld.player().enqueueRandom(ctx.getVehicleInventoryID(), gameplaysMask=ctx.getGamePlayMask(), arenaTypeID=mapID)
        LOG_DEBUG('Sends request on queuing to the random battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueRandom()
        LOG_DEBUG('Sends request on dequeuing from the random battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise UserWarning('Inventory ID of vehicle can not be zero')
        if action is not None:
            arenaTypeID = action.mapID
        else:
            arenaTypeID = 0
        return RandomQueueCtx(invID, arenaTypeID=arenaTypeID, gamePlayMask=gameplay_ctx.getMask(), waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
