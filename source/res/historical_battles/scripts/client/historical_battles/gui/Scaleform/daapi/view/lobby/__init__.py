# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from historical_battles.gui.Scaleform.daapi.view.lobby.diorama_vehicle_marker_view import DioramaVehicleMarkerView
from historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview.hb_vehicle_preview import HBVehiclePreview
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, DioramaVehicleMarkerView, 'lobbyVehicleMarkerView.swf', WindowLayer.MARKER, VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, ScopeTemplates.DEFAULT_SCOPE), ViewSettings(VIEW_ALIAS.HB_VEHICLE_PREVIEW, HBVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.HB_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (LobbyPackageBusinessHandler(),)


class LobbyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.HB_VEHICLE_PREVIEW, self.loadViewByCtxEvent),)
        super(LobbyPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
