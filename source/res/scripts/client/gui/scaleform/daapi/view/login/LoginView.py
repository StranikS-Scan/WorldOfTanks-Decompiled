# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/LoginView.py
import json
from collections import defaultdict
import BigWorld
import WWISE
import constants
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from wg_async import wg_async, wg_await
from connection_mgr import LOGIN_STATUS
from external_strings_utils import isAccountLoginValid, isPasswordValid
from frameworks.wulf import WindowFlags, WindowStatus
from gui import DialogsInterface, GUI_SETTINGS
from gui import makeHtmlString
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.LoginPageMeta import LoginPageMeta
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.dialogs.dialogs import showSimple
from gui.impl.gen import R
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import OpenLinkEvent, LoginEventEx, ArgsEvent, LoginEvent, LoadViewEvent, ViewEventType
from helpers import getFullClientVersion, dependency, uniprof
from helpers.i18n import makeString as _ms
from helpers.statistics import HANGAR_LOADING_STATE
from helpers.time_utils import makeLocalServerTime
from login_modes import createLoginMode
from login_modes.base_mode import INVALID_FIELDS
from predefined_hosts import AUTO_LOGIN_QUERY_URL, AUTO_LOGIN_QUERY_ENABLED, g_preDefinedHosts
from shared_utils import CONST_CONTAINER
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.login_manager import ILoginManager
from skeletons.helpers.statistics import IStatisticsCollector
_STATUS_TO_INVALID_FIELDS_MAPPING = defaultdict(lambda : INVALID_FIELDS.ALL_VALID, {LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD: INVALID_FIELDS.PWD_INVALID,
 LOGIN_STATUS.LOGIN_REJECTED_ILLEGAL_CHARACTERS: INVALID_FIELDS.LOGIN_PWD_INVALID,
 LOGIN_STATUS.LOGIN_REJECTED_SERVER_NOT_READY: INVALID_FIELDS.SERVER_INVALID,
 LOGIN_STATUS.SESSION_END: INVALID_FIELDS.PWD_INVALID})

class CustomLoginStatuses(CONST_CONTAINER):
    ANOTHER_PERIPHERY = 'another_periphery'
    CHECKOUT_ERROR = 'checkout_error'
    CENTER_RESTART = 'centerRestart'
    VERSION_MISMATCH = 'versionMismatch'
    ACCESS_FORBIDDEN_TO_PERIPHERY = 'accessForbiddenToPeriphery'


def DialogPredicate(window):
    return window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED) and window.windowFlags & WindowFlags.DIALOG


