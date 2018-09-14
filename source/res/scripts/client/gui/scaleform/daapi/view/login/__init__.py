# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/__init__.py
import random
import sys
import BigWorld
import MusicController
import ResMgr
import Settings
import constants
from adisp import process
from ConnectionManager import connectionManager
from debug_utils import LOG_DEBUG
from external_strings_utils import _ACCOUNT_NAME_MIN_LENGTH_REG
from gui import GUI_SETTINGS, DialogsInterface, makeHtmlString
from gui.battle_control import g_sessionProvider
from gui.Scaleform import SCALEFORM_WALLPAPER_PATH
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LoginPageMeta import LoginPageMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.login.EULADispatcher import EULADispatcher
from gui.Scaleform.daapi.view.login.LoginDispatcher import LoginDispatcher
from gui.Scaleform.Waiting import Waiting
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.events import LoginEvent, LoginEventEx, HideWindowEvent
from gui.shared.events import ArgsEvent, OpenLinkEvent
from helpers import i18n, getFullClientVersion
from gui.Scaleform.locale.WAITING import WAITING
from gui.Scaleform.locale.MENU import MENU
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_URL, AUTO_LOGIN_QUERY_ENABLED, REQUEST_RATE, HOST_AVAILABILITY
from gui.social_network_login.Bridge import bridge as socialNetworkLoginBridge

