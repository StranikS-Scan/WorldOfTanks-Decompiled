# Embedded file name: scripts/client/gui/prb_control/items/unit_items.py
from collections import namedtuple
import itertools
import weakref
from UnitBase import UNIT_ROLE, UNIT_FLAGS, ROSTER_TYPE_TO_CLASS, ROSTER_TYPE, INV_ID_CLEAR_VEHICLE
from account_helpers import getAccountDatabaseID
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.context import unit_ctx
from gui.prb_control.settings import CREATOR_SLOT_INDEX, UNIT_RESTRICTION
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.utils.decorators import ReprInjector
from shared_utils import findFirst

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
        return self.role & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR and self.slotIdx == CREATOR_SLOT_INDEX

    def isInvite(self):
        return self.role & UNIT_ROLE.INVITED > 0

    def isInArena(self):
        return self.role & UNIT_ROLE.IN_ARENA > 0

    def isOffline(self):
        return self.role & UNIT_ROLE.OFFLINE > 0

    def isInSearch(self):
        if self.unit is not None:
            return self.unit.getFlags() & UNIT_FLAGS.IN_SEARCH > 0
        else:
            return False

    def isInQueue(self):
        if self.unit is not None:
            return self.unit.getFlags() & UNIT_FLAGS.IN_QUEUE > 0
        else:
            return False

    def isInPreArena(self):
        if self.unit is not None:
            return self.unit.getFlags() & UNIT_FLAGS.IN_PRE_ARENA > 0
        else:
            return False

    def isLegionary(self):
        return self.role & UNIT_ROLE.LEGIONARY > 0

    def isCurrentPlayer(self):
        return self.dbID == getAccountDatabaseID()

    def getVehiclesCDs(self):
        requestCriteria = REQ_CRITERIA.INVENTORY
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        if self.isCurrentPlayer():
            vehicles = g_itemsCache.items.getVehicles(requestCriteria).keys()
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
        if self.unit is not None and not self.isCreator() and slotIdx != CREATOR_SLOT_INDEX:
            slots = self.unit.getFreeSlots()
            if slotIdx in slots:
                vehicles = self.getVehiclesToSlot(slotIdx)
                return (len(vehicles) > 0, vehicles)
        return (False, [])

    def canAssignToSlots(self, allSlots = False):
        result = (True, UNIT_RESTRICTION.UNDEFINED)
        if self.unit is not None:
            if not len(self.unit.getFreeSlots()):
                result = (False, UNIT_RESTRICTION.UNIT_IS_FULL)
            elif not len(self.getAvailableSlots(allSlots=allSlots)):
                result = (False, UNIT_RESTRICTION.VEHICLE_NOT_FOUND)
            elif UnitFlags(self.unit.getFlags()).isLocked():
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

    def isReadyToBattle(self, state):
        result = False
        if self.vehInvID:
            vehicle = g_itemsCache.items.getVehicle(self.vehInvID)
            if vehicle:
                result = vehicle.isReadyToPrebattle(checkForRent=not state.isInPreArena())
        return result

    def updateInventory(self, vehInvCDs):
        if self.vehTypeCD and self.vehTypeCD not in vehInvCDs:
            return unit_ctx.SetVehicleUnitCtx(vehInvID=INV_ID_CLEAR_VEHICLE, waitingID='prebattle/change_settings')
        else:
            return None

    def getVehicle(self):
        if self.vehInvID:
            return g_itemsCache.items.getVehicle(self.vehInvID)
        else:
            return None


