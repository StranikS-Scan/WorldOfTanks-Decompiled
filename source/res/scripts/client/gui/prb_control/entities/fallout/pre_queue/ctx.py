# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/pre_queue/ctx.py
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryIDs', 'vInvIDs'), ('getGameplaysMask', 'gameplayMask'), ('getWaitingID', 'waitingID'))
class FalloutQueueCtx(QueueCtx):

    def __init__(self, queueType, vehInvIDs, canAddToSquad=False, waitingID=''):
        super(FalloutQueueCtx, self).__init__(entityType=queueType, waitingID=waitingID)
        self.__vehInvIDs = vehInvIDs
        self.__canAddToSquad = canAddToSquad

    def getVehicleInventoryIDs(self):
        return list(self.__vehInvIDs)

    def canAddToSquad(self):
        return self.__canAddToSquad
