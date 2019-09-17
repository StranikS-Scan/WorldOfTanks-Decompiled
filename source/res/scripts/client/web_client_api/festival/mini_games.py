# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/festival/mini_games.py
import Windowing
from gui.shared.event_dispatcher import hideWebBrowserOverlay
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from web_client_api import w2c, W2CSchema

class MiniGamesWebApiMixin(object):

    @w2c(W2CSchema, 'show_cursor')
    def showCursor(self, _):
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if app and app.cursorMgr:
            app.cursorMgr.attachCursor()

    @w2c(W2CSchema, 'hide_cursor')
    def hideCursor(self, _):
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if app and app.cursorMgr:
            app.cursorMgr.detachCursor()

    @w2c(W2CSchema, 'show_card_view')
    def showCardView(self, _):
        hideWebBrowserOverlay(ctx={'showFestivalView': True})

    @w2c(W2CSchema, 'is_client_active')
    def isClientActive(self, _):
        return Windowing.isWindowAccessible()
