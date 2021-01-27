# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/shop_view.py
import logging
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import SHOP_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
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


class ShopBase(_ShopOverlayBase):
    _COMMON_SOUND_SPACE = SHOP_SOUND_SPACE

    def __init__(self, ctx=None):
        if 'url' not in ctx:
            ctx['url'] = getShopURL()
        super(ShopBase, self).__init__(ctx)

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.web_handlers import createShopWebHandlers
        return createShopWebHandlers()


class ShopView(LobbySubView, ShopBase):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(ShopView, self).__init__(ctx)
        g_playerEvents.onShopResync += self.__onShopResync

    def onCloseBtnClick(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onEscapePress(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_playerEvents.onShopResync -= self.__onShopResync
        super(ShopView, self)._dispose()

    def __onShopResync(self):
        self._refresh()


class ShopOverlay(_ShopOverlayBase):

    def onEscapePress(self):
        if not self._browserParams.get('isHidden'):
            self.destroy()


class PremContentPageOverlay(WebView):

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createPremAccWebHandlers
        return createPremAccWebHandlers()


class BobPageOverlay(WebView):

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createBobOverlayWebHandlers
        return createBobOverlayWebHandlers()
