# Embedded file name: scripts/client/gui/clans/states.py
from adisp import process, async
import BigWorld
from client_request_lib.exceptions import ResponseCodes
from helpers import getClientLanguage
from ConnectionManager import connectionManager
from gui.LobbyContext import g_lobbyContext
from gui.clans.restrictions import AccountClanLimits, DefaultAccountClanLimits
from gui.clans import contexts
from gui.clans.factory import g_clanFactory
from gui.clans.settings import CLAN_CONTROLLER_STATES, LOGIN_STATE, CLAN_REQUESTED_DATA_TYPE
from gui.clans.requests import ClanRequestResponse
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils import getPlayerDatabaseID, backoff
from debug_utils import LOG_WARNING, LOG_DEBUG
_PING_BACK_OFF_MIN_DELAY = 60
_PING_BACK_OFF_MAX_DELAY = 1200
_PING_BACK_OFF_MODIFIER = 30
_PING_BACK_OFF_EXP_RANDOM_FACTOR = 5

@ReprInjector.simple(('getStateID', 'state'))

class _ClanState(object):

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

    def update(self):
        self._changeState(self._getNextState())

    @async
    def sendRequest(self, ctx, callback, allowDelay = None):
        callback(self._makeErrorResponse())

    def login(self):
        pass

    def logout(self):
        pass

    def _changeState(self, state):
        if state is not None and self._clanCtrl is not None and state.getStateID() != self._clanCtrl.getStateID():
            clanCtrl = self._clanCtrl
            self.fini()
            state.init()
            clanCtrl.changeState(state)
            state.invalidate()
        return

    def _getNextState(self):
        state = None
        if connectionManager.isConnected():
            if g_lobbyContext.getServerSettings().roaming.isInRoaming():
                state = ClanRoamingState(self._clanCtrl)
            elif not g_lobbyContext.getServerSettings().clanProfile.isEnabled():
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
        return

    def init(self):
        super(_ClanWebState, self).init()
        self.__webRequester = g_clanFactory.createWebRequester(g_lobbyContext.getServerSettings().clanProfile.getSettingsJSON(), client_lang=getClientLanguage())
        self.__requestsCtrl = g_clanFactory.createClanRequestsController(self._clanCtrl, g_clanFactory.createClanRequester(self.__webRequester))

    def fini(self):
        self.__webRequester = None
        self.__requestsCtrl.fini()
        super(_ClanWebState, self).fini()
        return

    @async
    def sendRequest(self, ctx, callback, allowDelay = None):

        def _cbWrapper(result):
            LOG_DEBUG('Response is received:', ctx, result)
            callback(result)

        self.__requestsCtrl.request(ctx, callback=_cbWrapper, allowDelay=allowDelay)

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

    def init(self):
        super(ClanUnavailableState, self).init()

    def fini(self):
        self._cancelPingCB()
        self.__backOff.reset()
        super(ClanUnavailableState, self).fini()

    def invalidate(self):
        self._ping()

    @async
    @process
    def sendRequest(self, ctx, callback, allowDelay = True):
        if ctx.getRequestType() == CLAN_REQUESTED_DATA_TYPE.PING:
            result = yield super(ClanUnavailableState, self).sendRequest(ctx, allowDelay=allowDelay)
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

    def _getNextState(self):
        return super(ClanUnavailableState, self)._getNextState()


@ReprInjector.withParent()

class ClanAvailableState(_ClanWebState):

    def __init__(self, clansCtrl):
        super(ClanAvailableState, self).__init__(clansCtrl, CLAN_CONTROLLER_STATES.STATE_AVAILABLE)
        self.__loginState = LOGIN_STATE.LOGGED_OFF
        self._tokenRequester = None
        self.__waitingRequests = list()
        return

    def init(self):
        super(ClanAvailableState, self).init()
        self._tokenRequester = g_clanFactory.createTokenRequester()

    def fini(self):
        super(ClanAvailableState, self).fini()

    def isAvailable(self):
        return True

    def isLoggedOn(self):
        return self.__loginState == LOGIN_STATE.LOGGED_ON

    def getLimits(self, profile):
        return AccountClanLimits(profile)

    @async
    @process
    def sendRequest(self, ctx, callback, allowDelay = True):
        if ctx.isAuthorizationRequired() and not self.isLoggedOn():
            self.__waitingRequests.append((ctx,
             callback,
             ClanRequestResponse(ResponseCodes.AUTHENTIFICATION_ERROR, 'The user is not authorized.', None),
             allowDelay))
            self.login()
        else:
            if self._clanCtrl and self._clanCtrl.simWGCGEnabled():
                result = yield super(ClanAvailableState, self).sendRequest(ctx, allowDelay=allowDelay)
            else:
                result = ClanRequestResponse(ResponseCodes.WGCG_ERROR, 'Simulated WGCG error!', None)
            if result.code == ResponseCodes.WGCG_ERROR:
                LOG_DEBUG('WGCG error has occurred! The state will be changed to NA.')
                self._changeState(ClanUnavailableState(self._clanCtrl))
                callback(result)
            elif result.code == ResponseCodes.AUTHENTIFICATION_ERROR:
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

    @process
    def logout(self):
        if self.isLoggedOn():
            yield self.__doLogOut()

    def _getNextState(self):
        return super(ClanAvailableState, self)._getNextState()

    @async
    @process
    def __doLogin(self, callback):
        if not LOGIN_STATE.canDoLogin(self.__loginState):
            callback(self.isLoggedOn())
            return
        LOG_DEBUG('Clan gate login processing...')
        self.__loginState = LOGIN_STATE.LOGGING_IN
        nextLoginState = LOGIN_STATE.LOGGED_OFF
        LOG_DEBUG('Requesting spa token...')
        response = yield self._tokenRequester.request()
        if response and response.isValid():
            pDbID = getPlayerDatabaseID()
            if response.getDatabaseID() == pDbID:
                LOG_DEBUG('Trying to login to the clan lib...')
                result = yield self.sendRequest(contexts.LogInCtx(pDbID, response.getToken()))
                if result.isSuccess():
                    nextLoginState = LOGIN_STATE.LOGGED_ON
                else:
                    nextLoginState = LOGIN_STATE.LOGGED_OFF
        else:
            LOG_WARNING('There is error while getting spa token for clan gate', response)
        self.__loginState = nextLoginState
        if self.isLoggedOn():
            self._clanCtrl.onStateUpdated()
        self.__processWaitingRequests()
        callback(self.isLoggedOn())

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
        if self.isLoggedOn():
            while len(self.__waitingRequests):
                ctx, clallback, prevResult, allowDelay = self.__waitingRequests.pop(0)
                result = yield self.sendRequest(ctx, allowDelay=allowDelay)
                clallback(result)

        else:
            while len(self.__waitingRequests):
                ctx, clallback, prevResult, allowDelay = self.__waitingRequests.pop(0)
                clallback(prevResult)
