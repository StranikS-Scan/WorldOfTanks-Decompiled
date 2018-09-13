# Embedded file name: scripts/client/gui/prb_control/functional/unit_ext.py
import time
import BigWorld
from PlayerEvents import g_playerEvents
from UnitBase import UNIT_ERROR, UNIT_SLOT, INV_ID_CLEAR_VEHICLE
from account_helpers import getPlayerDatabaseID
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING
from gui import prb_control, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.prb_control import getClientUnitMgr, getClientUnitBrowser
from gui.prb_control import events_dispatcher
from gui.prb_control.context import unit_ctx
from gui.prb_control.formatters import messages
from gui.prb_control.functional import interfaces
from gui.prb_control.items.unit_seqs import UnitsListIterator
from gui.prb_control.items.unit_seqs import UnitsUpdateIterator
from gui.prb_control.prb_cooldown import PrbCooldownManager
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import REQ_CRITERIA, g_itemsCache
from helpers import time_utils

class UnitRequestProcessor(object):
    __slots__ = ('__requests', '__functional')

    def __init__(self, functional):
        super(UnitRequestProcessor, self).__init__()
        self.__requests = {}
        self.__functional = functional

    def init(self):
        unitMgr = getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived += self.unitMgr_onUnitResponseReceived
            unitMgr.onUnitErrorReceived += self.unitMgr_onUnitErrorReceived
        else:
            LOG_ERROR('Unit manager is not defined')

    def fini(self):
        unitMgr = getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitResponseReceived -= self.unitMgr_onUnitResponseReceived
            unitMgr.onUnitErrorReceived -= self.unitMgr_onUnitErrorReceived
        self.__requests.clear()
        self.__functional = None
        return

    def doRequest(self, ctx, methodName, *args, **kwargs):
        if self._sendRequest(ctx, methodName, [], *args, **kwargs):
            ctx.startProcessing()

    def doRequestChain(self, ctx, chain):
        if self._sendNextRequest(ctx, chain):
            ctx.startProcessing()

    def doRawRequest(self, methodName, *args, **kwargs):
        unitMgr = prb_control.getClientUnitMgr()
        method = getattr(unitMgr, methodName)
        if callable(method):
            method(*args, **kwargs)
        else:
            LOG_ERROR('Name of method is invalid', methodName)

    def unitMgr_onUnitResponseReceived(self, requestID):
        self._onResponseReceived(requestID, True)

    def unitMgr_onUnitErrorReceived(self, requestID, unitMgrID, unitIdx, errorCode, _):
        self._onResponseReceived(requestID, False)
        if errorCode != UNIT_ERROR.OK and self.__functional.getID() == unitMgrID and self.__functional.getUnitIdx() == unitIdx:
            for listener in self.__functional.getListenersIterator():
                listener.onUnitErrorReceived(errorCode)

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
        unitMgr = prb_control.getClientUnitMgr()
        result = False
        method = getattr(unitMgr, methodName)
        if callable(method):
            requestID = method(*args, **kwargs)
            if requestID > 0:
                self.__requests[requestID] = (ctx, chain)
                result = True
            else:
                LOG_ERROR('Request ID can not be null')
        else:
            LOG_ERROR('Name of method is invalid', methodName)
        return result

    def _sendNextRequest(self, ctx, chain):
        methodName, args, kwargs = chain[0]
        return self._sendRequest(ctx, methodName, chain[1:], *args, **kwargs)

    def _onResponseReceived(self, requestID, result):
        if requestID > 0:
            ctx, chain = self.__requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and len(chain):
                    self._sendNextRequest(ctx, chain)
                    return
                ctx.stopProcessing(result)
        else:
            while len(self.__requests):
                _, data = self.__requests.popitem()
                data[0].stopProcessing(False)

        return


def _getUnitFromBrowser(unitIdx):
    unitBrowser = getClientUnitBrowser()
    if unitBrowser:
        results = unitBrowser.results
    else:
        results = {}
    if unitIdx in results:
        unit = results[unitIdx]['unit']
    else:
        unit = None
    return (unitIdx, unit)


def _getUnitFromSortieCache(unitIdx):
    from gui.shared.ClanCache import g_clanCache
    provider = g_clanCache.fortProvider
    unit = None
    if not provider:
        return unit
    else:
        fortCtrl = provider.getController()
        if fortCtrl:
            cache = fortCtrl.getSortiesCache()
            if cache:
                unit = cache.getUnitByIndex(unitIdx)
        return (unitIdx, unit)


_UNIT_GETTER_BY_PRB_TYPE = {PREBATTLE_TYPE.UNIT: _getUnitFromBrowser,
 PREBATTLE_TYPE.SORTIE: _getUnitFromSortieCache}

