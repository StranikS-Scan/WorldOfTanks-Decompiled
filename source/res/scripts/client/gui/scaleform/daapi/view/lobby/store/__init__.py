# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/__init__.py
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.store.Inventory import Inventory
    from gui.Scaleform.daapi.view.lobby.store.Shop import Shop
    from gui.Scaleform.daapi.view.lobby.store.StoreTable import StoreTable
    return (ViewSettings(VIEW_ALIAS.LOBBY_INVENTORY, Inventory, 'inventory.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_INVENTORY, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.LOBBY_SHOP, Shop, 'shop.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_SHOP, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.SHOP_TABLE, StoreTable, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (StorePackageBusinessHandler(),)


class StorePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_INVENTORY, self.loadViewByCtxEvent), (VIEW_ALIAS.LOBBY_SHOP, self.loadViewByCtxEvent))
        super(StorePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
