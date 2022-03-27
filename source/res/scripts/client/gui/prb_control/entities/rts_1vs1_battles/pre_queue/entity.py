# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_1vs1_battles/pre_queue/entity.py
import logging
import typing
import BigWorld
from actions_validator import RTS1x1ActionsValidator
from constants import QUEUE_TYPE
from gui.impl.gen import R
from gui.prb_control import prb_getters
from gui.prb_control.items import SelectResult
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntity
from gui.prb_control.entities.rts_1vs1_battles.pre_queue.ctx import RTS1x1BattleQueueCtx
from gui.prb_control.entities.rts_1vs1_battles.pre_queue.permissions import RTS1x1Permissions
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.prb_control.entity import PeriodicEntryPoint
from gui.periodic_battles.prb_control.scheduler import PeriodicScheduler
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
logger = logging.getLogger(__name__)

class RTS1x1Scheduler(PeriodicScheduler):
    _RES_ROOT = R.strings.system_messages.rts
    _controller = dependency.descriptor(IRTSBattlesController)


class _RTS1x1BattleSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedRTS1x1 += entity.onEnqueued
        g_playerEvents.onDequeuedRTS1x1 += entity.onDequeued
        g_playerEvents.onEnqueuedRTS1x1Failure += entity.onEnqueueError
        g_playerEvents.onKickedFromRTS1x1Queue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedRTS1x1 -= entity.onEnqueued
        g_playerEvents.onDequeuedRTS1x1 -= entity.onDequeued
        g_playerEvents.onEnqueuedRTS1x1Failure -= entity.onEnqueueError
        g_playerEvents.onKickedFromRTS1x1Queue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class RTS1x1BattleEntryPoint(PeriodicEntryPoint):
    _RES_ROOT = R.strings.system_messages.rts
    _controller = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        super(RTS1x1BattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.RTS_1x1, QUEUE_TYPE.RTS_1x1)


class RTS1x1BattleEntity(PreQueueEntity):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        super(RTS1x1BattleEntity, self).__init__(FUNCTIONAL_FLAG.RTS_1x1, QUEUE_TYPE.RTS_1x1, _RTS1x1BattleSubscriber())

    @prequeue_storage_getter(QUEUE_TYPE.RTS_1x1)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        return super(RTS1x1BattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        g_eventDispatcher.loadHangar()
        return super(RTS1x1BattleEntity, self).fini(ctx, woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.RTS_1x1 else super(RTS1x1BattleEntity, self).doSelectAction(action)

    def isInQueue(self):
        return prb_getters.isInRTS1x1Queue()

    def getPermissions(self, pID=None, **kwargs):
        return RTS1x1Permissions(self.isInQueue())

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(RTS1x1BattleEntity, self).leave(ctx, callback=callback)

    def _createActionsValidator(self):
        return RTS1x1ActionsValidator(self)

    def _createScheduler(self):
        return RTS1x1Scheduler(self)

    def _makeQueueCtxByAction(self, action=None):
        return RTS1x1BattleQueueCtx(waitingID='prebattle/join')

    def _doQueue(self, ctx):
        logger.debug('Sends request on queuing to the RTS 1x1 battles')
        BigWorld.player().enqueueRTS1vs1Battles()

    def _doDequeue(self, ctx):
        logger.debug('Sends request on dequeuing from the RTS 1x1 battles')
        BigWorld.player().dequeueRTS1vs1Battles()

    def _goToQueueUI(self):
        g_eventDispatcher.loadRTS1x1BattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
