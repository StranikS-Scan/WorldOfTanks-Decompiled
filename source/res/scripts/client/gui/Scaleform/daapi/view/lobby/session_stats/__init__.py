# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/__init__.py
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_popover import SessionStatsPopover
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_settings import SessionStatsSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.app_loader import settings as app_settings
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_overview import SessionStatsOverview
    from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_views import SessionBattleStatsView
    from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_views import SessionVehicleStatsView
    from gui.Scaleform.framework import ViewSettings
    from gui.Scaleform.framework import GroupedViewSettings
    from gui.Scaleform.framework import ViewTypes
    from gui.Scaleform.framework import ScopeTemplates
    return (ViewSettings(SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS, SessionBattleStatsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_PY_ALIAS, SessionVehicleStatsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(SESSION_STATS_CONSTANTS.SESSION_STATS_OVERVIEW_PY_ALIAS, SessionStatsOverview, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(SESSION_STATS_CONSTANTS.SESSION_STATS_SETTINGS_PY_ALIAS, SessionStatsSettings, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     GroupedViewSettings(SESSION_STATS_CONSTANTS.SESSION_STATS_POPOVER, SessionStatsPopover, 'sessionStatsPopover.swf', ViewTypes.WINDOW, 'SessionStatsPopover', SESSION_STATS_CONSTANTS.SESSION_STATS_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE))


def getBusinessHandlers():
    return (SessionStatsPackageBusinessHandler(),)


class SessionStatsPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((SESSION_STATS_CONSTANTS.SESSION_STATS_POPOVER, self.loadViewByCtxEvent),)
        super(SessionStatsPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