def getUnitFromStorage(prbType, unitIdx):
    if prbType in _UNIT_GETTER_BY_PRB_TYPE:
        unitIdx, unit = _UNIT_GETTER_BY_PRB_TYPE[prbType](unitIdx)
    else:
        LOG_WARNING('Unit is not found by prebattle type', prbType)
        unit = None
    return (unitIdx, unit)


class UnitAutoSearchHandler(object):

    def __init__(self, functional):
        super(UnitAutoSearchHandler, self).__init__()
        self.__functional = functional
        self.__vTypeDescrs = []
        self.__isInSearch = False
        self.__hasResult = False
        self.__startSearchTime = -1
        self.__lastErrorCode = UNIT_ERROR.OK

    def init(self):
        browser = getClientUnitBrowser()
        if browser:
            browser.onSearchSuccessReceived += self.unitBrowser_onSearchSuccessReceived
            browser.onErrorReceived += self.unitBrowser_onErrorReceived
        else:
            LOG_ERROR('Unit browser is not defined')
        g_playerEvents.onDequeuedUnitAssembler += self.pe_onDequeuedUnitAssembler
        g_playerEvents.onKickedFromUnitAssembler += self.pe_onKickedFromUnitAssembler
        g_playerEvents.onEnqueuedUnitAssembler += self.pe_onEnqueuedUnitAssembler

    def fini(self):
        browser = getClientUnitBrowser()
        if browser:
            browser.onSearchSuccessReceived -= self.unitBrowser_onSearchSuccessReceived
            browser.onErrorReceived -= self.unitBrowser_onErrorReceived
        g_playerEvents.onDequeuedUnitAssembler -= self.pe_onDequeuedUnitAssembler
        g_playerEvents.onKickedFromUnitAssembler -= self.pe_onKickedFromUnitAssembler
        g_playerEvents.onEnqueuedUnitAssembler -= self.pe_onEnqueuedUnitAssembler
        if self.__isInSearch:
            self.stop()
        self.__functional = None
        return

    def initEvents(self, listener):
        if self.__hasResult:
            browser = getClientUnitBrowser()
            if browser:
                acceptDelta = self.getAcceptDelta(browser._acceptDeadlineUTC)
                if acceptDelta > 0:
                    LOG_DEBUG('onUnitAutoSearchSuccess', acceptDelta)
                    listener.onUnitAutoSearchSuccess(acceptDelta)
        elif self.__isInSearch:
            events_dispatcher.setUnitProgressInCarousel(self.__functional.getPrbType(), True)
            listener.onUnitAutoSearchStarted(self.getTimeLeftInSearch())

    def isInSearch(self):
        return self.__isInSearch

    def getTimeLeftInSearch(self):
        if self.__startSearchTime > -1:
            timeLeft = int(BigWorld.time() - self.__startSearchTime)
        else:
            timeLeft = -1
        return timeLeft

    def getAcceptDelta(self, acceptDeadlineUTC):
        if acceptDeadlineUTC:
            return max(0, int(time_utils.makeLocalServerTime(acceptDeadlineUTC) - time.time()))
        return 0

    def start(self, vTypeDescrs = None):
        if self.__isInSearch:
            LOG_ERROR('Auto search already started.')
            return False
        else:
            browser = getClientUnitBrowser()
            if browser:
                if vTypeDescrs is not None:
                    self.__vTypeDescrs = vTypeDescrs
                self.__lastErrorCode = UNIT_ERROR.OK
                browser.startSearch(vehTypes=self.__vTypeDescrs)
                return True
            LOG_ERROR('Unit browser is not defined')
            return False
            return

    def stop(self):
        if not self.__isInSearch:
            LOG_DEBUG('Auto search did not start. Exits form search forced.')
            self.__exitFromQueue()
            return True
        browser = getClientUnitBrowser()
        if browser:
            self.__lastErrorCode = UNIT_ERROR.OK
            browser.stopSearch()
        else:
            LOG_ERROR('Unit browser is not defined')
            return False

    def accept(self):
        if not self.__hasResult:
            LOG_ERROR('First, sends request for search.')
            return False
        else:
            browser = getClientUnitBrowser()
            if browser:
                self.__lastErrorCode = UNIT_ERROR.OK
                browser.acceptSearch()
                return True
            LOG_ERROR('Unit browser is not defined')
            return False

    def decline(self):
        if not self.__hasResult:
            LOG_ERROR('First, sends request for search.')
            return False
        else:
            browser = getClientUnitBrowser()
            if browser:
                self.__lastErrorCode = UNIT_ERROR.OK
                browser.declineSearch()
                return True
            LOG_ERROR('Unit browser is not defined')
            return False

    def pe_onDequeuedUnitAssembler(self):
        self.__exitFromQueue()

    def pe_onKickedFromUnitAssembler(self):
        self.__exitFromQueue()
        SystemMessages.pushMessage(messages.getUnitKickedReasonMessage('KICKED_FROM_UNIT_ASSEMBLER'), type=SystemMessages.SM_TYPE.Warning)

    def pe_onEnqueuedUnitAssembler(self):
        self.__isInSearch = True
        self.__startSearchTime = BigWorld.time()
        events_dispatcher.setUnitProgressInCarousel(self.__functional.getPrbType(), True)
        for listener in self.__functional.getListenersIterator():
            listener.onUnitAutoSearchStarted(0)
        else:
            events_dispatcher.showUnitWindow(self.__functional.getPrbType())

    def unitBrowser_onSearchSuccessReceived(self, unitMgrID, unitIdx, acceptDeadlineUTC):
        self.__hasResult = True
        acceptDelta = self.getAcceptDelta(acceptDeadlineUTC)
        LOG_DEBUG('onUnitAutoSearchSuccess', acceptDelta, acceptDeadlineUTC)
        events_dispatcher.setUnitProgressInCarousel(self.__functional.getPrbType(), False)
        for listener in self.__functional.getListenersIterator():
            listener.onUnitAutoSearchSuccess(acceptDelta)
        else:
            events_dispatcher.showUnitWindow(self.__functional.getPrbType())

    def unitBrowser_onErrorReceived(self, errorCode, _):
        self.__isInSearch = False
        self.__lastErrorCode = errorCode
        if errorCode != UNIT_ERROR.OK:
            for listener in self.__functional.getListenersIterator():
                listener.onUnitBrowserErrorReceived(errorCode)

    def __exitFromQueue(self):
        self.__isInSearch = False
        self.__lastErrorCode = UNIT_ERROR.OK
        self.__hasResult = False
        self.__startSearchTime = 0
        prbType = self.__functional.getPrbType()
        events_dispatcher.setUnitProgressInCarousel(prbType, False)
        for listener in self.__functional.getListenersIterator():
            listener.onUnitAutoSearchFinished()
        else:
            events_dispatcher.showUnitWindow(prbType)


