# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/BrowserWindow.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BrowserWindowMeta import BrowserWindowMeta
from gui.Scaleform.locale.WAITING import WAITING
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBrowserController

class BrowserWindow(BrowserWindowMeta):
    __metaclass__ = event_bus_handlers.EventBusListener
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self, ctx=None):
        super(BrowserWindow, self).__init__()
        self.__size = ctx.get('size')
        self.__browserID = ctx.get('browserID')
        self.__customTitle = ctx.get('title')
        self.__showActionBtn = ctx.get('showActionBtn', True)
        self.__showWaiting = ctx.get('showWaiting', False)
        self.__showCloseBtn = ctx.get('showCloseBtn', False)
        self.__isSolidBorder = ctx.get('isSolidBorder', False)
        self.__alias = ctx.get('alias', '')
        self.__handlers = ctx.get('handlers', None)
        self.__uniqueBrowserName = '_'.join((self.__alias, str(self.__browserID)))
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BrowserWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserID, self.__handlers, self.__alias)

    def onWindowClose(self):
        webBrowser = self.browserCtrl.getBrowser(self.__browserID)
        if webBrowser is not None:
            webBrowser.onUserRequestToClose()
        else:
            LOG_ERROR('Browser not found. Browser id = "{}"'.format(self.__browserID))
        self.destroy()
        return

    def _populate(self):
        super(BrowserWindow, self)._populate()
        self.as_configureS(self.__customTitle, self.__showActionBtn, self.__showCloseBtn, self.__isSolidBorder)
        self.as_setSizeS(*self.__size)
        if self.__showWaiting:
            self.as_showWaitingS(WAITING.LOADCONTENT, {})

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BROWSER_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def __handleBrowserClose(self, event):
        if event.ctx.get('browserID') == self.__browserID:
            self.destroy()

    @property
    def uniqueBrowserName(self):
        return self.__uniqueBrowserName
