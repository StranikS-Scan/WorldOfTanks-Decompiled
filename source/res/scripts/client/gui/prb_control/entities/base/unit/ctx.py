# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/ctx.py
from account_helpers import gameplay_ctx
from external_strings_utils import truncate_utf8
from UnitBase import UNIT_SLOT
from gui.prb_control import settings, prb_getters
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx
from gui.shared.utils.decorators import ReprInjector
_CTRL_ENTITY_TYPE = settings.CTRL_ENTITY_TYPE
_REQUEST_TYPE = settings.REQUEST_TYPE
_UNDEFINED = settings.FUNCTIONAL_FLAG.UNDEFINED

@ReprInjector.withParent(('getID', 'unitMgrID'))
class UnitRequestCtx(PrbCtrlRequestCtx):
    """
    Base context for all unit requests.
    """
    __slots__ = ()

    def __init__(self, **kwargs):
        super(UnitRequestCtx, self).__init__(ctrlType=_CTRL_ENTITY_TYPE.UNIT, **kwargs)

    def getID(self):
        """
        Getter for joined unit index.
        """
        return prb_getters.getUnitMgrID()

    def getCooldown(self):
        pass


@ReprInjector.withParent(('__rosterID', 'rosterID'))
class CreateUnitCtx(UnitRequestCtx):
    """
    Context for unit creation request.
    """
    __slots__ = ('__rosterID',)

    def __init__(self, prbType, flags=_UNDEFINED, waitingID='', rosterID=0):
        super(CreateUnitCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)
        self.__rosterID = rosterID

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE

    def getRosterID(self):
        """
        Unit roster type ID.
        """
        return self.__rosterID


class JoinUnitModeCtx(UnitRequestCtx):
    """
    Context for join unit mode request.
    """
    __slots__ = ()

    def __init__(self, prbType, waitingID='', flags=_UNDEFINED):
        super(JoinUnitModeCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)

    def getID(self):
        """
        Getter for current unit manager ID
        """
        return prb_getters.getUnitMgrID()


@ReprInjector.withParent(('__unitMgrID', 'unitMgrID'), ('__slotIdx', 'slotIdx'))
class JoinUnitCtx(UnitRequestCtx):
    """
    Context for join unit request.
    """
    __slots__ = ('__unitMgrID', '__slotIdx')

    def __init__(self, unitMgrID, prbType, slotIdx=None, waitingID=''):
        super(JoinUnitCtx, self).__init__(entityType=prbType, waitingID=waitingID)
        self.__unitMgrID = unitMgrID
        self.__slotIdx = slotIdx

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN

    def getID(self):
        """
        Getter for unit manager ID of entity we're joining to.
        """
        return self.__unitMgrID

    def getSlotIdx(self):
        """
        Getter for slot index that we're trying to get.
        """
        return self.__slotIdx


class LeaveUnitCtx(UnitRequestCtx):
    """
    Context for join unit request.
    """

    def __init__(self, waitingID='', flags=_UNDEFINED, entityType=0):
        super(LeaveUnitCtx, self).__init__(waitingID=waitingID, flags=flags, entityType=entityType)

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE


@ReprInjector.withParent(('__isLocked', 'isLocked'))
class LockUnitCtx(UnitRequestCtx):
    """
    Unit lock/unlock request context.
    """
    __slots__ = ('__isLocked',)

    def __init__(self, isLocked=True, waitingID=''):
        super(LockUnitCtx, self).__init__(waitingID=waitingID)
        self.__isLocked = isLocked

    def getRequestType(self):
        return _REQUEST_TYPE.LOCK

    def isLocked(self):
        """
        Lock state getter.
        """
        return self.__isLocked


@ReprInjector.withParent(('__slotIdx', 'slotIdx'), ('__isClosed', 'isClosed'))
class CloseSlotUnitCtx(UnitRequestCtx):
    """
    Context for close/open slot request.
    """
    __slots__ = ('__slotIdx', '__isClosed')

    def __init__(self, slotIdx, isClosed=True, waitingID=''):
        super(CloseSlotUnitCtx, self).__init__(waitingID=waitingID)
        self.__slotIdx = slotIdx
        self.__isClosed = isClosed

    def getRequestType(self):
        return _REQUEST_TYPE.CLOSE_SLOT

    def getSlotIdx(self):
        """
        Getter for slot index for operation
        """
        return self.__slotIdx

    def isClosed(self):
        """
        Close/open flag getter
        """
        return self.__isClosed


