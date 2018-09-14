# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/ClientUnit.py
import struct
from collections import namedtuple
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV, LOG_CURRENT_EXCEPTION
import Event
import fortified_regions
from UnitBase import UnitBase, UNIT_OP, UNIT_ROLE, UNIT_FLAGS, LEADER_SLOT
from shared_utils import makeTupleByDict
PLAYER_ID_CHR = '<q'
VEH_LEN_CHR = '<H'
VEH_LEN_SIZE = struct.calcsize(VEH_LEN_CHR)

class _ClubExtra(namedtuple('_ClubExtra', ('mapID', 'clubDBID', 'clubName', 'clubEmblemIDs', 'divisionID', 'isBaseDefence', 'accDBIDtoRole', 'accDBIDtoClubTimestamp', 'isRatedBattle', 'isEnemyReady', 'startTime'))):

    def getClubDbID(self):
        return self.clubDBID

    def getEmblem64x64(self):
        try:
            return self.clubEmblemIDs[2]
        except:
            pass

        return None


class _SortieExtra(namedtuple('_SortieExtra', ('clanEquipments', 'lastEquipRev'))):

    def getConsumables(self):
        result = {}
        if self.clanEquipments:
            for eqIntCD, slotIdx in self.clanEquipments[1]:
                result[slotIdx] = fortified_regions.g_cache.equipmentToOrder[eqIntCD]

        return result


class _FortBattleExtra(namedtuple('_FortBattleExtra', ('clanEquipments', 'lastEquipRev', 'canUseEquipments'))):

    def getConsumables(self):
        result = {}
        if self.clanEquipments:
            for eqIntCD, slotIdx in self.clanEquipments[1]:
                result[slotIdx] = fortified_regions.g_cache.equipmentToOrder[eqIntCD]

        return result


_EXTRA_BY_PRB_TYPE = {PREBATTLE_TYPE.CLUBS: _ClubExtra,
 PREBATTLE_TYPE.SORTIE: _SortieExtra,
 PREBATTLE_TYPE.FORT_BATTLE: _FortBattleExtra}

