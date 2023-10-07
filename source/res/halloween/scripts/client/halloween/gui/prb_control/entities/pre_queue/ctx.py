# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/pre_queue/ctx.py
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector
from halloween_common.halloween_constants import QUEUE_TYPE

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'))
class HalloweenBattleQueueCtx(QueueCtx):

    def __init__(self, vehInvID, waitingID='', entityType=QUEUE_TYPE.HALLOWEEN_BATTLES):
        super(HalloweenBattleQueueCtx, self).__init__(entityType=entityType, waitingID=waitingID)
        self.__vehInvID = vehInvID

    def getVehicleInventoryID(self):
        return self.__vehInvID
