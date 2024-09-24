# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from frameworks.wulf import WindowLayer
from tech_tree_trade_in.gui.scaleform.daapi.view.lobby.tech_tree_trade_in_banner import TechTreeTradeInBannerComponent
from tech_tree_trade_in.gui.scaleform.genConsts.TECH_TREE_TRADE_IN_HANGAR_ALIASES import TECH_TREE_TRADE_IN_HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(TECH_TREE_TRADE_IN_HANGAR_ALIASES.TECH_TREE_TRADE_IN_BROWSER_OVERLAY, WebView, 'browserScreen.swf', WindowLayer.TOP_WINDOW, TECH_TREE_TRADE_IN_HANGAR_ALIASES.TECH_TREE_TRADE_IN_BROWSER_OVERLAY, ScopeTemplates.LOBBY_TOP_SUB_SCOPE), ComponentSettings(HANGAR_ALIASES.TECH_TREE_TRADE_IN_BANNER, TechTreeTradeInBannerComponent, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (TechTreeTradeInPackageBusinessHandler(),)


class TechTreeTradeInPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((TECH_TREE_TRADE_IN_HANGAR_ALIASES.TECH_TREE_TRADE_IN_BROWSER_OVERLAY, self.loadViewByCtxEvent),)
        super(TechTreeTradeInPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
