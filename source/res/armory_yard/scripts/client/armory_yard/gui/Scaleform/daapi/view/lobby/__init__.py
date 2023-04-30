# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.armory_yard_vehicle_preview import ArmoryYardVehiclePreview
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.system_factory import registerCarouselEventEntryPoint
from gui.impl.gen import R
from armory_yard.gui.impl.lobby.feature.armory_yard_hangar_widget_view import ArmoryYardCarouselWidgetView
registerCarouselEventEntryPoint(R.views.armory_yard.lobby.feature.ArmoryYardWidgetView(), ArmoryYardCarouselWidgetView)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.armory_yard_entry_point import ArmoryYardEntryPoint
    return (ComponentSettings(HANGAR_ALIASES.ARMORY_YARD_ENTRY_POINT, ArmoryYardEntryPoint, ScopeTemplates.DEFAULT_SCOPE), ViewSettings(HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW, ArmoryYardVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, HANGAR_ALIASES.ARMORY_YARD_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE))


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
