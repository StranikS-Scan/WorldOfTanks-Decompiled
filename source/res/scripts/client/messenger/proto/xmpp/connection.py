# Embedded file name: scripts/client/messenger/proto/xmpp/connection.py
import random
import BigWorld
from constants import TOKEN_TYPE
from ConnectionManager import connectionManager
from adisp import process
from gui.shared.utils import backoff, getPlayerDatabaseID
from gui.shared.utils.requesters import TokenRequester, TokenResponse
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp.gloox_constants import DISCONNECT_REASON, CONNECTION_IMPL_TYPE, GLOOX_EVENT
from messenger.proto.xmpp.gloox_wrapper import ClientEventsHandler
from messenger.proto.xmpp.log_output import CLIENT_LOG_AREA, g_logOutput
from messenger.proto.xmpp.logger import sendEventToServer, XMPP_EVENT_LOG
_BACK_OFF_MIN_DELAY = 10
_BACK_OFF_MAX_DELAY = 5120
_BACK_OFF_MODIFIER = 10
_BACK_OFF_MOD_RANDOM_FACTOR = 2
_BACK_OFF_EXP_RANDOM_FACTOR = 1
_BACK_OFF_MIN_RANDOM = 20
_BACK_OFF_MAX_RANDOM = 30
_MAX_REQ_TOKEN_TRIES = 4
_NUMBER_OF_ITEMS_IN_SAMPLE = 2

def _makeSample(*args):
    queue = []
    for seq in args:
        count = min(len(seq), _NUMBER_OF_ITEMS_IN_SAMPLE)
        queue.extend(random.sample(seq, count))

    return queue


class ConnectionsIterator(object):

    def __init__(self, base = None, alt = None, bosh = None):
        super(ConnectionsIterator, self).__init__()
        self.__tcp = _makeSample(base or [], alt or [])
        self.__bosh = _makeSample(bosh or [])

    def __iter__(self):
        return self

    def clear(self):
        self.__tcp = []
        self.__bosh = []

    def hasNext(self):
        return self.__tcp or self.__bosh

    def next(self):
        if self.__tcp:
            cType = CONNECTION_IMPL_TYPE.TCP
            host, port = self.__tcp.pop(0)
        elif self.__bosh:
            cType = CONNECTION_IMPL_TYPE.BOSH
            host, port = self.__bosh.pop(0)
        else:
            raise StopIteration
        return (cType, host, port)


class ConnectionsInfo(object):

    def __init__(self):
        super(ConnectionsInfo, self).__init__()
        self.__iterator = None
        self.__backOff = None
        self.__address = ('', -1)
        return

    def init(self):
        self.__iterator = g_settings.server.XMPP.getConnectionsIterator()
        self.__backOff = backoff.RandomBackoff(minTime=_BACK_OFF_MIN_RANDOM, maxTime=_BACK_OFF_MAX_RANDOM)

    def clear(self):
        if self.__backOff:
            self.__backOff.reset()
        if self.__iterator:
            self.__iterator.clear()

    def getPlayerFullJID(self):
        return g_settings.server.XMPP.getFullJID(getPlayerDatabaseID())

    def getNextConnection(self):
        if not self.__iterator.hasNext():
            self.__iterator = g_settings.server.XMPP.getConnectionsIterator()
            if isinstance(self.__backOff, backoff.RandomBackoff):
                backOff = backoff.ModBackoff(_BACK_OFF_MIN_DELAY, _BACK_OFF_MAX_DELAY, _BACK_OFF_MODIFIER, _BACK_OFF_MOD_RANDOM_FACTOR)
                backOff.shift(self.__backOff.getTries())
                self.__backOff = backOff
        cType, host, port = self.__iterator.next()
        self.__address = (host, port)
        return (cType, host, port)

    def getNextDelay(self):
        return self.__backOff.next()

    def getTries(self):
        return self.__backOff.getTries()

    def getLastAddress(self):
        return self.__address


class ChatTokenResponse(TokenResponse):

    def getCredential(self):
        return str(self._token)


