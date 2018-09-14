# Embedded file name: scripts/client/gui/prb_control/factories/PreQueueFactory.py
import inspect
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.context.pre_queue_ctx import LeavePreQueueCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional import battle_tutorial
from gui.prb_control.functional import not_supported
from gui.prb_control.functional import fallout
from gui.prb_control.functional import prequeue
from gui.prb_control.functional import random
from gui.prb_control.functional import sandbox_queue
from gui.prb_control.items import FunctionalState
import gui.prb_control.prb_getters
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.prb_control.settings import FUNCTIONAL_FLAG as _FLAG
from gui.prb_control.storage import prequeue_storage_getter
__all__ = ('PreQueueFactory',)
_SUPPORTED_QUEUES = {QUEUE_TYPE.RANDOMS: random.RandomQueueFunctional,
 QUEUE_TYPE.EVENT_BATTLES: fallout.FalloutQueueFunctional,
 QUEUE_TYPE.TUTORIAL: battle_tutorial.TutorialQueueFunctional,
 QUEUE_TYPE.SANDBOX: sandbox_queue.SandboxQueueFunctional}
_SUPPORTED_ENTRY_BY_ACTION = {PREBATTLE_ACTION_NAME.RANDOM_QUEUE: (prequeue.PreQueueEntry, (QUEUE_TYPE.RANDOMS, _FLAG.UNDEFINED)),
 PREBATTLE_ACTION_NAME.FALLOUT: (fallout.FalloutEntry, None),
 PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL: (battle_tutorial.TutorialPreQueueEntry, None),
 PREBATTLE_ACTION_NAME.SANDBOX: (prequeue.PreQueueEntry, (QUEUE_TYPE.SANDBOX, _FLAG.UNDEFINED))}

class PreQueueFactory(ControlFactory):

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def eventsStorage(self):
        return None

    @prequeue_storage_getter(QUEUE_TYPE.SANDBOX)
    def pveStorage(self):
        return None

    def createEntry(self, ctx):
        LOG_ERROR('preQueue functional has not any entries')
        return None

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createFunctional(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.PREQUEUE:
            if ctx.hasFlags(_FLAG.SWITCH) and (ctx.hasFlags(_FLAG.LEAVE_ENTITY) or ctx.hasFlags(_FLAG.LEAVE_INTRO)):
                created = None
            else:
                queueType = ctx.getEntityType()
                if queueType:
                    created = self._createByQueueType(queueType, ctx)
                else:
                    created = self._createDefaultFunctional(ctx)
        else:
            created = self._createByAccountState(ctx)
        return created

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.PREQUEUE, functional.getEntityType(), True, functional.isInQueue())

    def createLeaveCtx(self, flags = _FLAG.UNDEFINED):
        return LeavePreQueueCtx(waitingID='prebattle/leave', flags=flags)

    def _createByAccountState(self, ctx):
        queueType = gui.prb_control.prb_getters.getQueueType()
        if queueType:
            created = self._createByQueueType(queueType, ctx)
        else:
            created = self._createDefaultFunctional(ctx)
        return created

    def _createByQueueType(self, queueType, ctx):
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.PREQUEUE:
            return self._createDefaultFunctional(ctx)
        ctx.removeFlags(_FLAG.PRE_QUEUE_BITMASK)
        clazz = queueType in _SUPPORTED_QUEUES and _SUPPORTED_QUEUES[queueType]
        if not inspect.isclass(clazz):
            raise AssertionError('Class is not found, checks settings')
            created = clazz()
            ctx.addFlags(created.getFunctionalFlags())
        else:
            LOG_ERROR('Queue with given type is not supported', queueType)
            ctx.addFlags(_FLAG.PRE_QUEUE)
            created = not_supported.NotSupportedFunctional()
        return created

    def _createDefaultFunctional(self, ctx):
        created = None
        if ctx.hasFlags(_FLAG.NO_PREBATTLE) and ctx.hasFlags(_FLAG.NO_UNIT):
            isProcessed, created = self._createDefaultByStorage(ctx)
            if not isProcessed:
                if not ctx.hasFlags(_FLAG.RANDOM_BATTLES):
                    ctx.removeFlags(_FLAG.PRE_QUEUE_BITMASK)
                    created = random.RandomQueueFunctional()
                    ctx.addFlags(created.getFunctionalFlags())
        elif not ctx.hasFlags(_FLAG.NO_QUEUE):
            ctx.removeFlags(_FLAG.PRE_QUEUE_BITMASK)
            created = prequeue.NoPreQueueFunctional()
            ctx.addFlags(created.getFunctionalFlags())
        return created

    def _createDefaultByStorage(self, ctx):
        if self.eventsStorage.isModeSelected():
            if not ctx.hasFlags(_FLAG.EVENT_BATTLES):
                ctx.removeFlags(_FLAG.PRE_QUEUE_BITMASK)
                created = fallout.FalloutQueueFunctional()
                ctx.addFlags(created.getFunctionalFlags())
            else:
                created = None
            return (True, created)
        elif self.pveStorage.isModeSelected():
            if not ctx.hasFlags(_FLAG.SANDBOX):
                ctx.removeFlags(_FLAG.PRE_QUEUE_BITMASK)
                created = sandbox_queue.SandboxQueueFunctional()
                ctx.addFlags(created.getFunctionalFlags())
            else:
                created = None
            return (True, created)
        else:
            return (False, None)
