# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/strongholds/contexts.py
import typing
from account_helpers import getAccountDatabaseID
from gui.clans import items
from gui.clans.settings import DEFAULT_COOLDOWN
from gui.shared.utils.decorators import ReprInjector
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.clan.contexts import ClanRequestBaseCtx
from gui.wgcg.settings import WebRequestDataType
from shared_utils import makeTupleByDict
from soft_exception import SoftException

@ReprInjector.withParent()
class StrongholdInfoCtx(ClanRequestBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_INFO

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.ClanStrongholdInfoData, incomeData)

    def getDefDataObj(self):
        return items.ClanStrongholdInfoData()


@ReprInjector.withParent()
class StrongholdStatisticsCtx(ClanRequestBaseCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_STATISTICS

    def getDataObj(self, incomeData):
        incomeData = incomeData or {}
        return makeTupleByDict(items.StrongholdStatisticsData, incomeData)

    def getDefDataObj(self):
        return items.StrongholdStatisticsData()

    def isAuthorizationRequired(self):
        return True

    def isCaching(self):
        return False


class StrongholdRequestCtx(CommonWebRequestCtx):
    __slots__ = ('__unitMgrId',)

    def __init__(self, unitMgrId=None, **kwargs):
        super(StrongholdRequestCtx, self).__init__(**kwargs)
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


class StrongholdLeaveCtx(StrongholdRequestCtx):

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        return cls(unitMgrId=unitMgrId, waitingID=prbCtx.getWaitingID())

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_LEAVE


class StrongholdSetVehicleCtx(StrongholdRequestCtx):
    __slots__ = ('__vehTypeCD',)

    def __init__(self, vehTypeCD, **kwargs):
        super(StrongholdSetVehicleCtx, self).__init__(**kwargs)
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


class StrongholdAssignCtx(StrongholdRequestCtx):
    __slots__ = ('__isRemove', '__pID', '__slotIdx')

    def __init__(self, pID, isRemove, slotIdx, **kwargs):
        super(StrongholdAssignCtx, self).__init__(**kwargs)
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

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_ASSIGN if not self.__isRemove else WebRequestDataType.STRONGHOLD_UNASSIGN

    def getPlayerID(self):
        return self.__pID

    def getSlotIdx(self):
        return self.__slotIdx


class StrongholdUnassignCtx(StrongholdRequestCtx):
    __slots__ = ('__isRemove', '__pID')

    def __init__(self, pID, isRemove, **kwargs):
        super(StrongholdUnassignCtx, self).__init__(**kwargs)
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


class StrongholdChangeOpenedCtx(StrongholdRequestCtx):
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, **kwargs):
        super(StrongholdChangeOpenedCtx, self).__init__(**kwargs)
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


class StrongholdSetReadyCtx(StrongholdRequestCtx):
    __slots__ = ('__isReady',)

    def __init__(self, isReady, **kwargs):
        super(StrongholdSetReadyCtx, self).__init__(**kwargs)
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


