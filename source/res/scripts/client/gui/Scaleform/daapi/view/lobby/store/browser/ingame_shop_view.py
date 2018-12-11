# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/browser/ingame_shop_view.py
import logging
import BigWorld
from PlayerEvents import g_playerEvents
from adisp import process
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.daapi.view.lobby.store.browser import ingameshop_helpers
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.meta.IngameShopViewMeta import IngameShopViewMeta
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from sound_constants import INGAMESHOP_SOUND_SPACE
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_SESSION_TIMEOUT = 300
_g_lastSessionInfo = None

def _gelLastSessionInfo():
    global _g_lastSessionInfo
    if _g_lastSessionInfo is None:
        _g_lastSessionInfo = _LastSessionInfo(_SESSION_TIMEOUT)
    return _g_lastSessionInfo


class _LastSessionInfo(object):

    def __init__(self, secondsTimeout):
        self.__url = ingameshop_helpers.getWebShopURL()
        self.__lifetime = secondsTimeout
        self.__nextRefreshTime = BigWorld.time() + self.__lifetime
        self.__lastUserID = BigWorld.player().databaseID

    @property
    def url(self):
        hostUrl = ingameshop_helpers.getWebShopURL()
        if self.__needResetUrl(hostUrl):
            self.__url = hostUrl
        return self.__url

    @url.setter
    def url(self, urlStr):
        self.__url = urlStr
        self.refreshLifetime()

    def refreshLifetime(self):
        self.__nextRefreshTime = BigWorld.time() + self.__lifetime

    def __needResetUrl(self, hostUrl):
        return BigWorld.time() >= self.__nextRefreshTime or not self.__url.startswith(hostUrl) or BigWorld.player().databaseID != self.__lastUserID


class IngameShopBase(IngameShopViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)
    _COMMON_SOUND_SPACE = INGAMESHOP_SOUND_SPACE

    def __init__(self, ctx=None):
        super(IngameShopBase, self).__init__(ctx)
        self.__browser = None
        self.__hasFocus = False
        self.__browserId = 0
        self.__loadBrowserCbID = None
        self._url = ctx.get('url') if ctx else None
        self._useLastSessionUrl = False
        self._browserParams = (ctx or {}).get('browserParams', makeBrowserParams())
        return

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape(not hasFocus)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def getBrowser(self):
        return self.__browser

    def _onRegisterFlashComponent(self, viewPy, alias):
        from gui.Scaleform.daapi.view.lobby.store.browser.web_handlers import createShopWebHandlers
        super(IngameShopBase, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(browserID=self.__browserId, webHandlersMap=createShopWebHandlers())
            viewPy.onError += self.__onError

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self.__onError
        super(IngameShopBase, self)._onUnregisterFlashComponent(viewPy, alias)

    def _getUrl(self):
        return self._url

    @process
    def __loadBrowser(self, width, height):
        url = self._getUrl()
        if url is not None:
            self.__browserId = yield self.browserCtrl.load(url=url, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser, browserID=self.alias)
            self.__browser = self.browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = True
                self.__browser.useSpecialKeys = False
                self.__browser.ignoreAltKey = True
                if self._useLastSessionUrl:
                    self.__browser.onLoadStart += self._updateLastUrl
            self.__updateSkipEscape(not self.__hasFocus)
        else:
            _logger.error('ERROR: Browser could not be opened. Invalid URL!')
        return

    def _populate(self):
        super(IngameShopBase, self)._populate()
        self.fireEvent(events.IngameShopEvent(events.IngameShopEvent.INGAMESHOP_ACTIVATED), scope=EVENT_BUS_SCOPE.DEFAULT)
        self.as_setBrowserParamsS(self._browserParams)

    def _dispose(self):
        if self._useLastSessionUrl:
            _gelLastSessionInfo().refreshLifetime()
        if self.__browser:
            self.__browser.onLoadStart -= self._updateLastUrl
        super(IngameShopBase, self)._dispose()
        if self.__browserId:
            self.browserCtrl.delBrowser(self.__browserId)
        self.fireEvent(events.IngameShopEvent(events.IngameShopEvent.INGAMESHOP_DEACTIVATED), scope=EVENT_BUS_SCOPE.DEFAULT)

    def _refresh(self):
        self.__browser.refresh()

    @staticmethod
    def _updateLastUrl(newUrl):
        _gelLastSessionInfo().url = newUrl

    def __updateSkipEscape(self, skipEscape):
        if self.__browser is not None:
            self.__browser.skipEscape = skipEscape
            self.__browser.ignoreKeyEvents = skipEscape
        return

    def __onError(self):
        self.__updateSkipEscape(True)
        self.fireEvent(events.IngameShopEvent(events.IngameShopEvent.INGAMESHOP_DATA_UNAVAILABLE), scope=EVENT_BUS_SCOPE.DEFAULT)

    def __showBrowser(self):
        self.__loadBrowserCbID = BigWorld.callback(0.01, self.__loadBrowserAS)

    def __loadBrowserAS(self):
        self.__loadBrowserCbID = None
        self.as_loadBrowserS()
        return


class IngameShopView(LobbySubView, IngameShopBase):
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(IngameShopView, self).__init__(ctx)
        self._useLastSessionUrl = True
        if not self._url:
            self._url = _gelLastSessionInfo().url
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


class IngameShopOverlay(IngameShopBase):

    def __init__(self, *args):
        super(IngameShopOverlay, self).__init__(*args)
        self.__uniqueBrowserName = VIEW_ALIAS.OVERLAY_WEB_STORE

    @property
    def uniqueBrowserName(self):
        return self.__uniqueBrowserName

    def onEscapePress(self):
        if not self._browserParams.get('isTransparent'):
            self.destroy()
