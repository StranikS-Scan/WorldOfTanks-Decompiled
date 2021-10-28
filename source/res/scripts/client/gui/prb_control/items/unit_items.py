# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/unit_items.py
import itertools
import weakref
from collections import namedtuple
from UnitBase import UNIT_ROLE, UNIT_FLAGS, ROSTER_TYPE_TO_CLASS, ROSTER_TYPE
from account_helpers import getAccountDatabaseID
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.prb_helpers import BadgesHelper
from helpers import dependency
from gui.prb_control.settings import CREATOR_SLOT_INDEX
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException

class PlayerUnitInfo(object):
    __slots__ = ('dbID', 'unitMgrID', 'unit', 'name', 'rating', 'accountWTR', 'role', 'accID', 'vehDict', 'isReady', 'isInSlot', 'slotIdx', 'regionCode', 'clanDBID', 'clanAbbrev', 'timeJoin', 'igrType', 'badges', 'hasPremium', 'extraData', 'afkIsBanned', 'afkExpireTime')
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, dbID, unitMgrID, unit, nickName='', rating=0, accountWTR=0, role=0, accountID=0, vehDict=None, isReady=False, isInSlot=False, slotIdx=-1, clanAbbrev=None, timeJoin=0, igrType=0, clanDBID=None, badges=None, **kwargs):
        self.dbID = dbID
        self.unitMgrID = unitMgrID
        if unit is not None:
            self.unit = weakref.proxy(unit)
        else:
            self.unit = None
        self.name = nickName
        self.rating = rating
        self.accountWTR = accountWTR
        self.role = role
        self.accID = accountID
        self.vehDict = vehDict or {}
        self.isReady = isReady
        self.isInSlot = isInSlot
        self.slotIdx = slotIdx
        self.clanDBID = clanDBID
        self.clanAbbrev = clanAbbrev
        self.timeJoin = timeJoin
        self.igrType = igrType
        self.badges = BadgesHelper(badges or ())
        self.hasPremium = kwargs.get('isPremium', False)
        self.extraData = kwargs.get('extraData', {})
        self.afkIsBanned = kwargs.get('afkIsBanned', False)
        self.afkExpireTime = kwargs.get('afkExpireTime', 0)
        return

    def __repr__(self):
        return 'PlayerUnitInfo(dbID = {0:n}, fullName = {1:>s}, unitMgrID = {2:n} rating = {3:n}, isCommander = {4!r:s}, role = {5:n}, accID = {6:n}, isReady={7!r:s}, isInSlot={8!r:s}, igrType = {9:n}, accountWTR = {10:n})'.format(self.dbID, self.getFullName(), self.unitMgrID, self.rating, self.isCommander(), self.role, self.accID, self.isReady, self.isInSlot, self.igrType, self.accountWTR)

    def getFullName(self):
        return self.lobbyContext.getPlayerFullName(self.name, clanAbbrev=self.clanAbbrev, pDBID=self.dbID)

    def getRegion(self):
        return self.lobbyContext.getRegionCode(self.dbID)

    def isCommander(self):
        return self.role & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR and self.slotIdx == CREATOR_SLOT_INDEX

    def isInvite(self):
        return self.role & UNIT_ROLE.INVITED > 0

    def isInArena(self):
        return self.role & UNIT_ROLE.IN_ARENA > 0

    def isOffline(self):
        return self.role & UNIT_ROLE.OFFLINE > 0

    def isInSearch(self):
        return self.unit.getFlags() & UNIT_FLAGS.IN_SEARCH > 0 if self.unit is not None else False

    def isFinishAssembling(self):
        return self.unit.getFlags() & UNIT_FLAGS.FINISH_ASSEMBLING > 0 if self.unit is not None else False

    def isInQueue(self):
        return self.unit.getFlags() & UNIT_FLAGS.IN_QUEUE > 0 if self.unit is not None else False

    def isLegionary(self):
        return self.role & UNIT_ROLE.LEGIONARY > 0

    def isCurrentPlayer(self):
        return self.dbID == getAccountDatabaseID()

    def getVehiclesCDs(self):
        requestCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        if self.isCurrentPlayer():
            vehicles = self.itemsCache.items.getVehicles(requestCriteria).keys()
        else:
            vehicles = self.vehDict.keys()
        return vehicles or []

    def getVehiclesToSlot(self, slotIdx):
        if self.unit is not None:
            checkVehicle = self.unit.getRoster().checkVehicle

            def validator(vehCD):
                return checkVehicle(vehCD, slotIdx)[0]

            return filter(validator, self.getVehiclesCDs())
        else:
            return []

    def canAssignToSlot(self, slotIdx):
        if self.unit is not None and not self.isCommander() and slotIdx != CREATOR_SLOT_INDEX:
            slots = self.unit.getFreeSlots()
            if slotIdx in slots:
                vehicles = self.getVehiclesToSlot(slotIdx)
                return (bool(vehicles), vehicles)
        return (False, [])

    def getVehiclesToSlots(self, allSlots=False):
        if self.unit is not None:
            slots = self.unit.getFreeSlots()
            if allSlots:
                slots = set(list(slots) + self.unit.getPlayerSlots().values())
            return self.unit.getRoster().matchVehicleListToSlotList(self.getVehiclesCDs(), slots)
        else:
            return {}

    def getAvailableSlots(self, allSlots=False):
        matches = self.getVehiclesToSlots(allSlots)
        return set(itertools.chain(*matches.values()))

    def getSlotsToVehicles(self, allSlots=False):
        matches = self.getVehiclesToSlots(allSlots)
        slots = set(itertools.chain(*matches.values()))
        result = {}
        for slot in slots:
            result[slot] = list(itertools.ifilter(lambda v, s=slot: s in matches[v], matches.iterkeys()))

        return result

    def getBadge(self):
        return self.badges.getBadge()


