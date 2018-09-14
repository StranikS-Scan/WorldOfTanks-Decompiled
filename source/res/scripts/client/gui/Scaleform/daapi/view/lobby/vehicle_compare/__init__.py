# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/__init__.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_cm_handlers import VehicleCompareContextMenuHandler
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates, ViewTypes
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.VEH_COMPARE, VehicleCompareContextMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_add_vehicle_popover import VehicleCompareAddVehiclePopover
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_cart_popover import VehicleCompareCartPopover
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_modules_window import VehicleModulesWindow
    return (GroupedViewSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_MODULES_WINDOW, VehicleModulesWindow, 'vehicleModulesWindow.swf', ViewTypes.WINDOW, 'VehicleModulesWindow', None, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CMP_ADD_VEHICLE_POPOVER, VehicleCompareAddVehiclePopover, 'vehicleCompareAddVehiclePopover.swf', ViewTypes.WINDOW, 'VehicleCompareAddVehiclePopover', VEHICLE_COMPARE_CONSTANTS.VEHICLE_CMP_ADD_VEHICLE_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE), GroupedViewSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER, VehicleCompareCartPopover, 'vehicleCompareCartPopover.swf', ViewTypes.WINDOW, 'vehicleCompareCartPopover', VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE))


def getBusinessHandlers():
    return (VehComparePackageBusinessHandler(),)


class VehComparePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VEHICLE_COMPARE_CONSTANTS.VEHICLE_CMP_ADD_VEHICLE_POPOVER, self.loadViewByCtxEvent), (VEHICLE_COMPARE_CONSTANTS.VEHICLE_MODULES_WINDOW, self.loadViewByCtxEvent), (VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER, self.loadViewByCtxEvent))
        super(VehComparePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
