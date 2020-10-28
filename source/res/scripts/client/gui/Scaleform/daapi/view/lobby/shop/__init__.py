# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shop/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.shop.rental_term_selection_popover import RentalTermSelectionPopover
from gui.Scaleform.daapi.view.lobby.shop.vehicle_sell_confirmation_popover import VehicleSellConfirmationPopover
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.SHOP_ALIASES import SHOP_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (GroupedViewSettings(SHOP_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, VehicleSellConfirmationPopover, 'vehicleSellConfirmationPopover.swf', WindowLayer.TOP_WINDOW, SHOP_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, SHOP_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(SHOP_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, RentalTermSelectionPopover, 'rentalTermSelectionPopover.swf', WindowLayer.TOP_WINDOW, SHOP_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, SHOP_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (ShopPackageBusinessHandler(),)


class ShopPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((SHOP_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, self.loadViewByCtxEvent), (SHOP_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, self.loadViewByCtxEvent))
        super(ShopPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
