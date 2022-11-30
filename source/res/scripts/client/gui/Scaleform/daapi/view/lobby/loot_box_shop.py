# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/loot_box_shop.py
import copy
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.shop import Source
from gui.shared.event_dispatcher import showLootBoxBuyWindow
from helpers import dependency
from items.components.ny_constants import ToySettings
from ny_common.settings import NYLootBoxConsts, NY_CONFIG_NAME
from skeletons.gui.lobby_context import ILobbyContext
from web.web_client_api import webApiCollection
from web.web_client_api.frontline import FrontLineWebApi
from web.web_client_api.ny20 import LootBoxOpenTabWebApi, LootBoxWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import SoundWebApi, SoundStateWebApi, HangarSoundWebApi
from web.web_client_api.ui import CloseWindowWebApi, UtilWebApi, OpenWindowWebApi, NotificationWebApi
from web.web_client_api.vehicles import VehiclesWebApi
from gui.sounds.filters import switchHangarFilteredFilter
_WEB_API_MG_COLLECTION = (CloseWindowWebApi,
 OpenWindowWebApi,
 NotificationWebApi,
 RequestWebApi,
 ShopWebApi,
 SoundWebApi,
 SoundStateWebApi,
 HangarSoundWebApi,
 UtilWebApi,
 QuestsWebApi,
 VehiclesWebApi,
 RewardsWebApi,
 SocialWebApi,
 FrontLineWebApi,
 LootBoxOpenTabWebApi,
 LootBoxWebApi)
_WEB_SETTINGS_MAP = {ToySettings.NEW_YEAR: 'ny/',
 ToySettings.CHRISTMAS: 'christmas/',
 ToySettings.FAIRYTALE: 'magic/',
 ToySettings.ORIENTAL: 'east/',
 '': ''}

class LootBoxShopOverlay(WebView):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        self.__category = ctx['category']
        url = ctx['url']
        if not url.endswith('/'):
            url += '/'
        url += _WEB_SETTINGS_MAP[self.__category] + '?source=' + Source.EXTERNAL
        super(LootBoxShopOverlay, self).__init__(ctx={'url': url})
        self.__currentSettings = copy.deepcopy(self.__lobbyContext.getServerSettings().getLootBoxShop())

    def webHandlers(self):
        return webApiCollection(*_WEB_API_MG_COLLECTION)

    def _populate(self):
        super(LootBoxShopOverlay, self)._populate()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        switchHangarFilteredFilter(on=True)

    def _dispose(self):
        switchHangarFilteredFilter(on=False)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(LootBoxShopOverlay, self)._dispose()

    def __onServerSettingsChanged(self, diff):
        if not self.__lobbyContext.getServerSettings().isLootBoxesEnabled():
            self.destroy()
            return
        elif diff.get(NY_CONFIG_NAME, {}).get(NYLootBoxConsts.CONFIG_NAME) is None:
            return
        else:
            newSettings = self.__lobbyContext.getServerSettings().getLootBoxShop()
            if newSettings != self.__currentSettings:
                self.destroy()
                showLootBoxBuyWindow()
            return
