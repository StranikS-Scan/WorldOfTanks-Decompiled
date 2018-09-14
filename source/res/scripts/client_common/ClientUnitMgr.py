# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/ClientUnitMgr.py
import cPickle
from ClientUnit import ClientUnit
import Event
import constants
from debug_utils import LOG_DEBUG, LOG_DAN, LOG_CURRENT_EXCEPTION
from UnitBase import UNIT_SLOT, UNIT_BROWSER_CMD, CLIENT_UNIT_CMD, INV_ID_CLEAR_VEHICLE, UNIT_BROWSER_TYPE, UNIT_ERROR
from unit_roster_config import UnitRosterSlot
import AccountCommands

class ClientUnitMgr(object):

    def __init__(self, account):
        self.__eManager = Event.EventManager()
        self.onUnitJoined = Event.Event(self.__eManager)
        self.onUnitLeft = Event.Event(self.__eManager)
        self.onUnitRestored = Event.Event(self.__eManager)
        self.onUnitErrorReceived = Event.Event(self.__eManager)
        self.onUnitResponseReceived = Event.Event(self.__eManager)
        self.id = 0
        self.unitIdx = 0
        self.battleID = None
        self.__account = account
        self.__requestID = 0
        self.units = {}
        return

    def destroy(self):
        self.battleID = None
        self.__account = None
        self.__eManager.clear()
        self._clearUnits()
        self.unitIdx = 0
        return

    def __getNextRequestID(self):
        self.__requestID += 1
        return self.__requestID

    def onUnitUpdate(self, unitMgrID, packedUnit, packedOps):
        LOG_DAN('onUnitUpdate: unitMgrID=%s, packedUnit=%r, packedOps=%r' % (unitMgrID, packedUnit, packedOps))
        if not unitMgrID:
            unitIdx = 0
        else:
            unitIdx = 1
        if self.id != unitMgrID:
            prevMgrID = self.id
            prevUnitIdx = self.unitIdx
            self.id = unitMgrID
            self.unitIdx = unitIdx
            self._clearUnits()
            if not self.id and prevMgrID:
                self.onUnitLeft(prevMgrID, prevUnitIdx)
        if packedUnit:
            unit = ClientUnit(packedUnit=packedUnit)
            if unitIdx in self.units:
                self.units[unitIdx].destroy()
            self.units[unitIdx] = unit
            if 'battleID' in unit._extras:
                self.battleID = unit._extras['battleID']
            self.onUnitJoined(self.id, self.unitIdx)
        if packedOps:
            unit = self.units.get(unitIdx)
            if unit:
                unit.unpackOps(packedOps)
                unit.onUnitUpdated()

    def onUnitError(self, requestID, unitMgrID, errorCode, errorString):
        LOG_DEBUG('onUnitError: unitMgr=%s, errorCode=%s, errorString=%r' % (unitMgrID, errorCode, errorString))
        unitIdx = 1
        if errorCode == UNIT_ERROR.UNIT_RESTORED:
            self._restore()
        self.onUnitErrorReceived(requestID, unitMgrID, unitIdx, errorCode, errorString)

    def onUnitCallOk(self, requestID):
        LOG_DEBUG('onUnitCallOk: requestID=%s OK' % requestID)
        self.onUnitResponseReceived(requestID)

    def create(self, unitMgrFlags = 0):
        requestID = self.__getNextRequestID()
        LOG_DAN('unit.createUnitMgr', requestID, unitMgrFlags)
        self.__account.base.createUnitMgr(requestID, unitMgrFlags)
        return requestID

    def createSquad(self):
        requestID = self.__getNextRequestID()
        LOG_DAN('unit.createSquadUnitMgr', requestID)
        self.__account.base.createSquadUnitMgr(requestID)
        return requestID

    def createEventSquad(self, eventType):
        requestID = self.__getNextRequestID()
        LOG_DAN('unit.createEventSquadUnitMgr', requestID)
        self.__account.base.createEventSquadUnitMgr(requestID, eventType)
        return requestID

    def join(self, unitMgrID, unitIdx = 1, vehInvID = 0, slotIdx = UNIT_SLOT.REMOVE):
        requestID = self.__getNextRequestID()
        LOG_DAN('unit.joinUnit', requestID, unitMgrID, unitIdx, slotIdx)
        self.__account.base.joinUnit(requestID, unitMgrID, slotIdx)
        return requestID

    def __doUnitCmd(self, cmd, unitMgrID = 0, uint64Arg = 0, int32Arg = 0, strArg = ''):
        requestID = self.__getNextRequestID()
        if not unitMgrID:
            unitMgrID = self.id
        LOG_DAN('unit.__doUnitCmd', cmd, requestID, unitMgrID, uint64Arg, int32Arg, strArg)
        self.__account.base.doUnitCmd(cmd, requestID, unitMgrID, uint64Arg, int32Arg, strArg)
        return requestID

    def doCustomUnitCmd(self, cmd, unitMgrID = 0, uint64Arg = 0, int32Arg = 0, strArg = ''):
        return self.__doUnitCmd(cmd, unitMgrID, uint64Arg, int32Arg, strArg)

    def leave(self):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.LEAVE_UNIT)

    def setVehicle(self, vehInvID = INV_ID_CLEAR_VEHICLE, setReady = False):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_VEHICLE, 0, vehInvID, int(setReady))

    def setMember(self, vehInvID, slotIdx = UNIT_SLOT.ANY):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_MEMBER, 0, vehInvID, slotIdx)

    def fit(self, playerID, slotIdx = UNIT_SLOT.ANY, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.FIT_UNIT_MEMBER, self.id, playerID, slotIdx)

    def unfit(self, playerID, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.FIT_UNIT_MEMBER, self.id, playerID, UNIT_SLOT.REMOVE)

    def assign(self, playerID, slotIdx, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.ASSIGN_UNIT_MEMBER, self.id, playerID, slotIdx)

    def unassign(self, playerID, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.ASSIGN_UNIT_MEMBER, self.id, playerID, UNIT_SLOT.REMOVE)

    def reassign(self, playerID, slotIdx, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.REASSIGN_UNIT_MEMBER, self.id, playerID, slotIdx)

    def kick(self, playerID, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.KICK_UNIT_PLAYER, self.id, playerID)

    def setReady(self, isReady = True, resetVehicle = False):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_MEMBER_READY, self.id, int(isReady), int(resetVehicle))

    def setRosterSlot(self, rosterSlotIdx, vehTypeID = None, nationNames = [], levels = (1, 8), vehClassNames = [], unitIdx = 0):
        LOG_DAN('setRosterSlot: slot=%s, vehTypeID=%s, nationNames=%s, levels=%s, vehClassNames=%s' % (rosterSlotIdx,
         vehTypeID,
         repr(nationNames),
         repr(levels),
         repr(vehClassNames)))
        rSlot = UnitRosterSlot(vehTypeID, nationNames, levels, vehClassNames)
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_ROSTER_SLOT, self.id, 0, rosterSlotIdx, rSlot.pack())

    def setAllRosterSlots(self, rosterDefsDict, unitIdx = 0):
        LOG_DAN('setAllRosterSlots: rosterDefsDict=%r' % rosterDefsDict)
        rosterSlots = {}
        for rosterSlotIdx, rosterDict in rosterDefsDict.iteritems():
            vehTypeID = rosterDict.get('vehTypeID', None)
            nationNames = rosterDict.get('nationNames', [])
            levels = rosterDict.get('levels', None)
            vehClassNames = rosterDict.get('vehClassNames', [])
            rSlot = UnitRosterSlot(vehTypeID, nationNames, levels, vehClassNames)
            rosterSlots[rosterSlotIdx] = rSlot.pack()

        requestID = self.__getNextRequestID()
        LOG_DAN('unit.setAllRosterSlots: rosterSlots=%r' % rosterSlots, requestID, self.id)
        self.__account.base.setAllRosterSlots(requestID, self.id, rosterSlots.keys(), rosterSlots.values())
        return requestID

    def lockUnit(self, isLocked = True, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.LOCK_UNIT, self.id, int(isLocked))

    def closeSlot(self, slotIdx, isClosed = True, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.CLOSE_UNIT_SLOT, self.id, int(isClosed), slotIdx)

    def openUnit(self, isOpen = True, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.OPEN_UNIT, self.id, int(isOpen))

    def setDevMode(self, isDevMode = True, unitIdx = 0):
        if constants.IS_DEVELOPMENT:
            return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_DEV_MODE, self.id, int(isDevMode))

    def setRatedBattle(self, isRatedBattle = True, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_RATED_BATTLE, self.id, int(isRatedBattle))

    def invite(self, accountsToInvite, comment):
        requestID = self.__getNextRequestID()
        LOG_DAN('unit.sendUnitInvites', requestID, accountsToInvite, comment)
        self.__account.base.sendUnitInvites(requestID, accountsToInvite, comment)
        return requestID

    def startBattle(self, unitIdx = 0, vehInvID = 0, gameplaysMask = None):
        if gameplaysMask is not None:
            self.setGameplaysMask(gameplaysMask)
        return self.__doUnitCmd(CLIENT_UNIT_CMD.START_UNIT_BATTLE, self.id, vehInvID)

    def stopBattle(self, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.STOP_UNIT_BATTLE, self.id)

    def startAutoSearch(self, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.START_AUTO_SEARCH, self.id)

    def stopAutoSearch(self, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.STOP_AUTO_SEARCH, self.id)

    def setComment(self, strComment, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_UNIT_COMMENT, self.id, 0, 0, strComment)

    def setGameplaysMask(self, gameplaysMask, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_GAMEPLAYS_MASK, self.id, gameplaysMask)

    def giveLeadership(self, memberDBID, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.GIVE_LEADERSHIP, self.id, memberDBID)

    def changeSortieDivision(self, division, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.CHANGE_SORTIE_DIVISION, self.id, division)

    def setEventSquadVehicleList(self, vehicleList, unitIdx = 0):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_EVENT_SQUAD_VEHICLE_LIST, self.id, 0, 0, ','.join(map(str, vehicleList)))

    def changeEventSquadType(self, newEventType):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.CHANGE_EVENT_SQUAD_TYPE, self.id, newEventType)

    def setEventSquadReady(self, isReady = True):
        return self.__doUnitCmd(CLIENT_UNIT_CMD.SET_EVENT_SQUAD_MEMBER_READY, self.id, int(isReady))

    def _clearUnits(self):
        while len(self.units):
            _, unit = self.units.popitem()
            unit.destroy()

    def _restore(self):
        prevMgrID = self.id
        prevUnitIdx = self.unitIdx
        if prevMgrID:
            self.onUnitRestored(prevMgrID, prevUnitIdx)
        self.id = 0
        self.unitIdx = 0
        self.battleID = None
        self._clearUnits()
        if prevMgrID:
            self.onUnitLeft(prevMgrID, prevUnitIdx)
        return


