# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/pre_queue/ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getVehicleInventoryID', 'vInvID'), ('getGamePlayMask', 'gamePlayMask'), ('getWaitingID', 'waitingID'), ('isOnly10ModeEnabled', 'isOnly10ModeEnabled'))
class RandomQueueCtx(QueueCtx):

    def __init__(self, vInventoryID, arenaTypeID=0, gamePlayMask=0, waitingID='', isOnly10ModeEnabled=0):
        super(RandomQueueCtx, self).__init__(entityType=QUEUE_TYPE.RANDOMS, waitingID=waitingID)
        self.__vInventoryID = vInventoryID
        self.__arenaTypeID = arenaTypeID
        self.__gamePlayMask = gamePlayMask
        self.__isOnly10ModeEnabled = isOnly10ModeEnabled

    def getVehicleInventoryID(self):
        return self.__vInventoryID

    def getDemoArenaTypeID(self):
        return self.__arenaTypeID

    def getGamePlayMask(self):
        return self.__gamePlayMask

    def isOnly10ModeEnabled(self):
        return self.__isOnly10ModeEnabled
