# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event_two/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'), ('getWaitingID', 'waitingID'))
class EventBattlesTwoQueueCtx(QueueCtx):
    """
    BossMode enqueue context
    """

    def __init__(self, vInventoryID, waitingID=''):
        super(EventBattlesTwoQueueCtx, self).__init__(entityType=QUEUE_TYPE.EVENT_BATTLES_2, waitingID=waitingID)
        self.__vInventoryID = vInventoryID

    def getVehicleInventoryID(self):
        """
        Gets the selected vehicle inventory ID
        """
        return self.__vInventoryID
