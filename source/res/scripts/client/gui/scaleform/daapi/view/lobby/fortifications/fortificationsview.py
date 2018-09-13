# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortificationsView.py
import BigWorld
import MusicController
import SoundGroups
from adisp import process
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.daapi.view.meta.FortificationsViewMeta import FortificationsViewMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.SoundEffectsId import SoundEffectsId
from gui.shared.fortifications.context import CreateFortCtx
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.shared import events, EVENT_BUS_SCOPE

class FortificationsView(LobbySubView, FortificationsViewMeta, FortViewHelper):

    def __init__(self):
        super(FortificationsView, self).__init__()
        self.__reqID = None
        self.__initialize = False
        self.__currentView = None
        return

    def _populate(self):
        BigWorld.wg_setCategoryVolume('hangar_v2', 0.0)
        MusicController.g_musicController.stop()
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY_FORT)
        super(FortificationsView, self)._populate()
        self.startFortListening()
        SoundGroups.g_instance.onVolumeChanged += self._onVolumeChanged
        self.loadView()

    def onEscapePress(self):
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        BigWorld.wg_setCategoryVolume('hangar_v2', SoundGroups.g_instance.getVolume('ambient'))
        MusicController.g_musicController.stop()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        SoundGroups.g_instance.onVolumeChanged -= self._onVolumeChanged
        self.stopFortListening()
        super(FortificationsView, self)._dispose()

    def onFortCreateClick(self):
        if self.app.soundManager is not None:
            self.app.soundManager.playEffectSound(SoundEffectsId.FORT_CREATE)
        self.requestFortCreation()
        return

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
        if loadingView != self.__currentView:
            self.__currentView = loadingView
            self.as_loadViewS(loadingView, '')

    def onClientStateChanged(self, state):
        self.loadView()

    def _onVolumeChanged(self, categoryName, volume):
        if categoryName == 'ambient':
            BigWorld.wg_setCategoryVolume('hangar_v2', 0)
