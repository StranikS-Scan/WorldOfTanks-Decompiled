# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/Manager.py
import pickle
import time
import typing
import logging
import BigWorld
import LGC
import Settings
import constants
from account_helpers.settings_core.settings_constants import GAME
from connection_mgr import CONNECTION_METHOD
from Preferences import Preferences
from Servers import Servers, DevelopmentServers
from debug_utils import LOG_DEBUG
from gui import SystemMessages, makeHtmlString, GUI_SETTINGS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_MINUTE
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_ENABLED, AUTO_LOGIN_QUERY_URL
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from soft_exception import SoftException
from gui.Scaleform.Waiting import Waiting
from Event import Event
from PlayerEvents import g_playerEvents
from connection_mgr import LOGIN_STATUS
_PERIPHERY_DEFAULT_LIFETIME = 15 * ONE_MINUTE
_LIMIT_LOGIN_COUNT = 5
_logger = logging.getLogger(__name__)

class Manager(ILoginManager):
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self._preferences = None
        self.__servers = None
        self.__lgcPublication = constants.LGC_PUBLICATION.LGC_UNKNOWN
        self.__lgcManager = None
        self.__triedToInitLGC = False
        self.onConnectionInitiated = Event()
        self.onConnectionRejected = Event()
        return

    @property
    def lgcAvailable(self):
        return self.__lgcManager is not None

    def getLgcPublication(self):
        return self.__lgcPublication

    @property
    def isLgcSteam(self):
        return self.__lgcPublication == constants.LGC_PUBLICATION.LGC_STEAM

    def init(self):
        if LGC.prepare():
            publication = LGC.getPublication()
            self.__lgcPublication = constants.LGC_PUBLICATION.LGC_BASE if constants.LGC_PUBLICATION.LGC_PC == publication else publication
        else:
            _logger.error('LGC API initialization failed')
        self.tryPrepareLGCLogin()
        self._preferences = Preferences()
        if constants.IS_DEVELOPMENT:
            self.__servers = DevelopmentServers(self._preferences)
        else:
            self.__servers = Servers(self._preferences)
        self.connectionMgr.onLoggedOn += self._onLoggedOn
        g_clientUpdateManager.addCallbacks({'serverSettings.periphery_routing_config': self.__onServerSettingsChanged})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.connectionMgr.onLoggedOn -= self._onLoggedOn
        self.connectionMgr.onRejected -= self._onRejected
        self._preferences = None
        self.__servers.fini()
        self.__servers = None
        self.stopLgc()
        self.onConnectionInitiated.clear()
        self.onConnectionRejected.clear()
        return

    def initiateLogin(self, email, password, serverName, isSocialToken2Login, rememberUser):
        self.onConnectionInitiated()
        self.connectionMgr.onRejected += self._onRejected
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
         'auth_method': authMethod,
         'publication': str(self.__lgcPublication)}
        if isToken2Login:
            loginParams['token2'] = self._preferences['token2']
        if not isSocialToken2Login:
            self._preferences['login_type'] = 'credentials'
        self.connectionMgr.initiateConnection(loginParams, password, serverName)
        self.connectionMgr.setLastLogin(email)

    def initiateRelogin(self, login, token2, serverName):
        self.onConnectionInitiated()
        self.connectionMgr.onRejected += self._onRejected
        self._preferences['server_name'] = serverName
        if self.lgcAvailable:
            self.__lgcManager.relogin(token2, serverName)
        else:
            loginParams = {'login': login,
             'token2': token2,
             'session': BigWorld.wg_cpsalt(self._preferences['session']),
             'temporary': str(int(not self._preferences['remember_user'])),
             'auth_method': CONNECTION_METHOD.TOKEN2}
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
        serverName = self._preferences['server_name']
        serverSelect = self.settingsCore.getSetting(GAME.LOGIN_SERVER_SELECTION)
        if self.lgcAvailable and self.__lgcManager.onLoggedOn(responseData):
            self._preferences.clear()
            self._preferences['server_name'] = serverName
            self._preferences['server_select_was_set'] = serverSelect
            self._preferences.writeLoginInfo()
            self.__lgcManager.onRejected -= self._onRejected
            self.__lgcManager.onInitiated -= self._onLGCInitiated
            return
        loginCount = self._preferences.get('loginCount', 0)
        self._preferences['loginCount'] = 1 if loginCount >= _LIMIT_LOGIN_COUNT else loginCount + 1
        if self._preferences['remember_user']:
            self._preferences['name'] = name
            self._preferences['token2'] = token2
        else:
            email = self._preferences['login']
            session = self._preferences['session']
            loginCount = self._preferences['loginCount']
            self._preferences.clear()
            if not constants.IS_SINGAPORE and not GUI_SETTINGS.igrCredentialsReset:
                self._preferences['login'] = email
            self._preferences['server_name'] = serverName
            self._preferences['session'] = session
            self._preferences['loginCount'] = loginCount
        self._preferences['server_select_was_set'] = serverSelect
        self._preferences.writeLoginInfo()
        self.__dumpUserName(name)
        self._showSecurityMessage(responseData)
        self.connectionMgr.onRejected -= self._onRejected

    def _onLGCInitiated(self, *_):
        self.onConnectionInitiated()

    def _onRejected(self, *_):
        self.onConnectionRejected()

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

    def addOnLgcErrorListener(self, listener):
        if self.lgcAvailable:
            self.__lgcManager.onLgcError += listener
        else:
            _logger.warning('Try to addOnLgcErrorListener while LGC is not available')

    def removeOnLgcErrorListener(self, listener):
        if self.lgcAvailable:
            self.__lgcManager.onLgcError -= listener
        else:
            _logger.warning('Try to removeOnLgcErrorListener while LGC is not available')

    def tryLgcLogin(self, serverName=None):
        if not self.lgcAvailable:
            _logger.warning('LGC is not available, no possibility to login via it, so return')
            return
        else:
            if serverName is None:
                selectedServer = self.__servers.selectedServer
                if not selectedServer:
                    _logger.warning('No server was selected when LGC connect happened, so return')
                    return
                serverName = selectedServer['data']
            else:
                self._preferences['server_name'] = serverName
            self.__lgcManager.onRejected += self._onRejected
            self.__lgcManager.onInitiated += self._onLGCInitiated
            hostName = self._getHost(CONNECTION_METHOD.TOKEN, serverName)
            self.__lgcManager.login(hostName)
            return

    def stopLgc(self):
        if self.lgcAvailable:
            self.__lgcManager.onRejected -= self._onRejected
            self.__lgcManager.onInitiated -= self._onLGCInitiated
            self.__lgcManager.destroy()
            self.__lgcManager = None
        return

    def tryPrepareLGCLogin(self):
        if self.lgcAvailable:
            if not LGC.prepareLogin():
                self.stopLgc()
                LGC.printLastError()
        elif not self.__triedToInitLGC:
            if LGC.prepareLogin():
                self.__lgcManager = _LgcModeManager()
            else:
                LGC.printLastError()
        self.__triedToInitLGC = True

    def checkLgcCouldRetry(self, status):
        return self.__lgcManager.checkLgcCouldRetry(status) if self.lgcAvailable else False

    def __onServerSettingsChanged(self, diff):
        if 'isEnabled' in diff and not diff['isEnabled']:
            self.connectionMgr.setPeripheryRoutingGroup(None, None)
            return
        else:
            if 'peripheryRoutingGroups' in diff:
                self.connectionMgr.setPeripheryRoutingGroup(self.connectionMgr.peripheryRoutingGroup, diff['peripheryRoutingGroups'].get(self.connectionMgr.peripheryRoutingGroup))
            return


