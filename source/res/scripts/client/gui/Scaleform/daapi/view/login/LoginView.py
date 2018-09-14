# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LoginView.py
import json
import random
import weakref
from collections import defaultdict, namedtuple
import WWISE
import BigWorld
import ResMgr
import ScaleformFileLoader
import Settings
import constants
from ConnectionManager import connectionManager, LOGIN_STATUS
from PlayerEvents import g_playerEvents
from adisp import process
from external_strings_utils import _LOGIN_NAME_MIN_LENGTH
from external_strings_utils import isAccountLoginValid, isPasswordValid, _PASSWORD_MIN_LENGTH, _PASSWORD_MAX_LENGTH
from gui import DialogsInterface, GUI_SETTINGS, Scaleform
from gui.Scaleform import getPathForFlash, SCALEFORM_STARTUP_VIDEO_MASK, DEFAULT_VIDEO_BUFFERING_TIME
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.meta.LoginPageMeta import LoginPageMeta
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.BAN_REASON import BAN_REASON
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.WAITING import WAITING
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import OpenLinkEvent, LoginEventEx, ArgsEvent, LoginEvent
from helpers import getFullClientVersion, dependency
from helpers.i18n import makeString as _ms
from helpers.statistics import g_statistics, HANGAR_LOADING_STATE
from helpers.time_utils import makeLocalServerTime
from predefined_hosts import AUTO_LOGIN_QUERY_URL, AUTO_LOGIN_QUERY_ENABLED, g_preDefinedHosts
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.login_manager import ILoginManager

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
_ValidateCredentialsResult = namedtuple('ValidateCredentialsResult', ('isValid', 'errorMessage', 'invalidFields'))
_BG_MODE_VIDEO, _BG_MODE_WALLPAPER = range(0, 2)
_LOGIN_VIDEO_FILE = SCALEFORM_STARTUP_VIDEO_MASK % '_login.usm'

class BackgroundMode(object):
    """
    This class responsible for changing graphics and sound states on login page.
    It load and save last state of mode to preferences.xml
    
    Description of section with background mode data of login page in preferences.xml
    <root>
        ...
        <scriptsPreferences>
            ...
            <videoBufferingTime/> - float(0.0-...), time for buffering of video, 0.0 - full streaming without buffering
            <loginPage>
                <lastBgMode/> - int(_BG_MODE_VIDEO=0/_BG_MODE_WALLPAPER=1),
                <mute/> - bool(mute=true/unmute=false),
                <showLoginWallpaper/> - bool(show=true/hide=false),
                <lastLoginBgImage/> - string, name last showed wallpaper
            </loginPage>
        </scriptsPreferences>
    </root>
    """

    def __init__(self, view):
        self.__isSoundMuted = False
        self.__bgMode = _BG_MODE_VIDEO
        self.__userPrefs = Settings.g_instance.userPrefs
        self.__view = weakref.proxy(view)
        self.__lastImage = ''
        self.__show = True
        self.__switchButton = True
        self.__bufferTime = self.__userPrefs.readFloat(Settings.VIDEO_BUFFERING_TIME, DEFAULT_VIDEO_BUFFERING_TIME)
        self.__images = self.__getWallpapersList()

    def showWallpaper(self, showSwitchButton):
        self.__view.as_showWallpaperS(self.__show, self.__randomImage(), showSwitchButton, self.__isSoundMuted)
        WWISE.WW_eventGlobalSync('loginscreen_ambient_start')
        if self.__isSoundMuted:
            WWISE.WW_eventGlobalSync('loginscreen_mute')

    def show(self):
        self.__loadFromPrefs()
        if self.__bgMode == _BG_MODE_VIDEO:
            self.__view.as_showLoginVideoS(_LOGIN_VIDEO_FILE, self.__bufferTime, self.__isSoundMuted)
        else:
            self.showWallpaper(self.__switchButton)

    def hide(self):
        WWISE.WW_eventGlobalSync(('loginscreen_music_stop_longfade', 'loginscreen_ambient_stop')[self.__bgMode])
        self.__saveToPrefs()

    def toggleMute(self, value):
        self.__isSoundMuted = value
        WWISE.WW_eventGlobalSync(('loginscreen_unmute', 'loginscreen_mute')[self.__isSoundMuted])

    def fadeSound(self):
        WWISE.WW_eventGlobalSync(('loginscreen_music_pause', 'loginscreen_ambient_stop')[self.__bgMode])

    def switch(self):
        if self.__bgMode != _BG_MODE_VIDEO:
            self.__bgMode = _BG_MODE_VIDEO
            self.__view.as_showLoginVideoS(_LOGIN_VIDEO_FILE, self.__bufferTime, self.__isSoundMuted)
        else:
            self.__bgMode = _BG_MODE_WALLPAPER
            self.__view.as_showWallpaperS(self.__show, self.__randomImage(), self.__switchButton, self.__isSoundMuted)
        WWISE.WW_eventGlobalSync(('loginscreen_music_resume', 'loginscreen_ambient_start')[self.__bgMode])
        if self.__isSoundMuted:
            WWISE.WW_eventGlobalSync('loginscreen_mute')

    def startVideoSound(self):
        WWISE.WW_eventGlobalSync('loginscreen_music_start')
        if self.__isSoundMuted:
            WWISE.WW_eventGlobalSync('loginscreen_mute')

    def __loadFromPrefs(self):
        if self.__userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            ds = self.__userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
            self.__isSoundMuted = ds.readBool('mute', False)
            self.__bgMode = ds.readInt('lastBgMode', _BG_MODE_VIDEO)
            self.__lastImage = ds.readString('lastLoginBgImage', '')
            self.__show = ds.readBool('showLoginWallpaper', True)

    def __saveToPrefs(self):
        if not self.__userPrefs.has_key(Settings.KEY_LOGINPAGE_PREFERENCES):
            self.__userPrefs.write(Settings.KEY_LOGINPAGE_PREFERENCES, '')
        ds = self.__userPrefs[Settings.KEY_LOGINPAGE_PREFERENCES]
        ds.writeBool('mute', self.__isSoundMuted)
        ds.writeInt('lastBgMode', self.__bgMode)
        ds.writeString('lastLoginBgImage', self.__lastImage)
        ds.writeBool('showLoginWallpaper', self.__show)

    def __randomImage(self):
        BG_IMAGES_PATH = '../maps/login/%s.png'
        if self.__show and self.__images:
            if len(self.__images) == 1:
                newFile = self.__images[0]
            else:
                while True:
                    newFile = random.choice(self.__images)
                    if newFile != self.__lastImage:
                        break

            self.__lastImage = newFile
        else:
            newFile = '__login_bg'
        return BG_IMAGES_PATH % newFile

    @staticmethod
    def __getWallpapersList():
        files = []
        ds = ResMgr.openSection(Scaleform.SCALEFORM_WALLPAPER_PATH)
        for filename in ds.keys():
            if filename[-4:] == '.png' and filename[0:2] != '__':
                files.append(filename[0:-4])

        return files