@ReprInjector.withParent(('__vehTypeCD', 'vTypeCD'), ('__vehInvID', 'vehInvID'))
class SetVehicleUnitCtx(UnitRequestCtx):
    """
    Context for setting unit vehicle request
    """
    __slots__ = ('__vehTypeCD', '__vehInvID', 'setReady')

    def __init__(self, vTypeCD=0, vehInvID=0, waitingID=''):
        super(SetVehicleUnitCtx, self).__init__(waitingID=waitingID)
        self.__vehTypeCD = vTypeCD
        self.__vehInvID = vehInvID
        self.setReady = False

    def getRequestType(self):
        return _REQUEST_TYPE.SET_VEHICLE

    def getVehTypeCD(self):
        """
        Getter for selecting vehicle's compact descriptor
        """
        return self.__vehTypeCD

    def getVehInvID(self):
        """
        Getter for selecting vehicle's inventory ID
        """
        return self.__vehInvID


@ReprInjector.withParent(('__isOpened', 'isOpened'))
class ChangeOpenedUnitCtx(UnitRequestCtx):
    """
    Change opened/closed unit state context.
    """
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, waitingID=''):
        super(ChangeOpenedUnitCtx, self).__init__(waitingID=waitingID)
        self.__isOpened = isOpened

    def getRequestType(self):
        return settings.REQUEST_TYPE.CHANGE_OPENED

    def isOpened(self):
        """
        Is it opened or closed.
        """
        return self.__isOpened


@ReprInjector.withParent(('__comment', 'comment'))
class ChangeCommentUnitCtx(UnitRequestCtx):
    """
    Context for changing unit's comment.
    """
    __slots__ = ('__comment',)

    def __init__(self, comment, waitingID=''):
        super(ChangeCommentUnitCtx, self).__init__(waitingID=waitingID)
        self.__comment = truncate_utf8(comment, settings.UNIT_COMMENT_MAX_LENGTH)

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT

    def getComment(self):
        """
        Obvious getter for comment itself.
        """
        return self.__comment

    def isCommentChanged(self, unit):
        """
        Is this new comment or old one.
        """
        return self.__comment != unit.getComment()


@ReprInjector.withParent(('resetVehicle', 'resetVehicle'), ('__isReady', 'isReady'))
class SetReadyUnitCtx(UnitRequestCtx):
    """
    Context for setting current player's state to ready/not ready.
    """
    __slots__ = ('__isReady', 'resetVehicle')

    def __init__(self, isReady=True, waitingID=''):
        super(SetReadyUnitCtx, self).__init__(waitingID=waitingID)
        self.__isReady = isReady
        self.resetVehicle = False

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE

    def isReady(self):
        """
        Is this player should become ready or not ready.
        """
        return self.__isReady


@ReprInjector.withParent(('__pID', 'pID'), ('__slotIdx', 'slotIdx'))
class AssignUnitCtx(UnitRequestCtx):
    """
    Context for assigning player to some slot in unit
    """
    __slots__ = ('__pID', '__slotIdx')

    def __init__(self, pID, slotIdx, waitingID=''):
        super(AssignUnitCtx, self).__init__(waitingID=waitingID)
        self.__pID = pID
        self.__slotIdx = slotIdx

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN

    def getPlayerID(self):
        """
        Getter for player's ID
        """
        return self.__pID

    def getSlotIdx(self):
        """
        Assigning slot index
        """
        return self.__slotIdx

    def isRemove(self):
        return self.__slotIdx == UNIT_SLOT.REMOVE


@ReprInjector.withParent(('__action', 'action'), ('__vehTypes', 'vehTypes'))
class AutoSearchUnitCtx(UnitRequestCtx):
    """
    Context to start or stop auto-search for solo-player
    """
    __slots__ = ('__action', '__vehTypes')

    def __init__(self, waitingID='', action=1, vehTypes=None):
        super(AutoSearchUnitCtx, self).__init__(waitingID=waitingID)
        self.__action = action
        self.__vehTypes = [] if vehTypes is None else vehTypes
        return

    def getRequestType(self):
        return _REQUEST_TYPE.AUTO_SEARCH

    def getAction(self):
        return self.__action

    def getActionName(self):
        """
        Getter for action's name.
        """
        return 'start' if self.__action > 0 else 'stop'

    def isRequestToStart(self):
        """
        Is this requst to start or stop auto-search
        """
        return self.__action > 0

    def getVehTypes(self):
        """
        Getter for prefered vehicle's intCD's
        """
        return self.__vehTypes


class AcceptSearchUnitCtx(UnitRequestCtx):
    """
    Context for auto-search accept request
    """
    __slots__ = ()

    def getRequestType(self):
        return _REQUEST_TYPE.ACCEPT_SEARCH


class DeclineSearchUnitCtx(UnitRequestCtx):
    """
    Context for auto-search accept decline
    """
    __slots__ = ()

    def getRequestType(self):
        return _REQUEST_TYPE.DECLINE_SEARCH


