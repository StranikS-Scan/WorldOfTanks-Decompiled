# Embedded file name: scripts/client/ConnectionManager.py
import hashlib
import ResMgr
import BigWorld
import constants
import json
from Event import Event
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_NOTE
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_URL
from helpers import getClientLanguage
from account_shared import isValidClientVersion
from account_helpers import pwd_token
_MIN_RECONNECTION_TIMEOUT = 5
_RECONNECTION_TIMEOUT_INCREMENT = 5
_MAX_RECONNECTION_TIMEOUT = 20

class CONNECTION_METHOD():
    BASIC = 'basic'
    TOKEN = 'token'
    TOKEN2 = 'token2'


class LOGIN_STATUS():
    NOT_SET = 'NOT_SET'
    LOGGED_ON = 'LOGGED_ON'
    LOGGED_ON_OFFLINE = 'LOGGED_ON_OFFLINE'
    CONNECTION_FAILED = 'CONNECTION_FAILED'
    DNS_LOOKUP_FAILED = 'DNS_LOOKUP_FAILED'
    UNKNOWN_ERROR = 'UNKNOWN_ERROR'
    CANCELLED = 'CANCELLED'
    ALREADY_ONLINE_LOCALLY = 'ALREADY_ONLINE_LOCALLY'
    LOGIN_REJECTED_BAN = 'LOGIN_REJECTED_BAN'
    LOGIN_REJECTED_NO_SUCH_USER = 'LOGIN_REJECTED_NO_SUCH_USER'
    LOGIN_REJECTED_INVALID_PASSWORD = 'LOGIN_REJECTED_INVALID_PASSWORD'
    LOGIN_REJECTED_ALREADY_LOGGED_IN = 'LOGIN_REJECTED_ALREADY_LOGGED_IN'
    LOGIN_REJECTED_BAD_DIGEST = 'LOGIN_REJECTED_BAD_DIGEST'
    LOGIN_REJECTED_DB_GENERAL_FAILURE = 'LOGIN_REJECTED_DB_GENERAL_FAILURE'
    LOGIN_REJECTED_DB_NOT_READY = 'LOGIN_REJECTED_DB_NOT_READY'
    LOGIN_REJECTED_ILLEGAL_CHARACTERS = 'LOGIN_REJECTED_ILLEGAL_CHARACTERS'
    LOGIN_CUSTOM_DEFINED_ERROR = 'LOGIN_CUSTOM_DEFINED_ERROR'
    LOGIN_BAD_PROTOCOL_VERSION = 'LOGIN_BAD_PROTOCOL_VERSION'
    LOGIN_REJECTED_SERVER_NOT_READY = 'LOGIN_REJECTED_SERVER_NOT_READY'
    LOGIN_REJECTED_RATE_LIMITED = 'LOGIN_REJECTED_RATE_LIMITED'


class ConnectionData(object):

    def __init__(self):
        self.username = None
        self.password = None
        self.inactivityTimeout = None
        self.publicKeyPath = None
        self.clientContext = None
        return


