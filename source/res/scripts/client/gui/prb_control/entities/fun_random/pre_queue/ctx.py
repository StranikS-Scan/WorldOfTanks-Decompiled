# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'), ('getWaitingID', 'waitingID'))
class FunRandomQueueCtx(QueueCtx):

    def __init__(self, vInventoryID, waitingID=''):
        super(FunRandomQueueCtx, self).__init__(entityType=QUEUE_TYPE.FUN_RANDOM, waitingID=waitingID)
        self.__vInventoryID = vInventoryID

    def getVehicleInventoryID(self):
        return self.__vInventoryID