class LoginView(LoginPageMeta):
    loginManager = dependency.descriptor(ILoginManager)
    connectionMgr = dependency.descriptor(IConnectionManager)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    __gui = dependency.descriptor(IGuiLoader)

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

    @wg_async
    def onLogin(self, userName, password, serverName, isSocialToken2Login):
        if self._loginMode.showRememberServerWarning:
            builder = ResSimpleDialogBuilder()
            builder.setFlags(WindowFlags.DIALOG | WindowFlags.WINDOW_FULLSCREEN)
            builder.setMessagesAndButtons(R.strings.dialogs.dyn('loginToPeripheryAndRemember'))
            success = yield wg_await(showSimple(builder.build(self)))
            if not success:
                return
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
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LEGAL_INFO_WINDOW)), EVENT_BUS_SCOPE.LOBBY)

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

    def onTextLinkClick(self, linkId):
        self.fireEvent(OpenLinkEvent(linkId))

    def isToken(self):
        return self._loginMode.isToken2()

    def onEscape(self):
        self.__closeOpenedDialogs()
        self.__showExitDialog()

    def changeAccount(self):
        self.__clearPeripheryRouting()
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

    def doUpdate(self):
        pass

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
        self.connectionMgr.onPeripheryRoutingGroupUpdated += self.__updateServersList
        g_playerEvents.onAccountShowGUI += self._clearLoginView
        g_playerEvents.onEntityCheckOutEnqueued += self._onEntityCheckoutEnqueued
        g_playerEvents.onAccountBecomeNonPlayer += self._onAccountBecomeNonPlayer
        g_playerEvents.onBootcampStartChoice += self.__onBootcampStartChoice
        self.as_setVersionS(getFullClientVersion())
        self.as_setCopyrightS(backport.text(R.strings.menu.copy()), backport.text(R.strings.menu.legal()))
        self.sessionProvider.getCtx().lastArenaUniqueID = None
        self.sessionProvider.getCtx().lastArenaBonusType = None
        self._loginMode.onPopulate()
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
        self.connectionMgr.onPeripheryRoutingGroupUpdated -= self.__updateServersList
        self.connectionMgr.onRejected -= self._onLoginRejected
        self.connectionMgr.onKickWhileLoginReceived -= self._onKickedWhileLogin
        self.connectionMgr.onQueued -= self._onHandleQueue
        self.connectionMgr.onLoggedOn -= self._onLoggedOn
        self._servers.onServersStatusChanged -= self.__updateServersList
        g_playerEvents.onAccountShowGUI -= self._clearLoginView
        g_playerEvents.onEntityCheckOutEnqueued -= self._onEntityCheckoutEnqueued
        g_playerEvents.onAccountBecomeNonPlayer -= self._onAccountBecomeNonPlayer
        g_playerEvents.onBootcampStartChoice -= self.__onBootcampStartChoice
        if self._entityEnqueueCancelCallback:
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
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
        if peripheryID > 0:
            self.__customLoginStatus = CustomLoginStatuses.ANOTHER_PERIPHERY
        elif peripheryID == 0:
            self.__customLoginStatus = CustomLoginStatuses.CHECKOUT_ERROR
        elif peripheryID == -2:
            self.__customLoginStatus = CustomLoginStatuses.CENTER_RESTART
        elif peripheryID == -3:
            self.__customLoginStatus = CustomLoginStatuses.VERSION_MISMATCH
        elif peripheryID == -4:
            self.__customLoginStatus = CustomLoginStatuses.ACCESS_FORBIDDEN_TO_PERIPHERY
        if not self.__loginRetryDialogShown and peripheryID >= 0:
            self.__showLoginRetryDialog({'waitingOpen': backport.text(R.strings.waiting.titles.dyn(self.__customLoginStatus)()),
             'waitingClose': backport.msgid(R.strings.waiting.buttons.cease()),
             'message': backport.text(R.strings.waiting.message.dyn(self.__customLoginStatus)(), self.__getServerText(self.__customLoginStatus, self.connectionMgr.serverUserName))})

    def _onHandleQueue(self, queueNumber):
        serverName = self.connectionMgr.serverUserName
        showAutoSearchBtn = AUTO_LOGIN_QUERY_ENABLED and not self._autoSearchVisited
        if showAutoSearchBtn:
            cancelBtnLbl = backport.msgid(R.strings.waiting.buttons.cancel())
        else:
            cancelBtnLbl = backport.msgid(R.strings.waiting.buttons.exitQueue())
        message = backport.text(R.strings.waiting.message.queue(), self.__getServerText('overload', serverName), queueNumber)
        if showAutoSearchBtn:
            message = backport.text(R.strings.waiting.message.useAutoSearch(), self.__getServerText('overload', serverName), queueNumber, serverName)
        if not self.__loginQueueDialogShown:
            self._clearLoginView()
            self.__loginQueueDialogShown = True
            self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOGIN_QUEUE), title=backport.msgid(R.strings.waiting.titles.queue()), message=message, cancelLabel=cancelBtnLbl, showAutoLoginBtn=showAutoSearchBtn), EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self._onLoginQueueClosed, EVENT_BUS_SCOPE.LOBBY)
            self.addListener(LoginEventEx.SWITCH_LOGIN_QUEUE_TO_AUTO, self._onLoginQueueSwitched, EVENT_BUS_SCOPE.LOBBY)
        else:
            ctx = {'title': backport.msgid(R.strings.waiting.titles.queue()),
             'message': message,
             'cancelLabel': cancelBtnLbl,
             'showAutoLoginBtn': showAutoSearchBtn}
            self.fireEvent(ArgsEvent(ArgsEvent.UPDATE_ARGS, VIEW_ALIAS.LOGIN_QUEUE, ctx), EVENT_BUS_SCOPE.LOBBY)

    def _onLoginQueueClosed(self, event):
        self.__closeLoginQueueDialog()

    def _onEntityCheckoutEnqueued(self, cancelCallback):
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG_SHOW)), EVENT_BUS_SCOPE.LOBBY)
        self._entityEnqueueCancelCallback = cancelCallback

    def _onAccountBecomeNonPlayer(self):
        if self._entityEnqueueCancelCallback:
            self._entityEnqueueCancelCallback = None
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
        return

    def _onEntityCheckoutCanceled(self, event):
        if event.alias == VIEW_ALIAS.BOOTCAMP_QUEUE_DIALOG_CANCEL:
            Waiting.show('login')
            g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._onEntityCheckoutCanceled, EVENT_BUS_SCOPE.LOBBY)
            if self._entityEnqueueCancelCallback:
                self._entityEnqueueCancelCallback()
            self._entityEnqueueCancelCallback = None
        return

    def _onLoginQueueSwitched(self, event):
        self.__closeLoginQueueDialog()
        self.as_switchToAutoAndSubmitS(AUTO_LOGIN_QUERY_URL)

    def _onLoginRejected(self, loginStatus, responseData):
        Waiting.hide('login')
        loginStatus = str(loginStatus)
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
                self.as_setErrorMessageS(backport.text(R.strings.menu.login.status.dyn(loginStatus)()), _STATUS_TO_INVALID_FIELDS_MAPPING[loginStatus])
            self.__clearFields(_STATUS_TO_INVALID_FIELDS_MAPPING[loginStatus])
        self._dropLoginQueue(loginStatus)
        return

    def _dropLoginQueue(self, loginStatus):
        if loginStatus != LOGIN_STATUS.LOGIN_REJECTED_RATE_LIMITED and self.__loginRetryDialogShown:
            self.__closeLoginQueueDialog()

    def __clearFields(self, invalidField):
        if invalidField == INVALID_FIELDS.PWD_INVALID:
            self.as_resetPasswordS()

    @adisp_process
    def __loginRejectedUpdateNeeded(self):
        success = yield DialogsInterface.showI18nConfirmDialog('updateNeeded')
        if success and not BigWorld.wg_quitAndStartLauncher():
            self.as_setErrorMessageS(backport.text(R.strings.menu.login.status.launchernotfound()), INVALID_FIELDS.ALL_VALID)

    def __loginRejectedBan(self, responseData):
        bansJSON = responseData.get('bans')
        bans = json.loads(bansJSON)
        expiryTime = int(bans.get('expiryTime', '0'))
        reason = bans.get('reason', '')
        if reason == backport.msgid(R.strings.ban_reason.china_migration()):
            g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.MIGRATION))
        if reason.startswith('#'):
            reason = _ms(reason)
        if expiryTime > 0:
            if bans.get('curfew') is not None and bans.get('reason', '') != '#ban_reason:curfew_ban':
                self.as_setErrorMessageS(reason, INVALID_FIELDS.ALL_VALID)
            else:
                expiryTime = makeLocalServerTime(expiryTime)
                expiryTime = backport.getLongDateFormat(expiryTime) + ' ' + backport.getLongTimeFormat(expiryTime)
                self.as_setErrorMessageS(backport.text(R.strings.menu.login.status.LOGIN_REJECTED_BAN(), time=expiryTime, reason=reason), INVALID_FIELDS.ALL_VALID)
        else:
            self.as_setErrorMessageS(backport.text(R.strings.menu.login.status.LOGIN_REJECTED_BAN_UNLIMITED(), reason=reason), INVALID_FIELDS.ALL_VALID)
        return

    def __loginRejectedRateLimited(self):
        backport.text(R.strings.menu.login.status.LOGIN_REJECTED_RATE_LIMITED())
        self.as_setErrorMessageS(backport.text(R.strings.menu.login.status.LOGIN_REJECTED_RATE_LIMITED()), INVALID_FIELDS.ALL_VALID)
        if not self.__loginRetryDialogShown:
            self.__showLoginRetryDialog({'waitingOpen': backport.msgid(R.strings.waiting.titles.queue()),
             'waitingClose': backport.msgid(R.strings.waiting.buttons.exitQueue()),
             'message': backport.text(R.strings.waiting.message.autoLogin(), self.__getServerText('overload', self.connectionMgr.serverUserName))})

    def __loginRejectedWithCustomState(self):
        if self.__customLoginStatus == CustomLoginStatuses.ACCESS_FORBIDDEN_TO_PERIPHERY:
            if self.connectionMgr.peripheryRoutingGroup is not None:
                peripheriesStr = ', '.join((p.shortName for p in self.connectionMgr.availableHosts))
            else:
                peripheriesStr = ''
            msg = backport.text(R.strings.menu.login.status.dyn(self.__customLoginStatus)(), peripheries=peripheriesStr)
        else:
            msg = backport.text(R.strings.menu.login.status.dyn(self.__customLoginStatus)())
        self.as_setErrorMessageS(msg, INVALID_FIELDS.ALL_VALID)
        self.__clearFields(INVALID_FIELDS.ALL_VALID)
        return

    def __showLoginRetryDialog(self, data):
        self._clearLoginView()
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOGIN_QUEUE), title=data['waitingOpen'], message=data['message'], cancelLabel=data['waitingClose'], showAutoLoginBtn=False), EVENT_BUS_SCOPE.LOBBY)
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

    def __closeOpenedDialogs(self):
        for window in self.__gui.windowsManager.findWindows(DialogPredicate):
            window.destroy()

    @wg_async
    def __showExitDialog(self):
        isOk = yield wg_await(dialogs.quitGame(self.getParentWindow()))
        if isOk:
            self.destroy()
            BigWorld.quit()

    def __getServerText(self, key, serverName):
        return makeHtmlString('html_templates:login/server-state', key, {'message': backport.text(R.strings.waiting.message.server.dyn(key)(), server=serverName)})

    def __onBootcampStartChoice(self):
        WWISE.WW_eventGlobal('loginscreen_mute')

    def __clearPeripheryRouting(self):
        if self.connectionMgr.peripheryRoutingGroup is not None:
            self.connectionMgr.setPeripheryRoutingGroup(None, None)
        return
