# Embedded file name: scripts/client/gui/prb_control/context/unit_ctx.py
from external_strings_utils import truncate_utf8
from gui.prb_control import getUnitIdx, settings as prb_settings, getUnitMgrID
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.prb_control.settings import UNIT_MODE_FLAGS
from gui.shared.utils.decorators import ReprInjector
_CTRL_ENTITY_TYPE = prb_settings.CTRL_ENTITY_TYPE
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_FUNCTIONAL_EXIT = prb_settings.FUNCTIONAL_EXIT

class _UnitRequestCtx(PrbCtrlRequestCtx):

    def getCtrlType(self):
        return _CTRL_ENTITY_TYPE.UNIT

    def getUnitIdx(self):
        return getUnitIdx()


@ReprInjector.simple(('getRosterID', 'rosterID'), ('getWaitingID', 'waitingID'))

class CreateUnitCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', rosterID = 0):
        super(CreateUnitCtx, self).__init__(waitingID=waitingID, funcExit=_FUNCTIONAL_EXIT.UNIT)
        self.__rosterID = rosterID

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE

    def getRosterID(self):
        return self.__rosterID


@ReprInjector.simple(('__prbType', 'prbType'), ('getID', 'unitMgrID'), ('getWaitingID', 'waitingID'))

class JoinModeCtx(_UnitRequestCtx):

    def __init__(self, prbType, modeFlags = UNIT_MODE_FLAGS.UNDEFINED, waitingID = '', funcExit = prb_settings.FUNCTIONAL_EXIT.SWITCH):
        super(JoinModeCtx, self).__init__(waitingID=waitingID, funcExit=funcExit)
        self.__prbType = prbType
        self.__modeFlags = modeFlags

    def getID(self):
        return getUnitMgrID()

    def getPrbType(self):
        return self.__prbType

    def getModeFlags(self):
        return self.__modeFlags


@ReprInjector.simple(('__unitMgrID', 'unitMgrID'), ('__slotIdx', 'slotIdx'), ('getWaitingID', 'waitingID'))

class JoinUnitCtx(_UnitRequestCtx):

    def __init__(self, unitMgrID, slotIdx = None, waitingID = ''):
        super(JoinUnitCtx, self).__init__(waitingID=waitingID, funcExit=_FUNCTIONAL_EXIT.UNIT)
        self.__unitMgrID = unitMgrID
        self.__slotIdx = slotIdx

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN

    def getID(self):
        return self.__unitMgrID

    def getSlotIdx(self):
        return self.__slotIdx


@ReprInjector.simple(('getID', 'unitIdx'), ('getFuncExit', 'exit'), ('getWaitingID', 'waitingID'))

class LeaveUnitCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', funcExit = _FUNCTIONAL_EXIT.NO_FUNC):
        super(LeaveUnitCtx, self).__init__(waitingID=waitingID, funcExit=funcExit)

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE

    def getID(self):
        return getUnitIdx()


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isLocked', 'isLocked'), ('getWaitingID', 'waitingID'))

class LockUnitCtx(_UnitRequestCtx):

    def __init__(self, isLocked = True, waitingID = ''):
        super(LockUnitCtx, self).__init__(waitingID=waitingID)
        self.__isLocked = isLocked

    def getRequestType(self):
        return _REQUEST_TYPE.LOCK

    def isLocked(self):
        return self.__isLocked


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__slotIdx', 'slotIdx'), ('__isClosed', 'isClosed'), ('getWaitingID', 'waitingID'))

class CloseSlotCtx(_UnitRequestCtx):

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

    def __init__(self, vTypeCD = 0, vehInvID = 0, waitingID = ''):
        super(SetVehicleUnitCtx, self).__init__(waitingID=waitingID)
        self.__vehTypeCD = vTypeCD
        self.__vehInvID = vehInvID

    def getRequestType(self):
        return _REQUEST_TYPE.SET_VEHICLE

    def getVehTypeCD(self):
        return self.__vehTypeCD

    def getVehInvID(self):
        return self.__vehInvID


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isOpened', 'isOpened'), ('getWaitingID', 'waitingID'))

