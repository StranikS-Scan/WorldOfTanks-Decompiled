# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/shop_view.py
import logging
from functools import partial
from PlayerEvents import g_playerEvents
from crew2.sandbox import SANDBOX_CONSTANTS
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
from web.web_client_api import w2capi, w2c, W2CSchema, webApiCollection
from web.web_client_api.sound import SOUND_STATE_WEB_API_ID, SoundWebApi
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

    def onCloseBtnClick(self):
        if not SANDBOX_CONSTANTS.SHOP_PLACEHOLDER_ON:
            super(ShopOverlay, self).onCloseBtnClick()
            return
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def webHandlers(self):
        if not SANDBOX_CONSTANTS.SHOP_PLACEHOLDER_ON:
            return super(ShopOverlay, self).webHandlers()

        @w2capi(name='open_tab', key='tab_id')
        class OpenTabWebApiOverride(object):

            def __init__(self, overlay):
                super(OpenTabWebApiOverride, self).__init__()
                self.__overlay = overlay

            @w2c(W2CSchema)
            def hangar(self, cmd):
                self.__overlay.onEscapePress()

        _OpenTabWebApi = partial(OpenTabWebApiOverride, self)
        return webApiCollection(_OpenTabWebApi, SoundWebApi)


class ShopOverlayDormitory(ShopOverlay):

    def webHandlers(self):
        webHandlers = super(ShopOverlayDormitory, self).webHandlers()
        soundStateWebApi = next((handler for handler in webHandlers if handler.name == SOUND_STATE_WEB_API_ID), None)
        if soundStateWebApi is not None:
            webHandlers.remove(soundStateWebApi)
        return webHandlers


class PremContentPageOverlay(WebView):

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createPremAccWebHandlers
        return createPremAccWebHandlers()