class InventoryVehiclesWatcher(object):

    def __init__(self, functional):
        super(InventoryVehiclesWatcher, self).__init__()
        self.__functional = functional

    def init(self):
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehiclesUpdated})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)

    def autoSetVehicle(self):
        pInfo = self.__functional.getPlayerInfo()
        if pInfo.isInSlot:
            vehicles = pInfo.getAvaibleVehiclesToSlot(pInfo.slotIdx)
            if len(vehicles) == 1:
                self.__functional.request(unit_ctx.SetVehicleUnitCtx(vTypeCD=vehicles[0], waitingID='prebattle/change_settings'))

    def validate(self, update = False):
        items = g_itemsCache.items
        invVehicles = items.getVehicles(REQ_CRITERIA.INVENTORY)
        vehCDs = invVehicles.keys()
        pInfo = self.__functional.getPlayerInfo()
        if pInfo.isInSlot:
            _, unit = self.__functional.getUnit()
            roster = unit.getRoster()
            if not roster.checkVehicleList(vehCDs, pInfo.slotIdx) and not pInfo.isCreator():
                self.__functional.request(unit_ctx.AssignUnitCtx(pInfo.dbID, UNIT_SLOT.REMOVE, 'prebattle/assign'))
            else:
                vInfo = self.__functional.getVehicleInfo()
                if vInfo.vehTypeCD and vInfo.vehTypeCD not in vehCDs:
                    self.__functional.request(unit_ctx.SetVehicleUnitCtx(vehInvID=INV_ID_CLEAR_VEHICLE, waitingID='prebattle/change_settings'))
                elif update:
                    self.__functional.unit_onUnitPlayerVehDictChanged(getPlayerDatabaseID())
        elif update:
            self.__functional.unit_onUnitPlayerVehDictChanged(getPlayerDatabaseID())

    def __onVehiclesUpdated(self, *args):
        self.validate(update=True)


