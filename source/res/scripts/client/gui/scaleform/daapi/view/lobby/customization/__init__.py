# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/__init__.py
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.customization.filter_popover import FilterPopover
    from gui.Scaleform.daapi.view.lobby.customization.purchase_window import PurchaseWindow
    return (GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, FilterPopover, 'customizationFiltersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, PurchaseWindow, 'customizationBuyWindow.swf', ViewTypes.TOP_WINDOW, 'customizationBuyWindow', None, ScopeTemplates.DEFAULT_SCOPE))


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
    return (CustomizationPackageBusinessHandler(),)


class CustomizationPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, self.loadViewByCtxEvent), (VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, self.loadViewByCtxEvent))
        super(CustomizationPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
