# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/Scaleform/daapi/view/lobby/__init__.py
from __future__ import absolute_import
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ComponentSettings, WindowLayer, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from resource_well.gui.impl.lobby.feature.resource_well_browser_view import ResourceWellBrowserView
    from resource_well.gui.Scaleform.daapi.view.lobby.vehicle_preview.resource_well_preview import ResourceWellVehiclePreview
    from resource_well.gui.Scaleform.daapi.view.lobby.vehicle_preview.info.vehicle_preview_bottom_panel import VehiclePreviewBottomPanel
    from resource_well.gui.impl.lobby.feature.progression_view import ProgressionWindow
    from resource_well.gui.impl.lobby.feature.completed_progression_view import CompletedProgressionWindow
    return (ViewSettings(VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW, ResourceWellVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW, ResourceWellBrowserView, 'browserScreen.swf', WindowLayer.TOP_WINDOW, VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_WELL_PY_ALIAS, VehiclePreviewBottomPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.RESOURCE_WELL_PROGRESSION, ProgressionWindow, '', WindowLayer.SUB_VIEW, VIEW_ALIAS.RESOURCE_WELL_PROGRESSION, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.RESOURCE_WELL_COMPLETED_PROGRESSION, CompletedProgressionWindow, '', WindowLayer.SUB_VIEW, VIEW_ALIAS.RESOURCE_WELL_COMPLETED_PROGRESSION, ScopeTemplates.LOBBY_SUB_SCOPE))


def getStateMachineRegistrators():
    from resource_well.gui.impl.lobby.feature.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getBusinessHandlers():
    return (ResourceWellLobbyBusinessHandler(),)


class ResourceWellLobbyBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.RESOURCE_WELL_VEHICLE_PREVIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.RESOURCE_WELL_BROWSER_VIEW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.RESOURCE_WELL_PROGRESSION, self.loadViewByCtxEvent),
         (VIEW_ALIAS.RESOURCE_WELL_COMPLETED_PROGRESSION, self.loadViewByCtxEvent))
        super(ResourceWellLobbyBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
