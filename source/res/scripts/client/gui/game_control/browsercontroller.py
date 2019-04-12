# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/BrowserController.py
import logging
import BigWorld
import Event
from WebBrowser import WebBrowser
from adisp import async, process
from gui import GUI_SETTINGS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.browser_filters import getFilters as _getGlobalFilters
from gui.game_control.gc_constants import BROWSER
from gui.game_control.links import URLMacros
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import LoadViewEvent, BrowserEvent
from gui.shared.utils.functions import getViewName
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBrowserController
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class BrowserController(IBrowserController):
    _BROWSER_TEXTURE = 'BrowserBg'
    _ALT_BROWSER_TEXTURE = 'AltBrowserBg'

    def __init__(self):
        super(BrowserController, self).__init__()
        self.__browsers = {}
        self.__browsersCallbacks = {}
        self.__browserCreationCallbacks = {}
        self.__browserIDGenerator = SequenceIDGenerator()
        self.__eventMgr = Event.EventManager()
        self.onBrowserAdded = Event.Event(self.__eventMgr)
        self.onBrowserDeleted = Event.Event(self.__eventMgr)
        self.__urlMacros = URLMacros()
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
        self.__browsersCallbacks.clear()
        self.__browsersCallbacks = None
        self.__browsers.clear()
        self.__browsers = None
        self.__pendingBrowsers.clear()
        self.__pendingBrowsers = None
        self.__browserIDGenerator = None
        super(BrowserController, self).fini()
        return

    def onAvatarBecomePlayer(self):
        self.__stop()
        BigWorld.destroyBrowser()

    def onDisconnected(self):
        self.__stop()
        BigWorld.destroyBrowser()

    def onLobbyStarted(self, ctx):
        BigWorld.createBrowser()

    def addFilterHandler(self, handler):
        self.__filters.add(handler)

    def removeFilterHandler(self, handler):
        self.__filters.discard(handler)

    @async
    @process
    def load(self, url=None, title=None, showActionBtn=True, showWaiting=True, browserID=None, isAsync=False, browserSize=None, isDefault=True, callback=None, showCloseBtn=False, useBrowserWindow=True, isModal=False, showCreateWaiting=False, handlers=None, showBrowserCallback=None, isSolidBorder=False):
        if showCreateWaiting:
            Waiting.show('browser/init')
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
         'showWindow': useBrowserWindow,
         'alias': VIEW_ALIAS.BROWSER_WINDOW_MODAL if isModal else VIEW_ALIAS.BROWSER_WINDOW,
         'showCreateWaiting': showCreateWaiting,
         'handlers': handlers,
         'showBrowserCallback': showBrowserCallback,
         'isSolidBorder': isSolidBorder}
        if browserID not in self.__browsers and browserID not in self.__pendingBrowsers:
            texture = self._BROWSER_TEXTURE
            appLoader = dependency.instance(IAppLoader)
            app = appLoader.getApp()
            if app is None:
                raise SoftException('Application can not be None')
            browser = WebBrowser(webBrowserID, app, texture, size, url, handlers=self.__filters)
            self.__browsers[browserID] = browser
            if self.__isCreatingBrowser():
                _logger.debug('CTRL: Queueing a browser creation: %r - %s', browserID, url)
                self.__pendingBrowsers[browserID] = ctx
            else:
                self.__createBrowser(ctx)
        elif browserID in self.__pendingBrowsers:
            _logger.debug('CTRL: Re-queuing a browser creation, overriding: %r - %s', browserID, url)
            self.__pendingBrowsers[browserID] = ctx
        elif browserID in self.__browsers:
            _logger.debug('CTRL: Re-navigating an existing browser: %r - %s', browserID, url)
            browser = self.__browsers[browserID]
            browser.navigate(url)
            browser.changeTitle(title)
        callback(browserID)
        return

    def getAllBrowsers(self):
        return self.__browsers

    def getBrowser(self, browserID):
        return self.__browsers.get(browserID)

    def delBrowser(self, browserID):
        if browserID in self.__browsers:
            _logger.debug('CTRL: Deleting a browser: %s', browserID)
            browser = self.__browsers.pop(browserID)
            self.__clearCallbacks(browserID, browser, True)
            browser.destroy()
            if self.__creatingBrowserID == browserID:
                self.__creatingBrowserID = None
                self.__tryCreateNextPendingBrowser()
            if browserID in self.__pendingBrowsers:
                del self.__pendingBrowsers[browserID]
        self.onBrowserDeleted(browserID)
        return

    def __isCreatingBrowser(self):
        return self.__creatingBrowserID is not None

    def __createDone(self, ctx):
        _logger.debug('CTRL: Finished creating a browser: %s', self.__creatingBrowserID)
        if ctx['showCreateWaiting']:
            Waiting.hide('browser/init')

    def __tryCreateNextPendingBrowser(self):
        self.__creatingBrowserID = None
        if self.__pendingBrowsers:
            nextCtx = self.__pendingBrowsers.popitem()[1]
            self.__createBrowser(nextCtx)
        return

    def __createBrowser(self, ctx):
        browserID = ctx['browserID']
        _logger.debug('CTRL: Creating a browser: %r - %s', browserID, ctx['url'])
        self.__creatingBrowserID = browserID
        browser = self.__browsers[browserID]
        if not browser.create():
            _logger.debug('CTRL: Failed the create step: %r', browserID)
            self.delBrowser(browserID)
            self.__tryCreateNextPendingBrowser()
            return
        else:
            self.onBrowserAdded(browserID)

            def createBrowserTimeout():
                _logger.debug('CTRL: Browser create timed out')
                createNextBrowser()

            timeoutid = BigWorld.callback(30.0, createBrowserTimeout)

            def createNextBrowser():
                _logger.debug('CTRL: Triggering create of next browser from: %s', browserID)
                BigWorld.cancelCallback(timeoutid)
                creation = self.__browserCreationCallbacks.pop(browserID, None)
                if creation is not None:
                    self.__browsers[browserID].onCanCreateNewBrowser -= creation
                BigWorld.callback(1.0, self.__tryCreateNextPendingBrowser)
                return

            def failedCreationCallback(url):
                _logger.debug('CTRL: Failed a creation: %r - %s', browserID, url)
                self.__clearCallbacks(browserID, self.__browsers[browserID], False)
                self.delBrowser(browserID)

            def successfulCreationCallback(url, isLoaded, httpStatusCode=None):
                _logger.debug('CTRL: Ready to show: %r - %r - %s', browserID, isLoaded, url)
                self.__clearCallbacks(browserID, self.__browsers[browserID], False)
                if isLoaded:
                    self.__showBrowser(browserID, ctx)
                else:
                    _logger.warning('Browser request url %s was not loaded!', url)
                g_eventBus.handleEvent(BrowserEvent(BrowserEvent.BROWSER_CREATED, ctx=ctx))
                self.__createDone(ctx)

            def titleUpdateCallback(title):
                ctx['title'] = title

            browser.onCanCreateNewBrowser += createNextBrowser
            self.__browserCreationCallbacks[browserID] = createNextBrowser
            browser.onFailedCreation += failedCreationCallback
            browser.onTitleChange += titleUpdateCallback
            if ctx['isAsync']:
                self.__browsersCallbacks[browserID] = (None,
                 successfulCreationCallback,
                 failedCreationCallback,
                 titleUpdateCallback)
                browser.onLoadEnd += successfulCreationCallback
            else:
                self.__browsersCallbacks[browserID] = (successfulCreationCallback,
                 None,
                 failedCreationCallback,
                 titleUpdateCallback)
                browser.onReady += successfulCreationCallback
            return

    def __stop(self):
        while self.__browsers:
            browserID, browser = self.__browsers.popitem()
            self.__clearCallbacks(browserID, browser, True)
            browser.destroy()

    def __clearCallbacks(self, browserID, browser, incDelayedCreation):
        ready, loadEnd, failed, title = self.__browsersCallbacks.pop(browserID, (None, None, None, None))
        if browser is not None:
            if failed is not None:
                browser.onFailedCreation -= failed
            if ready is not None:
                browser.onReady -= ready
            if loadEnd is not None:
                browser.onLoadEnd -= loadEnd
            if title is not None:
                browser.onTitleChange -= title
        if incDelayedCreation:
            creation = self.__browserCreationCallbacks.pop(browserID, None)
            if browser is not None and creation is not None:
                browser.onCanCreateNewBrowser -= creation
        return

    def __showBrowser(self, browserID, ctx):
        _logger.debug('CTRL: Showing a browser: %r - %s', browserID, ctx['url'])
        if ctx.get('showWindow'):
            alias = ctx['alias']
            g_eventBus.handleEvent(LoadViewEvent(alias, getViewName(alias, browserID), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
        showBrowserCallback = ctx.get('showBrowserCallback')
        if showBrowserCallback:
            showBrowserCallback()
