# Embedded file name: scripts/client/gui/prb_control/items/unit_items.py
from collections import namedtuple
import itertools
import weakref
from UnitBase import UNIT_ROLE, UNIT_STATE, ROSTER_TYPE_TO_CLASS, ROSTER_TYPE
from account_helpers import getPlayerDatabaseID
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.settings import CREATOR_SLOT_INDEX, UNIT_RESTRICTION
from gui.shared import g_itemsCache, REQ_CRITERIA

class PlayerUnitInfo(object):
    __slots__ = ('dbID', 'unitIdx', 'unit', 'name', 'rating', 'role', 'accID', 'vehDict', 'isReady', 'isInSlot', 'slotIdx', 'regionCode', 'clanDBID', 'clanAbbrev', 'timeJoin', 'igrType')

    def __init__(self, dbID, unitIdx, unit, nickName = '', rating = 0, role = 0, accountID = 0, vehDict = None, isReady = False, isInSlot = False, slotIdx = -1, clanAbbrev = None, timeJoin = 0, igrType = 0, **kwargs):
        self.dbID = dbID
        self.unitIdx = unitIdx
        if unit is not None:
            self.unit = weakref.proxy(unit)
        else:
            self.unit = None
        self.name = nickName
        self.rating = rating
        self.role = role
        self.accID = accountID
        self.vehDict = vehDict or {}
        self.isReady = isReady
        self.isInSlot = isInSlot
        self.slotIdx = slotIdx
        self.clanDBID = None
        self.clanAbbrev = clanAbbrev
        self.timeJoin = timeJoin
        self.igrType = igrType
        return

    def __repr__(self):
        return 'PlayerUnitInfo(dbID = {0:n}, fullName = {1:>s}, unitIdx = {2:n} rating = {3:n}, isCreator = {4!r:s}, role = {5:n}, accID = {6:n}, isReady={7!r:s}, isInSlot={8!r:s}, igrType = {9:n})'.format(self.dbID, self.getFullName(), self.unitIdx, self.rating, self.isCreator(), self.role, self.accID, self.isReady, self.isInSlot, self.igrType)

    def getFullName(self):
        return g_lobbyContext.getPlayerFullName(self.name, clanAbbrev=self.clanAbbrev, pDBID=self.dbID)

    def getRegion(self):
        return g_lobbyContext.getRegionCode(self.dbID)

    def isCreator(self):
        return self.role & UNIT_ROLE.COMMANDER_UPDATES > 0

    def isInvite(self):
        return self.role & UNIT_ROLE.INVITED > 0

    def isInArena(self):
        return self.role & UNIT_ROLE.IN_ARENA > 0

    def isOffline(self):
        return self.role & UNIT_ROLE.OFFLINE > 0

    def isInSearch(self):
        if self.unit is not None:
            return self.unit.getState() & UNIT_STATE.IN_SEARCH > 0
        else:
            return False

    def isInQueue(self):
        if self.unit is not None:
            return self.unit.getState() & UNIT_STATE.IN_QUEUE > 0
        else:
            return False

    def isLegionary(self):
        return self.role & UNIT_ROLE.LEGIONARY > 0

    def isCurrentPlayer(self):
        return self.dbID == getPlayerDatabaseID()

    def getVehiclesCDs(self):
        if self.isCurrentPlayer():
            vehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).keys()
        else:
            vehicles = self.vehDict.keys()
        return vehicles or []

    def getVehiclesToSlot(self, slotIdx):
        if self.unit is not None:
            checkVehicle = self.unit.getRoster().checkVehicle
            validator = lambda vehCD: checkVehicle(vehCD, slotIdx)[0]
            return filter(validator, self.getVehiclesCDs())
        else:
            return []

    def canAssignToSlot(self, slotIdx):
        result = (False, [])
        if self.unit is not None and not self.isCreator() and slotIdx != CREATOR_SLOT_INDEX:
            slots = self.unit.getFreeSlots()
            if slotIdx in slots:
                vehicles = self.getVehiclesToSlot(slotIdx)
                result = (len(vehicles) > 0, vehicles)
        return result

    def canAssignToSlots(self, allSlots = False):
        result = (True, UNIT_RESTRICTION.UNDEFINED)
        if self.unit is not None:
            if not len(self.unit.getFreeSlots()):
                result = (False, UNIT_RESTRICTION.UNIT_IS_FULL)
            elif not len(self.getAvailableSlots(allSlots=allSlots)):
                result = (False, UNIT_RESTRICTION.VEHICLE_NOT_FOUND)
            elif UnitState(self.unit.getState()).isLocked():
                result = (False, UNIT_RESTRICTION.UNIT_IS_LOCKED)
        return result

    def getVehiclesToSlots(self, allSlots = False):
        if self.unit is not None:
            slots = self.unit.getFreeSlots()
            if allSlots:
                slots = set(list(slots) + self.unit.getPlayerSlots().values())
            return self.unit.getRoster().matchVehicleListToSlotList(self.getVehiclesCDs(), slots)
        else:
            return {}

    def getAvailableSlots(self, allSlots = False):
        matches = self.getVehiclesToSlots(allSlots)
        return set(itertools.chain(*matches.values()))

    def getSlotsToVehicles(self, allSlots = False):
        matches = self.getVehiclesToSlots(allSlots)
        slots = set(itertools.chain(*matches.values()))
        result = {}
        for slot in slots:
            result[slot] = list(itertools.ifilter(lambda v: slot in matches[v], matches.iterkeys()))

        return result

    @classmethod
    def fromPrbInfo(cls, prbInfo, slotIdx = -1):
        role = UNIT_ROLE.DEFAULT
        if prbInfo.isCreator:
            role |= UNIT_ROLE.COMMANDER_UPDATES | UNIT_ROLE.CHANGE_ROSTER
        if prbInfo.isOffline():
            role |= UNIT_ROLE.OFFLINE
        if prbInfo.inBattle():
            role |= UNIT_ROLE.IN_ARENA
        return PlayerUnitInfo(prbInfo.dbID, -1, None, prbInfo.name, accountID=prbInfo.accID, role=role, isReady=prbInfo.isReady(), isInSlot=True, clanAbbrev=prbInfo.clanAbbrev, igrType=prbInfo.igrType, slotIdx=slotIdx)


