# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LoginView.py
import json
from collections import defaultdict
import BigWorld
import constants
from PlayerEvents import g_playerEvents
from adisp import process
from async import async, await
from connection_mgr import LOGIN_STATUS
from external_strings_utils import isAccountLoginValid, isPasswordValid
from gui import DialogsInterface, GUI_SETTINGS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LoginPageMeta import LoginPageMeta
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.BAN_REASON import BAN_REASON
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.WAITING import WAITING
from gui.impl import dialogs
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import OpenLinkEvent, LoginEventEx, ArgsEvent, LoginEvent, BootcampEvent
from helpers import getFullClientVersion, dependency, uniprof
from helpers.i18n import makeString as _ms
from helpers.statistics import HANGAR_LOADING_STATE
from helpers.time_utils import makeLocalServerTime
from login_modes import createLoginMode
from login_modes.base_mode import INVALID_FIELDS
from predefined_hosts import AUTO_LOGIN_QUERY_URL, AUTO_LOGIN_QUERY_ENABLED, g_preDefinedHosts
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.login_manager import ILoginManager
from skeletons.helpers.statistics import IStatisticsCollector
_STATUS_TO_INVALID_FIELDS_MAPPING = defaultdict(lambda : INVALID_FIELDS.ALL_VALID, {LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD: INVALID_FIELDS.PWD_INVALID,
 LOGIN_STATUS.LOGIN_REJECTED_ILLEGAL_CHARACTERS: INVALID_FIELDS.LOGIN_PWD_INVALID,
 LOGIN_STATUS.LOGIN_REJECTED_SERVER_NOT_READY: INVALID_FIELDS.SERVER_INVALID,
 LOGIN_STATUS.SESSION_END: INVALID_FIELDS.PWD_INVALID})

