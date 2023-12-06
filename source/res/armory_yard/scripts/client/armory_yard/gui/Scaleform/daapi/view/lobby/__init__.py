# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/__init__.py
from armory_yard.gui.impl.lobby.feature.armory_yard_hangar_widget_view import isArmoryYardEntryPointAvailable
from frameworks.wulf import WindowLayer
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.armory_yard_vehicle_preview import ArmoryYardVehiclePreview
from helpers import dependency
from gui.app_loader import settings as app_settings
from skeletons.gui.game_control import IArmoryYardController
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.system_factory import registerBannerEntryPointValidator, registerBannerEntryPointLUIRule
registerBannerEntryPointValidator(HANGAR_ALIASES.ARMORY_YARD_WIDGET_ENTRY_POINT, isArmoryYardEntryPointAvailable)
registerBannerEntryPointLUIRule(HANGAR_ALIASES.ARMORY_YARD_WIDGET_ENTRY_POINT, LuiRules.ARMORY_YARD_ENTRY_POINT)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.armory_yard_entry_point import ArmoryYardEntryPoint, ArmoryYardEntryPointWidget
    return (ComponentSettings(HANGAR_ALIASES.ARMORY_YARD_ENTRY_POINT, ArmoryYardEntryPoint, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_ALIASES.ARMORY_YARD_WIDGET_ENTRY_POINT, ArmoryYardEntryPointWidget, ScopeTemplates.DEFAULT_SCOPE), ViewSettings(HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW, ArmoryYardVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (_ArmoryYardBusinessHandler(),)


class _ArmoryYardBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW, self.__handleVehConfiguratorEvent),)
        super(_ArmoryYardBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __handleVehConfiguratorEvent(self, event):
        window = self.findViewByAlias(WindowLayer.TOP_WINDOW, HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW)
        if window is not None:
            window.destroy()
        else:
            self.loadViewByCtxEvent(event)
        return