class VehicleInfo(object):
    __slots__ = ('vehInvID', 'vehTypeCD', 'vehLevel')

    def __init__(self, vehInvID = 0, vehTypeCompDescr = 0, vehLevel = 0, **kwargs):
        super(VehicleInfo, self).__init__()
        self.vehInvID = vehInvID
        self.vehTypeCD = vehTypeCompDescr
        self.vehLevel = vehLevel

    def __repr__(self):
        return 'VehicleInfo(vehInvID = {0:n}, vehTypeCD = {1:n}, vehLevel = {2:n})'.format(self.vehInvID, self.vehTypeCD, self.vehLevel)

    def isEmpty(self):
        return not self.vehInvID

    def isReadyToBattle(self):
        result = False
        if self.vehInvID:
            vehicle = g_itemsCache.items.getVehicle(self.vehInvID)
            if vehicle:
                result = vehicle.isReadyToPrebattle
        return result


class SlotState(object):
    __slots__ = ('isClosed', 'isFree')

    def __init__(self, isClosed = False, isFree = True):
        super(SlotState, self).__init__()
        self.isClosed = isClosed
        self.isFree = isFree

    def __repr__(self):
        return 'SlotState(isClosed = {0!r:s}, isFree = {1!r:s})'.format(self.isClosed, self.isFree)


class SlotInfo(object):
    __slots__ = ('index', 'state', 'player', 'vehicle')

    def __init__(self, index, state, player = None, vehicle = None):
        super(SlotInfo, self).__init__()
        self.index = index
        self.state = state
        self.player = player
        self.vehicle = vehicle

    def __repr__(self):
        return 'SlotInfo(index = {0:n}, state = {1!r:s}, player = {2!r:s}, vehicle = {3!r:s})'.format(self.index, self.state, self.player, self.vehicle)


