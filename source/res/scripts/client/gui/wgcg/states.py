# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/states.py
from collections import namedtuple
import BigWorld
from adisp import process, async
from client_request_lib.exceptions import ResponseCodes
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui.clans.restrictions import AccountClanLimits, DefaultAccountClanLimits
from gui.clans.settings import LOGIN_STATE
from gui.shared.utils import getPlayerDatabaseID, backoff
from gui.shared.utils.decorators import ReprInjector
from gui.wgcg.base.contexts import LogInCtx, LogOutCtx, PingCtx
from gui.wgcg.factory import g_webFactory
from gui.wgcg.requests import WgcgRequestResponse
from gui.wgcg.settings import WebRequestDataType
from helpers import dependency
from helpers import getClientLanguage
from helpers import time_utils
from shared_utils import CONST_CONTAINER
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
_PING_BACK_OFF_MIN_DELAY = 60
_PING_BACK_OFF_MAX_DELAY = 1200
_PING_BACK_OFF_MODIFIER = 30
_PING_BACK_OFF_EXP_RANDOM_FACTOR = 5

class WebControllerStates(CONST_CONTAINER):
    STATE_NOT_DEFINED = 0
    STATE_AVAILABLE = 1
    STATE_UNAVAILABLE = 2
    STATE_ROAMING = 3
    STATE_DISABLED = 4


AccessTokenData = namedtuple('AccessTokenData', ('accessToken', 'expiresAt'))
_RELOGIN_CODES = (401,)

@ReprInjector.simple(('getStateID', 'state'))
class _State(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, webCtrl, stateID):
        self.__stateID = stateID
        self._webCtrl = webCtrl

    def init(self):
        pass

    def fini(self):
        self._webCtrl = None
        return

    def invalidate(self):
        pass

    def getStateID(self):
        return self.__stateID

    def getLimits(self, profile):
        return DefaultAccountClanLimits()

    def isAvailable(self):
        return False

    def isLoggedOn(self):
        return False

    def getWebRequester(self):
        return None

    def compare(self, state):
        return self.getStateID() == state.getStateID() if state is not None else False

    def update(self):
        self._changeState(self._getNextState())

    @async
    def sendRequest(self, ctx, callback, allowDelay=None):
        callback(self._makeErrorResponse())

    def login(self):
        pass

    @async
    @process
    def loginAsync(self, callback):
        yield lambda callback: callback(True)
        callback(False)

    def logout(self):
        pass

    @async
    @process
    def getAccessTokenData(self, force=False, callback=None):
        yield lambda callback: callback(True)
        callback(None)
        return

    def _changeState(self, state):
        if state is not None and self._webCtrl is not None and not self._webCtrl.compareStates(state):
            webCtrl = self._webCtrl
            self.fini()
            state.init()
            webCtrl.changeState(state)
            state.invalidate()
        return

    def _getNextState(self):
        state = None
        if self.connectionMgr.isConnected():
            if self.lobbyContext.getServerSettings().roaming.isInRoaming():
                state = RoamingState(self._webCtrl)
            elif not self.lobbyContext.getServerSettings().wgcg.isEnabled():
                state = DisabledState(self._webCtrl)
        else:
            state = UndefinedState(self._webCtrl)
        return state

    def _makeErrorResponse(self):
        return WgcgRequestResponse(ResponseCodes.UNKNOWN_ERROR, 'Request cannot be sent from the current state', None)


@ReprInjector.withParent()
class UndefinedState(_State):

    def __init__(self, webCtrl):
        super(UndefinedState, self).__init__(webCtrl, WebControllerStates.STATE_NOT_DEFINED)

    def _getNextState(self):
        state = super(UndefinedState, self)._getNextState()
        if state is None:
            state = AvailableState(self._webCtrl)
        return state


@ReprInjector.withParent()
class RoamingState(_State):

    def __init__(self, webCtrl):
        super(RoamingState, self).__init__(webCtrl, WebControllerStates.STATE_ROAMING)

    def _getNextState(self):
        state = super(RoamingState, self)._getNextState()
        if state is None:
            state = AvailableState(self._webCtrl)
        return state


@ReprInjector.withParent()
class DisabledState(_State):

    def __init__(self, webCtrl):
        super(DisabledState, self).__init__(webCtrl, WebControllerStates.STATE_DISABLED)

    def _getNextState(self):
        state = super(DisabledState, self)._getNextState()
        if state is None:
            state = AvailableState(self._webCtrl)
        return state


