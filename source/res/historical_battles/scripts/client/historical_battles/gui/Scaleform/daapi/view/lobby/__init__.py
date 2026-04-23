# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from historical_battles.gui.Scaleform.daapi.view.lobby.diorama_vehicle_marker_view import DioramaVehicleMarkerView
from historical_battles.gui.Scaleform.daapi.view.lobby.vehicle_preview.hb_vehicle_preview import HBVehiclePreview
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.HISTORICALBATTLES_ALIASES import HISTORICALBATTLES_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from order_widget import OrderWidget
    from quests_widget import QuestsWidget
    from shop_widget import ShopWidget
    from division_panel import DivisionPanel
    from progression_widget import ProgressionWidget
    from front_panel import FrontPanel
    from hangar_vignette import HangarVignette
    return (ViewSettings(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, DioramaVehicleMarkerView, 'lobbyVehicleMarkerView.swf', WindowLayer.MARKER, VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.HB_VEHICLE_PREVIEW, HBVehiclePreview, 'vehiclePreview.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.HB_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_ORDER_WIDGET, OrderWidget, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_QUESTS_WIDGET, QuestsWidget, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_SHOP_WIDGET, ShopWidget, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_DIVISION_PANEL, DivisionPanel, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_PROGRESSION_WIDGET, ProgressionWidget, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_FRONT_PANEL, FrontPanel, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HISTORICALBATTLES_ALIASES.HISTORICAL_BATTLES_HANGAR_VIGNETTE, HangarVignette, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (LobbyPackageBusinessHandler(),)


class LobbyPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.HB_VEHICLE_PREVIEW, self.loadViewByCtxEvent),)
        super(LobbyPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
