# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/BrowserView.py
import BigWorld
import Keys
from adisp import process
from debug_utils import LOG_ERROR
from gui.InputHandler import g_instance as g_inputHandler
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BrowserViewMeta import BrowserViewMeta
from gui.Scaleform.locale.WAITING import WAITING
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
from skeletons.gui.lobby_context import ILobbyContext

def makeBrowserParams(waitingMessage=WAITING.LOADCONTENT, isTransparent=False):
    return {'waitingMessage': waitingMessage,
     'isTransparent': isTransparent}


class BrowserView(LobbySubView, BrowserViewMeta):
    __background_alpha__ = 1.0
    browserCtrl = dependency.descriptor(IBrowserController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx=None):
        super(BrowserView, self).__init__(ctx)
        self.__browserId = 0
        self.__ctx = ctx
        self.__hasFocus = False
        self.__browser = None
        self.__browserView = None
        self.__errorOccurred = False
        self.__closedByUser = False
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
        self.__loadBrowser(width, height)

    def updateCtx(self, ctx):
        if ctx:
            self.__ctx.update(ctx)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BrowserView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, self.__getFromCtx('webHandlers'), alias=self.alias)
            viewPy.onError += self.__onError
            self.__browserView = viewPy

    def _populate(self):
        super(BrowserView, self)._populate()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_inputHandler.onKeyDown += self.__onKeyDown

    def _dispose(self):
        if self.__browserView:
            self.__browserView.onError -= self.__onError
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
    def __loadBrowser(self, width, height):
        url = self.__getFromCtx('url')
        if url is not None:
            self.__browserId = yield self.browserCtrl.load(url=url, useBrowserWindow=False, showBrowserCallback=self.__showBrowser, browserSize=(width, height))
            browser = self.browserCtrl.getBrowser(self.__browserId)
            if browser:
                browser.useSpecialKeys = self.__getFromCtx('useSpecialKeys', False)
                browser.allowRightClick = self.__getFromCtx('allowRightClick', False)
                browser.setDisabledKeys(self.__getFromCtx('disabledKeys', tuple()))
                self.__browser = browser
                self.__updateSkipEscape()
            else:
                LOG_ERROR('Failed to create browser!')
        else:
            LOG_ERROR('Url is missing!')
        return

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)

    def __updateSkipEscape(self):
        if self.__browser is not None:
            self.__browser.skipEscape = not self.__hasFocus or self.__errorOccurred
        return

    def __onServerSettingChanged(self, diff):
        handler = self.__getFromCtx('onServerSettingsChange')
        if callable(handler):
            handler(self, diff)
