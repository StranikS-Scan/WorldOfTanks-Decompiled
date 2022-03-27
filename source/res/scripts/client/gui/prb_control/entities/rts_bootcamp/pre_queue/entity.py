# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_bootcamp/pre_queue/entity.py
import logging
import typing
import BigWorld
from constants import QUEUE_TYPE
from gui.impl.gen import R
from gui.prb_control import prb_getters, prbDispatcherProperty
from gui.prb_control.items import SelectResult
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntity
from gui.prb_control.entities.rts_bootcamp.pre_queue.actions_validator import RTSBootcampActionsValidator
from gui.prb_control.entities.rts_bootcamp.pre_queue.ctx import RTSBootcampBattleQueueCtx
from gui.prb_control.entities.rts_bootcamp.pre_queue.permissions import RTSBootcampPermissions
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.prb_control.entity import PeriodicEntryPoint
from gui.periodic_battles.prb_control.scheduler import PeriodicScheduler
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IRTSBattlesController
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
logger = logging.getLogger(__name__)

class RTSBootcampScheduler(PeriodicScheduler):
    _RES_ROOT = R.strings.system_messages.rts
    _controller = dependency.descriptor(IRTSBattlesController)


class _RTSBootcampSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedRTSBootcamp += entity.onEnqueued
        g_playerEvents.onDequeuedRTSBootcamp += entity.onDequeued
        g_playerEvents.onEnqueuedRTSBootcampFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromRTSBootcampQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedRTSBootcamp -= entity.onEnqueued
        g_playerEvents.onDequeuedRTSBootcamp -= entity.onDequeued
        g_playerEvents.onEnqueuedRTSBootcampFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromRTSBootcampQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class RTSBootcampEntryPoint(PeriodicEntryPoint):
    _RES_ROOT = R.strings.system_messages.rts
    _controller = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        super(RTSBootcampEntryPoint, self).__init__(FUNCTIONAL_FLAG.RTS_BOOTCAMP, QUEUE_TYPE.RTS_BOOTCAMP)


class RTSBootcampEntity(PreQueueEntity):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, isCreatedByDefault=False):
        super(RTSBootcampEntity, self).__init__(FUNCTIONAL_FLAG.RTS_BOOTCAMP, QUEUE_TYPE.RTS_BOOTCAMP, _RTSBootcampSubscriber())
        self._delayedInitTimer = None
        self._isCreatedByDefault = isCreatedByDefault
        return

    @prequeue_storage_getter(QUEUE_TYPE.RTS_BOOTCAMP)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self._delayedInitTimer = BigWorld.callback(0.0, self._delayedInit)
        return super(RTSBootcampEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if self._delayedInitTimer is not None:
            BigWorld.cancelCallback(self._delayedInitTimer)
            self._delayedInitTimer = None
        g_eventDispatcher.loadHangar()
        return super(RTSBootcampEntity, self).fini(ctx, woEvents)

    def queue(self, ctx, callback=None):
        super(RTSBootcampEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        return SelectResult(True, None) if action.actionName == PREBATTLE_ACTION_NAME.RTS_BOOTCAMP else super(RTSBootcampEntity, self).doSelectAction(action)

    def isInQueue(self):
        return prb_getters.isInRTSBootcampQueue()

    def getPermissions(self, pID=None, **kwargs):
        return RTSBootcampPermissions(self.isInQueue())

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(RTSBootcampEntity, self).leave(ctx, callback=callback)

    def _delayedInit(self):
        self._delayedInitTimer = None
        if self._isCreatedByDefault:
            self.__rtsController.returnFromRTSBootcamp()
        elif not self.isInQueue():
            self.queue(self._makeQueueCtxByAction(), self._delayedQueueCallback)
        return

    def _delayedQueueCallback(self, success):
        if not success:
            self._exitFromQueueUI()

    def _createActionsValidator(self):
        return RTSBootcampActionsValidator(self)

    def _createScheduler(self):
        return RTSBootcampScheduler(self)

    def _makeQueueCtxByAction(self, action=None):
        return RTSBootcampBattleQueueCtx(waitingID='prebattle/join')

    def _doQueue(self, ctx):
        logger.debug('Sends request on queuing to the RTS 1x1 battles')
        BigWorld.player().enqueueRTSBootcampBattles()

    def _doDequeue(self, ctx):
        logger.debug('Sends request on dequeuing from the RTS 1x1 battles')
        BigWorld.player().dequeueRTSBootcampBattles()

    def _goToQueueUI(self):
        g_eventDispatcher.loadRTSBootcampQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _exitFromQueueUI(self):
        self.__rtsController.returnFromRTSBootcamp()