class UnitState(object):
    __slots__ = ('__state', '__stateDiff', '__isReady')

    def __init__(self, state, prevState = None, isReady = False):
        super(UnitState, self).__init__()
        self.__state = state
        self.__isReady = isReady
        self.__stateDiff = state ^ prevState if prevState is not None else state
        return

    def __repr__(self):
        return 'UnitState(bitmask = {0!r:s}, isReady = {1!r:s}, diff = {2!r:s})'.format(self.__state, self.__isReady, self.__stateDiff)

    def __eq__(self, other):
        return self.__state == other.state

    def isLocked(self):
        return self.__state & UNIT_STATE.LOCKED > 0

    def isLockedStateChanged(self):
        return self.__stateDiff & UNIT_STATE.LOCKED > 0

    def isOpened(self):
        return self.__state & UNIT_STATE.INVITE_ONLY == 0

    def isOpenedStateChanged(self):
        return self.__stateDiff & UNIT_STATE.INVITE_ONLY > 0

    def isInSearch(self):
        return self.__state & UNIT_STATE.IN_SEARCH > 0 or self.__state & UNIT_STATE.PRE_SEARCH > 0

    def isInQueue(self):
        return self.__state & UNIT_STATE.IN_QUEUE > 0 or self.__state & UNIT_STATE.PRE_QUEUE > 0

    def isInIdle(self):
        return self.__state & UNIT_STATE.MODAL_STATES > 0

    def isReady(self):
        return self.__isReady

    def isDevMode(self):
        return self.__state & UNIT_STATE.DEV_MODE > 0

    def isInArena(self):
        return self.__state & UNIT_STATE.IN_ARENA > 0

    def isSortie(self):
        return self.__state & UNIT_STATE.SORTIE > 0

    def isFortBattle(self):
        return self.__state & UNIT_STATE.FORT_BATTLE > 0


UnitStats = namedtuple('UnitStats', ('readyCount', 'occupiedSlotsCount', 'openedSlotsCount', 'freeSlotsCount', 'curTotalLevel', 'levelsSeq', 'minTotalLevel', 'maxTotalLevel'))

class UnitRosterSettings(object):
    TOTAL_SLOTS = 15
    __slots__ = ('_minLevel', '_maxLevel', '_maxSlots', '_maxClosedSlots', '_maxEmptySlots', '_minTotalLevel', '_maxTotalLevel')

    def __init__(self, minLevel = 1, maxLevel = 10, maxSlots = TOTAL_SLOTS, maxClosedSlots = 0, maxEmptySlots = 0, minTotalLevel = 1, maxTotalLevel = 150):
        super(UnitRosterSettings, self).__init__()
        self._minLevel = minLevel
        self._maxLevel = maxLevel
        self._maxSlots = maxSlots
        self._maxClosedSlots = maxClosedSlots
        self._maxEmptySlots = maxEmptySlots
        self._minTotalLevel = minTotalLevel
        self._maxTotalLevel = maxTotalLevel

    def __repr__(self):
        return '{0:>s}(minLevel = {1:n}, maxLevel = {2:n}, maxSlots = {3:n}, maxClosedSlots = {4:n}, maxEmptySlots = {5:n}, minTotalLevel = {6:n}, maxTotalLevel = {7:n})'.format(self.__class__.__name__, self._minLevel, self._maxLevel, self._maxSlots, self._maxClosedSlots, self._maxEmptySlots, self._minTotalLevel, self._maxTotalLevel)

    def getMinLevel(self):
        return self._minLevel

    def getMaxLevel(self):
        return self._maxLevel

    def getMinTotalLevel(self):
        return self._minTotalLevel

    def getMaxTotalLevel(self):
        return self._maxTotalLevel

    def getLevelsRange(self):
        return xrange(self._minLevel, self._maxLevel + 1)

    def getAllSlotsRange(self):
        return xrange(CREATOR_SLOT_INDEX, self._maxSlots)

    def getPlayersSlotsRange(self):
        return xrange(CREATOR_SLOT_INDEX + 1, self._maxSlots)

    def getMaxSlots(self):
        return self._maxSlots

    def getMaxClosedSlots(self):
        return self._maxClosedSlots

    def getMaxEmptySlots(self):
        return self._maxEmptySlots

    def getMinSlots(self):
        return self.getMaxSlots() - self.getMaxEmptySlots()

    def getDisabledSlotsRange(self):
        return tuple()


