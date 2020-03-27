# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/tournament/contexts.py
from account_helpers import getAccountDatabaseID
from gui.clans.settings import DEFAULT_COOLDOWN
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
from soft_exception import SoftException

class TournamentRequestCtx(CommonWebRequestCtx):
    __slots__ = ('__unitMgrId',)

    def __init__(self, unitMgrId=None, **kwargs):
        super(TournamentRequestCtx, self).__init__(**kwargs)
        self.__unitMgrId = unitMgrId

    def getUnitMgrID(self):
        return self.__unitMgrId

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise NotImplementedError

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False


class TournamentJoinBattleCtx(TournamentRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.TOURNAMENT_JOIN_BATTLE

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class TournamentLeaveModeCtx(TournamentRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.TOURNAMENT_LEAVE_MODE

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        return cls(unitMgrId=unitMgrId, waitingID=prbCtx.getWaitingID())


class TournamentUpdateCtx(TournamentRequestCtx):
    __slots__ = ('__rev',)

    def __init__(self, rev, **kwargs):
        super(TournamentUpdateCtx, self).__init__(**kwargs)
        self.__rev = rev

    def getRequestType(self):
        return WebRequestDataType.TOURNAMENT_UPDATE

    def getCooldown(self):
        return DEFAULT_COOLDOWN

    def getRev(self):
        return self.__rev

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class TournamentAssignCtx(TournamentRequestCtx):
    __slots__ = ('__isRemove', '__pID', '__slotIdx')

    def __init__(self, pID, isRemove, slotIdx, **kwargs):
        super(TournamentAssignCtx, self).__init__(**kwargs)
        self.__pID = pID
        self.__slotIdx = slotIdx
        self.__isRemove = isRemove

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        pID = prbCtx.getPlayerID()
        isRemove = prbCtx.isRemove()
        slotIdx = prbCtx.getSlotIdx()
        return cls(pID, isRemove, slotIdx, unitMgrId=unitMgrId, waitingID=waitingID)


class TournamentUnassignCtx(TournamentRequestCtx):
    __slots__ = ('__isRemove', '__pID')

    def __init__(self, pID, isRemove, **kwargs):
        super(TournamentUnassignCtx, self).__init__(**kwargs)
        self.__pID = pID
        self.__isRemove = isRemove

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        pID = prbCtx.getPlayerID()
        isRemove = prbCtx.isRemove()
        return cls(pID, isRemove, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_UNASSIGN

    def getPlayerID(self):
        return self.__pID


class TournamentChangeOpenedCtx(TournamentRequestCtx):
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, **kwargs):
        super(TournamentChangeOpenedCtx, self).__init__(**kwargs)
        self.__isOpened = isOpened

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        isOpened = prbCtx.isOpened()
        return cls(isOpened, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_CHANGE_OPENED

    def isOpened(self):
        return self.__isOpened


class TournamentSetVehicleCtx(TournamentRequestCtx):
    __slots__ = ('__vehTypeCD',)

    def __init__(self, vehTypeCD, **kwargs):
        super(TournamentSetVehicleCtx, self).__init__(**kwargs)
        self.__vehTypeCD = vehTypeCD

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        vehTypeCD = prbCtx.getVehTypeCD()
        return cls(vehTypeCD, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SET_VEHICLE

    def getVehTypeCD(self):
        return self.__vehTypeCD


class TournamentSetReadyCtx(TournamentRequestCtx):
    __slots__ = ('__isReady',)

    def __init__(self, isReady, **kwargs):
        super(TournamentSetReadyCtx, self).__init__(**kwargs)
        self.__isReady = isReady

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        isReady = prbCtx.isReady()
        return cls(isReady, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SET_PLAYER_STATE

    def isReady(self):
        return self.__isReady


class TournamentBattleQueueCtx(TournamentRequestCtx):
    __slots__ = ('__action',)

    def __init__(self, action, **kwargs):
        super(TournamentBattleQueueCtx, self).__init__(**kwargs)
        self.__action = action

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        action = prbCtx.getAction()
        return cls(action, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_BATTLE_QUEUE

    def isRequestToStart(self):
        return self.__action > 0


class TournamentKickPlayerCtx(TournamentRequestCtx):
    __slots__ = ('__pID',)

    def __init__(self, pID, **kwargs):
        super(TournamentKickPlayerCtx, self).__init__(**kwargs)
        self.__pID = pID

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        pID = prbCtx.getPlayerID()
        return cls(pID, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_KICK

    def getPlayerID(self):
        return self.__pID


class TournamentGiveLeadershipCtx(TournamentRequestCtx):
    __slots__ = ('__databaseID', '__pID')

    def __init__(self, pID, **kwargs):
        super(TournamentGiveLeadershipCtx, self).__init__(**kwargs)
        self.__pID = pID

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        pID = prbCtx.getPlayerID()
        return cls(pID, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_GIVE_LEADERSHIP if self.__pID != getAccountDatabaseID() else WebRequestDataType.STRONGHOLD_TAKE_LEADERSHIP

    def getPlayerID(self):
        return self.__pID


class TournamentSendInvitesCtx(TournamentRequestCtx):
    __slots__ = ('__databaseIDs', '__comment')

    def __init__(self, databaseIDs, comment, **args):
        super(TournamentSendInvitesCtx, self).__init__(**args)
        self.__databaseIDs = databaseIDs
        self.__comment = comment

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        databaseIDs = prbCtx.getDatabaseIDs()
        comment = prbCtx.getComment()
        return cls(databaseIDs, comment, unitMgrId=unitMgrId, waitingID=waitingID)

    def getDatabaseIDs(self):
        return self.__databaseIDs

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SEND_INVITE


class TournamentSetSlotVehicleTypeFilter(TournamentRequestCtx):
    __slots__ = ('__slotIdx', '__vehicleTypes')

    def __init__(self, slotIdx, vehicleTypes, **args):
        super(TournamentSetSlotVehicleTypeFilter, self).__init__(**args)
        self.__slotIdx = slotIdx
        self.__vehicleTypes = vehicleTypes

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SET_SLOT_VEHICLE_TYPE_FILTER

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        vehTypes = prbCtx.getVehTypes()
        slotIdx = prbCtx.getSlotIdx()
        return cls(slotIdx, vehTypes, unitMgrId=unitMgrId, waitingID=waitingID)

    def getSlotIdx(self):
        return self.__slotIdx

    def getVehicleTypes(self):
        return self.__vehicleTypes


class TournamentSetSlotVehiclesFilter(TournamentRequestCtx):
    __slots__ = ('__slotIdx', '__vehicles')

    def __init__(self, slotIdx, vehicles, **args):
        super(TournamentSetSlotVehiclesFilter, self).__init__(**args)
        self.__slotIdx = slotIdx
        self.__vehicles = vehicles

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SET_SLOT_VEHICLES_FILTER

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        vehicles = prbCtx.getVehicles()
        slotIdx = prbCtx.getSlotIdx()
        return cls(slotIdx, vehicles, unitMgrId=unitMgrId, waitingID=waitingID)

    def getSlotIdx(self):
        return self.__slotIdx

    def getVehicles(self):
        return self.__vehicles


class TournamentStopPlayersMatchingCtx(TournamentRequestCtx):

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        return cls(unitMgrId=unitMgrId, waitingID=prbCtx.getWaitingID())

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_STOP_PLAYERS_MATCHING


class SlotVehicleFiltersUpdateCtx(TournamentRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SLOT_VEHICLE_FILTERS_UPDATE

    def getCooldown(self):
        return DEFAULT_COOLDOWN

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class TournamentMatchmakingInfoCtx(TournamentRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.TOURNAMENT_MATCHMAKING_INFO

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')
