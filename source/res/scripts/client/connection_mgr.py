# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/connection_mgr.py
import hashlib
import json
import ResMgr
import BigWorld
import constants
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_NOTE
from shared_utils import nextTick
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_URL
from helpers import getClientLanguage, uniprof
from account_shared import isValidClientVersion
from account_helpers import pwd_token
from skeletons.connection_mgr import IConnectionManager
_MIN_RECONNECTION_TIMEOUT = 5
_RECONNECTION_TIMEOUT_INCREMENT = 5
_MAX_RECONNECTION_TIMEOUT = 20

class CONNECTION_METHOD(object):
    BASIC = 'basic'
    TOKEN = 'token'
    TOKEN2 = 'token2'


class LOGIN_STATUS(object):
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
    SESSION_END = 'SESSION_END'
    LOGIN_REJECTED_ALREADY_LOGGED_IN = 'LOGIN_REJECTED_ALREADY_LOGGED_IN'
    LOGIN_REJECTED_BAD_DIGEST = 'LOGIN_REJECTED_BAD_DIGEST'
    LOGIN_REJECTED_DB_GENERAL_FAILURE = 'LOGIN_REJECTED_DB_GENERAL_FAILURE'
    LOGIN_REJECTED_DB_NOT_READY = 'LOGIN_REJECTED_DB_NOT_READY'
    LOGIN_REJECTED_ILLEGAL_CHARACTERS = 'LOGIN_REJECTED_ILLEGAL_CHARACTERS'
    LOGIN_CUSTOM_DEFINED_ERROR = 'LOGIN_CUSTOM_DEFINED_ERROR'
    LOGIN_BAD_PROTOCOL_VERSION = 'LOGIN_BAD_PROTOCOL_VERSION'
    LOGIN_REJECTED_SERVER_NOT_READY = 'LOGIN_REJECTED_SERVER_NOT_READY'
    LOGIN_REJECTED_RATE_LIMITED = 'LOGIN_REJECTED_RATE_LIMITED'


_INVALID_PASSWORD_TOKEN2_EXPIRED = 'Invalid token2'

class ConnectionData(object):

    def __init__(self):
        self.username = None
        self.password = None
        self.inactivityTimeout = None
        self.publicKeyPath = None
        self.clientContext = None
        return


