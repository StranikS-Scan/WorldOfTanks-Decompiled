# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/Browser.py
from Event import Event
from web.client_web_api.common import WebEventSender
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.meta.BrowserMeta import BrowserMeta
from gui.Scaleform.locale.MENU import MENU
from gui.shared.events import BrowserEvent
from gui.shared.formatters import icons
from helpers import i18n, dependency
from skeletons.gui.game_control import IBrowserController
from web.web_client_api import WebCommandHandler
from soft_exception import SoftException

class Browser(BrowserMeta):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(Browser, self).__init__()
        self.__browserID = None
        self.__browser = None
        self.__size = None
        self.__isLoaded = True
        self.__httpStatusCode = None
        self.__webCommandHandler = None
        self.__webEventSender = None
        self.showContentUnderLoading = True
        self.onError = Event()
        return

    @property
    def browser(self):
        return self.__browser

    def init(self, browserID, webHandlersMap=None, alias=''):
        self.__browserID = browserID
        self.__browser = self.browserCtrl.getBrowser(self.__browserID)
        if self.__browser is None:
            raise SoftException('Cannot find browser')
        self.__webCommandHandler = WebCommandHandler(self.__browserID, alias, self)
        if webHandlersMap is not None:
            self.__webCommandHandler.addHandlers(webHandlersMap)
        self.__webCommandHandler.onCallback += self.__onWebCommandCallback
        self.__webEventSender = WebEventSender()
        self.__webEventSender.onCallback += self.__onWebEventCallback
        self.__webEventSender.init()
        if not self.__browser.hasBrowser:
            self.addListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
        else:
            self.__prepareBrowser()
        return

    def onWindowClose(self):
        self.destroy()

    def browserAction(self, action):
        if self.__browser is not None:
            self.__browser.browserAction(action)
        return

    def browserMove(self, x, y, z):
        if self.__browser is not None:
            self.__browser.browserMove(x, y, z)
        return

    def browserDown(self, x, y, z):
        if self.__browser is not None:
            self.__browser.browserDown(x, y, z)
        return

    def browserUp(self, x, y, z):
        if self.__browser is not None:
            self.__browser.browserUp(x, y, z)
        return

    def browserFocusOut(self):
        if self.__browser is not None:
            self.__browser.browserFocusOut()
        return

    def onBrowserShow(self, needRefresh=False):
        self.__browser.onBrowserShow(needRefresh)

    def onBrowserHide(self):
        if self.__browser is not None:
            self.__browser.onBrowserHide()
        return

    def invalidateView(self):
        if self.__browser is not None:
            self.__browser.invalidateView()
        return

    def setBrowserSize(self, width, height):
        self.__size = (width, height)
        if self.__browser is not None:
            self.__browser.updateSize(self.__size)
        return

    def showDataUnavailableView(self):
        header = icons.alert() + i18n.makeString(MENU.BROWSER_DATAUNAVAILABLE_HEADER)
        description = i18n.makeString(MENU.BROWSER_DATAUNAVAILABLE_DESCRIPTION)
        self.as_loadingStopS()
        self.as_showServiceViewS(header, description)
        self.onError()

    def showLoading(self, show):
        if show:
            self.as_loadingStartS(self.showContentUnderLoading)
        else:
            self.as_loadingStopS()

    def _dispose(self):
        if self.__browser:
            self.__browser.onLoadStart -= self.__onLoadStart
            self.__browser.onLoadingStateChange -= self.__onLoadingStateChange
            self.__browser.onLoadEnd -= self.__onLoadEnd
            self.__browser.onNavigate -= self.__onNavigate
            self.__browser.onJsHostQuery -= self.__onJsHostQuery
            self.__browser.onTitleChange -= self.__onTitleChange
            self.__browser = None
        if self.__webCommandHandler:
            self.__webCommandHandler.onCallback -= self.__onWebCommandCallback
            self.__webCommandHandler.fini()
            self.__webCommandHandler = None
        if self.__webEventSender:
            self.__webEventSender.onCallback -= self.__onWebEventCallback
            self.__webEventSender.fini()
            self.__webEventSender = None
        self.browserCtrl.delBrowser(self.__browserID)
        self.removeListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
        super(Browser, self)._dispose()
        return

    def __onLoadStart(self, url):
        pass

    def __onLoadEnd(self, _, isLoaded=True, httpStatusCode=None):
        self.__isLoaded = self.__isLoaded and isLoaded
        self.__httpStatusCode = httpStatusCode
        if not self.__checkIsPageLoaded():
            self.showDataUnavailableView()

    def __onLoadingStateChange(self, isLoading, manageLoadingScreen):
        if isLoading and manageLoadingScreen:
            self.as_loadingStartS(self.showContentUnderLoading)
        elif not self.__checkIsPageLoaded():
            self.showDataUnavailableView()
        elif manageLoadingScreen:
            self.as_loadingStopS()

    def __checkIsPageLoaded(self):
        if not self.__isLoaded:
            return False
        return False if self.__httpStatusCode and self.__httpStatusCode >= 400 else True

    def __onNavigate(self, _):
        self.as_hideServiceViewS()
        self.__isLoaded = True

    def __onJsHostQuery(self, command):
        try:
            if self.__webCommandHandler is not None:
                self.__webCommandHandler.handleCommand(command)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    def __onWebCommandCallback(self, callbackData):
        self.__browser.sendMessage(callbackData)

    def __onWebEventCallback(self, callbackData):
        self.__browser.sendEvent(callbackData)

    def __onTitleChange(self, title):
        self.as_changeTitleS(title)

    def __handleBrowserCreated(self, event):
        if event.ctx['browserID'] == self.__browserID:
            self.removeListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
            self.__browser = self.browserCtrl.getBrowser(self.__browserID)
            if self.__browser is None:
                raise SoftException('Cannot find browser')
            self.__prepareBrowser()
        return

    def __prepareBrowser(self):
        self.__browser.onLoadStart += self.__onLoadStart
        self.__browser.onLoadingStateChange += self.__onLoadingStateChange
        self.__browser.onLoadEnd += self.__onLoadEnd
        self.__browser.onNavigate += self.__onNavigate
        self.__browser.onJsHostQuery += self.__onJsHostQuery
        self.__browser.onTitleChange += self.__onTitleChange
        if self.__size is not None:
            self.__browser.updateSize(self.__size)
        if self.__browser.isNavigationComplete:
            self.as_loadingStopS()
        return
