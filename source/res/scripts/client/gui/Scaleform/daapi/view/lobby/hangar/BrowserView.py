# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/BrowserView.py
import BigWorld
import Keys
from adisp import process
from debug_utils import LOG_ERROR
from gui.InputHandler import g_instance as g_inputHandler
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BrowserScreenMeta import BrowserScreenMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.lobby_context import ILobbyContext

def makeBrowserParams(waitingMessage=R.invalid(), isTransparent=False):
    if not waitingMessage:
        waitingMessage = R.strings.waiting.loadContent()
    return {'waitingMessage': backport.msgid(waitingMessage),
     'isTransparent': isTransparent}


class BrowserView(LobbySubView, BrowserScreenMeta):
    __background_alpha__ = 1.0
    browserCtrl = dependency.descriptor(IBrowserController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(BrowserView, self).__init__(ctx)
        self.__browserId = None
        self.__ctx = ctx
        self.__hasFocus = False
        self.__browser = None
        self.__browserComponent = None
        self.__errorOccurred = False
        self.__closedByUser = False
        self.__isBrowserLoading = True
        self.__pendingRequest = None
        self.__viewSize = None
        return

    def onFocusChange(self, hasFocus):
        self.__hasFocus = hasFocus
        self.__updateSkipEscape()

    def onCloseBtnClick(self):
        self.__closedByUser = True
        self.onCloseView()

    def onCloseView(self):
        returnAlias = self.__getFromCtx('returnAlias', VIEW_ALIAS.LOBBY_HANGAR)
        self.fireEvent(events.LoadViewEvent(returnAlias, ctx=self.__ctx), EVENT_BUS_SCOPE.LOBBY)

    def viewSize(self, width, height):
        self.__viewSize = (width, height)
        self.__loadBrowser()

    def updateCtx(self, ctx):
        if ctx:
            self.__ctx.update(ctx)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BrowserView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, self.__getFromCtx('webHandlers'), alias=self.alias)
            viewPy.onError += self.__onError
            self.__browserComponent = viewPy

    def _populate(self):
        super(BrowserView, self)._populate()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_inputHandler.onKeyDown += self.__onKeyDown

    def _invalidate(self, *args, **kwargs):
        super(BrowserView, self)._invalidate(*args, **kwargs)
        self.__ctx = args[0]
        if self.__isBrowserLoading:
            self.__pendingRequest = self.__getFromCtx('url')
        elif self.__browser:
            self.__configureBrowser()
            self.__navigateTo(self.__getFromCtx('url'))
        else:
            self.__loadBrowser()
        if self.__browserComponent:
            self.__browserComponent.init(self.__browserId, self.__getFromCtx('webHandlers'), alias=self.alias)

    def _dispose(self):
        if self.__browserComponent:
            self.__browserComponent.onError -= self.__onError
        returnCallback = self.__getFromCtx('returnClb')
        if returnCallback is not None:
            callbackArgs = {'byUser': self.__closedByUser}
            if self.__browser:
                callbackArgs['url'] = self.__browser.url
            returnCallback(**callbackArgs)
        g_inputHandler.onKeyDown -= self.__onKeyDown
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(BrowserView, self)._dispose()
        return

    def __onError(self):
        self.__errorOccurred = True
        self.__updateSkipEscape()

    def __onKeyDown(self, event):
        if event.key == Keys.KEY_ESCAPE:
            if not self.__browser.skipEscape:
                self.onCloseView()

    def __getFromCtx(self, name, default=None):
        ctx = self.__ctx
        return ctx.get(name, default) if ctx else default

    @process
    def __loadBrowser(self):
        url = self.__getFromCtx('url')
        if url is not None:
            self.__isBrowserLoading = True
            self.__browserId = yield self.browserCtrl.load(url=url, useBrowserWindow=False, showBrowserCallback=self.__showBrowser, browserSize=self.__viewSize, browserID=self.__browserId)
            self.__isBrowserLoading = False
            self.__configureBrowser()
        else:
            LOG_ERROR('Url is missing!')
        return

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)
        if self.__pendingRequest:
            self.__navigateTo(self.__pendingRequest)
            self.__pendingRequest = None
        return

    def __updateSkipEscape(self):
        if self.__browser is not None:
            self.__browser.skipEscape = not self.__hasFocus or self.__errorOccurred
        return

    def __onServerSettingChanged(self, diff):
        handler = self.__getFromCtx('onServerSettingsChange')
        if callable(handler):
            handler(self, diff)

    def __configureBrowser(self):
        browser = self.browserCtrl.getBrowser(self.__browserId)
        if browser:
            browser.useSpecialKeys = self.__getFromCtx('useSpecialKeys', False)
            browser.allowRightClick = self.__getFromCtx('allowRightClick', False)
            browser.setDisabledKeys(self.__getFromCtx('disabledKeys', tuple()))
            self.__browser = browser
            self.__updateSkipEscape()
        else:
            LOG_ERROR('Failed to create browser!')

    def __navigateTo(self, url):
        if url is not None and self.__browser is not None:
            self.__browser.navigate(url)
        return
