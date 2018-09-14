# Embedded file name: scripts/client/gui/shared/fortifications/fort_ext.py
import BigWorld
import Event
from FortifiedRegionBase import FORT_ERROR, FORT_AUTO_UNSUBSCRIBE_TIMEOUT
from account_helpers import getAccountDatabaseID
from constants import REQUEST_COOLDOWN
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SYSTEM_MESSAGES
from gui.shared.fortifications import getClientFortMgr, getClientFort
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE_NAMES, CLIENT_FORT_STATE
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
from gui.shared.utils.requesters import RequestCtx, RequestsByIDProcessor
from helpers import i18n

class SimpleFortRequester(RequestsByIDProcessor):

    def __init__(self, success = None):
        super(SimpleFortRequester, self).__init__()
        if success is None:
            self._success = (FORT_ERROR.OK,)
        else:
            self._success = success
        return

    def init(self):
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortResponseReceived += self._fortMgr_onFortResponseReceived
            fortMgr.onFortUpdateReceived += self._fortMgr_onFortUpdateReceived
        else:
            LOG_DEBUG('Fort manager is not defined')

    def fini(self):
        fortMgr = getClientFortMgr()
        if fortMgr:
            fortMgr.onFortResponseReceived -= self._fortMgr_onFortResponseReceived
            fortMgr.onFortUpdateReceived -= self._fortMgr_onFortUpdateReceived
        super(SimpleFortRequester, self).fini()

    def getSender(self):
        return getClientFortMgr()

    def _fortMgr_onFortResponseReceived(self, requestID, resultCode, _):
        self._onResponseReceived(requestID, resultCode in self._success)

    def _fortMgr_onFortUpdateReceived(self, isFullUpdate):
        if isFullUpdate:
            self.stopProcessing()


class PlayerFortRequester(SimpleFortRequester):

    def __init__(self, success = None):
        super(PlayerFortRequester, self).__init__(success)
        self._databaseID = getAccountDatabaseID()
        self._individualRqIDs = set()

    def init(self):
        super(PlayerFortRequester, self).init()
        fort = getClientFort()
        if fort:
            fort.onResponseReceived += self._fort_onResponseReceived
        else:
            LOG_DEBUG('Fort is not defined')

    def fini(self):
        fort = getClientFort()
        if fort:
            fort.onResponseReceived -= self._fort_onResponseReceived
        super(PlayerFortRequester, self).fini()

    def stopProcessing(self):
        self._individualRqIDs.clear()
        super(PlayerFortRequester, self).stopProcessing()

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
        result, requestID = super(PlayerFortRequester, self)._sendRequest(ctx, methodName, chain, *args, **kwargs)
        if result and ctx.isUpdateExpected():
            self._individualRqIDs.add(requestID)
        return (result, requestID)

    def _fortMgr_onFortResponseReceived(self, requestID, resultCode, _):
        result = resultCode in self._success
        if not result or requestID not in self._individualRqIDs:
            self._onResponseReceived(requestID, result)

    def _fort_onResponseReceived(self, requestID, callerDBID):
        if callerDBID == self._databaseID:
            self._onResponseReceived(requestID, True)


class FortSubscriptionKeeper(object):

    def __init__(self):
        super(FortSubscriptionKeeper, self).__init__()
        self.__isStarted = False
        self.__callbackID = None
        self.__requester = None
        self.__ctx = None
        self.__isAutoUnsubscribed = True
        self.__isEnabled = False
        self.onAutoUnsubscribed = Event.Event()
        return

    def isEnabled(self):
        return self.__isEnabled

    def isAutoUnsubscribed(self):
        return self.__isAutoUnsubscribed

    def start(self, stateID):
        if self.__isStarted:
            return
        self.__isStarted = True
        self.__requester = SimpleFortRequester((FORT_ERROR.OK, FORT_ERROR.NOT_CREATED))
        self.__requester.init()
        self.__ctx = RequestCtx()
        self.__isAutoUnsubscribed = False
        self.__isEnabled = stateID in CLIENT_FORT_STATE.KEEP_ALIVE
        self.__setTimeout()

    def stop(self):
        self.__isStarted = False
        self.__isAutoUnsubscribed = True
        self.__isEnabled = False
        if self.__ctx:
            self.__ctx.clear()
            self.__ctx = None
        if self.__requester:
            self.__requester.fini()
            self.__requester = None
        self.__clearTimeout()
        self.onAutoUnsubscribed.clear()
        return

    def update(self, stateID):
        isEnabled = stateID in CLIENT_FORT_STATE.KEEP_ALIVE
        if self.__isEnabled is isEnabled:
            return
        self.__isEnabled = isEnabled
        if self.__isEnabled and not self.__ctx.isProcessing():
            self.__setTimeout()

    def __setTimeout(self):
        if self.__callbackID is None:
            self.__callbackID = BigWorld.callback(FORT_AUTO_UNSUBSCRIBE_TIMEOUT, self.__timeout)
        return

    def __clearTimeout(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __timeout(self):
        self.__callbackID = None
        if self.__isEnabled:
            self.__sendRequest()
        else:
            LOG_DEBUG('Client is unsubscribed automatically')
            self.onAutoUnsubscribed()
            self.__isAutoUnsubscribed = True
        return

    def __sendRequest(self):
        self.__requester.doRequestEx(self.__ctx, self.__callback, 'keepalive')

    def __callback(self, result):
        if result:
            self.__setTimeout()


class FortCooldownManager(RequestCooldownManager):

    def __init__(self):
        super(FortCooldownManager, self).__init__(REQUEST_SCOPE.FORTIFICATION)

    def lookupName(self, rqTypeID):
        requestName = rqTypeID
        if rqTypeID in FORT_REQUEST_TYPE_NAMES:
            requestName = I18N_SYSTEM_MESSAGES.fortification_request_name(FORT_REQUEST_TYPE_NAMES[rqTypeID])
            requestName = i18n.makeString(requestName)
        else:
            LOG_WARNING('Request type is not found', rqTypeID)
        return requestName

    def getDefaultCoolDown(self):
        return REQUEST_COOLDOWN.CALL_FORT_METHOD
