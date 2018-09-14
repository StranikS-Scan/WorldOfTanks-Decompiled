# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LoginView.py
import json
import random
from collections import defaultdict, namedtuple
import BigWorld
import ResMgr
import Settings
import constants
import WWISE
from adisp import process
from gui import DialogsInterface, GUI_SETTINGS
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.battle_control import g_sessionProvider
from gui.Scaleform.Waiting import Waiting
from gui import Scaleform
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LoginPageMeta import LoginPageMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.BAN_REASON import BAN_REASON
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.WAITING import WAITING
from PlayerEvents import g_playerEvents
from ConnectionManager import connectionManager, LOGIN_STATUS
from gui.shared import events, g_eventBus
from gui.shared.events import OpenLinkEvent, LoginEventEx, ArgsEvent, LoginEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import getFullClientVersion
from helpers.i18n import makeString as _ms
from gui.login import g_loginManager
from helpers.time_utils import makeLocalServerTime
from predefined_hosts import AUTO_LOGIN_QUERY_URL, AUTO_LOGIN_QUERY_ENABLED, g_preDefinedHosts
from external_strings_utils import isAccountLoginValid, isPasswordValid, _PASSWORD_MIN_LENGTH, _PASSWORD_MAX_LENGTH
from external_strings_utils import _LOGIN_NAME_MIN_LENGTH
from helpers.statistics import g_statistics, HANGAR_LOADING_STATE

class INVALID_FIELDS:
    ALL_VALID = 0
    LOGIN_INVALID = 1
    PWD_INVALID = 2
    SERVER_INVALID = 4
    LOGIN_PWD_INVALID = LOGIN_INVALID | PWD_INVALID


_STATUS_TO_INVALID_FIELDS_MAPPING = defaultdict(lambda : INVALID_FIELDS.ALL_VALID, {LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD: INVALID_FIELDS.PWD_INVALID,
 LOGIN_STATUS.LOGIN_REJECTED_ILLEGAL_CHARACTERS: INVALID_FIELDS.LOGIN_PWD_INVALID,
 LOGIN_STATUS.LOGIN_REJECTED_SERVER_NOT_READY: INVALID_FIELDS.SERVER_INVALID,
 LOGIN_STATUS.SESSION_END: INVALID_FIELDS.PWD_INVALID})
_VIDEO_BG_MODE = 0
_WALLPAPER_BG_MODE = 1
_ValidateCredentialsResult = namedtuple('ValidateCredentialsResult', ('isValid', 'errorMessage', 'invalidFields'))

