# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'))
class EventBattleQueueCtx(QueueCtx):

    def __init__(self, vehInvID, waitingID='', entityType=QUEUE_TYPE.EVENT_BATTLES):
        super(EventBattleQueueCtx, self).__init__(entityType=entityType, waitingID=waitingID)
        self.__vehInvID = vehInvID

    def getVehicleInventoryID(self):
        return self.__vehInvID
