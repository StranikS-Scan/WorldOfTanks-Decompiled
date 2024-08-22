# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.crew_tab_view import CrewTabInject
from gui.Scaleform.framework import ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehiclePreviewParameters
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.top_panel_tabs import VehiclePreviewTopPanelTabs
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview_bottom_panel import VehiclePreviewBottomPanel
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.bottom_panel_trade_in import VehiclePreviewBottomPanelTradeIn
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.bottom_panel_offer_gift import VehiclePreviewBottomPanelOfferGift
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.browse_tab import VehiclePreviewBrowseTab
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.modules_tab import VehiclePreviewModulesTab, ModulesPanel
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.pack_items_popover import PackItemsPopover
    from gui.Scaleform.daapi.view.lobby.trade_in.trade_off_widget import TradeOffWidget
    from gui.Scaleform.framework import ScopeTemplates, GroupedViewSettings
    from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.bottom_panel_style_buying import VehiclePreviewBottomPanelStyleBuying
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.bottom_panel_showcase_style_buying import VehiclePreviewBottomPanelShowcaseStyleBuying
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.bottom_panel_style_progression import VehiclePreviewBottomPanelStyleProgression
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.rental_vehicle_preview import VehiclePreviewBottomPanelRental
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.bottom_panel_resource_well import VehiclePreviewBottomPanelResourceWell
    return (ComponentSettings(VEHPREVIEW_CONSTANTS.PARAMETERS_PY_ALIAS, VehiclePreviewParameters, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_PY_ALIAS, VehiclePreviewTopPanelTabs, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_PY_ALIAS, VehiclePreviewBottomPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_TRADE_IN_PY_ALIAS, VehiclePreviewBottomPanelTradeIn, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_PROGRESSION_PY_ALIAS, VehiclePreviewBottomPanelStyleProgression, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_BUYING_PY_ALIAS, VehiclePreviewBottomPanelStyleBuying, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_SHOWCASE_STYLE_BUYING_PY_ALIAS, VehiclePreviewBottomPanelShowcaseStyleBuying, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_OFFER_GIFT_PY_ALIAS, VehiclePreviewBottomPanelOfferGift, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WELL_PY_ALIAS, VehiclePreviewBottomPanelResourceWell, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BROWSE_LINKAGE, VehiclePreviewBrowseTab, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.MODULES_LINKAGE, VehiclePreviewModulesTab, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.MODULES_PY_ALIAS, ModulesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.CREW_TAB_INJECT, CrewTabInject, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PACK_ITEM_POPOVER, PackItemsPopover, 'packItemsPopover.swf', WindowLayer.WINDOW, VIEW_ALIAS.PACK_ITEM_POPOVER, VIEW_ALIAS.PACK_ITEM_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.TRADE_OFF_WIDGET_ALIAS, TradeOffWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WOT_PLUS_LINKAGE, VehiclePreviewBottomPanelRental, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (VehPreviewPackageBusinessHandler(),)


class VehPreviewPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.PACK_ITEM_POPOVER, self.loadViewByCtxEvent),)
        super(VehPreviewPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
