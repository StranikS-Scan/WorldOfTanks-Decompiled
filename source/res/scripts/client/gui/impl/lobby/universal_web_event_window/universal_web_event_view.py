# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/universal_web_event_window/universal_web_event_view.py
from gui.impl.gen import R
from gui.impl.lobby.common.browser_view import BrowserView
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from frameworks.wulf import WindowFlags, WindowLayer, ViewFlags
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

class UniversalWebEvenView(BrowserView):
    __gameSession = dependency.descriptor(IGameSessionController)

    def _initialize(self, *args, **kwargs):
        super(UniversalWebEvenView, self)._initialize(*args, **kwargs)
        self.__gameSession.onNewDayNotify += self.__onNewDay

    def _finalize(self):
        self.__gameSession.onNewDayNotify -= self.__onNewDay
        super(UniversalWebEvenView, self)._finalize()

    def __onNewDay(self, _):
        self.browser.refresh()


class UniversalWebEventWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, url):
        webHandlers = webApiCollection(CloseWindowWebApi, OpenWindowWebApi, NotificationWebApi, OpenTabWebApi, RequestWebApi, ShopWebApi, SoundWebApi, SoundStateWebApi, HangarSoundWebApi, UtilWebApi, VehiclesWebApi, ReactiveCommunicationWebApi, RewardsWebApi, SocialWebApi, BlueprintsConvertSaleWebApi, PlatformWebApi)
        settings = makeSettings(url=url, isClosable=False, webHandlers=webHandlers, viewFlags=ViewFlags.VIEW, restoreBackground=True)
        view = UniversalWebEvenView(R.views.lobby.common.BrowserView(), settings)
        super(UniversalWebEventWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=view, layer=WindowLayer.FULLSCREEN_WINDOW)
