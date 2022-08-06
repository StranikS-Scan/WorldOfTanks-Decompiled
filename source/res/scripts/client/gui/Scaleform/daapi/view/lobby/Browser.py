# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/Browser.py
import typing
import SCALEFORM
from Event import Event
from gui.browser import BrowserViewWebHandlers
from gui.Scaleform.daapi.view.meta.BrowserMeta import BrowserMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.shared.events import BrowserEvent
from gui.shared.formatters import icons
from WebBrowser import CURSOR_TYPES
from helpers import i18n, dependency
from skeletons.gui.game_control import IBrowserController
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from WebBrowser import WebBrowser
_CURSOR_TYPES = {CURSOR_TYPES.Hand: CursorManager.HAND,
 CURSOR_TYPES.Pointer: CursorManager.ARROW,
 CURSOR_TYPES.IBeam: CursorManager.IBEAM,
 CURSOR_TYPES.Grab: CursorManager.DRAG_OPEN,
 CURSOR_TYPES.Grabbing: CursorManager.DRAG_CLOSE,
 CURSOR_TYPES.ColumnResize: CursorManager.MOVE}

def _getCursorType(cursorType):
    return _CURSOR_TYPES.get(cursorType) or CursorManager.ARROW


class Browser(BrowserMeta):
    __browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(Browser, self).__init__()
        self.__browserID = None
        self.__browser = None
        self.__size = None
        self.__isLoaded = True
        self.__httpStatusCode = None
        self.__webCommandHandler = None
        self.showContentUnderLoading = True
        self.onError = Event()
        return

    @property
    def browser(self):
        return self.__browser

    def init(self, browserID, webHandlersMap=None, alias=''):
        if self.__browserID == browserID:
            return
        else:
            self.__clean()
            self.__browserID = browserID
            self.__browser = self.__browserCtrl.getBrowser(self.__browserID)
            if self.__browser is None:
                raise SoftException('Cannot find browser')
            self.__webCommandHandler = BrowserViewWebHandlers(self.__browser, self.__browserID, self, webHandlersMap, alias)
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
        if not self.__browser.isFocused:
            self.__setCursor()
        self.__browser.onBrowserShow(needRefresh)

    def onBrowserHide(self):
        if self.__browser is not None:
            self.__browser.onBrowserHide()
        return

    def invalidateView(self):
        if self.__browser is not None:
            self.__browser.invalidateView()
        return

    def setBrowserSize(self, width, height, scale):
        self.__size = (width, height, scale)
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
        self.__clean()
        if self.__webCommandHandler:
            self.__webCommandHandler.fini()
            self.__webCommandHandler = None
        if self.__browser:
            SCALEFORM.resetScaleformWebRender(self.__browser.id)
        self.__browserCtrl.delBrowser(self.__browserID)
        self.__browser = None
        self.app.cursorMgr.setCursorForced(CursorManager.ARROW)
        super(Browser, self)._dispose()
        return

    def __clean(self):
        if self.__browser:
            self.__browser.onLoadStart -= self.__onLoadStart
            self.__browser.onLoadingStateChange -= self.__onLoadingStateChange
            self.__browser.onLoadEnd -= self.__onLoadEnd
            self.__browser.onNavigate -= self.__onNavigate
            self.__browser.onJsHostQuery -= self.__onJsHostQuery
            self.__browser.onTitleChange -= self.__onTitleChange
            self.__browser.onCursorUpdated -= self.__onCursorUpdated
            self.__browser.onResized -= self.__onResized
        self.removeListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)

    def __onLoadStart(self, url):
        pass

    def __onLoadEnd(self, _, isLoaded=True, httpStatusCode=None):
        self.__isLoaded = self.__isLoaded and isLoaded
        self.__httpStatusCode = httpStatusCode
        if not self.__checkIsPageLoaded():
            self.showDataUnavailableView()

    def __onReady(self, *args):
        self.__browser.onReady -= self.__onReady
        self.as_loadBitmapS(SCALEFORM.setScaleformWebRender(self.__browser.id))

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
        self.__webCommandHandler.handleCommand(command)

    def __onTitleChange(self, title):
        self.as_changeTitleS(title)

    def __onCursorUpdated(self, _):
        self.__setCursor()

    def __onResized(self, width, height):
        self.as_resizeS(width, height)

    def __handleBrowserCreated(self, event):
        if event.ctx['browserID'] == self.__browserID:
            self.removeListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
            self.__browser = self.__browserCtrl.getBrowser(self.__browserID)
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
        self.__browser.onCursorUpdated += self.__onCursorUpdated
        self.__browser.onResized += self.__onResized
        if self.__size is not None:
            self.__browser.updateSize(self.__size)
        if SCALEFORM.hasScaleformWebRender(self.__browser.id):
            self.as_loadBitmapS(SCALEFORM.getWebTextureUrl(self.__browser.id))
        elif self.__browser.isReady:
            self.as_loadBitmapS(SCALEFORM.setScaleformWebRender(self.__browser.id))
        else:
            self.__browser.onReady += self.__onReady
        if self.__browser.isNavigationComplete:
            self.as_loadingStopS()
        return

    def __setCursor(self):
        self.app.cursorMgr.setCursorForced(_getCursorType(self.__browser.cursor))