class ConnectionHandler(ClientEventsHandler):

    def __init__(self):
        super(ConnectionHandler, self).__init__()
        self.__tokenRequester = TokenRequester(TOKEN_TYPE.XMPPCS, ChatTokenResponse, False)
        self.__reconnectCallbackID = None
        self.__reqTokenCallbackID = None
        self.__connectionsInfo = ConnectionsInfo()
        self.__reqTokenBackOff = backoff.ExpBackoff(self.__tokenRequester.getReqCoolDown(), _BACK_OFF_MAX_DELAY, _BACK_OFF_MODIFIER, _BACK_OFF_EXP_RANDOM_FACTOR)
        return

    def connect(self):
        if self.__reconnectCallbackID is None:
            self.__connectionsInfo.init()
            self.__doConnect()
        else:
            g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Connection already is processing')
        return

    def disconnect(self):
        client = self.client()
        if client:
            g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Sends request to disconnect and removes all listeners')
            client.disconnect()
        self.clear()

    def clear(self):
        self.__connectionsInfo.clear()
        self.__reqTokenBackOff.reset()
        self.__cancelReconnectCallback()
        self.__cancelReqTokenCallback()
        self.__tokenRequester.clear()
        g_settings.server.XMPP.clear()

    def isInGameServer(self):
        return connectionManager.isConnected()

    def registerHandlers(self):
        client = self.client()
        client.registerHandler(GLOOX_EVENT.CONNECTED, self.__handleConnect)
        client.registerHandler(GLOOX_EVENT.LOGIN, self.__handleLogin)
        client.registerHandler(GLOOX_EVENT.DISCONNECTED, self.__handleDisconnect)

    def unregisterHandlers(self):
        client = self.client()
        client.unregisterHandler(GLOOX_EVENT.CONNECTED, self.__handleConnect)
        client.unregisterHandler(GLOOX_EVENT.LOGIN, self.__handleLogin)
        client.unregisterHandler(GLOOX_EVENT.DISCONNECTED, self.__handleDisconnect)

    def __doConnect(self):
        client = self.client()
        if not client.isDisconnected():
            g_logOutput.warning(CLIENT_LOG_AREA.CONNECTION, 'Client already is connected(ing)', client.getConnectionAddress(), client.getConnectionState())
            return
        jid = self.__connectionsInfo.getPlayerFullJID()
        if jid:
            cType, host, port = self.__connectionsInfo.getNextConnection()
            g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Connect to XMPP sever', jid, host, port)
            if cType == CONNECTION_IMPL_TYPE.TCP:
                client.connect(str(jid), host, port)
            elif cType == CONNECTION_IMPL_TYPE.BOSH:
                client.connectBosh(str(jid), host, port, '/bosh/')
            else:
                g_logOutput.error(CLIENT_LOG_AREA.CONNECTION, 'This type of connection is not supported', cType)
        else:
            g_logOutput.error(CLIENT_LOG_AREA.CONNECTION, 'JID is empty')

    def __doNextConnect(self):
        self.__reconnectCallbackID = None
        self.__doConnect()
        return

    @process
    def __doLogin(self):
        client = self.client()
        if not client.isConnecting():
            g_logOutput.warning(CLIENT_LOG_AREA.LOGIN, 'Client is not connecting', client.getConnectionAddress(), client.getConnectionState())
            yield lambda callback: callback(None)
            return
        g_logOutput.debug(CLIENT_LOG_AREA.TOKEN, 'Sends request to SPA')
        response = yield self.__tokenRequester.request()
        g_logOutput.debug(CLIENT_LOG_AREA.TOKEN, 'Response is received from SPA', response)
        if not response:
            g_logOutput.error(CLIENT_LOG_AREA.TOKEN, 'Received chat token is empty')
            return
        if response.isValid():
            if response.getDatabaseID() == getPlayerDatabaseID():
                g_logOutput.debug(CLIENT_LOG_AREA.LOGIN, 'Login to XMPP sever')
                client.login(response.getCredential())
            else:
                g_logOutput.error(CLIENT_LOG_AREA.LOGIN, "Player's database ID mismatch", getPlayerDatabaseID())
        else:
            g_logOutput.warning(CLIENT_LOG_AREA.TOKEN, 'Received chat token is not valid', response)
            self.__handleTokenError()

    def __doNextLogin(self):
        self.__reqTokenCallbackID = None
        self.__doLogin()
        return

    def __cancelReconnectCallback(self):
        if self.__reconnectCallbackID is not None:
            BigWorld.cancelCallback(self.__reconnectCallbackID)
            self.__reconnectCallbackID = None
        return

    def __cancelReqTokenCallback(self):
        if self.__reqTokenCallbackID is not None:
            BigWorld.cancelCallback(self.__reqTokenCallbackID)
            self.__reqTokenCallbackID = None
        return

    def __handleConnect(self):
        g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Client is connected')
        self.__cancelReconnectCallback()
        self.__reqTokenBackOff.reset()
        self.__doLogin()

    def __handleLogin(self):
        g_logOutput.debug(CLIENT_LOG_AREA.LOGIN, 'Client is login')
        self.__connectionsInfo.clear()
        self.__reqTokenBackOff.reset()
        g_messengerEvents.onPluginConnected(PROTO_TYPE.XMPP)

    def __handleDisconnect(self, reason, description):
        g_messengerEvents.onPluginDisconnected(PROTO_TYPE.XMPP)
        client = self.client()
        if not client:
            return
        g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Client is disconnected')
        self.__cancelReconnectCallback()
        self.__cancelReqTokenCallback()
        if reason == DISCONNECT_REASON.AUTHENTICATION:
            self.__tokenRequester.clear()
        if self.isInGameServer() and reason != DISCONNECT_REASON.BY_REQUEST:
            delay = self.__connectionsInfo.getNextDelay()
            self.__reconnectCallbackID = BigWorld.callback(delay, self.__doNextConnect)
            g_logOutput.debug(CLIENT_LOG_AREA.CONNECTION, 'Will try to reconnect after {0} seconds'.format(delay), description)
            host, port = self.__connectionsInfo.getLastAddress()
            tries = self.__connectionsInfo.getTries()
            g_messengerEvents.onPluginConnectFailed(PROTO_TYPE.XMPP, (host, port), tries)
            sendEventToServer(XMPP_EVENT_LOG.DISCONNECT, host, port, reason, description, tries)

    def __handleTokenError(self):
        client = self.client()
        if not client:
            return
        if self.__reqTokenBackOff.getTries() < _MAX_REQ_TOKEN_TRIES:
            delay = self.__reqTokenBackOff.next()
            self.__reqTokenCallbackID = BigWorld.callback(delay, self.__doNextLogin)
            g_logOutput.debug(CLIENT_LOG_AREA.TOKEN, 'Will try to request token after {0} seconds'.format(delay))
        else:
            self.client().disconnect()
            self.__handleDisconnect(DISCONNECT_REASON.OTHER_ERROR, 'Received chat token is not valid')
