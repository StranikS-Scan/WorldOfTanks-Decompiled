# Embedded file name: scripts/client/gui/prb_control/context/pre_queue_ctx.py
from CurrentVehicle import g_currentVehicle
from account_helpers import gameplay_ctx
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE

class _PreQueueRequestCtx(PrbCtrlRequestCtx):

    def getEntityType(self):
        return CTRL_ENTITY_TYPE.PREQUEUE


class JoinRandomQueueCtx(_PreQueueRequestCtx):

    def __init__(self, demoArenaTypeID = 0, waitingID = ''):
        super(JoinRandomQueueCtx, self).__init__(waitingID)
        self.__demoArenaTypeID = demoArenaTypeID

    def __repr__(self):
        return 'JoinRandomQueueCtx(vInvID = {0:n}, gamePlayMask = {1:n}, waitingID = {2:>s})'.format(self.getVehicleInventoryID(), self.getGamePlayMask(), self.getWaitingID())

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getGamePlayMask(self):
        return gameplay_ctx.getMask()

    def getDemoArenaTypeID(self):
        return self.__demoArenaTypeID

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


class JoinEventBattlesQueueCtx(_PreQueueRequestCtx):

    def __repr__(self):
        return 'JoinEventBattlesQueueCtx(vInvID = {0:n}, waitingID = {1:>s})'.format(self.getVehicleInventoryID(), self.getWaitingID())

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


class JoinHistoricalQueueCtx(_PreQueueRequestCtx):

    def __init__(self, histBattleID = 0, isCreditsAmmo = True, waitingID = ''):
        super(JoinHistoricalQueueCtx, self).__init__(waitingID)
        self.__histBattleID = histBattleID
        self.__isCreditsAmmo = isCreditsAmmo

    def __repr__(self):
        return 'JoinHistoricalQueueCtx(vInvID = {0:n}, histBattleID = {1:n}, isCreditsAmmo = {2:n}, waitingID = {3:>s})'.format(self.getVehicleInventoryID(), self.getHistBattleID(), self.getIsCreditsAmmo(), self.getWaitingID())

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getHistBattleID(self):
        return self.__histBattleID

    def getIsCreditsAmmo(self):
        return self.__isCreditsAmmo

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


class LeavePreQueueCtx(_PreQueueRequestCtx):

    def __repr__(self):
        return 'LeavePreQueueCtx(waitingID = {0:>s})'.format(self.getWaitingID())

    def getRequestType(self):
        return REQUEST_TYPE.LEAVE


__all__ = ('JoinRandomQueueCtx', 'JoinEventBattlesQueueCtx', 'JoinHistoricalQueueCtx', 'LeavePreQueueCtx')
