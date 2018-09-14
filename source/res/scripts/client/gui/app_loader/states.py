# Embedded file name: scripts/client/gui/app_loader/states.py
import BigWorld
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
        spaceID = ctx.guiSpace
        if spaceID == _SPACE_ID.UNDEFINED:
            if _isBattleReplayAutoStart():
                return None
            elif isShowStartupVideo():
                ctx.guiSpace = _SPACE_ID.INTRO_VIDEO
                return IntroVideoState()
            else:
                ctx.guiSpace = _SPACE_ID.LOGIN
                return LoginState()
        else:
            if spaceID == _SPACE_ID.LOGIN:
                return LoginState()
            if spaceID in _SPACE_ID.BATTLE_LOADING_IDS:
                return _createBattleLoadingState(spaceID)
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
        ctx.guiSpace = _SPACE_ID.LOGIN
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
        spaceID = ctx.guiSpace
        if spaceID == self.getSpaceID():
            return None
        elif not ctx.isConnected() and not _isBattleReplayPlaying():
            ctx.guiSpace = _SPACE_ID.LOGIN
            LOG_WARNING('Can not change GUI space to other, because client is not connected to game server.', ctx)
            return None
        elif spaceID == _SPACE_ID.LOBBY:
            return LobbyState()
        elif spaceID in _SPACE_ID.BATTLE_LOADING_IDS:
            return _createBattleLoadingState(spaceID)
        else:
            LOG_ERROR('State can not be switched', self, ctx)
            return None

    def _updateDscDesc(self, ctx):
        if ctx.dsnReason in (_REASON.EVENT, _REASON.KICK):
            self._dsnDesc = ctx.dsnDesc

    def _showDsnDialogIfNeed(self, appFactory, appNS):
        if self._dsnDesc is not None:
            appFactory.showDisconnectDialog(appNS, self._dsnDesc)
        return

    def _clearEntitiesAndSpaces(self):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        keepClientOnlySpaces = False
        if g_hangarSpace is not None and g_hangarSpace.inited:
            keepClientOnlySpaces = g_hangarSpace.spaceLoading()
        BigWorld.clearEntitiesAndSpaces(keepClientOnlySpaces)
        return


class ConnectionState(IGlobalState):

    def goNext(self, ctx):
        if not ctx.isConnected() and not _isBattleReplayPlaying():
            ctx.guiSpace = _SPACE_ID.LOGIN
        spaceID = ctx.guiSpace
        newState = None
        if spaceID != self.getSpaceID():
            if spaceID == _SPACE_ID.LOGIN:
                newState = LoginState()
            else:
                newState = self._getNextState(spaceID)
                if not newState:
                    LOG_ERROR('State can not be switched', self, ctx)
        return newState

    def _getNextState(self, spaceID):
        return None


@ReprInjector.simple()

class WaitingState(ConnectionState):

    def getSpaceID(self):
        return _SPACE_ID.WAITING

    def _getNextState(self, spaceID):
        if spaceID == _SPACE_ID.LOBBY:
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

    def _getNextState(self, spaceID):
        newState = None
        if spaceID in _SPACE_ID.BATTLE_LOADING_IDS:
            return _createBattleLoadingState(spaceID)
        else:
            return newState


@ReprInjector.simple()

class BattleLoadingState(ConnectionState):
    __slots__ = ('_spaceID', '_destroyLobby')

    def __init__(self, spaceID = None):
        super(BattleLoadingState, self).__init__()
        self._destroyLobby = True
        self._spaceID = spaceID

    def getSpaceID(self):
        return _SPACE_ID.BATTLE_LOADING

    def fini(self, ctx):
        super(BattleLoadingState, self).fini(ctx)
        self._destroyLobby = ctx.guiSpace == _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.detachCursor(appNS)
            if self._spaceID is None:
                return
            if self._spaceID == _SPACE_ID.FALLOUT_MULTI_TEAM_LOADING:
                appFactory.goToFalloutMultiTeamLoading(appNS)
            else:
                appFactory.goToBattleLoading(appNS)
        return

    def hideGUI(self, appFactory):
        if self._destroyLobby:
            appFactory.destroyLobby()

    def _getNextState(self, spaceID):
        newState = None
        if spaceID == _SPACE_ID.BATTLE:
            newState = self._createBattleState()
        elif spaceID == _SPACE_ID.LOBBY:
            newState = LobbyState()
        return newState

    def _createBattleState(self):
        return BattleState()