class LoginView(View, LoginPageMeta, AppRef):

    def __init__(self, ctx = None):
        super(LoginView, self).__init__(ctx=None)
        self.__onLoadCallback = ctx.get('callback')
        self.__loginDispatcher = LoginDispatcher()
        self.__onLoginQueue = False
        self.__capsLockState = None
        self.__lang = None
        self.__autoSearchVisited = False
        self.__lastSelectedServer = None
        self.__enableInputsCbId = None
        self.__showLoginWallpaperNode = 'showLoginWallpaper'
        if GUI_SETTINGS.socialNetworkLogin['enabled']:
            if not Settings.g_instance.userPrefs.has_key(Settings.KEY_LOGIN_INFO):
                Settings.g_instance.userPrefs.write(Settings.KEY_LOGIN_INFO, '')
            self.__loginPreferences = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO]
            self.__rememberMe = self.__loginPreferences.readBool('rememberPwd', False)
            self.__lastLoginType = self.__loginPreferences.readString('lastLoginType', 'basic')
            self.__loginHost = None
            self.__processingLoginBySocial = False
            self.__tokenLoginParams = {}
            self.__socialNetworkLogin = socialNetworkLoginBridge
            self.__socialNetworkLogin.init(self.__onServerReceivedData, GUI_SETTINGS.socialNetworkLogin['encryptToken'])
        return

    def _populate(self):
        super(LoginView, self)._populate()
        if self.__onLoadCallback is not None:
            self.__onLoadCallback()
        self.__setupDispatcherHandlers(True)
        self.__loginDispatcher.create()
        self.__enableInputsIfModalViewsNotExisting()
        self.__loadVersion()
        self.__setCopyright()
        Waiting.close()
        MusicController.g_musicController.stopAmbient()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOGIN)
        self.__loadRandomBgImage()
        if constants.IS_DEVELOPMENT:
            try:
                tmp_fil = open('GUIUnitTest.ut', 'r')
                if tmp_fil.readline().strip() != '':
                    tmp_fil.close()
                    sys.path.append('../../gui_unit_test/scripts')
                    import GUIUnitTest
                else:
                    tmp_fil.close()
            except IOError:
                pass

        self.__capsLockCallback = BigWorld.callback(0.1, self.__checkUserInputState)
        g_sessionProvider.getCtx().lastArenaUniqueID = None
        if self.app.cursorMgr is not None:
            self.app.cursorMgr.attachCursor(True)
        self.__showRequiredLoginScreen()
        return

    def _dispose(self):
        self.__setupDispatcherHandlers(False)
        self.__onLoadCallback = None
        self.__loginDispatcher.destroy()
        self.__loginDispatcher = None
        self.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, self.__onLoginQueueSwitched, EVENT_BUS_SCOPE.LOBBY)
        self.__lastSelectedServer = None
        if self.__capsLockCallback is not None:
            BigWorld.cancelCallback(self.__capsLockCallback)
            self.__capsLockCallback = None
        if GUI_SETTINGS.socialNetworkLogin['enabled']:
            self.__socialNetworkLogin.fini()
        super(LoginView, self)._dispose()
        return

    def onSetStatus(self, newStatus, statusCode):
        self.__setStatus(newStatus, statusCode)

    def onLoginAppFailed(self, status, message):
        self.__createAnAccountResponse(True, '')

    def onSetOptions(self, optionsList, host):
        options = []
        selectedId = 0
        if self.__lastSelectedServer is None:
            searchForHost = AUTO_LOGIN_QUERY_URL if AUTO_LOGIN_QUERY_ENABLED else host
        else:
            searchForHost = self.__lastSelectedServer
        for idx, (key, name, csisStatus, peripheryID) in enumerate(optionsList):
            if key == searchForHost:
                selectedId = idx
                if csisStatus == HOST_AVAILABILITY.NOT_AVAILABLE and AUTO_LOGIN_QUERY_ENABLED:
                    selectedId = 0
            options.append({'label': name,
             'data': key,
             'csisStatus': csisStatus})

        self.as_setServersListS(options, selectedId)
        return

    def onAfterAutoLoginTimerClearing(self, host, clearInFlash):
        urls = g_preDefinedHosts.urlIterator(host)
        if urls is not None:
            urls.resume()
        self.__minOrderInQueue = 18446744073709551615L
        if clearInFlash:
            self.fireEvent(LoginEvent(LoginEvent.CANCEL_LGN_QUEUE, View.alias))
        return

    def onCancelQueue(self, showWaiting, logged):
        self.cancelQueue(showWaiting, logged)

    @process
    def onHandleUpdateClientSoftwareNeeded(self):
        success = yield DialogsInterface.showI18nConfirmDialog('updateNeeded')
        if success and not BigWorld.wg_quitAndStartLauncher():
            self.__setStatus(i18n.convert(i18n.makeString(MENU.LOGIN_STATUS_LAUNCHERNOTFOUND)), 0)

    def onHandleLoginRejectedRateLimited(self, message):
        self.__setAutoLogin(WAITING.TITLES_QUEUE, message, WAITING.BUTTONS_EXITQUEUE)

    def onHandleActivating(self, message):
        self.__setAutoLogin(WAITING.TITLES_REGISTERING, message, WAITING.BUTTONS_EXIT)

    def __setAutoLogin(self, waitingOpen, message, waitingClose):
        Waiting.hide('login')
        if not self.__onLoginQueue:
            self.__setLoginQueue(True)
            self.fireEvent(LoginEventEx(LoginEventEx.SET_AUTO_LOGIN, View.alias, waitingOpen, message, waitingClose, False), EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)

    def __onLoginQueueClosed(self, evnet):
        self.__closeLoginQueue()

    def __onLoginQueueSwitched(self, evnet):
        self.__closeLoginQueue()
        self.as_switchToAutoAndSubmitS(AUTO_LOGIN_QUERY_URL)

    def __closeLoginQueue(self):
        self.__loginDispatcher.onExitFromAutoLogin()
        self.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, self.__onLoginQueueSwitched, EVENT_BUS_SCOPE.LOBBY)
        self.__setLoginQueue(False)
        self.__setStatus('', 0)

    def onHandleAutoRegisterInvalidPass(self):
        self.__createAnAccountResponse(False, MENU.LOGIN_STATUS_LOGIN_REJECTED_NICKNAME_ALREADY_EXIST)

    def onHandleAutoRegisterActivating(self):
        self.__createAnAccountResponse(True, '')
        Waiting.hide('login')

    def onHandleAutoLoginQueryFailed(self, message):
        self.__setAutoLogin(WAITING.TITLES_AUTO_LOGIN_QUERY_FAILED, message, WAITING.BUTTONS_CEASE)

    def onDoAutoLogin(self):
        lastLoginType = 'basic'
        if GUI_SETTINGS.socialNetworkLogin['enabled']:
            lastLoginType = self.__lastLoginType
        if lastLoginType != 'basic':
            self.__socialNetworkLogin.makeToken2LoginParams(self.__tokenLoginParams)
            if AUTO_LOGIN_QUERY_URL == self.__loginHost:
                g_preDefinedHosts.autoLoginQuery(self.__connectToHost)
            else:
                self.__connectToHost(g_preDefinedHosts.byUrl(self.__loginHost))
        else:
            LOG_DEBUG('onDoAutoLogin')
            self.as_doAutoLoginS()

    def onAccountNameIsInvalid(self):
        self.__createAnAccountResponse(False, MENU.LOGIN_STATUS_INVALID_NICKNAME)

    def onNicknameTooSmall(self):
        self.__createAnAccountResponse(False, i18n.makeString(MENU.LOGIN_STATUS_INVALID_LOGIN_LENGTH) % {'count': _ACCOUNT_NAME_MIN_LENGTH_REG})

    def onHandleAutoRegisterJSONParsingFailed(self):
        self.__createAnAccountResponse(False, MENU.LOGIN_STATUS_LOGIN_REJECTED_UNABLE_TO_PARSE_JSON)

    def onHandleKickWhileLogin(self, messageType, message):
        self.__setAutoLogin(WAITING.titles(messageType), message, WAITING.BUTTONS_CEASE)

    def onHandleQueue(self, serverName, queueNumber):
        showAutoSearchBtn = AUTO_LOGIN_QUERY_ENABLED and not self.__autoSearchVisited
        cancelBtnLbl = WAITING.BUTTONS_CANCEL if showAutoSearchBtn else WAITING.BUTTONS_EXITQUEUE
        message = i18n.makeString(WAITING.MESSAGE_QUEUE, serverName, queueNumber)
        if showAutoSearchBtn:
            message = i18n.makeString(WAITING.MESSAGE_USEAUTOSEARCH, serverName, queueNumber, serverName)
        if not self.__onLoginQueue:
            Waiting.close()
            self.__setLoginQueue(True)
            self.fireEvent(LoginEventEx(LoginEventEx.SET_LOGIN_QUEUE, View.alias, WAITING.TITLES_QUEUE, message, cancelBtnLbl, showAutoSearchBtn), EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, self.__onLoginQueueSwitched, EVENT_BUS_SCOPE.LOBBY)
        else:
            ctx = {'title': WAITING.TITLES_QUEUE,
             'message': message,
             'cancelLabel': cancelBtnLbl,
             'showAutoLoginBtn': showAutoSearchBtn}
            self.fireEvent(ArgsEvent(ArgsEvent.UPDATE_ARGS, VIEW_ALIAS.LOGIN_QUEUE, ctx), EVENT_BUS_SCOPE.LOBBY)

    def onConfigLoaded(self, user, password, rememberPwd, isRememberPwd):
        if GUI_SETTINGS.socialNetworkLogin['enabled']:
            user = user if self.__lastLoginType == 'basic' else ''
        self.as_setDefaultValuesS(user, password, rememberPwd, isRememberPwd, GUI_SETTINGS.igrCredentialsReset, not GUI_SETTINGS.isEmpty('recoveryPswdURL'))

    def onHandleInvalidPasswordWithToken(self, user, rememberPwd):
        self.__showRequiredLoginScreen()
        self.as_setDefaultValuesS(user, '', rememberPwd, GUI_SETTINGS.rememberPassVisible, GUI_SETTINGS.igrCredentialsReset, not GUI_SETTINGS.isEmpty('recoveryPswdURL'))

    def startListenCsisUpdate(self, startListen):
        self.__loginDispatcher.startListenCsisQuery(startListen)

    def isCSISUpdateOnRequest(self):
        return GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ON_REQUEST

    def saveLastSelectedServer(self, server):
        self.__lastSelectedServer = server

    def showLegal(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LEGAL_INFO_WINDOW))

    def isPwdInvalid(self, password):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not self.__loginDispatcher.isToken():
            from external_strings_utils import isPasswordValid
            isInvalid = not isPasswordValid(password)
        return isInvalid

    def isLoginInvalid(self, login):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not self.__loginDispatcher.isToken():
            from external_strings_utils import isAccountLoginValid
            isInvalid = not isAccountLoginValid(login)
        return isInvalid

    def onTextLinkClick(self, socialNetworkName):
        BigWorld.wg_openWebBrowser(self.__socialNetworkLogin.getSocialNetworkURL(socialNetworkName))

    def changeAccount(self):
        self.__rememberMe = False
        self.as_setDefaultValuesS('', '', False, GUI_SETTINGS.rememberPassVisible, GUI_SETTINGS.igrCredentialsReset, not GUI_SETTINGS.isEmpty('recoveryPswdURL'))
        self.__showRequiredLoginScreen()
        self.as_setErrorMessageS(self.__socialNetworkLogin.getLogoutWarning(self.__lastLoginType), 0)
        self.__loginPreferences.writeString('login', '')
        self.__loginPreferences.writeBool('rememberPwd', False)
        self.__loginPreferences.writeString('lastLoginType', 'basic')
        self.__loginPreferences.writeString('token2', '')
        self.__loginPreferences.writeString('user', '')

    def onRegister(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.REGISTRATION))

    def onRecovery(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.RECOVERY_PASSWORD))

    def onSetRememberPassword(self, remember):
        self.__rememberMe = remember
        self.__loginDispatcher.setRememberPwd(remember)

    def onExitFromAutoLogin(self):
        self.__loginDispatcher.onExitFromAutoLogin()

    def isToken(self):
        return self.__loginDispatcher.isToken()

    def resetToken(self):
        LOG_DEBUG('Token has been invalidated')
        self.__loginDispatcher.resetToken()

    def onEscape(self):
        DialogsInterface.showI18nConfirmDialog('quit', self.__onConfirmClosed, focusedID=DIALOG_BUTTON_ID.CLOSE)

    def onLogin(self, user, password, host, isSocialToken2Login):
        if GUI_SETTINGS.socialNetworkLogin['enabled']:
            self.__loginHost = host
            connectionManager.onConnected += self.__onSocialLoginConnected
            if not isSocialToken2Login:
                self.__lastLoginType = 'basic'
        self.as_enableS(False)
        if host == AUTO_LOGIN_QUERY_URL:
            self.__autoSearchVisited = True
        else:
            self.__autoSearchVisited = False
        self.__loginDispatcher.onLogin(user, password, host, self.__onEndLoginTrying, isSocialToken2Login=isSocialToken2Login)
        self.fireEvent(events.HideWindowEvent(HideWindowEvent.HIDE_LEGAL_INFO_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def onLoginBySocial(self, socialNetworkName, host):
        self.__loginHost = host
        self.__lastLoginType = socialNetworkName
        if not self.__socialNetworkLogin.initiateLogin(socialNetworkName, self.__rememberMe):
            self.__setStatus(i18n.makeString('#menu:login/social/status/SYSTEM_ERROR'), 0)

    def __onServerReceivedData(self, token, spaID, tokenDecrypter):
        if self.__processingLoginBySocial:
            return None
        else:
            self.__processingLoginBySocial = True
            self.__tokenLoginParams = self.__socialNetworkLogin.getLoginParams()
            self.__tokenLoginParams['token'] = tokenDecrypter(token)
            self.__tokenLoginParams['account_id'] = spaID
            connectionManager.onConnected += self.__onSocialLoginConnected
            connectionManager.onRejected += self.__onSocialLoginRejected
            connectionManager.onDisconnected += self.__onSocialLoginDisconnected
            Waiting.show('login')
            if AUTO_LOGIN_QUERY_URL == self.__loginHost:
                g_preDefinedHosts.autoLoginQuery(self.__connectToHost)
            else:
                self.__connectToHost(g_preDefinedHosts.byUrl(self.__loginHost))
            BigWorld.wg_bringWindowToForeground()
            return None

    def __connectToHost(self, host):
        connectionManager.connect(host.urlToken, '', '', host.keyPath, isNeedSavingPwd=self.__rememberMe, tokenLoginParams=self.__tokenLoginParams)

    def __onSocialLoginConnected(self):
        self.__loginPreferences.writeBool('rememberPwd', self.__rememberMe)
        self.__loginPreferences.writeString('lastLoginType', self.__lastLoginType)
        self.__loginPreferences.writeString('host', self.__loginHost)
        connectionManager.onConnected -= self.__onSocialLoginConnected

    def __onSocialLoginRejected(self):
        self.__processingLoginBySocial = False
        connectionManager.onRejected -= self.__onSocialLoginRejected

    def __onSocialLoginDisconnected(self):
        self.__processingLoginBySocial = False
        connectionManager.onDisconnected -= self.__onSocialLoginDisconnected

    def __showRequiredLoginScreen(self):
        if GUI_SETTINGS.socialNetworkLogin['enabled']:
            socialList = self.__socialNetworkLogin.getAvailableSocialNetworks()
            socialDataList = []
            for socialId in socialList:
                item = {'socialId': socialId,
                 'tpHeader': self.__socialNetworkLogin.getTooltipHeader(socialId),
                 'tpBody': self.__socialNetworkLogin.getTooltipBody(socialId)}
                socialDataList.append(item)

            if self.__lastLoginType in socialList and self.__rememberMe:
                self.as_showSocialFormS(self.__loginDispatcher.isToken(), self.__loginPreferences.readString('user'), makeHtmlString('html_templates:socialNetworkLogin', 'transparentLogo', {'socialNetwork': self.__lastLoginType}), self.__lastLoginType)
            else:
                self.as_showSimpleFormS(True, socialDataList)
        else:
            self.as_showSimpleFormS(False, None)
        return

    def __onEULAClosed(self):
        self.__enableInputsIfModalViewsNotExisting()

    def __onEndLoginTrying(self):
        self.__enableInputsIfModalViewsNotExisting()

    def __enableInputsIfModalViewsNotExisting(self):
        if not self.app.containerManager.isModalViewsIsExists():
            if self.__enableInputsCbId is not None:
                BigWorld.cancelCallback(self.__enableInputsCbId)
                self.__enableInputsCbId = None
            self.as_enableS(True)
        else:
            self.__enableInputsCbId = BigWorld.callback(0.5, self.__enableInputsIfModalViewsNotExisting)
        return

    def __onConfirmClosed(self, isOk):
        if isOk:
            self.destroy()
            BigWorld.quit()

    def __checkUserInputState(self):
        caps = BigWorld.wg_isCapsLockOn()
        if self.__capsLockState != caps:
            self.__capsLockState = caps
            self.__setCapsLockState(self.__capsLockState)
        lang = BigWorld.wg_getLangCode()
        if self.__lang != lang:
            self.__lang = lang
            self.__setKeyboardLand(self.__lang)
        self.__capsLockCallback = BigWorld.callback(0.1, self.__checkUserInputState)

    def __setCapsLockState(self, isActive):
        self.as_setCapsLockStateS(isActive)

    def __setKeyboardLand(self, lang):
        self.as_setKeyboardLangS(lang)

    def __loadVersion(self):
        self.as_setVersionS(getFullClientVersion())

    def __setCopyright(self):
        copyStr = i18n.makeString(MENU.COPY)
        legalStr = i18n.makeString(MENU.LEGAL)
        self.as_setCopyrightS(copyStr, legalStr)

    def __setStatus(self, status, statusCode):
        self.as_setErrorMessageS(status, statusCode)
        Waiting.close()

    def __createAnAccountResponse(self, success, errorMsg):
        self.fireEvent(LoginEvent(LoginEvent.CLOSE_CREATE_AN_ACCOUNT, View.alias, success, errorMsg))

    def __loadRandomBgImage(self):
        wallpapperSettings = self.__readUserPreferenceLogin()
        wallpaperFiles = self.__getWallpapersList()
        BG_IMAGES_PATH = '../maps/login/%s.png'
        if wallpapperSettings['show'] and len(wallpaperFiles) > 0:
            if len(wallpaperFiles) == 1:
                newFile = wallpaperFiles[0]
            else:
                newFile = ''
                while True:
                    newFile = random.choice(wallpaperFiles)
                    if newFile != wallpapperSettings['filename']:
                        break

            self.__saveUserPreferencesLogin(newFile)
            bgImage = BG_IMAGES_PATH % newFile
        else:
            bgImage = BG_IMAGES_PATH % '__login_bg'
            wallpapperSettings['show'] = False
        self.as_showWallpaperS(wallpapperSettings['show'], bgImage)

    @staticmethod
    def __getWallpapersList():
        result = []
        ds = ResMgr.openSection(SCALEFORM_WALLPAPER_PATH)
        for filename in ds.keys():
            if filename[-4:] == '.png' and filename[0:2] != '__':
                result.append(filename[0:-4])

        return result

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

    def cancelQueue(self, showWaiting = True, logged = False):
        if self.__onLoginQueue:
            if showWaiting:
                Waiting.show('enter')
            self.__setLoginQueue(False)
        self.fireEvent(LoginEvent(LoginEvent.CANCEL_LGN_QUEUE, View.alias))

    def __setupDispatcherHandlers(self, setup):
        for methodName in LoginDispatcher.EVENTS:
            handler = getattr(self, methodName)
            event = getattr(self.__loginDispatcher, methodName)
            if setup:
                event += handler
            else:
                event -= handler

    def __setLoginQueue(self, value):
        self.__onLoginQueue = value
