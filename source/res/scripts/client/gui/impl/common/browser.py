# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/browser.py
import logging
import typing
import Event
from frameworks.wulf import ViewSettings, ViewFlags
from gui.browser import BrowserViewWebHandlers
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.common.browser_model import BrowserModel, BrowserState, PageState, TetxureState
from gui.impl.gen import R
from helpers import dependency
from adisp import adisp_process
from skeletons.gui.game_control import IBrowserController
if typing.TYPE_CHECKING:
    from typing import Optional
    from WebBrowser import WebBrowser
    from web.web_client_api import webApiCollection
_logger = logging.getLogger(__name__)

class BrowserSettings(ViewSettings):

    def __init__(self, layoutID=R.views.common.Browser(), flags=ViewFlags.VIEW, model=None, args=()):
        super(BrowserSettings, self).__init__(layoutID, flags, model or BrowserModel(), args)


TViewModel = typing.TypeVar('TViewModel', bound=BrowserModel)

class Browser(ViewImpl[TViewModel]):
    __slots__ = ('__url', '__browserId', '__browser', '__webCommandHandler', '__webHandlersMap', 'onBrowserObtained', '__eventManager')
    __browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, url='', settings=None, webHandlersMap=None, preload=False, *args, **kwargs):
        super(Browser, self).__init__((settings or BrowserSettings()), *args, **kwargs)
        self.__url = url
        self.__browserId = 0
        self.__webHandlersMap = webHandlersMap
        self.__browser = None
        self.__webCommandHandler = None
        self.__eventManager = Event.EventManager()
        self.onBrowserObtained = Event.Event(self.__eventManager)
        self.getViewModel().setBrowserState(BrowserState.INITIALIZATION)
        self.getViewModel().setPageState(PageState.INITIALIZATION)
        self.getViewModel().setTexState(TetxureState.INITIALIZATION)
        if preload and self.__url:
            self.__loadBrowser()
        return

    @property
    def browser(self):
        return self.__browser

    @property
    def url(self):
        return self.__url

    def setWaitingMessage(self, message):
        self.getViewModel().setWaitingMessage(message)

    def showLoading(self, show):
        if show:
            self.getViewModel().setBrowserState(BrowserState.FORCELOADING)
        else:
            self.getViewModel().setBrowserState(BrowserState.LOADED)

    def _getEvents(self):
        return ((self.getViewModel().createWebView, self.__onCreateVebView),
         (self.getViewModel().focus, self.__onFocus),
         (self.getViewModel().unfocus, self.__onUnfocus),
         (self.getViewModel().reload, self.__onReload))

    def _finalize(self):
        self.__browserCtrl.onBrowserAdded -= self.__onBrowserAddedHandler
        if self.__webCommandHandler:
            self.__webCommandHandler.fini()
        if self.__browser:
            self.__browser.onLoadStart -= self.__onLoadStart
            self.__browser.onLoadingStateChange -= self.__onLoadingStateChange
            self.__browser.onLoadEnd -= self.__onLoadEnd
            self.__browser.onTitleChange -= self.__onTitleChange
            self.__browser.onJsHostQuery -= self.__onJsHostQuery
            self.__browser.onTextureStateChanged -= self.__onTextureStateChanged
        if self.__browserId:
            self.__browserCtrl.delBrowser(self.__browserId)
        self.__eventManager.clear()
        super(Browser, self)._finalize()

    @adisp_process
    def __loadBrowser(self):
        self.__browserId = yield self.__browserCtrl.load(url=self.__url, useBrowserWindow=False)
        self.__browser = self.__browserCtrl.getBrowser(self.__browserId)
        if self.__browser is not None and self.__browser.hasBrowser:
            self.__initBrowser()
        else:
            self.__browserCtrl.onBrowserAdded += self.__onBrowserAddedHandler
        return

    def __initBrowser(self):
        self.onBrowserObtained(self.__browser)
        self.__browser.onLoadStart += self.__onLoadStart
        self.__browser.onLoadingStateChange += self.__onLoadingStateChange
        self.__browser.onLoadEnd += self.__onLoadEnd
        self.__browser.onTitleChange += self.__onTitleChange
        self.__browser.onJsHostQuery += self.__onJsHostQuery
        self.__browser.onTextureStateChanged += self.__onTextureStateChanged
        with self.getViewModel().transaction() as model:
            model.setId(self.__browserId)
            if self.__browser.isNavigationComplete:
                model.setBrowserState(BrowserState.LOADED)
        self.__webCommandHandler = BrowserViewWebHandlers(self.__browser, self.__browserId, self, self.__webHandlersMap)

    def __onBrowserAddedHandler(self, browserId):
        if browserId != self.__browserId:
            return
        self.__browser = self.__browserCtrl.getBrowser(self.__browserId)
        self.__initBrowser()

    def __onCreateVebView(self):
        if self.__browserId:
            _logger.error('Browser creation was already requested. id: %i', self.__browserId)
            return
        self.__loadBrowser()

    def __onFocus(self):
        if not self.__browser:
            _logger.error('Browser not created')
            return
        self.__browser.focus()

    def __onUnfocus(self):
        if not self.__browser:
            _logger.error('Browser not created')
            return
        self.__browser.unfocus()

    def __onReload(self):
        if not self.__browser:
            _logger.error('Browser not created')
            return
        self.__browser.refresh()

    def __onLoadStart(self, url):
        self.getViewModel().setPageState(PageState.LOADING)

    def __onLoadEnd(self, _, isLoaded=True, httpStatusCode=None):
        with self.getViewModel().transaction() as model:
            model.setPageState(PageState.LOADED if isLoaded else PageState.FAILED)
            if httpStatusCode is not None:
                model.setHttpStatusCode(httpStatusCode)
        return

    def __onLoadingStateChange(self, isLoading, allowAutoLoadingScreenChange):
        with self.getViewModel().transaction() as model:
            if allowAutoLoadingScreenChange:
                model.setBrowserState(BrowserState.LOADING if isLoading else BrowserState.LOADED)

    def __onTitleChange(self, title):
        self.getViewModel().setTitle(title)

    def __onJsHostQuery(self, command):
        self.__webCommandHandler.handleCommand(command)

    def __onTextureStateChanged(self, isOk):
        self.getViewModel().setTexState(TetxureState.LOADED if isOk else TetxureState.FAILED)
