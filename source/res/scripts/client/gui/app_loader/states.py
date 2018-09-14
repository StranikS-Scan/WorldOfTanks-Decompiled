# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/states.py
import BigWorld
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.shared.utils.decorators import ReprInjector
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.app_loader.settings import APP_STATE_ID as _STATE_ID
from gui.app_loader.settings import DISCONNECT_REASON as _REASON
from helpers import isShowStartupVideo

def _isBattleReplayAutoStart():
    import BattleReplay
    return BattleReplay.g_replayCtrl.autoStartBattleReplay()


def _isBattleReplayPlaying():
    import BattleReplay
    return BattleReplay.g_replayCtrl.isPlaying


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
                return _createBattleLoadingState(ctx)
            LOG_ERROR('State can not be switched', self, ctx)
        return None


@ReprInjector.simple()
class IntroVideoState(IGlobalState):

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
            return _createBattleLoadingState(ctx)
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

    def getSpaceID(self):
        return _SPACE_ID.LOBBY

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLobby(appNS)

    def _getNextState(self, ctx):
        newState = None
        return _createBattleLoadingState(ctx) if ctx.guiSpaceID == _SPACE_ID.BATTLE_LOADING else newState


@ReprInjector.simple()
class BattleLoadingState(ConnectionState):
    __slots__ = ('_arenaGuiType', '_destroyLobby')

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN, checkSpace=True):
        super(BattleLoadingState, self).__init__(checkSpace=checkSpace)
        self._arenaGuiType = arenaGuiType
        self._destroyLobby = True

    def fini(self, ctx):
        super(BattleLoadingState, self).fini(ctx)
        self._destroyLobby = ctx.guiSpaceID == _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.detachCursor(appNS)
            appFactory.goToBattleLoading(appNS, self._arenaGuiType)

    def hideGUI(self, appFactory):
        if self._destroyLobby:
            appFactory.destroyLobby()

    def _getNextState(self, ctx):
        spaceID = ctx.guiSpaceID
        newState = None
        if spaceID == _SPACE_ID.BATTLE:
            newState = self._createBattleState()
        elif spaceID == _SPACE_ID.LOBBY:
            newState = LobbyState()
        return newState

    def _createBattleState(self):
        return BattleState(self._arenaGuiType)


@ReprInjector.simple()
class ReplayLoadingState(BattleLoadingState):
    __slots__ = ()

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(ReplayLoadingState, self).__init__(arenaGuiType=arenaGuiType, checkSpace=False)

    def hideGUI(self, appFactory):
        appFactory.hideLobby()

    def _createBattleState(self):
        return ReplayBattleState(self._arenaGuiType)


def _createBattleLoadingState(ctx):
    if _isBattleReplayPlaying():
        return ReplayLoadingState(ctx.arenaGuiType)
    else:
        return BattleLoadingState(ctx.arenaGuiType)


@ReprInjector.simple()
class BattleState(ConnectionState):

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(BattleState, self).__init__()
        self._arenaGuiType = arenaGuiType

    def getSpaceID(self):
        return _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.goToBattle(appNS, self._arenaGuiType)

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

    def hideGUI(self, appFactory):
        appFactory.showLobby()
        appFactory.destroyBattle()

    def _getNextState(self, ctx):
        if ctx.guiSpaceID == _SPACE_ID.WAITING:
            newState = ReplayLoadingState(arenaGuiType=self._arenaGuiType)
        else:
            newState = None
        return newState