class LoginView(LoginPageMeta):

    def __init__(self, ctx=None):
        LoginPageMeta.__init__(self, ctx=ctx)
        self.__isListInitialized = False
        self.__loginRetryDialogShown = False
        self.__loginQueueDialogShown = False
        self.__capsLockState = None
        self.__lang = None
        self.__capsLockCallbackID = None
        self.__backgroundMode = _VIDEO_BG_MODE
        self.__isSoundMuted = False
        self.__customLoginStatus = None
        self._autoSearchVisited = False
        self._rememberUser = False
        g_loginManager.servers.updateServerList()
        self._servers = g_loginManager.servers
        return

    def onRegister(self, host):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.REGISTRATION))

    def onSetRememberPassword(self, rememberUser):
        self._rememberUser = rememberUser

    def onLogin(self, userName, password, serverName, isSocialToken2Login):
        g_statistics.noteHangarLoadingState(HANGAR_LOADING_STATE.LOGIN, True)
        self._autoSearchVisited = serverName == AUTO_LOGIN_QUERY_URL
        self.__customLoginStatus = None
        result = self.__validateCredentials(userName.lower().strip(), password.strip(), bool(g_loginManager.getPreference('token2')))
        if result.isValid:
            Waiting.show('login')
            g_loginManager.initiateLogin(userName, password, serverName, isSocialToken2Login, isSocialToken2Login or self._rememberUser)
        else:
            self.as_setErrorMessageS(result.errorMessage, result.invalidFields)
        return

    def resetToken(self):
        g_loginManager.clearToken2Preference()

    def showLegal(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LEGAL_INFO_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def isPwdInvalid(self, password):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not g_loginManager.getPreference('token2'):
            from external_strings_utils import isPasswordValid
            isInvalid = not isPasswordValid(password)
        return isInvalid

    def isLoginInvalid(self, login):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not g_loginManager.getPreference('token2'):
            from external_strings_utils import isAccountLoginValid
            isInvalid = not isAccountLoginValid(login)
        return isInvalid

    def onRecovery(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.RECOVERY_PASSWORD))

    def isToken(self):
        return bool(g_loginManager.getPreference('token2'))

    def onEscape(self):

        def buttonHandler(isOk):
            if isOk:
                self.destroy()
                BigWorld.quit()

        DialogsInterface.showI18nConfirmDialog('quit', buttonHandler, focusedID=DIALOG_BUTTON_ID.CLOSE)

    def startListenCsisUpdate(self, startListenCsis):
        g_loginManager.servers.startListenCsisQuery(startListenCsis)

    def onExitFromAutoLogin(self):
        pass

    def saveLastSelectedServer(self, server):
        pass

    def switchBgMode(self):
        if self.__backgroundMode == _VIDEO_BG_MODE:
            self.as_showLoginVideoS('video/_login.usm', self.__isSoundMuted)
            WWISE.WW_eventGlobalSync('loginscreen_music_resume')
        else:
            self._loadRandomBgImage()

    def musicFadeOut(self):
        if self.__backgroundMode == _VIDEO_BG_MODE:
            WWISE.WW_eventGlobalSync('loginscreen_music_pause')
            self.__backgroundMode = _WALLPAPER_BG_MODE
        else:
            WWISE.WW_eventGlobalSync('loginscreen_ambient_stop')
            self.__backgroundMode = _VIDEO_BG_MODE
        self.__saveLastBackgroundMode()

    def setMute(self, value):
        self.__isSoundMuted = value
        self.__saveLastMuteState()
        WWISE.WW_eventGlobalSync('loginscreen_mute' if self.__isSoundMuted else 'loginscreen_unmute')

    def onVideoLoaded(self):
        WWISE.WW_eventGlobalSync('loginscreen_music_start')
        if self.__isSoundMuted:
            WWISE.WW_eventGlobalSync('loginscreen_mute')

    def _populate(self):
        View._populate(self)
        self._serversDP = ServersDataProvider()
        self._serversDP.setFlashObject(self.as_getServersDPS())
        self.as_enableS(True)
        self._servers.onServersStatusChanged += self.__updateServersList
        connectionManager.onRejected += self._onLoginRejected
        connectionManager.onKickWhileLoginReceived += self._onKickedWhileLogin
        connectionManager.onQueued += self._onHandleQueue
        g_playerEvents.onAccountShowGUI += self._clearLoginView
        self.as_setVersionS(getFullClientVersion())
        self.as_setCopyrightS(_ms(MENU.COPY), _ms(MENU.LEGAL))
        if BigWorld.isLowProductivityPC():
            self._showOnlyStaticBackground()
        else:
            self._showBackground()
        if self.__capsLockCallbackID is None:
            self.__capsLockCallbackID = BigWorld.callback(0.1, self.__checkUserInputState)
        g_sessionProvider.getCtx().lastArenaUniqueID = None
        self._setData()
        self._showForm()
        return

    def _dispose(self):
        if self.__backgroundMode == _VIDEO_BG_MODE:
            WWISE.WW_eventGlobalSync('loginscreen_music_stop_longfade')
        else:
            WWISE.WW_eventGlobalSync('loginscreen_ambient_stop')
        if self.__capsLockCallbackID is not None:
            BigWorld.cancelCallback(self.__capsLockCallbackID)
            self.__capsLockCallbackID = None
        connectionManager.onRejected -= self._onLoginRejected
        connectionManager.onKickWhileLoginReceived -= self._onKickedWhileLogin
        connectionManager.onQueued -= self._onHandleQueue
        self._servers.onServersStatusChanged -= self.__updateServersList
        g_playerEvents.onAccountShowGUI -= self._clearLoginView
        self._serversDP.fini()
        self._serversDP = None
        View._dispose(self)
        return

    def _showForm(self):
        self.as_showSimpleFormS(False, None)
        return

    def _setData(self):
        self._rememberUser = g_loginManager.getPreference('remember_user')
        if self._rememberUser:
            password = '*' * g_loginManager.getPreference('password_length')
        else:
            password = ''
        if GUI_SETTINGS.clearLoginValue:
            login = password = ''
        else:
            login = g_loginManager.getPreference('login')
        self.as_setDefaultValuesS(login, password, self._rememberUser, GUI_SETTINGS.rememberPassVisible, GUI_SETTINGS.igrCredentialsReset, not GUI_SETTINGS.isEmpty('recoveryPswdURL'))
        self.__updateServersList()

    def _clearLoginView(self, *args):
        Waiting.hide('login')
        if self.__loginQueueDialogShown:
            self.__closeLoginQueueDialog()
        if self.__loginRetryDialogShown:
            self.__closeLoginRetryDialog()

    def _onKickedWhileLogin(self, peripheryID):
        if peripheryID >= 0:
            self.__customLoginStatus = 'another_periphery' if peripheryID else 'checkout_error'
            if not self.__loginRetryDialogShown:
                self.__showLoginRetryDialog({'waitingOpen': WAITING.titles(self.__customLoginStatus),
                 'waitingClose': WAITING.BUTTONS_CEASE,
                 'message': _ms(WAITING.message(self.__customLoginStatus), connectionManager.serverUserName)})
        elif peripheryID == -2:
            self.__customLoginStatus = 'centerRestart'
        elif peripheryID == -3:
            self.__customLoginStatus = 'versionMismatch'

    def _onHandleQueue(self, queueNumber):
        serverName = connectionManager.serverUserName
        showAutoSearchBtn = AUTO_LOGIN_QUERY_ENABLED and not self._autoSearchVisited
        cancelBtnLbl = WAITING.BUTTONS_CANCEL if showAutoSearchBtn else WAITING.BUTTONS_EXITQUEUE
        message = _ms(WAITING.MESSAGE_QUEUE, serverName, queueNumber)
        if showAutoSearchBtn:
            message = _ms(WAITING.MESSAGE_USEAUTOSEARCH, serverName, queueNumber, serverName)
        if not self.__loginQueueDialogShown:
            self._clearLoginView()
            self.__loginQueueDialogShown = True
            self.fireEvent(LoginEventEx(LoginEventEx.SET_LOGIN_QUEUE, View.alias, WAITING.TITLES_QUEUE, message, cancelBtnLbl, showAutoSearchBtn), EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self._onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, self._onLoginQueueSwitched, EVENT_BUS_SCOPE.LOBBY)
        else:
            ctx = {'title': WAITING.TITLES_QUEUE,
             'message': message,
             'cancelLabel': cancelBtnLbl,
             'showAutoLoginBtn': showAutoSearchBtn}
            self.fireEvent(ArgsEvent(ArgsEvent.UPDATE_ARGS, VIEW_ALIAS.LOGIN_QUEUE, ctx), EVENT_BUS_SCOPE.LOBBY)

    def _onLoginQueueClosed(self, event):
        self.__closeLoginQueueDialog()

    def _onLoginQueueSwitched(self, event):
        self.__closeLoginQueueDialog()
        self.as_switchToAutoAndSubmitS(AUTO_LOGIN_QUERY_URL)

    def _onLoginRejected(self, loginStatus, responseData):
        Waiting.hide('login')
        if loginStatus == LOGIN_STATUS.LOGIN_REJECTED_BAN:
            self.__loginRejectedBan(responseData)
        elif loginStatus == LOGIN_STATUS.LOGIN_REJECTED_RATE_LIMITED:
            self.__loginRejectedRateLimited()
        elif loginStatus in (LOGIN_STATUS.LOGIN_REJECTED_BAD_DIGEST, LOGIN_STATUS.LOGIN_BAD_PROTOCOL_VERSION):
            self.__loginRejectedUpdateNeeded()
        elif loginStatus == LOGIN_STATUS.NOT_SET and self.__customLoginStatus is not None:
            self.__loginRejectedWithCustomState()
        else:
            self.as_setErrorMessageS(_ms('#menu:login/status/' + loginStatus), _STATUS_TO_INVALID_FIELDS_MAPPING[loginStatus])
            self.__clearFields(_STATUS_TO_INVALID_FIELDS_MAPPING[loginStatus])
        self._dropLoginQueue(loginStatus)
        return

    def _dropLoginQueue(self, loginStatus):
        """Safely drop login queue considering login status and current state of login queue.
        """
        if loginStatus != LOGIN_STATUS.LOGIN_REJECTED_RATE_LIMITED and self.__loginRetryDialogShown:
            self.__closeLoginQueueDialog()

    def _showOnlyStaticBackground(self):
        self._loadLastMuteState()
        self._loadRandomBgImage(False)

    def _showBackground(self):
        self.__loadLastBackgroundMode()
        self._loadLastMuteState()
        if self.__backgroundMode == _WALLPAPER_BG_MODE:
            self._loadRandomBgImage()
        else:
            self.as_showLoginVideoS('video/_login.usm', self.__isSoundMuted)

    def _loadRandomBgImage(self, showSwitchButton=True):
        wallpaperSettings = self.__loadLastBackgroundImage()
        wallpaperFiles = self.__getWallpapersList()
        BG_IMAGES_PATH = '../maps/login/%s.png'
        if wallpaperSettings['show'] and len(wallpaperFiles) > 0:
            if len(wallpaperFiles) == 1:
                newFile = wallpaperFiles[0]
            else:
                newFile = ''
                while True:
                    newFile = random.choice(wallpaperFiles)
                    if newFile != wallpaperSettings['filename']:
                        break

            self.__saveLastBackgroundImage(newFile)
            bgImage = BG_IMAGES_PATH % newFile
        else:
            bgImage = BG_IMAGES_PATH % '__login_bg'
            wallpaperSettings['show'] = False
        WWISE.WW_eventGlobalSync('loginscreen_ambient_start')
        if self.__isSoundMuted:
            WWISE.WW_eventGlobalSync('loginscreen_mute')
        self.as_showWallpaperS(wallpaperSettings['show'], bgImage, showSwitchButton, self.__isSoundMuted)

    def __clearFields(self, invalidField):
        if invalidField == INVALID_FIELDS.PWD_INVALID:
            self.as_resetPasswordS()

    @process
    def __loginRejectedUpdateNeeded(self):
        success = yield DialogsInterface.showI18nConfirmDialog('updateNeeded')
        if success and not BigWorld.wg_quitAndStartLauncher():
            self.as_setErrorMessageS(_ms(MENU.LOGIN_STATUS_LAUNCHERNOTFOUND), INVALID_FIELDS.ALL_VALID)

    def __loginRejectedBan(self, responseData):
        bansJSON = responseData.get('bans')
        bans = json.loads(bansJSON)
        expiryTime = int(bans.get('expiryTime', '0'))
        reason = bans.get('reason', '')
        if reason == BAN_REASON.CHINA_MIGRATION:
            g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.MIGRATION))
        if reason.startswith('#'):
            reason = _ms(reason)
        if expiryTime > 0:
            expiryTime = makeLocalServerTime(expiryTime)
            expiryTime = BigWorld.wg_getLongDateFormat(expiryTime) + ' ' + BigWorld.wg_getLongTimeFormat(expiryTime)
            self.as_setErrorMessageS(_ms(MENU.LOGIN_STATUS_LOGIN_REJECTED_BAN, time=expiryTime, reason=reason), INVALID_FIELDS.ALL_VALID)
        else:
            self.as_setErrorMessageS(_ms(MENU.LOGIN_STATUS_LOGIN_REJECTED_BAN_UNLIMITED, reason=reason), INVALID_FIELDS.ALL_VALID)

    def __loginRejectedRateLimited(self):
        self.as_setErrorMessageS(_ms(MENU.LOGIN_STATUS_LOGIN_REJECTED_RATE_LIMITED), INVALID_FIELDS.ALL_VALID)
        if not self.__loginRetryDialogShown:
            self.__showLoginRetryDialog({'waitingOpen': WAITING.TITLES_QUEUE,
             'waitingClose': WAITING.BUTTONS_EXITQUEUE,
             'message': _ms(WAITING.MESSAGE_AUTOLOGIN, connectionManager.serverUserName)})

    def __loginRejectedWithCustomState(self):
        self.as_setErrorMessageS(_ms('#menu:login/status/' + self.__customLoginStatus), INVALID_FIELDS.ALL_VALID)
        self.__clearFields(INVALID_FIELDS.ALL_VALID)

    def __showLoginRetryDialog(self, data):
        self._clearLoginView()
        self.fireEvent(LoginEventEx(LoginEventEx.SET_AUTO_LOGIN, View.alias, data['waitingOpen'], data['message'], data['waitingClose'], False), EVENT_BUS_SCOPE.LOBBY)
        self.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__closeLoginRetryDialog, EVENT_BUS_SCOPE.LOBBY)
        self.__loginRetryDialogShown = True

    def __closeLoginRetryDialog(self, event=None):
        connectionManager.stopRetryConnection()
        self.fireEvent(LoginEvent(LoginEventEx.CANCEL_LGN_QUEUE, View.alias))
        self.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__closeLoginRetryDialog, EVENT_BUS_SCOPE.LOBBY)
        self.__loginRetryDialogShown = False

    def __closeLoginQueueDialog(self):
        self.fireEvent(LoginEvent(LoginEvent.CANCEL_LGN_QUEUE, View.alias))
        g_preDefinedHosts.resetQueryResult()
        self.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self._onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, self._onLoginQueueSwitched, EVENT_BUS_SCOPE.LOBBY)
        self.__loginQueueDialogShown = False

    def __checkUserInputState(self):
        self.__capsLockCallbackID = None
        caps = BigWorld.wg_isCapsLockOn()
        if self.__capsLockState != caps:
            self.__capsLockState = caps
            self.as_setCapsLockStateS(self.__capsLockState)
        lang = BigWorld.wg_getLangCode()
        if self.__lang != lang:
            self.__lang = lang
            self.as_setKeyboardLangS(self.__lang)
        self.__capsLockCallbackID = BigWorld.callback(0.1, self.__checkUserInputState)
        return

    def __validateCredentials(self, userName, password, isToken2Login):
        isValid = True
        errorMessage = None
        invalidFields = None
        if isToken2Login or constants.IS_DEVELOPMENT:
            return _ValidateCredentialsResult(isValid, errorMessage, invalidFields)
        else:
            if len(userName) < _LOGIN_NAME_MIN_LENGTH:
                isValid = False
                errorMessage = _ms(MENU.LOGIN_STATUS_INVALID_LOGIN_LENGTH, count=_LOGIN_NAME_MIN_LENGTH)
                invalidFields = INVALID_FIELDS.LOGIN_INVALID
            elif not isAccountLoginValid(userName):
                isValid = False
                errorMessage = _ms(MENU.LOGIN_STATUS_INVALID_LOGIN)
                invalidFields = INVALID_FIELDS.LOGIN_INVALID
            elif not isPasswordValid(password):
                isValid = False
                errorMessage = _ms(MENU.LOGIN_STATUS_INVALID_PASSWORD, minLength=_PASSWORD_MIN_LENGTH, maxLength=_PASSWORD_MAX_LENGTH)
                invalidFields = INVALID_FIELDS.PWD_INVALID
            return _ValidateCredentialsResult(isValid, errorMessage, invalidFields)

    @staticmethod
    def __getWallpapersList():
        result = []
        ds = ResMgr.openSection(Scaleform.SCALEFORM_WALLPAPER_PATH)
        for filename in ds.keys():
            if filename[-4:] == '.png' and filename[0:2] != '__':
                result.append(filename[0:-4])

        return result

    def __loadLastBackgroundImage(self):
        result = {'show': True,
         'filename': ''}
        userPrefs = Settings.g_instance.userPrefs
        ds = None
        if userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            ds = userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
            result['filename'] = ds.readString('lastLoginBgImage', '')
        else:
            userPrefs.write(Settings.KEY_LOGINPAGE_PREFERENCES, '')
            self.__saveLastBackgroundImage(result['filename'])
        if ds is None:
            ds = userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        if not ds.has_key('showLoginWallpaper'):
            self.__createNodeShowWallpaper()
        result['show'] = ds.readBool('showLoginWallpaper', True)
        return result

    @staticmethod
    def __saveLastBackgroundImage(filename):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeString('lastLoginBgImage', filename)

    def _loadLastMuteState(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            userPrefs.write(Settings.KEY_LOGINPAGE_PREFERENCES, '')
        if userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES].has_key('mute'):
            self.__isSoundMuted = userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES].readBool('mute', False)
        else:
            self.__saveLastMuteState()

    def __saveLastMuteState(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeBool('mute', self.__isSoundMuted)

    def __loadLastBackgroundMode(self):
        userPrefs = Settings.g_instance.userPrefs
        if userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            self.__backgroundMode = userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES].readInt('lastBgMode', _VIDEO_BG_MODE)
        else:
            userPrefs.write(Settings.KEY_LOGINPAGE_PREFERENCES, '')
            self.__saveLastBackgroundMode()

    def __saveLastBackgroundMode(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeInt('lastBgMode', self.__backgroundMode)

    def __createNodeShowWallpaper(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeBool('showLoginWallpaper', True)

    def __updateServersList(self, *args):
        self._serversDP.rebuildList(self._servers.serverList)
        if not self.__isListInitialized and self._servers.serverList:
            self.__isListInitialized = True
            self.as_setSelectedServerIndexS(self._servers.selectedServerIdx)
