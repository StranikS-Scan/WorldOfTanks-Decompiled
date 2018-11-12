# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/WebBrowser.py
import weakref
import urlparse
import functools
import logging
import BigWorld
import Keys
import helpers
from gui.Scaleform.managers.Cursor import Cursor
from gui.shared import event_dispatcher
from Event import Event, EventManager
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from web.cache.web_cache import WebExternalCache
_logger = logging.getLogger(__name__)
_BROWSER_KEY_LOGGING = False
_WOT_CLIENT_PARAM_NAME = 'wot_client_param'
_WOT_RESOURCE_CUSTOM_SCHEME = 'wotdata'
_WEB_CACHE_FOLDER = 'web_cache'
_WEB_MANIFEST_KEY = 'webManifestURL'
_g_webCache = None

def initExternalCache():
    global _g_webCache
    if _g_webCache is None:
        _logger.info('WebExternalCache init')
        _g_webCache = WebExternalCache(_WEB_CACHE_FOLDER)
        _g_webCache.load()
        _g_webCache.prefetchStart(GUI_SETTINGS.lookup(_WEB_MANIFEST_KEY))
    return


def destroyExternalCache():
    global _g_webCache
    if _g_webCache is not None:
        _g_webCache.close()
        _g_webCache = None
        _logger.info('WebExternalCache destroyed')
    return