class ClientUnitBrowser(object):

    def __init__(self, account):
        self.__account = account
        self.__eManager = Event.EventManager()
        self.onResultsReceived = Event.Event(self.__eManager)
        self.onResultsUpdated = Event.Event(self.__eManager)
        self.onSearchSuccessReceived = Event.Event(self.__eManager)
        self.onErrorReceived = Event.Event(self.__eManager)
        self.results = {}
        self._acceptUnitMgrID = 0
        self._acceptDeadlineUTC = 0

    def destroy(self):
        self.__account = None
        self.__eManager.clear()
        self.results.clear()
        return

    def subscribe(self, unitTypeFlags = UNIT_BROWSER_TYPE.NOT_RATED_UNITS, showOtherLocations = False):
        self.results = {}
        LOG_DAN('unitBrowser.subscribeUnitBrowser', unitTypeFlags, showOtherLocations)
        self.__account.base.subscribeUnitBrowser(unitTypeFlags, showOtherLocations)

    def unsubscribe(self):
        self.results = {}
        self.__account.base.unsubscribeUnitBrowser()
        LOG_DAN('unitBrowser.unsubscribeUnitBrowser')

    def recenter(self, targetRating, unitTypeFlags = UNIT_BROWSER_TYPE.NOT_RATED_UNITS, showOtherLocations = False):
        self.results = {}
        LOG_DAN('unitBrowser.recenterUnitBrowser', targetRating, unitTypeFlags, showOtherLocations)
        self.__account.base.recenterUnitBrowser(targetRating, unitTypeFlags, showOtherLocations)

    def left(self):
        LOG_DAN('unitBrowser.doUnitBrowserCmd', UNIT_BROWSER_CMD.LEFT)
        self.__account.base.doUnitBrowserCmd(UNIT_BROWSER_CMD.LEFT)

    def right(self):
        LOG_DAN('unitBrowser.doUnitBrowserCmd', UNIT_BROWSER_CMD.RIGHT)
        self.__account.base.doUnitBrowserCmd(UNIT_BROWSER_CMD.RIGHT)

    def refresh(self):
        self.results = {}
        LOG_DAN('unitBrowser.doUnitBrowserCmd', UNIT_BROWSER_CMD.REFRESH)
        self.__account.base.doUnitBrowserCmd(UNIT_BROWSER_CMD.REFRESH)

    def onError(self, errorCode, errorString):
        LOG_DAN('unitBrowser.onError: errorCode=%s, errorString=%r' % (errorCode, errorString))
        self.onErrorReceived(errorCode, errorString)

    def onResultsSet(self, pickledBrowserResultsList):
        browserResultsList = cPickle.loads(pickledBrowserResultsList)
        LOG_DAN('unitBrowser.onResultsSet: %s' % browserResultsList)
        self.results.clear()
        for row in browserResultsList:
            try:
                cfdUnitID, unitMgrID, cmdrRating, peripheryID, strUnitPack = row
                unit = ClientUnit(packedUnit=strUnitPack)
                self.results[cfdUnitID] = dict(unitMgrID=unitMgrID, cmdrRating=cmdrRating, peripheryID=peripheryID, unit=unit)
            except:
                LOG_CURRENT_EXCEPTION()

        LOG_DAN('unitBrowser results=%r' % self.results)
        self.onResultsReceived(self.results)

    def onResultsUpdate(self, pickledBrowserUpdatesDict):
        browserUpdatesDict = cPickle.loads(pickledBrowserUpdatesDict)
        LOG_DAN('unitBrowser.onResultsUpdate: %s' % browserUpdatesDict)
        res = {}
        for cfdUnitID, (cmdrRating, strUnitPack) in browserUpdatesDict.iteritems():
            try:
                if strUnitPack is None:
                    self.results.pop(cfdUnitID, None)
                    res[cfdUnitID] = None
                else:
                    unit = ClientUnit(packedUnit=strUnitPack)
                    if cfdUnitID in self.results:
                        self.results[cfdUnitID]['unit'] = unit
                        self.results[cfdUnitID]['cmdrRating'] = cmdrRating
                        res[cfdUnitID] = self.results[cfdUnitID]
            except:
                LOG_CURRENT_EXCEPTION()

        self.onResultsUpdated(res)
        return

    def startSearch(self, vehTypes = [], useOtherLocations = False):
        self.__account.enqueueUnitAssembler(vehTypes)

    def _search(self, vehInvIDs = []):
        from gui.shared import g_itemsCache
        for vehInvID in vehInvIDs:
            vehicle = g_itemsCache.items.getVehicle(vehInvID)
            LOG_DAN('vehicle[%s]=%r' % (vehInvID, vehicle))

    def stopSearch(self):
        self.__account.dequeueUnitAssembler()

    def onSearchSuccess(self, unitMgrID, acceptDeadlineUTC):
        LOG_DAN('onSearchSuccess: unitMgrID=%s, acceptDeadlineUTC=%s' % (unitMgrID, acceptDeadlineUTC))
        self._acceptUnitMgrID = unitMgrID
        self._acceptDeadlineUTC = acceptDeadlineUTC
        self.onSearchSuccessReceived(unitMgrID, acceptDeadlineUTC)

    def acceptSearch(self, unitMgrID = 0):
        if not unitMgrID:
            unitMgrID = self._acceptUnitMgrID
        LOG_DAN('unitBrowser.acceptUnitAutoSearch', unitMgrID)
        self.__account.base.acceptUnitAutoSearch(unitMgrID)

    def declineSearch(self, unitMgrID = 0):
        if not unitMgrID:
            unitMgrID = self._acceptUnitMgrID
        LOG_DAN('unitBrowser.declineSearch', unitMgrID)
        self.__account.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_UNIT_ASSEMBLER, unitMgrID, 0, 0)
