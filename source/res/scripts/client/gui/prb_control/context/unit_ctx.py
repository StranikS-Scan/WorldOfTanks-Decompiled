# Embedded file name: scripts/client/gui/prb_control/context/unit_ctx.py
from constants import PREBATTLE_TYPE
from account_helpers import gameplay_ctx
from external_strings_utils import truncate_utf8
from gui.prb_control import prb_getters, settings as prb_settings
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.shared.utils.decorators import ReprInjector
__all__ = ('CreateUnitCtx', 'JoinModeCtx', 'JoinUnitCtx', 'LeaveUnitCtx', 'LockUnitCtx', 'CloseSlotCtx', 'SetVehicleUnitCtx', 'ChangeOpenedUnitCtx', 'ChangeCommentUnitCtx', 'SetReadyUnitCtx', 'AssignUnitCtx', 'AutoSearchUnitCtx', 'AcceptSearchUnitCtx', 'DeclineSearchUnitCtx', 'BattleQueueUnitCtx', 'RosterSlotCtx', 'SetRostersSlotsCtx', 'KickPlayerCtx', 'ChangeRatedUnitCtx', 'SquadSettingsCtx', 'ChangeDivisionCtx', 'SetEventVehiclesCtx', 'ChangeEventSquadTypeCtx')
_CTRL_ENTITY_TYPE = prb_settings.CTRL_ENTITY_TYPE
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_FUNCTIONAL_FLAG = prb_settings.FUNCTIONAL_FLAG
_UNDEFINED = _FUNCTIONAL_FLAG.UNDEFINED
_SWITCH = _FUNCTIONAL_FLAG.SWITCH

class _UnitRequestCtx(PrbCtrlRequestCtx):
    __slots__ = ()

    def __init__(self, **kwargs):
        super(_UnitRequestCtx, self).__init__(ctrlType=_CTRL_ENTITY_TYPE.UNIT, **kwargs)

    def getUnitIdx(self):
        return prb_getters.getUnitIdx()

    def getCooldown(self):
        return 5.0


@ReprInjector.simple(('__prbType', 'prbType'), ('getRosterID', 'rosterID'), ('getWaitingID', 'waitingID'))

class CreateUnitCtx(_UnitRequestCtx):
    __slots__ = ('__rosterID',)

    def __init__(self, prbType, flags = _UNDEFINED, waitingID = '', rosterID = 0):
        super(CreateUnitCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)
        self.__rosterID = rosterID

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE

    def getRosterID(self):
        return self.__rosterID


@ReprInjector.simple(('__prbType', 'prbType'), ('getID', 'unitMgrID'), ('getWaitingID', 'waitingID'))

class JoinModeCtx(_UnitRequestCtx):
    __slots__ = ()

    def __init__(self, prbType, waitingID = '', flags = _UNDEFINED):
        super(JoinModeCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)

    def getID(self):
        return prb_getters.getUnitMgrID()


@ReprInjector.withParent(('__unitMgrID', 'unitMgrID'), ('__slotIdx', 'slotIdx'))

class JoinUnitCtx(_UnitRequestCtx):
    __slots__ = ('__unitMgrID', '__slotIdx')

    def __init__(self, unitMgrID, prbType, slotIdx = None, waitingID = ''):
        super(JoinUnitCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=_SWITCH)
        self.__unitMgrID = unitMgrID
        self.__slotIdx = slotIdx

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN

    def getID(self):
        return self.__unitMgrID

    def getSlotIdx(self):
        return self.__slotIdx


@ReprInjector.simple(('getID', 'unitIdx'), ('getFlagsToStrings', 'flags'), ('getWaitingID', 'waitingID'))

class LeaveUnitCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', flags = _UNDEFINED, entityType = 0):
        super(LeaveUnitCtx, self).__init__(waitingID=waitingID, flags=flags, entityType=entityType)

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE

    def getID(self):
        return prb_getters.getUnitIdx()


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isLocked', 'isLocked'), ('getWaitingID', 'waitingID'))

