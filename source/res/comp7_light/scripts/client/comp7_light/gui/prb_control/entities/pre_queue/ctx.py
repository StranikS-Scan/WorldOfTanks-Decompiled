# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/pre_queue/ctx.py
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'), ('getWaitingID', 'waitingID'))
class Comp7LightQueueCtx(QueueCtx):

    def __init__(self, entityType, vInventoryID, waitingID=''):
        super(Comp7LightQueueCtx, self).__init__(entityType=entityType, waitingID=waitingID)
        self.__vInventoryID = vInventoryID

    def getVehicleInventoryID(self):
        return self.__vInventoryID
