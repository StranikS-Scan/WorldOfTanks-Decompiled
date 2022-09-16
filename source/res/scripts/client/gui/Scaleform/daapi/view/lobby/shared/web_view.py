# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shared/web_view.py
import logging
import typing
import BigWorld
from adisp import adisp_process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.BrowserView import makeBrowserParams
from gui.Scaleform.daapi.view.meta.BrowserScreenMeta import BrowserScreenMeta
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.ambients import HangarOverlayEnv
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.managers import ContainerManager
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
BROWSER_LOAD_CALLBACK_DELAY = 0.01

class WebView(BrowserScreenMeta):
    __browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, ctx=None):
        super(WebView, self).__init__(ctx)
        self.__browser = None
        self.__hasFocus = False
        self.__browserId = 0
        self.__loadBrowserCbID = None
        self.__ctx = ctx or {}
        self._url = ctx.get('url') if ctx else None
        self._forcedSkipEscape = ctx.get('forcedSkipEscape', False) if ctx else False
        self._browserParams = (ctx or {}).get('browserParams', makeBrowserParams())
        self.__callbackOnLoad = ctx.get('callbackOnLoad', None) if ctx else None
        return

    @property
    def webHandlersReplacements(self):
        return None

    def onEscapePress(self):
        if not self._browserParams.get('isHidden'):
            self.destroy()

    def onCloseBtnClick(self):
        if not self._browserParams.get('isHidden'):
            self.destroy()

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape(not hasFocus)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def getBrowser(self):
        return self.__browser

    def webHandlers(self):
        from gui.Scaleform.daapi.view.lobby.shared.web_handlers import createWebHandlers
        return createWebHandlers(self.webHandlersReplacements)

    def _onRegisterFlashComponent(self, viewPy, alias):
        webHandlers = self.webHandlers()
        super(WebView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(browserID=self.__browserId, webHandlersMap=webHandlers)
            viewPy.onError += self._onError

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self._onError
        super(WebView, self)._onUnregisterFlashComponent(viewPy, alias)

    def _getUrl(self):
        return self._url

    def _populate(self):
        super(WebView, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_OVERLAY_BROWSER_VIEW, self.__handleBrowserClose, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_setBrowserParamsS(self._browserParams)

    def _dispose(self):
        super(WebView, self)._dispose()
        self.removeListener(events.HideWindowEvent.HIDE_OVERLAY_BROWSER_VIEW, self.__handleBrowserClose, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__browserId:
            self.__browserCtrl.delBrowser(self.__browserId)

    def _refresh(self):
        self.__browser.refresh()

    def _onError(self):
        self.__updateSkipEscape(True)

    @adisp_process
    def __loadBrowser(self, width, height):
        url = self._getUrl()
        if url is not None:
            self.__browserId = yield self.__browserCtrl.load(url=url, useBrowserWindow=False, browserSize=(width, height), showBrowserCallback=self.__showBrowser, browserID=self.alias)
            self.__browser = self.__browserCtrl.getBrowser(self.__browserId)
            if self.__browser:
                self.__browser.allowRightClick = self.__ctx.get('allowRightClick', True)
                self.__browser.useSpecialKeys = self.__ctx.get('useSpecialKeys', False)
                self.__browser.ignoreAltKey = self.__ctx.get('ignoreAltKey', True)
                self.__browser.ignoreCtrlClick = self.__ctx.get('ignoreCtrlClick', True)
                self.__browser.ignoreShiftClick = self.__ctx.get('ignoreShiftClick', True)
            self.__updateSkipEscape(not self.__hasFocus)
        else:
            _logger.error('ERROR: Browser could not be opened. Invalid URL!')
        return

    def __updateSkipEscape(self, skipEscape):
        if self.__browser is not None:
            self.__browser.skipEscape = self._forcedSkipEscape or skipEscape
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


class WebViewTransparent(WebView):
    __sound_env__ = HangarOverlayEnv

    def __init__(self, ctx=None):
        super(WebViewTransparent, self).__init__(ctx)
        self._browserParams = makeBrowserParams(bgAlpha=0.67)
        self._browserParams.update((ctx or {}).get('browserParams', {}))
        self.__blur = None
        self.__hiddenLayers = (ctx or {}).get('hiddenLayers', ())
        return

    def _populate(self):
        super(WebViewTransparent, self)._populate()
        if self.__hiddenLayers:
            containerManager = self.app.containerManager
            containerManager.hideContainers(self.__hiddenLayers, 0)

    def setParentWindow(self, window):
        super(WebViewTransparent, self).setParentWindow(window)
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer)

    def onEscapePress(self):
        self.destroy()

    def _dispose(self):
        if self.__blur is not None:
            self.__blur.fini()
        if self.__hiddenLayers:
            containerManager = self.app.containerManager
            containerManager.showContainers(self.__hiddenLayers, 0)
        super(WebViewTransparent, self)._dispose()
        return