class LockUnitCtx(_UnitRequestCtx):
    __slots__ = ('__isLocked',)

    def __init__(self, isLocked = True, waitingID = ''):
        super(LockUnitCtx, self).__init__(waitingID=waitingID)
        self.__isLocked = isLocked

    def getRequestType(self):
        return _REQUEST_TYPE.LOCK

    def isLocked(self):
        return self.__isLocked


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__slotIdx', 'slotIdx'), ('__isClosed', 'isClosed'), ('getWaitingID', 'waitingID'))

class CloseSlotCtx(_UnitRequestCtx):
    __slots__ = ('__slotIdx', '__isClosed')

    def __init__(self, slotIdx, isClosed = True, waitingID = ''):
        super(CloseSlotCtx, self).__init__(waitingID=waitingID)
        self.__slotIdx = slotIdx
        self.__isClosed = isClosed

    def getRequestType(self):
        return _REQUEST_TYPE.CLOSE_SLOT

    def getSlotIdx(self):
        return self.__slotIdx

    def isClosed(self):
        return self.__isClosed


@ReprInjector.simple(('__vehTypeCD', 'vTypeCD'), ('__vehInvID', 'vehInvID'), ('getWaitingID', 'waitingID'))

class SetVehicleUnitCtx(_UnitRequestCtx):
    __slots__ = ('__vehTypeCD', '__vehInvID', 'setReady')

    def __init__(self, vTypeCD = 0, vehInvID = 0, waitingID = ''):
        super(SetVehicleUnitCtx, self).__init__(waitingID=waitingID)
        self.__vehTypeCD = vTypeCD
        self.__vehInvID = vehInvID
        self.setReady = False

    def getRequestType(self):
        return _REQUEST_TYPE.SET_VEHICLE

    def getVehTypeCD(self):
        return self.__vehTypeCD

    def getVehInvID(self):
        return self.__vehInvID


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isOpened', 'isOpened'), ('getWaitingID', 'waitingID'))

class ChangeOpenedUnitCtx(_UnitRequestCtx):
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, waitingID = ''):
        super(ChangeOpenedUnitCtx, self).__init__(waitingID=waitingID)
        self.__isOpened = isOpened

    def getRequestType(self):
        return prb_settings.REQUEST_TYPE.CHANGE_OPENED

    def isOpened(self):
        return self.__isOpened


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__comment', 'comment'), ('getWaitingID', 'waitingID'))

class ChangeCommentUnitCtx(_UnitRequestCtx):
    __slots__ = ('__comment',)

    def __init__(self, comment, waitingID = ''):
        super(ChangeCommentUnitCtx, self).__init__(waitingID=waitingID)
        self.__comment = truncate_utf8(comment, prb_settings.UNIT_COMMENT_MAX_LENGTH)

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, unit):
        return self.__comment != unit.getComment()


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isReady', 'isReady'), ('getWaitingID', 'waitingID'))

class SetReadyUnitCtx(_UnitRequestCtx):
    __slots__ = ('__isReady', 'resetVehicle')

    def __init__(self, isReady = True, waitingID = ''):
        super(SetReadyUnitCtx, self).__init__(waitingID=waitingID)
        self.__isReady = isReady
        self.resetVehicle = False

    def isReady(self):
        return self.__isReady

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__pID', 'pID'), ('__slotIdx', 'slotIdx'), ('getWaitingID', 'waitingID'))

class AssignUnitCtx(_UnitRequestCtx):
    __slots__ = ('__pID', '__slotIdx')

    def __init__(self, pID, slotIdx, waitingID = ''):
        super(AssignUnitCtx, self).__init__(waitingID=waitingID)
        self.__pID = pID
        self.__slotIdx = slotIdx

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN

    def getPlayerID(self):
        return self.__pID

    def getSlotIdx(self):
        return self.__slotIdx


