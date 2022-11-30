# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings, ComponentSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from fun_random.gui.Scaleform.daapi.view.common.filter_popover import FunRandomCarouselFilterPopover
    from fun_random.gui.Scaleform.daapi.view.lobby.feature.prime_time_view import FunRandomPrimeTimeView
    from fun_random.gui.Scaleform.daapi.view.lobby.hangar.carousel.tank_carousel import FunRandomTankCarousel
    from fun_random.gui.Scaleform.daapi.view.lobby.hangar.fun_random_entry_point import FunRandomEntryPoint
    from fun_random.gui.Scaleform.daapi.view.lobby.hangar.fun_random_widget import FunRandomHangarWidgetComponent
    from fun_random.gui.Scaleform.daapi.view.lobby.hangar.fun_random_ny_widget import FunRandomNYHangarWidgetComponent
    return (ComponentSettings(HANGAR_ALIASES.FUN_RANDOM_TANK_CAROUSEL, FunRandomTankCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FUNRANDOM_ALIASES.FUN_RANDOM_ENTRY_POINT, FunRandomEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR_WIDGET, FunRandomHangarWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FUNRANDOM_ALIASES.FUN_RANDOM_NY_HANGAR_WIDGET, FunRandomNYHangarWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(FUNRANDOM_ALIASES.FUN_RANDOM_PRIME_TIME, FunRandomPrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, WindowLayer.SUB_VIEW, FUNRANDOM_ALIASES.FUN_RANDOM_PRIME_TIME, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     GroupedViewSettings(FUNRANDOM_ALIASES.FUN_RANDOM_CAROUSEL_FILTER_POPOVER, FunRandomCarouselFilterPopover, 'filtersPopoverView.swf', WindowLayer.WINDOW, FUNRANDOM_ALIASES.FUN_RANDOM_CAROUSEL_FILTER_POPOVER, FUNRANDOM_ALIASES.FUN_RANDOM_CAROUSEL_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (FunRandomLobbyBusinessHandler(),)


class FunRandomLobbyBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FUNRANDOM_ALIASES.FUN_RANDOM_PRIME_TIME, self.loadViewByCtxEvent), (FUNRANDOM_ALIASES.FUN_RANDOM_CAROUSEL_FILTER_POPOVER, self.loadViewByCtxEvent))
        super(FunRandomLobbyBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
