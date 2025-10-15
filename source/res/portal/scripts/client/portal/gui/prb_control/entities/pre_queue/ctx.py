# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/pre_queue/ctx.py
from portal_common.portal_constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'))
class PortalBattleQueueCtx(QueueCtx):

    def __init__(self, vehInvID, battleLevel, waitingID=''):
        super(PortalBattleQueueCtx, self).__init__(entityType=QUEUE_TYPE.PORTAL, waitingID=waitingID)
        self.__vehInvID = vehInvID
        self.__battleLevel = battleLevel

    def getVehicleInventoryID(self):
        return self.__vehInvID

    @property
    def battleLevel(self):
        return self.__battleLevel
