# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/Manager.py
import pickle
import time
import logging
import BigWorld
import Settings
import constants
from connection_mgr import CONNECTION_METHOD
from Preferences import Preferences
from Servers import Servers, DevelopmentServers
from debug_utils import LOG_DEBUG
from gui import SystemMessages, makeHtmlString, GUI_SETTINGS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_MINUTE
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_ENABLED, AUTO_LOGIN_QUERY_URL
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from soft_exception import SoftException
from gui.Scaleform.Waiting import Waiting
from Event import Event
from PlayerEvents import g_playerEvents
from connection_mgr import LOGIN_STATUS
from gui.server_events.recruit_helper import NonRecruitNotifierSingleton
_PERIPHERY_DEFAULT_LIFETIME = 15 * ONE_MINUTE
_LIMIT_LOGIN_COUNT = 5
_logger = logging.getLogger(__name__)

class Manager(ILoginManager):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self._preferences = None
        self.__servers = None
        self.__wgcManager = None
        self.__triedToInitWGC = False
        return

    @property
    def wgcAvailable(self):
        return self.__wgcManager is not None

    def init(self):
        self.tryPrepareWGCLogin()
        self._preferences = Preferences()
        if constants.IS_DEVELOPMENT:
            self.__servers = DevelopmentServers(self._preferences)
        else:
            self.__servers = Servers(self._preferences)
        self.connectionMgr.onLoggedOn += self._onLoggedOn

    def fini(self):
        self.connectionMgr.onLoggedOn -= self._onLoggedOn
        self._preferences = None
        self.__servers.fini()
        self.__servers = None
        self.stopWgc()
        return

    def initiateLogin(self, email, password, serverName, isSocialToken2Login, rememberUser):
        isToken2Login = isSocialToken2Login or self._preferences['token2']
        authMethod = CONNECTION_METHOD.TOKEN2 if isToken2Login else CONNECTION_METHOD.BASIC
        serverName = self._getHost(authMethod, serverName)
        self._preferences['session'] = BigWorld.wg_cpsalt(self._preferences['session'])
        self._preferences['password_length'] = len(password)
        self._preferences['remember_user'] = rememberUser
        self._preferences['login'] = email
        self._preferences['server_name'] = serverName
        loginParams = {'login': self._preferences['login'],
         'session': self._preferences['session'],
         'temporary': str(int(not rememberUser)),
         'auth_method': authMethod}
        if isToken2Login:
            loginParams['token2'] = self._preferences['token2']
        if not isSocialToken2Login:
            self._preferences['login_type'] = 'credentials'
        self.connectionMgr.initiateConnection(loginParams, password, serverName)
        self.connectionMgr.setLastLogin(email)

    def initiateRelogin(self, login, token2, serverName):
        if self.wgcAvailable:
            self.__wgcManager.relogin(token2, serverName)
        else:
            loginParams = {'login': login,
             'token2': token2,
             'session': BigWorld.wg_cpsalt(self._preferences['session']),
             'temporary': str(int(not self._preferences['remember_user'])),
             'auth_method': CONNECTION_METHOD.TOKEN2}
            self._preferences['server_name'] = serverName
            self.connectionMgr.initiateConnection(loginParams, '', serverName)

    def getPreference(self, key):
        return self._preferences[key]

    def clearPreferences(self):
        self._preferences.clear()

    def clearToken2Preference(self):
        self._preferences['token2'] = ''

    def writePreferences(self):
        self._preferences.writeLoginInfo()

    @property
    def servers(self):
        return self.__servers

    def _onLoggedOn(self, responseData):
        name = responseData.get('name', 'UNKNOWN')
        token2 = responseData.get('token2', '')
        self.lobbyContext.setCredentials(name, token2)
        if self.wgcAvailable and self.__wgcManager.onLoggedOn(responseData):
            self._preferences.clear()
            self._preferences.writeLoginInfo()
            return
        loginCount = self._preferences.get('loginCount', 0)
        self._preferences['loginCount'] = 1 if loginCount >= _LIMIT_LOGIN_COUNT else loginCount + 1
        if self._preferences['remember_user']:
            self._preferences['name'] = name
            self._preferences['token2'] = token2
            if 'server_name' in self._preferences and AUTO_LOGIN_QUERY_ENABLED:
                del self._preferences['server_name']
        else:
            email = self._preferences['login']
            serverName = self._preferences['server_name']
            session = self._preferences['session']
            loginCount = self._preferences['loginCount']
            self._preferences.clear()
            if not constants.IS_SINGAPORE and not GUI_SETTINGS.igrCredentialsReset:
                self._preferences['login'] = email
            if not AUTO_LOGIN_QUERY_ENABLED:
                self._preferences['server_name'] = serverName
            self._preferences['session'] = session
            self._preferences['loginCount'] = loginCount
        self._preferences.writeLoginInfo()
        self.__dumpUserName(name)
        self._showSecurityMessage(responseData)
        NonRecruitNotifierSingleton().getInstance().resetFirstShowState()

    def _showSecurityMessage(self, responseData):
        securityWarningType = responseData.get('security_msg')
        if securityWarningType is not None:
            securityLink = ''
            if not GUI_SETTINGS.isEmpty('securitySettingsURL'):
                securityLink = makeHtmlString('html_templates:lobby/system_messages', 'link', {'text': _ms(SYSTEM_MESSAGES.SECURITYMESSAGE_CHANGE_SETINGS),
                 'linkType': 'securityLink'})
            SystemMessages.pushI18nMessage('#system_messages:securityMessage/%s' % securityWarningType, type=SystemMessages.SM_TYPE.Warning, link=securityLink)
        return

    def writePeripheryLifetime(self):
        if AUTO_LOGIN_QUERY_ENABLED and self.connectionMgr.peripheryID:
            self._preferences['peripheryLifetime'] = pickle.dumps((self.connectionMgr.peripheryID, time.time() + _PERIPHERY_DEFAULT_LIFETIME))
            self._preferences.writeLoginInfo()

    @staticmethod
    def getAvailableSocialNetworks():
        raise SoftException('This method should not be reached in this context')

    def initiateSocialLogin(self, socialNetworkName, serverName, rememberUser, isRegistration):
        raise SoftException('This method should not be reached in this context')

    def _getHost(self, authMethod, hostName):
        if hostName != AUTO_LOGIN_QUERY_URL:
            return hostName
        else:
            pickledData = self._preferences['peripheryLifetime']
            if pickledData:
                try:
                    peripheryID, expirationTimestamp = pickle.loads(pickledData)
                except Exception:
                    LOG_DEBUG("Couldn't to read pickled periphery data. Connecting to {0}.".format(hostName))
                    return hostName

                if expirationTimestamp > time.time():
                    host = g_preDefinedHosts.periphery(peripheryID, False)
                    if host is None:
                        return hostName
                    if authMethod != CONNECTION_METHOD.BASIC and host.urlToken:
                        return host.urlToken
                    return host.url
            return hostName

    def __dumpUserName(self, name):
        Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].writeString('user', name)
        Settings.g_instance.save()

    def addOnWgcErrorListener(self, listener):
        if self.wgcAvailable:
            self.__wgcManager.onWgcError += listener
        else:
            _logger.warning('Try to addOnWgcErrorListener while WGC is not available')

    def removeOnWgcErrorListener(self, listener):
        if self.wgcAvailable:
            self.__wgcManager.onWgcError -= listener
        else:
            _logger.warning('Try to removeOnWgcErrorListener while WGC is not available')

    def tryWgcLogin(self, serverName=None):
        if not self.wgcAvailable:
            _logger.warning('WGC is not available, no possibility to login via it, so return')
            return
        else:
            if serverName is None:
                selectedServer = self.__servers.selectedServer
                if not selectedServer:
                    _logger.warning('No server was selected when WGC connect happened, so return')
                    return
                serverName = selectedServer['data']
            hostName = self._getHost(CONNECTION_METHOD.TOKEN, serverName)
            self.__wgcManager.login(hostName)
            return

    def stopWgc(self):
        if self.wgcAvailable:
            self.__wgcManager.destroy()
            self.__wgcManager = None
        return

    def tryPrepareWGCLogin(self):
        if self.wgcAvailable:
            if not BigWorld.WGC_prepareLogin():
                self.stopWgc()
        elif not self.__triedToInitWGC:
            if BigWorld.WGC_prepareLogin():
                self.__wgcManager = _WgcModeManager()
        self.__triedToInitWGC = True

    def checkWgcCouldRetry(self, status):
        return self.__wgcManager.checkWgcCouldRetry(status) if self.wgcAvailable else False


