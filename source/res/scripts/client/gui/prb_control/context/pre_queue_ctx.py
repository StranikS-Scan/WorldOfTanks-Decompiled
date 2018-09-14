# Embedded file name: scripts/client/gui/prb_control/context/pre_queue_ctx.py
from constants import QUEUE_TYPE
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.utils.decorators import ReprInjector
__all__ = ('QueueCtx', 'DequeueCtx', 'RandomQueueCtx', 'EventBattlesQueueCtx', 'JoinModeCtx', 'LeavePreQueueCtx')

class _PreQueueRequestCtx(PrbCtrlRequestCtx):

    def __init__(self, **kwargs):
        super(_PreQueueRequestCtx, self).__init__(ctrlType=CTRL_ENTITY_TYPE.PREQUEUE, **kwargs)


class QueueCtx(_PreQueueRequestCtx):

    def getRequestType(self):
        return REQUEST_TYPE.QUEUE


class DequeueCtx(_PreQueueRequestCtx):

    def getRequestType(self):
        return REQUEST_TYPE.DEQUEUE


@ReprInjector.simple(('getVehicleInventoryID', 'vInvID'), ('getWaitingID', 'waitingID'))

class SandboxQueueCtx(QueueCtx):

    def __init__(self, vInventoryID, waitingID = ''):
        super(SandboxQueueCtx, self).__init__(entityType=QUEUE_TYPE.SANDBOX, waitingID=waitingID)
        self.__vInventoryID = vInventoryID

    def getVehicleInventoryID(self):
        return self.__vInventoryID


@ReprInjector.simple(('getVehicleInventoryID', 'vInvID'), ('getGamePlayMask', 'gamePlayMask'), ('getWaitingID', 'waitingID'))

class RandomQueueCtx(QueueCtx):

    def __init__(self, vInventoryID, arenaTypeID = 0, gamePlayMask = 0, waitingID = ''):
        super(RandomQueueCtx, self).__init__(entityType=QUEUE_TYPE.RANDOMS, waitingID=waitingID)
        self.__vInventoryID = vInventoryID
        self.__arenaTypeID = arenaTypeID
        self.__gamePlayMask = gamePlayMask

    def getVehicleInventoryID(self):
        return self.__vInventoryID

    def getDemoArenaTypeID(self):
        return self.__arenaTypeID

    def getGamePlayMask(self):
        return self.__gamePlayMask


@ReprInjector.simple(('getVehicleInventoryIDs', 'vInvIDs'), ('getBattleType', 'battleType'), ('getGameplaysMask', 'gameplayMask'), ('getWaitingID', 'waitingID'))

class EventBattlesQueueCtx(QueueCtx):

    def __init__(self, vehInvIDs, battleType, canAddToSquad = False, waitingID = ''):
        super(EventBattlesQueueCtx, self).__init__(entityType=QUEUE_TYPE.EVENT_BATTLES, waitingID=waitingID)
        self.__vehInvIDs = vehInvIDs
        self.__battleType = battleType
        self.__canAddToSquad = canAddToSquad

    def getVehicleInventoryIDs(self):
        return list(self.__vehInvIDs)

    def getBattleType(self):
        return self.__battleType

    def canAddToSquad(self):
        return self.__canAddToSquad


@ReprInjector.withParent()

class JoinModeCtx(_PreQueueRequestCtx):

    def __init__(self, queueType, flags = FUNCTIONAL_FLAG.UNDEFINED, waitingID = ''):
        super(JoinModeCtx, self).__init__(entityType=queueType, flags=flags, waitingID=waitingID)

    def getID(self):
        return 0


@ReprInjector.withParent(('getWaitingID', 'waitingID'))

class LeavePreQueueCtx(_PreQueueRequestCtx):

    def getRequestType(self):
        return REQUEST_TYPE.LEAVE
