# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortificationsView.py
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortificationsViewMeta import FortificationsViewMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.WAITING import WAITING
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.shared import events, EVENT_BUS_SCOPE
from gui.ClientUpdateManager import g_clientUpdateManager

class FortificationsView(LobbySubView, FortificationsViewMeta, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortificationsView, self).__init__()
        self.__reqID = None
        self.__initialize = False
        self.__currentView = None
        return

    def onEscapePress(self):
        self.__close()

    def onWindowClose(self):
        self.destroy()

    def loadView(self):
        state = self.fortState
        if state.getStateID() == CLIENT_FORT_STATE.UNSUBSCRIBED:
            self.__makeWaitingData(True)
            return
        if state.isInitial():
            loadingView = FORTIFICATION_ALIASES.WELCOME_VIEW_LINKAGE
        elif state.isDisabled():
            loadingView = FORTIFICATION_ALIASES.DISCONNECT_VIEW_LINCKAGE
        else:
            loadingView = FORTIFICATION_ALIASES.MAIN_VIEW_LINKAGE
        if loadingView != self.__currentView:
            self.__makeWaitingData(True)
            self.__currentView = loadingView
            self.as_loadViewS(loadingView, '')
        else:
            self.__makeWaitingData(showWaiting=False)

    def onClientStateChanged(self, state):
        self.loadView()

    def _populate(self):
        g_fortSoundController.init()
        super(FortificationsView, self)._populate()
        self.addListener(events.FortEvent.VIEW_LOADED, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.FORT)
        self.addListener(events.FortEvent.REQUEST_TIMEOUT, self.__loadDisconnectedView, scope=EVENT_BUS_SCOPE.FORT)
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__onClanInfoChanged})
        self.startFortListening()
        Waiting.hide('loadPage')
        self.loadView()

    def _dispose(self):
        g_fortSoundController.fini()
        self.stopFortListening()
        self.removeListener(events.FortEvent.REQUEST_TIMEOUT, self.__loadDisconnectedView, scope=EVENT_BUS_SCOPE.FORT)
        self.removeListener(events.FortEvent.VIEW_LOADED, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.FORT)
        g_clientUpdateManager.removeCallback('stats.clanInfo', self.__onClanInfoChanged)
        super(FortificationsView, self)._dispose()

    def __makeWaitingData(self, showWaiting = False):
        self.as_waitingDataS({'isShowWaiting': showWaiting,
         'waitingLbl': WAITING.FORT_SERVERCONNECTION})

    def __onViewLoaded(self, e):
        self.__makeWaitingData()

    def __loadDisconnectedView(self, e):
        self.__makeWaitingData(True)
        loadingView = FORTIFICATION_ALIASES.DISCONNECT_VIEW_LINCKAGE
        self.__currentView = loadingView
        self.as_loadViewS(loadingView, '')

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onClanInfoChanged(self, clanInfo):
        if not clanInfo:
            self.__close()
