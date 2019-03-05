# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/spaces.py
import BigWorld
import BattleReplay
from PlayerEvents import g_playerEvents
from adisp import process
from constants import ARENA_GUI_TYPE
from gui import DialogsInterface
from gui.shared.utils.decorators import ReprInjector
from gui.Scaleform.Waiting import Waiting
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID, APP_NAME_SPACE
from gui.app_loader.settings import APP_STATE_ID as _STATE_ID
from helpers import dependency, isPlayerAvatar
from skeletons.connection_mgr import DisconnectReason
from skeletons.gui.shared.utils import IHangarSpace
_REASON = DisconnectReason

def _enableTimeWrapInReplay():
    BattleReplay.g_replayCtrl.enableTimeWrap()


def _disableTimeWrapInReplay():
    BattleReplay.g_replayCtrl.disableTimeWrap()


def _acceptVersionDiffering():
    BattleReplay.g_replayCtrl.acceptVersionDiffering()


def _stopBattleReplay():
    BattleReplay.g_replayCtrl.stop()


class GlobalSpace(object):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.UNDEFINED

    def init(self):
        pass

    def update(self):
        pass

    def fini(self):
        pass

    def showGUI(self, appFactory, appNS, appState):
        pass

    def updateGUI(self, appFactory, appNS):
        pass

    def hideGUI(self, appFactory, newState):
        pass


@ReprInjector.simple()
class IntroVideoSpace(GlobalSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.INTRO_VIDEO

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZING:
            appFactory.goToIntroVideo(appNS)


class ShowDialogAction(object):
    __slots__ = ()

    def getAppNS(self):
        return APP_NAME_SPACE.SF_LOBBY

    def doAction(self):
        raise NotImplementedError


class DisconnectDialogAction(ShowDialogAction):
    __slots__ = ('__reason', '__isBan', '__expiryTime')

    def __init__(self, reason, isBan=False, expiryTime=None):
        super(DisconnectDialogAction, self).__init__()
        self.__reason = reason
        self.__isBan = isBan
        self.__expiryTime = expiryTime

    def doAction(self):
        DialogsInterface.showDisconnect(self.__reason, self.__isBan, self.__expiryTime)


class ReplayVersionDiffersDialogAction(ShowDialogAction):
    __slots__ = ()

    @process
    def doAction(self):
        result = yield DialogsInterface.showI18nConfirmDialog('replayNotification')
        if result:
            _acceptVersionDiffering()
        else:
            _stopBattleReplay()


class ReplayFinishDialogAction(ShowDialogAction):

    def getAppNS(self):
        return APP_NAME_SPACE.SF_BATTLE

    @process
    def doAction(self):
        result = yield DialogsInterface.showI18nConfirmDialog('replayStopped')
        if result:
            BigWorld.callback(0.0, _stopBattleReplay)


@ReprInjector.simple()
class LoginSpace(GlobalSpace):
    __slots__ = ('_action',)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, action=None):
        super(LoginSpace, self).__init__()
        self._action = action

    def getSpaceID(self):
        return _SPACE_ID.LOGIN

    def init(self):
        self._clearEntitiesAndSpaces()

    def update(self):
        self._clearEntitiesAndSpaces()

    def fini(self):
        if Waiting.isOpened('login'):
            Waiting.hide('login')
        self._action = None
        return

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLogin(appNS)
            self._doActionIfNeed(appNS)

    def updateGUI(self, appFactory, appNS):
        self._doActionIfNeed(appNS)

    def _doActionIfNeed(self, appNS):
        if self._action is not None and self._action.getAppNS() == appNS:
            self._action.doAction()
        return

    @classmethod
    def _clearEntitiesAndSpaces(cls):
        keepClientOnlySpaces = False
        if cls.hangarSpace is not None and cls.hangarSpace.inited:
            keepClientOnlySpaces = cls.hangarSpace.spaceLoading()
        BigWorld.clearEntitiesAndSpaces(keepClientOnlySpaces)
        return


@ReprInjector.simple()
class WaitingSpace(GlobalSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.WAITING


@ReprInjector.simple()
class LobbySpace(GlobalSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.LOBBY

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLobby(appNS)

    def hideGUI(self, appFactory, newState):
        appFactory.detachCursor(APP_NAME_SPACE.SF_LOBBY)


class _ArenaSpace(GlobalSpace):
    __slots__ = ('_arenaGuiType',)

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(_ArenaSpace, self).__init__()
        self._arenaGuiType = arenaGuiType


@ReprInjector.simple()
class BattleLoadingSpace(_ArenaSpace):
    __slots__ = ()

    def __init__(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        super(BattleLoadingSpace, self).__init__(arenaGuiType=arenaGuiType)

    def getSpaceID(self):
        return _SPACE_ID.BATTLE_LOADING

    def hideGUI(self, appFactory, newState):
        if newState.getSpaceID() == _SPACE_ID.BATTLE:
            _enableTimeWrapInReplay()
        else:
            appFactory.hideBattle()
            appFactory.reloadLobbyPackages()
            appFactory.destroyBattle()
            appFactory.createLobby()
            appFactory.showLobby()

    def showGUI(self, appFactory, appNS, appState):
        appFactory.destroyLobby()
        isValidAvatar = isPlayerAvatar() and not g_playerEvents.isPlayerEntityChanging
        if appState == _STATE_ID.INITIALIZED and isValidAvatar:
            appFactory.loadBattlePage(appNS, arenaGuiType=self._arenaGuiType)

    def updateGUI(self, appFactory, appNS):
        if appNS != APP_NAME_SPACE.SF_BATTLE:
            return
        appFactory.showBattle()
        appFactory.goToBattleLoading(appNS)


@ReprInjector.simple()
class ReplayLoadingSpace(BattleLoadingSpace):
    __slots__ = ()

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.destroyLobby()
            appFactory.showBattle()
            appFactory.loadBattlePage(appNS, self._arenaGuiType)
            appFactory.goToBattleLoading(appNS)

    def hideGUI(self, appFactory, newState):
        _enableTimeWrapInReplay()


@ReprInjector.simple()
class BattleSpace(_ArenaSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.BATTLE

    def showGUI(self, appFactory, appNS, appState):
        if appState == _STATE_ID.INITIALIZED:
            appFactory.goToBattlePage(appNS)

    def hideGUI(self, appFactory, newState):
        appFactory.createLobby()
        appFactory.destroyBattle()


@ReprInjector.simple()
class ReplayBattleSpace(BattleSpace):
    __slots__ = ()

    def hideGUI(self, appFactory, newState):
        _disableTimeWrapInReplay()
