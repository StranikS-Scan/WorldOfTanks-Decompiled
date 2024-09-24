# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/winback/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'), ('getWaitingID', 'waitingID'), ('getWinbackFlags', 'winbackFlags'))
class WinbackModeQueueCtx(QueueCtx):

    def __init__(self, vInventoryID, waitingID='', winbackFlags=0):
        super(WinbackModeQueueCtx, self).__init__(entityType=QUEUE_TYPE.WINBACK, waitingID=waitingID)
        self.__vInventoryID = vInventoryID
        self.__winbackFlags = winbackFlags

    def getVehicleInventoryID(self):
        return self.__vInventoryID

    def getWinbackFlags(self):
        return self.__winbackFlags