class LoginView(LoginPageMeta):
    loginManager = dependency.descriptor(ILoginManager)
    connectionMgr = dependency.descriptor(IConnectionManager)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, ctx=None):
        LoginPageMeta.__init__(self, ctx=ctx)
        self.__isListInitialized = False
        self.__loginRetryDialogShown = False
        self.__loginQueueDialogShown = False
        self.__capsLockState = None
        self.__lang = None
        self.__capsLockCallbackID = None
        self.__customLoginStatus = None
        self._autoSearchVisited = False
        self._entityEnqueueCancelCallback = None
        self._servers = self.loginManager.servers
        self.loginManager.servers.updateServerList()
        self._loginMode = createLoginMode(self)
        return

    def onRegister(self, host):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.REGISTRATION))

    def onSetRememberPassword(self, rememberUser):
        self._loginMode.setRememberPassword(rememberUser)

    def onLogin(self, userName, password, serverName, isSocialToken2Login):
        self._loginMode.doLogin(userName, password, serverName, isSocialToken2Login)

    def _onLoggedOn(self, *args):
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.LOGIN, True)
        self.statsCollector.needCollectSystemData(True)
        selectedServer = self._servers.selectedServer
        self._autoSearchVisited = selectedServer['data'] == AUTO_LOGIN_QUERY_URL if selectedServer is not None else False
        self.__customLoginStatus = None
        return

    def resetToken(self):
        self._loginMode.resetToken()

    def showLegal(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LEGAL_INFO_WINDOW), EVENT_BUS_SCOPE.LOBBY)

    def isPwdInvalid(self, password):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not self._loginMode.isToken2():
            isInvalid = not isPasswordValid(password)
        return isInvalid

    def isLoginInvalid(self, login):
        isInvalid = False
        if not constants.IS_DEVELOPMENT and not self._loginMode.isToken2():
            isInvalid = not isAccountLoginValid(login)
        return isInvalid

    def onRecovery(self):
        self.fireEvent(OpenLinkEvent(OpenLinkEvent.RECOVERY_PASSWORD))

    def isToken(self):
        return self._loginMode.isToken2()

    def onEscape(self):
        self.__showExitDialog()

    def changeAccount(self):
        self._loginMode.changeAccount()

    def musicFadeOut(self):
        self._loginMode.musicFadeOut()

    def videoLoadingFailed(self):
        self._loginMode.videoLoadingFailed()

    def setMute(self, value):
        self._loginMode.setMute(value)

    def onVideoLoaded(self):
        self._loginMode.onVideoLoaded()

    def switchBgMode(self):
        self._loginMode.switchBgMode()

    def startListenCsisUpdate(self, startListenCsis):
        self.loginManager.servers.startListenCsisQuery(startListenCsis)

    @uniprof.regionDecorator(label='offline.login', scope='enter')
    def _populate(self):
        View._populate(self)
        self._serversDP = ServersDataProvider()
        self._serversDP.setFlashObject(self.as_getServersDPS())
        self.as_enableS(True)
        self._servers.onServersStatusChanged += self.__updateServersList
        self.connectionMgr.onRejected += self._onLoginRejected
        self.connectionMgr.onKickWhileLoginReceived += self._onKickedWhileLogin
        self.connectionMgr.onQueued += self._onHandleQueue
        self.connectionMgr.onLoggedOn += self._onLoggedOn
        g_playerEvents.onAccountShowGUI += self._clearLoginView
        g_playerEvents.onEntityCheckOutEnqueued += self._onEntityCheckoutEnqueued
        g_playerEvents.onAccountBecomeNonPlayer += self._onAccountBecomeNonPlayer
        self.as_setVersionS(getFullClientVersion())
        self.as_setCopyrightS(_ms(MENU.COPY), _ms(MENU.LEGAL))
        self.sessionProvider.getCtx().lastArenaUniqueID = None
        self._loginMode.init()
        self.update()
        if self.__capsLockCallbackID is None:
            self.__capsLockCallbackID = BigWorld.callback(0.0, self.__checkUserInputState)
        return

    @uniprof.regionDecorator(label='offline.login', scope='exit')
    def _dispose(self):
        self._loginMode.destroy()
        self._loginMode = None
        if self.__capsLockCallbackID is not None:
            BigWorld.cancelCallback(self.__capsLockCallbackID)
            self.__capsLockCallbackID = None
        self.connectionMgr.onRejected -= self._onLoginRejected
        self.connectionMgr.onKickWhileLoginReceived -= self._onKickedWhileLogin
        self.connectionMgr.onQueued -= self._onHandleQueue
        self.connectionMgr.onLoggedOn -= self._onLoggedOn
        self._servers.onServersStatusChanged -= self.__updateServersList
        g_playerEvents.onAccountShowGUI -= self._clearLoginView
        g_playerEvents.onEntityCheckOutEnqueued -= self._onEntityCheckoutEnqueued
        g_playerEvents.onAccountBecomeNonPlayer -= self._onAccountBecomeNonPlayer
        if self._entityEnqueueCancelCallback:
            g_eventBus.removeListener(BootcampEvent.QUEUE_DIALOG_CANCEL, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
        self._serversDP.fini()
        self._serversDP = None
        self._entityEnqueueCancelCallback = None
        super(LoginView, self)._dispose()
        return

    def update(self):
        self.as_setDefaultValuesS({'loginName': self._loginMode.login,
         'pwd': self._loginMode.password,
         'memberMe': self._loginMode.rememberUser,
         'memberMeVisible': self._loginMode.rememberPassVisible,
         'isIgrCredentialsReset': GUI_SETTINGS.igrCredentialsReset,
         'showRecoveryLink': not GUI_SETTINGS.isEmpty('recoveryPswdURL')})
        self._loginMode.updateForm()
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
                 'message': _ms(WAITING.message(self.__customLoginStatus), self.connectionMgr.serverUserName)})
        elif peripheryID == -2:
            self.__customLoginStatus = 'centerRestart'
        elif peripheryID == -3:
            self.__customLoginStatus = 'versionMismatch'

    def _onHandleQueue(self, queueNumber):
        serverName = self.connectionMgr.serverUserName
        showAutoSearchBtn = AUTO_LOGIN_QUERY_ENABLED and not self._autoSearchVisited
        cancelBtnLbl = WAITING.BUTTONS_CANCEL if showAutoSearchBtn else WAITING.BUTTONS_EXITQUEUE
        message = _ms(WAITING.MESSAGE_QUEUE, serverName, queueNumber)
        if showAutoSearchBtn:
            message = _ms(WAITING.MESSAGE_USEAUTOSEARCH, serverName, queueNumber, serverName)
        if not self.__loginQueueDialogShown:
            self._clearLoginView()
            self.__loginQueueDialogShown = True
            self.fireEvent(LoginEventEx(LoginEventEx.SET_LOGIN_QUEUE, '', WAITING.TITLES_QUEUE, message, cancelBtnLbl, showAutoSearchBtn), EVENT_BUS_SCOPE.LOBBY)
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

    def _onEntityCheckoutEnqueued(self, cancelCallback):
        g_eventBus.addListener(BootcampEvent.QUEUE_DIALOG_CANCEL, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(BootcampEvent(BootcampEvent.QUEUE_DIALOG_SHOW), EVENT_BUS_SCOPE.LOBBY)
        self._entityEnqueueCancelCallback = cancelCallback

    def _onAccountBecomeNonPlayer(self):
        if self._entityEnqueueCancelCallback:
            self._entityEnqueueCancelCallback = None
            g_eventBus.removeListener(BootcampEvent.QUEUE_DIALOG_CANCEL, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
        return

    def _onEntityCheckoutCanceled(self, _):
        Waiting.show('login')
        g_eventBus.removeListener(BootcampEvent.QUEUE_DIALOG_CANCEL, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
        if self._entityEnqueueCancelCallback:
            self._entityEnqueueCancelCallback()
        self._entityEnqueueCancelCallback = None
        return

    def _onLoginQueueSwitched(self, event):
        self.__closeLoginQueueDialog()
        self.as_switchToAutoAndSubmitS(AUTO_LOGIN_QUERY_URL)

    def _onLoginRejected(self, loginStatus, responseData):
        Waiting.hide('login')
        if not self._loginMode.skipRejectionError(loginStatus):
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
             'message': _ms(WAITING.MESSAGE_AUTOLOGIN, self.connectionMgr.serverUserName)})

    def __loginRejectedWithCustomState(self):
        self.as_setErrorMessageS(_ms('#menu:login/status/' + self.__customLoginStatus), INVALID_FIELDS.ALL_VALID)
        self.__clearFields(INVALID_FIELDS.ALL_VALID)

    def __showLoginRetryDialog(self, data):
        self._clearLoginView()
        self.fireEvent(LoginEventEx(LoginEventEx.SET_AUTO_LOGIN, '', data['waitingOpen'], data['message'], data['waitingClose'], False), EVENT_BUS_SCOPE.LOBBY)
        self.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__closeLoginRetryDialog, EVENT_BUS_SCOPE.LOBBY)
        self.__loginRetryDialogShown = True

    def __closeLoginRetryDialog(self, event=None):
        self.connectionMgr.stopRetryConnection()
        self.fireEvent(LoginEvent(LoginEventEx.CANCEL_LGN_QUEUE, ''))
        self.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__closeLoginRetryDialog, EVENT_BUS_SCOPE.LOBBY)
        self.__loginRetryDialogShown = False

    def __closeLoginQueueDialog(self):
        self.fireEvent(LoginEvent(LoginEvent.CANCEL_LGN_QUEUE, ''))
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

    def __updateServersList(self, *args):
        self._serversDP.rebuildList(self._servers.serverList)
        if not self.__isListInitialized and self._servers.serverList:
            self.__isListInitialized = True
            self.as_setSelectedServerIndexS(self._servers.selectedServerIdx)

    @async
    def __showExitDialog(self):
        isOk = yield await(dialogs.quitGame(self))
        if isOk:
            self.destroy()
            BigWorld.quit()
