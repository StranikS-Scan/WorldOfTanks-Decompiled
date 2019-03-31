# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Login.py
# Compiled at: 2019-03-19 22:43:51
import json
import BigWorld
import ResMgr
import MusicController
import Settings
import constants
from ConnectionManager import connectionManager
from PlayerEvents import g_playerEvents
from account_helpers.SteamAccount import g_steamAccount
from constants import IS_DEVELOPMENT
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_ERROR
from external_strings_utils import isAccountLoginValid, isPasswordValid, _LOGIN_NAME_MIN_LENGTH, _PASSWORD_MAX_LENGTH
from gui import VERSION_FILE_PATH, GUI_REMEMBER_PASS_VISIBLE, GUI_CLEAR_LOGIN_VALUE
from gui.BattleContext import g_battleContext
from gui.Scaleform.Disconnect import Disconnect
from gui.Scaleform.EULA import EULAInterface
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.windows import UIInterface
from helpers import i18n
from helpers.links import openMigrationWebsite
from helpers.obfuscators import PasswordObfuscator
from helpers.time_utils import makeLocalServerTime
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_URL

class Login(UIInterface):
    IS_FIRST_RUN = True
    __APPLICATION_CLOSE_DELAY_DEFAULT = 15
    DEFAULT_PASS_LENGTH = 10
    AUTO_LOGIN_QUERY_TIMEOUT = 5

    def __init__(self):
        self.__user = ''
        self.__host = ''
        self.__pass = ''
        self.__token2 = ''
        self.__passLength = 0
        self.__rememberPwd = False
        self.__closeCallbackId = None
        self.__eula = EULAInterface()
        self.__loginQueue = False
        self.__kickedFromServer = False
        self.__capsLockState = None
        self.__capsLockCallback = None
        self.__showLoginWallpaperNode = 'showLoginWallpaper'
        UIInterface.__init__(self)
        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.movie.backgroundAlpha = 1.0
        use_wgc = not ResMgr.isFile('../ignore_wgc')
        if not constants.IS_DEVELOPMENT and use_wgc:
            self.uiHolder.call('login.showWGCAlert', [])
        self.uiHolder.addExternalCallbacks({'login.Login': self.onLogin,
         'login.OpenWGC': self.onOpenWGC,
         'login.SetRememberPassword': self.onSetRememberPassword,
         'login.ExitFromAutoLogin': self.onExitFromAutoLogin,
         'login.EULAClose': self.steamLogin,
         'login.ConfirmUpdate': self.doUpdate})
        self.__loadUserConfig()
        g_preDefinedHosts.readScriptConfig(Settings.g_instance.scriptConfig)
        connectionManager.connectionStatusCallbacks += self.__handleConnectionStatus
        connectionManager.onConnected += self.__onConnected
        connectionManager.searchServersCallbacks += self.__serversFind
        connectionManager.startSearchServers()
        connectionManager.onDisconnected -= Disconnect.show
        Disconnect.hide()
        self.setOptions(g_preDefinedHosts.shortList())
        self.__loadVersion()
        g_playerEvents.onLoginQueueNumberReceived += self.onQueue
        g_playerEvents.onAccountBecomePlayer += self.__pe_onAccountBecomePlayer
        g_playerEvents.onKickWhileLoginReceived += self.handleKickWhileLogin
        Waiting.hide('loadPage')
        Waiting.close()
        MusicController.g_musicController.stopAmbient()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOGIN)
        self.__eula.populateUI(proxy)
        self.uiHolder.call('login.ShowLicense', [self.__eula.isShowLicense()])
        self.uiHolder.call('login.isSteam', [g_steamAccount.isValid])
        if not self.__eula.isShowLicense():
            self.steamLogin()
        self.__checkCapsLockState()
        g_battleContext.lastArenaUniqueID = None
        if use_wgc and BigWorld.WGC_prepareLogin():
            self.__tryWGCLogin()
        return

    def dispossessUI(self):
        if self.__capsLockCallback is not None:
            BigWorld.cancelCallback(self.__capsLockCallback)
            self.__capsLockCallback = None
        connectionManager.connectionStatusCallbacks -= self.__handleConnectionStatus
        connectionManager.onConnected -= self.__onConnected
        connectionManager.stopSearchServers()
        connectionManager.searchServersCallbacks -= self.__serversFind
        connectionManager.onDisconnected += Disconnect.show
        g_playerEvents.onLoginQueueNumberReceived -= self.onQueue
        g_playerEvents.onAccountBecomePlayer -= self.__pe_onAccountBecomePlayer
        g_playerEvents.onKickWhileLoginReceived -= self.handleKickWhileLogin
        self.uiHolder.removeExternalCallbacks('login.Login', 'login.OpenWGC', 'login.SetRememberPassword', 'login.ExitFromAutoLogin', 'login.EULAClose', 'login.ConfirmUpdate', 'login.tryCreateAnAccount')
        self.__eula.dispossessUI()
        UIInterface.dispossessUI(self)
        return

    def __loadVersion(self):
        sec = ResMgr.openSection(VERSION_FILE_PATH)
        version = i18n.makeString(sec.readString('appname')) + ' ' + sec.readString('version')
        self.call('Login.SetVersion', [version])

    def isToken(self):
        return len(self.__token2) > 0

    def resetToken(self):
        LOG_DEBUG('Token has been invalidated')
        self.__passLength = 0
        self.__token2 = ''

    def __loadUserConfig(self):
        LOG_DEBUG('__loadUserConfig')
        ds = self.__getUserLoginSection()
        password = ''
        self.__rememberPwd = False
        if GUI_REMEMBER_PASS_VISIBLE:
            self.__rememberPwd = ds.readBool('rememberPwd', False)
        if ds:
            if GUI_CLEAR_LOGIN_VALUE:
                ds.writeString('user', '')
                ds.writeString('login', '')
            self.__user = self.__getUserLoginName(ds)
            self.__host = ds.readString('host')
            decrypt = getattr(BigWorld, 'wg_ucpdata', None)
            if 'password' in ds.keys():
                password = ds.readString('password')
                decrypt = PasswordObfuscator().unobfuscate
            else:
                password = ds.readString('pwd')
            if not GUI_REMEMBER_PASS_VISIBLE:
                self.__rememberPwd = False
                password = ''
            elif password and 'rememberPwd' not in ds.keys():
                self.__rememberPwd = True
            else:
                self.__rememberPwd = ds.readBool('rememberPwd', False)
            if self.__rememberPwd and decrypt is not None:
                try:
                    password = decrypt(password)
                except (TypeError, AttributeError):
                    LOG_CURRENT_EXCEPTION()

            if 'token2' in ds.keys():
                token2 = ds.readString('token2')
                LOG_DEBUG('__loadUserConfig: token2: ', token2)
                if len(token2):
                    separatorPos = token2.find(':')
                    if separatorPos > 0:
                        try:
                            self.__passLength = int(token2[:separatorPos])
                        except ValueError:
                            self.__passLength = self.DEFAULT_PASS_LENGTH

                        self.__passLength = min(self.__passLength, _PASSWORD_MAX_LENGTH)
                        self.__token2 = token2[separatorPos + 1:]
                        password = '*' * self.__passLength
                    else:
                        self.__token2 = ''
        self.call('login.setDefaultValues', [self.__user, password, self.__rememberPwd])
        return

    @staticmethod
    def __getUserLoginSection():
        up = Settings.g_instance.userPrefs
        if up.has_key(Settings.KEY_LOGIN_INFO):
            return up[Settings.KEY_LOGIN_INFO]
        else:
            return up.write(Settings.KEY_LOGIN_INFO, '')

    @staticmethod
    def __getUserLoginName(loginInfoSection):
        userLogin = ''
        if 'user' in loginInfoSection.keys():
            userLogin = loginInfoSection.readString('user', '')
        elif 'login' in loginInfoSection.keys():
            userLogin = BigWorld.wg_ucpdata(loginInfoSection.readString('login', ''))
        return userLogin

    def __saveUserConfig(self, user, rememberPwd, host):
        li = self.__getUserLoginSection()
        if not g_steamAccount.isValid:
            li.writeString('login', BigWorld.wg_cpdata(user) if not GUI_CLEAR_LOGIN_VALUE else '')
            if 'user' in li.keys():
                li.deleteSection('user')
            li.writeBool('rememberPwd', rememberPwd if GUI_REMEMBER_PASS_VISIBLE else False)
        li.writeString('host', host)
        self.__saveUserToken(self.__passLength, self.__token2)
        Settings.g_instance.save()

    def __saveUserToken(self, passwordLength, token2):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO]
        if GUI_REMEMBER_PASS_VISIBLE:
            rememberPwd = ds.readBool('rememberPwd', False)
            li = self.__getUserLoginSection()
            if len(token2):
                token2 = '%d:%s' % (passwordLength, token2)
            'pwd' in li.keys() and li.deleteSection('pwd')
        li.writeString('token2', token2 if rememberPwd else '')
        Settings.g_instance.save()

    def showCreateAnAccountDialog(self):
        self.call('login.ShowCreateAnAccount', ['#dialogs:createAnAccount/title', '#dialogs:createAnAccount/message', '#dialogs:createAnAccount/submit'])

    def __createAnAccountResponse(self, succcess, errorMsg):
        self.call('login.CreateAnAccountResponce', [succcess, errorMsg])

    def __checkCapsLockState(self):
        if self.__capsLockState != BigWorld.wg_isCapsLockOn():
            self.__capsLockState = BigWorld.wg_isCapsLockOn()
            self.__setCapsLockState(self.__capsLockState)
        self.__capsLockCallback = BigWorld.callback(0.1, self.__checkCapsLockState)

    def __setCapsLockState(self, isActive):
        self.call('login.setCapsLockState', [isActive])

    def __tryWGCLogin(self):
        if not BigWorld.WGC_prepareToken():
            return
        BigWorld.WGC_printLastError()
        if BigWorld.WGC_processingState() != constants.WGC_STATE.ERROR:
            Waiting.show('login')
            self.__wgcCheck()

    def __wgcCheck(self):
        if BigWorld.WGC_processingState() == constants.WGC_STATE.WAITING_TOKEN_1:
            BigWorld.callback(0.01, self.__wgcCheck)
        elif BigWorld.WGC_processingState() == constants.WGC_STATE.LOGIN_IN_PROGRESS:
            self.__wgcConnect()
        else:
            BigWorld.WGC_printLastError()
            Waiting.hide('login')

    def __wgcConnect(self):
        Waiting.hide('login')
        host = self.__host
        if not g_preDefinedHosts.predefined(host):
            host = g_preDefinedHosts.first().url
        self.doLogin('', '', host, isWgc=True)

    def __serversFind(self, servers=None):
        hostList = g_preDefinedHosts.shortList()
        if servers is not None:
            for name, key in servers:
                if not g_preDefinedHosts.predefined(key):
                    hostList.append((key, name))

        self.setOptions(hostList)
        return

    def __handleConnectionStatus(self, stage, status, serverMsg):
        LOG_DEBUG('__handleConnectionStatus', stage, status, serverMsg)
        if stage == 1:
            handlerFunc = None
            if status == 'LOGGED_ON':
                handlerFunc = self.__logOnSuccess[status]
            else:
                handlerFunc = self.__logOnFailedHandlers.get(status, self.__logOnFailedDefaultHandler)
                if status != 'LOGIN_REJECTED_LOGIN_QUEUE':
                    self.__clearAutoLoginTimer()
                if status != 'LOGIN_REJECTED_RATE_LIMITED':
                    self.__resetLgTimeout()
                self.cancelQueue(showWaiting=False)
                g_preDefinedHosts.clearPeripheryTL()
            try:
                getattr(self, handlerFunc)(status, serverMsg)
            except:
                LOG_ERROR('Handle logon status error: status = %r, message = %r' % (status, serverMsg))
                LOG_CURRENT_EXCEPTION()
                Waiting.hide('login')

            if connectionManager.isUpdateClientSoftwareNeeded():
                self.__handleUpdateClientSoftwareNeeded()
            elif status != 'LOGGED_ON':
                connectionManager.disconnect()
        elif stage == 6:
            if not self.__kickedFromServer:
                self.cancelQueue(showWaiting=False)
            self.__setStatus(i18n.convert(i18n.makeString('#menu:login/status/disconnected')))
            connectionManager.disconnect()
        BigWorld.WGC_onServerResponse(False)
        return

    def __onConnected(self):
        BigWorld.WGC_onServerResponse(True)
        Waiting.hide('login')
        self.__loginQueue = False
        LOG_DEBUG('onConnected')

        def iCallback():
            BigWorld.disconnect()
            BigWorld.clearEntitiesAndSpaces()
            from gui.WindowsManager import g_windowsManager
            g_windowsManager.showLogin()
            Waiting.close()

        Waiting.show('enter', interruptCallback=iCallback)

    def __handleUpdateClientSoftwareNeeded(self):
        self.call('login.updateNeeded', [])

    def doUpdate(self, _):
        if not BigWorld.wg_quitAndStartLauncher():
            self.__setStatus(i18n.convert(i18n.makeString('#menu:login/status/launchernotfound')))

    def __handleMigrationNeeded(self):
        if not IS_DEVELOPMENT:
            self.__closeCallbackId = BigWorld.callback(self.__getApplicationCloseDelay(), BigWorld.quit)
            try:
                openMigrationWebsite(self.__user)
            except Exception:
                LOG_CURRENT_EXCEPTION()

    @staticmethod
    def __getApplicationCloseDelay():
        prefs = Settings.g_instance.userPrefs
        if prefs is None:
            delay = Login.__APPLICATION_CLOSE_DELAY_DEFAULT
        else:
            if not prefs.has_key(Settings.APPLICATION_CLOSE_DELAY):
                prefs.writeInt(Settings.APPLICATION_CLOSE_DELAY, Login.__APPLICATION_CLOSE_DELAY_DEFAULT)
            delay = prefs.readInt(Settings.APPLICATION_CLOSE_DELAY)
        return delay

    def setOptions(self, optionsList):
        options = [0]
        for i, (key, name) in enumerate(optionsList):
            if key == self.__host:
                options[0] = i
            options.append(name)
            options.append(key)

        self.call('login.setServersList', options)

    def __setStatus(self, status):
        self.call('login.setErrorMessage', [status])
        Waiting.close()

    __isAutoLoginTimerSet = False
    __isAutoLoginShow = False
    __autoLoginTimerID = None

    def __setAutoLoginTimer(self, time):
        if self.__isAutoLoginTimerSet:
            return
        self.__isAutoLoginTimerSet = True
        LOG_DEBUG('__setAutoLoginTimer', time)
        self.__isAutoLoginShow = True
        if time > 0:
            self.__autoLoginTimerID = BigWorld.callback(time, self.__doAutoLogin)
        else:
            self.__doAutoLogin()

    def __clearAutoLoginTimer(self, clearInFlash=True):
        if self.__isAutoLoginTimerSet:
            LOG_DEBUG('__clearAutoLoginTimer')
            if self.__autoLoginTimerID is not None:
                BigWorld.cancelCallback(self.__autoLoginTimerID)
                self.__autoLoginTimerID = None
            self.__isAutoLoginTimerSet = False
        if self.__isAutoLoginShow:
            urls = g_preDefinedHosts.urlIterator(self.__host)
            if urls is not None:
                urls.resume()
            self.__minOrderInQueue = 18446744073709551615L
            if clearInFlash:
                self.call('login.clearAutoLogin')
            self.__isAutoLoginShow = False
        return

    def __doAutoLogin(self):
        LOG_DEBUG('__doAutoLogin')
        self.__isAutoLoginTimerSet = False
        self.__autoLoginTimerID = None
        self.call('login.doAutoLogin', [])
        return

    def onExitFromAutoLogin(self, *args):
        self.__clearAutoLoginTimer(clearInFlash=False)
        self.__resetLgTimeout()
        g_preDefinedHosts.resetQueryResult()

    __lg_Timeout = 0
    __lg_maxTimeout = 20
    __lg_increment = 5

    def __getLgNextTimeout(self):
        self.__lg_Timeout = min(self.__lg_maxTimeout, self.__lg_Timeout + self.__lg_increment)
        return self.__lg_Timeout

    def __resetLgTimeout(self):
        self.__lg_Timeout = 0

    __logOnFailedHandlers = {'LOGIN_REJECTED_BAN': 'handleLoginRejectedBan',
     'LOGIN_CUSTOM_DEFINED_ERROR': 'handleLoginRejectedBan',
     'LOGIN_REJECTED_RATE_LIMITED': 'handleLoginRejectedRateLimited',
     'LOGIN_REJECTED_USERS_LIMIT': 'handleLoginRejectedUsersLimited',
     'LOGIN_REJECTED_LOGINS_NOT_ALLOWED': 'handleLoginAppFailed',
     'LOGIN_REJECTED_BASEAPP_TIMEOUT': 'handleLoginAppFailed',
     'CONNECTION_FAILED': 'handleLoginAppFailed',
     'DNS_LOOKUP_FAILED': 'handleLoginAppFailed',
     'LOGIN_REJECTED_NOT_REGISTERED': 'handleNotRegistered',
     'LOGIN_REJECTED_ACTIVATING': 'handleActivating',
     'LOGIN_REJECTED_INVALID_PASSWORD': 'handleInvalidPassword'}
    __logAutoRegisterHandlers = {'LOGIN_REJECTED_INVALID_PASSWORD': 'handleAutoRegisterInvalidPass',
     'LOGIN_REJECTED_UNABLE_TO_PARSE_JSON': 'handleAutoRegisterJSONParsingFailed',
     'LOGIN_REJECTED_ACTIVATING': 'handleAutoRegisterActivating'}
    __logOnSuccess = {'LOGGED_ON': 'handleLogOnSuccess'}
    __logOnFailedDefaultHandler = 'handleLogOnFailed'
    __minOrderInQueue = 18446744073709551615L

    def handleLogOnFailed(self, status, _):
        status = status or 'UNKNOWN_ERROR'
        errorMessage = i18n.makeString('#menu:login/status/' + status)
        self.__setStatus(errorMessage)

    def handleInvalidPassword(self, status, message):
        errorMessage = i18n.makeString('#menu:login/status/' + status)
        if len(self.__token2):
            self.resetToken()
            self.call('login.setDefaultValues', [self.__user,
             '',
             self.__rememberPwd,
             GUI_REMEMBER_PASS_VISIBLE])
            errorMessage = i18n.makeString('#menu:login/status/SESSION_END')
        self.__setStatus(errorMessage)

    def handleLogOnSuccess(self, status, message):
        try:
            LOG_DEBUG('handleLogOnSuccess', message)
            if not len(message):
                return
            msg_dict = json.loads(message)
            if not isinstance(msg_dict, dict):
                raise Exception, ''
        except Exception:
            self.handleLoginCustomDefinedError(status, message)
            LOG_CURRENT_EXCEPTION()
            return

        token2 = str(msg_dict.get('token2', ''))
        if token2:
            BigWorld.WGC_storeToken2(token2, BigWorld.WGC_getUserId())
        self.__saveUserToken(self.__passLength, str(msg_dict.get('token2', '')))

    def handleAutoRegisterInvalidPass(self, status, message):
        self.__createAnAccountResponse(False, '#menu:login/status/LOGIN_REJECTED_NICKNAME_ALREADY_EXIST')
        Waiting.close()

    def handleAutoRegisterJSONParsingFailed(self, status, message):
        self.__createAnAccountResponse(False, '#menu:login/status/LOGIN_REJECTED_UNABLE_TO_PARSE_JSON')
        Waiting.close()

    def handleActivating(self, status, message):
        message = i18n.makeString('#waiting:message/auto_login_activating')
        self.call('login.setAutoLogin', ['#waiting:titles/registering', message, '#waiting:buttons/exit'])
        self.__setAutoLoginTimer(self.__getLgNextTimeout())

    def handleAutoRegisterActivating(self, status, message):
        self.__createAnAccountResponse(True, '')
        Waiting.hide('login')
        self.handleActivating(status, message)

    def handleNotRegistered(self, status, message):
        if constants.IS_VIETNAM:
            self.showCreateAnAccountDialog()
        Waiting.close()

    def handleLoginRejectedBan(self, status, message):
        try:
            LOG_DEBUG('handleLoginRejectedBan', message)
            msg_dict = json.loads(message)
            if not isinstance(msg_dict, dict):
                self.handleLoginCustomDefinedError(status, message)
                return
            self.__token2 = msg_dict.get('token2', '')
            self.__saveUserToken(self.__passLength, self.__token2)
            json_dict = msg_dict.get('bans')
            msg_dict = json.loads(json_dict)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            self.handleLoginCustomDefinedError(status, message)
            return

        if isinstance(msg_dict, dict):
            expiryTime = int(msg_dict.get('expiryTime', 0))
            reason = msg_dict.get('reason', '').encode('utf-8')
        if reason == '#ban_reason:china_migration':
            self.__handleMigrationNeeded()
        if reason.startswith('#'):
            reason = i18n.makeString(reason)
        if expiryTime > 0:
            expiryTime = makeLocalServerTime(expiryTime)
            expiryTime = ' '.join((BigWorld.wg_getLongDateFormat(expiryTime), BigWorld.wg_getLongTimeFormat(expiryTime)))
            errorMessage = i18n.makeString('#menu:login/status/LOGIN_REJECTED_BAN', time=expiryTime, reason=reason)
        else:
            errorMessage = i18n.makeString('#menu:login/status/LOGIN_REJECTED_BAN_UNLIMITED', reason=reason)
        self.__setStatus(errorMessage)

    def onQueue(self, queueNumber):
        if not self.__loginQueue:
            Waiting.close()
            self.__loginQueue = True
        message = i18n.makeString('#waiting:message/queue', connectionManager.serverUserName, BigWorld.wg_getIntegralFormat(queueNumber))
        self.call('login.setLoginQueue', ['#waiting:titles/queue', message, '#waiting:buttons/exitQueue'])

    def cancelQueue(self, showWaiting=True, logged=False):
        if self.__loginQueue:
            if showWaiting:
                Waiting.show('enter')
            self.__loginQueue = False
        self.call('login.cancelLoginQueue', [logged])

    def __pe_onAccountBecomePlayer(self):
        self.cancelQueue(logged=True)

    def handleLoginCustomDefinedError(self, _, message):
        errorMessage = i18n.makeString('#menu:login/status/LOGIN_CUSTOM_DEFINED_ERROR', message)
        self.__setStatus(errorMessage)

    def handleLoginRejectedRateLimited(self, status, message):
        errorMessage = i18n.makeString('#menu:login/status/LOGIN_REJECTED_RATE_LIMITED')
        self.__setStatus(errorMessage)
        urls = g_preDefinedHosts.urlIterator(self.__host)
        if urls is not None and urls.end():
            urls.cursor = 0
        message = i18n.makeString('#waiting:message/autoLogin', connectionManager.serverUserName)
        self.call('login.setAutoLogin', ['#waiting:titles/queue', message, '#waiting:buttons/exitQueue'])
        self.__setAutoLoginTimer(self.__getLgNextTimeout())
        return

    def handleKickWhileLogin(self, peripheryID):
        g_preDefinedHosts.savePeripheryTL(peripheryID)
        self.__kickedFromServer = True
        messageType = 'another_periphery' if peripheryID else 'checkout_error'
        errorMessage = i18n.makeString('#system_messages:%s' % messageType)
        self.__setStatus(errorMessage)
        urls = g_preDefinedHosts.urlIterator(self.__host)
        if urls is not None and urls.end():
            urls.cursor = 0
        message = i18n.makeString('#waiting:message/%s' % messageType, connectionManager.serverUserName)
        self.call('login.setAutoLogin', ['#waiting:titles/%s' % messageType, message, '#waiting:buttons/cease'])
        self.__setAutoLoginTimer(self.__getLgNextTimeout())
        return

    def handleLoginRejectedUsersLimited(self, status, message):
        errorMessage = i18n.makeString('#menu:login/status/LOGIN_REJECTED_USERS_LIMIT')
        self.__setStatus(errorMessage)

    def __loginToNextLoginApp(self):
        urls = g_preDefinedHosts.urlIterator(self.__host)
        result = False
        if urls is not None:
            result = not urls.end()
            if result:
                Waiting.hide('login')
                self.__setAutoLoginTimer(0)
            else:
                urls.cursor = 0
        return result

    def handleLoginAppFailed(self, status, message):
        if self.handleAutoLoginQueryFailed(status):
            return
        if not self.__loginToNextLoginApp():
            self.handleLogOnFailed(status, message)

    def handleAutoLoginQueryFailed(self, status):
        result = False
        if AUTO_LOGIN_QUERY_URL == self.__host:
            result = True
            Waiting.hide('login')
            self.call('login.setAutoLogin', ['#waiting:titles/auto_login_query_failed', i18n.makeString('#waiting:message/auto_login_query_failed', server=connectionManager.serverUserName, reason=i18n.makeString('#menu:login/status/{0:>s}'.format(status))), '#waiting:buttons/cease'])
            self.__setAutoLoginTimer(self.AUTO_LOGIN_QUERY_TIMEOUT)
        return result

    def steamLogin(self, callbackId=None):
        if Login.IS_FIRST_RUN and g_steamAccount.isValid:
            Login.IS_FIRST_RUN = False
            self.__loadUserConfig()
            host = self.__host
            if not g_preDefinedHosts.predefined(host):
                host = g_preDefinedHosts.first().url
            self.doLogin('', '', host)

    def __readUserPreferenceLogin(self):
        result = {'show': True,
         'filename': ''}
        userPrefs = Settings.g_instance.userPrefs
        ds = None
        if not userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            userPrefs.write(Settings.KEY_LOGINPAGE_PREFERENCES, '')
            self.__saveUserPreferencesLogin(result['filename'])
        else:
            ds = userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
            result['filename'] = ds.readString('lastLoginBgImage', '')
        if ds is None:
            ds = userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        if not ds.has_key(self.__showLoginWallpaperNode):
            self.__createNodeShowWallpaper()
        result['show'] = ds.readBool(self.__showLoginWallpaperNode, True)
        return result

    @staticmethod
    def __saveUserPreferencesLogin(filename):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeString('lastLoginBgImage', filename)

    def __createNodeShowWallpaper(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeBool(self.__showLoginWallpaperNode, True)

    def doLogin(self, user, password, host, isWgc=False):
        LOG_DEBUG('onLogin')
        self.__kickedFromServer = False
        if self.__closeCallbackId:
            BigWorld.cancelCallback(self.__closeCallbackId)
            self.__closeCallbackId = None
        if g_steamAccount.isValid:
            user, password = g_steamAccount.getCredentials()
        elif not isWgc:
            user = user.lower().strip()
            if len(user) < _LOGIN_NAME_MIN_LENGTH:
                self.__setStatus(i18n.makeString('#menu:login/status/invalid_login_length') % {'count': _LOGIN_NAME_MIN_LENGTH})
                return
            if not isAccountLoginValid(user) and not IS_DEVELOPMENT:
                self.__setStatus(i18n.makeString('#menu:login/status/invalid_login'))
                return
            password = password.strip()
            if not isPasswordValid(password) and not IS_DEVELOPMENT and not len(self.__token2):
                self.__setStatus(i18n.makeString('#menu:login/status/invalid_password'))
                return
        Waiting.show('login')
        self.__host = host
        self.__user = user
        self.__passLength = len(password)
        if constants.IS_VIETNAM:
            self.__pass = password
        self.__saveUserConfig(user, self.__rememberPwd, self.__host)
        if len(self.__token2):
            password = ''
        if AUTO_LOGIN_QUERY_URL == host:
            g_preDefinedHosts.autoLoginQuery(lambda host: connectionManager.connect(host.url, user, password, host.keyPath, nickName=None, token2=self.__token2))
            return
        else:
            host = g_preDefinedHosts.byUrl(host)
            urls = host.urlIterator
            if urls is not None:
                if urls.end():
                    urls.cursor = 0
                host = urls.next()
                LOG_DEBUG('Gets next LoginApp url:', host)
            connectionManager.connect(host.url, user, password, host.keyPath, nickName=None, token2=self.__token2)
            return

    def onOpenWGC(self, _):
        LOG_DEBUG('onOpenWGC')
        BigWorld.wg_quitAndStartLauncher()

    def onLogin(self, _, user, password, host):
        self.doLogin(user, password, host)

    def onSetRememberPassword(self, _, remember):
        self.__rememberPwd = bool(remember)