class ChangeOpenedUnitCtx(_UnitRequestCtx):

    def __init__(self, isOpened, waitingID = ''):
        super(ChangeOpenedUnitCtx, self).__init__(waitingID=waitingID)
        self.__isOpened = isOpened

    def getRequestType(self):
        return prb_settings.REQUEST_TYPE.CHANGE_OPENED

    def isOpened(self):
        return self.__isOpened


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__comment', 'comment'), ('getWaitingID', 'waitingID'))

class ChangeCommentUnitCtx(_UnitRequestCtx):

    def __init__(self, comment, waitingID = ''):
        super(ChangeCommentUnitCtx, self).__init__(waitingID=waitingID)
        self.__comment = truncate_utf8(comment, prb_settings.UNIT_COMMENT_MAX_LENGTH)

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, unit):
        return self.__comment != unit._strComment


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__isReady', 'isReady'), ('getWaitingID', 'waitingID'))

class SetReadyUnitCtx(_UnitRequestCtx):

    def __init__(self, isReady = True, waitingID = ''):
        super(SetReadyUnitCtx, self).__init__(waitingID=waitingID)
        self.__isReady = isReady

    def isReady(self):
        return self.__isReady

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE


@ReprInjector.simple(('getUnitIdx', 'unitIdx'), ('__pID', 'pID'), ('__slotIdx', 'slotIdx'), ('getWaitingID', 'waitingID'))

class AssignUnitCtx(_UnitRequestCtx):

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

    def getRequestType(self):
        return _REQUEST_TYPE.ACCEPT_SEARCH


@ReprInjector.simple(('getWaitingID', 'waitingID'))

class DeclineSearchUnitCtx(_UnitRequestCtx):

    def getRequestType(self):
        return _REQUEST_TYPE.DECLINE_SEARCH


@ReprInjector.simple(('getActionName', 'action'), ('getWaitingID', 'waitingID'))

class BattleQueueUnitCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', action = 1, vehTypes = None):
        super(BattleQueueUnitCtx, self).__init__(waitingID=waitingID)
        self.__action = action
        self.__vehTypes = [] if vehTypes is None else vehTypes
        return

    def getActionName(self):
        if self.__action > 0:
            return 'start'
        return 'stop'

    def getRequestType(self):
        return _REQUEST_TYPE.BATTLE_QUEUE

    def isRequestToStart(self):
        return self.__action > 0


class RosterSlotCtx(object):

    def __init__(self, vehTypeCD = None, nationNames = None, levels = None, vehClassNames = None):
        self.__vehTypeCD = vehTypeCD
        self.__nationNames = nationNames or []
        self.__vehLevels = levels or (1, 8)
        self.__vehClassNames = vehClassNames or []

    def getCriteria(self):
        criteria = {}
        if self.__vehTypeCD:
            criteria['vehTypeID'] = self.__vehTypeCD
        else:
            criteria['nationNames'] = self.__nationNames
            criteria['levels'] = self.__vehLevels
            criteria['vehClassNames'] = self.__vehClassNames
        return criteria


@ReprInjector.simple(('__items', 'rostersSlots'), ('getWaitingID', 'waitingID'))

class SetRostersSlotsCtx(_UnitRequestCtx):

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

    def __init__(self, databaseID, waitingID = ''):
        super(KickPlayerCtx, self).__init__(waitingID=waitingID)
        self.__databaseID = databaseID

    def getPlayerID(self):
        return self.__databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


@ReprInjector.simple(('__databaseID', 'databaseID'), ('getWaitingID', 'waitingID'))

class GiveLeadershipCtx(_UnitRequestCtx):

    def __init__(self, databaseID, waitingID = ''):
        super(GiveLeadershipCtx, self).__init__(waitingID=waitingID)
        self.__databaseID = databaseID

    def getPlayerID(self):
        return self.__databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.GIVE_LEADERSHIP


__all__ = ('CreateUnitCtx', 'JoinModeCtx', 'JoinUnitCtx', 'LeaveUnitCtx', 'LockUnitCtx', 'CloseSlotCtx', 'SetVehicleUnitCtx', 'ChangeOpenedUnitCtx', 'ChangeCommentUnitCtx', 'SetReadyUnitCtx', 'AssignUnitCtx', 'AutoSearchUnitCtx', 'AcceptSearchUnitCtx', 'DeclineSearchUnitCtx', 'BattleQueueUnitCtx', 'RosterSlotCtx', 'SetRostersSlotsCtx', 'KickPlayerCtx')
