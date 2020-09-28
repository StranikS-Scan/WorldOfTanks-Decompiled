# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.store.browser.shop_view import ShopView, ShopOverlay, PremContentPageOverlay, WtEventShopOverlay
    from gui.Scaleform.daapi.view.lobby.shared.web_view import WebViewTransparent
    from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
    return (ViewSettings(VIEW_ALIAS.LOBBY_STORE, ShopView, 'browserScreen.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_STORE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OVERLAY_WEB_STORE, ShopOverlay, 'browserScreen.swf', ViewTypes.OVERLAY, VIEW_ALIAS.OVERLAY_WEB_STORE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.WEB_VIEW_TRANSPARENT, WebViewTransparent, 'browserScreen.swf', ViewTypes.OVERLAY, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW, PremContentPageOverlay, 'browserScreen.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OVERLAY_WT_EVENT_VIEW, WtEventShopOverlay, 'browserScreen.swf', ViewTypes.OVERLAY, VIEW_ALIAS.OVERLAY_WT_EVENT_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (StorePackageBusinessHandler(),)


class StorePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_STORE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.WEB_VIEW_TRANSPARENT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OVERLAY_WEB_STORE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OVERLAY_WT_EVENT_VIEW, self.loadViewByCtxEvent))
        super(StorePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