class UnitsListRequester(interfaces.IPrbListRequester):

    def __init__(self):
        self.__selectedID = None
        self.__callback = None
        self.__callbackUpdate = None
        self.__isSubscribed = False
        self.__cooldown = PrbCooldownManager()
        self.__handlers = {}
        self.__cache = {}
        return

    def __del__(self):
        LOG_DEBUG('Units list requester deleted:', self)

    def subscribe(self, vehTypes):
        if self.__isSubscribed:
            return
        self.__isSubscribed = True
        browser = getClientUnitBrowser()
        if browser:
            self.__cooldown.process(REQUEST_TYPE.UNITS_LIST)
            self.__handlers = {REQUEST_TYPE.UNITS_RECENTER: self.__recenter,
             REQUEST_TYPE.UNITS_REFRESH: self.__refresh,
             REQUEST_TYPE.UNITS_NAV_LEFT: self.__navLeft,
             REQUEST_TYPE.UNITS_NAV_RIGHT: self.__navRight}
            browser.subscribe(vehTypes=vehTypes)
            browser.onResultsReceived += self.__unitBrowser_onUnitsListReceived
            browser.onResultsUpdated += self.__unitBrowser_onUnitsListUpdated
        else:
            LOG_ERROR('Unit browser is not defined')

    def unsubscribe(self):
        self.__handlers.clear()
        browser = getClientUnitBrowser()
        if browser:
            if self.__isSubscribed:
                browser.unsubscribe()
            browser.onResultsReceived -= self.__unitBrowser_onUnitsListReceived
            browser.onResultsUpdated -= self.__unitBrowser_onUnitsListUpdated
        self.__isSubscribed = False
        self.__selectedID = None
        self.__pageNum = 0
        return

    def setSelectedID(self, selectedID):
        self.__selectedID = selectedID

    def start(self, callback):
        self.__cache.clear()
        if callback is not None and callable(callback):
            self.__callback = callback
        else:
            LOG_ERROR('Callback is None or is not callable')
            return
        if self.__cooldown.isInProcess(REQUEST_TYPE.UNITS_LIST):
            self.__cooldown.fireEvent(REQUEST_TYPE.UNITS_LIST)
        browser = getClientUnitBrowser()
        if browser:
            self.__unitBrowser_onUnitsListReceived(browser.results)
        return

    def stop(self):
        self.__cache.clear()
        self.__callback = None
        self.__callbackUpdate = None
        return

    def request(self, **kwargs):
        if self.__cooldown.validate(REQUEST_TYPE.UNITS_LIST):
            return
        LOG_DEBUG('Request list of units', kwargs)
        self.__cooldown.process(REQUEST_TYPE.UNITS_LIST)
        self.__cache.clear()
        browser = getClientUnitBrowser()
        if browser:
            if 'req' in kwargs:
                req = kwargs['req']
                if req in self.__handlers:
                    if self.__handlers[req](browser, **kwargs):
                        Waiting.show('prebattle/auto_search')
                else:
                    LOG_ERROR('Request is not supported', kwargs)
            else:
                LOG_ERROR('Request is not found', self.__handlers.keys(), kwargs)
        else:
            LOG_ERROR('Unit browser is not defined')

    def addCacheItem(self, item):
        self.__cache[item.cfdUnitID] = item

    def getCacheItem(self, cfdUnitID):
        try:
            item = self.__cache[cfdUnitID]
        except KeyError:
            LOG_ERROR('Item not found in cache', cfdUnitID)
            item = None

        return item

    def removeCacheItem(self, cfdUnitID):
        self.__cache.pop(cfdUnitID, None)
        return

    def __navLeft(self, browser, **kwargs):
        browser.left()
        return True

    def __navRight(self, browser, **kwargs):
        browser.right()
        return True

    def __recenter(self, browser, **kwargs):
        result = False
        if 'vehTypes' in kwargs:
            browser.recenter(g_itemsCache.items.stats.getGlobalRating(), vehTypes=kwargs['vehTypes'])
            result = True
        else:
            LOG_ERROR('Types of vehicles are not defined', kwargs)
        return result

    def __refresh(self, browser, **kwargs):
        browser.refresh()
        return True

    def __unitBrowser_onUnitsListReceived(self, data):
        Waiting.hide('prebattle/auto_search')
        if self.__callback:
            self.__callback(self.__selectedID, True, self.__cooldown.isInProcess(REQUEST_TYPE.UNITS_LIST), UnitsListIterator(self, data))

    def __unitBrowser_onUnitsListUpdated(self, data):
        if self.__callback:
            self.__callback(self.__selectedID, False, False, UnitsUpdateIterator(self, data))


_g_listReq = None

def initListReq(vehTypes):
    global _g_listReq
    if _g_listReq is None:
        _g_listReq = UnitsListRequester()
        _g_listReq.subscribe(vehTypes)
    return _g_listReq


def destroyListReq():
    global _g_listReq
    if _g_listReq:
        _g_listReq.unsubscribe()
        _g_listReq.stop()
        _g_listReq = None
    return


def getListReq():
    return _g_listReq