class ConnectionManager(object):

    def __init__(self):
        self.__connectionData = ConnectionData()
        self.__connectionUrl = None
        self.__connectionMethod = CONNECTION_METHOD.BASIC
        self.__connectionStatus = LOGIN_STATUS.NOT_SET
        self.__lastLoginName = None
        self.__hostItem = g_preDefinedHosts._makeHostItem('', '', '')
        self.__retryConnectionPeriod = _MIN_RECONNECTION_TIMEOUT
        self.__retryConnectionCallbackID = None
        g_playerEvents.onKickWhileLoginReceived += self.__reconnect
        self.onLoggedOn = Event()
        self.onConnected = Event()
        self.onRejected = Event()
        self.onDisconnected = Event()
        self.onKickedFromServer = Event()
        return

    def __del__(self):
        g_playerEvents.onKickWhileLoginReceived -= self.__reconnect
        self.stopRetryConnection()

    def initiateConnection(self, params, password, serverName):
        self.__setConnectionData(params, password)
        if serverName == AUTO_LOGIN_QUERY_URL:
            g_preDefinedHosts.autoLoginQuery(self.__setHostDataAndConnect)
        else:
            self.__setHostDataAndConnect(g_preDefinedHosts.byUrl(serverName))

    def stopRetryConnection(self):
        if self.__retryConnectionCallbackID is not None:
            BigWorld.cancelCallback(self.__retryConnectionCallbackID)
            self.__retryConnectionPeriod = 0
            self.__retryConnectionCallbackID = None
        return

    def __connect(self):
        self.__retryConnectionCallbackID = None
        LOG_DEBUG('Calling BigWorld.connect with params: {0}, serverName: {1}, inactivityTimeout: {2}, publicKeyPath: {3}'.format(self.__connectionData.username, self.__connectionUrl, constants.CLIENT_INACTIVITY_TIMEOUT, self.__connectionData.publicKeyPath))
        BigWorld.connect(self.__connectionUrl, self.__connectionData, self.__serverResponseHandler)
        if g_preDefinedHosts.predefined(self.__connectionUrl) or g_preDefinedHosts.roaming(self.__connectionUrl):
            self.__hostItem = g_preDefinedHosts.byUrl(self.__connectionUrl)
        else:
            for server in BigWorld.serverDiscovery.servers:
                if server.serverString == self.__connectionUrl:
                    self.__hostItem = self.__hostItem._replace(name=server.ownerName)
                    break

        return

    def __serverResponseHandler(self, stage, status, responseDataJSON):
        LOG_DEBUG('Received server response with stage: {0}, status: {1}, responseData: {2}'.format(stage, status, responseDataJSON))
        self.__connectionStatus = status
        try:
            responseData = json.loads(responseDataJSON)
        except ValueError:
            responseData = {}

        if status == LOGIN_STATUS.LOGGED_ON:
            if stage == 1:
                self.onLoggedOn(responseData)
                self.onConnected()
        else:
            if self.__retryConnectionCallbackID is None:
                self.onRejected(self.__connectionStatus, responseData)
            if status == LOGIN_STATUS.LOGIN_REJECTED_RATE_LIMITED:
                self.__reconnect()
            if stage == 6:
                self.onDisconnected()
        return

    def __setConnectionData(self, params, password):
        self.__lastLoginName = params['login']
        self.__connectionMethod = params['auth_method']
        params['auth_realm'] = constants.AUTH_REALM
        m = hashlib.md5()
        m.update(params['session'])
        params['session'] = m.hexdigest()
        if constants.IS_IGR_ENABLED:
            params['is_igr'] = '1'
        username_ = json.dumps(params, encoding='utf-8')
        LOG_NOTE('User authentication method: {0}'.format(params['auth_method']))
        if 'token2' in params and params['token2']:
            password = ''
        else:
            password = pwd_token.generate(password)
        self.__connectionData.username = username_
        self.__connectionData.password = password
        self.__connectionData.inactivityTimeout = constants.CLIENT_INACTIVITY_TIMEOUT
        self.__connectionData.clientContext = json.dumps({'lang_id': getClientLanguage()})
        if constants.IS_DEVELOPMENT and params['auth_method'] == CONNECTION_METHOD.BASIC and params['login'][0] == '@':
            try:
                self.__connectionData.username = params['login'][1:]
            except IndexError:
                self.__connectionData.username = params['login']

    def __setHostDataAndConnect(self, predefinedHost):
        self.__connectionData.publicKeyPath = predefinedHost.keyPath
        self.__connectionUrl = predefinedHost.urlToken if (self.__connectionMethod == CONNECTION_METHOD.TOKEN or self.__connectionMethod == CONNECTION_METHOD.TOKEN2) and predefinedHost.urlToken else predefinedHost.url
        self.__connect()

    def __reconnect(self, peripheryID = 0):
        self.stopRetryConnection()
        self.__retryConnectionCallbackID = BigWorld.callback(self.__getRetryConnectionPeriod(), self.__connect)

    def __getRetryConnectionPeriod(self):
        if self.__retryConnectionPeriod != _MAX_RECONNECTION_TIMEOUT:
            self.__retryConnectionPeriod += _RECONNECTION_TIMEOUT_INCREMENT
        return self.__retryConnectionPeriod

    @property
    def serverUserName(self):
        return self.__hostItem.name

    @property
    def serverUserNameShort(self):
        return self.__hostItem.shortName

    @property
    def peripheryID(self):
        return self.__hostItem.peripheryID

    @property
    def areaID(self):
        if not self.isDisconnected():
            return self.__hostItem.areaID
        else:
            return None

    @property
    def loginName(self):
        if not self.isDisconnected():
            return self.__lastLoginName
        else:
            return None

    @property
    def lastLoginName(self):
        return self.__lastLoginName

    @property
    def databaseID(self):
        if not self.isDisconnected():
            return BigWorld.player().databaseID
        else:
            return None

    def disconnect(self):
        BigWorld.disconnect()

    def setKickedFromServer(self, reason, isBan, expiryTime):
        self.disconnect()
        self.onKickedFromServer(reason, isBan, expiryTime)

    def isDisconnected(self):
        return self.__connectionStatus != LOGIN_STATUS.LOGGED_ON

    def isStandalone(self):
        return self.peripheryID == 0

    def isConnected(self):
        return self.__connectionStatus == LOGIN_STATUS.LOGGED_ON

    def checkClientServerVersions(self, clientVersion, serverVersion):
        if not isValidClientVersion(clientVersion, serverVersion) or ResMgr.activeContentType() in (constants.CONTENT_TYPE.INCOMPLETE, constants.CONTENT_TYPE.TUTORIAL):
            LOG_DEBUG('Version mismatch. Client is "%s", server needs "%s".' % (clientVersion, serverVersion))
            self.onRejected(LOGIN_STATUS.LOGIN_BAD_PROTOCOL_VERSION, {})
            BigWorld.disconnect()


connectionManager = ConnectionManager()