@ReprInjector.withParent()
class _WebState(_State):

    def __init__(self, webCtrl, stateID):
        super(_WebState, self).__init__(webCtrl, stateID)
        self.__requestsCtrl = None
        self.__webRequester = None
        self.__gateUrl = None
        return

    def init(self):
        super(_WebState, self).init()
        wgcg = self.lobbyContext.getServerSettings().wgcg
        self.__webRequester = g_webFactory.createWebRequester(wgcg, client_lang=getClientLanguage())
        self.__gateUrl = wgcg.getGateUrl()
        self.__requestsCtrl = g_webFactory.createWgcgRequestsController(self._webCtrl, g_webFactory.createWgcgRequester(self.__webRequester))

    def fini(self):
        self.__webRequester = None
        self.__requestsCtrl.fini()
        self.__gateUrl = None
        super(_WebState, self).fini()
        return

    def getGateUrl(self):
        return self.__gateUrl

    def compare(self, state):
        return super(_WebState, self).compare(state) and state.__gateUrl == self.__gateUrl if state is not None and isinstance(state, _WebState) else super(_WebState, self).compare(state)

    @async
    @process
    def sendRequest(self, ctx, callback, allowDelay=None):
        result = yield self._sendRequest(ctx, allowDelay=allowDelay)
        callback(result)

    @async
    def _sendRequest(self, ctx, callback, allowDelay=None):
        requestControler = self.__requestsCtrl

        def _cbWrapper(result):
            LOG_DEBUG('Response is received:', ctx, result)
            callback(result)

        requestControler.request(ctx, callback=_cbWrapper, allowDelay=allowDelay)

    def getWebRequester(self):
        return self.__webRequester


@ReprInjector.withParent()
class UnavailableState(_WebState):

    def __init__(self, webCtrl):
        super(UnavailableState, self).__init__(webCtrl, WebControllerStates.STATE_UNAVAILABLE)
        self.__bwCbId = None
        self.__ctx = PingCtx()
        self.__isPingRunning = False
        self.__backOff = backoff.ExpBackoff(_PING_BACK_OFF_MIN_DELAY, _PING_BACK_OFF_MAX_DELAY, _PING_BACK_OFF_MODIFIER, _PING_BACK_OFF_EXP_RANDOM_FACTOR)
        return

    def fini(self):
        self._cancelPingCB()
        self.__backOff.reset()
        super(UnavailableState, self).fini()

    def invalidate(self):
        self._ping()

    @async
    @process
    def _sendRequest(self, ctx, callback, allowDelay=True):
        if ctx.getRequestType() == WebRequestDataType.PING:
            result = yield super(UnavailableState, self)._sendRequest(ctx, allowDelay=allowDelay)
        else:
            result = WgcgRequestResponse(ResponseCodes.WGCG_ERROR, 'WGCG is not available.', None)
        callback(result)
        return

    @process
    def _ping(self):
        if self.__isPingRunning:
            return
        self._cancelPingCB()
        self.__isPingRunning = True
        result = yield self.sendRequest(self.__ctx, allowDelay=True)
        self.__isPingRunning = False
        if result.isSuccess() and self._webCtrl.simWGCGEnabled():
            self._changeState(AvailableState(self._webCtrl))
        else:
            self._schedulePingCB()

    def _schedulePingCB(self):
        if self.__bwCbId is None:
            delay = self.__backOff.next()
            self.__bwCbId = BigWorld.callback(delay, self._ping)
        return

    def _cancelPingCB(self):
        if self.__bwCbId is not None:
            BigWorld.cancelCallback(self.__bwCbId)
            self.__bwCbId = None
        return


