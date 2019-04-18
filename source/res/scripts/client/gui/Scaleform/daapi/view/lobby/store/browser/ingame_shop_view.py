# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/ingame_shop_view.py
import logging
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled, getWebShopURL
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import INGAMESHOP_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.shared.web_overlay_base import WebOverlayBase
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class _IngameShopOverlayBase(WebOverlayBase):

    def _onError(self):
        super(_IngameShopOverlayBase, self)._onError()
        self.fireEvent(events.IngameShopEvent(events.IngameShopEvent.INGAMESHOP_DATA_UNAVAILABLE), scope=EVENT_BUS_SCOPE.DEFAULT)

    def _populate(self):
        super(_IngameShopOverlayBase, self)._populate()
        self.fireEvent(events.IngameShopEvent(events.IngameShopEvent.INGAMESHOP_ACTIVATED), scope=EVENT_BUS_SCOPE.DEFAULT)

    def _dispose(self):
        super(_IngameShopOverlayBase, self)._dispose()
        self.fireEvent(events.IngameShopEvent(events.IngameShopEvent.INGAMESHOP_DEACTIVATED), scope=EVENT_BUS_SCOPE.DEFAULT)


class IngameShopBase(_IngameShopOverlayBase):
    _COMMON_SOUND_SPACE = INGAMESHOP_SOUND_SPACE

    def __init__(self, ctx=None):
        if 'url' not in ctx:
            ctx['url'] = getWebShopURL()
        super(IngameShopBase, self).__init__(ctx)

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.web_handlers import createShopWebHandlers
        return createShopWebHandlers()


class IngameShopView(LobbySubView, IngameShopBase):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(IngameShopView, self).__init__(ctx)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_playerEvents.onShopResync += self.__onShopResync

    def onEscapePress(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        g_playerEvents.onShopResync -= self.__onShopResync
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(IngameShopView, self)._dispose()

    def __onServerSettingsChanged(self, diff):
        if 'ingameShop' in diff and not isIngameShopEnabled():
            _logger.info('INFO: InGameShop disabled by server settings')
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onShopResync(self):
        self._refresh()


class IngameShopOverlay(_IngameShopOverlayBase):

    def onEscapePress(self):
        if not self._browserParams.get('isTransparent'):
            self.destroy()


class PremContentPageOverlay(WebOverlayBase):

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createPremAccWebHandlers
        return createPremAccWebHandlers()
