# Embedded file name: scripts/client/ConnectionManager.py
import constants
import json
import hashlib
import BigWorld
from Event import Event
from Singleton import Singleton
from enumerations import Enumeration
from debug_utils import *
from predefined_hosts import g_preDefinedHosts
from functools import partial
CONNECTION_STATUS = Enumeration('Connection status', ('disconnected', 'connected', 'connectionInProgress', 'disconnectingInProgress', 'kicked'))

def getHardwareID():
    import Settings
    up = Settings.g_instance.userPrefs
    if up.has_key(Settings.KEY_LOGIN_INFO):
        loginInfo = up[Settings.KEY_LOGIN_INFO]
    else:
        loginInfo = up.write(Settings.KEY_LOGIN_INFO, '')
    prevSalt = loginInfo.readString('salt', '')
    newSalt = BigWorld.wg_cpsalt(prevSalt)
    loginInfo.writeString('salt', newSalt)
    return newSalt


def md5hex(concealed_value):
    m = hashlib.md5()
    m.update(concealed_value)
    return m.hexdigest()


class AUTH_METHODS:
    BASIC = 'basic'
    EBANK = 'ebank'
    TOKEN2 = 'token2'
    TOKEN = 'token'


class ConnectionManager(Singleton):

    @staticmethod
    def instance():
        return ConnectionManager()

    def _singleton_init(self):
        self.__host = g_preDefinedHosts._makeHostItem('', '', '')
        self.searchServersCallbacks = Event()
        self.connectionStatusCallbacks = Event()
        self.__connectionStatus = CONNECTION_STATUS.disconnected
        self.onConnected = Event()
        self.onDisconnected = Event()
        self.onRejected = Event()
        self.__rawStatus = ''
        self.__loginName = None
        self.__isVersionsDiffered = False
        BigWorld.serverDiscovery.changeNotifier = self._searchServersHandler
        return

    def startSearchServers(self):
        if constants.IS_DEVELOPMENT:
            BigWorld.serverDiscovery.searching = 1

    def stopSearchServers(self):
        if constants.IS_DEVELOPMENT:
            BigWorld.serverDiscovery.searching = 0

    def _searchServersHandler(self):

        def _serverDottedHost(ip):
            return '%d.%d.%d.%d' % (ip >> 24 & 255,
             ip >> 16 & 255,
             ip >> 8 & 255,
             ip >> 0 & 255)

        def _serverNetName(details):
            name = _serverDottedHost(details.ip)
            if details.port:
                name += ':%d' % details.port
                return name

        def _serverNiceName(details):
            name = details.hostName
            if not name:
                name = _serverNetName(details)
            elif details.port:
                name += ':%d' % details.port
            if details.ownerName:
                name += ' (' + details.ownerName + ')'
            return name

        servers = [ (_serverNiceName(server), server.serverString) for server in BigWorld.serverDiscovery.servers ]
        self.searchServersCallbacks(servers)

    def connect(self, url, login, password, publicKeyPath = None, nickName = None, token2 = '', isNeedSavingPwd = False, tokenLoginParams = None):
        self.disconnect()
        LOG_DEBUG('url: %s; login: %s; pass: %s; name: %s; token: %s' % (url,
         login,
         password,
         nickName,
         token2))
        self.__isVersionsDiffered = False
        self.__setConnectionStatus(CONNECTION_STATUS.connectionInProgress)
        basicLoginParams = {'login': login,
         'auth_method': AUTH_METHODS.EBANK if constants.IS_VIETNAM else AUTH_METHODS.BASIC}
        loginParams = tokenLoginParams if tokenLoginParams is not None else basicLoginParams
        loginParams['session'] = md5hex(getHardwareID())
        loginParams['auth_realm'] = constants.AUTH_REALM
        loginParams['game'] = 'wot'
        loginParams['temporary'] = str(int(not isNeedSavingPwd))
        if nickName is not None:
            loginParams['nickname'] = nickName
            loginParams['auto_registration'] = 'true'
        if constants.IS_IGR_ENABLED:
            loginParams['is_igr'] = '1'
        if token2:
            loginParams['token2'] = token2
            loginParams['auth_method'] = AUTH_METHODS.TOKEN2

        class LoginInfo:
            pass

        loginInfo = LoginInfo()
        loginInfo.username = json.dumps(loginParams).encode('utf8')
        loginInfo.password = password
        loginInfo.inactivityTimeout = constants.CLIENT_INACTIVITY_TIMEOUT
        if publicKeyPath is not None:
            loginInfo.publicKeyPath = publicKeyPath
        if login and constants.IS_DEVELOPMENT and login[0] == '@':
            try:
                loginInfo.username = login[1:]
            except IndexError:
                loginInfo.username = login

        BigWorld.connect(url, loginInfo, partial(self.connectionWatcher, nickName is not None))
        self.__setConnectionStatus(CONNECTION_STATUS.connectionInProgress)
        self.__loginName = login
        if g_preDefinedHosts.predefined(url) or g_preDefinedHosts.roaming(url):
            self.__host = g_preDefinedHosts.byUrl(url)
        else:
            for server in BigWorld.serverDiscovery.servers:
                if server.serverString == url:
                    self.__host = self.__host._replace(name=server.ownerName)
                    break

        return

    def disconnect(self):
        keepClientOnlySpaces = False
        from gui.shared.utils.HangarSpace import g_hangarSpace
        if g_hangarSpace is not None and g_hangarSpace.inited:
            keepClientOnlySpaces = g_hangarSpace.spaceLoading()
        BigWorld.disconnect()
        BigWorld.clearEntitiesAndSpaces(keepClientOnlySpaces)
        if self.isConnected():
            self.__setConnectionStatus(CONNECTION_STATUS.disconnectingInProgress)
        return

    @property
    def serverUserName(self):
        return self.__host.name

    @property
    def serverUserNameShort(self):
        return self.__host.shortName

    @property
    def peripheryID(self):
        return self.__host.peripheryID

    @property
    def areaID(self):
        if not self.isDisconnected():
            return self.__host.areaID
        else:
            return None

    @property
    def loginName(self):
        if not self.isDisconnected():
            return self.__loginName
        else:
            return None

    @property
    def lastLoginName(self):
        return self.__loginName

    @property
    def databaseID(self):
        if not self.isDisconnected():
            return BigWorld.player().databaseID
        else:
            return None

    @property
    def isVersionsDiffered(self):
        return self.__isVersionsDiffered

    def onKickedFromServer(self, reason, isBan, expiryTime):
        self.__setConnectionStatus(CONNECTION_STATUS.kicked)
        from gui import DialogsInterface
        DialogsInterface.showDisconnect(reason, isBan, expiryTime)

    def connectionWatcher(self, isAutoRegister, stage, status, serverMsg):
        self.__connectionStatusCallback(stage, status, serverMsg, isAutoRegister)
        self.connectionStatusCallbacks(stage, status, serverMsg, isAutoRegister)

    def checkClientServerVersions(self, clientVersion, serverVersion):
        if serverVersion != clientVersion:
            LOG_DEBUG('Version mismatch. Client is "%s", server needs "%s".' % (clientVersion, serverVersion))
            self.__isVersionsDiffered = True
            BigWorld.callback(0.001, BigWorld.disconnect)
        else:
            self.__isVersionsDiffered = False

    def __connectionStatusCallback(self, stage, status, serverMsg, isAutoRegister):
        LOG_MX('__connectionStatusCallback', stage, status, serverMsg)
        self.__rawStatus = status
        if stage == 0:
            pass
        elif stage == 1:
            if status != 'LOGGED_ON':
                self.__setConnectionStatus(CONNECTION_STATUS.disconnected)
                self.onRejected()
            else:
                self.__setConnectionStatus(CONNECTION_STATUS.connected)
                self.onConnected()
        elif stage == 2:
            pass
        elif stage == 6:
            self.__setConnectionStatus(CONNECTION_STATUS.disconnected)
            self.onDisconnected()
        else:
            LOG_UNEXPECTED('stage:%d, status:%s, serverMsg:%s' % (stage, status, serverMsg))

    def __setConnectionStatus(self, status):
        self.__connectionStatus = status

    def isDisconnected(self):
        return self.__connectionStatus != CONNECTION_STATUS.connected

    def isConnected(self):
        return self.__connectionStatus == CONNECTION_STATUS.connected

    def isUpdateClientSoftwareNeeded(self):
        return self.__rawStatus in ('LOGIN_BAD_PROTOCOL_VERSION', 'LOGIN_REJECTED_BAD_DIGEST')


def _getClientUpdateUrl():
    import Settings
    return Settings.g_instance.scriptConfig.readString(Settings.KEY_UPDATE_URL)


connectionManager = ConnectionManager.instance()
