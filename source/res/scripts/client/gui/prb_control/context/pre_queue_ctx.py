# Embedded file name: scripts/client/gui/prb_control/context/pre_queue_ctx.py
from CurrentVehicle import g_currentVehicle
from account_helpers import gameplay_ctx
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector

class _PreQueueRequestCtx(PrbCtrlRequestCtx):

    def getCtrlType(self):
        return CTRL_ENTITY_TYPE.PREQUEUE


@ReprInjector.simple(('getVehicleInventoryID', 'vInvID'), ('getGamePlayMask', 'gamePlayMask'), ('getWaitingID', 'waitingID'))

class JoinRandomQueueCtx(_PreQueueRequestCtx):

    def __init__(self, demoArenaTypeID = 0, waitingID = ''):
        super(JoinRandomQueueCtx, self).__init__(waitingID=waitingID)
        self.__demoArenaTypeID = demoArenaTypeID

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getGamePlayMask(self):
        return gameplay_ctx.getMask()

    def getDemoArenaTypeID(self):
        return self.__demoArenaTypeID

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


@ReprInjector.simple(('getVehicleInventoryID', 'vInvID'), ('getWaitingID', 'waitingID'))

class JoinEventBattlesQueueCtx(_PreQueueRequestCtx):

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


@ReprInjector.simple(('getVehicleInventoryID', 'vInvID'), ('getHistBattleID', 'histBattleID'), ('getIsCreditsAmmo', 'isCreditsAmmo'), ('getWaitingID', 'waitingID'))

class JoinHistoricalQueueCtx(_PreQueueRequestCtx):

    def __init__(self, histBattleID = 0, isCreditsAmmo = True, waitingID = ''):
        super(JoinHistoricalQueueCtx, self).__init__(waitingID=waitingID)
        self.__histBattleID = histBattleID
        self.__isCreditsAmmo = isCreditsAmmo

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getHistBattleID(self):
        return self.__histBattleID

    def getIsCreditsAmmo(self):
        return self.__isCreditsAmmo

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


@ReprInjector.withParent(('__queueType', 'queueType'))

class JoinModeCtx(_PreQueueRequestCtx):

    def __init__(self, queueType, waitingID = ''):
        super(JoinModeCtx, self).__init__(waitingID=waitingID)
        self.__queueType = queueType

    def getQueueType(self):
        return self.__queueType

    def getID(self):
        return 0


@ReprInjector.simple(('getWaitingID', 'waitingID'))

class LeavePreQueueCtx(_PreQueueRequestCtx):

    def getRequestType(self):
        return REQUEST_TYPE.LEAVE


__all__ = ('JoinRandomQueueCtx', 'JoinEventBattlesQueueCtx', 'JoinHistoricalQueueCtx', 'JoinModeCtx', 'LeavePreQueueCtx')
