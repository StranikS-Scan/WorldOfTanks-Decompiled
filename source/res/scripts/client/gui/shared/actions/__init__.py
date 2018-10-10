# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/actions/__init__.py
import BigWorld
from adisp import process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework import ViewTypes
from gui.app_loader import g_appLoader
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.actions.chains import ActionsChain
from gui.shared.events import LoginEventEx, GUICommonEvent
from helpers import dependency
from predefined_hosts import g_preDefinedHosts, getHostURL
from skeletons.connection_mgr import IConnectionManager
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from constants import WGC_STATE
__all__ = ('LeavePrbModalEntity', 'DisconnectFromPeriphery', 'ConnectToPeriphery', 'PrbInvitesInit', 'ActionsChain')

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
                    ctx = factory.createLeaveCtx(flags=FUNCTIONAL_FLAG.SWITCH)
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
            LOG_DEBUG('Leave modal entity. Player left prebattle.')
        else:
            LOG_DEBUG('Leave modal entity. Action was failed.')
        self._running = False


class SelectPrb(Action):

    def __init__(self, prbAction):
        super(SelectPrb, self).__init__()
        self._running = False
        self._prbAction = prbAction

    def invoke(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher:
            self._running = True
            self.__doSelect(dispatcher)

    def isInstantaneous(self):
        return False

    @process
    def __doSelect(self, dispatcher):
        self._completed = yield dispatcher.doSelectAction(self._prbAction)
        if self._completed:
            LOG_DEBUG('Select prebattle entity. Player has joined prebattle.')
        else:
            LOG_DEBUG('Select prebattle entity. Action was failed.')
        self._running = False


class DisconnectFromPeriphery(Action):
    connectionMgr = dependency.descriptor(IConnectionManager)
    gameplay = dependency.descriptor(IGameplayLogic)

    def isInstantaneous(self):
        return False

    def invoke(self):
        self._running = True
        self.gameplay.goToLoginByRQ()

    def isRunning(self):
        app = g_appLoader.getApp()
        if app:
            from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
            view = app.containerManager.getView(ViewTypes.DEFAULT)
            if view and view.settings.alias == VIEW_ALIAS.LOGIN and view.isCreated() and self.connectionMgr.isDisconnected():
                LOG_DEBUG('Disconnect action. Player came to login')
                self._completed = True
                self._running = False
        return self._running


class ConnectToPeriphery(Action):
    loginManager = dependency.descriptor(ILoginManager)
    lobbyContext = dependency.descriptor(ILobbyContext)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, peripheryID):
        super(ConnectToPeriphery, self).__init__()
        self.__host = g_preDefinedHosts.periphery(peripheryID)
        self.__endTime = None
        self.__credentials = self.lobbyContext.getCredentials()
        self.__wgcLogin = False
        return

    def isInstantaneous(self):
        return False

    def isRunning(self):
        if self.__endTime and self.__endTime <= BigWorld.time():
            self.__endTime = None
            self.__doConnect()
        return super(ConnectToPeriphery, self).isRunning()

    def invoke(self):
        self.__wgcLogin = self.loginManager.checkWgcAvailability()
        if self.__host and (self.__credentials or self.__wgcLogin):
            if not self.__wgcLogin:
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
        if not self.__wgcLogin:
            login, token2 = self.__credentials
        else:
            login = 'wgc'
            token2 = ''
        self.__addHandlers()
        self.loginManager.initiateRelogin(login, token2, getHostURL(self.__host, token2))

    def __addHandlers(self):
        g_eventBus.addListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.connectionMgr.onConnected += self.__onConnected
        self.connectionMgr.onRejected += self.__onRejected

    def __removeHandlers(self):
        g_eventBus.removeListener(LoginEventEx.ON_LOGIN_QUEUE_CLOSED, self.__onLoginQueueClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        self.connectionMgr.onConnected -= self.__onConnected
        self.connectionMgr.onRejected -= self.__onRejected

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
        self._running = not self._isActive

    def isRunning(self):
        if self._isActive:
            self._running = False
            self._completed = True
        return self._running

    def isInstantaneous(self):
        return False


class OnLobbyInitedAction(Action):

    def __init__(self, onInited=None):
        super(OnLobbyInitedAction, self).__init__()
        self.__isLobbyInited = False
        self.__onInited = onInited
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)

    def invoke(self):
        self._running = True
        self._completed = False
        if self.__isLobbyInited:
            onInited = self.__onInited
            if onInited and callable(onInited):
                onInited()
            self._completed = True
            self._running = False

    def __onLobbyInited(self, _):
        self.__isLobbyInited = True
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self.invoke()
