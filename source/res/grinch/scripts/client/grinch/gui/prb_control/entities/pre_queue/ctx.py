# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/pre_queue/ctx.py
from grinch_common.grinch_constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'))
class GrinchQueueCtx(QueueCtx):

    def __init__(self, vehInvID, waitingID=''):
        super(GrinchQueueCtx, self).__init__(entityType=QUEUE_TYPE.GRINCH, waitingID=waitingID)
        self.__vehInvID = vehInvID

    def getVehicleInventoryID(self):
        return self.__vehInvID
