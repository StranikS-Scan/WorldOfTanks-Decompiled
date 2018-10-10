# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shop20/__init__.py
from gui.Scaleform.daapi.view.lobby.shop20.rental_term_selection_popover import RentalTermSelectionPopover
from gui.Scaleform.daapi.view.lobby.shop20.vehicle_sell_confirmation_popover import VehicleSellConfirmationPopover
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.SHOP20_ALIASES import SHOP20_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (GroupedViewSettings(SHOP20_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, VehicleSellConfirmationPopover, 'vehicleSellConfirmationPopover.swf', ViewTypes.TOP_WINDOW, SHOP20_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, SHOP20_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(SHOP20_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, RentalTermSelectionPopover, 'rentalTermSelectionPopover.swf', ViewTypes.TOP_WINDOW, SHOP20_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, SHOP20_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (Shop20PackageBusinessHandler(),)


class Shop20PackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((SHOP20_ALIASES.VEHICLE_SELL_CONFIRMATION_POPOVER_ALIAS, self.loadViewByCtxEvent), (SHOP20_ALIASES.RENTAL_TERM_SELECTION_POPOVER_ALIAS, self.loadViewByCtxEvent))
        super(Shop20PackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