@ReprInjector.simple()

class BattleTutorialLoadingState(BattleLoadingState):

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.detachCursor(appNS)
            appFactory.goToTutorialLoading(appNS)

    def _createBattleState(self):
        return BattleTutorialState()


@ReprInjector.simple()

class ReplayLoadingState(BattleLoadingState):

    def hideGUI(self, appFactory):
        appFactory.hideLobby()

    def _createBattleState(self):
        return ReplayBattleState()


def _createBattleLoadingState(spaceID):
    if spaceID == _SPACE_ID.BATTLE_TUT_LOADING:
        return BattleTutorialLoadingState(spaceID)
    elif _isBattleReplayPlaying():
        return ReplayLoadingState(spaceID)
    else:
        return BattleLoadingState(spaceID)


@ReprInjector.simple()

class AbstractBattleState(ConnectionState):

    def getSpaceID(self):
        return _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        raise NotImplementedError

    def hideGUI(self, appFactory):
        raise NotImplementedError

    def _getNextState(self, spaceID):
        if spaceID == _SPACE_ID.WAITING:
            newState = WaitingState()
        else:
            newState = None
        return newState


@ReprInjector.simple()

class BattleState(AbstractBattleState):

    def __init__(self):
        super(BattleState, self).__init__()
        self._isInvokeTutorial = False

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED and not self._isInvokeTutorial:
            try:
                from tutorial import loader
                if loader.g_loader:
                    settingsID = 'BATTLE_QUESTS'
                    if loader.g_loader.areSettingsEnabled(settingsID):
                        loader.g_loader.run(settingsID)
                        self._isInvokeTutorial = True
            except ImportError:
                LOG_ERROR('Module tutorial not found')

        if appState == _STATE_ID.INITIALIZED:
            appFactory.goToBattle(appNS)

    def hideGUI(self, appFactory):
        if self._isInvokeTutorial:
            try:
                from tutorial import loader
                if loader.g_loader:
                    loader.g_loader.stop(restore=False)
            except (ImportError, AttributeError):
                LOG_ERROR('Module tutorial not found')

        appFactory.createLobby()
        appFactory.destroyBattle()


@ReprInjector.simple()

class BattleTutorialState(AbstractBattleState):

    def __init__(self):
        super(BattleTutorialState, self).__init__()
        self._isInvokeTutorial = False

    def showGUI(self, appFactory, appNS, appState):
        if appState in (_STATE_ID.INITIALIZING, _STATE_ID.INITIALIZED) and not self._isInvokeTutorial:
            try:
                from tutorial import loader
                if loader.g_loader:
                    loader.g_loader.run('BATTLE')
                    self._isInvokeTutorial = True
            except (ImportError, AttributeError):
                self._isInvokeTutorial = False
                LOG_ERROR('Module tutorial not found')

        if appState == _STATE_ID.INITIALIZED:
            appFactory.goToBattle(appNS)

    def hideGUI(self, appFactory):
        if self._isInvokeTutorial:
            try:
                from tutorial import loader
                if loader.g_loader:
                    loader.g_loader.stop(restore=False)
            except (ImportError, AttributeError):
                LOG_ERROR('Module tutorial not found')

        appFactory.createLobby()
        appFactory.destroyBattle()


@ReprInjector.simple()

class ReplayBattleState(BattleState):

    def hideGUI(self, appFactory):
        appFactory.showLobby()
        appFactory.destroyBattle()

    def _getNextState(self, spaceID):
        if spaceID == _SPACE_ID.WAITING:
            newState = ReplayLoadingState()
        else:
            newState = None
        return newState
