# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/states.py
from adisp import process, async
import BigWorld
from helpers import time_utils
from client_request_lib.exceptions import ResponseCodes
from helpers import dependency
from helpers import getClientLanguage
from gui.clans.restrictions import AccountClanLimits, DefaultAccountClanLimits
from gui.clans import contexts
from gui.clans.factory import g_clanFactory
from gui.clans.settings import CLAN_CONTROLLER_STATES, LOGIN_STATE, CLAN_REQUESTED_DATA_TYPE, AccessTokenData
from gui.clans.requests import ClanRequestResponse
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils import getPlayerDatabaseID, backoff
from debug_utils import LOG_WARNING, LOG_DEBUG
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
_PING_BACK_OFF_MIN_DELAY = 60
_PING_BACK_OFF_MAX_DELAY = 1200
_PING_BACK_OFF_MODIFIER = 30
_PING_BACK_OFF_EXP_RANDOM_FACTOR = 5

@ReprInjector.simple(('getStateID', 'state'))
class _ClanState(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, clansCtrl, stateID):
        self.__stateID = stateID
        self._clanCtrl = clansCtrl

    def init(self):
        pass

    def fini(self):
        self._clanCtrl = None
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
    def getAccessTokenData(self, force, callback):
        yield lambda callback: callback(True)
        callback(None)
        return

    def logout(self):
        pass

    def _changeState(self, state):
        if state is not None and self._clanCtrl is not None and not self._clanCtrl.compareStates(state):
            clanCtrl = self._clanCtrl
            self.fini()
            state.init()
            clanCtrl.changeState(state)
            state.invalidate()
        return

    def _getNextState(self):
        state = None
        if self.connectionMgr.isConnected():
            if self.lobbyContext.getServerSettings().roaming.isInRoaming():
                state = ClanRoamingState(self._clanCtrl)
            elif not self.lobbyContext.getServerSettings().clanProfile.isEnabled():
                state = ClanDisabledState(self._clanCtrl)
        else:
            state = ClanUndefinedState(self._clanCtrl)
        return state

    def _makeErrorResponse(self):
        return ClanRequestResponse(ResponseCodes.UNKNOWN_ERROR, 'Request cannot be sent from the current state', None)


@ReprInjector.withParent()
class ClanUndefinedState(_ClanState):

    def __init__(self, clansCtrl):
        super(ClanUndefinedState, self).__init__(clansCtrl, CLAN_CONTROLLER_STATES.STATE_NOT_DEFINED)

    def _getNextState(self):
        state = super(ClanUndefinedState, self)._getNextState()
        if state is None:
            state = ClanAvailableState(self._clanCtrl)
        return state


@ReprInjector.withParent()
class ClanRoamingState(_ClanState):

    def __init__(self, clansCtrl):
        super(ClanRoamingState, self).__init__(clansCtrl, CLAN_CONTROLLER_STATES.STATE_ROAMING)

    def _getNextState(self):
        state = super(ClanRoamingState, self)._getNextState()
        if state is None:
            state = ClanAvailableState(self._clanCtrl)
        return state


@ReprInjector.withParent()
class ClanDisabledState(_ClanState):

    def __init__(self, clansCtrl):
        super(ClanDisabledState, self).__init__(clansCtrl, CLAN_CONTROLLER_STATES.STATE_DISABLED)

    def _getNextState(self):
        state = super(ClanDisabledState, self)._getNextState()
        if state is None:
            state = ClanAvailableState(self._clanCtrl)
        return state


