# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BrowserWindow.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.meta.BrowserMeta import BrowserMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import BrowserEvent, ShowWindowEvent
__author__ = 'd_dichkovsky'

class BrowserWindow(View, AbstractWindowView, BrowserMeta, AppRef):

    def __init__(self, ctx):
        super(BrowserWindow, self).__init__()
        url = ctx.get('url')
        self.customTitle = ctx.get('title', None)
        self.showActionBtn = ctx.get('showActionBtn', True)
        if url is not None:
            self.app.browser.setUrlToOpen(url)
        else:
            self.app.browser.resetToDefaultUrl()
        return

    def _populate(self):
        super(BrowserWindow, self)._populate()
        self.as_configureS(self.customTitle, self.showActionBtn)
        self.onBrowserShow(True)
        self.addListener(BrowserEvent.BROWSER_LOAD_START, self.__onLoadStart, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(BrowserEvent.BROWSER_LOAD_END, self.__onLoadEnd, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(ShowWindowEvent.SHOW_BROWSER_WINDOW, self.__onShow, EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(BrowserEvent.BROWSER_LOAD_START, self.__onLoadStart, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(BrowserEvent.BROWSER_LOAD_END, self.__onLoadEnd, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(ShowWindowEvent.SHOW_BROWSER_WINDOW, self.__onShow, EVENT_BUS_SCOPE.LOBBY)
        self.onBrowserHide()
        super(BrowserWindow, self)._dispose()

    def onWindowClose(self):
        self.destroy()

    def browserAction(self, action):
        self.app.browser.browserAction(action)

    def browserMove(self, x, y, z):
        self.app.browser.browserMove(x, y, z)

    def browserDown(self, x, y, z):
        self.app.browser.browserDown(x, y, z)

    def browserUp(self, x, y, z):
        self.app.browser.browserUp(x, y, z)

    def browserFocusOut(self):
        self.app.browser.browserFocusOut()

    def onBrowserShow(self, needRefresh = False):
        self.app.browser.onBrowserShow(needRefresh)

    def onBrowserHide(self):
        self.app.browser.onBrowserHide()

    def __onLoadStart(self, event):
        self.as_loadingStartS()

    def __onLoadEnd(self, event):
        self.as_loadingStopS()

    def __onShow(self, event):
        self.as_configureS(event.ctx.get('title', self.customTitle), event.ctx.get('showActionBtn', self.showActionBtn))
        if 'url' in event.ctx:
            self.app.browser.navigate(event.ctx['url'])
        else:
            self.app.browser.resetToDefaultUrl()
            self.app.browser.onBrowserShow(False)
