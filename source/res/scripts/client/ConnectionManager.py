# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ConnectionManager.py
# Compiled at: 2019-03-12 23:08:12
import hashlib
import json
import BigWorld
import constants
from Event import Event
from Singleton import Singleton
from constants import CLIENT_INACTIVITY_TIMEOUT
from debug_utils import LOG_UNEXPECTED
from enumerations import Enumeration
from predefined_hosts import g_preDefinedHosts
CONNECTION_STATUS = Enumeration('Connection status', ('disconnected', 'connected', 'connectionInProgress'))

def getHardwareID():
    import Settings
    up = Settings.g_instance.userPrefs
    loginInfo = None
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


class ConnectionManager(Singleton):

    @staticmethod
    def instance():
        return ConnectionManager()

    def _singleton_init(self):
        self.serverUserName = ''
        self.peripheryID = 0
        self.searchServersCallbacks = Event()
        self.connectionStatusCallbacks = Event()
        self.connectionStatusCallbacks += self.__connectionStatusCallback
        self.__connectionStatus = CONNECTION_STATUS.disconnected
        self.onConnected = Event()
        self.onDisconnected = Event()
        self.__rawStatus = ''
        self.__areaID = None
        self.__loginName = None
        BigWorld.serverDiscovery.changeNotifier = self._searchServersHandler
        return

    def startSearchServers(self):
        BigWorld.serverDiscovery.searching = 1

    def stopSearchServers(self):
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

    def connect(self, host, user, password, publicKeyPath=None, nickName=None, token2=''):
        self.disconnect()
        if host is not None:
            self.__setConnectionStatus(CONNECTION_STATUS.connectionInProgress)
            if user:
                dct = {'login': user,
                 'auth_method': AUTH_METHODS.BASIC,
                 'session': md5hex(getHardwareID()),
                 'auth_realm': 'SB'}
                if nickName is not None:
                    dct['nickname'] = nickName
                    dct['auto_registration'] = 'true'
                if token2:
                    dct['token2'] = token2
                    dct['auth_method'] = AUTH_METHODS.TOKEN2
            elif BigWorld.WGC_processingState() == constants.WGC_STATE.LOGIN_IN_PROGRESS:
                dct = BigWorld.WGC_loginData()
            else:
                dct = {}
            if not dct:
                LOG_UNEXPECTED("Can't get credentials")
                BigWorld.WGC_printLastError()

            class LoginInfo:
                pass

            loginInfo = LoginInfo()
            loginInfo.username = json.dumps(dct).encode('utf8')
            loginInfo.password = password
            loginInfo.inactivityTimeout = CLIENT_INACTIVITY_TIMEOUT
            if publicKeyPath is not None:
                loginInfo.publicKeyPath = publicKeyPath
            BigWorld.connect(host, loginInfo, self.connectionWatcher)
            self.__setConnectionStatus(CONNECTION_STATUS.connectionInProgress)
            self.serverUserName = ''
            self.peripheryID = 0
            self.__areaID = None
            self.__loginName = user
            if g_preDefinedHosts.predefined(host):
                host = g_preDefinedHosts.byUrl(host)
                self.serverUserName = host.name
                self.peripheryID = host.peripheryID
                self.__areaID = host.areaID
            else:
                for server in BigWorld.serverDiscovery.servers:
                    if server.serverString == host:
                        self.serverUserName = server.ownerName
                        break

        return

    def disconnect(self):
        if not self.isDisconnected():
            BigWorld.disconnect()

    @property
    def areaID(self):
        if not self.isDisconnected():
            return self.__areaID
        else:
            return None

    @property
    def loginName(self):
        if not self.isDisconnected():
            return self.__loginName
        else:
            return None

    def connectionWatcher(self, stage, status, serverMsg):
        self.connectionStatusCallbacks(stage, status, serverMsg)

    def __connectionStatusCallback(self, stage, status, serverMsg):
        self.__rawStatus = status
        if stage == 0:
            pass
        elif stage == 1:
            if status != 'LOGGED_ON':
                self.__setConnectionStatus(CONNECTION_STATUS.disconnected)
        elif stage == 2:
            self.__setConnectionStatus(CONNECTION_STATUS.connected)
            self.onConnected()
        elif stage == 6:
            self.__setConnectionStatus(CONNECTION_STATUS.disconnected)
            self.onDisconnected()
        else:
            LOG_UNEXPECTED('stage:%d, status:%s, serverMsg:%s' % (stage, status, serverMsg))

    def __setConnectionStatus(self, status):
        self.__connectionStatus = status

    def isDisconnected(self):
        return self.__connectionStatus != CONNECTION_STATUS.connected

    def isUpdateClientSoftwareNeeded(self):
        return self.__rawStatus in ('LOGIN_BAD_PROTOCOL_VERSION', 'LOGIN_REJECTED_BAD_DIGEST')


def _getClientUpdateUrl():
    import Settings
    updateUrl = Settings.g_instance.scriptConfig.readString(Settings.KEY_UPDATE_URL)
    return updateUrl


connectionManager = ConnectionManager.instance()
