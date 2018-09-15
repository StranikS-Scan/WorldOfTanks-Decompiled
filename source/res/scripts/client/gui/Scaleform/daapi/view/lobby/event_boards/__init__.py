# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_table_view import EventBoardsTableView
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_award_group import EventBoardsAwardGroup
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_pagination import EventBoardsPagination
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_maintenance import EventBoardsMaintenance
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_filter_popover import EventBoardsFilterPopover
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_filter_vehicles_popover import EventBoardsFilterVehiclesPopover
    return (ViewSettings(VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE, EventBoardsTableView, 'eventBoardsTable.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(VIEW_ALIAS.LOBBY_EVENT_BOARDS_AWARDGROUP, EventBoardsAwardGroup, None, ViewTypes.COMPONENT, VIEW_ALIAS.LOBBY_EVENT_BOARDS_AWARDGROUP, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_EVENT_BOARDS_PAGINATION, EventBoardsPagination, None, ViewTypes.COMPONENT, VIEW_ALIAS.LOBBY_EVENT_BOARDS_PAGINATION, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_EVENT_BOARDS_MAINTENANCE, EventBoardsMaintenance, None, ViewTypes.COMPONENT, VIEW_ALIAS.LOBBY_EVENT_BOARDS_MAINTENANCE, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS, EventBoardsFilterPopover, 'FilterPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.VEHICLES_FILTER_POPOVER, EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS, EventBoardsFilterVehiclesPopover, 'FilterVehiclesPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.VEHICLES_FILTER_POPOVER, EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (EventBoardsPackageBusinessHandler(),)


class EventBoardsPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE, self.loadViewByCtxEvent), (EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS, self.loadViewByCtxEvent), (EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS, self.loadViewByCtxEvent))
        super(EventBoardsPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
