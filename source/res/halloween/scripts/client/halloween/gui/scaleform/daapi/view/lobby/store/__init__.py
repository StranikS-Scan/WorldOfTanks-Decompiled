# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/store/__init__.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from halloween.gui import halloween_gui_constants

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.store.browser.shop_view import ShopOverlay
    from gui.Scaleform.framework import ViewSettings, ScopeTemplates
    return (ViewSettings(halloween_gui_constants.VIEW_ALIAS.HW_OVERLAY_WEB_STORE, ShopOverlay, 'browserScreen.swf', WindowLayer.OVERLAY, halloween_gui_constants.VIEW_ALIAS.HW_OVERLAY_WEB_STORE, ScopeTemplates.LOBBY_SUB_SCOPE),)


def getBusinessHandlers():
    return (StorePackageBusinessHandler(),)


class StorePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((halloween_gui_constants.VIEW_ALIAS.HW_OVERLAY_WEB_STORE, self.loadViewByCtxEvent),)
        super(StorePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
