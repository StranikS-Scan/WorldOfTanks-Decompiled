# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_overlay_base.py
import logging
import BigWorld
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.daapi.view.meta.IngameShopViewMeta import IngameShopViewMeta
from gui.shared import events, EVENT_BUS_SCOPE
from skeletons.gui.game_control import IBrowserController
from helpers import dependency
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
BROWSER_LOAD_CALLBACK_DELAY = 0.01

class WebOverlayBase(IngameShopViewMeta):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, ctx=None):
        super(WebOverlayBase, self).__init__(ctx)
        self.__browser = None
        self.__hasFocus = False
        self.__browserId = 0
        self.__loadBrowserCbID = None
        self.__ctx = ctx
        self._url = ctx.get('url') if ctx else None
        self.__callbackOnLoad = ctx.get('callbackOnLoad', None) if ctx else None
        self._browserParams = (ctx or {}).get('browserParams', makeBrowserParams())
        return

    def onEscapePress(self):
        if not self._browserParams.get('isTransparent'):
            self.destroy()

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape(not hasFocus)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def getBrowser(self):
        return self.__browser

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createBrowserOverlayWebHandlers
        return createBrowserOverlayWebHandlers()

    def _onRegisterFlashComponent(self, viewPy, alias):
        webHandlers = self.webHandlers()
        super(WebOverlayBase, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(browserID=self.__browserId, webHandlersMap=webHandlers)
            viewPy.onError += self._onError

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self._onError
        super(WebOverlayBase, self)._onUnregisterFlashComponent(viewPy, alias)

    def _getUrl(self):
        return self._url

    def _populate(self):
        super(WebOverlayBase, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_OVERLAY_BROWSER_VIEW, self.__handleBrowserClose, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_setBrowserParamsS(self._browserParams)

    def _dispose(self):
        super(WebOverlayBase, self)._dispose()
        self.removeListener(events.HideWindowEvent.HIDE_OVERLAY_BROWSER_VIEW, self.__handleBrowserClose, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__browserId:
            self.browserCtrl.delBrowser(self.__browserId)

    def _refresh(self):
        self.__browser.refresh()

    def _onError(self):
        self.__updateSkipEscape(True)

    def __getFromCtx(self, name, default=None):
        ctx = self.__ctx
        return ctx.get(name, default) if ctx else default

    @process
    def __loadBrowser(self, width, height):
        url = self._getUrl()
        if url is not None:
            self.__browserId = yield self.browserCtrl.load(url=url, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser, browserID=self.alias)
            self.__browser = self.browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = self.__getFromCtx('allowRightClick', True)
                self.__browser.useSpecialKeys = self.__getFromCtx('useSpecialKeys', False)
                self.__browser.ignoreAltKey = self.__getFromCtx('ignoreAltKey', True)
            self.__updateSkipEscape(not self.__hasFocus)
        else:
            _logger.error('ERROR: Browser could not be opened. Invalid URL!')
        return

    def __updateSkipEscape(self, skipEscape):
        if self.__browser is not None:
            self.__browser.skipEscape = skipEscape
            self.__browser.ignoreKeyEvents = skipEscape
        return

    def __showBrowser(self):
        self.__loadBrowserCbID = BigWorld.callback(BROWSER_LOAD_CALLBACK_DELAY, self.__loadBrowserAS)

    def __loadBrowserAS(self):
        self.__loadBrowserCbID = None
        if self.__callbackOnLoad is not None:
            self.__callbackOnLoad()
        self.as_loadBrowserS()
        return

    def __handleBrowserClose(self, _):
        self.destroy()
