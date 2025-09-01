# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/__init__.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates, ComponentSettings, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from gui.app_loader import settings as app_settings
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_cm_handlers import VehicleCompareContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.VEH_COMPARE, VehicleCompareContextMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_view import VehicleCompareView
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorMain
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_add_vehicle_popover import VehicleCompareAddVehiclePopover
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_cart_popover import VehicleCompareCartPopover
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_modules_view import VehicleModulesView
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_parameters import VehicleCompareParameters
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorView
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_ammo_inject import VehicleCompareConfiguratorAmmoInject
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_skills_inject import VehicleCompareConfiguratorSkillsInject
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_progression_inject import VehicleCompareConfiguratorProgressionInject
    return (ViewSettings(VIEW_ALIAS.VEHICLE_COMPARE, VehicleCompareView, 'vehicleCompareView.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEHICLE_COMPARE, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, VehicleCompareConfiguratorMain, 'vehicleCompareConfiguratorMain.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_MODULES_VIEW, VehicleModulesView, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_VIEW, VehicleCompareConfiguratorView, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CMP_ADD_VEHICLE_POPOVER, VehicleCompareAddVehiclePopover, 'vehicleCompareAddVehiclePopover.swf', WindowLayer.WINDOW, 'VehicleCompareAddVehiclePopover', VEHICLE_COMPARE_CONSTANTS.VEHICLE_CMP_ADD_VEHICLE_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     GroupedViewSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER, VehicleCompareCartPopover, 'vehicleCompareCartPopover.swf', WindowLayer.WINDOW, 'vehicleCompareCartPopover', VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     ComponentSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_PARAMS, VehicleCompareParameters, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_SKILLS_WIDGET, VehicleCompareConfiguratorSkillsInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_EQUIPMENT_WIDGET, VehicleCompareConfiguratorAmmoInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_MODIFICATIONS_WIDGET, VehicleCompareConfiguratorProgressionInject, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (VehComparePackageBusinessHandler(),)


def getStateMachineRegistrators():
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


class VehComparePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.VEHICLE_COMPARE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR, self.loadViewByCtxEvent),
         (VEHICLE_COMPARE_CONSTANTS.VEHICLE_CMP_ADD_VEHICLE_POPOVER, self.loadViewByCtxEvent),
         (VEHICLE_COMPARE_CONSTANTS.VEHICLE_MODULES_VIEW, self.loadViewByCtxEvent),
         (VEHICLE_COMPARE_CONSTANTS.VEHICLE_COMPARE_CART_POPOVER, self.loadViewByCtxEvent))
        super(VehComparePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
