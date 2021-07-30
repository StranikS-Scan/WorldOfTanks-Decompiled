# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.MAPBOX_ALIASES import MAPBOX_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.mapbox.mapbox_prime_time_view import MapboxPrimeTimeView
    return (ViewSettings(MAPBOX_ALIASES.MAPBOX_PRIME_TIME, MapboxPrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, WindowLayer.SUB_VIEW, MAPBOX_ALIASES.MAPBOX_PRIME_TIME, ScopeTemplates.LOBBY_SUB_SCOPE, True),)


def getBusinessHandlers():
    return (MapboxPackageBusinessHandler(),)


class MapboxPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((MAPBOX_ALIASES.MAPBOX_PRIME_TIME, self.loadViewByCtxEvent),)
        super(MapboxPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