class WebBrowser(object):
    hasBrowser = property(lambda self: self.__browser is not None)
    intializationUrl = property(lambda self: self.__baseUrl)
    baseUrl = property(lambda self: '' if self.__browser is None else self.__baseUrl)
    url = property(lambda self: '' if self.__browser is None else self.__browser.url)
    width = property(lambda self: 0 if self.__browser is None else self.__browser.width)
    height = property(lambda self: 0 if self.__browser is None else self.__browser.height)
    isNavigationComplete = property(lambda self: self.__isNavigationComplete)
    isFocused = property(lambda self: self.__isFocused)
    updateInterval = 0.01
    isSuccessfulLoad = property(lambda self: self.__successfulLoad)
    skipEscape = property(lambda self: self.__skipEscape)
    ignoreKeyEvents = property(lambda self: self.__ignoreKeyEvents)
    ignoreAltKey = property(lambda self: self.__ignoreAltKey)
    useSpecialKeys = property(lambda self: self.__useSpecialKeys)
    allowRightClick = property(lambda self: self.__allowRightClick)
    allowMouseWheel = property(lambda self: self.__allowMouseWheel)

    @skipEscape.setter
    def skipEscape(self, value):
        _logger.debug('skipEscape set %s (was: %s)', value, self.__skipEscape)
        self.__skipEscape = value

    @ignoreKeyEvents.setter
    def ignoreKeyEvents(self, value):
        _logger.debug('ignoreKeyEvents set %s (was: %s)', value, self.__ignoreKeyEvents)
        self.__ignoreKeyEvents = value

    @ignoreAltKey.setter
    def ignoreAltKey(self, value):
        _logger.debug('ignoreAltKey set %s (was: %s)', value, self.__ignoreAltKey)
        self.__ignoreAltKey = value

    @useSpecialKeys.setter
    def useSpecialKeys(self, value):
        _logger.debug('useSpecialKeys set %s (was: %s)', value, self.__useSpecialKeys)
        self.__useSpecialKeys = value

    @allowRightClick.setter
    def allowRightClick(self, value):
        _logger.debug('allowRightClick set %s (was: %s)', value, self.__allowRightClick)
        self.__allowRightClick = value

    @allowMouseWheel.setter
    def allowMouseWheel(self, value):
        _logger.debug('allowMouseWheel set %s (was: %s)', value, self.__allowMouseWheel)
        self.__allowMouseWheel = value

    def __init__(self, browserID, uiObj, texName, size, url='about:blank', isFocused=False, handlers=None):
        self.__browserID = browserID
        self.__cbID = None
        self.__baseUrl = url
        self.__uiObj = uiObj
        self.__texName = texName
        self.__browserSize = size
        self.__startFocused = isFocused
        self.__browser = None
        self.__isNavigationComplete = False
        self.__isFocused = False
        self.__navigationFilters = handlers or set()
        self.__skipEscape = True
        self.__ignoreKeyEvents = False
        self.__ignoreAltKey = False
        self.__useSpecialKeys = True
        self.__allowRightClick = False
        self.__allowMouseWheel = True
        self.__allowAutoLoadingScreenChange = True
        self.__isCloseTriggered = False
        self.__eventMgr = EventManager()
        self.onLoadStart = Event(self.__eventMgr)
        self.onLoadEnd = Event(self.__eventMgr)
        self.onLoadingStateChange = Event(self.__eventMgr)
        self.onReadyToShowContent = Event(self.__eventMgr)
        self.onNavigate = Event(self.__eventMgr)
        self.onReady = Event(self.__eventMgr)
        self.onJsHostQuery = Event(self.__eventMgr)
        self.onTitleChange = Event(self.__eventMgr)
        self.onFailedCreation = Event(self.__eventMgr)
        self.onCanCreateNewBrowser = Event(self.__eventMgr)
        self.onUserRequestToClose = Event(self.__eventMgr)
        _logger.info('INIT %s texture: %s, size %s, id: %s', self.__baseUrl, texName, size, self.__browserID)
        return

    def create(self):
        _logger.info('CREATE %s - %r', self.__baseUrl, self.__browserID)
        clientLanguage = helpers.getClientLanguage()
        self.__browser = BigWorld.createBrowser(self.__browserID, clientLanguage)
        if self.__browser is None:
            _logger.error('create() NO BROWSER WAS CREATED: %s', self.__baseUrl)
            return False
        else:
            self.__browser.script = EventListener(self)
            self.__browser.script.onLoadStart += self.__onLoadStart
            self.__browser.script.onLoadEnd += self.__onLoadEnd
            self.__browser.script.onLoadingStateChange += self.__onLoadingStateChange
            self.__browser.script.onDOMReady += self.__onReadyToShowContent
            self.__browser.script.onCursorUpdated += self.__onCursorUpdated
            self.__browser.script.onReady += self.__onReady
            self.__browser.script.onJsHostQuery += self.__onJsHostQuery
            self.__browser.script.onTitleChange += self.__onTitleChange

            def injectBrowserKeyEvent(me, e):
                if _BROWSER_KEY_LOGGING:
                    _logger.debug('injectBrowserKeyEvent: %s', (e.key,
                     e.isKeyDown(),
                     e.isAltDown(),
                     e.isShiftDown(),
                     e.isCtrlDown()))
                me.__browser.injectKeyEvent(e)

            def injectKeyDown(me, e):
                injectBrowserKeyEvent(me, e)

            def injectKeyUp(me, e):
                injectBrowserKeyEvent(me, e)

            def resetBit(value, bitMask):
                return value & ~bitMask

            self.__specialKeyHandlers = ((Keys.KEY_LEFTARROW,
              True,
              True,
              None,
              None,
              lambda me, _: me.__browser.goBack()), (Keys.KEY_RIGHTARROW,
              True,
              True,
              None,
              None,
              lambda me, _: me.__browser.goForward()), (Keys.KEY_F5,
              True,
              None,
              None,
              None,
              lambda me, _: me.__browser.reload()))
            self.__browserKeyHandlers = ((Keys.KEY_LSHIFT,
              False,
              None,
              True,
              None,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 1), None, e.cursorPosition))),
             (Keys.KEY_RSHIFT,
              False,
              None,
              True,
              None,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 1), None, e.cursorPosition))),
             (Keys.KEY_LCONTROL,
              False,
              None,
              None,
              True,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 2), None, e.cursorPosition))),
             (Keys.KEY_RCONTROL,
              False,
              None,
              None,
              True,
              lambda me, e: injectKeyUp(me, BigWorld.KeyEvent(e.key, e.repeatCount, resetBit(e.modifiers, 2), None, e.cursorPosition))),
             (None,
              True,
              None,
              None,
              None,
              injectKeyDown),
             (None,
              False,
              None,
              None,
              None,
              injectKeyUp))
            self.__disableKeyHandlers = []
            return True

    def setDisabledKeys(self, keys):
        self.__disableKeyHandlers = []
        for key, isKeyDown, isAltDown, isShiftDown, isCtrlDown in keys:
            self.__disableKeyHandlers.append((key,
             isKeyDown,
             isAltDown,
             isShiftDown,
             isCtrlDown,
             lambda me, e: None))

    def ready(self, success):
        _logger.info('READY %r %s %r', success, self.__baseUrl, self.__browserID)
        self.__ui = weakref.ref(self.__uiObj)
        self.__readyToShow = False
        self.__successfulLoad = False
        self.enableUpdate = True
        self.__isMouseDown = False
        self.__isFocused = False
        self.__isWaitingForUnfocus = False
        if success:
            browserSize = self.__browserSize
            self.__browser.setScaleformRender(self.__uiObj.movie, self.__texName, browserSize[0], browserSize[1])
            self.__browser.activate(True)
            self.__browser.focus()
            self.__browser.loadURL(self.__baseUrl)
            if self.__startFocused:
                self.focus()
            self.update()
            g_mgr.addBrowser(self)
            self.onReady(self.__browser.url, success)
        else:
            self.__isNavigationComplete = True
            _logger.error(' FAILED %s - %r', self.__baseUrl, self.__browserID)
            self.onFailedCreation(self.__baseUrl)

    def updateSize(self, size):
        self.__browserSize = size
        if self.hasBrowser:
            self.__browser.resize(size[0], size[1])

    def destroy(self):
        self.__eventMgr.clear()
        self.__eventMgr = None
        if self.__browser is not None:
            _logger.info('DESTROYED %s - %r', self.__baseUrl, self.__browserID)
            self.__browser.script.clear()
            self.__browser.script = None
            self.__browser.resetScaleformRender(self.__uiObj.movie, self.__texName)
            BigWorld.removeBrowser(self.__browserID)
            self.__browser = None
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        self.__ui = None
        self.__navigationFilters = None
        self.__setUICursor(self.__uiObj, Cursor.ARROW)
        g_mgr.delBrowser(self)
        return

    def focus(self):
        if self.hasBrowser and not self.isFocused:
            self.__browser.focus()
            self.__isFocused = True
            self.__setUICursor(self.__ui(), self.__browser.script.cursorType)

    def unfocus(self):
        if self.hasBrowser and self.isFocused:
            self.__browser.unfocus()
            self.__isFocused = False
            self.__isWaitingForUnfocus = False

    def refresh(self, ignoreCache=True):
        if BigWorld.time() - self.__loadStartTime < 0.5:
            _logger.debug('refresh - called too soon')
            return
        if self.hasBrowser:
            self.__browser.reload()
            self.onNavigate(self.__browser.url)

    def navigate(self, url):
        _logger.debug('navigate %s', url)
        self.__baseUrl = url
        if self.hasBrowser:
            self.__browser.script.newNavigation()
            self.__browser.loadURL(url)
            self.onNavigate(url)

    def sendMessage(self, message):
        if self.hasBrowser:
            self.__browser.sendMessage(message)

    def navigateBack(self):
        if self.hasBrowser:
            self.__browser.goBack(self.url)

    def navigateForward(self):
        if self.hasBrowser:
            self.__browser.goForward(self.url)

    def navigateStop(self):
        if BigWorld.time() - self.__loadStartTime < 0.5:
            _logger.debug('navigateStop - called too soon')
            return
        if self.hasBrowser:
            self.__browser.stop()
            self.__onLoadEnd(self.__browser.url)

    def update(self):
        self.__cbID = BigWorld.callback(self.updateInterval, self.update)

    def __getBrowserKeyHandler(self, key, isKeyDown, isAltDown, isShiftDown, isCtrlDown):
        from itertools import izip
        params = (key,
         isKeyDown,
         isAltDown,
         isShiftDown,
         isCtrlDown)
        matches = lambda t: t[0] is None or t[0] == t[1]
        browserKeyHandlers = tuple(self.__disableKeyHandlers) + self.__browserKeyHandlers
        if self.useSpecialKeys:
            browserKeyHandlers = self.__specialKeyHandlers + browserKeyHandlers
        for values in browserKeyHandlers:
            if functools.reduce(lambda a, b: a and matches(b), izip(values, params), True):
                return values[-1]

        return None

    def handleKeyEvent(self, event):
        e = event
        keyState = (e.key,
         e.isKeyDown(),
         e.isAltDown(),
         e.isShiftDown(),
         e.isCtrlDown())
        if self.__ignoreAltKey and e.key in (Keys.KEY_LALT, Keys.KEY_RALT):
            return False
        if not (self.hasBrowser and self.enableUpdate):
            return False
        if not self.allowRightClick and e.key == Keys.KEY_RIGHTMOUSE:
            return False
        if not self.skipEscape and e.key == Keys.KEY_ESCAPE and e.isKeyDown():
            self.__getBrowserKeyHandler(*keyState)(self, e)
            return True
        if not self.isFocused:
            self.__browser.injectKeyModifiers(e)
            return False
        if _BROWSER_KEY_LOGGING:
            _logger.debug('handleKeyEvent %s', keyState)
        if self.ignoreKeyEvents and e.key not in (Keys.KEY_LEFTMOUSE, Keys.KEY_RIGHTMOUSE):
            return False
        if e.key in (Keys.KEY_ESCAPE, Keys.KEY_SYSRQ):
            return False
        if e.key in (Keys.KEY_RETURN, Keys.KEY_NUMPADENTER) and e.isAltDown():
            return False
        self.__getBrowserKeyHandler(*keyState)(self, e)
        return True

    def browserMove(self, x, y, z):
        if not (self.hasBrowser and self.enableUpdate and self.isFocused):
            return
        if z != 0:
            if self.allowMouseWheel:
                self.__browser.injectMouseWheelEvent(z * 20)
            return
        self.__browser.injectMouseMoveEvent(x, y)

    def browserDown(self, x, y, z):
        if not (self.hasBrowser and self.enableUpdate):
            return
        if self.__isMouseDown:
            return
        if not self.isFocused:
            self.focus()
            self.__isMouseDown = True
            self.browserUp(x, y, z)
            self.browserMove(x, y, z)
        self.__isMouseDown = True

    def browserUp(self, x, y, z):
        if not (self.hasBrowser and self.enableUpdate):
            return
        if not self.__isMouseDown:
            return
        self.__isMouseDown = False
        if self.__isWaitingForUnfocus:
            self.unfocus()

    def browserFocusOut(self):
        if self.isFocused and self.__isMouseDown:
            self.__isWaitingForUnfocus = True
            return
        self.unfocus()

    def browserAction(self, action):
        if self.hasBrowser and self.enableUpdate:
            if action == 'reload' and self.isNavigationComplete:
                self.refresh()
            elif action == 'loading' and not self.isNavigationComplete:
                self.navigateStop()

    def onBrowserShow(self, needRefresh):
        self.enableUpdate = True
        if needRefresh and self.baseUrl != self.url:
            self.navigate(self.url)
        self.focus()

    def onBrowserHide(self):
        self.navigate(self.__baseUrl)
        self.enableUpdate = False
        self.unfocus()

    def addFilter(self, handler):
        if handler in self.__navigationFilters:
            _logger.error('Navigation filter is already added: %r', handler)
        else:
            self.__navigationFilters.add(handler)

    def removeFilter(self, handler):
        if handler in self.__navigationFilters:
            self.__navigationFilters.discard(handler)
        else:
            _logger.error("Trying to delete navigation filter which doesn't exist: %r", handler)

    def filterNavigation(self, url):
        query = urlparse.urlparse(url).query
        tags = urlparse.parse_qs(query).get(_WOT_CLIENT_PARAM_NAME, [])
        stopNavigation = False
        closeBrowser = False
        for handler in self.__navigationFilters:
            try:
                result = handler(url, tags)
                stopNavigation |= result.stopNavigation
                closeBrowser |= result.closeBrowser
                if result.stopNavigation:
                    _logger.debug('Navigation filter triggered navigation stop: %s', handler)
                if result.closeBrowser:
                    _logger.debug('Navigation filter triggered browser close: %s', handler)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        self.__isCloseTriggered = closeBrowser
        return stopNavigation

    def onResourceLoadRequest(self, url):
        result = urlparse.urlparse(url)
        return result.netloc + result.path if result.scheme == _WOT_RESOURCE_CUSTOM_SCHEME else _g_webCache.get(url)

    def setLoadingScreenVisible(self, visible):
        _logger.debug('setLoadingScreenVisible %s', visible)
        self.onLoadingStateChange(visible, True)

    def setAllowAutoLoadingScreen(self, enabled):
        _logger.debug('setAllowAutoLoadingScreen %s', enabled)
        self.__allowAutoLoadingScreenChange = enabled

    def changeTitle(self, title):
        self.onTitleChange(title)

    def __onLoadStart(self, url):
        if url == self.__browser.url:
            self.__isNavigationComplete = False
            self.__loadStartTime = BigWorld.time()
            _logger.debug('onLoadStart %s', self.__browser.url)
            self.onLoadStart(self.__browser.url)
            self.__readyToShow = False
            self.__successfulLoad = False

    def __onLoadEnd(self, url, isLoaded=True, httpStatusCode=None):
        if url == self.__browser.url:
            self.__isNavigationComplete = True
            self.__successfulLoad = isLoaded
            _logger.debug('onLoadEnd %s - %r - %r', self.__browser.url, isLoaded, httpStatusCode)
            self.onLoadEnd(self.__browser.url, isLoaded, httpStatusCode)

    def __onLoadingStateChange(self, isLoading):
        _logger.debug('onLoadingStateChange %r - %r', isLoading, self.__allowAutoLoadingScreenChange)
        self.onLoadingStateChange(isLoading, self.__allowAutoLoadingScreenChange)
        if self.__isCloseTriggered:
            event_dispatcher.hideWebBrowser(self.__browserID)
        elif not isLoading:
            self.onCanCreateNewBrowser()

    def __onReadyToShowContent(self, url):
        if url == self.__browser.url:
            _logger.debug('onReadyToShowContent %s', self.__browser.url)
            self.__readyToShow = True
            self.onReadyToShowContent(self.__browser.url)

    def __isValidTitle(self, title):
        if self.__browser.url.startswith('about:'):
            return False
        if self.__browser.url.endswith(title):
            return False
        if self.__browser.url.endswith('/'):
            secondtest = self.__browser.url[:-1]
            if secondtest.endswith(title):
                return False
        return False if self.__baseUrl == title or self.__baseUrl.endswith(title) else True

    def __setUICursor(self, ui, cursorType):
        if ui and cursorType:
            ui.cursorMgr.setCursorForced(cursorType)

    def __onTitleChange(self, title):
        if self.__isValidTitle(title):
            _logger.debug('onTitleChange %s : %s', title, self.__browser.url)
            self.onTitleChange(title)

    def __onCursorUpdated(self):
        if self.hasBrowser and self.isFocused:
            self.__setUICursor(self.__ui(), self.__browser.script.cursorType)

    def __onReady(self, success):
        self.ready(success)

    def __onJsHostQuery(self, command):
        self.onJsHostQuery(command)

    def executeJavascript(self, script, frame):
        if self.hasBrowser:
            self.__browser.executeJavascript(script, frame)


