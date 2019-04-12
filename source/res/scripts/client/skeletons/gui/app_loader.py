# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/app_loader.py
import typing
from Event import Event
from constants import ARENA_GUI_TYPE

class GuiGlobalSpaceID(object):
    UNDEFINED = 0
    WAITING = 1
    INTRO_VIDEO = 2
    LOGIN = 3
    LOBBY = 4
    BATTLE_LOADING = 5
    BATTLE = 6


class ApplicationStateID(object):
    NOT_CREATED = 0
    INITIALIZING = 1
    INITIALIZED = 2


class IGlobalSpace(object):
    __slots__ = ()

    def getSpaceID(self):
        return GuiGlobalSpaceID.UNDEFINED

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


class IWaitingWidget(object):

    def showWaiting(self, messageID):
        pass

    def hideWaiting(self):
        pass

    def setCallback(self, callback=None):
        pass

    def cancelCallback(self):
        pass


class IWaitingWorker(object):
    __slots__ = ()

    def getWaitingView(self, isBlocking):
        raise NotImplementedError

    def isWaitingShown(self, messageID=None):
        raise NotImplementedError

    def getWaitingTask(self, messageID):
        raise NotImplementedError

    def getSuspendedWaitingTask(self, messageID):
        raise NotImplementedError

    def show(self, messageID, isSingle=False, interruptCallback=None, isBlocking=True):
        raise NotImplementedError

    def hide(self, messageID):
        raise NotImplementedError

    def suspend(self):
        raise NotImplementedError

    def resume(self):
        raise NotImplementedError

    def isSuspended(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def cancelCallback(self):
        raise NotImplementedError

    def snapshort(self):
        return {}


class IAppFactory(object):
    __slots__ = ()

    def hasApp(self, appNS):
        return False

    def getApp(self, appNS=None):
        return None

    def getDefLobbyApp(self):
        return None

    def getDefBattleApp(self):
        return None

    def getWaitingWorker(self):
        return None

    def createLobby(self):
        pass

    def reloadLobbyPackages(self):
        pass

    def destroyLobby(self):
        pass

    def showLobby(self):
        pass

    def hideLobby(self):
        pass

    def showBattle(self):
        pass

    def hideBattle(self):
        pass

    def createBattle(self, arenaGuiType):
        pass

    def destroyBattle(self):
        pass

    def destroy(self):
        pass

    def attachCursor(self, appNS, flags=0):
        pass

    def detachCursor(self, appNS):
        pass

    def syncCursor(self, appNS, flags=0):
        pass

    def goToIntroVideo(self, appNS):
        pass

    def goToLogin(self, appNS):
        pass

    def goToLobby(self, appNS):
        pass

    def loadBattlePage(self, appNS, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        pass

    def goToBattleLoading(self, appNS):
        pass

    def goToBattlePage(self, appNS):
        pass

    def handleKey(self, appNS, isDown, key, mods):
        return False


class IAppLoader(object):
    onGUISpaceLeft = None
    onGUISpaceEntered = None

    def init(self, appFactory):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def getSpaceID(self):
        raise NotImplementedError

    def getAppStateID(self, appNS):
        raise NotImplementedError

    def getApp(self, appNS=None):
        raise NotImplementedError

    def getDefLobbyApp(self):
        raise NotImplementedError

    def getDefBattleApp(self):
        raise NotImplementedError

    def getWaitingWorker(self):
        raise NotImplementedError

    def changeSpace(self, space):
        raise NotImplementedError

    def createLobby(self):
        raise NotImplementedError

    def destroyLobby(self):
        raise NotImplementedError

    def showLobby(self):
        raise NotImplementedError

    def switchAccountEntity(self):
        raise NotImplementedError

    def createBattle(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        raise NotImplementedError

    def destroyBattle(self):
        raise NotImplementedError

    def attachCursor(self, appNS, flags=0):
        raise NotImplementedError

    def detachCursor(self, appNS):
        raise NotImplementedError

    def syncCursor(self, appNS, flags=0):
        raise NotImplementedError

    def handleKey(self, appNS, isDown, key, mods):
        raise NotImplementedError
