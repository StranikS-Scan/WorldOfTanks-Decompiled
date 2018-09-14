# Embedded file name: scripts/client/gui/prb_control/factories/PreQueueFactory.py
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.context.pre_queue_ctx import LeavePreQueueCtx
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.functional.fallout import FalloutEntry
from gui.prb_control.functional.no_prebattle import NoPreQueueFunctional
from gui.prb_control.functional.not_supported import QueueNotSupportedFunctional
from gui.prb_control.functional.random_queue import RandomQueueFunctional
from gui.prb_control.functional.historical import HistoricalQueueFunctional
from gui.prb_control.functional.historical import HistoricalEntry
from gui.prb_control.functional.event_battles import EventBattlesQueueFunctional
from gui.prb_control.items import FunctionalState
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE, FUNCTIONAL_EXIT
_SUPPORTED_QUEUES = {QUEUE_TYPE.RANDOMS: RandomQueueFunctional,
 QUEUE_TYPE.HISTORICAL: HistoricalQueueFunctional,
 QUEUE_TYPE.EVENT_BATTLES: EventBattlesQueueFunctional}
_SUPPORTED_ENTRY_BY_ACTION = {PREBATTLE_ACTION_NAME.HISTORICAL: (HistoricalEntry, None),
 PREBATTLE_ACTION_NAME.FALLOUT: (FalloutEntry, None)}

class PreQueueFactory(ControlFactory):

    def createEntry(self, ctx):
        LOG_ERROR('preQueue functional has not any entries')
        return None

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createFunctional(self, dispatcher, ctx):
        createParams = ctx.getCreateParams()
        if 'queueType' in createParams:
            queueType = createParams['queueType']
        else:
            queueType = None
        if queueType:
            queueType = createParams['queueType']
            settings = 'settings' in createParams and createParams['settings'].get(CTRL_ENTITY_TYPE.PREQUEUE)
        else:
            settings = None
        if queueType in _SUPPORTED_QUEUES:
            clazz = _SUPPORTED_QUEUES[queueType]
            if not clazz:
                raise AssertionError('Class is not found, checks settings')
                preQueueFunctional = clazz(settings)
                for listener in dispatcher._globalListeners:
                    preQueueFunctional.addListener(listener())

            else:
                LOG_ERROR('Queue with given type is not supported', queueType)
                preQueueFunctional = QueueNotSupportedFunctional(queueType)
        else:
            preQueueFunctional = NoPreQueueFunctional()
        return preQueueFunctional

    def createStateEntity(self, functional):
        return FunctionalState(CTRL_ENTITY_TYPE.PREQUEUE, functional.getQueueType(), True, functional.isInQueue())

    def createLeaveCtx(self, state = None, funcExit = FUNCTIONAL_EXIT.NO_FUNC):
        return LeavePreQueueCtx(waitingID='prebattle/leave')
