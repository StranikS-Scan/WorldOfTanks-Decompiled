# Embedded file name: scripts/client/ClientUnit.py
import struct
from collections import namedtuple
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV, LOG_CURRENT_EXCEPTION
import Event
import fortified_regions
from UnitBase import UnitBase, UNIT_OP, UNIT_ROLE, UNIT_STATE, LEADER_SLOT
from gui.shared.utils import makeTupleByDict
PLAYER_ID_CHR = '<q'
VEH_LEN_CHR = '<H'
VEH_LEN_SIZE = struct.calcsize(VEH_LEN_CHR)

class _ClubExtra(namedtuple('_ClubExtra', ('mapID', 'clubDBID', 'clubName', 'clubEmblemIDs', 'divisionID', 'isBaseDefence', 'accDBIDtoRole', 'isRatedBattle', 'isEnemyReady', 'startTime'))):

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


class _FortBattleExtra(namedtuple('_FortBattleExtra', ('clanEquipments', 'lastEquipRev'))):

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

    def __init__(self, slotDefs = {}, slotCount = 0, packedRoster = '', extras = '', packedUnit = ''):
        self.__eManager = Event.EventManager()
        self.onUnitStateChanged = Event.Event(self.__eManager)
        self.onUnitReadyMaskChanged = Event.Event(self.__eManager)
        self.onUnitVehicleChanged = Event.Event(self.__eManager)
        self.onUnitSettingChanged = Event.Event(self.__eManager)
        self.onUnitPlayerRoleChanged = Event.Event(self.__eManager)
        self.onUnitRosterChanged = Event.Event(self.__eManager)
        self.onUnitMembersListChanged = Event.Event(self.__eManager)
        self.onUnitPlayerAdded = Event.Event(self.__eManager)
        self.onUnitPlayerRemoved = Event.Event(self.__eManager)
        self.onUnitPlayersListChanged = Event.Event(self.__eManager)
        self.onUnitPlayerVehDictChanged = Event.Event(self.__eManager)
        self.onUnitPlayerInfoChanged = Event.Event(self.__eManager)
        self.onUnitExtraChanged = Event.Event(self.__eManager)
        self.onUnitUpdated = Event.Event(self.__eManager)
        self._creatorDBID = 0L
        UnitBase.__init__(self, slotDefs, slotCount, packedRoster, extras, packedUnit)

    def destroy(self):
        self.__eManager.clear()
        self._initClean()

    def getState(self):
        return self._state

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

    def getRoster(self):
        return self._roster

    def getPlayerSlots(self):
        return self._playerSlots

    def getLegionarySlots(self):
        result = {}
        for playerID, slotIdx in self._playerSlots.iteritems():
            playerData = self._players[playerID]
            role = playerData.get('role', 0)
            if role & UNIT_ROLE.LEGIONARY:
                result[playerID] = slotIdx

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

    def isPlayerReadyInSlot(self, slotIdx, mask = None):
        if mask is None:
            mask = self._readyMask
        return mask & 1 << slotIdx > 0

    def arePlayersReady(self, ignored = None):
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

    def isRosterSet(self, ignored = None):
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
        elif self._prebattleTypeID in _EXTRA_BY_PRB_TYPE:
            return makeTupleByDict(_EXTRA_BY_PRB_TYPE[self._prebattleTypeID], self._extras)
        else:
            return

    def unpackOps(self, packedOps = ''):
        invokedOps = UnitBase.unpackOps(self, packedOps)
        if {UNIT_OP.REMOVE_PLAYER, UNIT_OP.ADD_PLAYER} & invokedOps:
            self.onUnitPlayersListChanged()
        if {UNIT_OP.DEL_MEMBER, UNIT_OP.SET_MEMBER} & invokedOps:
            self.onUnitMembersListChanged()
        if UNIT_OP.SET_SLOT in invokedOps:
            self.onUnitRosterChanged()
        if {UNIT_OP.EXTRAS_UPDATE, UNIT_OP.EXTRAS_RESET} & invokedOps:
            self.onUnitExtraChanged(self._extras)

    def onUnitExtrasUpdate(self, updateStr):
        UnitBase.onUnitExtrasUpdate(self, updateStr)
        self.onUnitExtraChanged(self._extras)

    def _setUnitState(self, state):
        prevState = self._state
        UnitBase._setUnitState(self, state)
        self.onUnitStateChanged(prevState, self._state)

    def _setReadyMask(self, mask):
        prevMask = self._readyMask
        UnitBase._setReadyMask(self, mask)
        self.onUnitReadyMaskChanged(prevMask, self._readyMask)

    def _setVehicle(self, playerID, vehTypeCompDescr, vehInvID):
        UnitBase._setVehicle(self, playerID, vehTypeCompDescr, vehInvID)
        self.onUnitVehicleChanged(playerID, vehInvID, vehTypeCompDescr)

    def _clearVehicle(self, playerID):
        UnitBase._clearVehicle(self, playerID)
        self.onUnitVehicleChanged(playerID, 0, 0)

    def _unpackPlayer(self, packedOps):
        playerID, hasPlayer = 0, False
        try:
            playerID, = struct.unpack_from(PLAYER_ID_CHR, packedOps)
            filtered = dict(filter(lambda item: item[1].get('role', 0) & UNIT_ROLE.INVITED == 0, self._players.iteritems()))
            hasPlayer = playerID in filtered
        except struct.error as e:
            LOG_ERROR(e)

        nextOps = UnitBase._unpackPlayer(self, packedOps)
        if not hasPlayer and playerID:
            self.onUnitPlayerAdded(playerID, self.getPlayer(playerID))
        if hasPlayer:
            LOG_DEBUG_DEV('onUnitPlayerInfoChanged', playerID, self.getPlayer(playerID))
            self.onUnitPlayerInfoChanged(playerID, self.getPlayer(playerID))
        return nextOps

    def _addPlayer(self, playerID, **kwargs):
        if 'role' in kwargs and kwargs['role'] & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR and self._playerSlots.get(playerID) == LEADER_SLOT:
            self._creatorDBID = playerID
        UnitBase._addPlayer(self, playerID, **kwargs)

    def _removePlayer(self, playerID):
        pInfo = self.getPlayer(playerID)
        if pInfo:
            self.onUnitPlayerRemoved(playerID, pInfo)
        UnitBase._removePlayer(self, playerID)

    def _changePlayerRole(self, playerID, roleFlags):
        prevRoleFlags = UNIT_ROLE.DEFAULT
        if playerID in self._players:
            prevRoleFlags = self._players[playerID]['role']
        UnitBase._changePlayerRole(self, playerID, roleFlags)
        if roleFlags & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR and self._playerSlots.get(playerID) == LEADER_SLOT:
            self._creatorDBID = playerID
        self.onUnitPlayerRoleChanged(playerID, prevRoleFlags, roleFlags)

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
            playerID, = struct.unpack_from(PLAYER_ID_CHR, packedOps, offset=VEH_LEN_SIZE)
            self.onUnitPlayerVehDictChanged(playerID)
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
