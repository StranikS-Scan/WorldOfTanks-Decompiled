# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.customization_cm_handlers import CustomizationItemCMHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CUSTOMIZATION_ALIASES import CUSTOMIZATION_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.CUSTOMIZATION_ITEM, CustomizationItemCMHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.customization.customization_properties_sheet import CustomizationPropertiesSheet
    from gui.Scaleform.daapi.view.lobby.customization.customization_bottom_panel import CustomizationBottomPanel
    from gui.Scaleform.daapi.view.lobby.customization.filter_popover import FilterPopover
    from gui.Scaleform.daapi.view.lobby.customization.installed_items_popover import InstalledItemsPopover
    from gui.Scaleform.daapi.view.lobby.customization.purchase_window import PurchaseWindow
    from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog import ConfirmCustomizationItemDialog
    return (GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, FilterPopover, 'customizationFiltersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER, InstalledItemsPopover, 'customizationItemsPopover.swf', ViewTypes.WINDOW, VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER, VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, PurchaseWindow, 'customizationBuyWindow.swf', ViewTypes.LOBBY_TOP_SUB, 'customizationBuyWindow', None, ScopeTemplates.LOBBY_SUB_SCOPE, isModal=True, canDrag=False),
     GroupedViewSettings(CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, ConfirmCustomizationItemDialog, 'confirmCustomizationItemDialog.swf', ViewTypes.TOP_WINDOW, 'confirmCustomizationItemDialog', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ViewSettings(VIEW_ALIAS.CUSTOMIZATION_PROPERTIES_SHEET, CustomizationPropertiesSheet, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.CUSTOMIZATION_BOTTOM_PANEL, CustomizationBottomPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


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
        listeners = ((VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, self.loadViewByCtxEvent), (VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, self.loadViewByCtxEvent), (VIEW_ALIAS.CUSTOMIZATION_ITEMS_POPOVER, self.loadViewByCtxEvent))
        super(CustomizationPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class CustomizationDialogPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((ShowDialogEvent.SHOW_CONFIRM_C11N_BUY_DIALOG, self.__confirmCustomizationItemHandler), (ShowDialogEvent.SHOW_CONFIRM_C11N_SELL_DIALOG, self.__confirmCustomizationItemHandler))
        super(CustomizationDialogPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.GLOBAL)

    def __confirmCustomizationItemHandler(self, event):
        self.loadViewWithGenName(CUSTOMIZATION_ALIASES.CONFIRM_CUSTOMIZATION_ITEM_DIALOG, event.meta, event.handler)