class FalloutVehiclesInfo(object):
    __slots__ = ('vehInvIDs', 'vehTypeCDs')

    def __init__(self, vehInvIDs = None, vehTypeCDs = None, **kwargs):
        super(FalloutVehiclesInfo, self).__init__()
        self.vehInvIDs = vehInvIDs or ()
        self.vehTypeCDs = vehTypeCDs or ()

    @property
    def vehInvID(self):
        if self.vehInvIDs:
            return self.vehInvIDs[0]
        return 0

    @property
    def vehTypeCD(self):
        if self.vehTypeCDs:
            return self.vehTypeCDs[0]
        return 0

    def isEmpty(self):
        return findFirst(None, self.vehInvIDs) is None

    def isReadyToBattle(self, state):
        result = False
        for vehicle in self.getVehicles():
            if vehicle:
                result = vehicle.isReadyToPrebattle(checkForRent=not state.isInPreArena())

        return result

    def updateInventory(self, vehInvCDs):
        if not self.vehTypeCDs:
            return None
        vehsList = list(self.vehInvIDs)
        isChanged = False
        for i, vCD in enumerate(self.vehTypeCDs):
            if vCD != INV_ID_CLEAR_VEHICLE and vCD not in vehInvCDs:
                vehsList[i] = INV_ID_CLEAR_VEHICLE
                isChanged = True

        if isChanged:
            return unit_ctx.SetEventVehiclesCtx(vehsList, waitingID='prebattle/change_settings')
        else:
            return None

    def getVehicles(self):
        return map(g_itemsCache.items.getVehicle, self.vehInvIDs)


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


class UnitFlags(object):
    __slots__ = ('__flags', '__flagsDiff', '__isReady')

    def __init__(self, flags, prevFlags = None, isReady = False):
        super(UnitFlags, self).__init__()
        self.__flags = flags
        self.__isReady = isReady
        self.__flagsDiff = flags ^ prevFlags if prevFlags is not None else flags
        return

    def __repr__(self):
        return 'UnitFlags(bitmask = {0!r:s}, isReady = {1!r:s}, diff = {2!r:s})'.format(self.__flags, self.__isReady, self.__flagsDiff)

    def __eq__(self, other):
        return self.__flags == other.flags

    def isLocked(self):
        return self.__flags & UNIT_FLAGS.LOCKED > 0

    def isLockedStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.LOCKED > 0

    def isOpened(self):
        return self.__flags & UNIT_FLAGS.INVITE_ONLY == 0

    def isOpenedStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.INVITE_ONLY > 0

    def isOnlyRosterWaitChanged(self):
        return self.__flagsDiff == UNIT_FLAGS.IN_ROSTER_WAIT

    def isInSearch(self):
        return self.__flags & UNIT_FLAGS.IN_SEARCH > 0 or self.__flags & UNIT_FLAGS.PRE_SEARCH > 0

    def isInQueue(self):
        return self.__flags & UNIT_FLAGS.IN_QUEUE > 0 or self.__flags & UNIT_FLAGS.PRE_QUEUE > 0

    def isInQueueChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.IN_QUEUE > 0 or self.__flagsDiff & UNIT_FLAGS.PRE_QUEUE > 0

    def isInIdle(self):
        return self.__flags & UNIT_FLAGS.MODAL_STATES > 0

    def isReady(self):
        return self.__isReady

    def isDevMode(self):
        return self.__flags & UNIT_FLAGS.DEV_MODE > 0

    def isInArena(self):
        return self.__flags & UNIT_FLAGS.IN_ARENA > 0

    def isInPreArena(self):
        return self.__flags & UNIT_FLAGS.IN_PRE_ARENA > 0

    def isFreezed(self):
        return self.isLocked() or self.isInSearch() or self.isInQueue() or self.isInArena() or self.isInPreArena()

    def isChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.CHANGED_STATE_ASQ > 0

    def isPreArenaChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.IN_PRE_ARENA > 0


UnitStats = namedtuple('UnitStats', ('readyCount', 'occupiedSlotsCount', 'openedSlotsCount', 'freeSlotsCount', 'curTotalLevel', 'levelsSeq', 'minTotalLevel', 'maxTotalLevel'))

