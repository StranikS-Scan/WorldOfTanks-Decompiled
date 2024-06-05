# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/spaces.py
import BattleReplay
import BigWorld
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from constants import ARENA_GUI_TYPE, ACCOUNT_KICK_REASONS
from gui import DialogsInterface
from gui.Scaleform.Waiting import Waiting
from gui.app_loader.settings import APP_NAME_SPACE
from gui.game_loading import loading as gameLoading
from gui.game_loading.state_machine.const import GameLoadingStates
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent, LoginEvent, ViewEventType, CloseWindowEvent
from gui.shared.utils.decorators import ReprInjector
from helpers import dependency, isPlayerAvatar
from skeletons.connection_mgr import DisconnectReason, IConnectionManager
from skeletons.gameplay import IGameplayLogic
from skeletons.gui.app_loader import IGlobalSpace, GuiGlobalSpaceID as _SPACE_ID, ApplicationStateID
from skeletons.gui.game_control import IReloginController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.login_manager import ILoginManager
from skeletons.gui.shared.utils import IHangarSpace
_REASON = DisconnectReason

def _disableTimeWarpInReplay():
    BattleReplay.g_replayCtrl.disableTimeWarp()


def _acceptVersionDiffering():
    BattleReplay.g_replayCtrl.acceptVersionDiffering()


def _stopBattleReplay():
    BattleReplay.g_replayCtrl.stop()


def _onReplayBattleLoadingFinished():
    BattleReplay.g_replayCtrl.onBattleLoadingFinished()


class ShowDialogAction(object):
    __slots__ = ()

    def getAppNS(self):
        return APP_NAME_SPACE.SF_LOBBY

    def doAction(self):
        raise NotImplementedError


class DisconnectDialogAction(ShowDialogAction):
    __slots__ = ('__reason', '__kickReasonType', '__expiryTime')

    def __init__(self, reason, kickReasonType=ACCOUNT_KICK_REASONS.UNKNOWN, expiryTime=None):
        super(DisconnectDialogAction, self).__init__()
        self.__reason = reason
        self.__kickReasonType = kickReasonType
        self.__expiryTime = expiryTime

    def doAction(self):
        DialogsInterface.showDisconnect(self.__reason, self.__kickReasonType, self.__expiryTime)


class ReplayVersionDiffersDialogAction(ShowDialogAction):
    __slots__ = ()

    @adisp_process
    def doAction(self):
        result = yield DialogsInterface.showI18nConfirmDialog('replayNotification')
        if result:
            _acceptVersionDiffering()
        else:
            _stopBattleReplay()


class ReplayFinishDialogAction(ShowDialogAction):

    def getAppNS(self):
        return APP_NAME_SPACE.SF_BATTLE

    @adisp_process
    def doAction(self):
        result = yield DialogsInterface.showI18nConfirmDialog('replayStopped')
        if result:
            BigWorld.callback(0.0, _stopBattleReplay)


class CloseGameLoadingMixin(object):

    def __init__(self, *args, **kwargs):
        super(CloseGameLoadingMixin, self).__init__(*args, **kwargs)
        self.__callbackID = None
        return

    def init(self, *args, **kwargs):
        super(CloseGameLoadingMixin, self).init(*args, **kwargs)
        if not Waiting.isVisible():
            self._closeGameLoading()
            return
        for scope in (EVENT_BUS_SCOPE.LOBBY, EVENT_BUS_SCOPE.BATTLE):
            g_eventBus.addListener(LobbySimpleEvent.WAITING_HIDDEN, self.__waitingHiddenHandler, scope=scope)

    def fini(self, *args, **kwargs):
        self._unsubscribe()
        super(CloseGameLoadingMixin, self).fini(*args, **kwargs)

    def _closeGameLoading(self):
        gameLoading.getLoader().idl()

    def _unsubscribe(self):
        self.__cancelCallback()
        for scope in (EVENT_BUS_SCOPE.LOBBY, EVENT_BUS_SCOPE.BATTLE):
            g_eventBus.removeListener(LobbySimpleEvent.WAITING_HIDDEN, self.__waitingHiddenHandler, scope=scope)

    def __cancelCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __waitingHiddenHandler(self, _):
        self.__cancelCallback()
        self.__callbackID = BigWorld.callback(0, self.__delayedWaitingHiddenHandler)

    def __delayedWaitingHiddenHandler(self):
        self.__callbackID = None
        if not Waiting.isVisible():
            self._unsubscribe()
            self._closeGameLoading()
        return


