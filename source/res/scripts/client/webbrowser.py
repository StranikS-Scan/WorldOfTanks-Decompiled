# Embedded file name: scripts/client/WebBrowser.py
import BigWorld
import Keys
from gui.Scaleform.CursorDelegator import CursorDelegator
from Event import Event
from debug_utils import *
from gui.Scaleform.framework import AppRef
from debug_utils import _doLog
_BROWSER_LOGGING = True

def LOG_BROWSER(msg, *kargs):
    if _BROWSER_LOGGING and IS_DEVELOPMENT:
        _doLog('BROWSER', msg, kargs)


class WebBrowser(AppRef):
    hasBrowser = property(lambda self: self.__browser is not None)
    baseUrl = property(lambda self: ('' if self.__browser is None else self.__baseUrl))
    url = property(lambda self: ('' if self.__browser is None else self.__browser.url))
    width = property(lambda self: (0 if self.__browser is None else self.__browser.width))
    height = property(lambda self: (0 if self.__browser is None else self.__browser.height))
    isNavigationComplete = property(lambda self: self.__isNavigationComplete)
    isFocused = property(lambda self: self.__isFocused)
    updateInterval = 0.01

    def __init__(self, browserID, uiObj, texName, size, url = 'about:blank', isFocused = False, backgroundUrl = 'file:///gui/maps/bg.png'):
        self.__browserID = browserID
        self.__cbID = None
        self.__baseUrl = url
        self.__backgroundUrl = backgroundUrl
        self.onLoadStart = Event()
        self.onLoadEnd = Event()
        self.onNavigate = Event()
        LOG_BROWSER('__init__', self.__baseUrl, texName, size)
        self.__browser = uiObj.movie.createBrowser(texName, backgroundUrl, size[0], size[1])
        if self.__browser is None:
            return
        else:
            self.__keysDown = set()

            def injectBrowserKeyEvent(me, e):
                LOG_BROWSER('injectBrowserKeyEvent', (e.key,
                 e.isKeyDown(),
                 e.isAltDown(),
                 e.isShiftDown(),
                 e.isCtrlDown()))
                me.__browser.injectKeyEvent(e)

            def injectKeyDown(me, e):
                if e.key not in me.__keysDown:
                    me.__keysDown.add(e.key)
                    injectBrowserKeyEvent(me, e)

            def injectKeyUp(me, e):
                if e.key in me.__keysDown:
                    me.__keysDown.remove(e.key)
                    injectBrowserKeyEvent(me, e)

            def resetBit(value, bitMask):
                return value & ~bitMask

            self.__browserKeyHandlers = ((Keys.KEY_LEFTARROW,
              True,
              True,
              None,
              None,
              lambda me, _: me.__browser.goBack()),
             (Keys.KEY_RIGHTARROW,
              True,
              True,
              None,
              None,
              lambda me, _: me.__browser.goForward()),
             (Keys.KEY_F5,
              True,
              None,
              None,
              None,
              lambda me, _: me.__browser.reload(False)),
             (Keys.KEY_LSHIFT,
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
              lambda me, e: injectKeyDown(me, e)),
             (None,
              False,
              None,
              None,
              None,
              lambda me, e: injectKeyUp(me, e)))
            self.__browser.script = EventListener()
            self.__browser.script.onLoadStart += self.__onLoadStart
            self.__browser.script.onLoadEnd += self.__onLoadEnd
            self.__browser.script.onCursorUpdated += self.__onCursorUpdated
            self.enableUpdate = True
            self.__isMouseDown = False
            self.__isNavigationComplete = False
            self.__delayedUrls = []
            self.__isFocused = False
            self.__isWaitingForUnfocus = False
            if isFocused:
                self.focus()
            g_mgr.addBrowser(self)
            self.update()
            self.navigate(url)
            return

    def __processDelayedNavigation(self):
        if self.__isNavigationComplete and self.__delayedUrls:
            self.doNavigate(self.__delayedUrls.pop(0))
            return True
        return False

    def destroy(self):
        if self.__browser is not None:
            self.__browser.script.onLoadStart -= self.__onLoadStart
            self.__browser.script.onLoadEnd -= self.__onLoadEnd
            self.__browser.script.onCursorUpdated -= self.__onCursorUpdated
            self.__browser.script = None
            self.__browser = None
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        g_mgr.delBrowser(self)
        return

    def focus(self):
        if self.hasBrowser and not self.isFocused:
            self.__browser.focus()
            self.__isFocused = True
            self.app.cursorMgr.setCursorForced(self.__browser.script.cursorType)

    def unfocus(self):
        if self.hasBrowser and self.isFocused:
            self.__browser.unfocus()
            self.__isFocused = False
            self.__isWaitingForUnfocus = False
            self.app.cursorMgr.setCursorForced(None)
        return

    def refresh(self, ignoreCache = True):
        if self.hasBrowser:
            self.__browser.reload(ignoreCache)
            self.onNavigate(self.__browser.url)

    def navigate(self, url):
        self.__delayedUrls.append(url)
        self.__processDelayedNavigation()

    def doNavigate(self, url):
        LOG_BROWSER('doNavigate', url)
        if self.hasBrowser:
            self.__browser.loadURL(url)
            self.onNavigate(url)

    def navigateBack(self):
        if self.hasBrowser:
            self.__browser.goBack(self.url)

    def navigateForward(self):
        if self.hasBrowser:
            self.__browser.goForward(self.url)

    def navigateStop(self):
        if self.hasBrowser:
            self.__browser.stop()
            self.__onLoadEnd()

    def update(self):
        self.__cbID = BigWorld.callback(self.updateInterval, self.update)
        if self.hasBrowser and self.enableUpdate:
            try:
                self.__browser.updateTexture()
            except:
                LOG_CURRENT_EXCEPTION()

    def __getBrowserKeyHandler(self, key, isKeyDown, isAltDown, isShiftDown, isCtrlDown):
        from itertools import izip
        params = (key,
         isKeyDown,
         isAltDown,
         isShiftDown,
         isCtrlDown)
        matches = lambda t: t[0] is None or t[0] == t[1]
        for values in self.__browserKeyHandlers:
            if reduce(lambda a, b: a and matches(b), izip(values, params), True):
                return values[-1]

        return None

    def handleKeyEvent(self, event):
        if not (self.hasBrowser and self.isFocused and self.enableUpdate):
            return False
        if event.key == Keys.KEY_LEFTMOUSE:
            if not event.isKeyDown():
                self.browserUp(0, 0, 0)
            return False
        if event.key == Keys.KEY_ESCAPE:
            return False
        if event.key == Keys.KEY_RETURN and event.isAltDown():
            return False
        e = event
        self.__getBrowserKeyHandler(e.key, e.isKeyDown(), e.isAltDown(), e.isShiftDown(), e.isCtrlDown())(self, event)
        return True

    def browserMove(self, x, y, z):
        if not (self.hasBrowser and self.enableUpdate and self.isFocused):
            return
        if z != 0:
            self.__browser.injectMouseWheelEvent(z * 20)
        self.__browser.injectMouseMoveEvent(x, y)

    def browserDown(self, x, y, z):
        if not (self.hasBrowser and self.enableUpdate):
            return
        elif self.__isMouseDown:
            return
        else:
            if not self.isFocused:
                self.focus()
                self.__isMouseDown = True
                self.browserUp(x, y, z)
                self.browserMove(x, y, z)
            self.__isMouseDown = True
            self.__browser.injectKeyEvent(BigWorld.KeyEvent(Keys.KEY_LEFTMOUSE, 0, 0, None, (x, y)))
            return

    def browserUp(self, x, y, z):
        if not (self.hasBrowser and self.enableUpdate):
            return
        elif not self.__isMouseDown:
            return
        else:
            self.__isMouseDown = False
            self.__browser.injectKeyEvent(BigWorld.KeyEvent(Keys.KEY_LEFTMOUSE, -1, 0, None, (x, y)))
            if self.__isWaitingForUnfocus:
                self.unfocus()
            return

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

    def __onLoadStart(self):
        self.__isNavigationComplete = False
        if self.__browser.url != self.__backgroundUrl:
            LOG_BROWSER('onLoadStart', self.__browser.url)
            self.onLoadStart(self.__browser.url)

    def __onLoadEnd(self, isLoaded = True):
        self.__isNavigationComplete = True
        if not self.__processDelayedNavigation():
            if self.__browser.url == self.__backgroundUrl:
                LOG_BROWSER('onLoadEnd: prevent navigating to baseurl')
                self.__browser.goForward()
            else:
                LOG_BROWSER('onLoadEnd', self.__browser.url)
                self.onLoadEnd(self.__browser.url, isLoaded)

    def __onCursorUpdated(self):
        if self.hasBrowser and self.isFocused:
            self.app.cursorMgr.setCursorForced(self.__browser.script.cursorType)

    def executeJavascript(self, script, frame):
        if self.hasBrowser:
            self.__browser.executeJavascript(script, frame)


