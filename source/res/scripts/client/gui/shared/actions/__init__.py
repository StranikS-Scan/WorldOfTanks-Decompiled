# Embedded file name: scripts/client/gui/shared/actions/__init__.py
import BigWorld
from ConnectionManager import connectionManager, CONNECTION_METHOD
from adisp import process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework import ViewTypes
from gui.app_loader import g_appLoader
from gui.login import g_loginManager
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LoginEventEx, GUICommonEvent
from gui.shared.actions.chains import ActionsChain
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from predefined_hosts import g_preDefinedHosts, getHostURL
__all__ = ['LeavePrbModalEntity',
 'DisconnectFromPeriphery',
 'ConnectToPeriphery',
 'PrbInvitesInit',
 'ActionsChain']

class Action(object):

    def __init__(self):
        super(Action, self).__init__()
        self._completed = False
        self._running = False

    def invoke(self):
        pass

    def isInstantaneous(self):
        return True

    def isRunning(self):
        return self._running

    def isCompleted(self):
        return self._completed


CONNECT_TO_PERIPHERY_DELAY = 2.0

class LeavePrbModalEntity(Action):

    def __init__(self):
        super(LeavePrbModalEntity, self).__init__()
        self._running = False

    def invoke(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher:
            state = dispatcher.getFunctionalState()
            if state.hasModalEntity:
                factory = dispatcher.getControlFactories().get(state.ctrlTypeID)
                if factory:
                    ctx = factory.createLeaveCtx()
                    if ctx:
                        self._running = True
                        self.__doLeave(dispatcher, ctx)
                    else:
                        LOG_ERROR('Leave modal entity. Can not create leave ctx', state)
                else:
                    LOG_ERROR('Leave modal entity. Factory is not found', state)
            else:
                LOG_DEBUG('Leave modal entity. Player has not prebattle')
                self._completed = True

    def isInstantaneous(self):
        return False

    @process
    def __doLeave(self, dispatcher, ctx):
        self._completed = yield dispatcher.leave(ctx)
        if self._completed:
            LOG_DEBUG('Leave modal entity. Player left prebattle/unit.')
        else:
            LOG_ERROR('Leave modal entity. Action was failed.')
        self._running = False


class DisconnectFromPeriphery(Action):

    def __init__(self):
        super(DisconnectFromPeriphery, self).__init__()

    def isInstantaneous(self):
        return False

    def invoke(self):
        self._running = True
        g_appLoader.goToLoginByRQ()

    def isRunning(self):
        app = g_appLoader.getApp()
        if app:
            from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
            view = app.containerManager.getView(ViewTypes.DEFAULT)
            if view and view.settings.alias == VIEW_ALIAS.LOGIN and view._isCreated() and connectionManager.isDisconnected():
                LOG_DEBUG('Disconnect action. Player came to login')
                self._completed = True
                self._running = False
        return self._running


class ConnectToPeriphery(Action):

    def __init__(self, peripheryID):
        super(ConnectToPeriphery, self).__init__()
        self.__host = g_preDefinedHosts.periphery(peripheryID)
        self.__endTime = None
        self.__credentials = g_lobbyContext.getCredentials()
        return

    def isInstantaneous(self):
        return False

    def isRunning(self):
        if self.__endTime and self.__endTime <= BigWorld.time():
            self.__endTime = None
            self.__doConnect()
        return super(ConnectToPeriphery, self).isRunning()

    def invoke(self):
        if self.__host and self.__credentials:
            if len(self.__credentials) < 2:
                self._completed = False
                LOG_ERROR('Connect action. Login info is invalid')
                return
            login, token2 = self.__credentials
            if not login or not token2:
                self._completed = False
                LOG_ERROR('Connect action. Login info is invalid')
                return
            self._running = True
            self.__endTime = BigWorld.time() + CONNECT_TO_PERIPHERY_DELAY
            Waiting.show('login')
        else:
            LOG_ERROR('Connect action. Login info is invalid')
            self._completed = False
            self._running = False

    def __doConnect(self):
        login, token2 = self.__credentials
        self.__addHandlers()
        connectionManager.initiateConnection({'login': login,
         'token2': token2,
         'auth_method': CONNECTION_METHOD.TOKEN2,
         'session': BigWorld.wg_cpsalt(g_loginManager.getPreference('session')),
         'temporary': str(int(not g_loginManager.getPreference('remember_user')))}, '', getHostURL(self.__host, token2))

    def __addHandlers(self):
        g_eventBus.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        connectionManager.onConnected += self.__onConnected
        connectionManager.onRejected += self.__onRejected

    def __removeHandlers(self):
        g_eventBus.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        connectionManager.onConnected -= self.__onConnected
        connectionManager.onRejected -= self.__onRejected

    def __onConnected(self):
        self.__removeHandlers()
        self._completed = True
        self._running = False

    def __onRejected(self, status, responseData):
        self.__removeHandlers()
        self._completed = False
        self._running = False

    def __onLoginQueueClosed(self, _):
        self.__removeHandlers()
        self._completed = False
        self._running = False
        LOG_DEBUG('Connect action. Player exit from login queue')


class PrbInvitesInit(Action):

    def __init__(self):
        super(PrbInvitesInit, self).__init__()

    def isInstantaneous(self):
        return False

    def invoke(self):
        from gui.prb_control.dispatcher import g_prbLoader
        invitesManager = g_prbLoader.getInvitesManager()
        if invitesManager:
            if invitesManager.isInited():
                LOG_DEBUG('Invites init action. Invites init action. List of invites is build')
                self._completed = True
            else:
                self._running = True
                invitesManager.onInvitesListInited += self.__onInvitesListInited
        else:
            LOG_ERROR('Invites init action. Invites manager not found')
            self._completed = False

    def __onInvitesListInited(self):
        from gui.prb_control.dispatcher import g_prbLoader
        invitesManager = g_prbLoader.getInvitesManager()
        if invitesManager:
            LOG_DEBUG('Invites init action. List of invites is build')
            invitesManager.onInvitesListInited -= self.__onInvitesListInited
        else:
            LOG_ERROR('Invites manager not found')
        self._completed = True
        self._running = False


class WaitFlagActivation(Action):

    def __init__(self):
        super(WaitFlagActivation, self).__init__()
        self._isActive = False

    def activate(self):
        LOG_DEBUG('Flag is activated')
        self._isActive = True

    def inactivate(self):
        LOG_DEBUG('Flag is inactivated')
        self._isActive = False

    def invoke(self):
        if not self._isActive:
            self._running = True
        else:
            self._completed = True

    def isRunning(self):
        if self._isActive:
            self._running = False
            self._completed = True
        return self._running

    def isInstantaneous(self):
        return False


class ShowCompanyWindow(Action):

    def __init__(self):
        super(ShowCompanyWindow, self).__init__()
        self.__isLobbyInited = False
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)

    def invoke(self):
        self._running = True
        self._completed = False
        if self.__isLobbyInited:
            from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
            battle_selector_items.getItems().select(PREBATTLE_ACTION_NAME.COMPANY)
            self._completed = True
            self._running = False

    def __onLobbyInited(self, _):
        self.__isLobbyInited = True
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self.invoke()