@ReprInjector.simple()
class LoginSpace(IGlobalSpace):
    __slots__ = ('_action', '_isPlayerLoadingActive')
    hangarSpace = dependency.descriptor(IHangarSpace)
    connectionMgr = dependency.descriptor(IConnectionManager)
    loginManager = dependency.descriptor(ILoginManager)
    reloginCtrl = dependency.descriptor(IReloginController)

    def __init__(self, action=None):
        super(LoginSpace, self).__init__()
        self._action = action
        self._isPlayerLoadingActive = False

    def getSpaceID(self):
        return _SPACE_ID.LOGIN

    def init(self):
        self._clearEntitiesAndSpaces()
        BigWorld.notifySpaceChange('spaces/login_space')
        self.connectionMgr.onQueued += self._onLoginFailed
        self.connectionMgr.onConnected += self._onTryToLogin
        self.connectionMgr.onDisconnected += self._onDisconnected
        self.connectionMgr.onKickWhileLoginReceived += self._onLoginFailed
        self.loginManager.onConnectionInitiated += self._onTryToLogin
        self.loginManager.onConnectionRejected += self._onLoginFailed
        g_eventBus.addListener(LoginEvent.LOGIN_VIEW_READY, self._loginViewReadyHandler)
        g_eventBus.addListener(LoginEvent.CONNECTION_FAILED, self._onLoginFailed)
        g_eventBus.addListener(CloseWindowEvent.EULA_CLOSED, self._onEULAClosed)

    def fini(self):
        self.connectionMgr.onQueued -= self._onLoginFailed
        self.connectionMgr.onConnected -= self._onTryToLogin
        self.connectionMgr.onDisconnected -= self._onDisconnected
        self.connectionMgr.onKickWhileLoginReceived -= self._onLoginFailed
        self.loginManager.onConnectionInitiated -= self._onTryToLogin
        self.loginManager.onConnectionRejected -= self._onLoginFailed
        g_eventBus.removeListener(LoginEvent.LOGIN_VIEW_READY, self._loginViewReadyHandler)
        g_eventBus.removeListener(LoginEvent.CONNECTION_FAILED, self._onLoginFailed)
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(CloseWindowEvent.EULA_CLOSED, self._onEULAClosed)

    @property
    def __isReconnectActive(self):
        from gui.prb_control.dispatcher import g_prbLoader
        invitesManager = g_prbLoader.getInvitesManager()
        return self.reloginCtrl.isActive or invitesManager.isAcceptChainActive

    def setup(self, action=None):
        self._action = action

    def update(self):
        self._clearEntitiesAndSpaces()

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLogin(appNS)
            g_eventBus.addListener(ViewEventType.LOAD_VIEW, self._loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
            self._doActionIfNeed(appNS)

    def updateGUI(self, appFactory, appNS):
        self._doActionIfNeed(appNS)

    def hideGUI(self, appFactory, newState):
        worker = appFactory.getWaitingWorker()
        if worker.isWaitingShown(messageID=R.strings.waiting.login()):
            worker.hide(R.strings.waiting.login())
        self._action = None
        return

    def _doActionIfNeed(self, appNS):
        if self._action is not None and self._action.getAppNS() == appNS:
            self._action.doAction()
        return

    def _onDisconnected(self, *_):
        if not self.__isReconnectActive:
            self._onLoginFailed()

    def _onLoginFailed(self, *_):
        gameLoading.getLoader().loginScreen()
        self._isPlayerLoadingActive = False

    def _onTryToLogin(self, *_):
        if not self._isPlayerLoadingActive:
            gameLoading.getLoader().playerLoading()
            self._isPlayerLoadingActive = True

    def _onEULAClosed(self, event):
        if event.isAgree:
            gameLoading.getLoader().playerLoading(True)
            self._isPlayerLoadingActive = True

    def _loginViewReadyHandler(self, *_):
        if not self._isPlayerLoadingActive and not self.__isReconnectActive:
            gameLoading.getLoader().loginScreen()

    def _loadViewHandler(self, event):
        self._isPlayerLoadingActive = False
        gameLoading.getLoader().loginScreen()

    @classmethod
    def _clearEntitiesAndSpaces(cls):
        keepClientOnlySpaces = False
        if cls.hangarSpace is not None and cls.hangarSpace.inited:
            keepClientOnlySpaces = cls.hangarSpace.spaceLoading()
        BigWorld.clearEntitiesAndSpaces(keepClientOnlySpaces)
        return


@ReprInjector.simple()
class WaitingSpace(IGlobalSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.WAITING


@ReprInjector.simple()
class LobbySpace(CloseGameLoadingMixin, IGlobalSpace):
    __slots__ = ()
    gameplay = dependency.descriptor(IGameplayLogic)

    def init(self, *args, **kwargs):
        super(LobbySpace, self).init(*args, **kwargs)
        g_eventBus.addListener(LoginEvent.DISCONNECTION_STARTED, self._disconnectStartHandler)

    def fini(self, *args, **kwargs):
        g_eventBus.removeListener(LoginEvent.DISCONNECTION_STARTED, self._disconnectStartHandler)
        super(LobbySpace, self).fini(*args, **kwargs)

    def getSpaceID(self):
        return _SPACE_ID.LOBBY

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLobby(appNS)
            if gameLoading.getLoader().isStateEntered(GameLoadingStates.LOGIN_SCREEN.value):
                self._closeGameLoading()

    def hideGUI(self, appFactory, newState):
        appFactory.detachCursor(APP_NAME_SPACE.SF_LOBBY)

    @staticmethod
    def _disconnectStartHandler(*_):
        gameLoading.getLoader().playerLoading()


class _ArenaSpace(IGlobalSpace):
    __slots__ = ('_arenaGuiType',)

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(_ArenaSpace, self).__init__()
        self._arenaGuiType = arenaGuiType


@ReprInjector.simple()
class BattleLoadingSpace(CloseGameLoadingMixin, _ArenaSpace):
    __slots__ = ()

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(BattleLoadingSpace, self).__init__(arenaGuiType=arenaGuiType)

    def getSpaceID(self):
        return _SPACE_ID.BATTLE_LOADING

    def hideGUI(self, appFactory, newState):
        if newState.getSpaceID() == _SPACE_ID.BATTLE:
            _onReplayBattleLoadingFinished()
        else:
            appFactory.hideBattle()
            appFactory.reloadLobbyPackages()
            appFactory.destroyBattle()
            appFactory.createLobby()
            appFactory.showLobby()

    def showGUI(self, appFactory, appNS, appState):
        isValidAvatar = isPlayerAvatar() and not g_playerEvents.isPlayerEntityChanging
        if appState == ApplicationStateID.INITIALIZED and isValidAvatar:
            appFactory.loadBattlePage(appNS, arenaGuiType=self._arenaGuiType)

    def updateGUI(self, appFactory, appNS):
        if appNS != APP_NAME_SPACE.SF_BATTLE:
            return
        appFactory.showBattle()
        appFactory.goToBattleLoading(appNS)
        if BattleReplay.g_replayCtrl.getAutoStartFileName():
            super(BattleLoadingSpace, self)._closeGameLoading()

    def _closeGameLoading(self):
        lobbyContext = dependency.instance(ILobbyContext)
        if lobbyContext.getGuiCtx().get('skipHangar', False):
            return
        if not BattleReplay.g_replayCtrl.getAutoStartFileName():
            super(BattleLoadingSpace, self)._closeGameLoading()


@ReprInjector.simple()
class ReplayLoadingSpace(BattleLoadingSpace):
    __slots__ = ()

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.destroyLobby()
            appFactory.showBattle()
            appFactory.loadBattlePage(appNS, self._arenaGuiType)
            appFactory.goToBattleLoading(appNS)

    def hideGUI(self, appFactory, newState):
        _onReplayBattleLoadingFinished()


@ReprInjector.simple()
class BattleSpace(_ArenaSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.goToBattlePage(appNS)


@ReprInjector.simple()
class ReplayBattleSpace(BattleSpace):
    __slots__ = ()

    def hideGUI(self, appFactory, newState):
        _disableTimeWarpInReplay()