class LoginView(LoginPageMeta):
    loginManager = dependency.descriptor(ILoginManager)

    def __init__(self, ctx=None):
        LoginPageMeta.__init__(self, ctx=ctx)
        self.__isListInitialized = False
        self.__loginRetryDialogShown = False
        self.__loginQueueDialogShown = False
        self.__capsLockState = None
        self.__lang = None
        self.__capsLockCallbackID = None
        self.__backgroundMode = BackgroundMode(self)
        self.__customLoginStatus = None
        self._autoSearchVisited = False
        self._rememberUser = False
        self.loginManager.servers.updateServerList()
        self._servers = self.loginManager.servers
        return

    def onRegister(self, host):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.REGISTRATION))

    def onSetRememberPassword(self, rememberUser):
        self._rememberUser = rememberUser

    def onLogin(self, userName, password, serverName, isSocialToken2Login):
        g_statistics.noteHangarLoadingState(HANGAR_LOADING_STATE.LOGIN, True)
        self._autoSearchVisited = serverName == AUTO_LOGIN_QUERY_URL
        self.__customLoginStatus = None
        result = self.__validateCredentials(userName.lower().strip(), password.strip(), bool(self.loginManager.getPreference('token2')))
        if result.isValid:
            Waiting.show('login')
            self.loginManager.initiateLogin(userName, password, serverName, isSocialToken2Login, isSocialToken2Login or self._rememberUser)
        else:
            self.as_setErrorMessageS(result.errorMessage, result.invalidFields)
        return

    def resetToken(self):
        self.loginManager.clearToken2Preference()

    def showLegal(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LEGAL_INFO_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def isPwdInvalid(self, password):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not self.loginManager.getPreference('token2'):
            from external_strings_utils import isPasswordValid
            isInvalid = not isPasswordValid(password)
        return isInvalid

    def isLoginInvalid(self, login):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not self.loginManager.getPreference('token2'):
            from external_strings_utils import isAccountLoginValid
            isInvalid = not isAccountLoginValid(login)
        return isInvalid

    def onRecovery(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.RECOVERY_PASSWORD))

    def isToken(self):
        return bool(self.loginManager.getPreference('token2'))

    def onEscape(self):

        def buttonHandler(isOk):
            if isOk:
                self.destroy()
                BigWorld.quit()

        DialogsInterface.showI18nConfirmDialog('quit', buttonHandler, focusedID=DIALOG_BUTTON_ID.CLOSE)

    def startListenCsisUpdate(self, startListenCsis):
        self.loginManager.servers.startListenCsisQuery(startListenCsis)

    def onExitFromAutoLogin(self):
        pass

    def saveLastSelectedServer(self, server):
        pass

    def switchBgMode(self):
        self.__backgroundMode.switch()

    def musicFadeOut(self):
        self.__backgroundMode.fadeSound()

    def setMute(self, value):
        self.__backgroundMode.toggleMute(value)

    def onVideoLoaded(self):
        self.__backgroundMode.startVideoSound()

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
        ScaleformFileLoader.enableStreaming([getPathForFlash(_LOGIN_VIDEO_FILE)])
        self.__backgroundMode.show()
        if self.__capsLockCallbackID is None:
            self.__capsLockCallbackID = BigWorld.callback(0.1, self.__checkUserInputState)
        sessionProvider = dependency.instance(IBattleSessionProvider)
        sessionProvider.getCtx().lastArenaUniqueID = None
        self._setData()
        self._showForm()
        return

    def _dispose(self):
        ScaleformFileLoader.disableStreaming()
        self.__backgroundMode.hide()
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
        self._rememberUser = self.loginManager.getPreference('remember_user')
        if self._rememberUser:
            password = '*' * self.loginManager.getPreference('password_length')
        else:
            password = ''
        if GUI_SETTINGS.clearLoginValue:
            login = password = ''
        else:
            login = self.loginManager.getPreference('login')
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
        if isToken2Login or constants.IS_DEVELOPMENT and len(userName):
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

    def __updateServersList(self, *args):
        self._serversDP.rebuildList(self._servers.serverList)
        if not self.__isListInitialized and self._servers.serverList:
            self.__isListInitialized = True
            self.as_setSelectedServerIndexS(self._servers.selectedServerIdx)