class VehicleInfo(object):
    __slots__ = ('vehInvID', 'vehTypeCD', 'vehLevel', 'vehClassIdx')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehInvID=0, vehTypeCompDescr=0, vehLevel=0, vehClassIdx=0, **kwargs):
        super(VehicleInfo, self).__init__()
        self.vehInvID = vehInvID
        self.vehTypeCD = vehTypeCompDescr
        self.vehLevel = vehLevel
        self.vehClassIdx = vehClassIdx

    def __repr__(self):
        return 'VehicleInfo(vehInvID = {0:n}, vehTypeCD = {1:n}, vehLevel = {2:n}, vehClassIdx = {3})'.format(self.vehInvID, self.vehTypeCD, self.vehLevel, self.vehClassIdx)

    def isEmpty(self):
        return not self.vehInvID

    def isReadyToBattle(self, state):
        result = False
        if self.vehInvID:
            vehicle = self.itemsCache.items.getVehicle(self.vehInvID)
            if vehicle:
                result = vehicle.isReadyToPrebattle()
        return result

    def getVehicle(self):
        return self.itemsCache.items.getVehicle(self.vehInvID) if self.vehInvID else None


class SlotState(object):
    __slots__ = ('isClosed', 'isFree')

    def __init__(self, isClosed=False, isFree=True):
        super(SlotState, self).__init__()
        self.isClosed = isClosed
        self.isFree = isFree

    def __repr__(self):
        return 'SlotState(isClosed = {0!r:s}, isFree = {1!r:s})'.format(self.isClosed, self.isFree)


class SlotInfo(object):
    __slots__ = ('index', 'state', 'player', 'vehicle', 'profileVehicle')

    def __init__(self, index, state, player=None, vehicle=None, profile=None):
        super(SlotInfo, self).__init__()
        self.index = index
        self.state = state
        self.player = player
        self.vehicle = vehicle
        self.profileVehicle = profile

    def __repr__(self):
        return 'SlotInfo(index = {0:n}, state = {1!r:s}, player = {2!r:s}, vehicle = {3!r:s}, profileVehicle = {4!r:s})'.format(self.index, self.state, self.player, self.vehicle, self.profileVehicle)


class UnitFlags(object):
    __slots__ = ('__flags', '__flagsDiff', '__isReady')

    def __init__(self, flags, prevFlags=None, isReady=False):
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

    def isExternalLocked(self):
        return self.__flags & UNIT_FLAGS.IS_EXTERNAL_LOCK > 0

    def isLockedStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.LOCKED > 0

    def isSearchStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.IN_SEARCH > 0

    def isFinishAssemblingStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.FINISH_ASSEMBLING > 0

    def isExternalLockedStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.IS_EXTERNAL_LOCK > 0

    def isOpened(self):
        return self.__flags & UNIT_FLAGS.INVITE_ONLY == 0

    def isOpenedStateChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.INVITE_ONLY > 0

    def isOnlyRosterWaitChanged(self):
        return self.__flagsDiff == UNIT_FLAGS.IN_ROSTER_WAIT

    def isInSearch(self):
        return self.__flags & UNIT_FLAGS.IN_SEARCH > 0 or self.__flags & UNIT_FLAGS.PRE_SEARCH > 0

    def isFinishAssembling(self):
        return self.__flags & UNIT_FLAGS.FINISH_ASSEMBLING > 0

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

    def isInArenaChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.IN_ARENA > 0

    def isArenaFinished(self):
        return self.__flags & UNIT_FLAGS.ARENA_FINISHED > 0

    def isArenaFinishedChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.ARENA_FINISHED > 0

    def isFreezed(self):
        return self.isLocked() or self.isInSearch() or self.isInQueue() or self.isInArena()

    def isChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.CHANGED_STATE_ASQ > 0

    def isInExternalLegionariesMatching(self):
        return self.__flags & UNIT_FLAGS.EXTERNAL_LEGIONARIES_MATCHING > 0

    def isExternalLegionariesMatchingChanged(self):
        return self.__flagsDiff & UNIT_FLAGS.EXTERNAL_LEGIONARIES_MATCHING > 0


