# Embedded file name: scripts/client/gui/prb_control/context/unit_ctx.py
from external_strings_utils import truncate_utf8
from gui.prb_control import getUnitIdx, settings as prb_settings, getUnitMgrID
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.prb_control.settings import UNIT_MODE_FLAGS
_CTRL_ENTITY_TYPE = prb_settings.CTRL_ENTITY_TYPE
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_FUNCTIONAL_EXIT = prb_settings.FUNCTIONAL_EXIT
_GUI_EXIT = prb_settings.GUI_EXIT

class _UnitRequestCtx(PrbCtrlRequestCtx):

    def __init__(self, waitingID = ''):
        super(_UnitRequestCtx, self).__init__(waitingID)
        self.__isForced = False

    def getEntityType(self):
        return _CTRL_ENTITY_TYPE.UNIT

    def getUnitIdx(self):
        return getUnitIdx()

    def isForced(self):
        return self.__isForced

    def setForced(self, flag):
        self.__isForced = flag


class _UnitEntryCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', funcExit = _FUNCTIONAL_EXIT.NO_FUNC, guiExit = _GUI_EXIT.HANGAR):
        super(_UnitEntryCtx, self).__init__(waitingID)
        self.__funcExit = funcExit
        self.__guiExit = guiExit

    def getFuncExit(self):
        return self.__funcExit

    def getGuiExit(self):
        return self.__guiExit


