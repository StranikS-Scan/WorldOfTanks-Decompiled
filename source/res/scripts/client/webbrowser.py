# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/WebBrowser.py
import weakref
import urlparse
import functools
import logging
from enum import Enum
import BigWorld
import Keys
import SoundGroups
import Settings
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.shared import event_dispatcher
from Event import Event, EventManager
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from web.cache.web_cache import WebExternalCache
_logger = logging.getLogger(__name__)
_webAppLogger = logging.getLogger('{} (webapp)'.format(__name__))
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


class LogSeverity(Enum):
    disable = 0
    verbose = 1
    info = 2
    warning = 3
    error = 4


_LOG_SEVERITY_TO_LOG_LEVEL_MAP = {LogSeverity.disable: logging.NOTSET,
 LogSeverity.verbose: logging.DEBUG,
 LogSeverity.info: logging.INFO,
 LogSeverity.warning: logging.WARNING,
 LogSeverity.error: logging.ERROR}

class WebBrowser(object):
    hasBrowser = property(lambda self: self.__browser is not None)
    initializationUrl = property(lambda self: self.__baseUrl)
    baseUrl = property(lambda self: '' if self.__browser is None else self.__baseUrl)
    url = property(lambda self: '' if self.__browser is None else self.__browser.url)
    width = property(lambda self: 0 if self.__browser is None else self.__browser.width)
    height = property(lambda self: 0 if self.__browser is None else self.__browser.height)
    isNavigationComplete = property(lambda self: self.__isNavigationComplete)
    isFocused = property(lambda self: self.__isFocused)
    isAudioPlaying = property(lambda self: self.__isAudioPlaying)
    textureUrl = property(lambda self: self.__textureUrl)
    updateInterval = 0.01
    isSuccessfulLoad = property(lambda self: self.__successfulLoad)
    skipEscape = property(lambda self: self.__skipEscape)
    ignoreKeyEvents = property(lambda self: self.__ignoreKeyEvents)
    ignoreAltKey = property(lambda self: self.__ignoreAltKey)
    ignoreCtrlClick = property(lambda self: self.__ignoreCtrlClick)
    ignoreShiftClick = property(lambda self: self.__ignoreShiftClick)
    useSpecialKeys = property(lambda self: self.__useSpecialKeys)
    allowMiddleClick = property(lambda self: self.__allowMiddleClick)
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

    @ignoreCtrlClick.setter
    def ignoreCtrlClick(self, value):
        _logger.debug('ignoreCtrlClick set %s (was: %s)', value, self.__ignoreCtrlClick)
        self.__ignoreCtrlClick = value

    @ignoreShiftClick.setter
    def ignoreShiftClick(self, value):
        _logger.debug('ignoreShiftClick set %s (was: %s)', value, self.__ignoreShiftClick)
        self.__ignoreShiftClick = value

    @useSpecialKeys.setter
    def useSpecialKeys(self, value):
        _logger.debug('useSpecialKeys set %s (was: %s)', value, self.__useSpecialKeys)
        self.__useSpecialKeys = value

    @allowMiddleClick.setter
    def allowMiddleClick(self, value):
        _logger.debug('allowMiddleClick set %s (was: %s)', value, self.__allowMiddleClick)
        self.__allowMiddleClick = value

    @allowRightClick.setter
    def allowRightClick(self, value):
        _logger.debug('allowRightClick set %s (was: %s)', value, self.__allowRightClick)
        self.__allowRightClick = value

    @allowMouseWheel.setter
    def allowMouseWheel(self, value):
        _logger.debug('allowMouseWheel set %s (was: %s)', value, self.__allowMouseWheel)
        self.__allowMouseWheel = value

    def __init__(self, browserID, uiObj, size, url='about:blank', isFocused=False, handlers=None):
        self.__browserID = browserID
        self.__cbID = None
        self.__baseUrl = url
        self.__uiObj = uiObj
        self.__browserSize = size + (1.0,)
        self.__startFocused = isFocused
        self.__browser = None
        self.__isNavigationComplete = False
        self.__loadStartTime = None
        self.__isFocused = False
        self.__isAudioPlaying = False
        self.__navigationFilters = handlers or set()
        self.__skipEscape = True
        self.__ignoreKeyEvents = False
        self.__ignoreAltKey = False
        self.__ignoreCtrlClick = True
        self.__ignoreShiftClick = True
        self.__useSpecialKeys = True
        self.__allowMiddleClick = False
        self.__allowRightClick = False
        self.__allowMouseWheel = True
        self.__allowAutoLoadingScreenChange = True
        self.__isCloseTriggered = False
        self.__isAudioMutable = False
        self.__ctrlDown = False
        self.__shiftDown = False
        self.__textureUrl = ''
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
        self.onAudioStatusChanged = Event(self.__eventMgr)
        _logger.info('INIT %s size %s, id: %s', self.__baseUrl, size, self.__browserID)
        levelSetting = Settings.g_instance.engineConfig['webBrowser']['logVerbosity'].asString
        levelSettingEnum = LogSeverity[levelSetting]
        _webAppLogger.setLevel(_LOG_SEVERITY_TO_LOG_LEVEL_MAP[levelSettingEnum])
        return

    def create(self):
        _logger.info('CREATE %s id: %s', self.__baseUrl, self.__browserID)
        self.__browser = BigWorld.createWebView(self.__browserID)
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
            self.__browser.script.onDestroy += self.__onDestroy
            self.__browser.script.onAudioStatusChanged += self.__onAudioStatusChanged
            self.__browser.script.onConsoleMessage += self.__onConsoleMessage
            self.__browser.script.isBrowserPlayingAudio = False

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
        _logger.info('READY success: %r %s id: %s', success, self.__baseUrl, self.__browserID)
        self.__ui = weakref.ref(self.__uiObj)
        self.__readyToShow = False
        self.__successfulLoad = False
        self.enableUpdate = True
        self.__isMouseDown = False
        self.__isFocused = False
        self.__isWaitingForUnfocus = False
        if success:
            browserSize = self.__browserSize
            self.__textureUrl = self.__browser.setScaleformRender(str(self.__browserID), browserSize[0], browserSize[1], browserSize[2])
            _logger.info('READY scaleform texture url: %s', self.__textureUrl)
            self.__browser.activate(True)
            self.__browser.focus()
            self.__browser.loadURL(self.__baseUrl)
            if self.__startFocused:
                self.focus()
            g_mgr.addBrowser(self)
            self.onReady(self.__browser.url, success)
            self.onCanCreateNewBrowser()
        else:
            self.__isNavigationComplete = True
            _logger.error(' FAILED %s id: %s', self.__baseUrl, self.__browserID)
            self.onFailedCreation(self.__baseUrl)

    def invalidateView(self):
        if self.hasBrowser:
            self.__browser.invalidate()

    def updateSize(self, size):
        self.__browserSize = size
        if self.hasBrowser:
            self.__browser.resize(size[0], size[1], size[2])

    def destroy(self):
        if self.__eventMgr is not None:
            self.__eventMgr.clear()
            self.__eventMgr = None
        if self.__browser is not None:
            _logger.info('DESTROYED %s id: %s', self.__baseUrl, self.__browserID)
            self.__onAudioStatusChanged(isPlaying=False)
            self.__browser.script.clear()
            self.__browser.script = None
            self.__browser.resetScaleformRender()
            BigWorld.destroyWebView(self.__browserID)
            self.__browser = None
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        self.__ui = None
        self.__navigationFilters = None
        self.__setUICursor(self.__uiObj, CursorManager.ARROW)
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
        if self.__loadStartTime is None or BigWorld.time() - self.__loadStartTime < 0.5:
            _logger.debug('refresh - called too soon')
            return
        else:
            if self.hasBrowser:
                self.__browser.reload()
                self.onNavigate(self.__browser.url)
            return

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

    def sendEvent(self, webEvent):
        if self.hasBrowser:
            self.__browser.sendEvent(webEvent)

    def navigateBack(self):
        if self.hasBrowser:
            self.__browser.goBack(self.url)

    def navigateForward(self):
        if self.hasBrowser:
            self.__browser.goForward(self.url)

    def navigateStop(self):
        if self.__loadStartTime is None or BigWorld.time() - self.__loadStartTime < 0.5:
            _logger.debug('navigateStop - called too soon')
            return
        else:
            if self.hasBrowser:
                self.__browser.stop()
                self.__onLoadEnd(self.__browser.url)
            return

    def __getBrowserKeyHandler(self, key, isKeyDown, isAltDown, isShiftDown, isCtrlDown):
        from itertools import izip
        params = (key,
         isKeyDown,
         isAltDown,
         isShiftDown,
         isCtrlDown)

        def matches(t):
            return t[0] is None or t[0] == t[1]

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
        toolTipMgr = self.__uiObj.getToolTipMgr()
        if toolTipMgr and toolTipMgr.isReadyToHandleKey(event):
            return False
        if e.key in (Keys.KEY_LCONTROL, Keys.KEY_RCONTROL):
            self.__ctrlDown = e.isKeyDown()
        if self.__ignoreCtrlClick and self.__ctrlDown and e.key == Keys.KEY_LEFTMOUSE:
            return False
        if e.key in (Keys.KEY_LSHIFT, Keys.KEY_RSHIFT):
            self.__shiftDown = e.isKeyDown()
        if self.__ignoreShiftClick and self.__shiftDown and e.key == Keys.KEY_LEFTMOUSE:
            return False
        if self.__ignoreAltKey and e.key in (Keys.KEY_LALT, Keys.KEY_RALT):
            return False
        if not (self.hasBrowser and self.enableUpdate):
            return False
        if not self.allowMiddleClick and e.key == Keys.KEY_MIDDLEMOUSE:
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
        if self.ignoreKeyEvents and e.key not in (Keys.KEY_LEFTMOUSE, Keys.KEY_RIGHTMOUSE, Keys.KEY_MIDDLEMOUSE):
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

    def setAllowAutoLoadingScreen(self, enabled):
        _logger.debug('setAllowAutoLoadingScreen %s', enabled)
        self.__allowAutoLoadingScreenChange = enabled

    def setIsAudioMutable(self, isAudioMutable):
        self.__isAudioMutable = isAudioMutable

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

    def __onLoadEnd(self, url, isLoaded=True, httpStatusCode=None, errorDesc=None):
        if url == self.__browser.url or errorDesc:
            self.__isNavigationComplete = True
            self.__successfulLoad = isLoaded
            if not isLoaded or httpStatusCode and httpStatusCode >= 400 or errorDesc:
                _logger.error('FAILED Url: %s, Http code: %r, Browser error: %s', self.__browser.url, httpStatusCode, errorDesc)
            self.onLoadEnd(self.__browser.url, isLoaded, httpStatusCode)

    def __onLoadingStateChange(self, isLoading):
        _logger.debug('onLoadingStateChange %r %r', isLoading, self.__allowAutoLoadingScreenChange)
        self.onLoadingStateChange(isLoading, self.__allowAutoLoadingScreenChange)
        if self.__isCloseTriggered:
            event_dispatcher.hideWebBrowser(self.__browserID)

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
        if self.__baseUrl == title or self.__baseUrl.endswith(title):
            return False
        return False if title.startswith('http://') or title.startswith('https://') else True

    def __setUICursor(self, ui, cursorType):
        if ui and cursorType:
            ui.cursorMgr.setCursorForced(cursorType)

    def __onTitleChange(self, title):
        if self.__isValidTitle(title):
            _logger.debug('onTitleChange title: %s %s', title, self.__browser.url)
            self.onTitleChange(title)

    def __onCursorUpdated(self):
        if self.hasBrowser and self.isFocused:
            self.__setUICursor(self.__ui(), self.__browser.script.cursorType)

    def __onReady(self, success):
        self.ready(success)

    def __onDestroy(self):
        _logger.info('Destroy Web View %s - %r', self.__baseUrl, self.__browserID)
        self.destroy()

    def __onJsHostQuery(self, command):
        self.onJsHostQuery(command)

    def __onConsoleMessage(self, level, message, lineNumber, source, viewId):
        try:
            levelEnum = [ l for l in LogSeverity if l.value == level ][0]
        except IndexError:
            levelEnum = LogSeverity.disable

        if levelEnum != LogSeverity.disable:
            _webAppLogger.log(_LOG_SEVERITY_TO_LOG_LEVEL_MAP[levelEnum], '%s, line %s, viewId %s: %s', source, lineNumber, viewId, message)

    def __onAudioStatusChanged(self, isPlaying):
        if self.__isAudioMutable:
            self.__isAudioPlaying = bool(isPlaying)
            g_mgr.updateGameAudio()

    def executeJavascript(self, script, frame):
        if self.hasBrowser:
            self.__browser.executeJavascript(script, frame)


