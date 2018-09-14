# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/states.py
import BigWorld
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.shared.utils.decorators import ReprInjector
from gui.Scaleform.Waiting import Waiting
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID, APP_NAME_SPACE
from gui.app_loader.settings import APP_STATE_ID as _STATE_ID
from gui.app_loader.settings import DISCONNECT_REASON as _REASON
from helpers import isShowStartupVideo

def _isBattleReplayAutoStart():
    import BattleReplay
    return BattleReplay.g_replayCtrl.autoStartBattleReplay()


def _isBattleReplayPlaying():
    import BattleReplay
    return BattleReplay.g_replayCtrl.isPlaying


def _isBattleReplayRewind():
    import BattleReplay
    return BattleReplay.g_replayCtrl.rewind


def _isBattleReplayFinished():
    import BattleReplay
    return BattleReplay.isFinished()


def _enableTimeWrapInReplay():
    import BattleReplay
    BattleReplay.g_replayCtrl.onCommonSwfUnloaded()


def _disableTimeWrapInReplay():
    import BattleReplay
    BattleReplay.g_replayCtrl.onCommonSwfLoaded()


class IGlobalState(object):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.UNDEFINED

    def init(self, ctx):
        pass

    def update(self, ctx):
        pass

    def fini(self, ctx):
        pass

    def showGUI(self, appFactory, appNS, appState):
        pass

    def updateGUI(self, appFactory, appNS):
        pass

    def hideGUI(self, appFactory):
        pass

    def goNext(self, ctx):
        return None


@ReprInjector.simple()
class StartState(IGlobalState):
    __slots__ = ()

    def goNext(self, ctx):
        spaceID = ctx.guiSpaceID
        if spaceID == _SPACE_ID.UNDEFINED:
            if _isBattleReplayAutoStart():
                return None
            elif isShowStartupVideo():
                ctx.guiSpaceID = _SPACE_ID.INTRO_VIDEO
                return IntroVideoState()
            else:
                ctx.guiSpaceID = _SPACE_ID.LOGIN
                return LoginState()
        else:
            if spaceID == _SPACE_ID.LOGIN:
                return LoginState()
            if spaceID == _SPACE_ID.BATTLE_LOADING:
                return BattleLoadingState(ctx.arenaGuiType)
            LOG_ERROR('State can not be switched', self, ctx)
        return None


@ReprInjector.simple()
class IntroVideoState(IGlobalState):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.INTRO_VIDEO

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZING:
            appFactory.goToIntroVideo(appNS)

    def goNext(self, ctx):
        ctx.guiSpaceID = _SPACE_ID.LOGIN
        return LoginState()


@ReprInjector.simple()
class LoginState(IGlobalState):
    __slots__ = ('_dsnDesc',)

    def __init__(self):
        super(LoginState, self).__init__()
        self._dsnDesc = None
        return

    def getSpaceID(self):
        return _SPACE_ID.LOGIN

    def init(self, ctx):
        self._clearEntitiesAndSpaces()
        self._updateDscDesc(ctx)

    def update(self, ctx):
        self._clearEntitiesAndSpaces()
        self._updateDscDesc(ctx)

    def fini(self, ctx):
        if Waiting.isOpened('login'):
            Waiting.hide('login')
        ctx.resetDsn()
        self._dsnDesc = None
        return

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLogin(appNS)
            self._showDsnDialogIfNeed(appFactory, appNS)

    def updateGUI(self, appFactory, appNS):
        self._showDsnDialogIfNeed(appFactory, appNS)

    def goNext(self, ctx):
        spaceID = ctx.guiSpaceID
        if not ctx.isConnected() and not _isBattleReplayPlaying():
            ctx.guiSpaceID = _SPACE_ID.LOGIN
            LOG_WARNING('Can not change GUI space to other, because client is not connected to game server.', ctx)
            return None
        elif spaceID == _SPACE_ID.LOBBY:
            return LobbyState()
        elif spaceID == _SPACE_ID.BATTLE_LOADING:
            return BattleLoadingState(ctx.arenaGuiType)
        elif spaceID == _SPACE_ID.WAITING:
            return WaitingState()
        else:
            LOG_ERROR('State can not be switched', self, ctx)
            return None

    def _updateDscDesc(self, ctx):
        if ctx.dsnReason in (_REASON.EVENT, _REASON.KICK, _REASON.ERROR):
            self._dsnDesc = ctx.dsnDesc

    def _showDsnDialogIfNeed(self, appFactory, appNS):
        if self._dsnDesc is not None:
            appFactory.showDisconnectDialog(appNS, self._dsnDesc)
        return

    @staticmethod
    def _clearEntitiesAndSpaces():
        from gui.shared.utils.HangarSpace import g_hangarSpace
        keepClientOnlySpaces = False
        if g_hangarSpace is not None and g_hangarSpace.inited:
            keepClientOnlySpaces = g_hangarSpace.spaceLoading()
        BigWorld.clearEntitiesAndSpaces(keepClientOnlySpaces)
        return


