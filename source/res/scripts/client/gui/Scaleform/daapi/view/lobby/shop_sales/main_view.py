# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shop_sales/main_view.py
import WWISE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.shop import Origin
from gui.sounds.ambients import HangarOverlayEnv
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IShopSalesEventController
from web.web_client_api import webApiCollection
from web.web_client_api.blueprints_convert_sale import BlueprintsConvertSaleWebApi
from web.web_client_api.platform import PlatformWebApi
from web.web_client_api.quests import QuestsWebApi
from web.web_client_api.reactive_comm import ReactiveCommunicationWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.shop_sales_event import ShopSalesEventWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi, SoundWebApi
from web.web_client_api.ui import CloseWindowWebApi, NotificationWebApi, OpenTabWebApi, OpenWindowWebApi, UtilWebApi
from web.web_client_api.vehicles import VehiclesWebApi

class _OpenTabWebApi(OpenTabWebApi):
    __shopSales = dependency.descriptor(IShopSalesEventController)

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.SHOP_SALES_MAIN_VIEW

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getShopSalesMainViewReturnCallback

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getShopSalesMainViewReturnCallback

    def __getShopSalesMainViewReturnCallback(self):
        return self.__shopSales.openMainView(origin=Origin.VEHICLE_PREVIEW)


_DEFAULT_WEB_API_COLLECTION = (CloseWindowWebApi,
 OpenWindowWebApi,
 NotificationWebApi,
 _OpenTabWebApi,
 RequestWebApi,
 ShopWebApi,
 SoundWebApi,
 SoundStateWebApi,
 ShopSalesEventWebApi,
 HangarSoundWebApi,
 UtilWebApi,
 QuestsWebApi,
 VehiclesWebApi,
 ReactiveCommunicationWebApi,
 RewardsWebApi,
 SocialWebApi,
 BlueprintsConvertSaleWebApi,
 PlatformWebApi)

class ShopSalesMainView(WebView):
    __sound_env__ = HangarOverlayEnv
    __appLoader = dependency.descriptor(IAppLoader)
    __SOUND_ENTER = 'double_eleven_day_enter'
    __SOUND_EXIT = 'double_eleven_day_exit'

    def webHandlers(self):
        return webApiCollection(*_DEFAULT_WEB_API_COLLECTION)

    def _populate(self):
        super(ShopSalesMainView, self)._populate()
        app = self.__appLoader.getApp()
        if app and app.soundManager:
            app.soundManager.playEffectSound(self.__SOUND_ENTER)

    def _dispose(self):
        WWISE.WW_eventGlobal(self.__SOUND_EXIT)
        super(ShopSalesMainView, self)._dispose()
