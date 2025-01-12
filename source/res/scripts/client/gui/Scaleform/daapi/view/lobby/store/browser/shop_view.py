# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/shop_view.py
import logging
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import SHOP_SOUND_SPACE
from uilogging.shop.loggers import ShopMetricsLogger
from uilogging.shop.logging_constants import ShopLogKeys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class _ShopOverlayBase(WebView):

    def _onError(self):
        super(_ShopOverlayBase, self)._onError()
        self.fireEvent(events.ShopEvent(events.ShopEvent.SHOP_DATA_UNAVAILABLE), scope=EVENT_BUS_SCOPE.DEFAULT)

    def _populate(self):
        super(_ShopOverlayBase, self)._populate()
        self.fireEvent(events.ShopEvent(events.ShopEvent.SHOP_ACTIVATED), scope=EVENT_BUS_SCOPE.DEFAULT)

    def _dispose(self):
        super(_ShopOverlayBase, self)._dispose()
        self.fireEvent(events.ShopEvent(events.ShopEvent.SHOP_DEACTIVATED), scope=EVENT_BUS_SCOPE.DEFAULT)

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.web_handlers import createShopWebHandlers
        return createShopWebHandlers()


class ShopBase(_ShopOverlayBase):
    _COMMON_SOUND_SPACE = SHOP_SOUND_SPACE

    def __init__(self, ctx=None):
        if 'url' not in ctx:
            ctx['url'] = getShopURL()
        super(ShopBase, self).__init__(ctx)


class ShopView(LobbySubView, ShopBase):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(ShopView, self).__init__(ctx)
        g_playerEvents.onShopResync += self.__onShopResync
        self.__uiLogger = ShopMetricsLogger(item=ShopLogKeys.SHOP_VIEW)

    def onCloseBtnClick(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onEscapePress(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_playerEvents.onShopResync -= self.__onShopResync
        self.__uiLogger.onViewClosed()
        super(ShopView, self)._dispose()

    def __onShopResync(self):
        self._refresh()


class ShopOverlay(_ShopOverlayBase):

    def __init__(self, ctx=None):
        super(ShopOverlay, self).__init__(ctx)
        self.__uiLogger = ShopMetricsLogger(item=ShopLogKeys.SHOP_OVERLAY)

    def _dispose(self):
        self.__uiLogger.onViewClosed()
        super(ShopOverlay, self)._dispose()

    def onEscapePress(self):
        if not self._browserParams.get('isHidden'):
            self.destroy()
