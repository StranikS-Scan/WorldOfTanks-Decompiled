# Embedded file name: scripts/client/gui/prb_control/factories/PreQueueFactory.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.context.pre_queue_ctx import LeavePreQueueCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional.no_prebattle import NoPreQueueFunctional
from gui.prb_control.functional.not_supported import QueueNotSupportedFunctional
from gui.prb_control.functional.random_queue import RandomQueueFunctional
from gui.prb_control.functional.historical import HistoricalQueueFunctional
from gui.prb_control.functional.event_battles import EventBattlesQueueFunctional
from gui.prb_control.items import FunctionalState
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
_SUPPORTED_QUEUES = {QUEUE_TYPE.RANDOMS: RandomQueueFunctional,
 QUEUE_TYPE.HISTORICAL: HistoricalQueueFunctional,
 QUEUE_TYPE.EVENT_BATTLES: EventBattlesQueueFunctional}

class PreQueueFactory(ControlFactory):

    def createEntry(self, ctx):
        LOG_ERROR('preQueue functional has not any entries')
        return None

    def createFunctional(self, dispatcher, ctx):
        createParams = ctx.getCreateParams()
        if 'queueType' in createParams:
            queueType = createParams['queueType']
        else:
            queueType = None
        if queueType:
            queueType = createParams['queueType']
            if 'settings' in createParams:
                settings = createParams['settings']
            else:
                settings = None
            if queueType in _SUPPORTED_QUEUES:
                preQueueFunctional = _SUPPORTED_QUEUES[queueType](settings)
                for listener in dispatcher._globalListeners:
                    preQueueFunctional.addListener(listener())

            else:
                LOG_ERROR('Queue with given type is not supported', queueType)
                preQueueFunctional = QueueNotSupportedFunctional(queueType)
        else:
            preQueueFunctional = NoPreQueueFunctional()
        return preQueueFunctional

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.PREQUEUE, functional.getQueueType(), True)

    def createLeaveCtx(self):
        return LeavePreQueueCtx(waitingID='prebattle/leave')

    def getLeaveCtxByAction(self, action):
        ctx = None
        if action in [PREBATTLE_ACTION_NAME.LEAVE_RANDOM_QUEUE,
         PREBATTLE_ACTION_NAME.LEAVE_EVENT_BATTLES_QUEUE,
         PREBATTLE_ACTION_NAME.LEAVE_HISTORICAL,
         PREBATTLE_ACTION_NAME.PREQUEUE_LEAVE]:
            ctx = self.createLeaveCtx()
        return ctx

    def getOpenListCtxByAction(self, action):
        return None
