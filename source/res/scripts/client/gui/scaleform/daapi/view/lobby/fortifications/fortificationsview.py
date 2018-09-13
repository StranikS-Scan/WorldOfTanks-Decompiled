# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortificationsView.py
from adisp import process
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortSoundController import g_fortSoundController
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.meta.FortificationsViewMeta import FortificationsViewMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.fortifications.context import CreateFortCtx
from gui.Scaleform.Waiting import Waiting
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.shared import events, EVENT_BUS_SCOPE

class FortificationsView(LobbySubView, FortificationsViewMeta, FortViewHelper):

    def __init__(self):
        super(FortificationsView, self).__init__()
        self.__reqID = None
        self.__initialize = False
        self.__currentView = None
        Waiting.show('Flash')
        return

    def _populate(self):
        g_fortSoundController.init()
        super(FortificationsView, self)._populate()
        self.startFortListening()
        self.loadView()

    def onEscapePress(self):
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_fortSoundController.fini()
        self.stopFortListening()
        super(FortificationsView, self)._dispose()

    def onFortCreateClick(self):
        g_fortSoundController.playCreateFort()
        self.requestFortCreation()

    @process
    def requestFortCreation(self):
        result = yield self.fortProvider.sendRequest(CreateFortCtx('fort/create'))
        if result:
            SystemMessages.g_instance.pushI18nMessage(SYSTEM_MESSAGES.FORTIFICATION_CREATED, type=SystemMessages.SM_TYPE.Warning)

    def onWindowClose(self):
        self.destroy()

    def loadView(self):
        state = self.fortState
        if state.getStateID() == CLIENT_FORT_STATE.UNSUBSCRIBED:
            return
        if state.isInitial():
            loadingView = FORTIFICATION_ALIASES.WELCOME_VIEW_LINKAGE
        elif state.isDisabled():
            loadingView = FORTIFICATION_ALIASES.DISCONNECT_VIEW_LINCKAGE
        else:
            loadingView = FORTIFICATION_ALIASES.MAIN_VIEW_LINKAGE
        LOG_DEBUG(loadingView)
        if loadingView != self.__currentView:
            self.__currentView = loadingView
            self.as_loadViewS(loadingView, '')

    def onClientStateChanged(self, state):
        self.loadView()
