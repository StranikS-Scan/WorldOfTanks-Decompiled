# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/pre_queue/ctx.py
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx, LeavePrbAction
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.utils.decorators import ReprInjector

class _PreQueueRequestCtx(PrbCtrlRequestCtx):
    """
    Base pre queue request context.
    """

    def __init__(self, **kwargs):
        super(_PreQueueRequestCtx, self).__init__(ctrlType=CTRL_ENTITY_TYPE.PREQUEUE, **kwargs)


class QueueCtx(_PreQueueRequestCtx):
    """
    Enter queue request context.
    """

    def getRequestType(self):
        return REQUEST_TYPE.QUEUE


class DequeueCtx(_PreQueueRequestCtx):
    """
    Leave queue request context.
    """

    def getRequestType(self):
        return REQUEST_TYPE.DEQUEUE


class JoinPreQueueModeCtx(_PreQueueRequestCtx):
    """
    Join pre queue request context.
    """

    def __init__(self, queueType, flags=FUNCTIONAL_FLAG.UNDEFINED, waitingID=''):
        super(JoinPreQueueModeCtx, self).__init__(entityType=queueType, flags=flags, waitingID=waitingID)

    def getID(self):
        """
        Stub to look like other join mode ctx.
        """
        pass


@ReprInjector.withParent(('getWaitingID', 'waitingID'))
class LeavePreQueueCtx(_PreQueueRequestCtx):
    """
    Leave pre queue request context.
    """

    def getRequestType(self):
        return REQUEST_TYPE.LEAVE
