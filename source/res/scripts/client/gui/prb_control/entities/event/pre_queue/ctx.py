# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryIDs', 'vInvIDs', 'difficultyLevel'))
class EventBattleQueueCtx(QueueCtx):

    def __init__(self, vehInvIDs, difficultyLevel=None, waitingID=''):
        super(EventBattleQueueCtx, self).__init__(entityType=QUEUE_TYPE.EVENT_BATTLES, waitingID=waitingID)
        self.__vehInvIDs = vehInvIDs
        self.__difficultyLevel = difficultyLevel

    def getVehicleInventoryIDs(self):
        return self.__vehInvIDs

    def getDifficultyLevel(self):
        return self.__difficultyLevel