class EventListener(object):
    cursorType = property(lambda self: self.__cursorType)

    def __init__(self, browser):
        self.__cursorTypes = {CURSOR_TYPES.Hand: Cursor.HAND,
         CURSOR_TYPES.Pointer: Cursor.ARROW,
         CURSOR_TYPES.IBeam: Cursor.IBEAM,
         CURSOR_TYPES.Grab: Cursor.DRAG_OPEN,
         CURSOR_TYPES.Grabbing: Cursor.DRAG_CLOSE,
         CURSOR_TYPES.ColumnResize: Cursor.MOVE}
        self.__cursorType = None
        self.__eventMgr = EventManager()
        self.onLoadStart = Event(self.__eventMgr)
        self.onLoadEnd = Event(self.__eventMgr)
        self.onLoadingStateChange = Event(self.__eventMgr)
        self.onCursorUpdated = Event(self.__eventMgr)
        self.onDOMReady = Event(self.__eventMgr)
        self.onReady = Event(self.__eventMgr)
        self.onJsHostQuery = Event(self.__eventMgr)
        self.onTitleChange = Event(self.__eventMgr)
        self.__urlFailed = False
        self.__browserProxy = weakref.proxy(browser)
        return

    def clear(self):
        self.__eventMgr.clear()

    def newNavigation(self):
        self.__urlFailed = False

    def onChangeCursor(self, cursorType):
        self.__cursorType = self.__cursorTypes.get(cursorType) or Cursor.ARROW
        self.onCursorUpdated()

    def onChangeTitle(self, title):
        _logger.debug('onChangeTitle %s', title)
        self.onTitleChange(title)

    def ready(self, success):
        self.onReady(success)

    def onBeginLoadingFrame(self, frameId, isMainFrame, url):
        if isMainFrame:
            _logger.debug('onBeginLoadingFrame(isMainFrame) %s', url)
            self.onLoadStart(url)
            if self.__urlFailed:
                self.onLoadEnd(url, False)

    def onFailLoadingFrame(self, frameId, isMainFrame, url, errorCode, errorDesc):
        if isMainFrame:
            _logger.debug('onFailLoadingFrame(isMainFrame) %s, %r, %r', url, errorCode, errorDesc)
            self.__urlFailed = True

    def onFinishLoadingFrame(self, frameId, isMainFrame, url, httpStatusCode):
        if isMainFrame:
            _logger.debug('onFinishLoadingFrame(isMainFrame) %s, %r', url, httpStatusCode)
            self.onLoadEnd(url, not self.__urlFailed, httpStatusCode)

    def onBrowserLoadingStateChange(self, isLoading):
        _logger.debug('onBrowserLoadingStateChange() %r', isLoading)
        self.onLoadingStateChange(isLoading)

    def onDocumentReady(self, url):
        _logger.debug('onDocumentReady %s', url)
        self.onDOMReady(url)

    def onAddConsoleMessage(self, message, lineNumber, source):
        pass

    def onFilterNavigation(self, url):
        return self.__browserProxy.filterNavigation(url)

    def onResourceLoadRequest(self, url):
        return self.__browserProxy.onResourceLoadRequest(url)

    def onWhitelistMiss(self, isMainFrame, failedURL):
        _logger.error('Unable to load resource: %s. Main frame: %r', failedURL, isMainFrame)
        if isMainFrame:
            self.onLoadStart(failedURL)
            self.onLoadEnd(failedURL, False)

    def onShowCreatedWebView(self, url, isPopup):
        _logger.debug('onShowCreatedWebView %s %r', url, isPopup)