class EventListener():
    cursorType = property(lambda self: self.__cursorType)

    def __init__(self):
        self.__cursorTypes = {CURSOR_TYPES.Hand: CursorDelegator.HAND,
         CURSOR_TYPES.Pointer: CursorDelegator.ARROW,
         CURSOR_TYPES.IBeam: CursorDelegator.IBEAM,
         CURSOR_TYPES.Wait: CursorDelegator.WAITING,
         CURSOR_TYPES.Grab: CursorDelegator.DRAG_OPEN,
         CURSOR_TYPES.Grabbing: CursorDelegator.DRAG_CLOSE,
         CURSOR_TYPES.ColumnResize: CursorDelegator.HAND_RIGHT_LEFT}
        self.__cursorType = None
        self.onLoadStart = Event()
        self.onLoadEnd = Event()
        self.onCursorUpdated = Event()
        self.onDOMReady = Event()
        return

    def onChangeCursor(self, cursorType):
        self.__cursorType = self.__cursorTypes.get(cursorType) or CursorDelegator.ARROW
        self.onCursorUpdated()

    def onBeginLoadingFrame(self, frameId, isMainFrame, url):
        if isMainFrame:
            LOG_BROWSER('onBeginLoadingFrame(isMainFrame)', url)
            self.onLoadStart()

    def onFailLoadingFrame(self, frameId, isMainFrame, errorCode, url):
        if isMainFrame:
            LOG_BROWSER('onFailLoadingFrame(isMainFrame)', url)
            self.onLoadEnd(False)

    def onFinishLoadingFrame(self, frameId, isMainFrame, url):
        if isMainFrame:
            LOG_BROWSER('onFinishLoadingFrame(isMainFrame)', url)
            self.onLoadEnd()

    def onDocumentReady(self, url):
        LOG_BROWSER('onDocumentReady', url)
        self.onDOMReady()

    def onAddConsoleMessage(self, message, lineNumber, source):
        pass


class WebBrowserManager():
    first = property(lambda self: next(iter(self.__browsers)))

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

class FLASH_STRINGS():
    BROWSER_DOWN = 'common.browserDown'
    BROWSER_UP = 'common.browserUp'
    BROWSER_MOVE = 'common.browserMove'
    BROWSER_FOCUS_OUT = 'common.browserFocusOut'
    BROWSER_ACTION = 'common.browserAction'
    BROWSER_SHOW = 'common.browserShow'
    BROWSER_HIDE = 'common.browserHide'
    BROWSER_LOAD_START = 'common.browserLoadStart'
    BROWSER_LOAD_END = 'common.browserLoadEnd'


class LL_KEYS():
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


class CURSOR_TYPES():
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