@ReprInjector.withParent(('selectVehInvID', 'selectVehInvID'), ('getGamePlayMask', 'gamePlayMask'), ('getDemoArenaTypeID', 'getDemoArenaTypeID'))
class BattleQueueUnitCtx(AutoSearchUnitCtx):
    """
    Context for enqueue unit request
    """
    __slots__ = ('selectVehInvID', '__isActionStartBattle', 'mapID')

    def __init__(self, waitingID='', action=1, vehTypes=None):
        super(BattleQueueUnitCtx, self).__init__(waitingID=waitingID, action=action, vehTypes=vehTypes)
        self.selectVehInvID = 0
        self.mapID = 0

    def getRequestType(self):
        return _REQUEST_TYPE.BATTLE_QUEUE

    def getGamePlayMask(self):
        """
        Getter for selected gameplay mask.
        """
        return gameplay_ctx.getMask()

    def getDemoArenaTypeID(self):
        """
        Gets map arena type ID
        """
        return self.mapID


class RosterSlotCtx(object):
    """
    Context for forward set rosters slots request which holds information about
    roster restrictions set to proper slot.
    """

    def __init__(self, vehTypeCD=None, nationNames=None, levels=None, vehClassNames=None):
        self.__vehTypeCD = vehTypeCD
        self.__nationNames = nationNames
        self.__vehLevels = levels
        self.__vehClassNames = vehClassNames

    def getCriteria(self):
        """
        Getter for slot criteria.
        """
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


@ReprInjector.withParent(('__items', 'rostersSlots'))
class SetRostersSlotsUnitCtx(UnitRequestCtx):
    """
    Context for setting rosters in slots
    """
    __slots__ = ('__items',)

    def __init__(self, waitingID=''):
        super(SetRostersSlotsUnitCtx, self).__init__(waitingID=waitingID)
        self.__items = {}

    def getRequestType(self):
        return _REQUEST_TYPE.SET_ROSTERS_SLOTS

    def addRosterSlot(self, rosterSlotIdx, ctx):
        """
        Adds roster for given index.
        Args:
            rosterSlotIdx: slot index
            ctx: roster slot context
        """
        self.__items[rosterSlotIdx] = ctx.getCriteria()

    def getRosterSlots(self):
        """
        Getter for criteria in all slots provided.
        """
        return self.__items.copy()


@ReprInjector.withParent(('__databaseID', 'databaseID'))
class KickPlayerUnitCtx(UnitRequestCtx):
    """
    Context for player's kick
    """
    __slots__ = ('__databaseID',)

    def __init__(self, databaseID, waitingID=''):
        super(KickPlayerUnitCtx, self).__init__(waitingID=waitingID)
        self.__databaseID = databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK

    def getPlayerID(self):
        """
        Getter for database ID of player to kick
        """
        return self.__databaseID


@ReprInjector.withParent(('__databaseID', 'databaseID'))
class GiveLeadershipUnitCtx(UnitRequestCtx):
    """
    Context for giving leadership from commander to other player
    """
    __slots__ = ('__databaseID',)

    def __init__(self, databaseID, waitingID=''):
        super(GiveLeadershipUnitCtx, self).__init__(waitingID=waitingID)
        self.__databaseID = databaseID

    def getRequestType(self):
        return _REQUEST_TYPE.GIVE_LEADERSHIP

    def getPlayerID(self):
        """
        Getter for database ID of player to kick
        """
        return self.__databaseID


@ReprInjector.withParent(('__division', 'division'))
class ChangeDivisionUnitCtx(UnitRequestCtx):
    """
    Context for changing unit's division
    """
    __slots__ = ('__divisionID',)

    def __init__(self, divisionID, waitingID=''):
        super(ChangeDivisionUnitCtx, self).__init__(waitingID=waitingID)
        self.__divisionID = divisionID

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_DIVISION

    def getDivisionID(self):
        """
        Getter for new division ID
        """
        return self.__divisionID


@ReprInjector.withParent(('__vehsList', 'vehsList'))
class SetVehiclesUnitCtx(UnitRequestCtx):
    """
    Context for setting player's vehicles
    """
    __slots__ = ('__vehsList',)

    def __init__(self, vehsList, waitingID=''):
        super(SetVehiclesUnitCtx, self).__init__(waitingID=waitingID)
        self.__vehsList = vehsList

    def getRequestType(self):
        return _REQUEST_TYPE.SET_VEHICLE_LIST

    def getCooldown(self):
        pass

    def getVehsList(self):
        """
        Getter for selected vehicles inventory IDs list
        """
        return self.__vehsList
