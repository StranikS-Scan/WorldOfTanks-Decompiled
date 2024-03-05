# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/prb_control/entities/pre_queue/ctx.py
from cosmic_event_common.cosmic_constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'))
class CosmicEventBattleQueueCtx(QueueCtx):

    def __init__(self, vehInvID, waitingID=''):
        super(CosmicEventBattleQueueCtx, self).__init__(entityType=QUEUE_TYPE.COSMIC_EVENT, waitingID=waitingID)
        self.__vehInvID = vehInvID

    def getVehicleInventoryID(self):
        return self.__vehInvID