@ReprInjector.simple(('_minLevel', 'minLevel'), ('_maxLevel', 'maxLevel'), ('_maxSlots', 'maxSlots'), ('_maxClosedSlots', 'maxClosedSlots'), ('_maxEmptySlots', 'maxEmptySlots'), ('_minTotalLevel', 'minTotalLevel'), ('_maxTotalLevel', 'maxTotalLevel'), ('_maxLegionariesCount', 'maxLegionariesCount'))

class UnitRosterSettings(object):
    TOTAL_SLOTS = 15
    __slots__ = ('_minLevel', '_maxLevel', '_maxSlots', '_maxClosedSlots', '_maxEmptySlots', '_minTotalLevel', '_maxTotalLevel', '_maxLegionariesCount', '__weakref__')

    def __init__(self, minLevel = 1, maxLevel = 10, maxSlots = TOTAL_SLOTS, maxClosedSlots = 0, maxEmptySlots = 0, minTotalLevel = 1, maxTotalLevel = 150, maxLegionariesCount = 0):
        super(UnitRosterSettings, self).__init__()
        self._minLevel = minLevel
        self._maxLevel = maxLevel
        self._maxSlots = maxSlots
        self._maxClosedSlots = maxClosedSlots
        self._maxEmptySlots = maxEmptySlots
        self._minTotalLevel = minTotalLevel
        self._maxTotalLevel = maxTotalLevel
        self._maxLegionariesCount = maxLegionariesCount

    def getMinLevel(self):
        return self._minLevel

    def getMaxLevel(self):
        return self._maxLevel

    def getMinTotalLevel(self):
        return self._minTotalLevel

    def getMaxTotalLevel(self):
        return self._maxTotalLevel

    def getLevelsRange(self):
        return range(self._minLevel, self._maxLevel + 1)

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

    def getLegionariesMaxCount(self):
        return self._maxLegionariesCount


class DynamicRosterSettings(UnitRosterSettings):

    def __init__(self, unit):
        kwargs = {}
        roster = None
        if unit is not None:
            roster = unit.getRoster()
        if roster is not None:
            kwargs['minLevel'], kwargs['maxLevel'] = roster.SLOT_TYPE.DEFAULT_LEVELS
            kwargs['maxSlots'] = roster.MAX_SLOTS
            kwargs['maxClosedSlots'] = roster.MAX_CLOSED_SLOTS
            kwargs['maxEmptySlots'] = roster.MAX_EMPTY_SLOTS
            kwargs['minTotalLevel'] = roster.MIN_UNIT_POINTS_SUM
            kwargs['maxTotalLevel'] = roster.MAX_UNIT_POINTS_SUM
            kwargs['maxLegionariesCount'] = unit.getLegionaryMaxCount()
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
        maxLegionariesCount = clazz.MAX_LEGIONARIES_COUNT
        super(PredefinedRosterSettings, self).__init__(minLevel, maxLevel, maxSlots, maxClosedSlots, maxEmptySlots, minTotalLevel, maxTotalLevel, maxLegionariesCount)

    def getDisabledSlotsRange(self):
        if self._rosterTypeID in _SUPPORTED_ROSTER_SETTINGS[PREBATTLE_TYPE.SORTIE]:
            return xrange(self._maxSlots, self.TOTAL_SLOTS)
        return super(PredefinedRosterSettings, self).getDisabledSlotsRange()


_SUPPORTED_ROSTER_SETTINGS = {PREBATTLE_TYPE.UNIT: (ROSTER_TYPE.UNIT_ROSTER,),
 PREBATTLE_TYPE.SORTIE: (ROSTER_TYPE.SORTIE_ROSTER_6, ROSTER_TYPE.SORTIE_ROSTER_8, ROSTER_TYPE.SORTIE_ROSTER_10),
 PREBATTLE_TYPE.FORT_BATTLE: (ROSTER_TYPE.FORT_ROSTER_10,),
 PREBATTLE_TYPE.CLUBS: (ROSTER_TYPE.CLUB_ROSTER_10,)}

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
