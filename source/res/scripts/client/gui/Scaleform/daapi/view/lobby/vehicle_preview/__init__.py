# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.crew_tab_view import CrewTabInject
from gui.Scaleform.framework import ComponentSettings, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
    from gui.Scaleform.daapi.view.lobby.trade_in.trade_in_vehicle_preview import TradeInVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.marathon_vehicle_preview import MarathonVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import ConfigurableVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.offer_gift_vehicle_preview import OfferGiftVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.rental_vehicle_preview import RentalVehiclePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_progression_preview import VehicleStyleProgressionPreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_buying_preview import VehicleStyleBuyingPreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.showcase_style_buying_preview import VehicleShowcaseStyleBuyingPreview
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
    return (ViewSettings(VIEW_ALIAS.VEHICLE_PREVIEW, VehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.HERO_VEHICLE_PREVIEW, VehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.HERO_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW, ConfigurableVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.RENTAL_VEHICLE_PREVIEW, RentalVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.RENTAL_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.STYLE_PREVIEW, VehicleStylePreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.STYLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW, VehicleStyleProgressionPreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.STYLE_BUYING_PREVIEW, VehicleStyleBuyingPreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.STYLE_BUYING_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW, VehicleShowcaseStyleBuyingPreview, 'vehicleBasePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, TradeInVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW, MarathonVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW, OfferGiftVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.PARAMETERS_PY_ALIAS, VehiclePreviewParameters, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_PY_ALIAS, VehiclePreviewTopPanelTabs, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_PY_ALIAS, VehiclePreviewBottomPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_TRADE_IN_PY_ALIAS, VehiclePreviewBottomPanelTradeIn, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_PROGRESSION_PY_ALIAS, VehiclePreviewBottomPanelStyleProgression, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_BUYING_PY_ALIAS, VehiclePreviewBottomPanelStyleBuying, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_SHOWCASE_STYLE_BUYING_PY_ALIAS, VehiclePreviewBottomPanelShowcaseStyleBuying, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_OFFER_GIFT_PY_ALIAS, VehiclePreviewBottomPanelOfferGift, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BROWSE_LINKAGE, VehiclePreviewBrowseTab, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.MODULES_LINKAGE, VehiclePreviewModulesTab, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.MODULES_PY_ALIAS, ModulesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.CREW_TAB_INJECT, CrewTabInject, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.PACK_ITEM_POPOVER, PackItemsPopover, 'packItemsPopover.swf', WindowLayer.WINDOW, VIEW_ALIAS.PACK_ITEM_POPOVER, VIEW_ALIAS.PACK_ITEM_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.TRADE_OFF_WIDGET_ALIAS, TradeOffWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WOT_PLUS_LINKAGE, VehiclePreviewBottomPanelRental, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (VehPreviewPackageBusinessHandler(),)


def getStateMachineRegistrators():
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


class VehPreviewPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.PACK_ITEM_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.HERO_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.RENTAL_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.STYLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.STYLE_BUYING_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SHOWCASE_STYLE_BUYING_PREVIEW, self.loadViewByCtxEvent))
        super(VehPreviewPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