@ReprInjector.simple(('getActionName', 'action'), ('__vehTypes', 'vehTypes'), ('getWaitingID', 'waitingID'))

class AutoSearchUnitCtx(_UnitRequestCtx):
    __slots__ = ('__action', '__vehTypes')

    def __init__(self, waitingID = '', action = 1, vehTypes = None):
        super(AutoSearchUnitCtx, self).__init__(waitingID=waitingID)
        self.__action = action
        self.__vehTypes = [] if vehTypes is None else vehTypes
        return

    def getActionName(self):
        if self.__action > 0:
            return 'start'
        return 'stop'

    def getRequestType(self):
        return _REQUEST_TYPE.AUTO_SEARCH

    def isRequestToStart(self):
        return self.__action > 0

    def getVehTypes(self):
        return self.__vehTypes


@ReprInjector.simple(('getWaitingID', 'waitingID'))

class AcceptSearchUnitCtx(_UnitRequestCtx):
    __slots__ = ()

    def getRequestType(self):
        return _REQUEST_TYPE.ACCEPT_SEARCH


@ReprInjector.simple(('getWaitingID', 'waitingID'))

class DeclineSearchUnitCtx(_UnitRequestCtx):
    __slots__ = ()

    def getRequestType(self):
        return _REQUEST_TYPE.DECLINE_SEARCH


@ReprInjector.simple(('getActionName', 'action'), ('getWaitingID', 'waitingID'), ('getGamePlayMask', 'mask'))

class BattleQueueUnitCtx(_UnitRequestCtx):
    __slots__ = ('__action', '__vehTypes', 'selectVehInvID')

    def __init__(self, waitingID = '', action = 1, vehTypes = None):
        super(BattleQueueUnitCtx, self).__init__(waitingID=waitingID)
        self.__action = action
        self.__vehTypes = [] if vehTypes is None else vehTypes
        self.selectVehInvID = 0
        return

    def getActionName(self):
        if self.__action > 0:
            return 'start'
        return 'stop'

    def getRequestType(self):
        return _REQUEST_TYPE.BATTLE_QUEUE

    def isRequestToStart(self):
        return self.__action > 0

    def getGamePlayMask(self):
        return gameplay_ctx.getMask()


class RosterSlotCtx(object):

    def __init__(self, vehTypeCD = None, nationNames = None, levels = None, vehClassNames = None):
        self.__vehTypeCD = vehTypeCD
        self.__nationNames = nationNames
        self.__vehLevels = levels
        self.__vehClassNames = vehClassNames

    def getCriteria(self):
        criteria = {}
        if self.__vehTypeCD:
            criteria['vehTypeID'] = self.__vehTypeCD
        else:
            if self.__nationNames:
                criteria['nationNames'] = self.__nationNames
            if self.__vehLevels:
                criteria['levels'] = self.__vehLevels
            if self.__vehClassNames:
                criteria['vehClassNames'] = self.__vehClassNames
        return criteria


@ReprInjector.simple(('__items', 'rostersSlots'), ('getWaitingID', 'waitingID'))

class SetRostersSlotsCtx(_UnitRequestCtx):
    __slots__ = ('__items',)

    def __init__(self, waitingID = ''):
        super(SetRostersSlotsCtx, self).__init__(waitingID=waitingID)
        self.__items = {}

    def getRequestType(self):
        return _REQUEST_TYPE.SET_ROSTERS_SLOTS

    def addRosterSlot(self, rosterSlotIdx, ctx):
        self.__items[rosterSlotIdx] = ctx.getCriteria()

    def getRosterSlots(self):
        return self.__items.copy()


@ReprInjector.simple(('__databaseID', 'databaseID'), ('getWaitingID', 'waitingID'))