UnitStats = namedtuple('UnitStats', ('readyCount', 'occupiedSlotsCount', 'openedSlotsCount', 'freeSlotsCount', 'curTotalLevel', 'levelsSeq'))
UnitStats.__new__.__defaults__ = (0,
 0,
 0,
 0,
 0,
 ())
UnitFullData = namedtuple('UnitStats', ('unit', 'flags', 'stats', 'playerInfo', 'slotsIterator'))
UnitFullData.__new__.__defaults__ = (None,
 UnitFlags(0),
 UnitStats(),
 PlayerUnitInfo(-1L, 0, None),
 SlotInfo(-1, SlotState()))

@ReprInjector.simple(('_minLevel', 'minLevel'), ('_maxLevel', 'maxLevel'), ('_maxSlots', 'maxSlots'), ('_maxClosedSlots', 'maxClosedSlots'), ('_maxEmptySlots', 'maxEmptySlots'), ('_minTotalLevel', 'minTotalLevel'), ('_maxTotalLevel', 'maxTotalLevel'), ('_maxLegionariesCount', 'maxLegionariesCount'))
class UnitRosterSettings(object):
    TOTAL_SLOTS = 15
    __slots__ = ('_minLevel', '_maxLevel', '_maxSlots', '_maxClosedSlots', '_maxEmptySlots', '_minTotalLevel', '_maxTotalLevel', '_maxLegionariesCount', '__weakref__')

    def __init__(self, minLevel=MIN_VEHICLE_LEVEL, maxLevel=MAX_VEHICLE_LEVEL, maxSlots=TOTAL_SLOTS, maxClosedSlots=0, maxEmptySlots=0, minTotalLevel=1, maxTotalLevel=150, maxLegionariesCount=0):
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

    def getLevelsRange(self, minLevel=-1, maxLevel=-1):
        return range(self._minLevel, self._maxLevel + 1) if minLevel == -1 and maxLevel == -1 else range(minLevel, maxLevel + 1)

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

    def __eq__(self, other):
        for fn in self.__slots__:
            if not fn.startswith('__') and getattr(self, fn) != getattr(other, fn):
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class DynamicRosterSettings(UnitRosterSettings):

    def __init__(self, unit):
        kwargs = self._extractSettings(unit)
        super(DynamicRosterSettings, self).__init__(**kwargs)

    def _extractSettings(self, unit):
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
        return kwargs


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


_SUPPORTED_ROSTER_SETTINGS = {PREBATTLE_TYPE.UNIT: (ROSTER_TYPE.UNIT_ROSTER,),
 PREBATTLE_TYPE.STRONGHOLD: (ROSTER_TYPE.STRONGHOLD_ROSTER,),
 PREBATTLE_TYPE.E_SPORT_COMMON: (ROSTER_TYPE.UNIT_ROSTER,)}

class SupportedRosterSettings(object):

    @classmethod
    def last(cls, prbType):
        if prbType in _SUPPORTED_ROSTER_SETTINGS:
            return PredefinedRosterSettings(_SUPPORTED_ROSTER_SETTINGS[prbType][-1])
        raise SoftException('Unit type is not supported {0}'.format(prbType))

    @classmethod
    def list(cls, prbType):
        if prbType in _SUPPORTED_ROSTER_SETTINGS:
            seq = _SUPPORTED_ROSTER_SETTINGS[prbType]
            result = []
            for rosterTypeID in seq:
                result.append(PredefinedRosterSettings(rosterTypeID))

            return result
        raise SoftException('Unit type is not supported {0}'.format(prbType))


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
