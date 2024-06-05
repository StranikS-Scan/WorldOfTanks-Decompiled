# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/loader.py
import logging
import typing
import Event
from constants import ARENA_GUI_TYPE
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.app_loader.observers import GameplayStatesObserver
from gui.shared import g_eventBus, events
from gui.app_loader import spaces
from skeletons.gui.app_loader import IAppLoader, IAppFactory, ApplicationStateID
from skeletons.gui.app_loader import IWaitingWorker, IGlobalSpace
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class _EmptyWaitingWorker(IWaitingWorker):
    __slots__ = ()

    def getWaitingView(self, isBlocking):
        _logger.error('Waiting widget is not defined')
        return None

    def isWaitingShown(self, messageID=None):
        return False

    def getWaitingTask(self, messageID):
        _logger.error('Waiting task is not defined')
        return None

    def getSuspendedWaitingTask(self, messageID):
        _logger.error('Waiting suspended task is not defined')
        return None

    def show(self, messageID, isSingle=False, interruptCallback=None, isBlocking=True, isAlwaysOnTop=False, backgroundImage=None, softStart=False, showBg=True):
        _logger.error('Waiting is not found. Method "show" is ignored: %r', messageID)

    def hide(self, messageID):
        _logger.error('Waiting is not found. Method "hide" is ignored: %r', messageID)

    def suspend(self, lockerID=None):
        _logger.error('Waiting is not found. Method "suspend" is ignored')

    def isResumeLocked(self):
        return False

    def resume(self, lockerID=None, hard=False):
        _logger.error('Waiting is not found. Method "resumed" is ignored')

    def isSuspended(self):
        return False

    def close(self):
        _logger.error('Waiting is not found. Method "close" is ignored')

    def rollback(self):
        _logger.error('Waiting is not found. Method "rollback" is ignored')

    def cancelCallback(self):
        _logger.error('Waiting is not found. Method "cancelCallback" is ignored')


class _EmptyFactory(IAppFactory):
    __slots__ = ()

    def getWaitingWorker(self):
        return _EmptyWaitingWorker()


class AppLoader(IAppLoader):

    def __init__(self):
        super(AppLoader, self).__init__()
        self.__space = spaces.WaitingSpace()
        self.__appsStates = {}
        self.__appFactory = _EmptyFactory()
        self.__observer = GameplayStatesObserver(self)
        self.onGUISpaceLeft = Event.Event()
        self.onGUISpaceBeforeEnter = Event.Event()
        self.onGUISpaceEntered = Event.Event()
        self.onGUIInitialized = Event.Event()

    def init(self, appFactory):
        self.__appFactory = appFactory
        self.__observer.init()
        add = g_eventBus.addListener
        appEvent = events.AppLifeCycleEvent
        add(appEvent.INITIALIZING, self.__onAppInitializing)
        add(appEvent.INITIALIZED, self.__onAppInitialized)
        add(appEvent.DESTROYED, self.__onAppDestroyed)

    def fini(self):
        if self.__appFactory:
            self.__appFactory.destroy()
            self.__appFactory = None
        self.__observer.clear()
        remove = g_eventBus.removeListener
        appEvent = events.AppLifeCycleEvent
        remove(appEvent.INITIALIZING, self.__onAppInitializing)
        remove(appEvent.INITIALIZED, self.__onAppInitialized)
        remove(appEvent.DESTROYED, self.__onAppDestroyed)
        return

    def getSpaceID(self):
        return self.__space.getSpaceID()

    def getAppStateID(self, appNS):
        return self.__appsStates.get(appNS, ApplicationStateID.NOT_CREATED)

    def getApp(self, appNS=None):
        app = None
        if self.__appFactory:
            app = self.__appFactory.getApp(appNS=appNS)
        return app

    def getDefLobbyApp(self):
        app = None
        if self.__appFactory:
            app = self.__appFactory.getDefLobbyApp()
        return app

    def getDefBattleApp(self):
        app = None
        if self.__appFactory:
            app = self.__appFactory.getDefBattleApp()
        return app

    def getWaitingWorker(self):
        return self.__appFactory.getWaitingWorker()

    def changeSpace(self, space):
        return self.__updateSpace(space)

    def setupSpace(self, *args, **kwargs):
        self.__space.setup(*args, **kwargs)

    def createLobby(self):
        self.__appFactory.createLobby()

    def destroyLobby(self):
        self.changeSpace(spaces.WaitingSpace())
        self.__appFactory.destroyLobby()

    def showLobby(self):
        return self.changeSpace(spaces.LobbySpace())

    def switchAccountEntity(self):
        self.changeSpace(spaces.WaitingSpace())
        self.__appFactory.destroyLobby()
        self.__appFactory.createLobby()

    def createBattle(self, arenaGuiType=ARENA_GUI_TYPE.UNKNOWN):
        self.__appFactory.createBattle(arenaGuiType)

    def destroyBattle(self):
        self.changeSpace(spaces.WaitingSpace())
        self.__appFactory.destroyBattle()

    def attachCursor(self, appNS, flags=_CTRL_FLAG.CURSOR_VISIBLE):
        self.__appFactory.attachCursor(appNS, flags=flags)

    def detachCursor(self, appNS):
        self.__appFactory.detachCursor(appNS)

    def syncCursor(self, appNS, flags=_CTRL_FLAG.CURSOR_VISIBLE):
        self.__appFactory.syncCursor(appNS, flags=flags)

    def handleKey(self, appNS, isDown, key, mods):
        return self.__appFactory.handleKey(appNS, isDown, key, mods)

    def __updateSpace(self, newSpace):
        result = False
        if newSpace.getSpaceID() != self.__space.getSpaceID():
            _logger.info('Space is changed: %r -> %r', self.__space, newSpace)
            self.onGUISpaceLeft(self.__space.getSpaceID())
            self.__space.fini()
            self.__space.hideGUI(self.__appFactory, newSpace)
            self.__space = newSpace
            self.__space.init()
            self.onGUISpaceBeforeEnter(self.__space.getSpaceID())
            for appNS, appState in self.__getCreatedApps():
                self.__space.showGUI(self.__appFactory, appNS, appState)

            result = True
            self.onGUISpaceEntered(self.__space.getSpaceID())
        else:
            _logger.info('Space is updated: %s', self.__space)
            for appNS, appState in self.__getCreatedApps():
                self.__space.update()
                self.__space.updateGUI(self.__appFactory, appNS)

        return result

    def __getCreatedApps(self):
        for appNS, appState in self.__appsStates.iteritems():
            if appState != ApplicationStateID.NOT_CREATED:
                yield (appNS, appState)

    def __onAppInitializing(self, event):
        appNS = event.ns
        if self.__appFactory.hasApp(appNS):
            _logger.info('App is initializing: %s', appNS)
            self.__appsStates[appNS] = ApplicationStateID.INITIALIZING
            self.__space.showGUI(self.__appFactory, appNS, ApplicationStateID.INITIALIZING)

    def __onAppInitialized(self, event):
        appNS = event.ns
        if self.__appFactory.hasApp(appNS):
            _logger.info('App is initialized: %s', appNS)
            self.__appsStates[appNS] = ApplicationStateID.INITIALIZED
            self.__space.showGUI(self.__appFactory, appNS, ApplicationStateID.INITIALIZED)
            self.onGUIInitialized()

    def __onAppDestroyed(self, event):
        appNS = event.ns
        if self.__appFactory.hasApp(appNS):
            _logger.info('App is destroyed: %s', appNS)
            self.__appsStates[appNS] = ApplicationStateID.NOT_CREATED