class StrongholdSetReserveCtx(StrongholdRequestCtx):
    __slots__ = ('__reserveID', '__isRemove')

    def __init__(self, reserveID, isRemove, **kwargs):
        super(StrongholdSetReserveCtx, self).__init__(**kwargs)
        self.__reserveID = reserveID
        self.__isRemove = isRemove

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        reserveID = prbCtx.getReserveID()
        isRemove = prbCtx.getIsRemove()
        return cls(reserveID, isRemove, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SET_RESERVE

    def getReserveID(self):
        return self.__reserveID

    def getIsRemove(self):
        return self.__isRemove


class StrongholdUnsetReserveCtx(StrongholdRequestCtx):
    __slots__ = ('__reserveID', '__isRemove')

    def __init__(self, reserveID, isRemove, **kwargs):
        super(StrongholdUnsetReserveCtx, self).__init__(**kwargs)
        self.__reserveID = reserveID
        self.__isRemove = isRemove

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        reserveID = prbCtx.getReserveID()
        isRemove = prbCtx.getIsRemove()
        return cls(reserveID, isRemove, unitMgrId=unitMgrId, waitingID=waitingID)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_UNSET_RESERVE

    def getReserveID(self):
        return self.__reserveID

    def getIsRemove(self):
        return self.__isRemove


class StrongholdBattleQueueCtx(StrongholdRequestCtx):
    __slots__ = ('__action',)

    def __init__(self, action, **kwargs):
        super(StrongholdBattleQueueCtx, self).__init__(**kwargs)
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


class StrongholdKickPlayerCtx(StrongholdRequestCtx):
    __slots__ = ('__pID',)

    def __init__(self, pID, **kwargs):
        super(StrongholdKickPlayerCtx, self).__init__(**kwargs)
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


class StrongholdGiveLeadershipCtx(StrongholdRequestCtx):
    __slots__ = ('__databaseID', '__pID')

    def __init__(self, pID, **kwargs):
        super(StrongholdGiveLeadershipCtx, self).__init__(**kwargs)
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


class StrongholdSetEquipmentCommanderCtx(StrongholdRequestCtx):
    __slots__ = ('__pID', '__role')

    def __init__(self, pID=None, role=None, **kwargs):
        super(StrongholdSetEquipmentCommanderCtx, self).__init__(**kwargs)
        self.__pID = pID
        self.__role = role

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        waitingID = prbCtx.getWaitingID()
        pID = prbCtx.getPlayerID()
        role = prbCtx.getRole()
        return cls(pID, unitMgrId=unitMgrId, waitingID=waitingID, role=role)

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SET_EQUIPMENT_COMMANDER

    def getPlayerID(self):
        return self.__pID

    def getRole(self):
        return self.__role


class StrongholdUpdateCtx(StrongholdRequestCtx):
    __slots__ = ('__rev',)

    def __init__(self, rev, **kwargs):
        super(StrongholdUpdateCtx, self).__init__(**kwargs)
        self.__rev = rev

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_UPDATE

    def getCooldown(self):
        return DEFAULT_COOLDOWN

    def getRev(self):
        return self.__rev

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class StrongholdSendInvitesCtx(StrongholdRequestCtx):
    __slots__ = ('__databaseIDs', '__comment')

    def __init__(self, databaseIDs, comment, **args):
        super(StrongholdSendInvitesCtx, self).__init__(**args)
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


class StrongholdJoinBattleCtx(StrongholdRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_JOIN_BATTLE

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class StrongholdMatchmakingInfoCtx(StrongholdRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_MATCHMAKING_INFO

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class StrongholdSetSlotVehicleTypeFilter(StrongholdRequestCtx):
    __slots__ = ('__slotIdx', '__vehicleTypes')

    def __init__(self, slotIdx, vehicleTypes, **args):
        super(StrongholdSetSlotVehicleTypeFilter, self).__init__(**args)
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


class StrongholdSetSlotVehiclesFilter(StrongholdRequestCtx):
    __slots__ = ('__slotIdx', '__vehicles')

    def __init__(self, slotIdx, vehicles, **args):
        super(StrongholdSetSlotVehiclesFilter, self).__init__(**args)
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


class StrongholdStopPlayersMatchingCtx(StrongholdRequestCtx):

    @classmethod
    def fromPrbCtx(cls, prbCtx, unitMgrId):
        return cls(unitMgrId=unitMgrId, waitingID=prbCtx.getWaitingID())

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_STOP_PLAYERS_MATCHING


class SlotVehicleFiltersUpdateCtx(StrongholdRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_SLOT_VEHICLE_FILTERS_UPDATE

    def getCooldown(self):
        return DEFAULT_COOLDOWN

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class StrongholdLeaveModeCtx(StrongholdRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_LEAVE_MODE

    @classmethod
    def fromPrbCtx(cls, prbCtx):
        raise SoftException('This method should not be reached in this context')


class StrongholdEventGetFrozenVehiclesCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_EVENT_GET_FROZEN_VEHICLES

    def isAuthorizationRequired(self):
        return True


class StrongholdGetForbiddenVehiclesCtx(CommonWebRequestCtx):

    def getRequestType(self):
        return WebRequestDataType.STRONGHOLD_GET_FORBIDDEN_VEHICLES

    def isAuthorizationRequired(self):
        return True
