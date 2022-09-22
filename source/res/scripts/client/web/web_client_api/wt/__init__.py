# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/wt/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.gen import R
from gui.impl.lobby.wt_event.wt_event_sound import playLootBoxPortalExit
from gui.shared.event_dispatcher import showHangar, showEventStorageWindow
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from web.web_client_api import w2capi, W2CSchema, w2c

@w2capi(name='wt', key='action')
class WtWebApi(W2CSchema):

    @w2c(W2CSchema, name='show_event_storage_window')
    def showEventStorageWindow(self, _):
        appLoader = dependency.instance(IAppLoader)
        uiLoader = dependency.instance(IGuiLoader)
        app = appLoader.getApp()
        if app is not None and app.containerManager is not None:
            shopViewKey = ViewKey(VIEW_ALIAS.LOBBY_STORE, VIEW_ALIAS.LOBBY_STORE)
            shopOverlayViewKey = ViewKey(VIEW_ALIAS.OVERLAY_WEB_STORE, VIEW_ALIAS.OVERLAY_WEB_STORE)
            if app.containerManager.isViewCreated(shopViewKey):
                showHangar()
            elif app.containerManager.isViewCreated(shopOverlayViewKey):
                shopOverlayView = app.containerManager.getViewByKey(shopOverlayViewKey)
                shopOverlayView.destroy()

        def predicate(window):
            return window.content is not None and getattr(window.content, 'layoutID', None) == R.views.lobby.wt_event.WtEventPortal()

        windows = uiLoader.windowsManager.findWindows(predicate)
        if windows:
            eventPortalWindow = windows.pop()
            windowsToClose = uiLoader.windowsManager.findWindows(lambda window: window.parent == eventPortalWindow)
            if windowsToClose:
                playLootBoxPortalExit()
            for windowToClose in windowsToClose:
                windowToClose.destroy()

        else:
            showEventStorageWindow()
        return
