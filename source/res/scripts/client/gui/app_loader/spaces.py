# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/spaces.py
import BigWorld
import BattleReplay
from PlayerEvents import g_playerEvents
from adisp import process
from constants import ARENA_GUI_TYPE, ACCOUNT_KICK_REASONS
from gui import DialogsInterface
from gui.impl.gen import R
from gui.shared.utils.decorators import ReprInjector
from gui.app_loader.settings import APP_NAME_SPACE
from helpers import dependency, isPlayerAvatar
from skeletons.gui.app_loader import IGlobalSpace, GuiGlobalSpaceID as _SPACE_ID, ApplicationStateID
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


@ReprInjector.simple()
class IntroVideoSpace(IGlobalSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.INTRO_VIDEO

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZING:
            appFactory.goToIntroVideo(appNS)


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
class LoginSpace(IGlobalSpace):
    __slots__ = ('_action',)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, action=None):
        super(LoginSpace, self).__init__()
        self._action = action

    def getSpaceID(self):
        return _SPACE_ID.LOGIN

    def init(self):
        self._clearEntitiesAndSpaces()
        BigWorld.notifySpaceChange('spaces/login_space')

    def setup(self, action=None):
        self._action = action

    def update(self):
        self._clearEntitiesAndSpaces()

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLogin(appNS)
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
class LobbySpace(IGlobalSpace):
    __slots__ = ()

    def getSpaceID(self):
        return _SPACE_ID.LOBBY

    def showGUI(self, appFactory, appNS, appState):
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.attachCursor(appNS)
            appFactory.goToLobby(appNS)

    def hideGUI(self, appFactory, newState):
        appFactory.detachCursor(APP_NAME_SPACE.SF_LOBBY)


class _ArenaSpace(IGlobalSpace):
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
        isValidAvatar = isPlayerAvatar() and not g_playerEvents.isPlayerEntityChanging
        if appState == ApplicationStateID.INITIALIZED and isValidAvatar:
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
        if appState == ApplicationStateID.INITIALIZED:
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
        if appState == ApplicationStateID.INITIALIZED:
            appFactory.goToBattlePage(appNS)


@ReprInjector.simple()
class ReplayBattleSpace(BattleSpace):
    __slots__ = ()

    def hideGUI(self, appFactory, newState):
        _disableTimeWrapInReplay()
