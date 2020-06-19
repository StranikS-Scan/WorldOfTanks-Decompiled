# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/pre_queue/entity.py
import BigWorld
import ArenaType
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers import gameplay_ctx
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prb_getters
from gui.prb_control.entities.random.pre_queue.actions_validator import RandomActionsValidator
from gui.prb_control.entities.random.pre_queue.scheduler import RandomScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.random.pre_queue.ctx import RandomQueueCtx
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, REQUEST_TYPE
from soft_exception import SoftException
from vehicles_watcher import RandomVehiclesWatcher

class RandomSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedRandom += entity.onEnqueued
        g_playerEvents.onDequeuedRandom += entity.onDequeued
        g_playerEvents.onEnqueueRandomFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromRandomQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure
        g_playerEvents.onKickedFromEventBattles += entity.onKickedFromEventBattles

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedRandom -= entity.onEnqueued
        g_playerEvents.onDequeuedRandom -= entity.onDequeued
        g_playerEvents.onEnqueueRandomFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromRandomQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure
        g_playerEvents.onKickedFromEventBattles -= entity.onKickedFromEventBattles


class RandomEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(RandomEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.RANDOMS)


class RandomEntity(PreQueueEntity):

    def __init__(self):
        super(RandomEntity, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.RANDOMS, RandomSubscriber())
        self.__watcher = None
        return

    def isInQueue(self):
        return prb_getters.isInRandomQueue()

    def init(self, ctx=None):
        self.__watcher = RandomVehiclesWatcher()
        self.__watcher.start()
        return super(RandomEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(RandomEntity, self).fini(ctx, woEvents)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(RandomEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.RANDOM else super(RandomEntity, self).doSelectAction(action)

    def onKickedFromEventBattles(self, *args):
        if self._requestCtx.getRequestType() == REQUEST_TYPE.QUEUE:
            self._requestCtx.stopProcessing(True)
        self._invokeListeners('onKickedFromQueue', QUEUE_TYPE.EVENT_BATTLES, *args)
        self._exitFromQueueUI()
        SystemMessages.pushI18nMessage(backport.text(R.strings.system_messages.arena_start_errors.join.EVENT_DISABLED()), type=SystemMessages.SM_TYPE.Error)

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
            raise SoftException('Inventory ID of vehicle can not be zero')
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

    def _createActionsValidator(self):
        return RandomActionsValidator(self)

    def _createScheduler(self):
        return RandomScheduler(self)
