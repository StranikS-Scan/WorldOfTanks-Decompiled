# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE

def getContextMenuHandlers():
    from comp7.gui.Scaleform.daapi.view.lobby import user_cm_handlers
    return ((CONTEXT_MENU_HANDLER_TYPE.COMP_LEADERBOARD_USER, user_cm_handlers.Comp7LeaderboardCMHandler),)


def getViewSettings():
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_modifiers_panel import Comp7ModifiersPanelInject
    from comp7.gui.impl.lobby.tournaments_widget import TournamentsWidgetComponent
    from comp7.gui.Scaleform.daapi.view.lobby.comp7_entry_point import Comp7EntryPoint
    from comp7.gui.impl.lobby.main_widget import Comp7MainWidgetComponent
    from comp7.gui.Scaleform.daapi.view.lobby.comp7_prime_time_view import Comp7PrimeTimeView
    from comp7.gui.impl.lobby.comp7_grand_tournament_widget import Comp7GrandTournamentsWidgetComponent
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.carousels.tank_carousel import Comp7TankCarousel
    from gui.Scaleform.framework import getSwfExtensionUrl
    return (ViewSettings(HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, Comp7PrimeTimeView, getSwfExtensionUrl('comp7', HANGAR_ALIASES.COMP7_PRIME_TIME), WindowLayer.SUB_VIEW, HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ComponentSettings(HANGAR_ALIASES.COMP7_MODIFIERS_PANEL, Comp7ModifiersPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_TOURNAMENT_BANNER, TournamentsWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_ENTRY_POINT, Comp7EntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_WIDGET, Comp7MainWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_GRAND_TOURNAMENT_BANNER, Comp7GrandTournamentsWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.COMP7_TANK_CAROUSEL, Comp7TankCarousel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (Comp7PackageBusinessHandler(),)


class Comp7PackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((HANGAR_ALIASES.COMP7_PRIME_TIME_ALIAS, self.loadViewByCtxEvent),)
        super(Comp7PackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