@ReprInjector.withParent()
class _ClanWebState(_ClanState):

    def __init__(self, clansCtrl, stateID):
        super(_ClanWebState, self).__init__(clansCtrl, stateID)
        self.__requestsCtrl = None
        self.__webRequester = None
        self.__gateUrl = None
        return

    def init(self):
        super(_ClanWebState, self).init()
        clanProfile = self.lobbyContext.getServerSettings().clanProfile
        self.__webRequester = g_clanFactory.createWebRequester(clanProfile, client_lang=getClientLanguage())
        self.__gateUrl = clanProfile.getGateUrl()
        self.__requestsCtrl = g_clanFactory.createClanRequestsController(self._clanCtrl, g_clanFactory.createClanRequester(self.__webRequester))

    def fini(self):
        self.__webRequester = None
        self.__requestsCtrl.fini()
        self.__gateUrl = None
        super(_ClanWebState, self).fini()
        return

    def getGateUrl(self):
        return self.__gateUrl

    def compare(self, state):
        return super(_ClanWebState, self).compare(state) and state.__gateUrl == self.__gateUrl if state is not None and isinstance(state, _ClanWebState) else super(_ClanWebState, self).compare(state)

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
class ClanUnavailableState(_ClanWebState):

    def __init__(self, clansCtrl):
        super(ClanUnavailableState, self).__init__(clansCtrl, CLAN_CONTROLLER_STATES.STATE_UNAVAILABLE)
        self.__bwCbId = None
        self.__ctx = contexts.PingCtx()
        self.__isPingRunning = False
        self.__backOff = backoff.ExpBackoff(_PING_BACK_OFF_MIN_DELAY, _PING_BACK_OFF_MAX_DELAY, _PING_BACK_OFF_MODIFIER, _PING_BACK_OFF_EXP_RANDOM_FACTOR)
        return

    def fini(self):
        self._cancelPingCB()
        self.__backOff.reset()
        super(ClanUnavailableState, self).fini()

    def invalidate(self):
        self._ping()

    @async
    @process
    def _sendRequest(self, ctx, callback, allowDelay=True):
        if ctx.getRequestType() == CLAN_REQUESTED_DATA_TYPE.PING:
            result = yield super(ClanUnavailableState, self)._sendRequest(ctx, allowDelay=allowDelay)
        else:
            result = ClanRequestResponse(ResponseCodes.WGCG_ERROR, 'WGCG is not available.', None)
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
        if result.isSuccess() and self._clanCtrl.simWGCGEnabled():
            self._changeState(ClanAvailableState(self._clanCtrl))
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
class ClanAvailableState(_ClanWebState):

    def __init__(self, clansCtrl):
        super(ClanAvailableState, self).__init__(clansCtrl, CLAN_CONTROLLER_STATES.STATE_AVAILABLE)
        self.__loginState = LOGIN_STATE.LOGGED_OFF
        self._tokenRequester = None
        self.__waitingRequests = list()
        self.__clanSync = False
        self.__accessTokenData = None
        self.__accessTokenCallbacks = list()
        return

    def init(self):
        super(ClanAvailableState, self).init()
        self._tokenRequester = g_clanFactory.createTokenRequester()

    def isAvailable(self):
        return True

    def isLoggedOn(self):
        return self.__loginState == LOGIN_STATE.LOGGED_ON

    def getLimits(self, profile):
        return AccountClanLimits(profile)

    def clanSync(self, ctx):
        if not self.__clanSync and ctx.isClanSyncRequired():
            if self._clanCtrl and self.isLoggedOn():
                self._clanCtrl.onStateUpdated()
                self.__clanSync = True

    @async
    @process
    def _sendRequest(self, ctx, callback, allowDelay=True):
        if ctx.isAuthorizationRequired() and not self.isLoggedOn():
            self.__waitingRequests.append((ctx,
             callback,
             ClanRequestResponse(ResponseCodes.AUTHENTIFICATION_ERROR, 'The user is not authorized.', None),
             allowDelay))
            self.login()
        else:
            self.clanSync(ctx)
            if self._clanCtrl and self._clanCtrl.simWGCGEnabled():
                result = yield super(ClanAvailableState, self)._sendRequest(ctx, allowDelay=allowDelay)
            else:
                result = ClanRequestResponse(ResponseCodes.WGCG_ERROR, 'Simulated WGCG error!', None)
            resultCode = result.code
            if resultCode == ResponseCodes.WGCG_ERROR:
                LOG_DEBUG('WGCG error has occurred! The state will be changed to NA.')
                self._changeState(ClanUnavailableState(self._clanCtrl))
                callback(result)
            elif ctx.getRequestType() != CLAN_REQUESTED_DATA_TYPE.LOGIN and resultCode == ResponseCodes.AUTHENTIFICATION_ERROR:
                LOG_WARNING('Request requires user to be authenticated. Will try to login and resend the request.', ctx)
                self.__waitingRequests.append((ctx,
                 callback,
                 result,
                 allowDelay))
                self.login()
            else:
                callback(result)
        return

    @process
    def login(self):
        yield self.__doLogin()

    @async
    @process
    def getAccessTokenData(self, force, callback):
        yield lambda callback: callback(True)
        timeOut = self.__accessTokenData is None or time_utils.getCurrentTimestamp() > self.__accessTokenData.expiresAt
        if force or timeOut:
            if self.__loginState is LOGIN_STATE.LOGGING_IN:
                self.__accessTokenCallbacks.append(callback)
                return
            self.__loginState = LOGIN_STATE.LOGGED_OFF
            yield self.__doLogin()
        callback(self.__accessTokenData)
        return

    @process
    def logout(self):
        if self.isLoggedOn():
            yield self.__doLogOut()

    def _getNextState(self):
        state = super(ClanAvailableState, self)._getNextState()
        gateUrl = self.getGateUrl()
        if self.connectionMgr.isConnected() and state is None and gateUrl is not None and gateUrl != self.lobbyContext.getServerSettings().clanProfile.getGateUrl():
            state = ClanAvailableState(self._clanCtrl)
        return state

    @async
    @process
    def __doLogin(self, callback):
        if not LOGIN_STATE.canDoLogin(self.__loginState):
            callback(self.isLoggedOn())
            return
        else:
            self.__accessTokenData = None
            LOG_DEBUG('Clan gate login processing...')
            self.__loginState = LOGIN_STATE.LOGGING_IN
            nextLoginState = LOGIN_STATE.LOGGED_OFF
            LOG_DEBUG('Requesting spa token...')
            response = yield self._tokenRequester.request(allowDelay=True)
            if response and response.isValid():
                pDbID = getPlayerDatabaseID()
                if response.getDatabaseID() == pDbID:
                    LOG_DEBUG('Trying to login to the clan lib...')
                    responseTime = time_utils.getCurrentTimestamp()
                    result = yield self.sendRequest(contexts.LogInCtx(pDbID, response.getToken()))
                    if result.isSuccess():
                        nextLoginState = LOGIN_STATE.LOGGED_ON
                        data = result.getData()
                        self.__accessTokenData = AccessTokenData(data['access_token'], responseTime + float(data['expires_in']))
                    else:
                        nextLoginState = LOGIN_STATE.LOGGED_OFF
            else:
                LOG_WARNING('There is error while getting spa token for clan gate', response)
            self.__loginState = nextLoginState
            self.__clanSync = False
            self.__processWaitingRequests()
            callback(self.isLoggedOn())
            return

    @async
    @process
    def __doLogOut(self, callback):
        LOG_DEBUG('Clan gate logout processing...')
        result = yield self.sendRequest(contexts.LogOutCtx())
        if not result.isSuccess():
            LOG_WARNING('Disconnect problem!')
        self.__loginState = LOGIN_STATE.LOGGED_OFF
        self._clanCtrl.onStateUpdated()
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
