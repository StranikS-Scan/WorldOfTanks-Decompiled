# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ComponentSettings, WindowLayer, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from resource_well.gui.impl.lobby.feature.entry_point import ResourceWellEntryPointComponent
    from resource_well.gui.impl.lobby.feature.resource_well_browser_view import ResourceWellBrowserView
    from resource_well.gui.Scaleform.daapi.view.lobby.vehicle_preview.resource_well_preview import ResourceWellVehiclePreview
    from resource_well.gui.Scaleform.daapi.view.lobby.vehicle_preview.info.vehicle_preview_bottom_panel import VehiclePreviewBottomPanel
    return (ViewSettings(VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW, ResourceWellVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW, ResourceWellBrowserView, 'browserScreen.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HANGAR_ALIASES.RESOURCE_WELL_ENTRY_POINT, ResourceWellEntryPointComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WELL_PY_ALIAS, VehiclePreviewBottomPanel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (ResourceWellLobbyBusinessHandler(),)


class ResourceWellLobbyBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW, self.loadViewByCtxEvent), (VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW, self.loadViewByCtxEvent))
        super(ResourceWellLobbyBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
