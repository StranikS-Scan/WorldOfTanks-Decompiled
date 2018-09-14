# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization_2_0/__init__.py
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.customization_2_0.filter_popover import FilterPopover
    from gui.Scaleform.daapi.view.lobby.customization_2_0.purchases_popover import PurchasesPopover
    from gui.Scaleform.daapi.view.lobby.customization_2_0.purchase_window import PurchaseWindow
    return (GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, FilterPopover, 'customizationFiltersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_PURCHASE_WINDOW, PurchaseWindow, 'customizationBuyWindow.swf', ViewTypes.WINDOW, 'customizationBuyWindow', None, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(VIEW_ALIAS.CUSTOMIZATION_PURCHASES_POPOVER, PurchasesPopover, 'customizationPurchasesPopover.swf', ViewTypes.WINDOW, 'customizationPurchasesPopover', VIEW_ALIAS.CUSTOMIZATION_PURCHASES_POPOVER, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (CustomizationPackageBusinessHandler(),)


class CustomizationPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.CUSTOMIZATION_FILTER_POPOVER, self.loadViewByCtxEvent), (VIEW_ALIAS.CUSTOMIZATION_PURCHASES_POPOVER, self.loadViewByCtxEvent))
        super(CustomizationPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