class DynamicRosterSettings(UnitRosterSettings):

    def __init__(self, unit):
        kwargs = {}
        roster = None
        if unit:
            roster = unit.getRoster()
        if roster:
            kwargs['minLevel'], kwargs['maxLevel'] = roster.SLOT_TYPE.DEFAULT_LEVELS
            kwargs['maxSlots'] = roster.MAX_SLOTS
            kwargs['maxClosedSlots'] = roster.MAX_CLOSED_SLOTS
            kwargs['maxEmptySlots'] = roster.MAX_EMPTY_SLOTS
            kwargs['minTotalLevel'] = roster.MIN_UNIT_POINTS_SUM
            kwargs['maxTotalLevel'] = roster.MAX_UNIT_POINTS_SUM
        else:
            LOG_ERROR('Unit roster is not defined')
        super(DynamicRosterSettings, self).__init__(**kwargs)
        return


class PredefinedRosterSettings(UnitRosterSettings):

    def __init__(self, rosterTypeID):
        self._rosterTypeID = rosterTypeID
        clazz = ROSTER_TYPE_TO_CLASS[rosterTypeID]
        minLevel, maxLevel = clazz.SLOT_TYPE.DEFAULT_LEVELS
        maxSlots = clazz.MAX_SLOTS
        maxClosedSlots = clazz.MAX_CLOSED_SLOTS
        maxEmptySlots = clazz.MAX_EMPTY_SLOTS
        minTotalLevel = clazz.MIN_UNIT_POINTS_SUM
        maxTotalLevel = clazz.MAX_UNIT_POINTS_SUM
        super(PredefinedRosterSettings, self).__init__(minLevel, maxLevel, maxSlots, maxClosedSlots, maxEmptySlots, minTotalLevel, maxTotalLevel)

    def getDisabledSlotsRange(self):
        if self._rosterTypeID in _SUPPORTED_ROSTER_SETTINGS[PREBATTLE_TYPE.SORTIE]:
            return xrange(self._maxSlots, self.TOTAL_SLOTS)
        return super(PredefinedRosterSettings, self).getDisabledSlotsRange()


_SUPPORTED_ROSTER_SETTINGS = {PREBATTLE_TYPE.UNIT: (ROSTER_TYPE.UNIT_ROSTER,),
 PREBATTLE_TYPE.SORTIE: (ROSTER_TYPE.SORTIE_ROSTER_6, ROSTER_TYPE.SORTIE_ROSTER_8, ROSTER_TYPE.SORTIE_ROSTER_10),
 PREBATTLE_TYPE.FORT_BATTLE: (ROSTER_TYPE.FORT_ROSTER_10,)}

class SupportedRosterSettings(object):

    @classmethod
    def last(cls, prbType):
        if prbType in _SUPPORTED_ROSTER_SETTINGS:
            return PredefinedRosterSettings(_SUPPORTED_ROSTER_SETTINGS[prbType][-1])
        raise KeyError, 'Unit type is not supported {0}'.format(prbType)

    @classmethod
    def list(cls, prbType):
        if prbType in _SUPPORTED_ROSTER_SETTINGS:
            seq = _SUPPORTED_ROSTER_SETTINGS[prbType]
            result = []
            for rosterTypeID in seq:
                result.append(PredefinedRosterSettings(rosterTypeID))

            return result
        raise KeyError, 'Unit type is not supported {0}'.format(prbType)


def getUnitCandidatesComparator():

    def comparator(playerData, otherData):
        unitInfo, chatUser = playerData
        otherInfo, otherUser = otherData
        if chatUser is not None:
            isUserFriend = chatUser.isFriend()
        else:
            isUserFriend = False
        if otherUser is not None:
            isOtherFriend = otherUser.isFriend()
        else:
            isOtherFriend = False
        if isUserFriend ^ isOtherFriend:
            result = -1 if isUserFriend else 1
        elif unitInfo.isInvite() ^ otherInfo.isInvite():
            result = 1 if unitInfo.isInvite() else -1
        else:
            result = cmp(unitInfo.timeJoin, otherInfo.timeJoin)
        return result

    return comparator