class _WgcModeManager(object):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self.onWgcError = Event()
        self.__token2ToStore = None
        self.__selectedServer = None
        g_playerEvents.onAccountShowGUI += self.__onAccountDone
        self.connectionMgr.onRejected += self.__onRejected
        self.connectionMgr.onDisconnected += self.__onDisconnected
        return

    def destroy(self):
        g_playerEvents.onAccountShowGUI -= self.__onAccountDone
        self.connectionMgr.onRejected -= self.__onRejected
        self.connectionMgr.onDisconnected -= self.__onDisconnected

    def login(self, selectedServer):
        self.__selectedServer = selectedServer
        BigWorld.WGC_prepareToken()
        Waiting.show('login')
        self.__wgcCheck()

    def relogin(self, token2, selectedServer):
        self.__selectedServer = selectedServer
        loginParams = BigWorld.WGC_loginData()
        loginParams['token2'] = token2
        loginParams['auth_method'] = CONNECTION_METHOD.TOKEN2
        loginParams['auth_realm'] = constants.AUTH_REALM
        self.connectionMgr.initiateConnection(loginParams, '', selectedServer)

    def checkWgcCouldRetry(self, status):
        return self.connectionMgr.connectionMethod == CONNECTION_METHOD.TOKEN2 and (status == LOGIN_STATUS.SESSION_END or status == LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD)

    def onLoggedOn(self, responseData):
        self.__token2ToStore = responseData['token2']
        if BigWorld.WGC_processingState() == constants.WGC_STATE.LOGIN_IN_PROGRESS:
            BigWorld.WGC_onServerResponse(True)
            return True
        return False

    def __wgcCheck(self):
        state = BigWorld.WGC_processingState()
        if state == constants.WGC_STATE.WAITING_TOKEN_1:
            BigWorld.callback(0.0, self.__wgcCheck)
        elif state == constants.WGC_STATE.LOGIN_IN_PROGRESS:
            self.__wgcConnect()
        else:
            BigWorld.WGC_printLastError()
            Waiting.hide('login')
            self.onWgcError()

    def __wgcConnect(self):
        if self.__selectedServer is not None:
            state = BigWorld.WGC_processingState()
            if state == constants.WGC_STATE.LOGIN_IN_PROGRESS:
                loginParams = BigWorld.WGC_loginData()
                if loginParams is not None:
                    self.connectionMgr.initiateConnection(loginParams, '', self.__selectedServer)
                    self.connectionMgr.setLastLogin('')
                    return
                _logger.warning('No login params for WGC login, so return')
            else:
                _logger.warning('Could not login via WGC because wrong WGC_processingState (%d), so return', state)
        else:
            _logger.warning('No server was selected when WGC connect happened, so return')
        Waiting.hide('login')
        return

    def __onRejected(self, status, _):
        if self.checkWgcCouldRetry(status):
            BigWorld.WGC_onToken2Expired()
            self.login(self.__selectedServer)
        else:
            BigWorld.WGC_onServerResponse(False)

    def __onDisconnected(self):
        BigWorld.WGC_onServerResponse(False)

    def __onAccountDone(self, *args):
        if self.__token2ToStore:
            if BigWorld.WGC_processingState() == constants.WGC_STATE.LOGGEDIN and BigWorld.WGC_getUserId() == BigWorld.player().databaseID:
                BigWorld.WGC_storeToken2(self.__token2ToStore, BigWorld.player().databaseID)
            self.__token2ToStore = None
        return
