# Embedded file name: scripts/client/messenger/proto/xmpp/connection.py
import random
import BigWorld
from constants import TOKEN_TYPE
from ConnectionManager import connectionManager
from adisp import process
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING
from gui.shared.utils.requesters.token_rq import TokenRequester, TokenResponse
from messenger import g_settings
from messenger.ext.player_helpers import getPlayerDatabaseID
from messenger.m_constants import MESSENGER_SCOPE
from messenger.proto.xmpp.gloox_wrapper import GLOOX_EVENT, DISCONNECT_REASON
from messenger.proto.xmpp.gloox_wrapper import PRESENCE, ClientEventsHandler
_MAX_RECONNECT_TRIES = 8
_MAX_REQ_TOKEN_TRIES = 4

def getNextBackOff(tries, maxTries):
    delay = (1 << min(tries, maxTries)) * 10
    return delay + random.randint(0, delay)


class ChatTokenResponse(TokenResponse):

    def getCredential(self):
        return str(self._token)


class ConnectionHandler(ClientEventsHandler):

    def __init__(self):
        super(ConnectionHandler, self).__init__()
        self.__tokenRequester = TokenRequester(TOKEN_TYPE.XMPPCS, ChatTokenResponse, False)
        self.__reconnectCallbackID = None
        self.__reqTokenCallbackID = None
        self.__reconnectCount = 0
        self.__reqTokenCount = 0
        return

    def connect(self):
        if self.__reconnectCallbackID is None:
            self.__doConnect()
        else:
            LOG_DEBUG('Connection already is processing')
        return

    def disconnect(self):
        client = self.client()
        if client:
            client.disconnect()
        self.clear()

    def clear(self):
        self.__reconnectCount = 0
        self.__reqTokenCount = 0
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
            LOG_WARNING('Client already is connected(ing)', client.getConnectionAddress(), client.getConnectionState())
            return
        jid, host, port = g_settings.server.XMPP.getConnection(getPlayerDatabaseID())
        if jid:
            LOG_DEBUG('XMPPClient:Connection. Connect to XMPP sever', jid, host, port)
            client.connect(str(jid), host, port)
        else:
            LOG_ERROR('JID is empty')

    def __doNextConnect(self):
        self.__reconnectCallbackID = None
        self.__doConnect()
        return

    @process
    def __doLogin(self):
        client = self.client()
        if not client.isConnecting():
            LOG_WARNING('Client is not connecting', client.getConnectionAddress(), client.getConnectionState())
            yield lambda callback: callback(None)
            return
        LOG_DEBUG('XMPPClient:Token. Sends request to SPA')
        response = yield self.__tokenRequester.request()
        if not response:
            LOG_ERROR('Received chat token is empty')
            return
        if response.isValid():
            if response.getDatabaseID() == getPlayerDatabaseID():
                LOG_DEBUG('XMPPClient:Connection. Login to XMPP sever')
                self.client().login(response.getCredential())
            else:
                LOG_ERROR("Player's database ID mismatch", response, getPlayerDatabaseID())
        else:
            LOG_WARNING('Received chat token is not valid', response)
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
        LOG_DEBUG('XMPPClient::onConnect')
        self.__cancelReconnectCallback()
        self.__reconnectCount = 0
        self.__reqTokenCount = 0
        g_settings.server.XMPP.clearConnections()
        self.__doLogin()

    def __handleLogin(self):
        LOG_DEBUG('XMPPClient::onLogin')
        self.__reqTokenCount = 0

    def __handleDisconnect(self, reason, description):
        LOG_DEBUG('XMPPClient::onDisconnect', reason, description)
        self.__cancelReconnectCallback()
        self.__cancelReqTokenCallback()
        if reason == DISCONNECT_REASON.AUTHENTICATION:
            self.__tokenRequester.clear()
        if self.isInGameServer() and reason != DISCONNECT_REASON.BY_REQUEST:
            delay = getNextBackOff(self.__reconnectCount, _MAX_RECONNECT_TRIES)
            self.__reconnectCount += 1
            self.__reconnectCallbackID = BigWorld.callback(delay, self.__doNextConnect)
            LOG_DEBUG('XMPPClient::onDisconnect. Will try to reconnect after {0} seconds'.format(delay), description)

    def __handleTokenError(self):
        if self.__reqTokenCount < _MAX_REQ_TOKEN_TRIES:
            delay = max(getNextBackOff(self.__reqTokenCount, _MAX_REQ_TOKEN_TRIES), self.__tokenRequester.getReqCoolDown())
            self.__reqTokenCount += 1
            self.__reqTokenCallbackID = BigWorld.callback(delay, self.__doNextLogin)
            LOG_DEBUG('XMPPClient::Token. Will try to request token after {0} seconds'.format(delay))
        else:
            self.client().disconnect()
            self.__handleDisconnect(DISCONNECT_REASON.OTHER_ERROR, 'Received chat token is not valid')


class PresenceHandler(ClientEventsHandler):

    def __init__(self):
        super(PresenceHandler, self).__init__()
        self.clear()

    def update(self, scope = None):
        if scope:
            self.__scope = scope
        client = self.client()
        if not client or not client.isConnected():
            return
        presence = PRESENCE.UNAVAILABLE
        if self.__scope == MESSENGER_SCOPE.BATTLE:
            presence = PRESENCE.DND
        elif self.__scope == MESSENGER_SCOPE.LOBBY:
            presence = PRESENCE.AVAILABLE
        if client.getClientPresence() != presence:
            client.setClientPresence(presence)

    def clear(self):
        self.__scope = None
        return

    def registerHandlers(self):
        self.client().registerHandler(GLOOX_EVENT.LOGIN, self.__handleLogin)

    def unregisterHandlers(self):
        self.client().unregisterHandler(GLOOX_EVENT.LOGIN, self.__handleLogin)

    def __handleLogin(self):
        self.update()