class ConnectionManager(IConnectionManager):

    def __init__(self):
        self.__connectionData = ConnectionData()
        self.__connectionUrl = None
        self.__connectionMethod = CONNECTION_METHOD.BASIC
        self.__connectionStatus = LOGIN_STATUS.NOT_SET
        self.__lastLoginName = None
        self.__hostItem = g_preDefinedHosts._makeHostItem('', '', '')
        self.__retryConnectionPeriod = _MIN_RECONNECTION_TIMEOUT
        self.__retryConnectionCallbackID = None
        g_playerEvents.onKickWhileLoginReceived += self.__processKick
        g_playerEvents.onLoginQueueNumberReceived += self.__processQueue
        self.__eManager = EventManager()
        self.onLoggedOn = Event(self.__eManager)
        self.onConnected = Event(self.__eManager)
        self.onRejected = Event(self.__eManager)
        self.onDisconnected = Event(self.__eManager)
        self.onKickedFromServer = Event(self.__eManager)
        self.onKickWhileLoginReceived = Event(self.__eManager)
        self.onQueued = Event(self.__eManager)
        return

    def fini(self):
        g_playerEvents.onKickWhileLoginReceived -= self.__processKick
        g_playerEvents.onLoginQueueNumberReceived -= self.__processQueue
        self.__eManager.clear()
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

    @uniprof.regionDecorator(label='offline.connect', scope='enter')
    def __connect(self):
        self.__retryConnectionCallbackID = None
        if constants.IS_DEVELOPMENT:
            LOG_DEBUG('Calling BigWorld.connect with params: {0}, serverName: {1}, inactivityTimeout: {2}, publicKeyPath: {3}'.format(self.__connectionData.username, self.__connectionUrl, constants.CLIENT_INACTIVITY_TIMEOUT, self.__connectionData.publicKeyPath))
        nextTick(lambda : BigWorld.connect(self.__connectionUrl, self.__connectionData, self.__serverResponseHandler))()
        if g_preDefinedHosts.predefined(self.__connectionUrl) or g_preDefinedHosts.roaming(self.__connectionUrl):
            self.__hostItem = g_preDefinedHosts.byUrl(self.__connectionUrl)
        else:
            for server in BigWorld.serverDiscovery.servers:
                if server.serverString == self.__connectionUrl:
                    self.__hostItem = self.__hostItem._replace(name=server.ownerName, shortName=server.ownerName)
                    break
            else:
                self.__hostItem = self.__hostItem._replace(name=self.__connectionUrl, shortName=self.__connectionUrl)

        return

    @uniprof.regionDecorator(label='offline.connect', scope='exit')
    def __serverResponseHandler(self, stage, status, responseDataJSON):
        if constants.IS_DEVELOPMENT:
            LOG_DEBUG('Received server response with stage: {0}, status: {1}, responseData: {2}'.format(stage, status, responseDataJSON))
        self.__connectionStatus = status
        try:
            responseData = json.loads(responseDataJSON)
        except ValueError:
            responseData = {'errorMessage': responseDataJSON}

        if status == LOGIN_STATUS.LOGGED_ON:
            if stage == 1:
                if self.__connectionMethod == CONNECTION_METHOD.TOKEN and 'token2' in responseData:
                    self.__swtichToToken2(responseData['token2'])
                BigWorld.WGC_onServerResponse(True)
                self.onLoggedOn(responseData)
                self.onConnected()
        else:
            if self.__retryConnectionCallbackID is None:
                status_ = self.__connectionStatus
                if responseData.get('errorMessage', '') == _INVALID_PASSWORD_TOKEN2_EXPIRED:
                    status_ = LOGIN_STATUS.SESSION_END
                    BigWorld.WGC_onToken2Expired()
                self.onRejected(status_, responseData)
            if status == LOGIN_STATUS.LOGIN_REJECTED_RATE_LIMITED:
                self.__reconnect()
            if stage == 6:
                BigWorld.WGC_onServerResponse(False)
                self.onDisconnected()
                g_playerEvents.onDisconnected()
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

    def __swtichToToken2(self, token2):
        self.__connectionMethod = CONNECTION_METHOD.TOKEN2
        params = json.loads(self.__connectionData.username, encoding='utf-8')
        params.pop('token', None)
        params['token2'] = token2
        params['auth_method'] = CONNECTION_METHOD.TOKEN2
        self.__connectionData.username = json.dumps(params, encoding='utf-8')
        return

    def __setHostData(self, predefinedHost):
        self.__connectionData.publicKeyPath = predefinedHost.keyPath
        self.__connectionUrl = predefinedHost.urlToken if (self.__connectionMethod == CONNECTION_METHOD.TOKEN or self.__connectionMethod == CONNECTION_METHOD.TOKEN2) and predefinedHost.urlToken else predefinedHost.url

    def __setHostDataAndConnect(self, predefinedHost):
        self.__setHostData(predefinedHost)
        self.__connect()

    def __reconnect(self):
        self.stopRetryConnection()
        self.__retryConnectionCallbackID = BigWorld.callback(self.__getRetryConnectionPeriod(), self.__connect)

    def __getRetryConnectionPeriod(self):
        if self.__retryConnectionPeriod != _MAX_RECONNECTION_TIMEOUT:
            self.__retryConnectionPeriod += _RECONNECTION_TIMEOUT_INCREMENT
        return self.__retryConnectionPeriod

    def __processKick(self, peripheryID):
        if peripheryID > 0:
            host = g_preDefinedHosts.periphery(peripheryID, False)
            if host is not None:
                self.__setHostData(host)
            self.__reconnect()
        self.onKickWhileLoginReceived(peripheryID)
        return

    def __processQueue(self, queueNumber):
        self.onQueued(queueNumber)

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
        return self.__hostItem.areaID if not self.isDisconnected() else None

    @property
    def url(self):
        return self.__hostItem.url

    @property
    def loginName(self):
        return self.__lastLoginName if not self.isDisconnected() else None

    @property
    def lastLoginName(self):
        return self.__lastLoginName

    @property
    def databaseID(self):
        return BigWorld.player().databaseID if not self.isDisconnected() else None

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
