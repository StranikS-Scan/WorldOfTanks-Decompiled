# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/year_hare_affair_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from helpers import dependency
from skeletons.gui.game_control import IYearHareAffairController
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from web.web_client_api.clans import ClansWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
_YEAR_HARE_AFFAIR_WEB_API_COLLECTION = (ui_web_api.CloseWindowWebApi,
 ui_web_api.OpenWindowWebApi,
 ui_web_api.NotificationWebApi,
 ui_web_api.OpenTabWebApi,
 ui_web_api.UtilWebApi,
 sound_web_api.SoundWebApi,
 sound_web_api.SoundStateWebApi,
 sound_web_api.HangarSoundWebApi,
 ClansWebApi,
 QuestsWebApi,
 RewardsWebApi,
 ShopWebApi)

class YearHareAffairBrowserView(WebView):
    __yhaController = dependency.descriptor(IYearHareAffairController)

    def webHandlers(self):
        return webApiCollection(*_YEAR_HARE_AFFAIR_WEB_API_COLLECTION)

    def _populate(self):
        super(YearHareAffairBrowserView, self)._populate()
        self.__yhaController.onStateChanged += self.__onStateChanged

    def _dispose(self):
        self.__yhaController.onStateChanged -= self.__onStateChanged
        super(YearHareAffairBrowserView, self)._dispose()

    def __onStateChanged(self):
        self.onCloseBtnClick()
