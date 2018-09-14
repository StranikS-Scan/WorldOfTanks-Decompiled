# Embedded file name: scripts/client/gui/game_control/BrowserController.py
import weakref
import Event
from WebBrowser import WebBrowser
from ids_generators import SequenceIDGenerator
from gui import GUI_SETTINGS
from gui.game_control.links import URLMarcos
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from gui.shared.utils.functions import getViewName
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import AppRef

class BrowserController(AppRef):
    BROWSER_SIZE = (990, 550)
    BROWSER_BACKGROUND = 'file:///gui/maps/bg.png'
    _BROWSER_TEXTURE = 'BrowserBg'
    _ALT_BROWSER_TEXTURE = 'AltBrowserBg'

    def __init__(self, proxy):
        super(BrowserController, self).__init__()
        self.__proxy = weakref.proxy(proxy)
        self.__browsers = {}
        self.__browsersCallbacks = {}
        self.__browserIDGenerator = None
        self.__eventMgr = Event.EventManager()
        self.onBrowserAdded = Event.Event(self.__eventMgr)
        self.onBrowserDeleted = Event.Event(self.__eventMgr)
        self.__urlMacros = URLMarcos()
        return

    def init(self):
        pass

    def fini(self):
        self.__eventMgr.clear()
        self.__eventMgr = None
        self.__urlMacros.clear()
        self.__urlMacros = None
        return

    def start(self):
        self.__browserIDGenerator = SequenceIDGenerator()

    def stop(self):
        self.__browserIDGenerator = None
        while self.__browsers:
            browserID, browser = self.__browsers.popitem()
            callback = self.__browsersCallbacks.pop(browserID, None)
            if callback is not None:
                browser.onLoadEnd -= callback
            browser.destroy()

        return

    def load(self, url = None, title = None, showActionBtn = True, showWaiting = True, browserID = None, isAsync = False, browserSize = None, background = None, isDefault = True):
        url = url or GUI_SETTINGS.browser.url
        suffix = self.__urlMacros.parse(GUI_SETTINGS.browser.params)
        concatenator = '&' if '?' in url else '?'
        if suffix not in url:
            url = concatenator.join([url, suffix])
        size = browserSize or self.BROWSER_SIZE
        background = background or self.BROWSER_BACKGROUND
        if browserID not in self.__browsers:
            browserID = self.__browserIDGenerator.next()
            texture = self._BROWSER_TEXTURE if isDefault else self._ALT_BROWSER_TEXTURE
            self.__browsers[browserID] = WebBrowser(browserID, self.app, texture, size, url, backgroundUrl=background)
            self.onBrowserAdded(browserID)
        ctx = {'url': url,
         'title': title,
         'showActionBtn': showActionBtn,
         'showWaiting': showWaiting,
         'browserID': browserID,
         'size': size,
         'isDefault': isDefault}
        if isAsync:

            def callback(*args):
                self.__clearCallback(browserID)
                self.__showBrowser(browserID, ctx)

            self.__browsersCallbacks[browserID] = callback
            self.__browsers[browserID].onLoadEnd += callback
        else:
            self.__showBrowser(browserID, ctx)
        return browserID

    def getBrowser(self, browserID):
        return self.__browsers.get(browserID)

    def delBrowser(self, browserID):
        if browserID in self.__browsers:
            browser = self.__browsers.pop(browserID)
            callback = self.__browsersCallbacks.pop(browserID, None)
            if callback is not None:
                browser.onLoadEnd -= callback
            browser.destroy()
        self.onBrowserDeleted(browserID)
        return

    def __stop(self):
        while self.__browsers:
            browserID, browser = self.__browsers.popitem()
            callback = self.__browsersCallbacks.pop(browserID, None)
            if callback is not None:
                browser.onLoadEnd -= callback
            browser.destroy()

        return

    def __clearCallback(self, browserID):
        if browserID in self.__browsersCallbacks:
            callback = self.__browsersCallbacks.pop(browserID)
            self.__browsers[browserID].onLoadEnd -= callback

    def __showBrowser(self, browserID, ctx):
        self.app.fireEvent(LoadViewEvent(VIEW_ALIAS.BROWSER_WINDOW, getViewName(VIEW_ALIAS.BROWSER_WINDOW, browserID), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
