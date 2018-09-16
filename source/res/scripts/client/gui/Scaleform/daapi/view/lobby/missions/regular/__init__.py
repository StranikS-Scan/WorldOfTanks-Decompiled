# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.genConsts.LINKEDSET_ALIASES import LINKEDSET_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.common.filter_popover import VehiclesFilterPopover
    from gui.Scaleform.daapi.view.lobby.missions.regular.mission_details_container_view import MissionDetailsContainerView
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_filter_popover import MissionsFilterPopoverView
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_page import MissionsPage
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_token_popover import MissionsTokenPopover
    from gui.Scaleform.daapi.view.lobby.missions.regular.vehicle_selector import RegularMissionVehicleSelector
    from gui.Scaleform.daapi.view.lobby.missions.regular.vehicle_selector import RegularVehicleSelectorCarousel
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_views import MissionsGroupedView, MissionsMarathonView, MissionsCategoriesView, MissionsEventBoardsView, CurrentVehicleMissionsView
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_details_container_view import EventBoardsDetailsBrowserView, EventBoardsDetailsVehiclesView, EventBoardsDetailsAwardsView, EventBoardsDetailsBattleView
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_browser_overlay import EventBoardsBrowserOverlay
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vehicles_overlay import EventBoardsVehiclesOverlay
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_battle_overlay import EventBoardsBattleOverlay
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_awards_overlay import EventBoardsAwardsOverlay
    return (ViewSettings(VIEW_ALIAS.LOBBY_MISSIONS, MissionsPage, 'missionsPage.swf', ViewTypes.LOBBY_SUB, VIEW_ALIAS.LOBBY_MISSIONS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_MISSION_DETAILS, MissionDetailsContainerView, 'missionsDetails.swf', ViewTypes.LOBBY_TOP_SUB, VIEW_ALIAS.LOBBY_MISSION_DETAILS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, EventBoardsDetailsBrowserView, 'eventBoardsDetails.swf', ViewTypes.LOBBY_TOP_SUB, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, EventBoardsDetailsVehiclesView, 'eventBoardsDetails.swf', ViewTypes.LOBBY_TOP_SUB, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_VIEW, EventBoardsDetailsAwardsView, 'eventBoardsDetails.swf', ViewTypes.LOBBY_TOP_SUB, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, EventBoardsDetailsBattleView, 'eventBoardsDetails.swf', ViewTypes.LOBBY_TOP_SUB, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_ALIAS, EventBoardsBrowserOverlay, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_ALIAS, EventBoardsVehiclesOverlay, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_ALIAS, EventBoardsBattleOverlay, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_ALIAS, EventBoardsAwardsOverlay, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, MissionsGroupedView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, MissionsMarathonView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS, MissionsEventBoardsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, MissionsCategoriesView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, CurrentVehicleMissionsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.VIEW_SCOPE),
     ViewSettings(QUESTS_ALIASES.MISSIONS_VEHICLE_SELECTOR_ALIAS, RegularMissionVehicleSelector, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.VEHICLE_SELECTOR_CAROUSEL_ALIAS, RegularVehicleSelectorCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, MissionsFilterPopoverView, 'missionsFilterPopoverView.swf', ViewTypes.WINDOW, QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, MissionsTokenPopover, 'missionsTokenPopover.swf', ViewTypes.WINDOW, QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLES_FILTER_POPOVER, VehiclesFilterPopover, 'vehiclesFiltersPopoverView.swf', ViewTypes.WINDOW, VIEW_ALIAS.VEHICLES_FILTER_POPOVER, VIEW_ALIAS.VEHICLES_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (MissionsPackageBusinessHandler(),)


class MissionsPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_MISSIONS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_MISSION_DETAILS, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_VIEW, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, self.loadViewByCtxEvent))
        super(MissionsPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