class KickPlayerCtx(_UnitRequestCtx):
    __slots__ = ('__databaseID',)

    def __init__(self, databaseID, waitingID = ''):
        super(KickPlayerCtx, self).__init__(waitingID=waitingID)
        self.__databaseID = databaseID

    def getPlayerID(self):
        return self.__databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


@ReprInjector.simple(('__databaseID', 'databaseID'), ('getWaitingID', 'waitingID'))

class GiveLeadershipCtx(_UnitRequestCtx):
    __slots__ = ('__databaseID',)

    def __init__(self, databaseID, waitingID = ''):
        super(GiveLeadershipCtx, self).__init__(waitingID=waitingID)
        self.__databaseID = databaseID

    def getPlayerID(self):
        return self.__databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.GIVE_LEADERSHIP


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isRated', 'isRated'), ('getWaitingID', 'waitingID'))

class ChangeRatedUnitCtx(_UnitRequestCtx):
    __slots__ = ('__isRated',)

    def __init__(self, isRated, waitingID = ''):
        super(ChangeRatedUnitCtx, self).__init__(waitingID=waitingID)
        self.__isRated = isRated

    def getRequestType(self):
        return prb_settings.REQUEST_TYPE.CHANGE_RATED

    def isRated(self):
        return self.__isRated


@ReprInjector.simple(('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'))

class SquadSettingsCtx(_UnitRequestCtx):
    __slots__ = ('__accountsToInvite',)

    def __init__(self, waitingID = '', flags = prb_settings.FUNCTIONAL_FLAG.UNDEFINED, accountsToInvite = None, isForced = False):
        super(SquadSettingsCtx, self).__init__(entityType=PREBATTLE_TYPE.SQUAD, waitingID=waitingID, flags=flags, isForced=isForced)
        self.__accountsToInvite = accountsToInvite or []

    def getID(self):
        return 0

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE

    def getAccountsToInvite(self):
        return self.__accountsToInvite


@ReprInjector.simple(('__division', 'division'), ('getWaitingID', 'waitingID'))

class ChangeDivisionCtx(_UnitRequestCtx):
    __slots__ = ('__divisionID',)

    def __init__(self, divisionID, waitingID = ''):
        super(ChangeDivisionCtx, self).__init__(waitingID=waitingID)
        self.__divisionID = int(divisionID)

    def getDivisionID(self):
        return self.__divisionID

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_DIVISION


@ReprInjector.simple(('__vehsList', 'vehsList'), ('getWaitingID', 'waitingID'))

class SetEventVehiclesCtx(_UnitRequestCtx):
    __slots__ = ('__vehsList',)

    def __init__(self, vehsList, waitingID = ''):
        super(SetEventVehiclesCtx, self).__init__(waitingID=waitingID)
        self.__vehsList = vehsList

    def getVehsList(self):
        return self.__vehsList

    def getRequestType(self):
        return _REQUEST_TYPE.SET_ES_VEHICLE_LIST

    def getCooldown(self):
        return 2.0


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isReady', 'isReady'), ('getWaitingID', 'waitingID'))

class SetReadyEventSquadCtx(_UnitRequestCtx):
    __slots__ = ('__isReady',)

    def __init__(self, isReady = True, waitingID = ''):
        super(SetReadyEventSquadCtx, self).__init__(waitingID=waitingID)
        self.__isReady = isReady

    def isReady(self):
        return self.__isReady

    def getRequestType(self):
        return _REQUEST_TYPE.SET_ES_PLAYER_STATE


@ReprInjector.simple(('__eventType', 'eventType'), ('getWaitingID', 'waitingID'))

class ChangeEventSquadTypeCtx(_UnitRequestCtx):
    __slots__ = ('__eventType',)

    def __init__(self, eventType = True, waitingID = ''):
        super(ChangeEventSquadTypeCtx, self).__init__(waitingID=waitingID)
        self.__eventType = eventType

    def getBattleType(self):
        return self.__eventType

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_ES_TYPE