class EventListener(object):
    cursorType = property(lambda self: self.__cursorType)
    isBrowserPlayingAudio = False

    def __init__(self, browser):
        self.__cursorTypes = {CURSOR_TYPES.Hand: CursorManager.HAND,
         CURSOR_TYPES.Pointer: CursorManager.ARROW,
         CURSOR_TYPES.IBeam: CursorManager.IBEAM,
         CURSOR_TYPES.Grab: CursorManager.DRAG_OPEN,
         CURSOR_TYPES.Grabbing: CursorManager.DRAG_CLOSE,
         CURSOR_TYPES.ColumnResize: CursorManager.MOVE}
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
        self.onDestroy = Event(self.__eventMgr)
        self.onAudioStatusChanged = Event(self.__eventMgr)
        self.onConsoleMessage = Event(self.__eventMgr)
        self.__urlFailed = False
        self.__browserProxy = weakref.proxy(browser)
        return

    def clear(self):
        self.__eventMgr.clear()

    def newNavigation(self):
        self.__urlFailed = False

    def onChangeCursor(self, cursorType):
        self.__cursorType = self.__cursorTypes.get(cursorType) or CursorManager.ARROW
        self.onCursorUpdated()

    def onChangeTitle(self, title):
        _logger.debug('onChangeTitle %s', title)
        self.onTitleChange(title)

    def ready(self, success):
        self.onReady(success)

    def destroy(self):
        self.onDestroy()

    def onBeginLoadingFrame(self, frameId, isMainFrame, url):
        if isMainFrame:
            _logger.debug('onBeginLoadingFrame(isMainFrame) %s', url)
            self.onLoadStart(url)
            if self.__urlFailed:
                self.onLoadEnd(url, False)

    def onFailLoadingFrame(self, frameId, isMainFrame, url, errorCode, errorDesc):
        if isMainFrame:
            _logger.debug('onFailLoadingFrame(isMainFrame) %s, error: %r, text: %r', url, errorCode, errorDesc)
            self.__urlFailed = True
            self.onLoadEnd(url, not self.__urlFailed, errorDesc=errorDesc)

    def onFinishLoadingFrame(self, frameId, isMainFrame, url, httpStatusCode):
        if isMainFrame:
            _logger.debug('onFinishLoadingFrame(isMainFrame) %s, httpStatusCode: %r', url, httpStatusCode)
            self.onLoadEnd(url, not self.__urlFailed, httpStatusCode)

    def onBrowserLoadingStateChange(self, isLoading):
        _logger.debug('onBrowserLoadingStateChange isLoading: %r', isLoading)
        self.onLoadingStateChange(isLoading)

    def onDocumentReady(self, url):
        _logger.debug('onDocumentReady %s', url)
        self.onDOMReady(url)

    def onAddConsoleMessage(self, level, message, lineNumber, source, viewId):
        self.onConsoleMessage(level, message, lineNumber, source, viewId)

    def onFilterNavigation(self, url):
        return self.__browserProxy.filterNavigation(url)

    def onResourceLoadRequest(self, method, url):
        _logger.debug('requested %s %s', method, url)
        return self.__browserProxy.onResourceLoadRequest(url)

    def onResourceLoadComplete(self, method, url):
        _logger.debug('completed %s %s', method, url)

    def onResourceLoadError(self, method, url):
        _logger.warn('failed %s %s', method, url)

    def onWhitelistMiss(self, isMainFrame, failedURL, httpStatusCode=None):
        if isMainFrame:
            self.onLoadStart(failedURL)
            self.onLoadEnd(failedURL, False, httpStatusCode)

    def onShowCreatedWebView(self, url, isPopup):
        _logger.debug('onShowCreatedWebView %s isPopup: %r', url, isPopup)


class WebBrowserManager(object):
    first = property(lambda self: next(iter(self.__browsers)))
    len = property(lambda self: len(self.__browsers))
    isBackgroundAudioMuted = False

    def __init__(self):
        self.__browsers = set()

    def addBrowser(self, browser):
        self.__browsers.add(browser)

    def delBrowser(self, browser):
        self.__browsers.discard(browser)

    def getBrowserPlayingAudioCount(self):
        count = 0
        for browser in self.__browsers:
            if browser.isAudioPlaying:
                count += 1

        return count

    def updateGameAudio(self):
        openedBrowsersPresented = g_mgr.getBrowserPlayingAudioCount() > 0
        self.__muteBackgroundAudio(isMute=openedBrowsersPresented)

    def handleKeyEvent(self, event):
        for browser in self.__browsers:
            if browser.handleKeyEvent(event):
                return True

        return False

    def __muteBackgroundAudio(self, isMute):
        if self.isBackgroundAudioMuted != isMute:
            SoundGroups.g_instance.playSound2D('ue_master_mute' if isMute else 'ue_master_unmute')
            self.isBackgroundAudioMuted = isMute


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
