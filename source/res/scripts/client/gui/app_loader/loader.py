# Embedded file name: scripts/client/gui/app_loader/loader.py
import BigWorld
from ConnectionManager import connectionManager
import Event
from constants import ARENA_GUI_TYPE
from debug_utils import LOG_DEBUG
from gui.app_loader.interfaces import IAppFactory
from gui.shared import g_eventBus, events
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from gui.app_loader.settings import APP_STATE_ID as _STATE_ID
from gui.app_loader.settings import DISCONNECT_REASON as _DSN_REASON
from gui.app_loader.states import StartState
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.simple('guiSpace', 'appsStates', 'dsnReason', 'dsnDesc')

class _GlobalCtx(object):
    __slots__ = ('guiSpace', 'appsStates', 'dsnReason', 'dsnDesc')

    def __init__(self):
        super(_GlobalCtx, self).__init__()
        self.guiSpace = _SPACE_ID.UNDEFINED
        self.appsStates = {}
        self.dsnReason = _DSN_REASON.UNDEFINED
        self.dsnDesc = ()

    def isConnected(self):
        return connectionManager.isConnected()

    def resetDsn(self):
        self.dsnReason = _DSN_REASON.UNDEFINED
        self.dsnDesc = ()


class _EmptyFactory(IAppFactory):
    pass


class _AppLoader(object):
    __slots__ = ('__state', '__ctx', '__appFactory', 'onGUISpaceChanged')

    def __init__(self):
        super(_AppLoader, self).__init__()
        self.__state = StartState()
        self.__ctx = _GlobalCtx()
        self.__appFactory = _EmptyFactory()
        self.onGUISpaceChanged = Event.Event()

    def init(self, appFactory):
        self.__appFactory = appFactory
        add = g_eventBus.addListener
        appEvent = events.AppLifeCycleEvent
        spaceEvent = events.GlobalSpaceEvent
        add(appEvent.INITIALIZING, self.__onAppInitializing)
        add(appEvent.INITIALIZED, self.__onAppInitialized)
        add(appEvent.DESTROYED, self.__onAppDestroyed)
        add(spaceEvent.GO_NEXT, self.__onGoNextSpace)

    def fini(self):
        if self.__appFactory:
            self.__appFactory.destroy()
            self.__appFactory = None
        remove = g_eventBus.removeListener
        appEvent = events.AppLifeCycleEvent
        spaceEvent = events.GlobalSpaceEvent
        remove(appEvent.INITIALIZING, self.__onAppInitializing)
        remove(appEvent.INITIALIZED, self.__onAppInitialized)
        remove(appEvent.DESTROYED, self.__onAppDestroyed)
        remove(spaceEvent.GO_NEXT, self.__onGoNextSpace)
        return

    def getSpaceID(self):
        return self.__ctx.guiSpace

    def getPackageImporter(self):
        importer = None
        if self.__appFactory:
            importer = self.__appFactory.getPackageImporter()
        return importer

    def getAppStateID(self, appNS):
        return self.__ctx.appsStates.get(appNS, _STATE_ID.NOT_CREATED)

    def getApp(self, appNS = None):
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

    def startLobby(self):
        self.__appFactory.createLobby()
        self.__updateState()

    def startBattle(self):
        self.__appFactory.createBattle()

    def changeSpace(self, spaceID):
        self.__ctx.guiSpace = spaceID
        return self.__updateState()

    def showLogin(self):
        return self.changeSpace(_SPACE_ID.LOGIN)

    def showLobby(self):
        return self.changeSpace(_SPACE_ID.LOBBY)

    def showBattleLoading(self, arenaGuiType = ARENA_GUI_TYPE.UNKNOWN, isMultiTeam = False):
        if arenaGuiType == ARENA_GUI_TYPE.TUTORIAL:
            spaceID = _SPACE_ID.BATTLE_TUT_LOADING
        elif isMultiTeam:
            spaceID = _SPACE_ID.FALLOUT_MULTI_TEAM_LOADING
        else:
            spaceID = _SPACE_ID.BATTLE_LOADING
        return self.changeSpace(spaceID)

    def showBattle(self):
        return self.changeSpace(_SPACE_ID.BATTLE)

    def destroyBattle(self):
        if self.__ctx.dsnReason != _DSN_REASON.UNDEFINED:
            return False
        return self.changeSpace(_SPACE_ID.WAITING)

    def goToLoginByRQ(self, forced = False):
        if self.__ctx.dsnReason != _DSN_REASON.REQUEST or forced:
            LOG_DEBUG('Disconnects from server by request')
            self.__ctx.dsnReason = _DSN_REASON.REQUEST
            connectionManager.disconnect()
        return self.showLogin()

    def goToLoginByEvent(self):
        if self.__ctx.dsnReason not in (_DSN_REASON.REQUEST, _DSN_REASON.KICK):
            LOG_DEBUG('Disconnects from server by connection manager event')
            if self.__ctx.guiSpace != _SPACE_ID.LOGIN:
                self.__ctx.dsnReason = _DSN_REASON.EVENT
        return self.showLogin()

    def goToLoginByKick(self, reason, isBan, expiryTime):
        if self.__ctx.dsnReason != _DSN_REASON.KICK:
            LOG_DEBUG('Disconnects from server by kick')
            self.__ctx.dsnReason = _DSN_REASON.KICK
            self.__ctx.dsnDesc = (reason, isBan, expiryTime)
        return self.showLogin()

    def quitFromGame(self):
        BigWorld.quit()

    def __updateState(self):
        result = False
        newState = self.__state.goNext(self.__ctx)
        if newState:
            LOG_DEBUG('State is changed', newState)
            self.__state = self.__state
            self.__state.fini(self.__ctx)
            self.__state.hideGUI(self.__appFactory)
            self.__state = newState
            self.__state.init(self.__ctx)
            for appNS, appState in self.__getCreatedApps():
                self.__state.showGUI(self.__appFactory, appNS, appState)

            result = True
            self.onGUISpaceChanged(self.__ctx.guiSpace)
        else:
            for appNS, appState in self.__getCreatedApps():
                self.__state.update(self.__ctx)
                self.__state.updateGUI(self.__appFactory, appNS)

        return result

    def __getCreatedApps(self):
        for appNS, appState in self.__ctx.appsStates.iteritems():
            if appState != _STATE_ID.NOT_CREATED:
                yield (appNS, appState)

    def __onAppInitializing(self, event):
        appNS = event.ns
        if self.__appFactory.hasApp(appNS):
            LOG_DEBUG('App is initializing', appNS)
            self.__ctx.appsStates[appNS] = _STATE_ID.INITIALIZING
            self.__state.showGUI(self.__appFactory, appNS, _STATE_ID.INITIALIZING)

    def __onAppInitialized(self, event):
        appNS = event.ns
        if self.__appFactory.hasApp(appNS):
            LOG_DEBUG('App is initialized', appNS)
            self.__ctx.appsStates[appNS] = _STATE_ID.INITIALIZED
            self.__state.showGUI(self.__appFactory, appNS, _STATE_ID.INITIALIZED)

    def __onAppDestroyed(self, event):
        appNS = event.ns
        if self.__appFactory.hasApp(appNS):
            LOG_DEBUG('App is destroyed', appNS)
            self.__ctx.appsStates[appNS] = _STATE_ID.NOT_CREATED

    def __onGoNextSpace(self, _):
        self.__updateState()


g_appLoader = _AppLoader()
