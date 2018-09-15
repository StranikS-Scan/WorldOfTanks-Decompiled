# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/AccountUnitAPI.py
import constants
from constants import PREBATTLE_TYPE
from UnitBase import UNIT_SLOT, CLIENT_UNIT_CMD, INV_ID_CLEAR_VEHICLE
from unit_roster_config import UnitRosterSlot
from debug_utils import *

class UNIT_API:
    NONE = 0
    CLIENT = 1
    WGSH = 2


def getUnitApiID(serverRequestID):
    return serverRequestID >> 32


def getOriginalRequestID(serverRequestID):
    return serverRequestID & 4294967295L


class AccountUnitAPI:

    def create(self, requestID, prebattleType, eventQueueType):
        assert 0

    def join(self, requestID, unitMgrID, slotIdx):
        assert 0

    def doCmd(self, requestID, unitMgrID, cmdID, param32, param64, paramString):
        assert 0

    def setRosterSlots(self, requestID, unitMgrID, rosterSlotKeys, rosterSlotValues):
        assert 0

    def sendInvites(self, requestID, accountsToInvite, comment):
        assert 0

    def createEx(self, requestID, prebattleType, param32, param64, paramStr, paramPython):
        assert 0

    def joinEx(self, requestID, unitMgrID, *args):
        assert 0


class UnitClientAPI(object):

    def _callAPI(self, methodName, *args):
        assert 0

    def getUnitMgrID(self):
        pass

    def _callUnitAPI(self, methodName, *args):
        unitMgrID = self.getUnitMgrID()
        return self._callAPI(methodName, unitMgrID, *args)

    def _doCreate(self, prebattleType, int32Arg=0):
        return self._callAPI('create', prebattleType, int32Arg)

    def _doUnitCmd(self, cmd, uint64Arg=0, int32Arg=0, strArg=''):
        self._callUnitAPI('doCmd', cmd, uint64Arg, int32Arg, strArg)

    def create(self):
        return self._doCreate(PREBATTLE_TYPE.UNIT)

    def createSquad(self):
        return self._doCreate(PREBATTLE_TYPE.SQUAD)

    def createFalloutSquad(self, queueType):
        return self._doCreate(PREBATTLE_TYPE.FALLOUT, queueType)

    def createEventSquad(self, queueType):
        return self._doCreate(PREBATTLE_TYPE.EVENT, queueType)

    def join(self, unitMgrID, slotIdx=UNIT_SLOT.ANY):
        self._callAPI('join', unitMgrID, slotIdx)

    def invite(self, accountsToInvite, comment):
        return self._callUnitAPI('sendInvites', accountsToInvite, comment)

    def setAllRosterSlots(self, *args):
        return self._callUnitAPI('setRosterSlots', *args)

    def leave(self):
        return self._doUnitCmd(CLIENT_UNIT_CMD.LEAVE_UNIT)

    def setVehicle(self, vehInvID=INV_ID_CLEAR_VEHICLE, setReady=False):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_VEHICLE, vehInvID, int(setReady))

    def setVehicleType(self, vehTypeCompDescr=INV_ID_CLEAR_VEHICLE, vehLevel=0):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_VEHICLE_TYPE, vehTypeCompDescr, vehLevel)

    def setMember(self, vehInvID, slotIdx=UNIT_SLOT.ANY):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_MEMBER, vehInvID, slotIdx)

    def fit(self, playerID, slotIdx=UNIT_SLOT.ANY):
        return self._doUnitCmd(CLIENT_UNIT_CMD.FIT_UNIT_MEMBER, playerID, slotIdx)

    def unfit(self, playerID):
        return self._doUnitCmd(CLIENT_UNIT_CMD.FIT_UNIT_MEMBER, playerID, UNIT_SLOT.REMOVE)

    def assign(self, playerID, slotIdx):
        return self._doUnitCmd(CLIENT_UNIT_CMD.ASSIGN_UNIT_MEMBER, playerID, slotIdx)

    def unassign(self, playerID):
        return self._doUnitCmd(CLIENT_UNIT_CMD.ASSIGN_UNIT_MEMBER, playerID, UNIT_SLOT.REMOVE)

    def reassign(self, playerID, slotIdx):
        return self._doUnitCmd(CLIENT_UNIT_CMD.REASSIGN_UNIT_MEMBER, playerID, slotIdx)

    def kick(self, playerID):
        return self._doUnitCmd(CLIENT_UNIT_CMD.KICK_UNIT_PLAYER, playerID)

    def setReady(self, isReady=True, resetVehicle=False):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_MEMBER_READY, int(isReady), int(resetVehicle))

    def setRosterSlot(self, rosterSlotIdx, vehTypeID=None, nationNames=[], levels=(1, 8), vehClassNames=[]):
        LOG_DEBUG('setRosterSlot: slot=%s, vehTypeID=%s, nationNames=%s, levels=%s, vehClassNames=%s' % (rosterSlotIdx,
         vehTypeID,
         repr(nationNames),
         repr(levels),
         repr(vehClassNames)))
        rSlot = UnitRosterSlot(vehTypeID, nationNames, levels, vehClassNames)
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_ROSTER_SLOT, 0, rosterSlotIdx, rSlot.pack())

    def lockUnit(self, isLocked=True):
        return self._doUnitCmd(CLIENT_UNIT_CMD.LOCK_UNIT, int(isLocked))

    def closeSlot(self, slotIdx, isClosed=True):
        return self._doUnitCmd(CLIENT_UNIT_CMD.CLOSE_UNIT_SLOT, int(isClosed), slotIdx)

    def openUnit(self, isOpen=True):
        return self._doUnitCmd(CLIENT_UNIT_CMD.OPEN_UNIT, int(isOpen))

    def setDevMode(self, isDevMode=True):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_DEV_MODE, int(isDevMode)) if constants.IS_DEVELOPMENT else None

    def startBattle(self, vehInvID=0, gameplaysMask=None, arenaTypeID=0):
        if gameplaysMask is not None:
            self.setGameplaysMask(gameplaysMask)
        if arenaTypeID != 0:
            self.setArenaType(arenaTypeID)
        return self._doUnitCmd(CLIENT_UNIT_CMD.START_UNIT_BATTLE, vehInvID)

    def stopBattle(self):
        return self._doUnitCmd(CLIENT_UNIT_CMD.STOP_UNIT_BATTLE)

    def startAutoSearch(self):
        return self._doUnitCmd(CLIENT_UNIT_CMD.START_AUTO_SEARCH)

    def stopAutoSearch(self):
        return self._doUnitCmd(CLIENT_UNIT_CMD.STOP_AUTO_SEARCH)

    def setComment(self, strComment):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_COMMENT, 0, 0, strComment)

    def giveLeadership(self, memberDBID):
        return self._doUnitCmd(CLIENT_UNIT_CMD.GIVE_LEADERSHIP, memberDBID)

    def setGameplaysMask(self, gameplaysMask):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_GAMEPLAYS_MASK, gameplaysMask)

    def setArenaType(self, arenaTypeID):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_ARENA_TYPE, arenaTypeID)

    def setVehicleList(self, vehicleList):
        return self._doUnitCmd(CLIENT_UNIT_CMD.SET_VEHICLE_LIST, 0, 0, ','.join(map(str, vehicleList)))

    def changeFalloutType(self, newQueueType):
        return self._doUnitCmd(CLIENT_UNIT_CMD.CHANGE_FALLOUT_TYPE, newQueueType)

    def changeEventType(self, newQueueType):
        return self._doUnitCmd(CLIENT_UNIT_CMD.CHANGE_EVENT_TYPE, newQueueType)