class CreateUnitCtx(_UnitEntryCtx):

    def __init__(self, waitingID = '', rosterID = 0):
        super(CreateUnitCtx, self).__init__(waitingID=waitingID, funcExit=_FUNCTIONAL_EXIT.UNIT)
        self.__rosterID = rosterID

    def __repr__(self):
        return 'CreateUnitCtx(rosterID = {0:n}, waitingID = {1:>s})'.format(self.getRosterID(), self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE

    def getRosterID(self):
        return self.__rosterID


class JoinModeCtx(_UnitEntryCtx):

    def __init__(self, prbType, modeFlags = UNIT_MODE_FLAGS.SHOW_LIST, guiExit = _GUI_EXIT.HANGAR, waitingID = ''):
        super(JoinModeCtx, self).__init__(guiExit=guiExit, waitingID=waitingID)
        self.__prbType = prbType
        self.__modeFlags = modeFlags

    def __repr__(self):
        return 'JoinModeCtx(prbType = {0:n}, unitMgrID = {1!r:s}, waitingID = {2:>s})'.format(self.__prbType, self.getID(), self.getWaitingID())

    def getID(self):
        return getUnitMgrID()

    def getPrbType(self):
        return self.__prbType

    def getModeFlags(self):
        return self.__modeFlags


class JoinUnitCtx(_UnitEntryCtx):

    def __init__(self, unitMgrID, slotIdx = None, waitingID = ''):
        super(JoinUnitCtx, self).__init__(waitingID=waitingID, funcExit=_FUNCTIONAL_EXIT.UNIT)
        self.__unitMgrID = unitMgrID
        self.__slotIdx = slotIdx

    def __repr__(self):
        return 'JoinUnitCtx(unitMgrID = {0:n}, slotIdx = {1!r:s}, waitingID = {2:>s})'.format(self.__unitMgrID, self.__slotIdx, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN

    def getID(self):
        return self.__unitMgrID

    def getSlotIdx(self):
        return self.__slotIdx


class LeaveUnitCtx(_UnitEntryCtx):

    def __init__(self, waitingID = '', funcExit = _FUNCTIONAL_EXIT.NO_FUNC):
        super(LeaveUnitCtx, self).__init__(waitingID=waitingID, funcExit=funcExit)

    def __repr__(self):
        return 'LeaveUnitCtx(unitIdx = {0:n}, exit = {1!r:s}/{2!r:s}, waitingID = {3:>s})'.format(self.getID(), self.getFuncExit(), self.getGuiExit(), self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE

    def getID(self):
        return getUnitIdx()


class LockUnitCtx(_UnitRequestCtx):

    def __init__(self, isLocked = True, waitingID = ''):
        super(LockUnitCtx, self).__init__(waitingID)
        self.__isLocked = isLocked

    def __repr__(self):
        return 'LockUnitCtx(unitIdx = {0:n}, isLocked = {1!r:s}, waitingID = {2:>s})'.format(self.getUnitIdx(), self.__isLocked, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.LOCK

    def isLocked(self):
        return self.__isLocked


class CloseSlotCtx(_UnitRequestCtx):

    def __init__(self, slotIdx, isClosed = True, waitingID = ''):
        super(CloseSlotCtx, self).__init__(waitingID)
        self.__slotIdx = slotIdx
        self.__isClosed = isClosed

    def __repr__(self):
        return 'CloseSlotCtx(unitIdx = {0:n}, slotIdx = {1:n}, isClosed = {2!r:s}, waitingID = {3:>s})'.format(self.getUnitIdx(), self.__slotIdx, self.__isClosed, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.CLOSE_SLOT

    def getSlotIdx(self):
        return self.__slotIdx

    def isClosed(self):
        return self.__isClosed


class SetVehicleUnitCtx(_UnitRequestCtx):

    def __init__(self, vTypeCD = 0, vehInvID = 0, waitingID = ''):
        super(SetVehicleUnitCtx, self).__init__(waitingID)
        self.__vehTypeCD = vTypeCD
        self.__vehInvID = vehInvID

    def __repr__(self):
        return 'SetVehicleUnitCtx(vTypeCD = {0:n}, vehInvID = {1:n}, waitingID = {2:>s})'.format(self.__vehTypeCD, self.__vehInvID, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.SET_VEHICLE

    def getVehTypeCD(self):
        return self.__vehTypeCD

    def getVehInvID(self):
        return self.__vehInvID


class ChangeOpenedUnitCtx(_UnitRequestCtx):

    def __init__(self, isOpened, waitingID = ''):
        super(ChangeOpenedUnitCtx, self).__init__(waitingID)
        self.__isOpened = isOpened

    def __repr__(self):
        return 'ChangeOpenedUnitCtx(unitIdx = {0:n}, isOpened = {1!r:s}, waitingID = {2:>s})'.format(self.getUnitIdx(), self.__isOpened, self.getWaitingID())

    def getRequestType(self):
        return prb_settings.REQUEST_TYPE.CHANGE_OPENED

    def isOpened(self):
        return self.__isOpened


class ChangeCommentUnitCtx(_UnitRequestCtx):

    def __init__(self, comment, waitingID = ''):
        super(ChangeCommentUnitCtx, self).__init__(waitingID)
        self.__comment = truncate_utf8(comment, prb_settings.UNIT_COMMENT_MAX_LENGTH)

    def __repr__(self):
        return 'ChangeCommentUnitCtx(unitIdx = {0:n}, comment = {1:>s}, waitingID = {2:>s})'.format(self.getUnitIdx(), self.__comment, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, unit):
        return self.__comment != unit._strComment


class SetReadyUnitCtx(_UnitRequestCtx):

    def __init__(self, isReady = True, waitingID = ''):
        super(SetReadyUnitCtx, self).__init__(waitingID)
        self.__isReady = isReady

    def __repr__(self):
        return 'SetReadyUnitCtx(unitIdx = {0:n}, isReady = {1!r:s}, waitingID = {2:>s})'.format(self.getUnitIdx(), self.__isReady, self.getWaitingID())

    def isReady(self):
        return self.__isReady

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE


class AssignUnitCtx(_UnitRequestCtx):

    def __init__(self, pID, slotIdx, waitingID = ''):
        super(AssignUnitCtx, self).__init__(waitingID)
        self.__pID = pID
        self.__slotIdx = slotIdx

    def __repr__(self):
        return 'AssignUnitCtx(unitIdx = {0:n}, pID = {1:n}, slotIdx = {2:n}, waitingID = {3:>s})'.format(self.getUnitIdx(), self.__pID, self.__slotIdx, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN

    def getPlayerID(self):
        return self.__pID

    def getSlotIdx(self):
        return self.__slotIdx


class AutoSearchUnitCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', action = 1, vehTypes = None):
        super(AutoSearchUnitCtx, self).__init__(waitingID)
        self.__action = action
        self.__vehTypes = [] if vehTypes is None else vehTypes
        return

    def __repr__(self):
        return 'AutoSearchUnitCtx(action = {0:>s}, vehTypes = {1!r:s}, waitingID = {2:>s})'.format('start' if self.__action > 0 else 'stop', self.__vehTypes, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.AUTO_SEARCH

    def isRequestToStart(self):
        return self.__action > 0

    def getVehTypes(self):
        return self.__vehTypes


class AcceptSearchUnitCtx(_UnitRequestCtx):

    def __repr__(self):
        return 'AcceptSearchUnitCtx(waitingID = {0:>s})'.format(self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.ACCEPT_SEARCH


class DeclineSearchUnitCtx(_UnitRequestCtx):

    def __repr__(self):
        return 'DeclineSearchUnitCtx(waitingID = {0:>s})'.format(self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.DECLINE_SEARCH


class BattleQueueUnitCtx(_UnitRequestCtx):

    def __init__(self, waitingID = '', action = 1, vehTypes = None):
        super(BattleQueueUnitCtx, self).__init__(waitingID)
        self.__action = action
        self.__vehTypes = [] if vehTypes is None else vehTypes
        return

    def __repr__(self):
        return 'BattleQueueUnitCtx(action = {0:>s}, waitingID = {1:>s})'.format('start' if self.__action > 0 else 'stop', self.getWaitingID())

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


class SetRostersSlotsCtx(_UnitRequestCtx):

    def __init__(self, waitingID = ''):
        super(SetRostersSlotsCtx, self).__init__(waitingID)
        self.__items = {}

    def __repr__(self):
        return 'SetRostersSlotsCtx(rostersSlots = {0!r:s}, waitingID = {1:>s})'.format(self.__items, self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.SET_ROSTERS_SLOTS

    def addRosterSlot(self, rosterSlotIdx, ctx):
        self.__items[rosterSlotIdx] = ctx.getCriteria()

    def getRosterSlots(self):
        return self.__items.copy()


class KickPlayerCtx(_UnitRequestCtx):

    def __init__(self, databaseID, waitingID = ''):
        super(KickPlayerCtx, self).__init__(waitingID)
        self.__databaseID = databaseID

    def __repr__(self):
        return 'KickPlayerCtx(databaseID = {0:n}, waitingID = {1:>s})'.format(self.__databaseID, self.getWaitingID())

    def getPlayerID(self):
        return self.__databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


__all__ = ('CreateUnitCtx', 'JoinModeCtx', 'JoinUnitCtx', 'LeaveUnitCtx', 'LockUnitCtx', 'CloseSlotCtx', 'SetVehicleUnitCtx', 'ChangeOpenedUnitCtx', 'ChangeCommentUnitCtx', 'SetReadyUnitCtx', 'AssignUnitCtx', 'AutoSearchUnitCtx', 'AcceptSearchUnitCtx', 'DeclineSearchUnitCtx', 'BattleQueueUnitCtx', 'RosterSlotCtx', 'SetRostersSlotsCtx', 'KickPlayerCtx')
