# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fest_mini_game_browser.py
from gui.shared.event_dispatcher import showFestivalMainView
from helpers import dependency
from skeletons.festival import IFestivalController
from web_client_api import webApiCollection
from web_client_api.request import RequestWebApi
from web_client_api.festival import FestivalWebApi, FestivalOpenTabWebApi
from web_client_api.sound import SoundWebApi, SoundStateWebApi, HangarSoundWebApi, SoundPlay2DWebApi, SoundStop2DWebApi, GlobalSoundStateWebApi
from web_client_api.ui import CloseWindowWebApi, OpenTabWebApi
from gui.Scaleform.daapi.view.lobby.shared.web_overlay_base import WebOverlayBase
_WEB_API_MG_COLLECTION = (RequestWebApi,
 CloseWindowWebApi,
 SoundWebApi,
 SoundPlay2DWebApi,
 SoundStop2DWebApi,
 SoundStateWebApi,
 GlobalSoundStateWebApi,
 HangarSoundWebApi,
 FestivalWebApi)

class FestivalMiniGamePageOverlay(WebOverlayBase):
    __festController = dependency.descriptor(IFestivalController)

    def __init__(self, ctx=None):
        self.__fromHangar = ctx['fromHangar']
        super(FestivalMiniGamePageOverlay, self).__init__(ctx)

    def webHandlers(self):
        return webApiCollection(*(_WEB_API_MG_COLLECTION + (FestivalOpenTabWebApi if self.__fromHangar else OpenTabWebApi,)))

    def _populate(self):
        super(FestivalMiniGamePageOverlay, self)._populate()
        self.__festController.onMiniGamesUpdated += self.__onMiniGamesUpdated

    def _dispose(self):
        self.__festController.forceUpdateMiniGames()
        self.__festController.onMiniGamesUpdated -= self.__onMiniGamesUpdated
        super(FestivalMiniGamePageOverlay, self)._dispose()

    def __onMiniGamesUpdated(self):
        if not self.__festController.isMiniGamesEnabled():
            self.destroy()

    def _handleBrowserClose(self, event):
        if self.__fromHangar and event.ctx.get('showFestivalView'):
            showFestivalMainView()
        else:
            super(FestivalMiniGamePageOverlay, self)._handleBrowserClose(event)
