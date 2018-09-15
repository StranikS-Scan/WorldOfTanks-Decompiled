# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationItemCMHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.CUSTOMIZATION_ITEM, CustomizationItemCMHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import AnchorProperties
    from gui.Scaleform.daapi.view.lobby.customization.camo_anchor_properties import CamoAnchorProperties
    from gui.Scaleform.daapi.view.lobby.customization.customization_popover import CustomizationPopover
    from gui.Scaleform.daapi.view.lobby.customization.decal_anchor_properties import DecalAnchorProperties
    from gui.Scaleform.daapi.view.lobby.customization.effects_properties import EffectsAnchorProperties
    from gui.Scaleform.daapi.view.lobby.customization.filter_popover import FilterPopover
    from gui.Scaleform.daapi.view.lobby.customization.non_historic_indicator_popover import NonHistoricItemsPopover
    from gui.Scaleform.daapi.view.lobby.customization.paint_anchor_properties import PaintAnchorProperties
    from gui.Scaleform.daapi.view.lobby.customization.property_sheet_season_buttons_component import PropertySheetSeasonButtonsComponent
    from gui.Scaleform.daapi.view.lobby.customization.purchase_window import PurchaseWindow
    from gui.Scaleform.daapi.view.lobby.customization.style_anchor_properties import StyleAnchorProperties
    from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog import ConfirmCustomizationItemDialog
    return (GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, FilterPopover, 'customizationFiltersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_NON_HISTORIC_ITEMS_POPOVER, NonHistoricItemsPopover, 'customizationNonHistoricItemsPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.CUSTOMIZATION_NON_HISTORIC_ITEMS_POPOVER, VIEW_ALIAS.CUSTOMIZATION_NON_HISTORIC_ITEMS_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, PurchaseWindow, 'customizationBuyWindow.swf', ViewTypes.TOP_WINDOW, 'customizationBuyWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, ConfirmCustomizationItemDialog, 'confirmCustomizationItemDialog.swf', ViewTypes.TOP_WINDOW, 'confirmCustomizationItemDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ViewSettings(VIEW_ALIAS.CUSTOMIZATION_POPOVER, CustomizationPopover, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CUSTOMIZATION_ALIASES.CUSTOMIZATION_STYLE_POPOVER, StyleAnchorProperties, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CUSTOMIZATION_ALIASES.CUSTOMIZATION_DECAL_POPOVER, DecalAnchorProperties, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CUSTOMIZATION_ALIASES.CUSTOMIZATION_PAINT_POPOVER, PaintAnchorProperties, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CUSTOMIZATION_ALIASES.CUSTOMIZATION_CAMO_POPOVER, CamoAnchorProperties, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CUSTOMIZATION_ALIASES.CUSTOMIZATION_EFFECT_POPOVER, EffectsAnchorProperties, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SEASON_BUTTONS_COMPONENTS, PropertySheetSeasonButtonsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


CAMOUFLAGES_KIND_TEXTS = [VEHICLE_CUSTOMIZATION.CAMOUFLAGE_WINTER, VEHICLE_CUSTOMIZATION.CAMOUFLAGE_SUMMER, VEHICLE_CUSTOMIZATION.CAMOUFLAGE_DESERT]
CAMOUFLAGES_NATIONS_TEXTS = [VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_USSR,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_GERMANY,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_USA,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_CHINA,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_FRANCE,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_UK,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_JAPAN,
 VEHICLE_CUSTOMIZATION.CAMOUFLAGE_NATION_CZECH]

def getBusinessHandlers():
    return (CustomizationPackageBusinessHandler(), CustomizationDialogPackageBusinessHandler())


class CustomizationPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, self.loadViewByCtxEvent), (VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, self.loadViewByCtxEvent), (VIEW_ALIAS.CUSTOMIZATION_NON_HISTORIC_ITEMS_POPOVER, self.loadViewByCtxEvent))
        super(CustomizationPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class CustomizationDialogPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_CONFIRM_CUSTOMIZATION_ITEM_DIALOG, self.__confirmCustomizationItemHandler),)
        super(CustomizationDialogPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.GLOBAL)

    def __confirmCustomizationItemHandler(self, event):
        self.loadViewWithGenName(CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, event.meta, event.handler)