class WebBrowserManager(object):
    first = property(lambda self: next(iter(self.__browsers)))
    len = property(lambda self: len(self.__browsers))

    def __init__(self):
        self.__browsers = set()

    def addBrowser(self, browser):
        self.__browsers.add(browser)

    def delBrowser(self, browser):
        self.__browsers.discard(browser)

    def handleKeyEvent(self, event):
        for browser in self.__browsers:
            if browser.handleKeyEvent(event):
                return True

        return False


g_mgr = WebBrowserManager()

class FLASH_STRINGS(object):
    BROWSER_DOWN = 'common.browserDown'
    BROWSER_UP = 'common.browserUp'
    BROWSER_MOVE = 'common.browserMove'
    BROWSER_FOCUS_OUT = 'common.browserFocusOut'
    BROWSER_ACTION = 'common.browserAction'
    BROWSER_SHOW = 'common.browserShow'
    BROWSER_HIDE = 'common.browserHide'
    BROWSER_LOAD_START = 'common.browserLoadStart'
    BROWSER_LOAD_END = 'common.browserLoadEnd'


class LL_KEYS(object):
    VK_CANCEL = 3
    VK_HELP = 6
    VK_BACK_SPACE = 8
    VK_TAB = 9
    VK_CLEAR = 12
    VK_RETURN = 13
    VK_ENTER = 14
    VK_SHIFT = 16
    VK_CONTROL = 17
    VK_ALT = 18
    VK_PAUSE = 19
    VK_CAPS_LOCK = 20
    VK_ESCAPE = 27
    VK_SPACE = 32
    VK_PAGE_UP = 33
    VK_PAGE_DOWN = 34
    VK_END = 35
    VK_HOME = 36
    VK_LEFT = 37
    VK_UP = 38
    VK_RIGHT = 39
    VK_DOWN = 40
    VK_PRINTSCREEN = 44
    VK_INSERT = 45
    VK_DELETE = 46


class CURSOR_TYPES(object):
    Pointer = 0
    Cross = 1
    Hand = 2
    IBeam = 3
    Wait = 4
    Help = 5
    EastResize = 6
    NorthResize = 7
    NorthEastResize = 8
    NorthWestResize = 9
    SouthResize = 10
    SouthEastResize = 11
    SouthWestResize = 12
    WestResize = 13
    NorthSouthResize = 14
    EastWestResize = 15
    NorthEastSouthWestResize = 16
    NorthWestSouthEastResize = 17
    ColumnResize = 18
    RowResize = 19
    MiddlePanning = 20
    EastPanning = 21
    NorthPanning = 22
    NorthEastPanning = 23
    NorthWestPanning = 24
    SouthPanning = 25
    SouthEastPanning = 26
    SouthWestPanning = 27
    WestPanning = 28
    Move = 29
    VerticalText = 30
    Cell = 31
    ContextMenu = 32
    Alias = 33
    Progress = 34
    NoDrop = 35
    Copy = 36
    CursorNone = 37
    NotAllowed = 38
    ZoomIn = 39
    ZoomOut = 40
    Grab = 41
    Grabbing = 42
    Custom = 43
