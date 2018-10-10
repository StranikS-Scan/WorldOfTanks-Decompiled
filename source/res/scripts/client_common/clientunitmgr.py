# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/ClientUnitMgr.py
import cPickle
from ClientUnit import ClientUnit
import Event
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from UnitBase import UNIT_SLOT, UNIT_BROWSER_CMD, UNIT_BROWSER_TYPE, UNIT_ERROR, CMD_NAMES
from unit_roster_config import UnitRosterSlot
import AccountCommands
from AccountUnitAPI import UnitClientAPI

class ClientUnitMgr(UnitClientAPI):

    def __init__(self, account):
        self.__eManager = Event.EventManager()
        self.onUnitJoined = Event.Event(self.__eManager)
        self.onUnitLeft = Event.Event(self.__eManager)
        self.onUnitRestored = Event.Event(self.__eManager)
        self.onUnitErrorReceived = Event.Event(self.__eManager)
        self.onUnitNotifyReceived = Event.Event(self.__eManager)
        self.onUnitResponseReceived = Event.Event(self.__eManager)
        self.id = 0
        self.battleID = None
        self.__account = account
        self.__requestID = 0
        self.__unit = None
        return

    @property
    def unit(self):
        return self.__unit

    def clear(self):
        self.battleID = None
        self.__account = None
        self.__eManager.clear()
        self._clearUnit()
        return

    def __getNextRequestID(self):
        self.__requestID += 1
        return self.__requestID

    def onUnitUpdate(self, unitMgrID, packedUnit, packedOps):
        LOG_DEBUG('onUnitUpdate: unitMgrID=%s, packedUnit=%r, packedOps=%r' % (unitMgrID, packedUnit, packedOps))
        if self.id != unitMgrID:
            prevMgrID = self.id
            self.id = unitMgrID
            self.battleID = None
            self._clearUnit()
            if not self.id and prevMgrID:
                self.onUnitLeft(prevMgrID)
        if packedUnit:
            unit = ClientUnit(packedUnit=packedUnit)
            self._clearUnit()
            self.__unit = unit
            if 'battleID' in unit._extras:
                self.battleID = unit._extras['battleID']
            self.onUnitJoined(self.id, unit.getPrebattleType())
        if packedOps:
            unit = self.__unit
            if unit is not None:
                unit.lock()
                unit.unpackOps(packedOps)
                unit.unlock()
                unit.onUnitUpdated()
        return

    def onUnitError(self, requestID, unitMgrID, errorCode, errorString):
        LOG_DEBUG('onUnitError: unitMgr=%s, errorCode=%s, errorString=%r' % (unitMgrID, errorCode, errorString))
        if errorCode == UNIT_ERROR.UNIT_RESTORED:
            self._restore()
        self.onUnitErrorReceived(requestID, unitMgrID, errorCode, errorString)

    def onUnitNotify(self, unitMgrID, notifyCode, notifyString='', argsList=None):
        argsList = argsList or []
        LOG_DEBUG('onUnitNotify: unitMgr=%s, errorCode=%s, notifyString=%r argsList=%r' % (unitMgrID,
         notifyCode,
         notifyString,
         argsList))
        self.onUnitNotifyReceived(unitMgrID, notifyCode, notifyString, argsList)

    def onUnitCallOk(self, requestID):
        LOG_DEBUG('onUnitCallOk: requestID=%s OK' % requestID)
        self.onUnitResponseReceived(requestID)

    def join(self, unitMgrID, slotIdx=UNIT_SLOT.REMOVE):
        return self._callAPI('join', unitMgrID, slotIdx)

    def invite(self, accountsToInvite, comment):
        return self._callAPI('sendInvites', self.id, accountsToInvite, comment)

    def setAllRosterSlots(self, rosterDefsDict):
        LOG_DEBUG('setAllRosterSlots: rosterDefsDict=%r' % rosterDefsDict)
        rosterSlots = {}
        for rosterSlotIdx, rosterDict in rosterDefsDict.iteritems():
            vehTypeID = rosterDict.get('vehTypeID', None)
            nationNames = rosterDict.get('nationNames', [])
            levels = rosterDict.get('levels', None)
            vehClassNames = rosterDict.get('vehClassNames', [])
            rSlot = UnitRosterSlot(vehTypeID, nationNames, levels, vehClassNames)
            rosterSlots[rosterSlotIdx] = rSlot.pack()

        LOG_DEBUG('unit.setAllRosterSlots: rosterSlots=%r' % rosterSlots, self.id)
        return self._callAPI('setRosterSlots', self.id, rosterSlots.keys(), rosterSlots.values())

    def _callAPI(self, methodName, *args):
        requestID = self.__getNextRequestID()
        LOG_DEBUG('ClientUnitMgr', methodName, requestID, *args)
        attrName = 'accountUnitClient_' + methodName
        method = getattr(self.__account.base, attrName)
        method(requestID, *args)
        return requestID

    def _doUnitCmd(self, cmd, uint64Arg=0, int32Arg=0, strArg='', unitMgrID=0):
        unitMgrID = unitMgrID or self.id
        LOG_DEBUG('ClientUnitMgr._doUnitCmd', CMD_NAMES.get(cmd, '?'), unitMgrID)
        return self._callAPI('doCmd', unitMgrID, cmd, uint64Arg, int32Arg, strArg)

    def doCustomUnitCmd(self, cmd, unitMgrID=0, uint64Arg=0, int32Arg=0, strArg=''):
        return self._doUnitCmd(cmd, uint64Arg, int32Arg, strArg, unitMgrID)

    def _clearUnit(self):
        if self.__unit is not None:
            self.__unit.destroy()
            self.__unit = None
        return

    def _restore(self):
        prevMgrID = self.id
        if prevMgrID:
            self.onUnitRestored(prevMgrID)
        self.id = 0
        self.battleID = None
        self._clearUnit()
        if prevMgrID:
            self.onUnitLeft(prevMgrID)
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

    def clear(self):
        self.__account = None
        self.__eManager.clear()
        self.results.clear()
        return

    def subscribe(self, unitTypeFlags=UNIT_BROWSER_TYPE.NOT_RATED_UNITS, showOtherLocations=False):
        self.results = {}
        LOG_DEBUG('unitBrowser.subscribeUnitBrowser', unitTypeFlags, showOtherLocations)
        self.__account.base.accountUnitBrowser_subscribe(unitTypeFlags, showOtherLocations)

    def unsubscribe(self):
        self.results = {}
        self.__account.base.accountUnitBrowser_unsubscribe()
        LOG_DEBUG('unitBrowser.unsubscribeUnitBrowser')

    def recenter(self, targetRating, unitTypeFlags=UNIT_BROWSER_TYPE.NOT_RATED_UNITS, showOtherLocations=False):
        self.results = {}
        LOG_DEBUG('unitBrowser.recenterUnitBrowser', targetRating, unitTypeFlags, showOtherLocations)
        self.__account.base.accountUnitBrowser_recenter(targetRating, unitTypeFlags, showOtherLocations)

    def left(self):
        LOG_DEBUG('unitBrowser.doUnitBrowserCmd', UNIT_BROWSER_CMD.LEFT)
        self.__account.base.accountUnitBrowser_doCmd(UNIT_BROWSER_CMD.LEFT)

    def right(self):
        LOG_DEBUG('unitBrowser.doUnitBrowserCmd', UNIT_BROWSER_CMD.RIGHT)
        self.__account.base.accountUnitBrowser_doCmd(UNIT_BROWSER_CMD.RIGHT)

    def refresh(self):
        self.results = {}
        LOG_DEBUG('unitBrowser.doUnitBrowserCmd', UNIT_BROWSER_CMD.REFRESH)
        self.__account.base.accountUnitBrowser_doCmd(UNIT_BROWSER_CMD.REFRESH)

    def onError(self, errorCode, errorString):
        LOG_DEBUG('unitBrowser.onError: errorCode=%s, errorString=%r' % (errorCode, errorString))
        self.onErrorReceived(errorCode, errorString)

    def onResultsSet(self, pickledBrowserResultsList):
        browserResultsList = cPickle.loads(pickledBrowserResultsList)
        LOG_DEBUG('unitBrowser.onResultsSet: %s' % browserResultsList)
        self.results.clear()
        for row in browserResultsList:
            try:
                cfdUnitID, unitMgrID, cmdrRating, peripheryID, strUnitPack = row
                unit = ClientUnit(packedUnit=strUnitPack)
                self.results[cfdUnitID] = dict(unitMgrID=unitMgrID, cmdrRating=cmdrRating, peripheryID=peripheryID, unit=unit)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        LOG_DEBUG('unitBrowser results=%r' % self.results)
        self.onResultsReceived(self.results)

    def onResultsUpdate(self, pickledBrowserUpdatesDict):
        browserUpdatesDict = cPickle.loads(pickledBrowserUpdatesDict)
        LOG_DEBUG('unitBrowser.onResultsUpdate: %s' % browserUpdatesDict)
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
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.onResultsUpdated(res)
        return

    def startSearch(self, vehTypes=None, useOtherLocations=False):
        self.__account.enqueueUnitAssembler(vehTypes or [])

    def _search(self, vehInvIDs=None):
        from helpers import dependency
        from skeletons.gui.shared import IItemsCache
        itemsCache = dependency.instance(IItemsCache)
        vehInvIDs = vehInvIDs or []
        for vehInvID in vehInvIDs:
            vehicle = itemsCache.items.getVehicle(vehInvID)
            LOG_DEBUG('vehicle[%s]=%r' % (vehInvID, vehicle))

    def stopSearch(self):
        self.__account.dequeueUnitAssembler()

    def onSearchSuccess(self, unitMgrID, acceptDeadlineUTC):
        LOG_DEBUG('onSearchSuccess: unitMgrID=%s, acceptDeadlineUTC=%s' % (unitMgrID, acceptDeadlineUTC))
        self._acceptUnitMgrID = unitMgrID
        self._acceptDeadlineUTC = acceptDeadlineUTC
        self.onSearchSuccessReceived(unitMgrID, acceptDeadlineUTC)

    def acceptSearch(self, unitMgrID=0):
        if not unitMgrID:
            unitMgrID = self._acceptUnitMgrID
        LOG_DEBUG('unitBrowser.acceptSearch', unitMgrID)
        self.__account.base.accountUnitAssembler_acceptAutoSearch(0, unitMgrID)

    def declineSearch(self, unitMgrID=0):
        if not unitMgrID:
            unitMgrID = self._acceptUnitMgrID
        LOG_DEBUG('unitBrowser.declineSearch', unitMgrID)
        self.__account.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_UNIT_ASSEMBLER, unitMgrID, 0, 0)
