# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/weekend_brawl/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.WEEKENDBRAWL_ALIASES import WEEKENDBRAWL_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.weekend_brawl.weekend_brawl_prime_time_view import WeekendBrawlPrimeTimeView
    return (ViewSettings(WEEKENDBRAWL_ALIASES.WEEKEND_BRAWL_PRIME_TIME_ALIAS, WeekendBrawlPrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, WindowLayer.SUB_VIEW, WEEKENDBRAWL_ALIASES.WEEKEND_BRAWL_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),)


def getBusinessHandlers():
    return (WeekendBrawlPackageBusinessHandler(),)


class WeekendBrawlPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((WEEKENDBRAWL_ALIASES.WEEKEND_BRAWL_PRIME_TIME_ALIAS, self.loadViewByCtxEvent),)
        super(WeekendBrawlPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
