# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/shop_sales/shop_sales_main_view.py
import WWISE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.lobby.common.browser_view import BrowserView
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shop import Origin
from gui.sounds.ambients import HangarOverlayEnv
from helpers import dependency
from frameworks.wulf import WindowFlags, WindowLayer, ViewFlags
from skeletons.gui.game_control import IShopSalesEventController
from web.web_client_api.ui import OpenTabWebApi
from skeletons.gui.game_control import IGameSessionController
from web.web_client_api.blueprints_convert_sale import BlueprintsConvertSaleWebApi
from web.web_client_api.platform import PlatformWebApi
from web.web_client_api.reactive_comm import ReactiveCommunicationWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.rewards import RewardsWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.sound import HangarSoundWebApi, SoundStateWebApi, SoundWebApi
from web.web_client_api.ui import CloseWindowWebApi, NotificationWebApi, OpenWindowWebApi, UtilWebApi
from web.web_client_api import webApiCollection
from web.web_client_api.vehicles import VehiclesWebApi
from gui.impl.lobby.common.browser_view import makeSettings

class ShopSalesOpenTabWebApi(OpenTabWebApi):
    __shopSales = dependency.descriptor(IShopSalesEventController)

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.SHOP_SALES_VEHICLE_PREVIEW

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getShopSalesMainViewReturnCallback

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getShopSalesMainViewReturnCallback

    def __getShopSalesMainViewReturnCallback(self):
        return self.__shopSales.openMainView(origin=Origin.VEHICLE_PREVIEW)


class ShopSalesMainView(BrowserView):
    __sound_env__ = HangarOverlayEnv
    __gameSession = dependency.descriptor(IGameSessionController)
    __SOUND_ENTER = 'double_eleven_day_enter'
    __SOUND_EXIT = 'double_eleven_day_exit'

    def _initialize(self, *args, **kwargs):
        super(ShopSalesMainView, self)._initialize(*args, **kwargs)
        self.soundManager.playSound(self.__SOUND_ENTER)
        self.__gameSession.onNewDayNotify += self.__onNewDay

    def _finalize(self):
        WWISE.WW_eventGlobal(self.__SOUND_EXIT)
        self.__gameSession.onNewDayNotify -= self.__onNewDay
        super(ShopSalesMainView, self)._finalize()

    def __onNewDay(self, _):
        self.browser.refresh()


class ShopSalesMainWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, url):
        webHandlers = webApiCollection(CloseWindowWebApi, OpenWindowWebApi, NotificationWebApi, ShopSalesOpenTabWebApi, RequestWebApi, ShopWebApi, SoundWebApi, SoundStateWebApi, HangarSoundWebApi, UtilWebApi, VehiclesWebApi, ReactiveCommunicationWebApi, RewardsWebApi, SocialWebApi, BlueprintsConvertSaleWebApi, PlatformWebApi)
        settings = makeSettings(url=url, isClosable=False, webHandlers=webHandlers, viewFlags=ViewFlags.VIEW, restoreBackground=True)
        super(ShopSalesMainWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ShopSalesMainView(R.views.lobby.common.BrowserView(), settings), layer=WindowLayer.FULLSCREEN_WINDOW)