class _LgcModeManager(object):
    connectionMgr = dependency.descriptor(IConnectionManager)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.onLgcError = Event()
        self.__token2ToStore = None
        self.__selectedServer = None
        g_playerEvents.onAccountShowGUI += self.__onAccountDone
        self.connectionMgr.onRejected += self.__onRejected
        self.connectionMgr.onDisconnected += self.__onDisconnected
        self.onInitiated = Event()
        self.onRejected = Event()
        return

    def destroy(self):
        g_playerEvents.onAccountShowGUI -= self.__onAccountDone
        self.connectionMgr.onRejected -= self.__onRejected
        self.connectionMgr.onDisconnected -= self.__onDisconnected
        self.onRejected.clear()

    def login(self, selectedServer):
        self.__selectedServer = selectedServer
        self.__lobbyContext.setAccountComplete(LGC.isAccountComplete())
        self.onInitiated()
        LGC.prepareToken()
        Waiting.show('login')
        self.__lgcCheck()

    def relogin(self, token2, selectedServer):
        self.__selectedServer = selectedServer
        loginParams = LGC.loginData()
        loginParams['token2'] = token2
        loginParams['auth_method'] = CONNECTION_METHOD.TOKEN2
        loginParams['auth_realm'] = constants.AUTH_REALM
        self.connectionMgr.initiateConnection(loginParams, '', selectedServer)

    def checkLgcCouldRetry(self, status):
        return self.connectionMgr.connectionMethod == CONNECTION_METHOD.TOKEN2 and (status == LOGIN_STATUS.SESSION_END or status == LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD)

    def onLoggedOn(self, responseData):
        self.__token2ToStore = responseData['token2']
        if LGC.processingState() == constants.LGC_STATE.LOGIN_IN_PROGRESS:
            LGC.onServerResponse(True)
            return True
        return False

    def __lgcCheck(self):
        state = LGC.processingState()
        if state == constants.LGC_STATE.WAITING_TOKEN_1:
            BigWorld.callback(0.0, self.__lgcCheck)
        elif state == constants.LGC_STATE.LOGIN_IN_PROGRESS:
            self.__lgcConnect()
        else:
            LGC.printLastError()
            Waiting.hide('login')
            self.onRejected()
            self.onLgcError()

    def __lgcConnect(self):
        if self.__selectedServer is not None:
            state = LGC.processingState()
            if state == constants.LGC_STATE.LOGIN_IN_PROGRESS:
                loginParams = LGC.loginData()
                if loginParams is not None:
                    self.connectionMgr.initiateConnection(loginParams, '', self.__selectedServer)
                    self.connectionMgr.setLastLogin('')
                    return
                _logger.warning('No login params for LGC login, so return')
            else:
                _logger.warning('Could not login via LGC because wrong processingState (%d), so return', state)
        else:
            _logger.warning('No server was selected when LGC connect happened, so return')
        Waiting.hide('login')
        self.onRejected()
        return

    def __onRejected(self, status, _):
        Waiting.hide('login')
        if self.checkLgcCouldRetry(status):
            LGC.onToken2Expired()
            self.login(self.__selectedServer)
        else:
            LGC.onServerResponse(False)
            self.onRejected()

    def __onDisconnected(self):
        LGC.onServerResponse(False)

    def __onAccountDone(self, *args):
        if self.__token2ToStore:
            if LGC.processingState() == constants.LGC_STATE.LOGGEDIN and LGC.getUserId() == BigWorld.player().databaseID:
                LGC.storeToken2(self.__token2ToStore, BigWorld.player().databaseID)
            self.__token2ToStore = None
        return
