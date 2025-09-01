# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/__init__.py
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7_core.gui.Scaleform.genConsts.COMP7_CORE_HANGAR_ALIASES import COMP7_CORE_HANGAR_ALIASES
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    from comp7.gui.Scaleform.daapi.view.lobby import user_cm_handlers
    return ((CONTEXT_MENU_HANDLER_TYPE.COMP_LEADERBOARD_USER, user_cm_handlers.Comp7LeaderboardCMHandler),)


def getViewSettings():
    from comp7.gui.impl.lobby.tournaments_widget import TournamentsWidgetComponent
    from comp7.gui.Scaleform.daapi.view.lobby.comp7_prime_time_view import Comp7PrimeTimeView
    from comp7.gui.impl.lobby.comp7_grand_tournament_widget import Comp7GrandTournamentsWidgetComponent
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.carousels.tank_carousel import Comp7TankCarousel
    from comp7.gui.impl.lobby.hangar.comp7_hangar import Comp7HangarWindow
    from gui.Scaleform.framework import getSwfExtensionUrl
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
    from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import ConfigurableVehiclePreview
    return (ViewSettings(COMP7_HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, Comp7PrimeTimeView, getSwfExtensionUrl('comp7_core', COMP7_CORE_HANGAR_ALIASES.COMP7_CORE_PRIME_TIME_SWF), WindowLayer.SUB_VIEW, COMP7_HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(COMP7_HANGAR_ALIASES.COMP7_STYLE_PREVIEW, VehicleStylePreview, getSwfExtensionUrl('comp7_core', COMP7_CORE_HANGAR_ALIASES.COMP7_CORE_STYLE_PREVIEW_SWF), WindowLayer.SUB_VIEW, COMP7_HANGAR_ALIASES.COMP7_STYLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(COMP7_HANGAR_ALIASES.COMP7_CONFIGURABLE_VEHICLE_PREVIEW, ConfigurableVehiclePreview, getSwfExtensionUrl('comp7_core', COMP7_CORE_HANGAR_ALIASES.COMP7_CORE_VEHICLE_PREVIEW_SWF), WindowLayer.SUB_VIEW, COMP7_HANGAR_ALIASES.COMP7_CONFIGURABLE_VEHICLE_PREVIEW, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(COMP7_HANGAR_ALIASES.COMP7_LOBBY_HANGAR, Comp7HangarWindow, '', WindowLayer.SUB_VIEW, COMP7_HANGAR_ALIASES.COMP7_LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_TOURNAMENT_BANNER, TournamentsWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_GRAND_TOURNAMENT_BANNER, Comp7GrandTournamentsWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(COMP7_HANGAR_ALIASES.COMP7_TANK_CAROUSEL, Comp7TankCarousel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (Comp7PackageBusinessHandler(),)


class Comp7PackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((COMP7_HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, self.loadViewByCtxEvent),
         (COMP7_HANGAR_ALIASES.COMP7_LOBBY_HANGAR, self.loadViewByCtxEvent),
         (COMP7_HANGAR_ALIASES.COMP7_STYLE_PREVIEW, self.loadViewByCtxEvent),
         (COMP7_HANGAR_ALIASES.COMP7_CONFIGURABLE_VEHICLE_PREVIEW, self.loadViewByCtxEvent))
        super(Comp7PackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
