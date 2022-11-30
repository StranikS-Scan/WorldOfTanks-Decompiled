# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_browser_view.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebViewTransparent
from uilogging.ny.loggers import NyInfoVideoLogger

class NyBrowserView(WebViewTransparent):
    __uiLogger = NyInfoVideoLogger()

    def _populate(self):
        super(NyBrowserView, self)._populate()
        self.__uiLogger.onViewOpened()

    def _dispose(self):
        self.__uiLogger.onViewClosed()
        super(NyBrowserView, self)._dispose()