class ConnectionState(IGlobalState):
    __slots__ = ('_checkSpace',)

    def __init__(self, checkSpace=True):
        super(ConnectionState, self).__init__()
        self._checkSpace = checkSpace

    def goNext(self, ctx):
        if not ctx.isConnected() and not _isBattleReplayPlaying():
            ctx.guiSpaceID = _SPACE_ID.LOGIN
        spaceID = ctx.guiSpaceID
        newState = None
        if spaceID != self.getSpaceID() or not self._checkSpace:
            if spaceID == _SPACE_ID.LOGIN:
                newState = LoginState()
            else:
                newState = self._getNextState(ctx)
                if not newState and self._checkSpace:
                    LOG_ERROR('State can not be switched', self, ctx)
        return newState

    def _getNextState(self, ctx):
        return None


@ReprInjector.simple()
class WaitingState(ConnectionState):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.WAITING

    def _getNextState(self, ctx):
        if ctx.guiSpaceID == _SPACE_ID.LOBBY:
            newState = LobbyState()
        else:
            newState = None
        return newState


@ReprInjector.simple()
class LobbyState(ConnectionState):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.LOBBY

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLobby(appNS)

    def hideGUI(self, appFactory):
        appFactory.detachCursor(APP_NAME_SPACE.SF_LOBBY)

    def _getNextState(self, ctx):
        newState = None
        if ctx.guiSpaceID == _SPACE_ID.BATTLE_LOADING:
            return BattleLoadingState(ctx.arenaGuiType)
        else:
            if ctx.guiSpaceID == _SPACE_ID.WAITING:
                newState = WaitingState()
            return newState


class _ArenaState(ConnectionState):
    __slots__ = ('_arenaGuiType',)

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN, checkSpace=True):
        super(_ArenaState, self).__init__(checkSpace=checkSpace)
        self._arenaGuiType = arenaGuiType


@ReprInjector.simple()
class BattleLoadingState(_ArenaState):
    __slots__ = ('_doStartBattle',)

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(BattleLoadingState, self).__init__(arenaGuiType=arenaGuiType, checkSpace=False)
        self._doStartBattle = False

    def getSpaceID(self):
        return _SPACE_ID.BATTLE_LOADING

    def hideGUI(self, appFactory):
        if self._doStartBattle:
            _enableTimeWrapInReplay()
            appFactory.destroyLobby()
        else:
            appFactory.hideBattle()
            appFactory.reloadLobbyPackages()
            appFactory.destroyBattle()
            appFactory.showLobby()

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.hideLobby()
            appFactory.loadBattlePage(appNS, arenaGuiType=self._arenaGuiType)

    def updateGUI(self, appFactory, appNS):
        if appNS != APP_NAME_SPACE.SF_BATTLE:
            return
        appFactory.showBattle()
        appFactory.goToBattleLoading(appNS)

    def _getNextState(self, ctx):
        spaceID = ctx.guiSpaceID
        newState = None
        if spaceID == _SPACE_ID.BATTLE:
            self._doStartBattle = True
            newState = self._createBattleState()
        elif spaceID == _SPACE_ID.LOBBY:
            newState = LobbyState()
        elif spaceID == _SPACE_ID.WAITING:
            newState = WaitingState()
        return newState

    def _createBattleState(self):
        if _isBattleReplayPlaying():
            return ReplayBattleState(self._arenaGuiType)
        else:
            return BattleState(self._arenaGuiType)


@ReprInjector.simple()
class ReplayLoadingState(BattleLoadingState):
    __slots__ = ()

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.showBattle()
            appFactory.loadBattlePage(appNS, self._arenaGuiType)
            appFactory.goToBattleLoading(appNS)

    def hideGUI(self, appFactory):
        _enableTimeWrapInReplay()

    def _createBattleState(self):
        return ReplayBattleState(self._arenaGuiType)


@ReprInjector.simple()
class BattleState(_ArenaState):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.goToBattlePage(appNS)

    def hideGUI(self, appFactory):
        appFactory.createLobby()
        appFactory.destroyBattle()

    def _getNextState(self, ctx):
        if ctx.guiSpaceID == _SPACE_ID.WAITING:
            newState = WaitingState()
        else:
            newState = None
        return newState


@ReprInjector.simple()
class ReplayBattleState(BattleState):
    __slots__ = ()

    def hideGUI(self, appFactory):
        _disableTimeWrapInReplay()

    def _getNextState(self, ctx):
        if ctx.guiSpaceID == _SPACE_ID.WAITING:
            newState = ReplayWaiting()
        else:
            newState = None
        return newState


class ReplayWaiting(WaitingState):

    def showGUI(self, appFactory, appNS, appState):
        if _isBattleReplayPlaying() and (_isBattleReplayFinished() or not _isBattleReplayRewind()):
            appFactory.destroyBattle()

    def _getNextState(self, ctx):
        if ctx.guiSpaceID == _SPACE_ID.BATTLE_LOADING:
            newState = ReplayLoadingState(arenaGuiType=ctx.arenaGuiType)
        else:
            newState = None
        return newState
