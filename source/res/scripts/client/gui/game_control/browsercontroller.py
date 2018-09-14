# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/BrowserController.py
import Event
from WebBrowser import WebBrowser, LOG_BROWSER
from adisp import async, process
from debug_utils import LOG_WARNING
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import g_appLoader
from gui.game_control.browser_filters import getFilters as _getGlobalFilters
from gui.game_control.gc_constants import BROWSER
from gui.game_control.links import URLMarcos
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LoadViewEvent, BrowserEvent
from gui.shared.utils.functions import getViewName
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import IBrowserController

class BrowserController(IBrowserController):
    _BROWSER_TEXTURE = 'BrowserBg'
    _ALT_BROWSER_TEXTURE = 'AltBrowserBg'

    def __init__(self):
        super(BrowserController, self).__init__()
        self.__browsers = {}
        self.__browsersCallbacks = {}
        self.__browserIDGenerator = SequenceIDGenerator()
        self.__eventMgr = Event.EventManager()
        self.onBrowserAdded = Event.Event(self.__eventMgr)
        self.onBrowserDeleted = Event.Event(self.__eventMgr)
        self.__urlMacros = URLMarcos()
        self.__pendingBrowsers = {}
        self.__creatingBrowserID = None
        self.__filters = _getGlobalFilters()
        return

    def fini(self):
        self.__filters = None
        self.__eventMgr.clear()
        self.__eventMgr = None
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.__browserIDGenerator = None
        super(BrowserController, self).fini()
        return

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def addFilterHandler(self, handler):
        """ Adds given @handler to the browser urls filter chain. Calls
        it if there is a @tag in url onto opened browser page.
        Handler should receive url and list of client-specific tags,
        return bool as flag that routine have to stop
        """
        self.__filters.add(handler)

    def removeFilterHandler(self, handler):
        """ Remove given @handler from filtering chain. Handler description
        can be seen in addFilterhandler method doc-string
        """
        self.__filters.discard(handler)

    @async
    @process
    def load(self, url=None, title=None, showActionBtn=True, showWaiting=True, browserID=None, isAsync=False, browserSize=None, isDefault=True, callback=None, showCloseBtn=False, useBrowserWindow=True):
        url = yield self.__urlMacros.parse(url or GUI_SETTINGS.browser.url)
        suffix = yield self.__urlMacros.parse(GUI_SETTINGS.browser.params)
        concatenator = '&' if '?' in url else '?'
        if suffix not in url:
            url = concatenator.join([url, suffix])
        size = browserSize or BROWSER.SIZE
        webBrowserID = browserID
        if browserID is None:
            browserID = self.__browserIDGenerator.next()
            webBrowserID = browserID
        elif type(browserID) is not int:
            webBrowserID = self.__browserIDGenerator.next()
        ctx = {'url': url,
         'title': title,
         'showActionBtn': showActionBtn,
         'showWaiting': showWaiting,
         'browserID': browserID,
         'size': size,
         'isAsync': isAsync,
         'showCloseBtn': showCloseBtn,
         'showWindow': useBrowserWindow}
        if browserID not in self.__browsers and browserID not in self.__pendingBrowsers:
            texture = self._BROWSER_TEXTURE
            app = g_appLoader.getApp()
            assert app, 'Application can not be None'
            browser = WebBrowser(webBrowserID, app, texture, size, url, handlers=self.__filters)
            self.__browsers[browserID] = browser
            if self.__isCreatingBrowser():
                LOG_BROWSER('CTRL: Queueing a browser creation: ', browserID, url)
                self.__pendingBrowsers[browserID] = ctx
            else:
                self.__createBrowser(ctx)
        elif browserID in self.__pendingBrowsers:
            LOG_BROWSER('CTRL: Re-queuing a browser creation, overriding: ', browserID, url)
            self.__pendingBrowsers[browserID] = ctx
        elif browserID in self.__browsers:
            LOG_BROWSER('CTRL: Re-navigating an existing browser: ', browserID, url)
            self.__browsers[browserID].navigate(url)
        callback(browserID)
        return

    def getBrowser(self, browserID):
        return self.__browsers.get(browserID)

    def delBrowser(self, browserID):
        if browserID in self.__browsers:
            LOG_BROWSER('CTRL: Deleting a browser: ', browserID)
            browser = self.__browsers.pop(browserID)
            self.__clearCallbacks(browserID, browser)
            browser.destroy()
            if self.__creatingBrowserID == browserID:
                self.__creatingBrowserID = None
                self.__tryCreateNextPendingBrowser()
        self.onBrowserDeleted(browserID)
        return

    def __isCreatingBrowser(self):
        return self.__creatingBrowserID is not None

    def __createDone(self, ctx):
        LOG_BROWSER('CTRL: Finished creating a browser: ', self.__creatingBrowserID)
        self.__creatingBrowserID = None
        g_eventBus.handleEvent(BrowserEvent(BrowserEvent.BROWSER_CREATED, ctx=ctx))
        self.__tryCreateNextPendingBrowser()
        return

    def __tryCreateNextPendingBrowser(self):
        if len(self.__pendingBrowsers) > 0:
            nextCtx = self.__pendingBrowsers.popitem()[1]
            self.__createBrowser(nextCtx)

    def __createBrowser(self, ctx):
        browserID = ctx['browserID']
        LOG_BROWSER('CTRL: Creating a browser: ', browserID, ctx['url'])
        self.__creatingBrowserID = browserID
        if not self.__browsers[browserID].create():
            LOG_BROWSER('CTRL: Failed the create step: ', browserID)
            self.delBrowser(browserID)
            self.__createDone(browserID)
            return
        else:
            self.onBrowserAdded(browserID)

            def failedCreationCallback():
                LOG_BROWSER('CTRL: Failed a creation: ', browserID)
                self.__clearCallbacks(browserID, self.__browsers[browserID])
                self.delBrowser(browserID)
                self.__createDone(browserID)

            def successfulCreationCallback(url, isLoaded):
                LOG_BROWSER('CTRL: Successful creation, show window: ', browserID, isLoaded)
                self.__clearCallbacks(browserID, self.__browsers[browserID])
                if isLoaded:
                    self.__showBrowser(browserID, ctx)
                else:
                    LOG_WARNING('Browser request url was not loaded!', url)
                self.__createDone(browserID)

            self.__browsers[browserID].onFailedCreation += failedCreationCallback
            if ctx['isAsync']:
                self.__browsersCallbacks[browserID] = (None, successfulCreationCallback, failedCreationCallback)
                self.__browsers[browserID].onLoadEnd += successfulCreationCallback
            else:
                self.__browsersCallbacks[browserID] = (successfulCreationCallback, None, failedCreationCallback)
                self.__browsers[browserID].onReady += successfulCreationCallback
            return

    def __stop(self):
        while self.__browsers:
            browserID, browser = self.__browsers.popitem()
            self.__clearCallbacks(browserID, browser)
            browser.destroy()

    def __clearCallbacks(self, browserID, browser):
        ready, loadEnd, failed = self.__browsersCallbacks.pop(browserID, (None, None, None))
        if browser is not None:
            if failed is not None:
                browser.onFailedCreation -= failed
            if ready is not None:
                browser.onReady -= ready
            if loadEnd is not None:
                browser.onLoadEnd -= loadEnd
        return

    def __showBrowser(self, browserID, ctx):
        LOG_BROWSER('CTRL: Showing a browser: ', browserID, ctx['url'])
        if ctx.get('showWindow'):
            g_eventBus.handleEvent(LoadViewEvent(VIEW_ALIAS.BROWSER_WINDOW, getViewName(VIEW_ALIAS.BROWSER_WINDOW, browserID), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