@ReprInjector.withParent()
class AvailableState(_WebState):

    def __init__(self, webCtrl):
        super(AvailableState, self).__init__(webCtrl, WebControllerStates.STATE_AVAILABLE)
        self.__loginState = LOGIN_STATE.LOGGED_OFF
        self._tokenRequester = None
        self.__waitingRequests = list()
        self.__clanSync = False
        self.__accessTokenData = None
        self.__accessTokenCallbacks = list()
        return

    def init(self):
        super(AvailableState, self).init()
        self._tokenRequester = g_webFactory.createTokenRequester()

    def isAvailable(self):
        return True

    def isLoggedOn(self):
        return self.__loginState == LOGIN_STATE.LOGGED_ON

    def getLimits(self, profile):
        return AccountClanLimits(profile)

    def clanSync(self, ctx):
        if not self.__clanSync and ctx.isClanSyncRequired():
            if self._webCtrl and self.isLoggedOn():
                self._webCtrl.onStateUpdated()
                self.__clanSync = True

    @async
    @process
    def _sendRequest(self, ctx, callback, allowDelay=True):
        if ctx.isAuthorizationRequired() and not self.isLoggedOn():
            self.__waitingRequests.append((ctx,
             callback,
             WgcgRequestResponse(ResponseCodes.AUTHENTIFICATION_ERROR, 'The user is not authorized.', None),
             allowDelay))
            self.login()
        else:
            self.clanSync(ctx)
            if self._webCtrl and self._webCtrl.simWGCGEnabled():
                result = yield super(AvailableState, self)._sendRequest(ctx, allowDelay=allowDelay)
            else:
                result = WgcgRequestResponse(ResponseCodes.WGCG_ERROR, 'Simulated WGCG error!', None)
            resultCode = result.code
            if resultCode == ResponseCodes.WGCG_ERROR:
                LOG_DEBUG('WGCG error has occurred! The state will be changed to NA.')
                self._changeState(UnavailableState(self._webCtrl))
                callback(result)
            elif ctx.getRequestType() != WebRequestDataType.LOGIN and resultCode == ResponseCodes.AUTHENTIFICATION_ERROR:
                LOG_WARNING('Request requires user to be authenticated. Will try to login and resend the request.', ctx)
                self.__waitingRequests.append((ctx,
                 callback,
                 result,
                 allowDelay))
                self.login()
            elif ctx.getRequestType() != WebRequestDataType.LOGIN and resultCode in _RELOGIN_CODES:
                LOG_WARNING('Failed to do WGCG request. Need to relogin.', ctx)
                self.__waitingRequests.append((ctx,
                 callback,
                 result,
                 allowDelay))
                self.__loginState = LOGIN_STATE.LOGGED_OFF
                self.login()
            else:
                callback(result)
        return

    @process
    def login(self):
        yield self.__doLogin()

    @async
    @process
    def loginAsync(self, callback):
        yield self.__doLogin()
        callback(True)

    @process
    def logout(self):
        if self.isLoggedOn():
            yield self.__doLogOut()

    @async
    @process
    def getAccessTokenData(self, force=False, callback=None):
        yield lambda callback: callback(True)
        timeOut = self.__accessTokenData is None or time_utils.getServerUTCTime() > self.__accessTokenData.expiresAt
        if force or timeOut:
            if self.__loginState is LOGIN_STATE.LOGGING_IN:
                self.__accessTokenCallbacks.append(callback)
                return
            self.__loginState = LOGIN_STATE.LOGGED_OFF
            yield self.__doLogin()
        callback(self.__accessTokenData)
        return

    def _getNextState(self):
        state = super(AvailableState, self)._getNextState()
        gateUrl = self.getGateUrl()
        if self.connectionMgr.isConnected() and state is None and gateUrl is not None and gateUrl != self.lobbyContext.getServerSettings().wgcg.getGateUrl():
            state = AvailableState(self._webCtrl)
        return state

    @async
    @process
    def __doLogin(self, callback):
        if not LOGIN_STATE.canDoLogin(self.__loginState):
            callback(self.isLoggedOn())
            return
        LOG_DEBUG('Wgcg gate login processing...')
        self.__loginState = LOGIN_STATE.LOGGING_IN
        nextLoginState = LOGIN_STATE.LOGGED_OFF
        LOG_DEBUG('Requesting spa token...')
        response = yield self._tokenRequester.request(allowDelay=True)
        if response and response.isValid():
            pDbID = getPlayerDatabaseID()
            if response.getDatabaseID() == pDbID:
                LOG_DEBUG('Trying to login to the wgcg lib...')
                responseTime = time_utils.getServerUTCTime()
                result = yield self.sendRequest(LogInCtx(pDbID, response.getToken()))
                if result.isSuccess():
                    nextLoginState = LOGIN_STATE.LOGGED_ON
                    data = result.getData()
                    self.__accessTokenData = AccessTokenData(data['access_token'], responseTime + float(data['expires_in']))
                else:
                    nextLoginState = LOGIN_STATE.LOGGED_OFF
        else:
            LOG_WARNING('There is error while getting spa token for wgcg gate', response)
        self.__loginState = nextLoginState
        self.__clanSync = False
        self.__processWaitingRequests()
        callback(self.isLoggedOn())

    @async
    @process
    def __doLogOut(self, callback):
        LOG_DEBUG('Wgcg gate logout processing...')
        result = yield self.sendRequest(LogOutCtx())
        if not result.isSuccess():
            LOG_WARNING('Disconnect problem!')
        self.__loginState = LOGIN_STATE.LOGGED_OFF
        self._webCtrl.onStateUpdated()
        callback(result)

    @process
    def __processWaitingRequests(self):
        for callback in self.__accessTokenCallbacks:
            callback(self.__accessTokenData)

        del self.__accessTokenCallbacks[:]
        if self.isLoggedOn():
            while self.__waitingRequests:
                ctx, clallback, prevResult, allowDelay = self.__waitingRequests.pop(0)
                result = yield self._sendRequest(ctx, allowDelay=allowDelay)
                clallback(result)

        else:
            while self.__waitingRequests:
                ctx, clallback, prevResult, allowDelay = self.__waitingRequests.pop(0)
                clallback(prevResult)