class ClientUnit(UnitBase):

    def __init__(self, limitsDefs={}, slotDefs={}, slotCount=0, packedRoster='', extrasInit=None, packedUnit=''):
        self.__eManager = Event.SuspendedEventManager()
        self.onUnitFlagsChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitReadyMaskChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitVehicleChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitVehiclesChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitSettingChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitPlayerRoleChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitRosterChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitMembersListChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitPlayerAdded = Event.SuspendedEvent(self.__eManager)
        self.onUnitPlayerRemoved = Event.SuspendedEvent(self.__eManager)
        self.onUnitPlayersListChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitPlayerVehDictChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitPlayerInfoChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitExtraChanged = Event.SuspendedEvent(self.__eManager)
        self.onUnitUpdated = Event.SuspendedEvent(self.__eManager)
        self._creatorDBID = 0
        UnitBase.__init__(self, limitsDefs, slotDefs, slotCount, packedRoster, extrasInit, packedUnit)

    def destroy(self):
        self.__eManager.clear()
        self._initClean()

    def lock(self):
        self.__eManager.suspend()

    def unlock(self):
        self.__eManager.resume()

    def getFlags(self):
        return self._flags

    def getReadyMask(self):
        return self._readyMask

    def getPlayers(self):
        return self._players

    def getPlayer(self, dbID):
        data = None
        if dbID in self._players:
            data = self._players[dbID]
        return data

    def getCreatorDBID(self):
        return self._creatorDBID

    def getCreator(self):
        return self.getPlayer(self._creatorDBID)

    def getMembers(self):
        return self._members

    def getVehicles(self):
        return self._vehicles

    def getSelectedVehicleLevels(self):
        lst = list(set([ vehInfo.vehLevel for vehicles in self._vehicles.itervalues() for vehInfo in vehicles ]))
        lst.sort()
        return lst

    def getRoster(self):
        return self._roster

    def getPlayerSlots(self):
        return self._playerSlots

    def getMemberVehicles(self, dbID):
        return self.getVehicles().get(dbID, [])

    def getLegionarySlots(self):
        result = {}
        for accountDBID, slotIdx in self._playerSlots.iteritems():
            playerData = self._players[accountDBID]
            role = playerData.get('role', 0)
            if role & UNIT_ROLE.LEGIONARY:
                result[accountDBID] = slotIdx

        return result

    def getPlayerSlotIdx(self, dbID):
        slotIdx = -1
        if dbID in self._playerSlots:
            slotIdx = self._playerSlots[dbID]
        return slotIdx

    def getFreeSlots(self):
        return self._freeSlots

    def getComment(self):
        return self._strComment

    def getPrebattleType(self):
        return self._prebattleTypeID

    def getModalTimestamp(self):
        return self._modalTimestamp

    def isPlayerReadyInSlot(self, slotIdx, mask=None):
        if mask is None:
            mask = self._readyMask
        return mask & 1 << slotIdx > 0

    def arePlayersReady(self, ignored=None):
        readyMask = self._readyMask
        if ignored is not None:
            for slotIdx in ignored:
                bit = 1 << slotIdx
                if self._fullReadyMask & bit > 0:
                    readyMask |= bit

        return readyMask == self._fullReadyMask and readyMask

    def isSlotFree(self, slotIdx):
        return slotIdx in self._freeSlots

    def isSlotClosed(self, slotIdx):
        return self._closedSlotMask & 1 << slotIdx > 0

    def isOccupied(self, slotIdx):
        return slotIdx in self._members

    def isSlotDisabled(self, slotIdx):
        return not (self.isSlotClosed(slotIdx) or self.isSlotFree(slotIdx) or self.isOccupied(slotIdx))

    def isRosterSet(self, ignored=None):
        result = False
        if ignored is None:
            ignored = []
        for rosterSlotIdx, slot in self._roster.slots.iteritems():
            slotIndex = int(rosterSlotIdx / 2)
            if rosterSlotIdx in ignored or self.isSlotClosed(slotIndex):
                continue
            if not self._roster.isDefaultSlot(slot):
                result = True
                break

        return result

    def isSortie(self):
        return self._prebattleTypeID == PREBATTLE_TYPE.SORTIE

    def isSquad(self):
        return self._prebattleTypeID == PREBATTLE_TYPE.SQUAD

    def isEvent(self):
        return self._prebattleTypeID == PREBATTLE_TYPE.EVENT

    def isFalloutSquad(self):
        return self._prebattleTypeID == PREBATTLE_TYPE.FALLOUT

    def isPrebattlesSquad(self):
        return self._prebattleTypeID in PREBATTLE_TYPE.SQUAD_PREBATTLES

    def isFortBattle(self):
        return self._prebattleTypeID == PREBATTLE_TYPE.FORT_BATTLE

    def isClub(self):
        return self._prebattleTypeID == PREBATTLE_TYPE.CLUBS

    def isRated(self):
        return self.isClub() and self.getExtra().isRatedBattle

    def getRosterTypeID(self):
        return self._rosterTypeID

    def getExtra(self):
        if self._extras is None:
            return
        else:
            return makeTupleByDict(_EXTRA_BY_PRB_TYPE[self._prebattleTypeID], self._extras) if self._prebattleTypeID in _EXTRA_BY_PRB_TYPE else None

    def unpackOps(self, packedOps=''):
        invokedOps = UnitBase.unpackOps(self, packedOps)
        if {UNIT_OP.REMOVE_PLAYER, UNIT_OP.ADD_PLAYER} & invokedOps:
            self.onUnitPlayersListChanged()
        if {UNIT_OP.DEL_MEMBER, UNIT_OP.SET_MEMBER} & invokedOps:
            self.onUnitMembersListChanged()
        if UNIT_OP.SET_SLOT in invokedOps:
            self.onUnitRosterChanged()
        if {UNIT_OP.EXTRAS_UPDATE, UNIT_OP.EXTRAS_RESET} & invokedOps:
            self.onUnitExtraChanged(self._extras)

    def updateUnitExtras(self, updateStr):
        UnitBase.updateUnitExtras(self, updateStr)
        self.onUnitExtraChanged(self._extras)

    def _setUnitFlags(self, flags):
        prevFlags = self._flags
        UnitBase._setUnitFlags(self, flags)
        self.onUnitFlagsChanged(prevFlags, self._flags)

    def _setReadyMask(self, mask):
        prevMask = self._readyMask
        UnitBase._setReadyMask(self, mask)
        self.onUnitReadyMaskChanged(prevMask, self._readyMask)

    def _setVehicle(self, accountDBID, vehTypeCompDescr, vehInvID):
        UnitBase._setVehicle(self, accountDBID, vehTypeCompDescr, vehInvID)
        self.onUnitVehicleChanged(accountDBID, vehInvID, vehTypeCompDescr)

    def _setVehicleList(self, accountDBID, vehDataList):
        UnitBase._setVehicleList(self, accountDBID, vehDataList)
        self.onUnitVehiclesChanged(accountDBID, vehDataList)

    def _clearVehicle(self, accountDBID):
        UnitBase._clearVehicle(self, accountDBID)
        self.onUnitVehicleChanged(accountDBID, 0, 0)

    def _unpackPlayer(self, packedOps):
        accountDBID, hasPlayer = 0, False
        try:
            accountDBID = struct.unpack_from(PLAYER_ID_CHR, packedOps)
            filtered = dict(filter(lambda item: item[1].get('role', 0) & UNIT_ROLE.INVITED == 0, self._players.iteritems()))
            hasPlayer = accountDBID in filtered
        except struct.error as e:
            LOG_ERROR(e)

        nextOps = UnitBase._unpackPlayer(self, packedOps)
        if not hasPlayer and accountDBID:
            self.onUnitPlayerAdded(accountDBID, self.getPlayer(accountDBID))
        if hasPlayer:
            LOG_DEBUG_DEV('onUnitPlayerInfoChanged', accountDBID, self.getPlayer(accountDBID))
            self.onUnitPlayerInfoChanged(accountDBID, self.getPlayer(accountDBID))
        return nextOps

    def _addPlayer(self, accountDBID, **kwargs):
        if 'role' in kwargs and kwargs['role'] & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR and self._playerSlots.get(accountDBID) == LEADER_SLOT:
            self._creatorDBID = accountDBID
        UnitBase._addPlayer(self, accountDBID, **kwargs)

    def _removePlayer(self, accountDBID):
        pInfo = self.getPlayer(accountDBID)
        if pInfo:
            self.onUnitPlayerRemoved(accountDBID, pInfo)
        UnitBase._removePlayer(self, accountDBID)

    def _changePlayerRole(self, accountDBID, roleFlags):
        prevRoleFlags = UNIT_ROLE.DEFAULT
        if accountDBID in self._players:
            prevRoleFlags = self._players[accountDBID]['role']
        UnitBase._changePlayerRole(self, accountDBID, roleFlags)
        if roleFlags & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR and self._playerSlots.get(accountDBID) == LEADER_SLOT:
            self._creatorDBID = accountDBID
        self.onUnitPlayerRoleChanged(accountDBID, prevRoleFlags, roleFlags)

    def setComment(self, strComment):
        UnitBase.setComment(self, strComment)
        self.onUnitSettingChanged(UNIT_OP.SET_COMMENT, self._strComment)

    def _closeSlot(self, slotIdx):
        UnitBase._closeSlot(self, slotIdx)
        self.onUnitSettingChanged(UNIT_OP.CLOSE_SLOT, slotIdx)

    def _openSlot(self, slotIdx):
        UnitBase._openSlot(self, slotIdx)
        self.onUnitSettingChanged(UNIT_OP.OPEN_SLOT, slotIdx)

    def _unpackVehicleDict(self, packedOps):
        nextOps = UnitBase._unpackVehicleDict(self, packedOps)
        try:
            accountDBID = struct.unpack_from(PLAYER_ID_CHR, packedOps, offset=VEH_LEN_SIZE)
            self.onUnitPlayerVehDictChanged(accountDBID)
        except struct.error as e:
            LOG_ERROR(e)

        return nextOps

    def _giveLeadership(self, memberDBID):
        prevRoleFlags = self._players[memberDBID]['role']
        UnitBase._giveLeadership(self, memberDBID)
        newRoleFlags = self._players[memberDBID]['role']
        self._creatorDBID = memberDBID
        self.onUnitMembersListChanged()
        self.onUnitPlayerRoleChanged(memberDBID, prevRoleFlags, newRoleFlags)

    def _changeSortieDivision(self, division):
        UnitBase._changeSortieDivision(self, division)
        self.onUnitRosterChanged()
        self.onUnitMembersListChanged()
        self.onUnitSettingChanged(UNIT_OP.CHANGE_DIVISION, division)

    def _changeFalloutQueueType(self, queueType):
        UnitBase._changeFalloutQueueType(self, queueType)
        self.onUnitRosterChanged()
        self.onUnitMembersListChanged()
        self.onUnitSettingChanged(UNIT_OP.CHANGE_FALLOUT_TYPE, queueType)
