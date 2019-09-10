# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.store import store_cm_handlers
    from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
    return ((CONTEXT_MENU_HANDLER_TYPE.STORE_VEHICLE, store_cm_handlers.VehicleContextMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.store.browser.ingame_shop_view import IngameShopView, IngameShopOverlay, PremContentPageOverlay
    from gui.Scaleform.daapi.view.lobby.store.Inventory import Inventory
    from gui.Scaleform.daapi.view.lobby.store.Shop import Shop
    from gui.Scaleform.daapi.view.lobby.store.StoreActions import StoreActions
    from gui.Scaleform.daapi.view.lobby.store.StoreTable import StoreTable
    from gui.Scaleform.daapi.view.lobby.store.StoreView import StoreView
    from gui.Scaleform.daapi.view.lobby.shared.web_view import WebViewTransparent
    from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
    return (ViewSettings(VIEW_ALIAS.LOBBY_STORE, IngameShopView, 'browserScreen.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_STORE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_STORE_OLD, StoreView, 'store.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_STORE_OLD, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_STORAGE_OLD, StoreView, 'store.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_STORAGE_OLD, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OVERLAY_WEB_STORE, IngameShopOverlay, 'browserScreen.swf', ViewTypes.OVERLAY, VIEW_ALIAS.OVERLAY_WEB_STORE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.WEB_VIEW_TRANSPARENT, WebViewTransparent, 'browserScreen.swf', ViewTypes.OVERLAY, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW, PremContentPageOverlay, 'browserScreen.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.SHOP_TABLE, StoreTable, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_INVENTORY, Inventory, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_SHOP, Shop, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_STORE_ACTIONS, StoreActions, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (StorePackageBusinessHandler(),)


class StorePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_INVENTORY, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_STORE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.WEB_VIEW_TRANSPARENT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OVERLAY_WEB_STORE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_STORE_OLD, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_STORAGE_OLD, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW, self.loadViewByCtxEvent))
        super(StorePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
