# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx, JoinPreQueueModeCtx
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'), ('getDesiredSubModeID', 'subModeID'))
class FunRandomQueueCtx(QueueCtx):
    __slots__ = ('__desiredSubModeID', '__vInventoryID')

    def __init__(self, vInventoryID, desiredSubModeID, waitingID=''):
        super(FunRandomQueueCtx, self).__init__(entityType=QUEUE_TYPE.FUN_RANDOM, waitingID=waitingID)
        self.__desiredSubModeID = desiredSubModeID
        self.__vInventoryID = vInventoryID

    def getDesiredSubModeID(self):
        return self.__desiredSubModeID

    def getVehicleInventoryID(self):
        return self.__vInventoryID


@ReprInjector.withParent(('getDesiredSubModeID', 'desiredSubModeID'))
class JoinFunPreQueueModeCtx(JoinPreQueueModeCtx):
    __slots__ = ('__desiredSubModeID',)

    def __init__(self, queueType, desiredSubModeID, flags=FUNCTIONAL_FLAG.UNDEFINED, waitingID=''):
        super(JoinFunPreQueueModeCtx, self).__init__(queueType=queueType, flags=flags, waitingID=waitingID)
        self.__desiredSubModeID = desiredSubModeID

    def getDesiredSubModeID(self):
        return self.__desiredSubModeID
