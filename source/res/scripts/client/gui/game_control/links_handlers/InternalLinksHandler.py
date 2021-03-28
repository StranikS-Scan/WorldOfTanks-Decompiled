# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/links_handlers/InternalLinksHandler.py
from adisp import async, process
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.game_control.links import URLMacros
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.game_control import IInternalLinksController, IBrowserController
_LISTENERS = {}

class InternalLinksHandler(IInternalLinksController):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(InternalLinksHandler, self).__init__()
        self.__urlMacros = None
        self._browserID = None
        return

    def init(self):
        self.__urlMacros = URLMacros()
        addListener = g_eventBus.addListener
        for eventType, handlerName in _LISTENERS.iteritems():
            handler = getattr(self, handlerName, None)
            if not handler:
                LOG_ERROR('Handler is not found', eventType, handlerName)
                continue
            if not callable(handler):
                LOG_ERROR('Handler is invalid', eventType, handlerName, handler)
                continue
            addListener(eventType, handler)

        return

    def fini(self):
        if self.__urlMacros is not None:
            self.__urlMacros.clear()
            self.__urlMacros = None
        self._browserID = None
        removeListener = g_eventBus.removeListener
        for eventType, handlerName in _LISTENERS.iteritems():
            handler = getattr(self, handlerName, None)
            if handler:
                removeListener(eventType, handler)

        super(InternalLinksHandler, self).fini()
        return

    @async
    @process
    def getURL(self, name, callback):
        urlSettings = GUI_SETTINGS.lookup(name)
        if urlSettings:
            url = yield self.__urlMacros.parse(str(urlSettings))
        else:
            url = yield lambda callback: callback('')
        callback(url)

    @process
    def __openInternalBrowse(self, urlName, title='', browserSize=None, showActionBtn=True, showCloseBtn=False):
        parsedUrl = yield self.getURL(urlName)
        if parsedUrl:
            self._browserID = yield self.browserCtrl.load(parsedUrl, browserID=self._browserID, title=title, browserSize=browserSize, showActionBtn=showActionBtn, showCloseBtn=showCloseBtn)
