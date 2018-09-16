# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/Manager.py
import pickle
import time
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
_PERIPHERY_DEFAULT_LIFETIME = 15 * ONE_MINUTE

class Manager(ILoginManager):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self._preferences = None
        self.__servers = None
        return

    def init(self):
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
        return

    def initiateLogin(self, email, password, serverName, isSocialToken2Login, rememberUser):
        isWgcLogin = BigWorld.WGC_processingState() == constants.WGC_STATE.LOGIN_IN_PROGRESS
        if not isWgcLogin:
            isToken2Login = isSocialToken2Login or self._preferences['token2']
            if isToken2Login:
                authMethod = CONNECTION_METHOD.TOKEN2
            else:
                authMethod = CONNECTION_METHOD.BASIC
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
        else:
            loginParams = BigWorld.WGC_loginData()
            if loginParams is None:
                return
            authMethod = loginParams.get('auth_method', None)
            if authMethod is None:
                return
            serverName = self._getHost(authMethod, serverName)
        self.connectionMgr.initiateConnection(loginParams, password, serverName)
        self.connectionMgr.setLastLogin(email)
        return

    def initiateRelogin(self, login, token2, serverName):
        loginParams = None
        if login == 'wgc':
            if not BigWorld.WGC_prepareLogin():
                return
            loginParams = BigWorld.WGC_loginData()
        if loginParams is None:
            loginParams = {'login': login,
             'token2': token2,
             'session': BigWorld.wg_cpsalt(self._preferences['session']),
             'temporary': str(int(not self._preferences['remember_user'])),
             'auth_method': CONNECTION_METHOD.TOKEN2}
        self._preferences['server_name'] = serverName
        self.connectionMgr.initiateConnection(loginParams, '', serverName)
        return

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
        if BigWorld.WGC_processingState() == constants.WGC_STATE.LOGGEDIN:
            BigWorld.WGC_storeToken2(responseData['token2'])
        else:
            self.lobbyContext.setCredentials(name, token2)
            if self._preferences['remember_user']:
                self._preferences['name'] = name
                self._preferences['token2'] = token2
                if 'server_name' in self._preferences and AUTO_LOGIN_QUERY_ENABLED:
                    del self._preferences['server_name']
            else:
                email = self._preferences['login']
                serverName = self._preferences['server_name']
                session = self._preferences['session']
                self._preferences.clear()
                if not constants.IS_SINGAPORE and not GUI_SETTINGS.igrCredentialsReset:
                    self._preferences['login'] = email
                if not AUTO_LOGIN_QUERY_ENABLED:
                    self._preferences['server_name'] = serverName
                self._preferences['session'] = session
            self._preferences.writeLoginInfo()
            self.__dumpUserName(name)
        self._showSecurityMessage(responseData)

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

    def _getHost(self, authMethod, hostName):
        if hostName != AUTO_LOGIN_QUERY_URL:
            return hostName
        else:
            pickledData = self._preferences['peripheryLifetime']
            if pickledData:
                try:
                    peripheryID, expirationTimestamp = pickle.loads(pickledData)
                except:
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
        """ Dump user name to the preferences.xml (required by WGLeague's anti-cheat).
        
        See WOTD-55587. This method doesn't belong to Preferences class, so it's placed here.
        """
        Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].writeString('user', name)
        Settings.g_instance.save()
